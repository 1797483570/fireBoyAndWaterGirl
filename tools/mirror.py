#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
森林冰火人 H5 离线镜像抓取脚本
--------------------------------
数据来源: https://apps.ak-ioi.com/fireboy-and-watergirl/<季>/dist/
做法:
  1. 抓入口 HTML, 解析主脚本 (requirejs data-main / fairy-tales.min.js)
  2. 抓主脚本, 正则提取其引用的静态资源 (图集/音频/字体)
  3. 抓 temple.json, 从中取出全部关卡 JSON 路径
  4. 合并"首屏网络请求清单"(浏览器实测) + 正则结果 + 关卡清单, 并发下载
输出: <项目根>/games/<季>/dist/**  (保持原始相对路径, 便于游戏内相对引用)
"""

import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://apps.ak-ioi.com/fireboy-and-watergirl"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "games")

SEASONS = {
    "A": {"entry": "gameIndex.html", "main": None,
          "temples": ["data/forest/temple.json"]},
    "B": {"entry": "gameIndex.html", "main": None,
          "temples": ["data/light/temple.json"]},
    "C": {"entry": "gameIndex.html", "main": None,
          "temples": ["data/ice/temple.json"]},
    "D": {"entry": "gameIndex.html", "main": None,
          "temples": ["data/crystal/temple.json"]},
    "E": {"entry": "gameIndex.html", "main": None,
          "temples": ["data/elements/%s/temple.json" % t for t in
                      ("fire", "forest", "ice", "water", "crystal", "light", "wind")]},
    "F": {"entry": "index.htm", "main": "fairy-tales.min.js",
          "temples": ["data/fairytales/temple.json"]},
    "G": {"entry": "gameIndex.html", "main": None,
          "temples": ["data/friends/temple.json"]},
}

COMMON = [
    "bower_components/requirejs/require.js",
    "manifest.json",
    "game.json",
]

AUDIO = [
    "MenuMusic", "LevelMusic_speed", "LevelMusic_dark", "LevelMusicFinish_speed",
    "LevelMusic", "LevelMusicOver", "LevelMusicFinish", "CharToggle1", "CharToggle2",
    "EndPass", "EndFail", "EndDiamond", "Jump_fb", "Jump_wg", "Jump_fat",
    "Jump_small", "Jump_jump", "WaterSteps", "IceSteps_fb", "IceSteps_wg",
    "Death", "Diamond", "Door", "Freeze", "Melt", "Lever", "Pusher", "Platform",
    "Wind", "PortalOpen", "PortalLoop", "PortalClose", "PortalTransport",
    "Clock", "Slider", "LightPusher",
]

# 浏览器实测到的首屏资源(相对 dist), 用于兜底正则提取不到的部分
EXTRA = {
    "A": ["assets/images/TempleHallForest.jpg","assets/images/GameNameForest.png",
          "assets/atlasses/Temples/forest/TempleAssets.png",
          "assets/atlasses/Temples/forest/TempleAssets.json"],
    "B": ["assets/images/TempleHallLight.jpg","assets/images/GameNameLight.png",
          "assets/atlasses/Temples/light/TempleAssets.png",
          "assets/atlasses/Temples/light/TempleAssets.json"],
    "C": ["assets/images/TempleHallIce.jpg","assets/images/GameNameIce.png",
          "assets/atlasses/Temples/ice/TempleAssets.png",
          "assets/atlasses/Temples/ice/TempleAssets.json"],
    "D": ["assets/images/TempleHallCrystal.jpg","assets/images/GameNameCrystal.png",
          "assets/atlasses/Temples/crystal/TempleAssets.png",
          "assets/atlasses/Temples/crystal/TempleAssets.json"],
    "E": ["assets/images/branding/branding_logo_4399.png",
          "assets/images/TempleHallFire.jpg","assets/images/TempleHallForest.jpg",
          "assets/images/TempleHallIce.jpg","assets/images/TempleHallCrystal.jpg",
          "assets/images/TempleHallLight.jpg","assets/images/GameNameElements.png",
          "assets/atlasses/TempleIcons.png", "assets/atlasses/TempleIcons.json",
          "assets/fonts/font.png", "assets/fonts/font.fnt",
          "assets/images/stores/ios.png", "assets/images/stores/android.png",
          "assets/images/stores/microsoft.png", "assets/images/stores/steam.png",
          "assets/atlasses/Temples/fire/TempleAssets.png",
          "assets/atlasses/Temples/fire/TempleAssets.json",
          "assets/atlasses/Temples/forest/TempleAssets.png",
          "assets/atlasses/Temples/forest/TempleAssets.json",
          "assets/atlasses/Temples/ice/TempleAssets.png",
          "assets/atlasses/Temples/ice/TempleAssets.json",
          "assets/atlasses/Temples/water/TempleAssets.png",
          "assets/atlasses/Temples/water/TempleAssets.json",
          "assets/atlasses/Temples/crystal/TempleAssets.png",
          "assets/atlasses/Temples/crystal/TempleAssets.json",
          "assets/atlasses/Temples/light/TempleAssets.png",
          "assets/atlasses/Temples/light/TempleAssets.json",
          "assets/atlasses/Temples/wind/TempleAssets.png",
          "assets/atlasses/Temples/wind/TempleAssets.json",
          "assets/images/TempleHallWater.jpg", "assets/images/TempleHallWind.jpg"],
    "F": ["assets/images/TempleHallFairy.jpg", "assets/images/GameNameFairy.png",
          "assets/fonts/font.png", "assets/fonts/font.fnt",
          "assets/fonts/font_small.png", "assets/fonts/fontStone.png",
          "version.js"],
    "G": ["assets/images/TempleHallFriends.jpg","assets/images/GameNameFriends.png",
          "assets/atlasses/FriendsAssets.png", "assets/atlasses/FriendsAssets.json",
          "assets/atlasses/CursorAssets.png", "assets/atlasses/CursorAssets.json",
          "assets/atlasses/LangsAssets.png", "assets/atlasses/LangsAssets.json",
          "assets/atlasses/NewCharAssets.png", "assets/atlasses/NewCharAssets.json",
          "assets/atlasses/TutorialAssets.png", "assets/atlasses/TutorialAssets.json",
          "assets/atlasses/Temples/friends/TempleAssets.png",
          "assets/atlasses/Temples/friends/TempleAssets.json",
          "assets/images/LegacyThumbForest.png", "assets/images/LegacyThumbLight.png",
          "assets/images/LegacyThumbIce.png", "assets/images/LegacyThumbCrystal.png",
          "assets/images/LegacyThumbElements.png", "assets/images/LegacyThumbFairytales.png",
          "assets/images/stores/ios.png", "assets/images/stores/android.png",
          "assets/images/stores/microsoft.png", "assets/images/stores/steam.png"],
}

ASSET_RE = re.compile(
    r"""["'`(]([A-Za-z0-9_][A-Za-z0-9_\-./]*\.(?:png|jpe?g|webp|gif|svg|json|mp3|ogg|wav|m4a|mp4|webm|ttf|otf|woff2?|fnt|atlas|xml))["'`)]"""
)
DATA_MAIN_RE = re.compile(r'data-main="([^"]+)"')

STATS = {"ok": 0, "missing": 0, "bytes": 0, "fail": 0}
ERRORS = []


def fetch(url, referer=None, tries=3):
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if referer:
        headers["Referer"] = referer
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410):
                return e.code, None
            last = e
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(0.6 * (i + 1))
    return None, last


def local_path(season, rel):
    rel = rel.lstrip("/")
    return os.path.join(OUT, season, "dist", rel.replace("/", os.sep))


def norm(rel):
    rel = rel.split("?")[0].split("#")[0]
    if rel.startswith("../") or rel.startswith("http"):
        return None
    return rel.lstrip("/")


def download(season, rel, referer):
    rel = norm(rel)
    if not rel:
        return
    path = local_path(season, rel)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        STATS["bytes"] += os.path.getsize(path)
        return
    url = "%s/%s/dist/%s" % (BASE, season, rel)
    status, body = fetch(url, referer)
    if status == 200 and body is not None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(body)
        STATS["ok"] += 1
        STATS["bytes"] += len(body)
    elif status in (403, 404, 410):
        STATS["missing"] += 1
    else:
        STATS["fail"] += 1
        ERRORS.append((season, rel, str(status)))


def build_season(season):
    cfg = SEASONS[season]
    ref = "%s/%s/dist/%s" % (BASE, season, cfg["entry"])
    rels = set(COMMON) | set(EXTRA.get(season, []))
    rels.add(cfg["entry"])

    # 入口 HTML
    status, body = fetch(ref)
    if status != 200:
        print("[%s] 入口抓取失败 %s" % (season, status))
        return
    html = body.decode("utf-8", "replace")
    os.makedirs(os.path.join(OUT, season, "dist"), exist_ok=True)
    with open(local_path(season, cfg["entry"]), "wb") as f:
        f.write(body)

    # 主脚本
    main_rel = cfg["main"]
    m = DATA_MAIN_RE.search(html)
    if not m and not main_rel:
        print("[%s] 未找到 data-main" % season)
    mains = []
    if m:
        mains.append(m.group(1).split("?")[0])
    if main_rel:
        mains.append(main_rel)
    if season == "F":
        rels.add("version.js")

    main_text = ""
    for rel in mains:
        rels.add(rel)
        url = "%s/%s/dist/%s" % (BASE, season, rel)
        st, bd = fetch(url, ref)
        if st == 200:
            os.makedirs(os.path.dirname(local_path(season, rel)), exist_ok=True)
            with open(local_path(season, rel), "wb") as f:
                f.write(bd)
            main_text += bd.decode("utf-8", "replace")

    # 正则提取资源
    for mm in ASSET_RE.finditer(main_text):
        cand = norm(mm.group(1))
        if cand and not cand.startswith("..") and "." in cand:
            rels.add(cand)

    # 音频(尝试式, 404 会被跳过)
    for a in AUDIO:
        rels.add("assets/audio/%s.mp3" % a)

    # temple.json -> 关卡清单
    for tp in cfg["temples"]:
        url = "%s/%s/dist/%s" % (BASE, season, tp)
        st, bd = fetch(url, ref)
        if st != 200:
            print("  [%s] temple 缺失 %s (%s)" % (season, tp, st))
            continue
        os.makedirs(os.path.dirname(local_path(season, tp)), exist_ok=True)
        with open(local_path(season, tp), "wb") as f:
            f.write(bd)
        rels.add(tp)
        try:
            data = json.loads(bd.decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            print("  [%s] temple 解析失败 %s: %s" % (season, tp, e))
            continue
        n = 0
        for lv in data.get("levels", []):
            fn = lv.get("filename")
            if fn:
                rels.add(norm("data/" + fn))
                n += 1
        print("  [%s] %s -> %d 关" % (season, tp, n))

    rels.discard(None)
    print("[%s] 待下载 %d 个文件" % (season, len(rels)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda r: download(season, r, ref), sorted(rels)))


def main():
    only = sys.argv[1:] or list(SEASONS)
    t0 = time.time()
    for s in only:
        build_season(s)
        print("[%s] 累计: 下载 %d, 404 %d, 失败 %d, %.1f MB"
              % (s, STATS["ok"], STATS["missing"], STATS["fail"], STATS["bytes"] / 1048576))
    print("\n完成, 耗时 %.0fs, 总计 %.1f MB" % (time.time() - t0, STATS["bytes"] / 1048576))
    if ERRORS:
        print("失败项:")
        for e in ERRORS[:30]:
            print("  ", e)


if __name__ == "__main__":
    main()
