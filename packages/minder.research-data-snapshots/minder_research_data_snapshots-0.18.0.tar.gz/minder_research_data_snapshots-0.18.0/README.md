# minder.research-data-snapshots

## Install

```sh
python -m pip install minder.research-data-snapshots
```

This will provide exports in Parquet format, which should be sufficient if you're using Pandas or another dataframe library.

If you require exports in CSV format then use:

```sh
python -m pip install 'minder.research-data-snapshots[csv]'
```

## Use

First retrieve an access token from <https://research.minder.care/>

```sh
export RESEARCH_PORTAL_TOKEN_PATH=/path/to/access/token
```

Then use one of the following methods to retrieve data snapshots

### CLI

```sh
python -m minder.research_data_snapshots --dataset patients raw_heart_rate --organization SABP "H&F"
```

Run `python -m minder.research_data_snapshots --help` to see all options

### Library

```sh
python -m pip install 'pandas[parquet]'
```

```python
from datetime import datetime

import pandas as pd

from minder.research_data_snapshots import download_datasets

path = download_datasets(["patients"], ["ELM4RQF8R9dsU3CZEgtiTW"])[0]
df = pd.read_parquet(path)
print(df)

paths = download_datasets(["raw_heart_rate"])
df = pd.concat(
    pd.read_parquet(
        path,
        filters=[
            ("start_date", ">=", datetime.fromisoformat("2023-01-01T00Z")),
            ("start_date", "<", datetime.fromisoformat("2024-01-01T00Z")),
        ],
        columns=["id", "patient_id", "start_date"],
    )
    for path in paths
).sort_values("start_date").reset_index(drop=True)
```
