# InfluxDB pythonからデータを投げる例


## InfluxDB のデータ構造について覚えておくべきこと


### 用語

2022年5月現在:[用語集(Version2.2)](https://docs.influxdata.com/influxdb/v2.2/reference/glossary/)(古いバージョンと用語に違いあるので注意)
混乱したら用語集参照するとよい.

#### データの要素とそのコンセプト(わからなくなったら[公式](https://docs.influxdata.com/influxdb/v2.2/reference/key-concepts/data-elements)を参照)
1. **Bucket**: RDBの``Database``に相当するが``Database``に加えて,いつまでデータを保持するかという``Retention period``という情報を設定できる. 
時系列データは非常に大量のデータが大量に入ってくるので、ディスクがすぐにいっぱいになってしまう. 実用上はその大量のデータを人間に理解しやすいように要約した形にして利用することが多い.  
たとえば1秒ごとにセンサーから送られてくる気温データがあったとしよう。そして利用者は今月の気温の推移がどうだったかということが知りたいとする。
おそらくその人は1秒ごとの細かい値はどうでもよいだろう。知りたいのは一日ごとの平均、最小、最大などといった代表値のはずである。そこでたとえば3日だけ生データを保持してそのあとは統計要約データだけ残して,捨ててしまおうとなるのではないだろうか.  
なお用語としての注意点すべき点は、InfluxDB 1.xだと``Database``とよばれていて, 古いバージョンのClientライブラリAPIもDatabaseという語で書かれている。そのため古いネット記事を読むときに ``Database`` -> ``Bucket``と適せん読み替えて補う必要がある。
2. **Measurement**: RDBの``Table``に相当する. ``Measurement``は複数の``Point``で構成される.
3. **Series**: RDBに相当するような表現がないが, 強いていうならGroupby されたデータの集まりのようなイメージだろうか?　グループに相当するものが, ``Series Key`` データの値そのものを ``Series``
4. **Point**: 一時点の観察データを表す. RDBの``Row (行)``に相当する.``Point``は ``Timestamp``, ``Field``と(``Tag (オプショナル)``)で構成される.
5. **Field**: columnに相当する. Column 名に相当するものを Field Keyと呼ぶ。着目するデータの値そのもの. 例えばセンサー値, 座標値, 画像特徴量など. Field Keyが``temperature``だとしたら, 値は`25.5`, `18.8`といった要領.
6. **Tag**: Indexつきcolumnに相当する. Column名に相当するものをTag keyと呼ぶ。 人間が検索したいと考えるようような値を格納する. 検索の高速化が期待できる. Group byしたいようなものと言ったらよいか. Tag Keyが``house_name`` だとしたら Tagの値は``oyama-4``, ``okatsu``といった要領.
逆にUUIDやら, 実数値など人間が検索しようと思わない値を入れてしまうとパフォーマンス低下につながる.

### Python Client APIを使う場合
以下のような要領で書き込める.
```python
import random
import time
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import URL, TOKEN, ORG
from pydantic import BaseModel, Field


class PersonDetection(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    person_count: int = Field(default_factory=lambda: random.randint(1, 10))
    x: float = Field(default_factory=random.random)
    y: float = Field(default_factory=random.random)
    house_name: str = 'oyama-4'
    camera_id: str = 'camera1'


def write_data():
    def gen_data():
        return PersonDetection()

    data = gen_data()

    with InfluxDBClient(url=URL, org=ORG, token=TOKEN,
                        debug=True) as client:
        writer = client.write_api(SYNCHRONOUS)
        writer.write(bucket='house4',
                     record=(Point(measurement_name='person_detection')
                             .field('x', data.x)
                             .field('y', data.y)
                             .field('person_count', data.person_count)
                             .tag('house_name', data.house_name)
                             .tag('camera_id', data.camera_id)
                             ))
if __name__ == '__main__':
    while True:
        write_data()
        time.sleep(1)
```

