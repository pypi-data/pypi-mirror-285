#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/8 15:05
# @Author  : willingwu@futunn.com
# @File    : start_limitation.py
import datetime
# import time
from typing import List, Optional, Any

from django.db.models import IntegerChoices
# from django.utils.timezone import localtime
from pydantic import BaseModel, Field


class ReferMarketIDEnum(IntegerChoices):
    HK = 1, "港股"
    US = 23, "美股"
    CN = 32, "A股"
    USQQ = 44, "美股期权"
    HKQQ = 8, "港股期权"
    FX = 120, "外汇"
    SGGP = 180, "新加坡股票"
    JPQH = 185, "日本期货",
    # FD = 1, "基金"
    CSTSX = 200, "加拿大股票"
    AU = 210, "澳大利亚股票"
    JP = 830, "日本股票"


class TimeRangeConfig(BaseModel):
    days_of_week: List[int] = Field(description="周一到周几")
    start: str = Field(description="开始时刻")
    end: str = Field(description="结束时刻")

    @property
    def start_time(self) -> datetime.time:
        return datetime.datetime.strptime(self.start, "%H:%M:%S").time()

    @property
    def end_time(self) -> datetime.time:
        return datetime.datetime.strptime(self.end, "%H:%M:%S").time()
    
    def is_match(self, compare_time: datetime.datetime=None) -> bool:
        if compare_time is None:
            compare_time = datetime.datetime.now()
        if self.start_time <= compare_time.time() <= self.end_time:
            if compare_time.weekday() + 1 in self.days_of_week:
                return True
        return False


class MarketStatusConfig(BaseModel):
    market_id: ReferMarketIDEnum = Field(description="代表市场ID 从上述的市场ID里面选择")
    status: List[int] = Field(description="匹配的市场状态")
    description: Optional[str] = Field(description="市场状态展示文案", default="")

    def is_match(self) -> bool:
        from time_limitation_module.utils.market import get_market_current_status
        print(get_market_current_status(self.market_id))
        return get_market_current_status(self.market_id) in self.status


class TaskStartLimitationConfig(BaseModel):
    time_range_config: Optional[List[TimeRangeConfig]] = Field(description="周时间执行配置", default=[])
    market_status_config: Optional[List[MarketStatusConfig]] = Field(description="市场状态执行配置", default=[])
    suggest_config: Optional[List[Any]] = Field(description="建议执行时间配置")
    description: str = Field(description="前端用于描述时间配置的文案")

    def is_match(self) -> bool:  # 判断当前时间是否匹配
        # 建议执行时间配置不纳入强制检查
        all_configs = [*self.time_range_config, *self.market_status_config]
        if not all_configs:  # 如果没有配置，判断为匹配
            return True
        return any([x.is_match() for x in all_configs])
