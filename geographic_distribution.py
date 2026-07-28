import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text

def main():
    # 1. 配置文件路径（通过命令行参数传入，隐藏本地路径）
    parser = argparse.ArgumentParser(description="Plot sample distribution on a world map with spatial aggregation.")
    parser.add_argument("-i", "--input", required=True, help="Input Excel file containing samples data")
    parser.add_argument("-s", "--shapefile", required=True, help="Path to world shapefile (e.g., ne_10m_admin_0_countries.shp)")
    parser.add_argument("-o", "--output", default="final_labeled_map.png", help="Output image file name")
    
    args = parser.parse_args()

    # 2. 读取数据并统一列名
    df = pd.read_excel(args.input)
    df.columns = df.columns.str.strip()

    # 3. 数据聚合：加大空间聚合力度
    # 设置网格大小（单位：度）。3度大约相当于 300 公里范围。
    # 如果运行后觉得北美依然拥挤，可以把 3.0 改为 4.0 或 5.0
    grid_size = 3.0
    df['Lon_approx'] = (df['Longitude'] / grid_size).round() * grid_size
    df['Lat_approx'] = (df['Latitude'] / grid_size).round() * grid_size

    # 按近似经纬度进行分组，合并相近位置的文本
    grouped = df.groupby(['Lon_approx', 'Lat_approx', 'Phylum']).agg({
        'Longitude': 'mean', # 聚合后，使用该区域点的真实物理中心作为绘图坐标
        'Latitude': 'mean',
        'Protein': lambda x: '\n'.join(sorted(set(x.astype(str)))),  # 去重并排序后拼接
        'Genome_Accession': 'count'  # 统计该合并区域的样本总数
    }).reset_index()
    grouped.rename(columns={'Genome_Accession': 'Count'}, inplace=True)

    # 颜色分类映射
    unique_phyla = grouped['Phylum'].unique()
    colors = plt.cm.tab10.colors[:len(unique_phyla)]
    phylum_color_map = dict(zip(unique_phyla, colors))

    # 4. 加载底图
    world = gpd.read_file(args.shapefile)

    # 5. 绘图
    fig, ax = plt.subplots(figsize=(16, 9))
    world.plot(ax=ax, color='lightgrey', edgecolor='white', linewidth=0.5)

    # 6. 绘制圆点与标注
    texts = []
    for _, row in grouped.iterrows():
        p_color = phylum_color_map[row['Phylum']]

        # 绘制点：统一大小 s=40
        ax.scatter(row['Longitude'], row['Latitude'],
                   color=p_color, s=40,
                   zorder=5, alpha=0.8, edgecolors='white')

        # 标签标注：显示去重后的 Protein ID + 物种 + 样本总数
        label_text = f"{row['Protein']}\n{row['Phylum']} (n={row['Count']})"

        # 缩小字体和文本框内边距，减少占用空间
        t = ax.text(row['Longitude'], row['Latitude'], label_text,
                    fontsize=6, color='black', ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec=p_color, lw=0.8, alpha=0.9))
        texts.append(t)

    # 7. 自动避让
    # 增强文本之间的排斥力，增加迭代次数以彻底解开重叠死结
    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.8, alpha=0.8),
                force_points=0.2,         # 降低文本对点的排斥，允许框离点稍微近一点
                force_text=3.0,           # 极大增强文本框之间的排斥力
                expand_points=(1.5, 1.5),
                expand_text=(1.5, 1.5),
                max_iterations=4000)      # 增加迭代次数

    # 8. 保存
    # 如需添加图表标题，请记得保持标题中物种名斜体加粗的要求
    plt.title('', fontsize=20, fontweight='bold')
    ax.set_axis_off()
    plt.savefig(args.output, dpi=300, bbox_inches='tight')
    print(f"去重及空间聚合后的地图已成功保存为: {args.output}")

if __name__ == "__main__":
    main()