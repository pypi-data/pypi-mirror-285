# -*- coding: utf-8 -*-

"""
@Description: 
@Author: cat
@Date: 2024-07-16 21:27:11
@LastEditTime: 2024-07-16 22:41:10
@LastEditors: cat
"""
import threading
import time
from datetime import datetime, timezone
from uidgenerator.constants import Constants
from uidgenerator.datacenterworkid import (
    DataCenterWorkId as TypeDataCenterWorkId,
)
from typing import Union


class USnowflake:
    def __init__(self, dcw_id: TypeDataCenterWorkId, sequence: int = 0):
        self._sequence = sequence
        self._last_time_stamp = -1
        self.DataCenterWorkId = dcw_id
        self._lock = threading.Lock()

    _local_id_worker: Union["USnowflake", None] = None

    @staticmethod
    def Default() -> "USnowflake":
        if (
            not hasattr(USnowflake, "_local_id_worker")
            or USnowflake._local_id_worker is None
        ):
            USnowflake._local_id_worker = USnowflake(
                TypeDataCenterWorkId.GenLocalDataCenterWorkId()
            )
        return USnowflake._local_id_worker

    @property
    def DataCenterWorkId(self) -> TypeDataCenterWorkId:
        return self._data_center_work_id

    @DataCenterWorkId.setter
    def DataCenterWorkId(self, value: TypeDataCenterWorkId):
        self._data_center_work_id = value

    @property
    def SymDataCenterWorkId(self) -> TypeDataCenterWorkId:
        return self._sym_data_center_work_id

    @SymDataCenterWorkId.setter
    def SymDataCenterWorkId(self, value: TypeDataCenterWorkId):
        self._sym_data_center_work_id = value

    @property
    def Sequence(self) -> int:
        return self._sequence

    @Sequence.setter
    def Sequence(self, value: int):
        self._sequence = value

    def NextId(self) -> int:
        with self._lock:
            cur_time_stamp = self.TimeGen()
            if cur_time_stamp < self._last_time_stamp:
                if self._last_time_stamp - cur_time_stamp < Constants.MAX_BACKWARD_MS:
                    time.sleep((self._last_time_stamp - cur_time_stamp) / 1000.0)
                else:
                    if self.SymDataCenterWorkId is not None:
                        if (
                            self.SymDataCenterWorkId.ClockCallback
                            > self._last_time_stamp
                        ):
                            tmp0 = self.DataCenterWorkId
                            self.SymDataCenterWorkId.IsClockCallback = False
                            self.DataCenterWorkId = self.SymDataCenterWorkId
                            tmp0.IsClockCallback = True
                            tmp0.ClockCallback = self._last_time_stamp
                            self.SymDataCenterWorkId = tmp0
                        else:
                            raise InvalidSystemClock(
                                self._last_time_stamp,
                                cur_time_stamp,
                                f"Clock moved backwards. Refusing to generate id for {self._last_time_stamp - cur_time_stamp} milliseconds",
                            )
                    else:
                        tmp = self.DataCenterWorkId
                        sym_tmp = tmp.GetSymmetrical()
                        sym_tmp.IsClockCallback = False
                        self.DataCenterWorkId = sym_tmp
                        tmp.IsClockCallback = True
                        tmp.ClockCallback = self._last_time_stamp
                        self.SymDataCenterWorkId = tmp

            if self._last_time_stamp == cur_time_stamp:
                self._sequence = (self._sequence + 1) & Constants.SequenceMask
                if self._sequence == 0:
                    cur_time_stamp = self.TilNextMilliSecond(self._last_time_stamp)
            else:
                self._sequence = 0

            self._last_time_stamp = cur_time_stamp
            id2 = (
                (
                    (cur_time_stamp - Constants.TwePoch)
                    << Constants.TimeStampLeftShiftLeftShift
                )
                | (
                    self.DataCenterWorkId.DataCenterId
                    << Constants.MaxDataCenterIdIdShift
                )
                | (self.DataCenterWorkId.WorkId << Constants.WorkerIdShift)
                | self._sequence
            )
            return id2

    def TilNextMilliSecond(self, last_last_time_stamp: int) -> int:
        time_stamp = self.TimeGen()
        while time_stamp <= last_last_time_stamp:
            time_stamp = self.TimeGen()
        return time_stamp

    def TimeGen(self) -> int:
        # 获取当前时间（UTC）
        now_utc = datetime.now(timezone.utc)
        # 定义1970年1月1日的UTC时间点
        Jan1st1970 = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        # 计算两个时间点之间的差值并转换为毫秒
        delta = now_utc - Jan1st1970
        total_milliseconds = int(delta.total_seconds() * 1000)
        return total_milliseconds


class InvalidSystemClock(Exception):
    def __init__(self, last_time_stamp: int, cur_time_stamp: int, message: str):
        super().__init__(message)
        self.last_time_stamp = last_time_stamp
        self.cur_time_stamp = cur_time_stamp
