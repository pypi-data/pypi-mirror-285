"""minder.research-data-snapshots."""

import os
import re
from functools import cache
from pathlib import Path

import platformdirs
import requests
from tqdm import tqdm


@cache
def _get_organizations(token: str, api: str) -> dict[str, str]:
    response = requests.get(
        f"{api}/info/organizations",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    response.raise_for_status()
    return {organization["name"]: organization["id"] for organization in response.json()["organizations"]}


def _download_dataset(
    dataset: str,
    organization: str,
    folder: Path,
    refresh: bool,
    token: str,
    api: str,
    partition: bool,
) -> Path:
    file = (
        (folder / dataset / f"organization={organization}" / "part-0").with_suffix(".parquet")
        if partition
        else (folder / organization / dataset).with_suffix(".parquet")
    )
    if file.exists() and not refresh:
        return file
    file.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(
        f"{api}/data/organization/{organization}/{dataset}.parquet",
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=3600,
    )
    response.raise_for_status()
    with file.open(mode="wb") as f:
        progress = tqdm(
            desc=str(file),
            total=int(response.headers.get("content-length", -1)),
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        )
        for chunk in response.iter_content(1024):
            f.write(chunk)
            progress.update(len(chunk))
    return file


def download_datasets(
    datasets: list[str],
    organizations: list[str] | None = None,
    folder: Path | None = None,
    refresh: bool = False,
    token_path: Path | None = None,
    csv: bool = False,
    partition: bool = False,
) -> list[Path]:
    """Download one or more datasets.

    Parameters
    ----------
    datasets
        List of datasets to retrieve e.g. `["raw_heart_rate"]`
    organizations
        List of cohorts to include e.g. `["EMXHH7vg3xHNM7k2862nD6"]`. Defaults to all cohorts that you have access to.
    folder
        Path of destination folder for downloaded files. Defaults to user data folder (exact location depends on your
        operating system).
    refresh
        Whether to overwrite existing files. Set this to `True` if you want to update your downloaded data. Defaults to
        `False`.
    token_path
        Path of file containing your personal access token (PAT) from the Research Portal. If not specified then the
        value of the `RESEARCH_PORTAL_TOKEN_PATH` environment variable is used.
    csv
        Convert Parquet files to CSV. Set this to `True` if you're using Excel for data analysis. Otherwise Parquet is a
        superior format. Defaults to `False`.
    partition
        Arrange Parquet files in destination folder by organisation using Hive partitioning scheme. Defaults to `False`.

    Returns
    -------
    List of paths of downloaded Parquet files. Length will be number of datasets * number of cohorts.

    """
    RESEARCH_PORTAL_API = os.getenv("RESEARCH_PORTAL_API", "https://research.minder.care/api")
    MINDER_TOKEN = (
        os.environ["MINDER_TOKEN"]
        if "MINDER_TOKEN" in os.environ
        else Path(token_path or os.environ["RESEARCH_PORTAL_TOKEN_PATH"]).read_text("utf-8").rstrip()
    )
    if organizations is None:
        organizations = list(_get_organizations(MINDER_TOKEN, RESEARCH_PORTAL_API).values())
    if folder is None:
        folder = platformdirs.user_cache_path("research-data-snapshots")
    organizations = [
        organization
        if re.match(r"^[A-HJ-NP-Za-km-z1-9]{16,22}$", organization)
        else _get_organizations(MINDER_TOKEN, RESEARCH_PORTAL_API)[organization]
        for organization in organizations
    ]
    parquets = [
        _download_dataset(dataset, organization, folder, refresh, MINDER_TOKEN, RESEARCH_PORTAL_API, partition)
        for dataset in datasets
        for organization in organizations
    ]
    if csv:
        import pyarrow.csv
        import pyarrow.lib
        import pyarrow.parquet

        csvs = []
        for parquet in parquets:
            csv_path = parquet.with_suffix(".csv")
            try:
                pyarrow.csv.write_csv(pyarrow.parquet.read_table(parquet), csv_path)
            except pyarrow.lib.ArrowInvalid:
                import pandas as pd

                pd.read_parquet(parquet).to_csv(csv_path, index=False, date_format="%Y-%m-%d %H:%M:%S.%fZ")
            csvs.append(csv_path)
        return csvs
    return parquets
