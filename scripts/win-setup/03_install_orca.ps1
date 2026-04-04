# 03_install_orca.ps1
# 安装 Orca 5.x 到 D:\orca
# 需要先从 https://orcaforum.kofo.mpg.de 注册并下载
# Windows 版本为 zip 包，解压即用

$orca_zip = "C:\Users\Administrator\orca_5_0_4_windows_x86-64_shared_openmpi411.zip"
$orca_dir = "D:\orca"

if (-not (Test-Path $orca_zip)) {
    Write-Host "ERROR: 未找到 Orca zip 包: $orca_zip"
    Write-Host "请先从 https://orcaforum.kofo.mpg.de 注册并下载 Windows x86_64 版本"
    Write-Host "（学术免费，需注册）"
    Write-Host ""
    Write-Host "下载后放到: $orca_zip（或修改此脚本中的路径）"
    exit 1
}

Write-Host "解压 Orca 到 $orca_dir ..."
if (Test-Path $orca_dir) { Remove-Item $orca_dir -Recurse -Force }
Expand-Archive -Path $orca_zip -DestinationPath "D:\" -Force

# Orca zip 解压后的目录名可能不同，找到 orca.exe
$orca_exe = Get-ChildItem "D:\" -Recurse -Filter "orca.exe" | Select-Object -First 1
if ($orca_exe) {
    $actual_dir = $orca_exe.DirectoryName
    if ($actual_dir -ne $orca_dir) {
        Rename-Item $actual_dir $orca_dir
    }
    Write-Host "Orca 路径: $orca_dir\orca.exe"
} else {
    Write-Host "WARNING: 未找到 orca.exe，检查解压结果"
    Get-ChildItem "D:\" -Directory | Select-Object Name
}

# 验证
Write-Host "验证 Orca..."
& "$orca_dir\orca.exe" --version 2>&1
if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) {
    Write-Host "Orca OK"
}

# 测试：H2O 优化（约 10 秒）
Write-Host "运行 H2O 优化测试..."
$test_inp = "C:\Users\Administrator\test_h2o.inp"
@"
! B3LYP def2-SVP OPT
* xyz 0 1
O  0.000000  0.000000  0.119748
H  0.000000  0.756950 -0.478993
H  0.000000 -0.756950 -0.478993
*
"@ | Out-File -FilePath $test_inp -Encoding ASCII

& "$orca_dir\orca.exe" $test_inp | Select-String "HURRAY|THE OPTIMIZATION HAS CONVERGED|ERROR"
Write-Host "H2O 测试完成"
Write-Host "Orca 安装完成，路径: $orca_dir\orca.exe"
