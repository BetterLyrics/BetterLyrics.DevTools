using System.Reflection;
using System.ComponentModel.DataAnnotations;
using System.Text.Json;

namespace BetterLyrics.DevTools.Core
{
    public static class I18nGeneratorEngine
    {
        private static readonly string[] TargetLanguages = new[]
        {
            "en", "ar", "de", "es", "fr", "hi", "id", "it", "ja",
            "ko", "ms", "pt", "ru", "th", "vi", "zh-Hans", "zh-Hant"
        };

        // 引入 Action 委托，用于向外部（MSBuild）汇报日志
        public static void ExecuteGenerate(string pluginSlnDir, string outputDir, Action<string> logInfo, Action<string> logWarning, Action<string> logError)
        {
            if (string.IsNullOrEmpty(pluginSlnDir) || !Directory.Exists(pluginSlnDir))
            {
                logError("Invalid plugin solution directory.");
                return;
            }

            string assemblyPath = FindLatestPluginDll(pluginSlnDir);
            if (string.IsNullOrEmpty(assemblyPath))
            {
                logError("Cannot find any valid compiled assembly (.dll) in the solution directory.");
                return;
            }

            try
            {
                logInfo($"Parsing assembly: {Path.GetFileName(assemblyPath)}");

                var assembly = Assembly.LoadFrom(assemblyPath);
                var baseDict = new Dictionary<string, string>();

                var configTypes = assembly.GetTypes()
                    .Where(t => t.IsClass && !t.IsAbstract && (t.Name.EndsWith("Config") || t.BaseType?.Name == "PluginConfigBase"));

                foreach (var type in configTypes)
                {
                    var properties = type.GetProperties(BindingFlags.Public | BindingFlags.Instance);
                    foreach (var prop in properties)
                    {
                        var displayAttr = prop.GetCustomAttribute<DisplayAttribute>();
                        if (displayAttr == null) continue;

                        string prefix = type.Name;
                        string propName = prop.Name;

                        baseDict[$"{prefix}_{propName}_Name"] = displayAttr.Name ?? propName;
                        baseDict[$"{prefix}_{propName}_Desc"] = displayAttr.Description ?? "";
                    }
                }

                if (!baseDict.Any())
                {
                    logWarning("Cannot find any configuration classes with [Display] attributes in the assembly, skipping I18n generation.");
                    return;
                }

                if (!Directory.Exists(outputDir)) Directory.CreateDirectory(outputDir);

                var jsonOptions = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                };

                foreach (var lang in TargetLanguages)
                {
                    string langFilePath = Path.Combine(outputDir, $"{lang}.json");
                    File.WriteAllText(langFilePath, JsonSerializer.Serialize(baseDict, jsonOptions));
                }

                logInfo($"Successfully generated {TargetLanguages.Length} language templates in {outputDir}.");
            }
            catch (Exception ex)
            {
                logError($"Failed to extract I18n: {ex.Message}");
            }
        }

        private static string FindLatestPluginDll(string slnDir)
        {
            try
            {
                var dllFiles = Directory.GetFiles(slnDir, "*.dll", SearchOption.AllDirectories)
                    .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}", StringComparison.OrdinalIgnoreCase))
                    .Select(f => new FileInfo(f))
                    .OrderByDescending(f => f.LastWriteTime)
                    .ToList();

                return dllFiles.FirstOrDefault()?.FullName;
            }
            catch { return null; }
        }
    }
}