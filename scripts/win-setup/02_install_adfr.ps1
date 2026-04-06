# 02_install_adfr.ps1
# 安装 ADFR Suite 到 D:\drylab-tools\ADFRsuite
#
# 下载方式：
#   https://ccsb.scripps.edu/adfr/downloads/
#   注册账号后下载 Windows 64-bit 安装包
#   将安装包放到 D:\drylab-tools\installers\ADFRsuite_Windows_x86_64.exe

$install_root = "D:\drylab-tools"
$installer_dir = "$install_root\installers"
$adfr_dir = "$install_root\ADFRsuite"
# 自动找安装包（匹配多种命名格式）
$installer = Get-ChildItem $installer_dir -Include "ADFRsuite*.exe","ADFRsuite*Setup*.exe" -Recurse |
             Sort-Object LastWriteTime -Descending |
             Select-Object -First 1 -ExpandProperty FullName

if (-not $installer) {
    Write-Host "ERROR: 未找到 ADFR Suite 安装包"
    Write-Host "请将安装包放到: $installer_dir\"
    Write-Host "下载地址: https://ccsb.scripps.edu/adfr/downloads/"
    exit 1
}

New-Item -ItemType Directory -Force -Path $install_root | Out-Null

Write-Host "找到安装包: $installer"
Write-Host "安装 ADFR Suite 到 $adfr_dir ..."
Start-Process -FilePath $installer -ArgumentList "/S", "/D=$adfr_dir" -Wait -NoNewWindow

# 检查可用的 prepare_receptor 入口
$receptor_exe = $null
@("$adfr_dir\bin\prepare_receptor.exe",
  "$adfr_dir\bin\prepare_receptor",
  "$adfr_dir\bin\prepare_receptor4.py") | ForEach-Object {
    if (Test-Path $_ -and $null -eq $receptor_exe) { $receptor_exe = $_ }
}

if ($receptor_exe) {
    Write-Host "prepare_receptor OK: $receptor_exe"
} else {
    Write-Host "WARNING: prepare_receptor 未找到，列出 bin 目录内容："
    Get-ChildItem "$adfr_dir\bin" | Select-Object Name
}

Write-Host "ADFR Suite 安装完成，路径: $adfr_dir"
