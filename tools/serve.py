#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""森林冰火人 H5 本地服务：静态文件 + 存档同步接口。

用法:
    python tools/serve.py [端口]      # 默认 8123

接口:
    GET  /api/save   -> 返回 saves/progress.json（不存在则 404）
    POST /api/save   -> 整份覆盖写入 saves/progress.json（写前备份 .bak.json）

只监听 127.0.0.1，仅本机可访问。
"""

import json
import os
import shutil
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(ROOT, "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")
BACKUP_FILE = os.path.join(SAVE_DIR, "progress.bak.json")

NO_CACHE = {".html", ".json", ".js", ".css"}


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
            self._json(200, {"ok": True, "save": os.path.exists(SAVE_FILE)})
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
        self._json(200, {"ok": True, "seasons": seasons, "updatedAt": data.get("updatedAt")})
        self.log_message("save written: %d seasons", seasons)


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
