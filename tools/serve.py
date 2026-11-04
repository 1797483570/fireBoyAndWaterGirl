#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""森林冰火人 H5 本地服务：静态文件 + 存档同步接口。

用法:
    python tools/serve.py [端口]      # 默认 8123

接口:
    GET  /api/ping   -> 探活 {"ok":true,"save":bool}
    GET  /api/save   -> 返回 saves/progress.json（不存在则 404）
    POST /api/save   -> 整份覆盖写入 saves/progress.json（写前备份 .bak.json）
                        写盘成功后，若当前目录是带远端的 git 仓库，后台自动
                        git add/commit/push 该文件（可设 FB_NO_GIT=1 关闭）
    GET  /api/git    -> 最近一次自动推送的状态

只监听 127.0.0.1，仅本机可访问。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(ROOT, "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")
BACKUP_FILE = os.path.join(SAVE_DIR, "progress.bak.json")

NO_CACHE = {".html", ".json", ".js", ".css"}

SAVE_REL = "saves/progress.json"
GIT_ENABLED = os.environ.get("FB_NO_GIT", "") not in ("1", "true", "yes")

_git_lock = threading.Lock()
_git_state = {"status": "idle", "message": "", "at": None, "enabled": GIT_ENABLED}


def _git(args, timeout=60):
    """在项目根目录跑 git，禁止任何交互式提示（否则后台进程会挂住）。"""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"      # 不等待终端输入
    env["GCM_INTERACTIVE"] = "never"      # 不弹凭据管理器的 GUI 窗口
    env.pop("GIT_ASKPASS", None)
    return subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        stdin=subprocess.DEVNULL,
    )


def _set_git_state(status, message=""):
    _git_state.update({"status": status, "message": message, "at": time.time()})


def _push_progress():
    """把 saves/progress.json 提交并推送。任何一步失败都只记录状态，不抛给请求方。"""
    if not GIT_ENABLED:
        _set_git_state("disabled", "FB_NO_GIT=1")
        return

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        _set_git_state("disabled", "not a git repository")
        return

    remotes = _git(["remote"]).stdout.split()
    if not remotes:
        _set_git_state("disabled", "no git remote")
        return

    _set_git_state("pushing", "committing...")

    _git(["add", SAVE_REL])
    staged = _git(["diff", "--cached", "--quiet", SAVE_REL])
    if staged.returncode != 0:
        msg = "save: 自动保存进度 %s" % time.strftime("%Y-%m-%d %H:%M")
        commit = _git(["commit", "-m", msg, "--", SAVE_REL])
        if commit.returncode != 0:
            _set_git_state("pending", (commit.stderr or commit.stdout).strip()[:180] or "commit failed")
            return
    else:
        msg = ""

    upstream = _git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream.returncode != 0:
        _set_git_state("pending", "current branch has no upstream")
        return

    ahead = _git(["rev-list", "--count", "@{u}..HEAD"]).stdout.strip()
    if ahead in ("", "0"):
        _set_git_state("pushed", msg or "already up to date")
        return

    push = _git(["-c", "credential.interactive=false", "push", "origin", "HEAD"], timeout=120)
    if push.returncode != 0:
        _set_git_state("pending", (push.stderr or push.stdout).strip()[:180] or "push failed")
        return

    _set_git_state("pushed", msg or ("pushed %d commit" % int(ahead)))


def schedule_push():
    """后台触发一次推送；上一次还没结束时直接跳过（下次保存会再触发）。"""
    if not GIT_ENABLED:
        return "disabled"
    if not _git_lock.acquire(blocking=False):
        return "busy"

    def run():
        try:
            _push_progress()
        except Exception as exc:  # noqa: BLE001 —— 后台线程不能抛
            _set_git_state("pending", str(exc)[:180])
        finally:
            _git_lock.release()

    threading.Thread(target=run, daemon=True).start()
    return "scheduled"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    # ---------- 工具 ----------
    def _json(self, code, payload=None, raw=None):
        body = raw if raw is not None else json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def end_headers(self):
        path = self.path.split("?")[0]
        if os.path.splitext(path)[1].lower() in NO_CACHE:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    # ---------- GET ----------
    def do_GET(self):
        if self.path.split("?")[0] == "/api/save":
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "rb") as fh:
                    self._json(200, raw=fh.read())
            else:
                self._json(404, {"error": "no save file"})
            return
        if self.path.split("?")[0] == "/api/ping":
            self._json(200, {"ok": True, "save": os.path.exists(SAVE_FILE), "git": GIT_ENABLED})
            return
        if self.path.split("?")[0] == "/api/git":
            self._json(200, dict(_git_state))
            return
        super().do_GET()

    # ---------- POST ----------
    def do_POST(self):
        if self.path.split("?")[0] != "/api/save":
            self._json(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > 32 * 1024 * 1024:
            self._json(400, {"error": "bad length"})
            return

        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid json"})
            return

        if not isinstance(data, dict) or not isinstance(data.get("saves"), dict):
            self._json(400, {"error": "invalid payload: need {saves:{...}}"})
            return

        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            if os.path.exists(SAVE_FILE):
                shutil.copy2(SAVE_FILE, BACKUP_FILE)
            fd, tmp = tempfile.mkstemp(dir=SAVE_DIR, suffix=".tmp")
            with os.fdopen(fd, "wb") as fh:
                fh.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
            os.replace(tmp, SAVE_FILE)
        except OSError as exc:
            self._json(500, {"error": "write failed: %s" % exc})
            return

        seasons = len(data["saves"])
        git_status = schedule_push()
        self._json(200, {"ok": True, "seasons": seasons, "updatedAt": data.get("updatedAt"), "git": git_status})
        self.log_message("save written: %d seasons (git: %s)", seasons, git_status)


def main():
    port = 8123
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("invalid port: %s" % sys.argv[1])
            return 2

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Fireboy & Watergirl H5 - local server")
    print("  root : %s" % ROOT)
    print("  url  : http://127.0.0.1:%d/" % port)
    print("  save : %s" % SAVE_FILE)
    print("  Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
