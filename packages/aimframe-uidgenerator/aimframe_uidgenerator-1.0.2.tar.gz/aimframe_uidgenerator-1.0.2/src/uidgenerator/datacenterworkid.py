# -*- coding: utf-8 -*-

"""
@Description: 
@Author: cat
@Date: 2024-07-16 19:50:34
@LastEditTime: 2024-07-16 21:44:20
@LastEditors: cat
"""
from . import Constants
import math
from ipaddress import ip_address
import socket


class DataCenterWorkId:
    def __init__(self, dcw_id: int, data_center_id_bits: int):
        if dcw_id <= 0 or dcw_id >= 2**Constants.MaxDataCenterWorkIdBits:
            raise ValueError(
                f"snowflake id must have {Constants.MaxDataCenterWorkIdBits} bits of DataCenterWorkId !"
            )
        if (
            data_center_id_bits < 0
            or data_center_id_bits >= Constants.MaxDataCenterWorkIdBits
        ):
            raise ValueError(
                f"snowflake dataCenterIdBits must  >0 and <{Constants.MaxDataCenterWorkIdBits} !"
            )

        self._dcwId = dcw_id
        self._dataCenterIdBits = data_center_id_bits
        dcw_str = f"{dcw_id:b}".zfill(Constants.MaxDataCenterWorkIdBits)
        self.DataCenterId = int(dcw_str[:data_center_id_bits], 2)
        self.WorkId = int(dcw_str[data_center_id_bits:], 2)

        self.IsClockCallback = False
        self.ClockCallback: int = 0

    def GetSymmetrical(self):
        center_digit = 2 ** (Constants.MaxDataCenterWorkIdBits - 1)
        sym_dcw_id = (
            self._dcwId - center_digit
            if self._dcwId >= center_digit
            else self._dcwId + center_digit
        )
        return DataCenterWorkId(sym_dcw_id, self._dataCenterIdBits)

    @staticmethod
    def GenLocalDataCenterWorkId():
        try:
            hostname = socket.gethostname()
            ip = ip_address(socket.gethostbyname(hostname))
            packed = ip.packed  # 获取IP地址的包含格式
            ipbytes = [int(x) for x in packed]  # 将包含格式转换为整数列表
            ipbyteslen = len(ipbytes)
            dcwid = 0
            if ipbyteslen == 4:
                for ip0 in ipbytes:
                    dcwid += ip0 & 0xFF
            elif ipbyteslen == 16:
                for ip0 in ipbytes:
                    dcwid += ip0 & 0b111111
            else:
                print("Bad LocalHost InternetAddress, please check your network!")
                raise ValueError(
                    "Bad LocalHost InternetAddress, please check your network!"
                )

            return DataCenterWorkId(dcwid, Constants.DataCenterIdBits)
        except Exception as e:
            raise ValueError(
                "Error getting local IP or initializing DataCenterWorkId!"
            ) from e
