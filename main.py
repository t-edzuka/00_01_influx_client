import random
import time
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.bucket_api import BucketsApi
from influxdb_client.domain.bucket import Bucket
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from influxdb_client.client.write_api import PointSettings
from config import URL, TOKEN, ORG, BUCKET_NAME
from pydantic import BaseModel, Field
from dateutil import tz


class PersonDetection(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    person_count: int = Field(default_factory=lambda: random.randint(1, 10))
    x: float = Field(default_factory=random.random)
    y: float = Field(default_factory=random.random)
    sensor_id: str = 'camera1'


def main():
    def gen_data():
        return PersonDetection()

    data = gen_data()

    with InfluxDBClient(url=URL, org=ORG, token=TOKEN,
                        debug=True) as client:
        writer = client.write_api(SYNCHRONOUS)
        writer.write(bucket=BUCKET_NAME,
                     record=(Point(measurement_name='person_detection')
                             .time(time=datetime.now(tz=tz.gettz('Asia/Tokyo')))
                             .field('x', data.x)
                             .field('y', data.y)
                             .field('person_count', data.person_count)
                             .tag('sensor_id', data.sensor_id)
                             ))
        time.sleep(1)


if __name__ == '__main__':
    while True:
        main()
