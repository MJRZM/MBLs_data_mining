import argparse
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

def main():
    # 使用 argparse 设置命令行参数，隐去具体的项目文件名
    parser = argparse.ArgumentParser(description="Generate a high-resolution clustered heatmap with dynamic text colors.")
    parser.add_argument("-i", "--input", required=True, help="Input Excel file (e.g., MIC data)")
    parser.add_argument("-oh", "--out_heatmap", default="Heatmap_GiantFont_Clean.tif", help="Output file for the main heatmap")
    parser.add_argument("-oc", "--out_colorbar", default="Colorbar_GiantFont_Clean.tif", help="Output file for the independent colorbar")
    
    args = parser.parse_args()

    # 1. 数据加载与预处理
    file_path = args.input
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return
        
    df = pd.read_excel(file_path, index_col=0, engine='openpyxl')
    df = df.apply(pd.to_numeric, errors='coerce').fillna(1)

    # 转置矩阵
    df_raw = df.T
    df_log = np.log2(df_raw)

    # 全局字体加粗
    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'

    # --- 第一部分：超大字号热图 (彻底拆分版) ---
    g = sns.clustermap(
        df_log,
        method='ward',
        cmap="RdBu_r",
        center=0,
        vmin=-4, vmax=4,
        figsize=(40, 20),
        linewidths=2.5,
        linecolor='black',
        dendrogram_ratio=(0.08, 0.1),
        annot=df_raw.values,
        fmt='g',
        # 💡【核心修改 1】这里暂时给一个基础字号设置，颜色会在下方被动态覆盖
        annot_kws={"size": 24, "weight": "bold"},
        cbar=False,
        tree_kws=dict(linewidths=5, colors='black')
    )

    # 彻底清理背景 and 残影
    g.ax_cbar.set_visible(False)
    g.ax_row_dendrogram.set_axis_off()
    g.ax_col_dendrogram.set_axis_off()

    # 💡【核心修改 2】遍历热图中的每一个文本标签，根据 log2 值动态调整颜色
    # 当背景极深（绝对值大于 2.5）时文字变白，否则保持黑色
    for text in g.ax_heatmap.texts:
        # 获取当前格子在 df_log 中对应的数值
        val = float(text.get_text())
        # 因为 text 标签显示的是原始倍数（如 128），我们需要计算它的 log2 值来对应颜色深浅
        if val > 0:
            log_val = np.log2(val)
            if abs(log_val) > 2.5:
                text.set_color('white')
            else:
                text.set_color('black')
        else:
            text.set_color('black')

    # 横纵坐标字号设置
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=90, fontsize=36, fontweight='bold')
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=36, fontweight='bold')

    # 热图外框极度强化
    for _, spine in g.ax_heatmap.spines.items():
        spine.set_visible(True)
        spine.set_linewidth(6)

    # 保存主图
    g.savefig(args.out_heatmap, dpi=500, format='tif',
              bbox_inches='tight', pil_kwargs={"compression": "tiff_lzw"})

    # --- 第二部分：独立图注 ---
    fig_cbar, ax_cbar_new = plt.subplots(figsize=(2, 8))
    norm = Normalize(vmin=-4, vmax=4)
    sm = ScalarMappable(cmap="RdBu_r", norm=norm)
    sm.set_array([])

    cb = fig_cbar.colorbar(sm, cax=ax_cbar_new, orientation='vertical')
    cb.ax.tick_params(labelsize=28, width=5)
    for label in cb.ax.get_yticklabels():
        label.set_fontweight('bold')

    ax_cbar_new.set_ylabel('log2(Fold Change)', fontsize=30, fontweight='bold', labelpad=20)

    # 保存图注
    fig_cbar.savefig(args.out_colorbar, dpi=500, format='tif',
                     bbox_inches='tight', pil_kwargs={"compression": "tiff_lzw"})

    print("✅ 完美的巨幕级高分辨率图片已生成！")
    print(f"主图：{args.out_heatmap} (深色格子字体已自动切换为白色)")
    print(f"图注：{args.out_colorbar}")

    # 如果在纯无界面的服务器环境中运行，可以注释掉下面这行
    plt.show()

if __name__ == "__main__":
    main()