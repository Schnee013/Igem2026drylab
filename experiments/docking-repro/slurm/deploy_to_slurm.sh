#!/bin/bash
# Gpr2 重对接部署脚本 — Mac → Slurm 服务器
# 用法: bash experiments/docking-repro/slurm/deploy_to_slurm.sh
#
# 前提: SSH 密钥已配置到 10.40.4.5:10022 (user=guest)
# → docs/logs/2026-04-16.md §Gpr2 Docking Pose 朝向验证

set -euo pipefail

SERVER="10.40.4.5"
REMOTE_DIR="~/drylab-docking"
LOCAL_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

echo "=== Step 1: 创建远程目录结构 ==="
ssh "$SERVER" "mkdir -p $REMOTE_DIR/{src/modeling/docking-repro,experiments/docking-repro/{prepared/{receptors,ligands},results,logs}} ~/bin"

echo "=== Step 2: 传输代码（6 文件） ==="
CODE_DIR="$LOCAL_ROOT/src/modeling/docking-repro"
for f in config.yaml dock.py run_wt_singlestage.py grid_box.py utils.py validate.py; do
    scp "$CODE_DIR/$f" "$SERVER:$REMOTE_DIR/src/modeling/docking-repro/"
    echo "  ✓ $f"
done

echo "=== Step 3: 传输受体数据 ==="
PREP_DIR="$LOCAL_ROOT/experiments/docking-repro/prepared"
scp "$PREP_DIR/receptors/Gpr2_G1X9E2_tm.pdbqt" "$SERVER:$REMOTE_DIR/experiments/docking-repro/prepared/receptors/"
scp "$PREP_DIR/receptors/Gpr2_G1X9E2_tm.pdb" "$SERVER:$REMOTE_DIR/experiments/docking-repro/prepared/receptors/"
echo "  ✓ Gpr2 receptor (.pdbqt + .pdb)"

echo "=== Step 4: 传输配体数据 ==="
for lig in ascr18 ascr3 ascr7 ascr1; do
    scp "$PREP_DIR/ligands/${lig}_optimized.pdbqt" "$SERVER:$REMOTE_DIR/experiments/docking-repro/prepared/ligands/"
    echo "  ✓ ${lig}_optimized.pdbqt"
done

echo "=== Step 5: 传输 sbatch 脚本 ==="
scp "$LOCAL_ROOT/experiments/docking-repro/slurm/gpr2_redock.sh" "$SERVER:$REMOTE_DIR/"

echo ""
echo "=== 部署完成 ==="
echo "接下来在服务器上执行:"
echo "  ssh $SERVER"
echo "  # 检查/安装 Vina:"
echo "  #   which vina || (下载 vina_1.2.7_linux_x86_64 到 ~/bin/vina && chmod +x ~/bin/vina)"
echo "  ~/bin/vina --version"
echo "  # 提交作业:"
echo "  cd ~/drylab-docking && sbatch gpr2_redock.sh"
echo "  squeue -u \$USER"
