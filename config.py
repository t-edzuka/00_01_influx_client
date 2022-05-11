from pathlib import Path
import os
from dotenv import load_dotenv

"""
このファイルと同階層ディレクトリにある'.env' ファイルを読み込んで, InfluxDBの設定を読みだす.
"""

env_path = Path(__file__).parent.joinpath('.env')
load_dotenv(env_path)

URL = os.getenv('INFLUXDB_V2_URL')
ORG = os.getenv('INFLUXDB_V2_ORG')
TOKEN = os.getenv('INFLUXDB_V2_TOKEN')

