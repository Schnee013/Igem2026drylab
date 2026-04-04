# 04_verify_env.ps1
# 验证 Windows 计算环境完整性
# 全部通过后即可开始运行 docking-repro pipeline

$conda_python = "D:\miniconda3\envs\docking-repro\Scripts\python.exe"
$adfr_bin = "D:\ADFRsuite\bin"
$orca_exe = "D:\orca\orca.exe"

$all_pass = $true

function Check($name, $test_expr) {
    $result = & $test_expr
    if ($result) {
        Write-Host "[PASS] $name"
    } else {
        Write-Host "[FAIL] $name"
        $script:all_pass = $false
    }
}

Write-Host "=== docking-repro 环境验证 ==="
Write-Host ""

# Python 环境
Write-Host "--- Python 依赖 ---"
Check "Python 3.11" { Test-Path $conda_python }
Check "vina" { & $conda_python -c "import vina" 2>&1; $LASTEXITCODE -eq 0 }
Check "rdkit" { & $conda_python -c "from rdkit import Chem" 2>&1; $LASTEXITCODE -eq 0 }
Check "biopython" { & $conda_python -c "from Bio import PDB" 2>&1; $LASTEXITCODE -eq 0 }
Check "meeko" { & $conda_python -c "import meeko" 2>&1; $LASTEXITCODE -eq 0 }
Check "numpy" { & $conda_python -c "import numpy" 2>&1; $LASTEXITCODE -eq 0 }

Write-Host ""
Write-Host "--- ADFR Suite ---"
$adfr_receptor = if (Test-Path "$adfr_bin\prepare_receptor.exe") { "$adfr_bin\prepare_receptor.exe" }
                 elseif (Test-Path "$adfr_bin\prepare_receptor4.py") { "$adfr_bin\prepare_receptor4.py" }
                 else { $null }
Check "prepare_receptor" { $null -ne $adfr_receptor }
$adfr_ligand = if (Test-Path "$adfr_bin\prepare_ligand.exe") { "$adfr_bin\prepare_ligand.exe" }
               elseif (Test-Path "$adfr_bin\prepare_ligand4.py") { "$adfr_bin\prepare_ligand4.py" }
               else { $null }
Check "prepare_ligand" { $null -ne $adfr_ligand }

Write-Host ""
Write-Host "--- Orca ---"
Check "orca.exe" { Test-Path $orca_exe }

Write-Host ""
Write-Host "--- 磁盘空间（D:）---"
$disk = Get-PSDrive D
$free_gb = [math]::Round($disk.Free / 1GB, 1)
Write-Host "  可用: ${free_gb} GB"
if ($free_gb -lt 10) {
    Write-Host "[WARN] 空间不足 10GB，Orca 计算可能需要额外空间"
}

Write-Host ""
if ($all_pass) {
    Write-Host "=== 所有检查通过，可以开始运行 docking-repro pipeline ==="
    Write-Host ""
    Write-Host "运行命令（在 Windows 上）："
    Write-Host "  D:\miniconda3\envs\docking-repro\Scripts\python.exe run_pipeline.py --step prepare"
} else {
    Write-Host "=== 有检查未通过，请先完成安装再继续 ==="
}
