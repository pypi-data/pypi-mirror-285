#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

"""
这个脚本定义了农民类。

农民应该根据当前的可用水量，选择自己的灌溉策略。
"""

from typing import Dict, List, Literal, Optional, Union, overload

import numpy as np
import pandas as pd
import xarray as xr
from abses import Actor
from aquacrop import AquaCropModel, Crop, FieldMngt, IrrigationManagement, Soil
from loguru import logger
from sko.GA import GA

from aquacrop_abses.cell import DT_PATTERN, CropCell
from aquacrop_abses.load_datasets import convert_to_dataframe

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias


DY = "Dry yield (tonne/ha)"
FY = "Fresh yield (tonne/ha)"
YP = "Yield potential (tonne/ha)"
IRR = "Seasonal irrigation (mm)"

YieldItem: TypeAlias = Literal[
    "dry_yield",
    "fresh_yield",
    "yield_potential",
]


class Farmer(Actor):
    """
    可以选择自己灌溉策的农民行动者。。

    Irrigation management parameters are selected by creating an `IrrigationManagement` object.
    With this class we can specify a range of different irrigation management strategies.
    The 6 different strategies can be selected using the `IrrMethod` argument:

    - `IrrMethod=0`: Rainfed (no irrigation)
    - `IrrMethod=1`: Irrigation if soil water content drops below a specified threshold.
    Four thresholds representing four major crop growth stages
    (emergence, canopy growth, max canopy, senescence).
    - `IrrMethod=2`: Irrigation in every N days
    - `IrrMethod=3`: Predefined irrigation schedule
    - `IrrMethod=4`: Net irrigation
    (maintain a soil-water level by topping up all compartments daily)
    - `IrrMethod=5`: Constant depth applied each day

    预测得到的结果包括：
    - fy: "Fresh yield (tonne/ha)"
    - dy: "Dry yield (tonne/ha)"
    - yp: "Yield potential (tonne/ha)"
    - irr: "Seasonal irrigation (mm)"
    """

    irr_methods = {
        0: "Rainfed",
        1: "Soil Moisture Targets",
        2: "Set Time Interval",
        3: "Predefined Schedule",
        4: "Net Irrigation",
        5: "Constant Depth",
    }

    def __init__(self, *args, single: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # 只有一个作物的情况
        self._single_crop = single
        # 灌溉策略
        self.irr_method: int = self.p.get("irr_method", 0)
        # 当前年份的产量估算结果
        self._results: pd.DataFrame = pd.DataFrame()

    def __repr__(self) -> str:
        irr: str = self.irr_methods[self.irr_method]
        return f"<{self.unique_id} [{irr}]>"

    @property
    def crop_here(self) -> Crop | List[Crop]:
        """当前地块上的作物"""
        crops = self.get("crops")
        return crops[0] if self._single_crop else crops

    @property
    def irr_method(self) -> int:
        """灌溉策略"""
        return self._irr_method

    @irr_method.setter
    def irr_method(self, value: int) -> None:
        if value not in self.irr_methods:
            raise ValueError(f"Invalid value for irr_method: {value}.")
        self._irr_method = value

    @property
    def field_management(self) -> FieldMngt:
        """当前的田间管理策略"""
        return FieldMngt(**self.p.get("FieldMngt", {}))

    @property
    def dry_yield(self) -> pd.Series | float:
        """当前年份的干产量"""
        return self._results.get(DY)

    @property
    def fresh_yield(self) -> pd.Series | float:
        """当前年份的湿产量"""
        return self._results.get(FY)

    @property
    def yield_potential(self) -> pd.Series | float:
        """当前年份的潜在产量"""
        return self._results.get(YP)

    @property
    def seasonal_irrigation(self) -> pd.Series | float:
        """当前年份的灌溉量"""
        if self._single_crop:
            return self._results.get(IRR)
        return self._results[IRR].sum()

    def irr_management(self, **kwargs) -> IrrigationManagement:
        """当前的灌溉管理策略。"""
        params = self.p.get("IrrigationManagement", {})
        params.update(kwargs)
        return IrrigationManagement(irrigation_method=self.irr_method, **params)

    def optimize_smt(
        self,
        weather_df: pd.DataFrame,
        size_pop: int = 50,
        max_iter: int = 50,
        prob_mut: float = 0.001,
        **kwargs,
    ) -> pd.DataFrame:
        """以土壤水为目标，优化灌溉管理策略。
        使用该方法后，将会更新 `irr_method` 属性为 1。
        即分别设置四个阶段的土壤水量目标，每个阶段都是 0-100% 的浮点数。

        Parameters:
            weather_df:
                包含气象数据的 DataFrame。
            size_pop:
                种群大小。
            max_iter:
                最大迭代次数。
            prob_mut:
                变异概率。
            **kwargs:
                用来覆盖默认灌溉管理措施参数的关键字参数。

        Returns:
            优化后灌溉策略的产量数据。
        """
        self.irr_method = 1

        def fitness(smts: np.ndarray) -> float:
            reward = self.simulate(
                weather_df, is_test=True, SMT=smts.tolist(), **kwargs
            )
            return 0 - reward

        ga = GA(
            func=fitness,
            n_dim=4,
            size_pop=size_pop,
            max_iter=max_iter,
            prob_mut=prob_mut,
            lb=[0, 0, 0, 0],
            ub=[100, 100, 100, 100],
            precision=10.0,
        )
        best_x, best_y = ga.run()
        logger.debug(f"Best SMT: {best_x}, Reward: {0 - best_y}")
        return self.simulate(weather_df, SMT=best_x.tolist(), **kwargs)

    @overload
    def simulate(
        self, weather_df: pd.DataFrame, is_test: bool = True, **kwargs
    ) -> float:
        ...

    @overload
    def simulate(
        self, weather_df: pd.DataFrame, is_test: bool = False, **kwargs
    ) -> pd.DataFrame:
        ...

    def simulate(
        self, weather_df: pd.DataFrame, is_test: bool = False, **kwargs
    ) -> Union[pd.DataFrame, float]:
        """模拟本地块上所有作物的生长。

        Parameters:
            weather_df:
                包含气象数据的 DataFrame。
            is_test:
                如果为 True，只返回产量数据，用来模型调优。
            **kwargs:
                用来覆盖默认灌溉管理措施参数的关键字参数。

        Returns:
            如果 `is_test` 为 True，返回产量数据。
            否则返回一个 DataFrame，包含所有作物的模拟结果。
        """
        if self._single_crop:
            res = self.simulate_once(self.crop_here, weather_df, **kwargs)
            if is_test:
                return res.get(DY)
            res["Season"] = self.time.year
            self._results = res.iloc[0, :]
        else:
            data = []
            for crop in self.crop_here:
                res = self.simulate_once(crop, weather_df, **kwargs)
                data.append(res)
            result_all = pd.concat(data)
            if is_test:
                return result_all[DY].sum()
            result_all["Season"] = self.time.year
            self._results = result_all.set_index("crop Type")
        return self._results

    def simulate_once(
        self,
        crop: Crop,
        weather_df: pd.DataFrame,
        cell: Optional[CropCell] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """模拟一个时间步长。
        这个时间步应该是一年，因为作物通常按年来种植。
        但是气象数据集是按日来的，而且有些作物会跨年。
        所以我们用两个自然年的数据来模拟一个作物年。
        """
        if cell is None:
            cell = self.at
        start_dt, end_dt = cell.crops_datetime
        model = AquaCropModel(
            sim_start_time=start_dt.strftime(DT_PATTERN),
            sim_end_time=end_dt.strftime(DT_PATTERN),
            weather_df=weather_df,  # fixed
            soil=Soil(cell.soil),  # fixed
            crop=crop,  # fixed
            initial_water_content=cell.init_wc,  # fixed?
            # 这里灌溉管理策略是可变的
            irrigation_management=self.irr_management(**kwargs),
            field_management=self.field_management,  # fixed/strategy
            groundwater=cell.groundwater,  # fixed
        )
        model.run_model(till_termination=True)
        return model.get_simulation_results()

    def weather_data(
        self,
        climate_ds: Dict[str, xr.DataArray],
        var_mapping: Dict[str, str],
        crops_dates_only: bool = False,
        cell: Optional[CropCell] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Load data from a climate dataset."""
        if cell is None:
            cell = self.at
        df = convert_to_dataframe(
            datasets=climate_ds,
            coordinate=cell.coordinate,
            var_mapping=var_mapping,
            **kwargs,
        )
        if crops_dates_only:
            start, end = cell.crops_datetime
            df = df[(df["Date"] >= start) & (df["Date"] <= end)]
        return df
