"""Download, cache and hydrate data files from the Matbench Discovery Figshare article.

https://figshare.com/articles/dataset/22715158
"""

import gzip
import json
import os
import pickle
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from enum import StrEnum
from glob import glob
from pathlib import Path
from typing import Any, Self

import pandas as pd
from monty.json import MontyDecoder
from pymatgen.analysis.phase_diagram import PatchedPhaseDiagram
from pymatviz.enums import Key
from tqdm import tqdm

from matbench_discovery import FIGSHARE_DIR

# ruff: noqa: T201

# repo URL to raw files on GitHub
RAW_REPO_URL = "https://github.com/janosh/matbench-discovery/raw"
figshare_versions = sorted(
    x.split(os.path.sep)[-1].split(".json")[0] for x in glob(f"{FIGSHARE_DIR}/*.json")
)
# directory to cache downloaded data files
default_cache_dir = os.getenv(
    "MATBENCH_DISCOVERY_CACHE_DIR",
    f"{os.path.expanduser('~/.cache/matbench-discovery')}/{figshare_versions[-1]}",
)


def as_dict_handler(obj: Any) -> dict[str, Any] | None:
    """Pass this to json.dump(default=) or as pandas.to_json(default_handler=) to
    serialize Python classes with as_dict(). Warning: Objects without a as_dict() method
    are replaced with None in the serialized data.
    """
    try:
        return obj.as_dict()  # all MSONable objects implement as_dict()
    except AttributeError:
        return None  # replace unhandled objects with None in serialized data
        # removes e.g. non-serializable AseAtoms from M3GNet relaxation trajectories


def load(
    key: str,
    *,
    version: str = figshare_versions[-1],
    cache_dir: str | Path = default_cache_dir,
    hydrate: bool = False,
    **kwargs: Any,
) -> pd.DataFrame | PatchedPhaseDiagram:
    """Download parts of or the full MP training data and WBM test data as pandas
    DataFrames. The full training and test sets are each about ~500 MB as compressed
    JSON which will be cached locally to cache_dir for faster re-loading unless
    cache_dir is set to None.

    See matbench_discovery.data.DATA_FILES for recognized data keys. See [here]
    (https://janosh.github.io/matbench-discovery/contribute#--direct-download) for file
    descriptions.

    Args:
        key (str): Which parts of the MP/WBM data to load. Must be one of
            list(DATA_FILES).
        version (str, optional): Which version of the dataset to load. Defaults to
            latest version of data files published to Figshare. Pass any invalid version
            to see valid options.
        cache_dir (str, optional): Where to cache data files on local drive. Defaults to
            '~/.cache/matbench-discovery'. Set to None to disable caching.
        hydrate (bool, optional): Whether to hydrate pymatgen objects. If False,
            Structures and ComputedStructureEntries are returned as dictionaries which
            can be hydrated on-demand with df.col.map(Structure.from_dict). Defaults to
            False as it noticeably increases load time.
        **kwargs: Additional keyword arguments passed to pandas.read_json or read_csv,
            depending on which file is loaded.

    Raises:
        ValueError: On bad version number or bad data_key.

    Returns:
        pd.DataFrame: Single dataframe or dictionary of dfs if multiple data requested.
    """
    if version not in figshare_versions:
        raise ValueError(f"Unexpected {version=}. Must be one of {figshare_versions}.")

    if not isinstance(key, str) or key not in DATA_FILES:
        raise ValueError(f"Unknown {key=}, must be one of {list(DATA_FILES)}.")

    with open(f"{FIGSHARE_DIR}/{version}.json") as json_file:
        file_urls = json.load(json_file)["files"]

    file_path = DataFiles.__dict__[key]

    cache_path = f"{cache_dir}/{file_path}"
    if not os.path.isfile(cache_path):  # download from Figshare URL
        url = file_urls[key][0]
        print(f"Downloading {key!r} from {url}")
        try:
            # ensure directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            # download and save to disk
            urllib.request.urlretrieve(url, cache_path)
            print(f"Cached {key!r} to {cache_path!r}")
        except urllib.error.HTTPError as exc:
            raise ValueError(f"Bad {url=}") from exc
        except Exception:
            print(f"\n\nvariable dump:\n{file_path=},\n{url=}")
            raise

    print(f"Loading {key!r} from cached file at {cache_path!r}")
    if ".pkl" in file_path:  # handle key='mp_patched_phase_diagram' separately
        with gzip.open(cache_path, "rb") as zip_file:
            return pickle.load(zip_file)  # noqa: S301
    if ".pth" in file_path:  # handle model checkpoints (e.g. key='alignn_checkpoint')
        return cache_path

    csv_ext = (".csv", ".csv.gz", ".csv.bz2")
    reader = pd.read_csv if file_path.endswith(csv_ext) else pd.read_json
    try:
        df_out = reader(cache_path, **kwargs)
    except Exception:
        print(f"\n\nvariable dump:\n{file_path=},\n{reader=}\n{kwargs=}")
        raise

    if Key.mat_id in df_out:
        df_out = df_out.set_index(Key.mat_id)
    if hydrate:
        for col in df_out:
            if not isinstance(df_out[col].iloc[0], dict):
                continue
            try:
                # convert dicts to pymatgen Structures and ComputedStructureEntries
                df_out[col] = [
                    MontyDecoder().process_decoded(dct)
                    for dct in tqdm(df_out[col], desc=col)
                ]
            except Exception:
                print(f"\n\nvariable dump:\n{col=},\n{df_out[col]=}")
                raise

    return df_out


def glob_to_df(
    pattern: str,
    *,
    reader: Callable[[Any], pd.DataFrame] | None = None,
    pbar: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """Combine data files matching a glob pattern into a single dataframe.

    Args:
        pattern (str): Glob file pattern.
        reader (Callable[[Any], pd.DataFrame], optional): Function that loads data from
            disk. Defaults to pd.read_csv if ".csv" in pattern else pd.read_json.
        pbar (bool, optional): Whether to show progress bar. Defaults to True.
        **kwargs: Keyword arguments passed to reader (i.e. pd.read_csv or pd.read_json).

    Returns:
        pd.DataFrame: Combined dataframe.
    """
    reader = reader or pd.read_csv if ".csv" in pattern.lower() else pd.read_json

    # prefix pattern with ROOT if not absolute path
    files = glob(pattern)
    if len(files) == 0:
        raise FileNotFoundError(f"No files matching glob {pattern=}")

    sub_dfs = {}  # used to join slurm job array results into single df
    for file in tqdm(files, disable=not pbar):
        df_i = reader(file, **kwargs)
        sub_dfs[file] = df_i

    return pd.concat(sub_dfs.values())


class DataFiles(StrEnum):
    """Enum of data files with associated file directories and URLs."""

    def __new__(cls, file_path: str) -> Self:
        """Create a new member of the FileUrls enum with a given URL where to load the
        file from and directory where to save it to.
        """
        obj = str.__new__(cls)
        file_name = file_path.split("/")[-1]
        obj._value_ = file_name

        obj._file_path = f"{default_cache_dir}/{file_path}"  # noqa: SLF001
        return obj

    def __str__(self) -> str:
        """Return the file path associated with the file URL. Use str(DataFiles.some_key)
        if you want the file path without auto-downloading the file if it doesn't exist
        yet, e.g. for use in the script that generates the file in the first place.
        """
        return self._file_path

    @property
    def path(self) -> str:
        """Return the file path associated with the file URL if it exists, otherwise
        download the file first, then return the path.
        """
        key, path = self.name, self._file_path

        if not os.path.isfile(self._file_path):
            msg = (
                f"{path!r} associated with {key=} does not exist. Would you like to "
                "download it now? This will cache the file for future use."
            )

            # default to 'y' if not in interactive session, and user can't answer
            answer = "" if sys.stdin.isatty() else "y"
            while answer not in ("y", "n"):
                answer = input(f"{msg} [y/n] ").lower().strip()
            if answer == "y":
                load(key)  # download and cache data file
        return path

    mp_computed_structure_entries = (
        "mp/2023-02-07-mp-computed-structure-entries.json.gz"
    )
    mp_elemental_ref_entries = "mp/2023-02-07-mp-elemental-reference-entries.json.gz"
    mp_energies = "mp/2023-01-10-mp-energies.csv.gz"
    mp_patched_phase_diagram = "mp/2023-02-07-ppd-mp.pkl.gz"
    mp_trj_extxyz = "mp/2023-11-22-mp-trj-extxyz-by-yuan.zip"
    # snapshot of every task (calculation) in MP as of 2023-03-16 (14 GB)
    all_mp_tasks = "mp/2023-03-16-all-mp-tasks.zip"

    wbm_computed_structure_entries = (
        "wbm/2022-10-19-wbm-computed-structure-entries.json.bz2"
    )
    wbm_initial_structures = "wbm/2022-10-19-wbm-init-structs.json.bz2"
    wbm_cses_plus_init_structs = (
        "wbm/2022-10-19-wbm-computed-structure-entries+init-structs.json.bz2"
    )
    wbm_summary = "wbm/2023-12-13-wbm-summary.csv.gz"

    alignn_checkpoint = "2023-06-02-pbenner-best-alignn-model.pth.zip"


# data files can be downloaded and cached with matbench_discovery.data.load()
DATA_FILES = DataFiles()


df_wbm = load("wbm_summary")
# str() around Key.mat_id added for https://github.com/janosh/matbench-discovery/issues/81
df_wbm[str(Key.mat_id)] = df_wbm.index
