# 02_install_adfr.ps1
# 安装 ADFR Suite 到 D:\ADFRsuite
# 需要先从 https://ccsb.scripps.edu/adfr/downloads/ 手动下载安装包
# 下载后放到 C:\Users\Administrator\ADFRsuite_x86_64Windows_1.0.exe

$installer = "C:\Users\Administrator\ADFRsuite_x86_64Windows_1.0.exe"
$install_dir = "D:\ADFRsuite"

if (-not (Test-Path $installer)) {
    Write-Host "ERROR: 未找到安装包 $installer"
    Write-Host "请先从 https://ccsb.scripps.edu/adfr/downloads/ 下载 Windows 版本"
    Write-Host "（需要注册账号，学术免费）"
    exit 1
}

Write-Host "安装 ADFR Suite 到 $install_dir ..."
Start-Process -FilePath $installer -ArgumentList "/S", "/D=$install_dir" -Wait -NoNewWindow

Write-Host "验证 prepare_receptor..."
if (Test-Path "$install_dir\bin\prepare_receptor.exe") {
    & "$install_dir\bin\prepare_receptor.exe" --help 2>&1 | Select-Object -First 3
    Write-Host "prepare_receptor OK"
} elseif (Test-Path "$install_dir\bin\prepare_receptor4.py") {
    Write-Host "prepare_receptor4.py 可用（需通过 ADFR Python 调用）"
} else {
    Write-Host "WARNING: prepare_receptor 未找到，检查安装路径"
    Get-ChildItem "$install_dir\bin" | Select-Object Name
}

Write-Host "验证 prepare_ligand..."
if (Test-Path "$install_dir\bin\prepare_ligand.exe") {
    Write-Host "prepare_ligand OK"
} elseif (Test-Path "$install_dir\bin\prepare_ligand4.py") {
    Write-Host "prepare_ligand4.py 可用"
}

Write-Host "ADFR Suite 安装完成，路径: $install_dir\bin"
