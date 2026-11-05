# 森林冰火人 H5 · 本地离线版

[![License: MIT](https://img.shields.io/badge/License-MIT-e8c684.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg)](https://www.python.org/)
[![No Build](https://img.shields.io/badge/build-none-8bd46f.svg)](#快速开始)
[![Offline](https://img.shields.io/badge/offline-ready-7fd8ff.svg)](#快速开始)
[![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-222.svg)](#部署到-github-pages)

把官方在线的 **Fireboy & Watergirl H5 全 7 季（A–G，293 关）** 完整镜像到本地，
并配了一个 **PS5 风格**的统一大厅入口页。

- 🎮 **全程离线可玩** —— 不依赖任何线上接口，双击就能进
- 🖼️ **影院级大厅** —— 横向卡片轮播、环形进度、键盘 / 滚轮 / 拖拽三种操作
- 💾 **存档随仓库走** —— 进度落在 `saves/progress.json`，换机器 clone 下来接着玩
- 📱 **多端适配** —— 桌面等比缩放、手机横屏专用布局、竖屏引导页
- 🧩 **零构建** —— 单文件 HTML + 原生 JS，无 npm、无打包、无依赖

---

## 目录

- [快速开始](#快速开始)
- [目录结构](#目录结构)
- [大厅怎么用](#大厅怎么用)
- [存档同步（随仓库走）](#存档同步随仓库走)
- [部署到 GitHub Pages](#部署到-github-pages)
- [适配](#适配)
- [本地服务接口](#本地服务接口)
- [重新镜像 / 增量补齐](#重新镜像--增量补齐)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [许可](#许可)
- [致谢](#致谢)

---

## 快速开始

**双击 `启动游戏.bat`** —— 会自动起一个本地服务并打开浏览器大厅。

> ⚠️ 必须走本地 HTTP 服务，直接双击 `index.html`（file:// 协议）会白屏，
> 因为游戏用 RequireJS 动态加载关卡 JSON，file:// 下被浏览器安全策略拦掉。
> 另外**只有用 `启动游戏.bat` 启动才能保存存档**（纯静态服务没有写文件的接口）。

如果 8123 端口被占用，脚本会自动顺延到 8124、8125……

> 📌 浏览器按「协议+主机+端口」隔离 localStorage，
> **换了端口，游戏存档就看不到之前的进度了**。想延续存档请固定用 8123。

需要 Python 3（Windows 一般自带或可从 python.org 安装，安装时勾选 *Add Python to PATH*）。

## 目录结构

```
森林冰火人H5/
├── index.html          # 大厅入口页（单文件，无外部依赖）
├── 启动游戏.bat        # 双击启动：本地服务 + 打开浏览器
├── games/              # 7 季游戏本体（82 MB / 841 文件 / 293 关）
│   ├── A/dist/         # 森林圣殿 48 关
│   ├── B/dist/         # 光明圣殿 45 关
│   ├── C/dist/         # 寒冰圣殿 53 关
│   ├── D/dist/         # 水晶殿   39 关
│   ├── E/dist/         # 元素（7 神殿）39 关
│   ├── F/dist/         # 童话    32 关（入口是 index.htm）
│   └── G/dist/         # 朋友    37 关
├── saves/
│   └── progress.json   # 存档（7 季合一，跟着 git 提交走）
└── tools/
    ├── serve.py        # 本地服务：静态文件 + 存档读写接口
    └── mirror.py       # 幂等镜像脚本，可重跑做增量补齐
```

每季都严格保持原站的相对路径（`games/<季>/dist/...`），
游戏内部的 `../../../assets/...`、`../../api/...` 等引用因此无需任何改动。

---

## 大厅怎么用

| 操作 | 说明 |
| --- | --- |
| `←` `→` / `↑` `↓` | 切换赛季 |
| `Home` / `End` | 跳到第一 / 最后一季 |
| `Enter` / 空格 | 启动当前赛季 |
| `F` | 全屏 |
| 鼠标滚轮 | 切换赛季 |
| 按住拖拽卡片 | 跟手移动，松手超过 1/4 卡宽才切一张（不会连跳） |
| 点卡片 | 未选中的卡点一下选中，选中卡再点直接进游戏 |

- 右上角显示**总星数**和**总通关数**，数据实时读自存档。
- 每张卡上的 `0 / 48 关` 和左侧环形进度，都是该季真实进度。
- 地址栏 `#A`–`#G` 可直接定位到某一季（可收藏）。
- 游戏在**新标签页**打开，大厅页保留，随时可以切回去换季。

---

## 存档同步（随仓库走）

### 存在哪

| 位置 | 作用 |
| --- | --- |
| `saves/progress.json` | **仓库真源**，7 季合成一个文件，提交后随代码走 |
| 浏览器 localStorage | 游戏本体只认它，每次启动由大厅从仓库档灌入 |

存档文件结构：

```json
{
  "version": 1,
  "updatedAt": "2026-11-04T08:25:54.201Z",
  "saves": {
    "fb-forest": { "temples": [...], "gameComplete": false },
    "fb-light":  { ... }
  }
}
```

localStorage key 对照：`fb-forest` / `fb-light` / `fb-ice` / `fb-crystal` / `fb-elements` / `fb-fairytales` / `fb-friends` + `:progress`。

### 怎么流转

```
启动大厅 ──GET /api/save──▶ 仓库档
                              │
                       逐关合并（取较优）
                              │
                    ▼          ▼
              localStorage  ◀──┘   ──▶ 游戏读到仓库里的进度
                              │
   玩完切回大厅 / 每 4 秒轮询 / 点存档按钮
                              │
                    POST /api/save
                              ▼
                    saves/progress.json
                              │
              写盘成功后（仅本地启动、且有推送权限时）
                              ▼
                    git add + commit + push
                              │
                    远端仓库 · GitHub Pages
```

### 合并规则（仓库优先 + 兼容浏览器存档）

- 同一关两边都有 → 取 `best.stars` **更高的那份**
- 只在浏览器有（刚玩、还没同步）→ **保留，不会被旧仓库档吃掉**
- 只在仓库有 → 补进浏览器
- 整季浏览器没有 → 直接用仓库档
- 关卡结构以当前浏览器档为骨架（防止旧结构的仓库档打乱选关界面）

### 什么时候写回仓库

| 时机 | 行为 |
| --- | --- |
| 大厅加载时 | 读仓库档合并进 localStorage；若合并后发现浏览器独有进度，**自动回写** |
| 切回大厅标签页（focus / visibilitychange） | 检测差异，有变化自动写回 |
| 每 4 秒（页面可见时） | 同上，兜底 |
| 点右上角存档按钮 | 手动保存，并弹提示 |

### 自动推送到 git

写盘成功后，`serve.py` 会**在后台线程**里自动执行一次：

```bash
git add saves/progress.json
git commit -m "save: 自动保存进度 2026-11-04 18:48"
git push origin HEAD
```

只有三个条件全满足才会推：

1. 当前目录是 git 仓库，且配了 remote
2. 当前分支有 upstream（`origin/main`）
3. git 凭据可用（Windows 凭据管理器 / SSH key），且**不会弹交互窗口**

任一条件不满足就只写文件、不动 git，前端提示「已保存，但推送未完成：<原因>」。
设环境变量 `FB_NO_GIT=1` 可彻底关掉自动推送。

> 推送是后台进行的，页面不会卡。存档按钮的 tooltip 会显示最近一次结果，
> 比如「存档已写入仓库 · 已推送 save: 自动保存进度 18:48」。

#### 为什么不自己手写 `git commit` 了

自动推送已经覆盖日常场景，`save:` 前缀的提交会由脚本产生。
你想手动改存档再提交也完全可以，两者不冲突。

### 存档按钮的三种状态

| 指示灯 | 状态 | 含义 |
| --- | --- | --- |
| 🟢 绿 | synced | 已写入 `saves/progress.json`（tooltip 会附上推送结果） |
| 🟡 金 | dirty | 有进度未写入，正在/等待保存 |
| ⚪ 灰 | offline | 没走 `启动游戏.bat`（在线访问 / file:// / 无 API 的静态服务），只存浏览器 |

> `offline` 下游戏照常能玩，只是进度不会落到 `saves/progress.json`，也不会推送到 git。

### 手动提交（可选）

自动推送失败时（比如当时没网），补救就是：

```bash
git add saves/progress.json
git commit -m "save: 森林圣殿 12/48"
git push
```

> 换机器拉到代码后直接双击 `启动游戏.bat`，大厅会把 `saves/progress.json` 灌进新浏览器的 localStorage，进度无缝接着玩。
> 多台机器同时推进度时，`git pull` 若在 `saves/progress.json` 报冲突，**随便选一边、下再启动一次大厅即可**——大厅会把两边的进度按「取较优」重新合并回写。

---

## 部署到 GitHub Pages

可以直接部署，本项目已针对静态托管做过适配：

- 全部资源都是**相对路径**（已扫描 1740 处引用，0 处绝对路径、0 处大小写不一致）
- 已加 `.nojekyll`，跳过 Jekyll 构建，直接发布原始文件
- 单文件最大 2.5 MB，远低于 Pages 的 100 MB 限制

### 开启方式

仓库 → **Settings → Pages** → Source 选 `Deploy from a branch` → Branch 选 `main` / `(root)` → Save。

地址为：`https://1797483570.github.io/fireBoyAndWaterGirl/`

> ⚠️ 私有仓库需要 GitHub Pro 才能开启 Pages（免费账号的 Pages 只支持 public 仓库）。
> 本仓库是 public，Pages 已开启。

### 线上访问**不读**仓库里的存档

这是刻意设计的：GitHub Pages 上没有 `/api/ping`，大厅会直接判定为 `offline`，
**完全不读** `saves/progress.json`，只用访问者自己浏览器里的 localStorage。

| 能力 | 本地 `启动游戏.bat` | GitHub Pages |
| --- | --- | --- |
| 读 `saves/progress.json` 灌进浏览器 | ✅ | ❌（刻意不读） |
| 玩完写回 `saves/progress.json` | ✅ | ❌ |
| 自动 commit + push | ✅（有权限时） | ❌ |
| 用自己的浏览器存档 | ✅ | ✅ |

原因：仓库里的存档是**你自己的**进度，线上访问者（包括陌生人）不该看到它，
也不该被它覆盖。所以线上就是一份干净的、从零开始的独立体验。

> 想把自己的进度带到线上？做不到，也不打算做 —— 线上存档按浏览器隔离。

### 体积提醒

仓库 82 MB，Pages 站点上限 1 GB / 单文件 100 MB，都在范围内。
但玩家进入某一季要下载 9–13 MB，首次加载会比本地慢一些；大厅首屏只加载封面图（约 500 KB）。

---

## 适配

- **桌面**：以 860px 高为设计基准等比缩放，宽度自适应；超宽屏会显示更多卡片。
- **手机横屏**：自动切到「左信息 / 右卡片」布局，用 470px 基准，元素不会被缩得过小；
  顶栏保留总星数 / 总通关数（紧凑胶囊，`✓` 代替「已通关」文字）。
- **手机 / 平板竖屏**：大厅改为**纵向布局**（info 区在上、卡片轮播在下），照常浏览与选关；
  点「开始游戏」会提示「进入游戏后请横屏游玩」——游戏本体是横屏的，这一步躲不掉。
  切换方向时自动重排，不用刷新。
- **安全区（刘海 / 灵动岛 / 圆角）**：读取 `env(safe-area-inset-*)`，整个舞台按安全区内缩，
  内容不会被 iPhone 横屏时的前置摄像头、圆角或底部 home indicator 遮挡；
  `visualViewport` 变化（iOS 地址栏收起 / 展开）时也会重排。
  想在桌面上预演，控制台执行 `window.__FB_SAFE = {left:59,right:59,top:0,bottom:21}` 再触发一次 resize 即可。
  竖屏时兜底的是顶部灵动岛与底部 home indicator（59 / 34pt）。
  真机自查：地址后加 `?debug=1`，左上角会显示 `v1.3.2 SAFE L/R/T/B · win · screen`。
  若 `env()` 被浏览器报成 0，代码会按机型兜底（iPhone 横屏、屏幕长边 ≥ 812pt → 左右 59 / 44pt）。

---

## 本地服务接口

`tools/serve.py`（Python 标准库，零依赖，只监听 127.0.0.1）：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/ping` | 探活，返回 `{"ok":true,"save":true,"git":true}` |
| GET | `/api/save` | 返回存档（不存在则 404） |
| POST | `/api/save` | 整份覆盖写入，写前备份 `progress.bak.json`，成功后后台自动 git 提交推送 |
| GET | `/api/git` | 最近一次自动推送状态：`idle` / `pushing` / `pushed` / `pending` / `disabled` |

`/api/git` 的 `pending` 表示「文件已写入但没推上去」（没网、没权限、分支无 upstream 等），
`message` 字段会带失败原因。

也可以手动起：

```bash
python tools/serve.py 8123
```

---

## 重新镜像 / 增量补齐

```bash
python tools/mirror.py
```

脚本是幂等的：已存在的文件跳过，缺的补下。改 `SEASONS` / `COMMON` / `AUDIO` / `EXTRA` 配置可调整抓取范围。

原站首页（游戏列表、云同步、关卡预览）依赖 `../api/`，没有镜像；
本项目的游戏本体已确认**不依赖**这些接口，纯离线可玩。
PWA 的 `manifest.json` 与部分图标在原站就是 404，用现有图标做了占位，不影响运行。

---

## 常见问题

**Q：双击 `index.html` 一片空白？**
A：file:// 下 RequireJS 加载关卡 JSON 会被安全策略拦截，必须走本地 HTTP 服务，用 `启动游戏.bat`。

**Q：右上角存档灯是灰的 / 蓝的？**
A：绿色 = 已写入 `saves/progress.json`（tooltip 会附推送结果）；金色 = 有进度待写入；灰色 = 没走 `启动游戏.bat`，只存浏览器。详见[存档同步](#存档同步随仓库走)。

**Q：换端口后进度没了？**
A：localStorage 按 origin 隔离，`127.0.0.1:8123` 和 `:8124` 是两份存档。固定用 8123 即可。

**Q：自动推送失败 / 不想让它自动提交？**
A：看 `/api/git` 返回的 `message`（没网、没权限、分支无 upstream 都可能）。设 `FB_NO_GIT=1` 再启动可彻底关闭自动推送，只写文件。

**Q：玩完在另一台机器上看不到进度？**
A：先在玩的那台上让大厅把进度写进 `saves/progress.json`（回大厅自动写），commit + push；另一台 `git pull` 后重开大厅。

**Q：`git pull` 时 `saves/progress.json` 冲突了？**
A：随便选一边解决冲突，再启动一次大厅 —— 合并逻辑会按「逐关取较优」把两边进度合起来并回写。

**Q：能在线玩吗？**
A：可以，见[部署到 GitHub Pages](#部署到-github-pages)。线上访问不读仓库存档，用访问者自己浏览器的 localStorage，从零开始。

---

## 贡献

欢迎提 Issue / PR，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 许可

本项目**自写部分**（大厅 `index.html`、`tools/` 下的脚本、文档）采用 [MIT License](LICENSE)。

⚠️ `games/` 下的游戏本体（*Fireboy and Watergirl* 系列的程序、美术、音频、关卡数据）
版权归其各自权利人所有，**不在 MIT 授权范围内**，仅作为个人离线备份与学习用途收录于此。
如需商用或再分发，请自行取得授权。详见 [NOTICE.md](NOTICE.md)。

---

## 致谢

- 游戏原作：[Fireboy and Watergirl](https://www.fireboyandwatergirl.net/)（Oslo Albet / KiZi）
- 本项目只做了本地镜像与大厅封装，游戏本身的乐趣全归原作者

如果这个项目对你有帮助，给个 ⭐ 就行。
