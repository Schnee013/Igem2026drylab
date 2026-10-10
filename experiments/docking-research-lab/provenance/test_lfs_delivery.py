"""Failure-path tests for the selected-data restorer."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from lfs_delivery import restore, safe_path, sha256


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name).resolve()
        self.root = self.repo / 'experiments/research'
        self.prov = self.root / 'provenance'
        self.prov.mkdir(parents=True)
        self.archive = self.repo / 'payload.zip'
        self.body = b'original research input\n'
        with zipfile.ZipFile(self.archive, 'w') as z:
            z.writestr('input.dat', self.body)
        self.row = dict(path='inputs/input.dat', bytes=str(len(self.body)),
                        sha256=hashlib.sha256(self.body).hexdigest(),
                        storage='zip', container='payload.zip', member='input.dat', role='test')
        self.release = dict(schema_version=1, archives=[dict(path='payload.zip',
            bytes=self.archive.stat().st_size, sha256=sha256(self.archive))],
            restore_manifest='provenance/lfs-files.csv', git_checksums='provenance/release-git.sha256')
        self.write_manifest()

    def write_manifest(self):
        with (self.prov / 'lfs-files.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, list(self.row)); w.writeheader(); w.writerow(self.row)
        (self.prov / 'lfs-release.json').write_text(json.dumps(self.release))
        (self.prov / 'release-git.sha256').write_text(''.join(
            sha256(self.prov / p) + '  provenance/' + p + '\n'
            for p in ['lfs-files.csv', 'lfs-release.json']))

    def tearDown(self):
        self.temp.cleanup()

    def test_restore_and_repeat(self):
        self.assertEqual(restore(self.root)['restored'], 1)
        self.assertEqual((self.root / self.row['path']).read_bytes(), self.body)
        self.assertEqual(restore(self.root)['already_present_and_identical'], 1)

    def test_existing_change_is_preserved(self):
        p = self.root / self.row['path']; p.parent.mkdir(); p.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'preserved without overwrite'):
            restore(self.root)
        self.assertEqual(p.read_bytes(), b'changed')

    def test_changed_archive_is_rejected_before_write(self):
        self.archive.write_bytes(b'bad archive')
        with self.assertRaisesRegex(ValueError, 'Missing or changed LFS'):
            restore(self.root)
        self.assertFalse((self.root / 'inputs').exists())

    def test_bad_member_hash_does_not_install_file(self):
        self.row['sha256'] = '0' * 64; self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'Restored content differs'):
            restore(self.root)
        self.assertFalse((self.root / self.row['path']).exists())
        self.assertFalse(list(self.root.rglob('.restore-*')))

    def test_traversal_and_symlink_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe release path'):
            safe_path(self.root, '../escape')
        (self.root / 'inputs').symlink_to(self.repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            restore(self.root)


if __name__ == '__main__':
    unittest.main()
