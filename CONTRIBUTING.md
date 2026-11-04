# 贡献指南

感谢愿意一起把这个大厅做得更好。这个项目刻意保持**零构建、零依赖**，所以上手成本很低。

## 项目约束（请先读）

| 约束 | 原因 |
| --- | --- |
| 大厅只用单文件 `index.html`（内联 CSS/JS） | 双击即用，无需 npm / 打包 |
| 不引入任何框架或 CDN 资源 | 必须能完全离线运行 |
| 不修改 `games/` 下的游戏本体 | 那是原站镜像，保持逐字节一致 |
| `tools/` 只用 Python 标准库 | 用户机器不必装第三方包 |

## 本地开发

```bash
git clone https://github.com/1797483570/fireBoyAndWaterGirl.git
cd fireBoyAndWaterGirl
python tools/serve.py 8123      # 或双击 启动游戏.bat
# 打开 http://127.0.0.1:8123/
```

大厅改完直接刷新即可，没有编译步骤。

## 提交前自检

```bash
python tools/check_case.py      # 静态托管路径大小写一致性（Linux 区分大小写）
python -m py_compile tools/serve.py tools/mirror.py tools/check_case.py
```

- [ ] 桌面（1920×1080 / 1440×900）与手机横屏（844×390）都看过
- [ ] 键盘 ← → Enter / 滚轮 / 拖拽 都还能正常切换
- [ ] 存档灯状态（🟢 synced / 🟡 dirty / 🔵 readonly / ⚪ offline）符合预期
- [ ] 没有新增外部网络请求（`grep -n "https\?://" index.html`）

## 提交信息规范

参考 Conventional Commits，中文描述即可：

```
feat: 卡片支持按住拖拽跟手切换
fix: 手机横屏下卡片被裁切
docs: 补充存档合并规则
chore: 更新镜像脚本资源清单
save: 森林圣殿 3/48
```

`saves/progress.json` 的提交统一用 `save:` 前缀，方便回溯进度变化。

## 镜像更新

想补某一季缺失的资源：

```bash
python tools/mirror.py
```

脚本幂等，已存在的文件会跳过。改 `SEASONS` / `COMMON` / `AUDIO` / `EXTRA` 可调整抓取范围。

## 不要提交的东西

- `saves/*.bak.json`、`saves/*.tmp`（`.gitignore` 已覆盖）
- `__pycache__/`、`*.pyc`
- 编辑器配置目录（`.vscode/`、`.idea/`）

## 提 PR

1. 从 `main` 切分支：`git checkout -b feat/your-idea`
2. 按上面的自检清单过一遍
3. PR 描述里说明**改了什么 / 为什么 / 怎么验证的**，有前后对比截图更好

## 版权提醒

`games/` 下的游戏内容版权归原权利人所有，请勿把本仓库的游戏素材用于商业用途或再分发。
详见 [LICENSE](LICENSE)。
