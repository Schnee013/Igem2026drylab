"""Restore the selected LFS data to the paths consumed by Docking analyses."""
import argparse
import json
from pathlib import Path
import zipfile
from lfs_delivery import restore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(restore(args.root), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        raise SystemExit('STOP: ' + str(exc))


if __name__ == '__main__':
    main()
