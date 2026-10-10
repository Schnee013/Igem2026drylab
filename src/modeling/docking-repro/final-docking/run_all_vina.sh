#!/usr/bin/env bash
set -u -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="${ROOT:-$(cd -- "$SCRIPT_DIR/../../../.." && pwd -P)}"
PYTHON="${PYTHON:-python3}"
VINA="${VINA:-$(command -v vina || true)}"
BOX_FILE="${BOX_FILE:-$("$PYTHON" "$SCRIPT_DIR/project_paths.py" box_config --root "$ROOT")}"
RECEPTOR_ROOT="${RECEPTOR_ROOT:-$("$PYTHON" "$SCRIPT_DIR/project_paths.py" receptor_pdbqt --root "$ROOT")}"
LIGAND_ROOT="${LIGAND_ROOT:-$("$PYTHON" "$SCRIPT_DIR/project_paths.py" ligand_pdbqt --root "$ROOT")}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$("$PYTHON" "$SCRIPT_DIR/project_paths.py" vina_results --root "$ROOT")}"
DRY_RUN="${DRY_RUN:-0}"
RUN_TS="$(date +%Y%m%d_%H%M%S)_$$"

# 只处理这 5 个 WT 家族中的已对齐受体；Gpr2/Gpr3 还包括其 deltaN_aligned。
RECEPTOR_REL_DIRS=(
    'daf37_wt/wt_aligned'
    'gpr2_twf154_wt/wt_aligned'
    'gpr2_twf154_wt/deltaN_aligned'
    'gpr3_twf154_wt/wt_aligned'
    'gpr3_twf154_wt/deltaN_aligned'
    'gprc_wt/wt_aligned'
    'srbc64_wt/wt_aligned'
)
EXPECTED_PDBQT_PER_DIR=5

if [[ "$DRY_RUN" != 0 && "$DRY_RUN" != 1 ]]; then
    echo "错误：DRY_RUN 只能为 0 或 1" >&2
    exit 1
fi
if [[ "$DRY_RUN" == 0 && ! -x "$VINA" ]]; then
    echo "错误：Vina 不存在或不可执行：$VINA" >&2
    exit 1
fi
if [[ ! -f "$BOX_FILE" ]]; then
    echo "错误：找不到盒子参数文件：$BOX_FILE" >&2
    exit 1
fi
if [[ ! -d "$RECEPTOR_ROOT" ]]; then
    echo "错误：找不到受体目录：$RECEPTOR_ROOT" >&2
    exit 1
fi
if [[ ! -d "$LIGAND_ROOT" ]]; then
    echo "错误：找不到配体目录：$LIGAND_ROOT" >&2
    exit 1
fi

# 每个白名单目录都必须存在且恰有 model 0-4 共 5 个 PDBQT，防止不完整批次被误跑。
receptor_files=()
missing_receptor_sets=0
for rel_dir in "${RECEPTOR_REL_DIRS[@]}"; do
    receptor_dir="$RECEPTOR_ROOT/$rel_dir"
    if [[ ! -d "$receptor_dir" ]]; then
        echo "[错误] 缺少受体目录：$receptor_dir" >&2
        missing_receptor_sets=$((missing_receptor_sets + 1))
        continue
    fi

    before_count="${#receptor_files[@]}"
    while IFS= read -r f; do
        receptor_files+=("$f")
    done < <(find "$receptor_dir" -maxdepth 1 -type f -name '*.pdbqt' -print | sort)

    set_count=$(( ${#receptor_files[@]} - before_count ))
    if [[ "$set_count" -ne "$EXPECTED_PDBQT_PER_DIR" ]]; then
        echo "[错误] $receptor_dir 应有 $EXPECTED_PDBQT_PER_DIR 个 PDBQT，实际为 $set_count" >&2
        missing_receptor_sets=$((missing_receptor_sets + 1))
    fi
done

if (( missing_receptor_sets > 0 )); then
    echo "错误：受体输入预检失败 $missing_receptor_sets 项；尚未启动 Vina" >&2
    exit 1
fi

ligand_files=()
while IFS= read -r f; do
    ligand_files+=("$f")
done < <(find "$LIGAND_ROOT" -type f -name '*.pdbqt' -print | sort)

if [[ "${#ligand_files[@]}" -eq 0 ]]; then
    echo "错误：$LIGAND_ROOT 下没有找到配体 PDBQT" >&2
    exit 1
fi

# boxes.tsv 第一列按 WT 家族的 model_0 命名；同一家族所有已对齐模型共用该固定 box。
find_box() {
    local wanted="$1"
    local key cx cy cz sx sy sz

    while read -r key cx cy cz sx sy sz; do
        case "${key:-}" in
            ""|\#*) continue ;;
        esac
        if [[ "$key" == "$wanted" ]]; then
            sz="${sz%$'\r'}"
            printf '%s %s %s %s %s %s\n' "$cx" "$cy" "$cz" "$sx" "$sy" "$sz"
            return 0
        fi
    done < "$BOX_FILE"
    return 1
}

valid_number() {
    [[ "$1" =~ ^-?([0-9]+([.][0-9]*)?|[.][0-9]+)$ ]]
}

valid_box() {
    local box="$1"
    local cx cy cz sx sy sz extra v

    read -r cx cy cz sx sy sz extra <<< "$box"
    [[ -z "${extra:-}" ]] || return 1
    for v in "$cx" "$cy" "$cz" "$sx" "$sy" "$sz"; do
        valid_number "$v" || return 1
    done
}

# 在启动任何任务前，先验证每个受体都能映射到合法的固定 box。
run_queue=()
box_failures=0
for receptor_path in "${receptor_files[@]}"; do
    receptor_rel="${receptor_path#"$RECEPTOR_ROOT"/}"
    family="${receptor_rel%%/*}"
    box_key="${family}_model_0"

    if ! box="$(find_box "$box_key")"; then
        echo "[错误] boxes.tsv 缺少固定 box：$box_key（受体：$receptor_rel）" >&2
        box_failures=$((box_failures + 1))
        continue
    fi
    if ! valid_box "$box"; then
        echo "[错误] boxes.tsv 中 $box_key 的 box 非法：$box" >&2
        box_failures=$((box_failures + 1))
        continue
    fi

    run_queue+=("$receptor_path|$receptor_rel|$box_key|$box")
done

if (( box_failures > 0 )); then
    echo "错误：box 预检失败 $box_failures 项；尚未启动 Vina" >&2
    exit 1
fi

jobs=0
failures=0
echo "受体数：${#run_queue[@]}"
echo "配体数：${#ligand_files[@]}"
echo "计划任务数：$(( ${#run_queue[@]} * ${#ligand_files[@]} ))"
echo "本次输出根目录：$OUTPUT_ROOT"

if [[ "$DRY_RUN" == 1 ]]; then
    echo "输入和搜索盒检查通过；未启动 Vina，未创建输出目录。"
    exit 0
fi

for entry in "${run_queue[@]}"; do
    IFS='|' read -r receptor_path receptor_rel box_key box <<< "$entry"
    read -r cx cy cz sx sy sz <<< "$box"
    receptor_id="${receptor_rel%.pdbqt}"

    for ligand_path in "${ligand_files[@]}"; do
        ligand_rel="${ligand_path#"$LIGAND_ROOT"/}"
        ligand_id="${ligand_rel%.pdbqt}"

        # 保留受体与配体的相对目录，不再把路径压平成下划线名称。
        combo_dir="$OUTPUT_ROOT/$receptor_id/ligands/$ligand_id/run_$RUN_TS"
        output="$combo_dir/poses.pdbqt"
        log="$combo_dir/vina.log"

        if [[ -e "$output" || -e "$log" ]]; then
            echo "[错误] 输出路径已存在，跳过：$combo_dir" >&2
            failures=$((failures + 1))
            continue
        fi
        if ! mkdir -p "$combo_dir"; then
            echo "[错误] 无法创建输出目录：$combo_dir" >&2
            failures=$((failures + 1))
            continue
        fi

        jobs=$((jobs + 1))
        echo "[运行] $receptor_rel × $ligand_rel（box: $box_key）"

        if "$VINA" \
            --receptor "$receptor_path" \
            --ligand "$ligand_path" \
            --center_x "$cx" \
            --center_y "$cy" \
            --center_z "$cz" \
            --size_x "$sx" \
            --size_y "$sy" \
            --size_z "$sz" \
            --cpu 16 \
            --exhaustiveness 8 \
            --num_modes 9 \
            --energy_range 3 \
            --seed 1919 \
            --out "$output" \
            > "$log" 2>&1
        then
            if [[ -s "$output" ]]; then
                echo "[完成] $output"
            else
                echo "[失败] Vina 返回成功，但输出为空；检查 $log" >&2
                failures=$((failures + 1))
            fi
        else
            echo "[失败] 检查日志：$log" >&2
            failures=$((failures + 1))
        fi
    done
done

echo
echo "任务数：$jobs"
echo "失败数：$failures"
echo "结果结构：$OUTPUT_ROOT/<家族>/<wt_aligned|deltaN_aligned>/<受体名>/ligands/<配体相对路径>/run_$RUN_TS/"

[[ "$failures" -eq 0 && "$jobs" -gt 0 ]]
