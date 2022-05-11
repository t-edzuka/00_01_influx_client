# InfluxDB pythonからデータを投げる例


## InfluxDB のデータ構造について覚えておくべきこと


### 用語

2022年5月現在:[用語集(Version2.2)](https://docs.influxdata.com/influxdb/v2.2/reference/glossary/)(古いバージョンと用語に違いあるので注意)
混乱したら用語集参照するとよい.

#### データの要素 (わからなくなったら[公式](https://docs.influxdata.com/influxdb/v2.2/reference/key-concepts/data-elements)を参照)
1. **Bucket**: RDBの``Database``に相当するが``Database``に加えて,いつまでデータを保持するかという``Retention period``という情報を設定できる. 
非常に大量のデータが入ってくるときは特定の期間の平均などの代表値のみを残して生データは捨ててしまうといったような使い方がディスク容量を削減し、可視化しやすくなるので、実世界での用途に向いている.  
用語としての注意点としてInfluxDB 1.xだと``Database``とよばれていて, 古いバージョンのClientライブラリAPIもDatabaseという語で書かれているので,古いネット記事を読むときに混乱の原因になる。
2. **Measurement**: RDBの``Table``に相当する. ``Measurement``は複数の``Point``で構成される.
3. **Series**: RDBに相当するような表現がないが, 強いていうならGroupby されたデータの集まりのようなイメージだろうか? 
4. **Point**: 一時点の観察データを表す. RDBの``Row (行)``に相当する.``Point``は ``Timestamp``, ``Field``と(``Tag (オプショナル)``)で構成される.
5. **Field**: columnに相当する. 着目するデータの値そのものが来る. 例えばセンサー値, 座標値, 画像特徴量など.
