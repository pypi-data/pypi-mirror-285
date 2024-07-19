#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""自然系统
"""
from typing import Dict

import numpy as np
import rioxarray as rxr
import xarray as xr
from abses import PatchModule
from abses.patch import Raster
from loguru import logger
from omegaconf import DictConfig

from aquacrop_abses.load_datasets import load_datasets, select_climate_ds_by_year

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

ClimateDatasets: TypeAlias = Dict[str, xr.DataArray]


class CropLand(PatchModule):
    """Where to crop."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_datasets = None
        self._cached_tick = None

    @property
    def climate(self) -> ClimateDatasets:
        """气象数据集"""
        if self.time.year == self._cached_tick:
            return self._cached_datasets
        ds = self.load_climate(self.ds.mete)
        # 重投影数据集
        if reproject := self.ds.mete.get("reproject"):
            self._reproject_datasets(ds, **reproject)
        self._cached_datasets = ds
        self._cached_tick = self.time.year
        return ds

    def _reproject_datasets(self, ds: ClimateDatasets, **kwargs) -> None:
        """重投影数据集"""

        def _reproject_by_time(da: xr.DataArray) -> xr.DataArray:
            reprojected_list = []
            for time_step in da.time:
                tmp_res = self.reproject(da.sel(time=time_step), **kwargs)
                reprojected_list.append(tmp_res)
            return xr.concat(reprojected_list, dim="time")

        crs = kwargs.pop("crs", self.crs)
        dims = dict(kwargs.pop("dims", {}))
        for varname, da in ds.items():
            da.rio.write_crs(crs, inplace=True)
            ds[varname] = _reproject_by_time(da.rename(dims))
            logger.debug(f"Reprojected {varname} dataset to match CropLand.")

    def load_climate(self, mete_config: DictConfig) -> ClimateDatasets:
        """获得近两年的气象数据集"""
        if mete_config.multi_files:
            return select_climate_ds_by_year(
                folder=mete_config.dir,
                pattern=mete_config.pattern,
                year=self.time.year,
                check_attrs=mete_config.get("check_attrs", True),
                var_names=mete_config.var_names,
            )
        return load_datasets(mete_config.paths, self.time.year)

    def load_soil_type(self, soil: Raster | str) -> None:
        """加载土壤类型"""
        if isinstance(soil, str):
            soil = rxr.open_rasterio(soil)
            logger.info(f"Loaded soil type from {soil}")
        self.apply_raster(soil, "soil", resampling_method="mode")
        logger.debug("Soil dataset resampled by 'mode'.")
        soils = self.cells.array("soil")
        for soil_type in np.unique(soils):
            logger.debug(
                f"Soil type {soil_type} has {np.sum(soils == soil_type)} pixels."
            )
