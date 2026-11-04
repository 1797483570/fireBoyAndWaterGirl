# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 结构，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 大厅：赛季内关卡缩略预览
- 存档：按赛季维度查看历史变化

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
