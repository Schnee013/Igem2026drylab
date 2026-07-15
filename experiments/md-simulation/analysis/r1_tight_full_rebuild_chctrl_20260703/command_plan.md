# Route 1 Command Plan

> Status: Package A executed after user approval on 2026-07-03. Package B and Package C were explicitly approved by the user on 2026-07-04 and completed for reduced `chctrl` only. No Ch-1/Ch-2/Ch-4 action was executed.

## Local-Only Commands Allowed Without Remote Approval

Local read-only checks may be run from `/Users/roy/Documents/drylab` if dependencies exist:

```bash
command -v gmx
shasum -a 256 <input-files>
wc -c <input-files>
```

Local GROMACS, if later available, may only check or build local prototype files under the prototype root. It must not be used as an evidence generator for E2-produced GROMACS binary outputs.

Any local command that creates prototype files must write only under:

```text
experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/
```

## E2 Approval Package Required Before Remote Execution

Before any SSH/E2 action, write a fully specified package with:

| Field | Required before approval |
|---|---|
| Remote host | exact SSH alias or host |
| Remote run directory | exact path under the approved personal project directory |
| Upload command | exact `rsync`/`scp` command |
| Environment command | exact module/conda/source commands |
| `grompp` command | full command with paths and warning policy |
| Smoke `mdrun` command | full command with GPU/CPU/thread settings |
| E2 output preprocessing / evidence command | exact recorded E2 `gmx_mpi` command used to check, convert, preprocess, and evidence-analyze E2 `.tpr`, `.cpt`, `.edr`, `.trr`, `.xtc`, and any `gmx`-processed outputs |
| Expected wall time | explicit estimate |
| Stop condition | e.g. fatal error, LINCS, missing outputs, wall-time cap |
| Log paths | exact stdout/stderr/log paths |
| Download command | exact result sync path |
| Cleanup rule | what can and cannot be removed |

## E2 Output Analysis Rule

Any future reduced-`chctrl` E2 binary output must follow `environments/e2-md-gromacs.md`: E2-produced `.tpr`, `.cpt`, `.edr`, `.trr`, `.xtc`, and any `gmx`-processed evidence output must be checked, converted, preprocessed, and evidence-analyzed with the recorded E2 GROMACS environment for that run.

For the current E2 route, the authoritative command is:

```text
/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
```

unless a future run-specific provenance file records a different command. Local `chimeric`, `chimeric-md-2025`, Homebrew, or other local `gmx` / `gmx_mpi` environments may only be used for non-authoritative inspection, or for Python-only analysis after E2-side preprocessing has produced documented, synced, checksummed inputs.

## Current Stop

The previous stop condition for Package B was lifted by explicit user approval on 2026-07-04. Package B produced final step6.6 `.gro`, `.cpt`, `.tpr`, `.edr`, and `.xtc` files. Package C was also explicitly approved/requested by the user and completed as a 100 ps short production test.

Current stop: any additional E2 command, candidate build, candidate benchmark, long production, cleanup, or transfer to Ch-1/Ch-2/Ch-4 requires a new approval package.

Post-comparison routing update: `r1_z_only_public_atom_count_comparison.md` downgrades the current `120 A` XY / `20 A` water R1 instantiation as a compute-saving route. It remains chctrl exploratory build/run evidence. Further Z-only water-thickness shaving is paused as the primary path because the recorded atom-count delta is only `-6776` atoms (`-2.57%`) and the public membrane-system comparison supports normal protein/total atom fractions.

Post-agreement route-family update: `experiments/md-simulation/analysis/chimeric_route_family_selection_20260704.md` recorded a historical R4 source-gate selection. Later R4 material-boundary records supersede that as a current instruction. R4 builds, E2 commands, candidate actions, source-acquisition queues, and further R1-Z runs each require separate routed approval.

As of 2026-07-04:

- Local `command -v gmx` returned no path in this follow-up pass, so local `grompp` is unavailable.
- CHARMM-GUI job `8305210188` has produced an exploratory `chctrl` GROMACS input package under `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/`.
- Static checks found `257130` atoms in the prototype `step5_input.gro`, a `-6776` atom delta versus the current chctrl `263906` atom reference, matching topology atom sums, required index groups, and matching core production MDP settings.
- Package B/C result outputs are stored at `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/`.
- `padding_rule.md` is `exploratory`; candidate-transferable numeric padding requires a separate source-backed rule.
- The E2 GROMACS environment is the authoritative GROMACS evidence generator for this route because local `gmx` is absent and E2-produced binary outputs must be handled under `environments/e2-md-gromacs.md`.
- This R1 command plan has no current next work item. Any future R1, R4, or candidate action needs a new routed approval package.

Any next package must be newly written and approved before execution.

## Approval Package A: E2 GMX Environment And Metadata Preflight

Status: executed after user approval on 2026-07-03. This package performed no `grompp`, no `mdrun`, no smoke, no benchmark, and no production. It verified the recorded E2 GROMACS command and staged the R1 prototype metadata under an isolated R1 directory.

| Field | Value |
|---|---|
| Remote host | `nkuliulab-e2` |
| Remote run directory | `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env` |
| Local upload source | `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/` |
| Remote metadata destination | `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env/prototype_metadata/` |
| Environment command | `GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi` |
| `grompp` command | Not run in Package A. |
| Smoke `mdrun` command | Not run in Package A. |
| GPU/CPU/thread settings | No MD workload; only `gmx_mpi --version` plus `nvidia-smi`; no thread allocation. |
| Expected wall time | Less than 5 minutes if SSH and filesystem are responsive. |
| Logs | Remote: `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env/logs/e2_preflight_20260703_gmx_env.log`; local download target: `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/run_logs/e2_preflight_20260703_gmx_env/` |
| Stop condition | Stop on SSH/auth failure, missing remote directory creation, missing/non-executable `GMX_CMD`, failed `gmx_mpi --version`, or failed metadata checksum command. |
| Cleanup rule | Do not delete remote logs. Remote metadata copy may be removed only after local logs and checksums are synced and a later cleanup is explicitly approved. |

Setup command:

```bash
ssh nkuliulab-e2 'mkdir -p /ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env/{logs,prototype_metadata}'
```

Upload command:

```bash
rsync -avP experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/ nkuliulab-e2:/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env/prototype_metadata/
```

Remote preflight command:

```bash
ssh nkuliulab-e2 'set -euo pipefail
RUN_DIR=/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env
GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
cd "$RUN_DIR"
{
  echo "started=$(date -Is)"
  echo "host=$(hostname)"
  echo "user=$(whoami)"
  echo "pwd=$(pwd)"
  echo "gmx_cmd=$GMX_CMD"
  "$GMX_CMD" --version
  echo
  nvidia-smi
  echo
  quota -uvs || true
  echo
  sha256sum prototype_metadata/source_files.sha256 prototype_metadata/route.json prototype_metadata/build_notes.md
} > logs/e2_preflight_20260703_gmx_env.log 2>&1'
```

Download command:

```bash
mkdir -p experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/run_logs/e2_preflight_20260703_gmx_env
rsync -avP nkuliulab-e2:/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env/logs/ experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/run_logs/e2_preflight_20260703_gmx_env/
```

Execution evidence:

- Local log: `experiments/md-simulation/analysis/r1_tight_full_rebuild_chctrl_20260703/run_logs/e2_preflight_20260703_gmx_env/e2_preflight_20260703_gmx_env.log`
- Remote directory: `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/preflight_20260703_gmx_env`
- Verified `gmx_mpi`: GROMACS `2025.4-conda_forge`, Open MPI `5.0.8`, GPU support CUDA.
- Observed GPU: NVIDIA A100-SXM4-80GB.
- No `grompp`, `mdrun`, smoke, benchmark, production, or candidate action was executed.

## Approval Package B: Chctrl CHARMM-GUI Step6 Minimization/Equilibration Gate

Status: explicitly approved by the user on 2026-07-04 and completed. Step6 `mdrun` completed through `step6.6_equilibration`; the first sanity command failed because `gmx check -s` is not a valid GROMACS 2025.4 option. Corrected sanity uses `gmx dump -s` for `.tpr`, `gmx check -f` for `.xtc`, and `gmx check -e` for `.edr`; `.gro` is recorded by existence and checksum because `gmx check -c` on the full-system `.gro` triggers a slow close-contact listing that is not needed for this gate. This package ran only the exploratory reduced `chctrl` CHARMM-GUI step6 minimization/equilibration sequence needed to produce `step6.6_equilibration.gro` and related binary outputs. It did not run production, candidate systems, Ch-1, Ch-2, or Ch-4.

| Field | Value |
|---|---|
| Remote host | `nkuliulab-e2` |
| Remote run directory | `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704` |
| Local upload source | `experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/` |
| Remote input destination | `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704/input/gromacs/` |
| Environment command | `GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi`; record `"$GMX_CMD" --version` before `grompp`. |
| Warning policy | `-maxwarn 0`; any warning, fatal, or nonzero `grompp` exit blocks the next step until reviewed. |
| `grompp` command class | Run CHARMM-GUI `step6.0_minimization.mdp` from `step5_input.gro`, then `step6.1` through `step6.6` from the previous step output, always with `-r step5_input.gro`, `topol.top`, and `index.ndx`. Full shell command is below. |
| `mdrun` command class | Minimization uses one `gmx_mpi` process with `OMP_NUM_THREADS=24`, `-ntomp 24`, and `-pin on`; equilibration uses the same plus `-nb gpu`, `-pme gpu`, and `-bonded gpu`. Full shell command is below. |
| GPU/CPU/thread settings | One A100 for equilibration, one MPI rank invoked directly through `gmx_mpi`, 24 OpenMP threads; no concurrent MD job launched by this package. |
| Expected wall time | Wall-time cap `90m`. Expected to be under that cap for a 257,130-atom step6 minimization/equilibration gate, but actual timing is evidence to record, not assumed. |
| Logs | Remote logs under `logs/`: `gmx_version.log`, `nvidia_smi_start.log`, `grompp_step6.*.log`, `mdrun_step6.*.log`, `sanity_gmx_check.log`, `sanity_energy.log`, `manifest_sha256.txt`. GROMACS step logs under `work/`. |
| Stop condition | Stop on missing input file, missing/non-executable `GMX_CMD`, any `grompp` warning/fatal/error/nonzero exit, any `mdrun` fatal/error/LINCS explosion/nonzero exit, missing step output, unreadable `.tpr`/`.gro`/`.edr`/`.xtc`, wall-time cap, or GPU/CUDA compatibility error. |
| E2 output preprocessing / evidence command | `"$GMX_CMD" dump -s` for final `.tpr`, `"$GMX_CMD" check -f` for `.xtc`, and `"$GMX_CMD" check -e` for `.edr`; `.gro` existence and checksum are recorded; `"$GMX_CMD" energy` extracts potential, temperature, pressure, box, and density from final `.edr`, all inside the recorded E2 environment. |
| Local download target | `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/` |
| Download command | `rsync -avP nkuliulab-e2:/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704/ experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/` |
| Cleanup rule | Do not delete remote inputs, logs, `.tpr`, `.edr`, `.xtc`, `.cpt`, `.gro`, or manifest until local checksum verification and explicit cleanup approval. |

Setup command:

```bash
ssh nkuliulab-e2 'mkdir -p /ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704/{input/gromacs,work,logs,sanity}'
```

Upload command:

```bash
rsync -avP experiments/md-simulation/systems/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/gromacs/ nkuliulab-e2:/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704/input/gromacs/
```

Remote step6 command:

```bash
ssh nkuliulab-e2 'set -euo pipefail
RUN_DIR=/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704
GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
export OMP_NUM_THREADS=24
export GMX_MAXBACKUP=-1
cd "$RUN_DIR"
{
  echo "started=$(date -Is)"
  echo "host=$(hostname)"
  echo "user=$(whoami)"
  echo "pwd=$(pwd)"
  echo "gmx_cmd=$GMX_CMD"
  "$GMX_CMD" --version
} > logs/gmx_version.log 2>&1
nvidia-smi > logs/nvidia_smi_start.log 2>&1 || true
test -s input/gromacs/step5_input.gro
test -s input/gromacs/topol.top
test -s input/gromacs/index.ndx
test -d input/gromacs/toppar
cd input/gromacs
"$GMX_CMD" grompp -f step6.0_minimization.mdp -o ../../work/step6.0_minimization.tpr -c step5_input.gro -r step5_input.gro -p topol.top -n index.ndx -po ../../work/step6.0_minimization_out.mdp -maxwarn 0 > ../../logs/grompp_step6.0_minimization.log 2>&1
"$GMX_CMD" mdrun -v -deffnm ../../work/step6.0_minimization -ntomp 24 -pin on > ../../logs/mdrun_step6.0_minimization.log 2>&1
prev=step6.0_minimization
for i in 1 2 3 4 5 6; do
  step=step6.${i}_equilibration
  "$GMX_CMD" grompp -f ${step}.mdp -o ../../work/${step}.tpr -c ../../work/${prev}.gro -r step5_input.gro -p topol.top -n index.ndx -po ../../work/${step}_out.mdp -maxwarn 0 > ../../logs/grompp_${step}.log 2>&1
  "$GMX_CMD" mdrun -v -deffnm ../../work/${step} -ntomp 24 -pin on -nb gpu -pme gpu -bonded gpu > ../../logs/mdrun_${step}.log 2>&1
  prev=${step}
done
cd "$RUN_DIR"
"$GMX_CMD" dump -s work/step6.6_equilibration.tpr > logs/sanity_gmx_dump_step6.6_tpr.log 2>&1
test -s work/step6.6_equilibration.gro
echo "gro_exists=work/step6.6_equilibration.gro" > logs/sanity_gmx_check.log
"$GMX_CMD" check -f work/step6.6_equilibration.xtc >> logs/sanity_gmx_check.log 2>&1
"$GMX_CMD" check -e work/step6.6_equilibration.edr >> logs/sanity_gmx_check.log 2>&1
printf "Potential\nTemperature\nPressure\nBox-X\nBox-Y\nBox-Z\nDensity\n0\n" | "$GMX_CMD" energy -f work/step6.6_equilibration.edr -o sanity/step6.6_energy.xvg > logs/sanity_energy.log 2>&1
find input work logs sanity -type f -print0 | xargs -0 sha256sum > logs/manifest_sha256.txt
echo "finished=$(date -Is)" >> logs/gmx_version.log'
```

Download command:

```bash
mkdir -p experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil
rsync -avP nkuliulab-e2:/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704/ experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/
```

Post-download local bookkeeping after successful execution:

```bash
find experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil -type f -print0 | xargs -0 shasum -a 256 > experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/local_download.sha256
```

Package B execution evidence:

- Result root: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/`.
- Final step6.6 files exist under `work/`: `.gro`, `.cpt`, `.tpr`, `.edr`, `.xtc`.
- `work/step6.6_equilibration.gro` atom count: `257130`.
- `step6.6_equilibration` performance: `39.920 ns/day`, `0.601 hour/ns`.
- E2-side energy summary from `logs/sanity_energy.log`: temperature `303.201 K`, pressure `0.704 bar`, density `1028.91 kg/m^3`.
- `mdrun_step6.0_minimization.log` contains `86` `LINCS WARNING` matches but minimization converged to `Fmax < 1000` in `4523` steps.
- Local text scan found no LINCS/fatal/CUDA/nan matches in `mdrun_step6.1_equilibration.log` through `mdrun_step6.6_equilibration.log`.

Package B is a chctrl-only action. Ch-1/Ch-2/Ch-4 remain blocked pending a separate candidate action.

## Approval Package C: Reduced Chctrl Short Production Test

Status: explicitly requested/approved by the user on 2026-07-04 after Package B and completed. This package ran only a short reduced-`chctrl` production test from Package B outputs. Candidate production and any Ch-1/Ch-2/Ch-4 action require a separate approval path.

| Field | Value |
|---|---|
| Remote host | `nkuliulab-e2` |
| Remote run directory | `/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704` |
| Required Package B inputs | `work/step6.6_equilibration.gro`, `work/step6.6_equilibration.cpt`, `work/step6.6_equilibration.tpr`, `work/step6.6_equilibration.edr`, `input/gromacs/step7_production.mdp`, `input/gromacs/topol.top`, `input/gromacs/index.ndx`, `input/gromacs/toppar/` |
| Environment command | `GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi`; record `"$GMX_CMD" --version` before `grompp`. |
| Warning policy | `-maxwarn 0`; any warning, fatal, or nonzero `grompp` exit blocks `mdrun`. |
| `grompp` command | Build `production_smoke/r1_chctrl_short_prod.tpr` from `input/gromacs/step7_production.mdp`, `work/step6.6_equilibration.gro`, `work/step6.6_equilibration.cpt`, `topol.top`, and `index.ndx`. |
| `mdrun` command | Run `production_smoke/r1_chctrl_short_prod` with `-nsteps 50000` override, `-ntomp 24`, `-pin on`, `-nb gpu`, `-pme gpu`, and `-bonded gpu`. At `dt=0.002 ps`, this is a nominal `100 ps` short production test. |
| GPU/CPU/thread settings | One A100, one MPI build invoked as a single process through `gmx_mpi`, 24 OpenMP threads, GPU nonbonded/PME/bonded offload. |
| GPU utilization capture | Run `nvidia-smi --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,memory.used,power.draw --format=csv -l 5` during `mdrun`, logging to `logs/nvidia_smi_production_short.csv`. |
| Expected wall time | Wall-time cap `20m`; actual wall time, `Performance:` ns/day, and GPU utilization are evidence to record, not assumptions. |
| Logs | `logs/grompp_r1_chctrl_short_prod.log`, `logs/mdrun_r1_chctrl_short_prod.log`, `logs/nvidia_smi_production_short.csv`, `logs/sanity_short_prod_check.log`, `logs/sanity_short_prod_energy.log`, `logs/production_short_summary.tsv`, `logs/manifest_sha256_after_production_short.txt`. |
| Stop condition | Stop on missing Package B output, `grompp` warning/fatal/error/nonzero exit, `mdrun` fatal/error/LINCS explosion/nonzero exit, unreadable `.tpr`/`.edr`/`.xtc`, wall-time cap, or GPU/CUDA compatibility error. |
| E2 output preprocessing / evidence command | `"$GMX_CMD" dump -s` for short production `.tpr`, `"$GMX_CMD" check -f` for `.xtc`, and `"$GMX_CMD" check -e` for `.edr`; final `.gro` existence and checksum are recorded; `"$GMX_CMD" energy` extracts potential, temperature, pressure, box, and density from short production `.edr`, all inside the recorded E2 environment. |
| Local download target | Same result root as Package B: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/` after Package C completes. |
| Download command | `rsync -avP nkuliulab-e2:/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704/ experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/` |
| Cleanup rule | Do not delete remote inputs, logs, `.tpr`, `.edr`, `.xtc`, `.cpt`, `.gro`, or manifests until local checksum verification and explicit cleanup approval. |

Remote short production command:

```bash
ssh nkuliulab-e2 'set -euo pipefail
RUN_DIR=/ifs1/User/dengwei/igem/md-simulation/r1_tight_full_rebuild_chctrl_20260703/charmm_gui_8305210188_step6_20260704
GMX_CMD=/ifs1/User/dengwei/igem/envs/gromacs-2025.4-mpi-cuda/bin/gmx_mpi
export OMP_NUM_THREADS=24
export GMX_MAXBACKUP=-1
cd "$RUN_DIR"
mkdir -p production_smoke logs sanity
test -s work/step6.6_equilibration.gro
test -s work/step6.6_equilibration.cpt
test -s work/step6.6_equilibration.tpr
test -s work/step6.6_equilibration.edr
test -s input/gromacs/step7_production.mdp
test -s input/gromacs/topol.top
test -s input/gromacs/index.ndx
test -d input/gromacs/toppar
{
  echo "started=$(date -Is)"
  echo "host=$(hostname)"
  echo "user=$(whoami)"
  echo "pwd=$(pwd)"
  echo "gmx_cmd=$GMX_CMD"
  "$GMX_CMD" --version
} > logs/gmx_version_production_short.log 2>&1
cd input/gromacs
"$GMX_CMD" grompp -f step7_production.mdp -o ../../production_smoke/r1_chctrl_short_prod.tpr -c ../../work/step6.6_equilibration.gro -t ../../work/step6.6_equilibration.cpt -p topol.top -n index.ndx -po ../../production_smoke/r1_chctrl_short_prod_out.mdp -maxwarn 0 > ../../logs/grompp_r1_chctrl_short_prod.log 2>&1
cd "$RUN_DIR"
nvidia-smi --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,memory.used,power.draw --format=csv -l 5 > logs/nvidia_smi_production_short.csv 2>&1 &
SMI_PID=$!
set +e
"$GMX_CMD" mdrun -v -deffnm production_smoke/r1_chctrl_short_prod -nsteps 50000 -ntomp 24 -pin on -nb gpu -pme gpu -bonded gpu > logs/mdrun_r1_chctrl_short_prod.log 2>&1
MDRUN_STATUS=$?
set -e
kill "$SMI_PID" 2>/dev/null || true
wait "$SMI_PID" 2>/dev/null || true
test "$MDRUN_STATUS" -eq 0
"$GMX_CMD" dump -s production_smoke/r1_chctrl_short_prod.tpr > logs/sanity_short_prod_tpr_dump.log 2>&1
: > logs/sanity_short_prod_check.log
"$GMX_CMD" check -f production_smoke/r1_chctrl_short_prod.xtc >> logs/sanity_short_prod_check.log 2>&1
"$GMX_CMD" check -e production_smoke/r1_chctrl_short_prod.edr >> logs/sanity_short_prod_check.log 2>&1
test -s production_smoke/r1_chctrl_short_prod.gro
echo "gro_exists=production_smoke/r1_chctrl_short_prod.gro" >> logs/sanity_short_prod_check.log
printf "Potential\nTemperature\nPressure\nBox-X\nBox-Y\nBox-Z\nDensity\n0\n" | "$GMX_CMD" energy -f production_smoke/r1_chctrl_short_prod.edr -o sanity/r1_chctrl_short_prod_energy.xvg > logs/sanity_short_prod_energy.log 2>&1
{
  echo -e "key\tvalue"
  echo -e "finished\t$(date -Is)"
  echo -e "nsteps_override\t50000"
  echo -e "nominal_ps\t100"
  grep -E "Performance:" logs/mdrun_r1_chctrl_short_prod.log | tail -n 1 | sed "s/^/performance_line\t/"
  awk -F, "NR>1 {gsub(/ %/,\"\",\$4); gsub(/^ +/,\"\",\$4); if (\$4 ~ /^[0-9.]+$/) {sum+=\$4; n++}} END {if (n>0) printf \"gpu_utilization_avg_percent\t%.2f\\n\", sum/n; else print \"gpu_utilization_avg_percent\tNA\"}" logs/nvidia_smi_production_short.csv
} > logs/production_short_summary.tsv
find input work production_smoke logs sanity -type f -print0 | xargs -0 sha256sum > logs/manifest_sha256_after_production_short.txt
echo "finished=$(date -Is)" >> logs/gmx_version_production_short.log'
```

Package C execution evidence:

- Output prefix: `production_smoke/r1_chctrl_short_prod`.
- Short production files exist: `.gro`, `.cpt`, `.tpr`, `.edr`, `.xtc`, `.log`, `_out.mdp`.
- Final short-production `.gro` atom count: `257130`.
- Runtime override: `-nsteps 50000`, nominal `100 ps`.
- Performance: `74.362 ns/day`, `0.323 hour/ns`.
- GPU sampling: 25 samples; average all-sample utilization `84.36%`; average nonzero utilization `91.70%`; max utilization `99%`; max memory `575 MiB`.
- E2-side energy summary from `logs/sanity_short_prod_energy.log`: temperature `303.192 K`, pressure `7.549 bar`, density `1029.21 kg/m^3`.
- Local text scan found no LINCS/fatal/CUDA/nan matches in `logs/mdrun_r1_chctrl_short_prod.log`.
- Local checksum manifest after download: `experiments/md-simulation/results/chimeric-ste2-gpa1-wt/r1_tight_full_rebuild_chctrl/20260704_charmm_gui_8305210188_step6_equil/local_download.sha256`.

Result interpretation:

- `chctrl` exploratory prototype can be built through step6 and reached the 100 ps short-production endpoint on E2.
- Long-run physical sanity, source-backed numeric padding, compute-saving success, and candidate-transferability remain separate gates.
- Candidate systems remain blocked until reduced `chctrl` passes the remaining physical sanity and interpretation gates under the unchanged rule.
