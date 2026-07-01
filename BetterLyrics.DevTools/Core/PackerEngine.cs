using System.IO.Compression;
using System.Text.Json;

namespace BetterLyrics.DevTools.Core
{
    public static class PackerEngine
    {
        public static void ExecutePack(string hostSlnDir, string pluginSlnDir, string outputDir, Action<string> logInfo, Action<string> logWarning, Action<string> logError)
        {
            if (string.IsNullOrEmpty(hostSlnDir) || !Directory.Exists(hostSlnDir))
            {
                logError($"Host solution directory is invalid or does not exist: {hostSlnDir}");
                return;
            }

            string hostJsonPath = FindHostDepsJson(hostSlnDir);
            if (string.IsNullOrEmpty(hostJsonPath))
            {
                logError("Host deps.json file not found.");
                return;
            }

            string pluginBinDir = FindPluginBinDir(pluginSlnDir);
            if (string.IsNullOrEmpty(pluginBinDir))
            {
                logError("Plugin bin directory not found.");
                return;
            }

            var hostAssemblies = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try
            {
                using var jsonDoc = JsonDocument.Parse(File.ReadAllText(hostJsonPath));
                ExtractDlls(jsonDoc.RootElement, hostAssemblies);
            }
            catch (Exception ex)
            {
                logWarning($"Host JSON parsing failed ({ex.Message}), falling back to full packaging.");
                hostAssemblies.Clear();
            }

            string pluginDepsJson = Directory.GetFiles(pluginBinDir, "*.deps.json").FirstOrDefault();
            var pluginAssemblies = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            bool useStrictMode = false;

            if (!string.IsNullOrEmpty(pluginDepsJson) && File.Exists(pluginDepsJson))
            {
                try
                {
                    using var jsonDoc = JsonDocument.Parse(File.ReadAllText(pluginDepsJson));
                    ExtractDlls(jsonDoc.RootElement, pluginAssemblies);
                    useStrictMode = true;
                }
                catch { }
            }

            var keepAssemblies = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            if (useStrictMode)
            {
                keepAssemblies = new HashSet<string>(pluginAssemblies.Except(hostAssemblies), StringComparer.OrdinalIgnoreCase);
            }

            string pluginDllPath = Directory.GetFiles(pluginBinDir, "*.dll")
                .Select(Path.GetFileName)
                .FirstOrDefault(f => !f.Contains("Core", StringComparison.OrdinalIgnoreCase) && !f.Contains("DevTools", StringComparison.OrdinalIgnoreCase));

            string pluginName = !string.IsNullOrEmpty(pluginDllPath) ? Path.GetFileNameWithoutExtension(pluginDllPath) : "Plugin";
            string blpFilename = $"{pluginName}.v1.0.0.blp";
            string finalBlpPath = Path.Combine(outputDir, blpFilename);

            int trimCount = 0;
            string stagingDir = Path.Combine(Path.GetTempPath(), $"BL_Packer_{Guid.NewGuid():N}");
            Directory.CreateDirectory(stagingDir);

            try
            {
                var allFiles = Directory.GetFiles(pluginBinDir, "*.*", SearchOption.AllDirectories);
                foreach (var file in allFiles)
                {
                    string fileName = Path.GetFileName(file);
                    string fileExt = Path.GetExtension(file).ToLowerInvariant();
                    string relPath = Path.GetRelativePath(pluginBinDir, file);

                    bool isTrimmed = false;

                    if (fileExt == ".dll")
                    {
                        if (useStrictMode)
                        {
                            if (!keepAssemblies.Contains(fileName) && !fileName.Equals(pluginDllPath, StringComparison.OrdinalIgnoreCase))
                                isTrimmed = true;
                        }
                        else
                        {
                            if (hostAssemblies.Contains(fileName) || fileName.Equals("BetterLyrics.Core.dll", StringComparison.OrdinalIgnoreCase))
                                isTrimmed = true;
                        }
                    }

                    if (isTrimmed)
                    {
                        trimCount++;
                        continue;
                    }

                    string fnLower = fileName.ToLowerInvariant();
                    if (fnLower.Contains("_trimmingconfig") || fnLower.Contains("_trimmerroots") || fileExt == ".pdb")
                        continue;

                    string destPath = Path.Combine(stagingDir, relPath);
                    string destFolder = Path.GetDirectoryName(destPath);
                    if (!Directory.Exists(destFolder)) Directory.CreateDirectory(destFolder);

                    File.Copy(file, destPath, true);
                }

                if (!Directory.Exists(outputDir)) Directory.CreateDirectory(outputDir);
                if (File.Exists(finalBlpPath)) File.Delete(finalBlpPath);

                ZipFile.CreateFromDirectory(stagingDir, finalBlpPath, CompressionLevel.Optimal, false);

                logInfo($"Successfully packed! Trimmed {trimCount} redundant dependencies. Output: {finalBlpPath}");
            }
            finally
            {
                if (Directory.Exists(stagingDir)) Directory.Delete(stagingDir, true);
            }
        }

        private static string FindHostDepsJson(string slnDir)
        {
            try
            {
                var files = Directory.GetFiles(slnDir, "*.deps.json", SearchOption.AllDirectories)
                    .Where(f => !f.Contains(@"\obj\", StringComparison.OrdinalIgnoreCase) &&
                                !f.Contains("BetterLyrics.Core", StringComparison.OrdinalIgnoreCase))
                    .Where(f => Path.GetFileName(f).Equals("BetterLyrics.WinUI3.deps.json", StringComparison.OrdinalIgnoreCase) ||
                                Path.GetFileName(f).Equals("BetterLyrics.deps.json", StringComparison.OrdinalIgnoreCase))
                    .ToList();

                return files.OrderByDescending(f => new FileInfo(f).LastWriteTime).FirstOrDefault();
            }
            catch { return null; }
        }

        private static string FindPluginBinDir(string pluginSlnDir)
        {
            try
            {
                var allDepsFiles = Directory.GetFiles(pluginSlnDir, "*.deps.json", SearchOption.AllDirectories)
                    .Where(f => !f.Contains(@"\obj\", StringComparison.OrdinalIgnoreCase))
                    .ToList();

                if (!allDepsFiles.Any()) return null;

                return Path.GetDirectoryName(allDepsFiles.OrderByDescending(f => new FileInfo(f).LastWriteTime).First());
            }
            catch { return null; }
        }

        private static void ExtractDlls(JsonElement element, HashSet<string> outSet)
        {
            if (element.ValueKind == JsonValueKind.String)
            {
                string val = element.GetString();
                if (val != null && val.EndsWith(".dll", StringComparison.OrdinalIgnoreCase))
                    outSet.Add(Path.GetFileName(val));
            }
            else if (element.ValueKind == JsonValueKind.Object)
            {
                foreach (var prop in element.EnumerateObject())
                {
                    if (prop.Name.EndsWith(".dll", StringComparison.OrdinalIgnoreCase))
                        outSet.Add(Path.GetFileName(prop.Name));
                    ExtractDlls(prop.Value, outSet);
                }
            }
            else if (element.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in element.EnumerateArray()) ExtractDlls(item, outSet);
            }
        }
    }
}