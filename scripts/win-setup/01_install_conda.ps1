# 01_install_conda.ps1
# 安装 Miniconda3 到 D:\miniconda3
# 安装包下载到 D:\installers\（不碰 C 盘）

$install_root = "D:\drylab-tools"
$installer_dir = "$install_root\installers"
$conda_dir = "$install_root\miniconda3"
$installer = "$installer_dir\miniconda_installer.exe"
$miniconda_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"

New-Item -ItemType Directory -Force -Path $installer_dir | Out-Null

Write-Host "下载 Miniconda3 到 $installer ..."
Invoke-WebRequest -Uri $miniconda_url -OutFile $installer

Write-Host "安装 Miniconda3 到 $conda_dir ..."
Start-Process -FilePath $installer -ArgumentList `
    "/InstallationType=AllUsers", `
    "/AddToPath=1", `
    "/RegisterPython=0", `
    "/S", `
    "/D=$conda_dir" `
    -Wait -NoNewWindow

Write-Host "验证..."
& "$conda_dir\Scripts\conda.exe" --version

Write-Host "创建 docking-repro 环境..."
& "$conda_dir\Scripts\conda.exe" create -n docking-repro python=3.11 -y

Write-Host "安装 Python 依赖..."
& "$conda_dir\envs\docking-repro\Scripts\pip.exe" install `
    vina meeko biopython rdkit-pypi numpy pyyaml

Write-Host "验证 vina..."
& "$conda_dir\envs\docking-repro\Scripts\python.exe" -c "import vina; print('vina OK')"

Write-Host "完成！Miniconda 路径: $conda_dir"
