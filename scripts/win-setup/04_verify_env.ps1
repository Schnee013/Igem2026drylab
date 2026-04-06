# 04_verify_env.ps1
# 验证 Windows 计算环境完整性

$install_root  = "D:\drylab-tools"
$conda_python  = "$install_root\envs\docking-repro\python.exe"
# conda run 命令（用于正确激活环境 PATH/DLL）
$conda_run     = "conda run --prefix $install_root\envs\docking-repro python"
$adfr_bin      = "D:\ADFRsuite\bin"
$orca_exe      = "D:\orca\orca.exe"
$vina_exe      = "$install_root\vina.exe"

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
Check "vina (standalone exe)" { Test-Path $vina_exe }
Check "rdkit"     { $r = (conda run --prefix "$install_root\envs\docking-repro" python -c "from rdkit import Chem; print('ok')" 2>&1); $r -contains "ok" }
Check "biopython" { $r = (conda run --prefix "$install_root\envs\docking-repro" python -c "from Bio import PDB; print('ok')" 2>&1);    $r -contains "ok" }
Check "meeko"     { $r = (conda run --prefix "$install_root\envs\docking-repro" python -c "import meeko; print('ok')" 2>&1);            $r -contains "ok" }
Check "numpy"     { $r = (conda run --prefix "$install_root\envs\docking-repro" python -c "import numpy; print('ok')" 2>&1);            $r -contains "ok" }

Write-Host ""
Write-Host "--- ADFR Suite ($adfr_bin) ---"
$adfr_receptor = @("$adfr_bin\prepare_receptor.exe",
                   "$adfr_bin\prepare_receptor.bat",
                   "$adfr_bin\prepare_receptor",
                   "$adfr_bin\prepare_receptor4.py") |
                 Where-Object { Test-Path $_ } | Select-Object -First 1
Check "prepare_receptor" { $null -ne $adfr_receptor }
$adfr_ligand = @("$adfr_bin\prepare_ligand.exe",
                 "$adfr_bin\prepare_ligand.bat",
                 "$adfr_bin\prepare_ligand",
                 "$adfr_bin\prepare_ligand4.py") |
               Where-Object { Test-Path $_ } | Select-Object -First 1
Check "prepare_ligand" { $null -ne $adfr_ligand }

Write-Host ""
Write-Host "--- Orca ($orca_exe) ---"
Check "orca.exe" { Test-Path $orca_exe }

Write-Host ""
Write-Host "--- Vina ($vina_exe) ---"
Check "vina.exe" { Test-Path $vina_exe }

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
    Write-Host "  vina_bin: $vina_exe"
    Write-Host "  conda_python: $conda_python"
} else {
    Write-Host "=== 有检查未通过，完成安装后重新运行此脚本 ==="
}
