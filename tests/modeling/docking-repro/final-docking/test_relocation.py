"""Exercise the relocated command entry points without running simulations."""

import csv
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / 'src/modeling/docking-repro/final-docking'


class DockingRelocationTests(unittest.TestCase):
    def test_vina_discovery_from_another_directory_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='docking relocation ') as name:
            root = Path(name)
            code = root / CODE.relative_to(ROOT)
            shutil.copytree(CODE, code, ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'experiments').symlink_to(ROOT / 'experiments', target_is_directory=True)
            env = {**os.environ, 'DRY_RUN': '1', 'PYTHON': sys.executable,
                   'OUTPUT_ROOT': str(root / 'unused results')}
            env.pop('ROOT', None)
            result = subprocess.run(['bash', str(code / 'run_all_vina.sh')],
                                    cwd='/private/tmp', env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('计划任务数：70', result.stdout)
            self.assertFalse((root / 'unused results').exists())

    def test_saved_manifest_resolves_all_70_result_directories(self):
        sys.path.insert(0, str(CODE))
        try:
            from merge_prolif_csv import load_manifest, read_and_validate_source
            from project_paths import resolve_paths
            blocks, models = load_manifest(resolve_paths()['prolif_results'])
            self.assertEqual((len(blocks), len(models)), (70, 35))
            for block in blocks:
                self.assertTrue(block.output_dir.is_relative_to(ROOT))
                for kind, filename in [('frequency', 'interaction_frequency.csv'),
                                       ('presence', 'ifp_presence.csv'), ('counts', 'ifp_counts.csv')]:
                    self.assertTrue(read_and_validate_source(block.output_dir / 'ifp' / filename, kind))
        finally:
            sys.path.pop(0)

    def test_saved_ligand_ids_match_batch_expectations(self):
        sys.path.insert(0, str(CODE))
        try:
            from project_paths import resolve_paths
            ligand_root = resolve_paths()['ligand_pdbqt']
            names = {p.relative_to(ligand_root).with_suffix('').as_posix()
                     for p in ligand_root.rglob('*.pdbqt')}
            self.assertEqual(names, {'ascr3_deprotonated', 'ascr18_deprotonated'})
        finally:
            sys.path.pop(0)


if __name__ == '__main__':
    unittest.main()
