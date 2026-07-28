import os
import argparse
import pandas as pd
import numpy as np
from Bio import SeqIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
import matplotlib
matplotlib.use('Agg') # 避免服务器环境下绘图界面的报错
import matplotlib.pyplot as plt

# ==========================================
# 0. 强制限制底层数学计算库的最大线程数 (防止段错误崩溃)
# ==========================================
os.environ["OMP_NUM_THREADS"] = "10"
os.environ["OPENBLAS_NUM_THREADS"] = "10"
os.environ["MKL_NUM_THREADS"] = "10"
os.environ["VECLIB_MAXIMUM_THREADS"] = "10"
os.environ["NUMEXPR_NUM_THREADS"] = "10"


# ==========================================
# 1. 核心读取函数
# ==========================================
def load_ids(p):
    try:
        with open(p, 'r') as f:
            return set(line.strip().split()[0] for line in f if line.strip())
    except FileNotFoundError:
        print(f"警告: 未找到文件 {p}，视为空集合。")
        return set()


def main():
    # ==========================================
    # 2. 命令行参数配置 (隐藏私有项目文件名)
    # ==========================================
    parser = argparse.ArgumentParser(description="Sequence extraction, t-SNE reduction, DBSCAN clustering and visualization.")
    parser.add_argument("-f", "--fasta", required=True, help="Input FASTA file")
    parser.add_argument("-k", "--known_ids", required=True, help="File containing known clusters IDs")
    parser.add_argument("-cne", "--candidate_non_elevated", required=True, help="File for Candidate (Non-elevated phenotype) IDs")
    parser.add_argument("-ce", "--candidate_elevated", required=True, help="File for Candidate (Elevated phenotype) IDs")
    parser.add_argument("-e", "--embedding_csv", default="tsne_dbscan_results.csv", help="Output/Input CSV for embedding coordinates")
    parser.add_argument("-o", "--output_plot", default="Ultimate_Clustering_Map.png", help="Output visualization image file")
    
    args = parser.parse_args()

    known_ids = load_ids(args.known_ids)
    blue_40_ids = load_ids(args.candidate_non_elevated)
    darkblue_13_ids = load_ids(args.candidate_elevated)

    def get_highlight_label(seq_id):
        if seq_id in darkblue_13_ids:
            return "Candidate (Elevated phenotype)"
        elif seq_id in blue_40_ids:
            return "Candidate (Non-elevated phenotype)"
        elif seq_id in known_ids:
            return "Known clusters"
        else:
            return "Background"

    # ==========================================
    # 3. 特征提取、降维与聚类计算
    # ==========================================
    if os.path.exists(args.embedding_csv):
        print(f">>> 发现已存在的坐标文件 '{args.embedding_csv}'，加载数据并刷新标签...")
        df = pd.read_csv(args.embedding_csv)
        df['Highlight_Type'] = df['ID'].apply(get_highlight_label)
    else:
        print(f">>> 未发现 '{args.embedding_csv}'，开始重新计算降维与聚类...")
        sequences, highlight_labels, seq_ids = [], [], []

        for record in SeqIO.parse(args.fasta, "fasta"):
            seq = str(record.seq).upper().replace('X', '').replace('-', '')
            if len(seq) < 3: continue
            sequences.append(" ".join([seq[i:i + 3] for i in range(len(seq) - 2)]))
            highlight_labels.append(get_highlight_label(record.id))
            seq_ids.append(record.id)

        print(">>> 正在提取 K-mer 特征...")
        X = CountVectorizer(binary=True, min_df=5).fit_transform(sequences)

        print(">>> 正在进行 SVD 降维...")
        X_reduced = TruncatedSVD(n_components=50, random_state=42).fit_transform(X)

        print(">>> 正在进行 t-SNE 降维...")
        tsne = TSNE(n_components=2, perplexity=30, random_state=42, n_jobs=10, init='pca', learning_rate='auto')
        embedding = tsne.fit_transform(X_reduced)

        print(">>> 正在进行 DBSCAN 发现性聚类 (证明天然分簇)...")
        dbscan = DBSCAN(eps=4.0, min_samples=15, n_jobs=10)
        cluster_labels = dbscan.fit_predict(embedding)

        df = pd.DataFrame(embedding, columns=['Dim1', 'Dim2'])
        df['ID'] = seq_ids
        df['Highlight_Type'] = highlight_labels
        df['Cluster'] = cluster_labels
        df.to_csv(args.embedding_csv, index=False)
        print(f">>> 计算完成，数据已保存至 {args.embedding_csv}")

    # ==========================================
    # 4. 计算簇的虚拟中心点 (用于画连线和星星)
    # ==========================================
    unique_clusters = sorted(df['Cluster'].unique())
    valid_clusters = [c for c in unique_clusters if c != -1]
    n_clusters = len(valid_clusters)
    print(f">>> 聚类算法证明：这些蛋白可以天然分为 {n_clusters} 个簇 (排除了噪声点)。")

    centers = {}
    for c in valid_clusters:
        sub_df = df[df['Cluster'] == c]
        centers[c] = (sub_df['Dim1'].mean(), sub_df['Dim2'].mean())

    # ==========================================
    # 5. 生成融合两种逻辑的可视化图表 (全新视觉优化)
    # ==========================================
    print(">>> 开始绘图...")
    plt.figure(figsize=(16, 12), dpi=300)
    ax = plt.gca()

    # --- 图层 1: 簇中心连线 ---
    for _, row in df.iterrows():
        c = row['Cluster']
        if c == -1: continue

        cx, cy = centers[c]
        ax.plot([row['Dim1'], cx], [row['Dim2'], cy],
                color='#D3D3D3', alpha=0.08, linewidth=0.1, zorder=1)

    # --- 图层 2: 天然分簇背景散点 ---
    cmap = plt.get_cmap('tab20', max(1, n_clusters))
    cluster_colors = {}

    for i, c in enumerate(valid_clusters):
        r, g, b, a = cmap(i)
        # 如果这个颜色偏红 (R高，G和B低)
        if r > 0.7 and g < 0.4 and b < 0.4:
            cluster_colors[c] = 'gold'  # 替换为金色/黄色
        else:
            cluster_colors[c] = cmap(i)

    # 2.1 画未归类的噪声点 (浅灰色，极高透明度)
    noise_df = df[df['Cluster'] == -1]
    ax.scatter(noise_df['Dim1'], noise_df['Dim2'],
               c='#E0E0E0', s=10, alpha=0.2, edgecolors='none', zorder=2)

    # 2.2 画自然分簇点
    bg_df = df[df['Highlight_Type'] == 'Background']
    for c in valid_clusters:
        sub_df = bg_df[bg_df['Cluster'] == c]
        ax.scatter(sub_df['Dim1'], sub_df['Dim2'],
                   c=[cluster_colors[c]], s=15, alpha=0.25, edgecolors='none', zorder=3)

    # --- 图层 3: 虚拟簇中心 (恢复为红星) ---
    for i, c in enumerate(valid_clusters):
        cx, cy = centers[c]
        ax.scatter(cx, cy, c='red', marker='*', s=200, edgecolors='k', linewidths=1.0,
                   zorder=4, label='Cluster Center' if i == 0 else "")

    # --- 图层 4: 特定关注点高亮 ---
    highlight_colors = {
        "Known clusters": "#d62728",
        "Candidate (Non-elevated phenotype)": "#800080",
        "Candidate (Elevated phenotype)": "#00BFFF"
    }

    plot_order = [
        "Known clusters",
        "Candidate (Non-elevated phenotype)",
        "Candidate (Elevated phenotype)"
    ]

    for t in plot_order:
        sub_df = df[df['Highlight_Type'] == t]
        if sub_df.empty: continue

        ax.scatter(sub_df['Dim1'], sub_df['Dim2'],
                   c=highlight_colors[t], s=60, label=t,
                   alpha=1.0, zorder=10, edgecolors='black', linewidths=1.0)

    # --- 图表美化 ---
    ax.set_title("", fontsize=24, pad=20)
    ax.set_xlabel("t-SNE 1", fontsize=20)
    ax.set_ylabel("t-SNE 2", fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.grid(True, linestyle='--', color='lightgray', alpha=0.5)

    ax.legend(markerscale=1.5, fontsize=16, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)

    plt.tight_layout()
    plt.savefig(args.output_plot, bbox_inches='tight')
    print(f">>> 绘图完成！图片已保存为 {args.output_plot}")

if __name__ == "__main__":
    main()