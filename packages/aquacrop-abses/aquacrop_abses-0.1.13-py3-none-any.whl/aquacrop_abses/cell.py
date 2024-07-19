#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""每个单元格
"""

from datetime import datetime
from typing import Iterable, List, Optional, Tuple, TypeAlias

import pandas as pd
from abses.cells import PatchCell, raster_attribute
from abses.tools.func import make_list
from aquacrop import Crop, GroundWater, InitialWaterContent, Soil

from aquacrop_abses.load_datasets import (
    clean_crop_type,
    get_crop_dates,
    load_soil_textures_table,
)

CropTypes: TypeAlias = Crop | Iterable[Crop] | str | Iterable[str]

VALID_SOILS = [
    "Custom",
    "Clay",
    "ClayLoam",
    "Default",
    "Loam",
    "LoamySand",
    "Sand",
    "SandyClay",
    "SandyClayLoam",
    "SandyLoam",
    "Silt",
    "SiltClayLoam",
    "SiltLoam",
    "SiltClay",
    "Paddy",
    "ac_TunisLocal",
]
DT_PATTERN = r"%Y/%m/%d"


def is_overlapping(
    start: datetime, end: datetime, start_2: datetime, end_2: datetime
) -> bool:
    """Check if two time intervals overlap."""
    return start <= end_2 and start_2 <= end


def get_crop_datetime(crop: Crop, year: int) -> Tuple[datetime, datetime]:
    """Get the planting and harvest dates for a crop in a given year."""
    planting_date = datetime.strptime(f"{year}/{crop.planting_date}", DT_PATTERN)
    harvest_date = datetime.strptime(f"{year}/{crop.harvest_date}", DT_PATTERN)
    if harvest_date < planting_date:
        harvest_date = datetime.strptime(f"{year + 1}/{crop.harvest_date}", DT_PATTERN)
    return planting_date, harvest_date


class CropCell(PatchCell):
    """种植作物的一个斑块。"""

    _soil_properties = load_soil_textures_table()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._crop_tick = self.time.tick
        self._crop_types: List[Crop] = []
        self._soil: Optional[str] = None
        self.groundwater: Optional[GroundWater] = None

    @property
    def init_wc(self) -> InitialWaterContent:
        """初始含水情况"""
        return InitialWaterContent(value=["FC"])

    @property
    def weather(self) -> pd.DataFrame:
        """气候"""
        return self.layer.get_weather_df(self)

    @property
    def soil(self) -> str:
        """土壤类型"""
        if self._soil is None:
            return "Default"
        return self._soil

    @soil.setter
    def soil(self, soil_type: Optional[str]) -> None:
        if isinstance(soil_type, Soil):
            soil_type = soil_type.Name
        if isinstance(soil_type, int):
            soil_type = self._soil_properties["Type"].get(soil_type, "Default")
        if isinstance(soil_type, str):
            if soil_type not in VALID_SOILS:
                raise ValueError(f"Invalid soil type: {soil_type}")
        self._soil = soil_type

    def _check_crop_overlapping(self, crop: Crop) -> None:
        for existing_crop in self._crop_types:
            if is_overlapping(
                *get_crop_datetime(crop, self.time.year),
                *get_crop_datetime(existing_crop, self.time.year),
            ):
                raise ValueError(
                    f"Crops overlap: {crop.Name} and existing {existing_crop.Name}."
                )

    @property
    def crops(self) -> List[Crop]:
        """Add crop."""
        return self._crop_types

    @crops.setter
    def crops(self, crops: CropTypes) -> None:
        """设置该地块的作物类型。"""
        for crop in make_list(crops):
            if isinstance(crop, str):
                dates = get_crop_dates(crop)
                crop = clean_crop_type(crop)
                crop = Crop(crop, **dates)
            if not isinstance(crop, Crop):
                raise TypeError("Crop must be a Crop.")
            self._check_crop_overlapping(crop=crop)
            self._crop_types.append(crop)

    def clean(self) -> None:
        """清除作物"""
        self._crop_types = []

    @raster_attribute
    def has_crops(self) -> int:
        """有多少农作物"""
        return len(self.crops)

    @property
    def crops_datetime(self) -> Tuple[datetime, datetime]:
        """所有农作物当前年份的生长周期"""
        planting_dates, harvest_dates = [], []
        for crop in self.crops:
            d1, d2 = get_crop_datetime(crop=crop, year=self.time.year)
            planting_dates.append(d1)
            harvest_dates.append(d2)
        return min(planting_dates), max(harvest_dates)
