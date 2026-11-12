# coding=utf-8
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import warnings

warnings.filterwarnings("ignore")


def main():
    # 1. 构造采样点假数据 (samples.xlsx)
    data = {
        'Longitude': [-81.0, 38.0, 105.0, 153.0, -119.0],
        'Latitude': [18.0, 21.0, 60.0, -27.0, 34.0],
        'Protein': ['Bla_MBL_1', 'Bla_MBL_2', 'Bla_MBL_3', 'Bla_MBL_4', 'Bla_MBL_5'],
        'Genome_Accession': ['GCA_001', 'GCA_002', 'GCA_003', 'GCA_004', 'GCA_005'],
        'Phylum': ['Proteobacteria', 'Firmicutes', 'Bacteroidota', 'Actinobacteriota', 'Proteobacteria']
    }
    df = pd.DataFrame(data)
    df.to_excel('samples.xlsx', index=False, engine='openpyxl')

    # 2. 构造底图假数据 (ne_10m_admin_0_countries.shp)
    # 用多边形手绘几个代表性的“假大陆”边界，彻底绕过 GeoPandas 1.0 的下载限制
    p_namerica = Polygon([(-140, 10), (-50, 10), (-50, 70), (-140, 70)])  # 假北美洲
    p_eurasia = Polygon([(-10, 10), (160, 10), (160, 70), (-10, 70)])  # 假亚欧大陆
    p_oceania = Polygon([(110, -50), (180, -50), (180, 0), (110, 0)])  # 假大洋洲

    world = gpd.GeoDataFrame({'geometry': [p_namerica, p_eurasia, p_oceania]}, crs="EPSG:4326")

    # 导出为你代码里写死的高精度 shapefile 文件名
    world.to_file('ne_10m_admin_0_countries.shp')

    print("✅ 地图测试数据生成完毕！包含 samples.xlsx 和 纯手工构建的假 shapefile 组。")


if __name__ == "__main__":
    main()