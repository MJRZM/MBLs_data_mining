import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap
from scipy.cluster.hierarchy import linkage

file_fc = 'fc_mean.xlsx'
file_p = 'p_values.xlsx'

if not os.path.exists(file_fc) or not os.path.exists(file_p):
    print(f"Error: files not found. Please ensure {file_fc} and {file_p} are in the current directory.")
else:
    df_fc = pd.read_excel(file_fc, index_col=0, engine='openpyxl').apply(pd.to_numeric, errors='coerce').fillna(1)
    df_p = pd.read_excel(file_p, index_col=0, engine='openpyxl').apply(pd.to_numeric, errors='coerce').fillna(1)

    df_fc = df_fc.T
    df_p = df_p.T

    df_annot = pd.DataFrame('', index=df_fc.index, columns=df_fc.columns)
    for col in df_fc.columns:
        for idx in df_fc.index:
            val = df_fc.loc[idx, col]
            pval = df_p.loc[idx, col]

            val_rounded = round(val, 1)
            val_str = f"{val_rounded:g}"

            if pval < 0.01:
                df_annot.loc[idx, col] = val_str + "\n**"
            elif pval < 0.05:
                df_annot.loc[idx, col] = val_str + "\n*"
            else:
                df_annot.loc[idx, col] = val_str

    df_log = np.log2(df_fc.replace(0, np.nan).fillna(1))
    row_link = linkage(df_log.values, method='ward')
    col_link = linkage(df_log.values.T, method='ward')

    df_color_plot = df_log.copy()

    mask_not_sig_or_down = (df_p >= 0.05) | (df_fc <= 1)
    df_color_plot[mask_not_sig_or_down] = -1

    plt.rcParams['font.sans-serif'] = ['Arial']
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'

    colors_gradient = [(1, 1, 1, 0), '#FFF0E6', '#FFDAB9', '#FC8D59', '#D73027', '#7F0000']
    cmap_custom = LinearSegmentedColormap.from_list("CustomGradient", colors_gradient)

    g = sns.clustermap(
        df_color_plot,
        row_linkage=row_link,
        col_linkage=col_link,
        cmap=cmap_custom,
        vmin=-1, vmax=4,
        figsize=(40, 20),
        linewidths=2.5,
        linecolor='black',
        dendrogram_ratio=(0.08, 0.1),
        annot=df_annot,
        fmt='',
        annot_kws={"size": 22, "weight": "bold", "linespacing": 1.6},
        cbar=False,
        tree_kws=dict(linewidths=5, colors='black')
    )

    g.ax_cbar.set_visible(False)
    g.ax_row_dendrogram.set_axis_off()
    g.ax_col_dendrogram.set_axis_off()

    for text in g.ax_heatmap.texts:
        t = text.get_text()
        num_str = t.replace('*', '').replace('\n', '')
        try:
            val_float = float(num_str)
            if val_float >= 8 and '*' in t:
                text.set_color('white')
            else:
                text.set_color('black')
        except ValueError:
            text.set_color('black')

    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=90, fontsize=36, fontweight='bold')
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=36, fontweight='bold')

    for _, spine in g.ax_heatmap.spines.items():
        spine.set_visible(True)
        spine.set_linewidth(6)

    g.savefig('heatmap_output.tif', dpi=500, format='tif',
              bbox_inches='tight', transparent=True, pil_kwargs={"compression": "tiff_lzw"})

    print("High-resolution heatmap generated successfully.")
    print("Applied features: transparent background, continuous gradient, 1 decimal place, significance markers with line break.")
    print("Output file: heatmap_output.tif")

    plt.show()