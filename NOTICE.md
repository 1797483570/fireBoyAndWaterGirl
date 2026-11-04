# 版权与第三方内容说明（NOTICE）

本文件说明仓库中**不属于** MIT 许可范围的内容。

## 本项目自写部分

以下内容版权归 **wushaoheng** 所有，采用 [MIT License](LICENSE)：

- `index.html`（大厅界面与全部交互逻辑）
- `tools/serve.py`、`tools/mirror.py`、`tools/check_case.py`
- `启动游戏.bat`、`.github/`、所有 Markdown 文档
- `saves/progress.json` 的文件格式设计

## 第三方游戏内容

`games/` 目录下是 **Fireboy and Watergirl** 系列 H5 游戏的原站构建产物，
包含其程序代码、美术资源、音频、字体与关卡数据。

**这些内容的全部权利归其各自权利人所有**（游戏由 Oslo Albet 开发，KiZi 等主体发行），
**不在本项目的 MIT 授权范围内**。

它们仅以「个人离线备份 / 技术学习」为目的收录于此，未作任何修改（除补齐原站本身 404 的
PWA `manifest.json` 与图标占位）。

如需将上述游戏内容用于商业用途、公开分发或二次创作，请自行向权利人取得授权。

## 依赖

本项目无第三方代码依赖：

- 大厅：原生 HTML / CSS / JavaScript，无框架、无 CDN
- 脚本：仅 Python 3 标准库（`http.server`、`json`、`os` 等）
