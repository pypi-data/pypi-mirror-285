import argparse
from pathlib import Path

from minder.research_data_snapshots import download_datasets

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", nargs="+", required=True, help="dataset name(s)")
parser.add_argument("--organization", nargs="+", help="organisation name(s) or identifier(s)")
parser.add_argument("--folder", type=Path, help="output folder")
parser.add_argument("--refresh", action="store_true", help="refresh selected datasets")
parser.add_argument("--token-path", type=Path, help="path to personal access token")
parser.add_argument("--csv", action="store_true", help="also output CSV files")
parser.add_argument("--partition", action="store_true", help="partition by organisation")
args = parser.parse_args()
download_datasets(args.dataset, args.organization, args.folder, args.refresh, args.token_path, args.csv, args.partition)
