# i18n.py

CURRENT_LANG = "zh"

I18N_STRINGS = {
    "zh": {
        "packer_title": "插件打包",
        "host_json_label": "主程序配置文件 (Host JSON):",
        "host_json_ph": "请选择主程序的依赖清单 JSON 文件...",
        "btn_browse": "浏览",
        "plugin_bin_label": "插件编译输出目录 (Plugin Bin):",
        "plugin_bin_ph": "选择插件生成的 bin/Release/ 目录...",
        "dist_out_label": "包输出目标目录 (Dist Output):",
        "dist_out_ph": "指定打包后 .blp 文件的存放位置...",
        "log_label": "执行日志:",
        "btn_pack": "剪裁并打包 (.blp)",
        "nav_packer": "插件打包",
        "nav_settings": "设置",
        "settings_title": "设置",
        "theme_label": "主题模式",
        "theme_dark": "深色",
        "theme_light": "浅色",
        "lang_label": "界面语言",
        "msg_missing_title": "参数缺失",
        "msg_missing_text": "请完整提供或选择三项核心路径参数！",
        "msg_path_title": "路径错误",
        "msg_path_text": "指定的主程序 JSON 或插件目录在本地不存在！",
        "log_start": "正在解析主程序配置中...",
        "log_host_success": "成功导入宿主组件白名单，共有 {} 个组件将被动态去重。",
        "log_host_warn": "JSON 结构读取失败 ({})，降级切换为全量不剪裁打包模式。",
        "log_trim": "[Smart Trim] 剪裁冗余项: {}",
        "log_err_no_dll": "未检测到有效的插件可执行文件，流程拦截！",
        "log_end_1": "插件打包结束！",
        "log_end_2": "已为您精简拦截了 {} 个重复公共依赖。",
        "log_end_3": "最终包产物已存至: {}",
        "msg_success_title": "打包成功",
        "msg_success_text": "插件包已成功生成！\n\n目标：{}",
        "log_strict_mode": "检测到插件依赖清单: {}，启用双 JSON 严格比对模式。",
        "log_strict_fail": "插件依赖清单解析失败 ({})，降级为常规文件比对。",
        "log_strict_calc": "经计算，差集对比完成。插件独立依赖项为 {} 个。",
    },
    "en": {
        "packer_title": "Plugin Packer",
        "host_json_label": "Host Config File (Host JSON):",
        "host_json_ph": "Select host dependency JSON file...",
        "btn_browse": "Browse",
        "plugin_bin_label": "Plugin Build Output (Plugin Bin):",
        "plugin_bin_ph": "Select plugin bin/Release/ directory...",
        "dist_out_label": "Dist Output Directory:",
        "dist_out_ph": "Specify output path for .blp file...",
        "log_label": "Execution Log:",
        "btn_pack": "Trim & Pack (.blp)",
        "nav_packer": "Packer",
        "nav_settings": "Settings",
        "settings_title": "Settings",
        "theme_label": "Theme Mode",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "lang_label": "Language",
        "msg_missing_title": "Missing Parameters",
        "msg_missing_text": "Please provide all required path parameters!",
        "msg_path_title": "Path Error",
        "msg_path_text": "Host JSON or Plugin directory does not exist locally!",
        "log_start": "Parsing host configuration...",
        "log_host_success": "Successfully imported host whitelist. {} components will be trimmed.",
        "log_host_warn": "Failed to read JSON ({}). Downgrading to full pack without trimming.",
        "log_trim": "[Smart Trim] Trimmed redundant item: {}",
        "log_err_no_dll": "No valid plugin executable detected. Process aborted!",
        "log_end_1": "Plugin packing completed successfully!",
        "log_end_2": "Successfully trimmed {} redundant dependencies.",
        "log_end_3": "Final package saved to: {}",
        "msg_success_title": "Pack Success",
        "msg_success_text": "Plugin package generated successfully!\n\nTarget: {}",
        "log_strict_mode": "Plugin deps.json detected: {}. Enabling strict dual-JSON diff mode.",
        "log_strict_fail": "Failed to parse plugin deps.json ({}). Downgrading to standard diff.",
        "log_strict_calc": "Diff calculation complete. Plugin requires {} unique dependencies.",
    }
}

def tr(key):
    global CURRENT_LANG
    return I18N_STRINGS.get(CURRENT_LANG, I18N_STRINGS["zh"]).get(key, key)

def set_lang(lang):
    """安全修改全局语言状态"""
    global CURRENT_LANG
    CURRENT_LANG = lang

def get_lang():
    global CURRENT_LANG
    return CURRENT_LANG