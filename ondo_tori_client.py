import warnings
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import click
import requests
from dateutil import tz
from loguru import logger
from pydantic import BaseModel, Field, BaseSettings, confloat


# おんどとり API アクセス例
#  https://ondotori.webstorage.jp/docs/api/reference/devices_device.html

def to_hyphen(key: str):
    """おんどとりアクセス時にポストで送信する際に利用する AccessInfo クラス:\n
    json キーをアンダースコアからハイフンに"""
    # Suppress the warning from pydantic, which is actually intentional to use alias for serialization.
    warnings.simplefilter('ignore')
    return key.replace('_', '-')


def to_jst(dt: datetime) -> datetime:
    jst_tz = tz.gettz('Asia/Tokyo')
    return dt.astimezone(jst_tz)


class AccessInfo(BaseSettings):
    api_key: str = Field(...)
    login_id: str = Field(...)
    login_pass: str = Field(...)
    remote_serial: Optional[List[str]] = Field(defaylt=None)
    base_serial: Optional[List[str]] = Field(default=None)

    class Config:
        """
        Put '.env' file to this file's directory.
            An example of .env file
                ONDOTORI_API_KEY='my-api-key'
                ONDOTORI_LOGIN_ID='my-id'
                ONDOTORI_LOGIN_PASS='my-password'
        """
        env_prefix = 'ondotori_'
        env_file = Path(__file__).resolve().parent / '.env'
        alias_generator = to_hyphen


class SensorUnit(str, Enum):
    """センサーの値の単位"""
    temperature = 'C'
    humidity = '%'

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def is_temperature(self) -> bool:
        """
        >>> SensorUnit('C').is_temperature()
        True
        """
        return self.value == self.temperature

    def is_humidity(self) -> bool:
        """
        >>> SensorUnit('%').is_humidity()
        True
        """

        return self.value == self.humidity


class ChannelContent(BaseModel):
    num: int
    name: Optional[str]
    value: Union[float, str]
    unit: SensorUnit

    def is_value_ok(self) -> bool:
        return type(self.value) == float

    def temperature(self) -> Union[float, None]:
        if self.is_value_ok() and self.unit.is_temperature():
            return self.value
        return

    def humidity(self) -> Union[confloat(ge=0.0, le=100.0), None]:
        """
        0 ~ 100 %
        """
        if self.is_value_ok() and self.unit.is_humidity():
            return self.value
        return


class BaseUnitContent(BaseModel):
    serial: str
    model: str
    name: Optional[str]


class GroupContent(BaseModel):
    num: int
    name: str


class DeviceContent(BaseModel):
    num: int
    serial: str
    model: str
    name: str
    battery: int
    rssi: Optional[str]
    time_diff: int
    std_bias: int
    dst_bias: int
    unixtime: datetime
    channel: List[ChannelContent]
    baseunit: BaseUnitContent
    group: GroupContent

    @property
    def temperature(self) -> Union[float, None]:
        for ch in self.channel:
            t = ch.temperature()
            if t is not None:
                return t

    @property
    def humidity(self) -> Union[confloat(ge=0.0, le=100.0), None]:
        for ch in self.channel:
            h = ch.humidity()
            if h is not None:
                return h

    @property
    def jst_datetime(self) -> datetime:
        return to_jst(self.unixtime)

    @property
    def time_diff(self) -> timedelta:
        now = to_jst(datetime.now())
        return now - self.jst_datetime

    def is_data_update_ok(self, before_seconds_thresh: int = 120) -> bool:
        """

        :param before_seconds_thresh: 最新のセンサーデータ取得時刻が
        現在と比較してこの時間差分以下だと False
        :return: bool
        """
        before_seconds_thresh = timedelta(seconds=before_seconds_thresh)
        return self.time_diff < before_seconds_thresh

    def is_battery_low(self):
        """バッテリーの値が1だと sensorのアップロードがストップする
        """
        return self.battery == 1


class OndotoriResponse(BaseModel):
    devices: List[DeviceContent]


def get_current_sensor_data(access_info: AccessInfo) -> Union[OndotoriResponse, None]:
    response = requests.post(url='https://api.webstorage.jp/v1/devices/current',
                             data=access_info.json(by_alias=True),
                             headers={'Content-Type': 'application/json',
                                      'X-HTTP-Method-Override': 'GET'})
    if response.ok:
        result = OndotoriResponse.parse_obj(response.json())
        return result
    else:
        logger.error(f'Error: status_code: {response.status_code}')
        return


if __name__ == '__main__':
    from devtools import debug

    info = AccessInfo()
    res = get_current_sensor_data(info)
    debug(res)
    print(f'{40 * "+"}')
    for device in res.devices:
        if device.is_data_update_ok(before_seconds_thresh=120):
            jst_time = device.jst_datetime
            humidity = device.humidity
            temperature = device.temperature
            debug(jst_time, humidity, temperature, device.battery, device.serial)
            print(f'{40 * "+"}')
