#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
加载气象数据集
"""

from datetime import date
from functools import lru_cache, wraps
from importlib import resources
from pathlib import Path
from typing import Dict, Optional, Tuple, cast

import pandas as pd
import xarray as xr
import yaml
from aquacrop.entities.crop import crop_params
from cmfd_handler.io import BatchHandler, ChinaMeteForcingData
from loguru import logger

CROPS_FOLDER = resources.files("res") / "crops"

# 读取字典
_KW = resources.files("res") / "kw_dictionary.yaml"
with open(Path(str(_KW)), "r", encoding="utf-8") as f:
    KWARGS = yaml.safe_load(f)


METE_VARS = ("MinTemp", "MaxTemp", "Precipitation", "ReferenceET")


def clean_crop_type(crop: str) -> str:
    """清洗并检查作物类型是否有效"""
    crop = KWARGS["crops"].get(crop, crop)
    if crop not in crop_params.keys():
        logger.critical(f"Unknown crop type: {crop}")
    return crop


def check_file_path(func=None, *, path_arg_name="path"):
    """Decorator to check if the file path exists."""
    if func is None:
        return lambda func: check_file_path(func, path_arg_name=path_arg_name)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the path parameter based on its name or position
        path_index = (
            func.__code__.co_varnames.index(path_arg_name)
            if path_arg_name in func.__code__.co_varnames
            else 0
        )
        path = kwargs.get(
            path_arg_name, args[path_index] if path_index < len(args) else None
        )

        # Perform the path checks
        if isinstance(path, str):
            path = Path(path)
        if not isinstance(path, Path):
            raise ValueError(f"Invalid type for path: {type(path)}")
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File {path} not found.")

        # Proceed with the original function
        return func(*args, **kwargs)

    return wrapper


def _load_dataset(
    path: Path | str,
    varname: str,
    year: Optional[int] = None,
) -> xr.DataArray:
    """加载一个气象数据集。
    Returns:
        3 dimensions: time, lat, lon
        有两年，分别是 year 和 year+1，日尺度数据集。
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"File {path} not found.")
    data_array = xr.open_dataset(path)
    if isinstance(data_array, xr.Dataset):
        data_array = data_array[varname]
    if year:
        time = slice(f"{year}-01-01", f"{year + 1}-12-31")
        return data_array.sel(time=time)
    return data_array


def load_datasets(
    ds_names: Dict[str, str | Path],
    year: Optional[int] = None,
    fillna: bool = True,
) -> Dict[str, xr.DataArray]:
    """一次性加载多个气象数据集。

    Parameters:
        folder: Path, the folder where the datasets are stored.
        ds_names: dict, key is the variable name, value is the filename.
        year: int, the year of the simulation.

    Returns:
        dict, key is the variable name, value is the dataset.
    """
    datasets = {}
    for varname, file_path in ds_names.items():
        path = Path(file_path)
        data = _load_dataset(path, varname, year=year)
        # 这里进行了简单的填充，以防止出现 NaN
        if fillna:
            data = data.fillna(data.mean())
        datasets[varname] = data
    return datasets


@lru_cache
def load_cmf_datasets(
    folder: Path | str,
    pattern: str,
    check_attrs: bool = True,
) -> BatchHandler:
    """加载 CMFD 数据集。"""
    CMFD = ChinaMeteForcingData(folder, freq="D")
    handler = CMFD.batch_executor(is_out_data=True, pattern=pattern)
    handler.check(check_attrs=check_attrs)
    return handler


def select_climate_ds_by_year(
    folder: Path | str,
    pattern: str,
    year: int,
    check_attrs: Optional[bool] = False,
    var_names: Tuple[str, ...] = ("pet", "max_temp", "min_temp", "prec_mm"),
) -> Dict[str, xr.DataArray]:
    """根据年份选择气象数据集。

    Args:
        folder: Path, the folder where the datasets are stored.

    Returns:
        dict, key is the variable name, value is the dataset.
    """
    handler = load_cmf_datasets(folder, pattern, check_attrs=check_attrs)
    date_slice = slice(f"{year}-01-01", f"{year + 1}-01-01")
    datasets = {}
    for varname in var_names:
        xda = handler.merge_data(var=varname, date_slice=date_slice)
        # datasets[varname] = xda.fillna(xda.mean())
        datasets[varname] = xda.pint.dequantify()
    return datasets


def convert_to_dataframe(
    datasets: Dict[str, xr.DataArray],
    coordinate: Tuple[float, float],
    var_mapping: Optional[Dict[str, str]] = None,
    dims: Tuple[str, str] = ("lat", "lon"),
) -> pd.DataFrame:
    """将多个数据集转换为 DataFrame。

    Parameters:
        datasets:

    Returns:
        DataFrame with columns: time, varname1, varname2, ...
    """
    lon, lat = coordinate
    # 检查变量名称映射
    if var_mapping is None:
        var_mapping = {var: var for var in METE_VARS}
        logger.warning(
            f"No variable mapping provided. Using default mapping {var_mapping}."
        )
    else:
        for var in METE_VARS:
            if var not in var_mapping:
                logger.warning(f"Variable {var} not found.")
                var_mapping[var] = var
    rename = {var_mapping[var]: var for var in var_mapping}
    # 选择数据
    df = pd.DataFrame()
    for varname, ds in datasets.items():
        # 根据经纬度选择数据
        kwargs = {dim: coord for dim, coord in zip(dims, (lat, lon))}
        selected_data = ds.sel(**kwargs, method="nearest")
        # 选择到对应的数据和日期索引，重置索引
        tmp_df = selected_data.to_dataframe()[varname].reset_index()
        tmp_df["time"] = pd.to_datetime(tmp_df["time"].values).normalize()
        # 合并数据
        if df.empty:
            df = tmp_df
        else:
            df = pd.merge(df, tmp_df, on="time", how="outer")
    # 参考 AquaCrop 的数据处理，以防止出现过小的分母
    df["pet"] = df["pet"].clip(lower=0.1)
    # 重命名列名，与 AquaCrop 的数据处理一致
    df.rename(rename, axis=1, inplace=True)
    # 列名必须排序好
    return df[rename.values()]


def get_crop_dates(crop, folder: Optional[Path] = None) -> Dict[str, str]:
    """获取作物的种植和收获日期。

    Args:
        path: Path, the path to the file.

    Returns:
        tuple, (planting_date, harvesting_date)
    """
    if folder is None:
        logger.debug(f"Loading crops from {CROPS_FOLDER}")
        folder = cast(Path, CROPS_FOLDER)
    with open(folder / f"{crop}.yaml", "r", encoding="utf-8") as file:
        crop = yaml.safe_load(file)
    start_dt: date = crop["start"]
    end_dt: date = crop["end"]
    return {
        "planting_date": start_dt.strftime(r"%m/%d"),
        "harvest_date": end_dt.strftime(r"%m/%d"),
    }


def load_soil_textures_table():
    """Load the soil textures table."""
    return pd.read_csv(resources.files("res") / "SoilTexture.csv", index_col=0)


@check_file_path
def get_stat_data(path: str | Path) -> pd.DataFrame:
    """获取国家统计局的数据。

    Args:
        path: Path, the path to the file.

    Returns:
        dict, key is the variable name, value is the value.
    """
    with open(path, "r", encoding="gbk") as file:
        skipped_lines = [next(file).strip() for _ in range(3)]
    print(skipped_lines[1], skipped_lines[2])
    return pd.read_csv(path, encoding="gbk", skiprows=3, skipfooter=2, engine="python")
