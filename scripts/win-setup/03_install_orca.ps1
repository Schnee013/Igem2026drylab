# 03_install_orca.ps1
# 安装 Orca 到 D:\drylab-tools\orca
#
# Orca 下载方式（二选一，均需注册学术账号）：
#   官方主站（国内可能连不上）: https://orcaforum.kofo.mpg.de
#   备用入口:                   https://www.faccts.de/orca/
#
# 下载 Windows x86_64 zip 包后放到:
#   D:\drylab-tools\installers\orca_5_x_x_windows_x86-64.zip
# （文件名中的版本号不影响脚本运行，只要匹配 orca_5_*_windows_*.zip 即可）

$install_root = "D:\drylab-tools"
$installer_dir = "$install_root\installers"
$orca_dir = "$install_root\orca"

# 自动找 zip 包（不要求精确版本号）
$orca_zip = Get-ChildItem $installer_dir -Filter "orca_5_*_windows_*.zip" |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1 -ExpandProperty FullName

if (-not $orca_zip) {
    Write-Host "ERROR: 未找到 Orca zip 包"
    Write-Host "请将 Orca Windows zip 放到: $installer_dir\"
    Write-Host ""
    Write-Host "下载地址（需注册学术账号）："
    Write-Host "  主站: https://orcaforum.kofo.mpg.de  （国内可能需要代理）"
    Write-Host "  备用: https://www.faccts.de/orca/"
    exit 1
}

Write-Host "找到安装包: $orca_zip"
Write-Host "解压到 $orca_dir ..."

if (Test-Path $orca_dir) { Remove-Item $orca_dir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $orca_dir | Out-Null
Expand-Archive -Path $orca_zip -DestinationPath $orca_dir -Force

# zip 内可能有一层子目录，把 orca.exe 提升到 $orca_dir 根
$orca_exe = Get-ChildItem $orca_dir -Recurse -Filter "orca.exe" | Select-Object -First 1
if ($orca_exe -and $orca_exe.DirectoryName -ne $orca_dir) {
    Write-Host "移动内容到 $orca_dir ..."
    Get-ChildItem $orca_exe.DirectoryName | Move-Item -Destination $orca_dir -Force
    Remove-Item $orca_exe.DirectoryName -Recurse -Force -ErrorAction SilentlyContinue
}

# 验证
$orca_bin = "$orca_dir\orca.exe"
if (Test-Path $orca_bin) {
    Write-Host "Orca 路径: $orca_bin"
    & $orca_bin --version 2>&1 | Select-Object -First 2
} else {
    Write-Host "WARNING: orca.exe 未找到，检查解压结果："
    Get-ChildItem $orca_dir | Select-Object Name
    exit 1
}

# 简单功能测试（H2O，约 10 秒）
Write-Host "运行 H2O 优化测试..."
$test_inp = "$install_root\test_h2o.inp"
@"
! B3LYP def2-SVP OPT
* xyz 0 1
O  0.000000  0.000000  0.119748
H  0.000000  0.756950 -0.478993
H  0.000000 -0.756950 -0.478993
*
"@ | Out-File -FilePath $test_inp -Encoding ASCII

$test_out = "$install_root\test_h2o.out"
& $orca_bin $test_inp | Out-File $test_out
$converged = Select-String "HURRAY|THE OPTIMIZATION HAS CONVERGED" $test_out
if ($converged) {
    Write-Host "H2O 测试通过 ✓"
} else {
    Write-Host "WARNING: 未检测到收敛标志，请手动检查 $test_out"
}

Write-Host "Orca 安装完成，路径: $orca_bin"
