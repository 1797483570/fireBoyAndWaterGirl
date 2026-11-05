# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 结构，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 大厅：赛季内关卡缩略预览
- 存档：按赛季维度查看历史变化

## [1.3.1] - 2026-11-04

### 修复
- **iPhone / iPad 横屏时内容被前置摄像头（灵动岛）遮挡**：
  `fit()` 改为先读 `env(safe-area-inset-left/right/top/bottom)`，
  把 `#stage` 按安全区内缩，可用宽高改为 `视口 - 安全区`，缩放基准同步换算
- 监听 `visualViewport` 的 `resize`，iOS 地址栏收起 / 展开时自动重排
- 竖屏引导页 `#rotate` 的内边距同样考虑安全区，文字不再贴着灵动岛
- 手机横屏主区内边距从 `18px` 提到 `22px`
- 安全区用「临时元素 + 四个方向的 `padding: env()`」探测（比读自定义属性可靠，
  各版本 Safari 对自定义属性里 `env()` 的求值行为不一致）；旋转屏幕后重新探测
- 控制台注入 `window.__FB_SAFE = {left,right,top,bottom}` 可模拟刘海，方便桌面调试，内容不贴安全区边缘

## [1.3.0] - 2026-11-04

### 新增
- **自动推送到 git**：写盘成功后，`serve.py` 在后台线程自动 `git add / commit / push`；
  仅当目录是 git 仓库、有 remote、分支有 upstream、凭据可用时执行，任一不满足只写文件
- `GET /api/git` 返回最近一次推送状态（`idle` / `pushing` / `pushed` / `pending` / `disabled`）
- 存档按钮 tooltip 显示推送结果，手动保存会提示「进度已推送到仓库」
- 环境变量 `FB_NO_GIT=1` 可关闭自动推送
- 推送串行执行，上一轮未结束时自动跳过，避免并发冲突

### 变更
- **在线访问（GitHub Pages）不再读取仓库存档**，改为只用访问者浏览器本地存档，
  避免把自己的进度暴露给线上访客；移除 `readonly` 只读模式与对应蓝灯
- `offline` 状态文案改为中性的「本地浏览器存档」

## [1.2.0] - 2026-11-04

### 新增
- 支持 **GitHub Pages 只读部署**：无 `/api/ping` 时自动改读 `saves/progress.json`
- 存档状态新增 🔵 `readonly`（只读托管），只读模式不触发自动回写
- `.nojekyll`，跳过 Jekyll 直接发布原始文件
- `tools/check_case.py`：校验静态托管的路径大小写一致性
- 仓库标准化：README 徽章与目录、LICENSE、CONTRIBUTING、CHANGELOG、Issue/PR 模板、`.editorconfig`

### 变更
- README 重组，补充常见问题与许可说明

## [1.1.0] - 2026-11-04

### 新增
- 存档同步：`saves/progress.json` 作为仓库真源，随代码提交
- `tools/serve.py`：静态服务 + `GET/POST /api/save`、`GET /api/ping`，写前自动备份
- 大厅存档按钮与四态指示灯，切回大厅 / 每 4 秒轮询 / 手动三种保存触发
- 存档合并策略：**逐关取较优**，仓库优先且不丢浏览器新进度
- `.gitignore`：忽略存档备份与临时文件

### 变更
- `启动游戏.bat` 改用 `tools/serve.py`，并在启动横幅显示存档路径

## [1.0.0] - 2026-11-04

### 新增
- 7 季游戏本体完整镜像（A–G，293 关，82 MB / 841 文件），保持原站相对路径
- PS5 风格大厅：横向卡片轮播、环形进度、赛季 logo 与描述
- 交互：键盘 `← → ↑ ↓ Home End Enter Space F`、滚轮切换、按住拖拽跟手
- 桌面以 860px 高为基准等比缩放；手机横屏专用布局；竖屏引导页
- `tools/mirror.py`：幂等镜像脚本，可增量补齐
- 作品页风格：影院暗黑金主题、封面模糊图层交叉淡入、噪点与光晕
