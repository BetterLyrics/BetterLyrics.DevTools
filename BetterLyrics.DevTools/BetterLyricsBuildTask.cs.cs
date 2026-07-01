using Microsoft.Build.Framework;
using BetterLyrics.DevTools.Core;

namespace BetterLyrics.DevTools
{
    public class BetterLyricsBuildTask : Microsoft.Build.Utilities.Task
    {
        [Required]
        public string ProjectDir { get; set; }

        public string HostSlnDir { get; set; }

        public override bool Execute()
        {
            // 封装委托，桥接 MSBuild 的日志系统
            Action<string> logInfo = msg => Log.LogMessage(MessageImportance.High, $"[DevTools] {msg}");
            Action<string> logWarning = msg => Log.LogWarning($"[DevTools Warning] {msg}");
            Action<string> logError = msg => Log.LogError($"[DevTools Error] {msg}");

            logInfo("Launch Build Task for BetterLyrics DevTools");

            string outputLangs = Path.Combine(ProjectDir, "Langs");
            string outputDist = Path.Combine(ProjectDir, "Dist");

            string hostDir = string.IsNullOrEmpty(HostSlnDir)
                ? Path.Combine(ProjectDir, @"..\..\BetterLyrics")
                : HostSlnDir;

            try
            {
                // 1. 生成多语言
                logInfo("Extracting and generating I18n language files...");
                I18nGeneratorEngine.ExecuteGenerate(ProjectDir, outputLangs, logInfo, logWarning, logError);

                // 2. 打包精简
                logInfo("Executing smart dependency trimming and .blp packaging...");
                PackerEngine.ExecutePack(hostDir, ProjectDir, outputDist, logInfo, logWarning, logError);

                return true;
            }
            catch (Exception ex)
            {
                logError($"Fatal Exception: {ex}");
                return false;
            }
        }
    }
}