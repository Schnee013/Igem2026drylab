"""Verify Git content, or the selected release after restoring its LFS data."""
import argparse
import json
from pathlib import Path
import zipfile
from lfs_delivery import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--mode', choices=['github', 'full'], default='github')
    args = parser.parse_args()
    try:
        result = verify(args.root, args.mode)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        result = {'status': 'FAIL', 'mode': args.mode, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
