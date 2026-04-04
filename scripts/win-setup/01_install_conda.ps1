# 01_install_conda.ps1
# 在 Windows 上安装 Miniconda3 到 D:\miniconda3
# 用法：以管理员身份在 PowerShell 中运行

$miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$installer = "C:\Users\Administrator\miniconda_installer.exe"

Write-Host "下载 Miniconda3..."
Invoke-WebRequest -Uri $miniconda_url -OutFile $installer

Write-Host "安装 Miniconda3 到 D:\miniconda3..."
Start-Process -FilePath $installer -ArgumentList `
    "/InstallationType=AllUsers", `
    "/AddToPath=1", `
    "/RegisterPython=0", `
    "/S", `
    "/D=D:\miniconda3" `
    -Wait -NoNewWindow

Write-Host "安装完成，验证..."
& "D:\miniconda3\Scripts\conda.exe" --version

Write-Host "创建 docking-repro 环境..."
& "D:\miniconda3\Scripts\conda.exe" create -n docking-repro python=3.11 -y

Write-Host "安装 Python 依赖..."
& "D:\miniconda3\envs\docking-repro\Scripts\pip.exe" install `
    vina meeko biopython rdkit-pypi numpy pyyaml

Write-Host "验证 vina..."
& "D:\miniconda3\envs\docking-repro\Scripts\python.exe" -c "import vina; print('vina OK')"

Write-Host "完成！"
