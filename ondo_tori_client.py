from datetime import datetime
from typing import List, Optional, Union

import requests
from loguru import logger
from pydantic import BaseModel, Field


# おんどとり API アクセス例
#  https://ondotori.webstorage.jp/docs/api/reference/devices_device.html

def to_hyphen(key: str):
    return key.replace('_', '-')


class AccessInfo(BaseModel):
    api_key: str = Field(...)
    login_id: str = Field(...)
    login_pass: str = Field(...)
    remote_serial: Optional[List[str]] = Field(default=["521475F4"])
    base_serial: Optional[List[str]] = Field(default=None)

    class Config:
        alias_generator = to_hyphen


class ChannelContent(BaseModel):
    num: int
    name: Optional[str]
    value: Union[float, str]
    unit: str


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
    battery: str
    rssi: Optional[str]
    time_diff: str
    std_bias: str
    dst_bias: str
    unixtime: datetime
    channel: List[ChannelContent]
    baseunit: BaseUnitContent
    group: GroupContent


class OndotoriResponse(BaseModel):
    devices: List[DeviceContent]


def get_current_sensor_data(access_info: AccessInfo):
    response = requests.post(url='https://api.webstorage.jp/v1/devices/current',
                             data=access_info.json(by_alias=True),
                             headers={'Content-Type': 'application/json',
                                      'X-HTTP-Method-Override': 'GET'})
    if response.ok:
        logger.debug('Success post login data')
        logger.debug(f'Data: {OndotoriResponse.parse_obj(response.json())}')
        logger.debug(f'Response Header: {response.headers}')
    else:
        logger.debug(f'Error: status_code: {response.status_code}')


if __name__ == '__main__':
    info = AccessInfo(api_key="xxx", login_id="yyy", login_pass="password")
    get_current_sensor_data(info)
