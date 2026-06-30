# BetterLyrics.DevTools

BetterLyrics 插件打包与依赖裁剪工具。基于 Python 和 PyQt5 (`qfluentwidgets`) 编写。

主要用于读取宿主程序的依赖清单，与插件自身的编译产物进行比对，自动剔除冗余的公共依赖（如 `BetterLyrics.Core.dll`），并将精简后的产物打包为 `.blp` 格式。

## 目录结构

```text
BetterLyricsDevTools/
├── main.py                     # 程序入口与窗体初始化
├── i18n.py                     # 国际化配置与翻译字典
└── views/
    ├── __init__.py
    ├── packer_interface.py     # 打包逻辑、文件比对与依赖裁剪核心
    └── settings_interface.py   # 主题 (Dark/Light) 与语言设置

```

## 运行环境

需要 Python 3.8+。

安装必要的 GUI 依赖：

```bash
pip install PyQt5 PyQt5-Tools qfluentwidgets
```

启动工具：

```bash
python main.py
```

## 使用说明

1. **Host JSON**：选择 BetterLyrics 主程序的依赖清单（如 `*.deps.json`）。程序会提取其包含的 DLL 作为去重白名单。
2. **Plugin Bin**：选择插件的编译输出目录（如 `bin/Release/...`）。
3. **Dist Output**：指定打包后 `.blp` 文件的存放位置。
4. 点击 **剪裁并打包 (.blp)**。

### 裁剪逻辑 (Smart Trim)

* **严格模式 (双 JSON 比对)**：如果插件目录内存在自身的 `deps.json`，程序会自动计算宿主与插件依赖的差集，精准保留插件特有的第三方依赖。
* **常规降级模式**：若插件缺少 `deps.json`，程序会遍历目录，只要是在宿主白名单里出现的 DLL 都会被直接剔除。
* **文件过滤**：打包过程会自动丢弃 `.pdb`、`_trimmingconfig` 等开发环境产物，并对插件主入口 DLL 做了防误杀保护。

## License

MIT License © BetterLyrics