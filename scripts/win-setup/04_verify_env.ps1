# 04_verify_env.ps1
# 验证 Windows 计算环境完整性

$install_root  = "D:\drylab-tools"
$conda_python  = "$install_root\miniconda3\envs\docking-repro\Scripts\python.exe"
$adfr_bin      = "$install_root\ADFRsuite\bin"
$orca_exe      = "$install_root\orca\orca.exe"

$all_pass = $true

function Check($name, [scriptblock]$test) {
    $ok = & $test
    $status = if ($ok) { "[PASS]" } else { "[FAIL]"; $script:all_pass = $false }
    Write-Host "$status $name"
}

Write-Host "=== docking-repro 环境验证 ==="
Write-Host "根目录: $install_root"
Write-Host ""

Write-Host "--- Python 依赖 ---"
Check "Python 3.11 ($conda_python)" { Test-Path $conda_python }
Check "vina"      { (& $conda_python -c "import vina"        2>&1) -and $LASTEXITCODE -eq 0 }
Check "rdkit"     { (& $conda_python -c "from rdkit import Chem" 2>&1) -and $LASTEXITCODE -eq 0 }
Check "biopython" { (& $conda_python -c "from Bio import PDB" 2>&1) -and $LASTEXITCODE -eq 0 }
Check "meeko"     { (& $conda_python -c "import meeko"       2>&1) -and $LASTEXITCODE -eq 0 }
Check "numpy"     { (& $conda_python -c "import numpy"       2>&1) -and $LASTEXITCODE -eq 0 }

Write-Host ""
Write-Host "--- ADFR Suite ($adfr_bin) ---"
$adfr_receptor = @("$adfr_bin\prepare_receptor.exe",
                   "$adfr_bin\prepare_receptor",
                   "$adfr_bin\prepare_receptor4.py") |
                 Where-Object { Test-Path $_ } | Select-Object -First 1
Check "prepare_receptor" { $null -ne $adfr_receptor }
$adfr_ligand = @("$adfr_bin\prepare_ligand.exe",
                 "$adfr_bin\prepare_ligand",
                 "$adfr_bin\prepare_ligand4.py") |
               Where-Object { Test-Path $_ } | Select-Object -First 1
Check "prepare_ligand" { $null -ne $adfr_ligand }

Write-Host ""
Write-Host "--- Orca ($orca_exe) ---"
Check "orca.exe" { Test-Path $orca_exe }

Write-Host ""
Write-Host "--- 磁盘空间 ---"
"C","D","E","F" | ForEach-Object {
    $drive = Get-PSDrive $_ -ErrorAction SilentlyContinue
    if ($drive) {
        $free = [math]::Round($drive.Free / 1GB, 1)
        Write-Host "  ${_}: $free GB 可用"
    }
}

Write-Host ""
if ($all_pass) {
    Write-Host "=== 全部通过 ==="
    Write-Host ""
    Write-Host "实际工具路径（更新到 config.yaml）："
    Write-Host "  adfr_bin: $adfr_bin"
    Write-Host "  orca_bin: $orca_exe"
    Write-Host "  conda_python: $conda_python"
} else {
    Write-Host "=== 有检查未通过，完成安装后重新运行此脚本 ==="
}
