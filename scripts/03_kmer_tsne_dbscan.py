import os

os.environ["OMP_NUM_THREADS"] = "10"
os.environ["OPENBLAS_NUM_THREADS"] = "10"
os.environ["MKL_NUM_THREADS"] = "10"
os.environ["VECLIB_MAXIMUM_THREADS"] = "10"
os.environ["NUMEXPR_NUM_THREADS"] = "10"

import pandas as pd
import numpy as np
from Bio import SeqIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FASTA_FILE = "input.fasta"
KNOWN_IDS_FILE = "known_ids.txt"
BLUE_40_FILE = "candidate_non_elevated_ids.txt"
DARKBLUE_13_FILE = "candidate_elevated_ids.txt"
EMBEDDING_FILE = "embedding_results.csv"
OUTPUT_PLOT = "clustering_map.png"


def load_ids(p):
    try:
        with open(p, 'r') as f:
            return set(line.strip().split()[0] for line in f if line.strip())
    except FileNotFoundError:
        print(f"Warning: file {p} not found, treating as empty set.")
        return set()


known_ids = load_ids(KNOWN_IDS_FILE)
blue_40_ids = load_ids(BLUE_40_FILE)
darkblue_13_ids = load_ids(DARKBLUE_13_FILE)


def get_highlight_label(seq_id):
    if seq_id in darkblue_13_ids:
        return "Candidate (Elevated phenotype)"
    elif seq_id in blue_40_ids:
        return "Candidate (Non-elevated phenotype)"
    elif seq_id in known_ids:
        return "Known clusters"
    else:
        return "Background"


if os.path.exists(EMBEDDING_FILE):
    print(f">>> Found existing coordinate file '{EMBEDDING_FILE}', loading data and refreshing labels...")
    df = pd.read_csv(EMBEDDING_FILE)
    df['Highlight_Type'] = df['ID'].apply(get_highlight_label)
else:
    print(f">>> '{EMBEDDING_FILE}' not found, recomputing dimensionality reduction and clustering...")
    sequences, highlight_labels, seq_ids = [], [], []

    for record in SeqIO.parse(FASTA_FILE, "fasta"):
        seq = str(record.seq).upper().replace('X', '').replace('-', '')
        if len(seq) < 3: continue
        sequences.append(" ".join([seq[i:i + 3] for i in range(len(seq) - 2)]))
        highlight_labels.append(get_highlight_label(record.id))
        seq_ids.append(record.id)

    print(">>> Extracting K-mer features...")
    X = CountVectorizer(binary=True, min_df=5).fit_transform(sequences)

    print(">>> Performing SVD dimensionality reduction...")
    X_reduced = TruncatedSVD(n_components=50, random_state=42).fit_transform(X)

    print(">>> Performing t-SNE dimensionality reduction...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42, n_jobs=10, init='pca', learning_rate='auto')
    embedding = tsne.fit_transform(X_reduced)

    print(">>> Performing DBSCAN clustering...")
    dbscan = DBSCAN(eps=4.0, min_samples=15, n_jobs=10)
    cluster_labels = dbscan.fit_predict(embedding)

    df = pd.DataFrame(embedding, columns=['Dim1', 'Dim2'])
    df['ID'] = seq_ids
    df['Highlight_Type'] = highlight_labels
    df['Cluster'] = cluster_labels
    df.to_csv(EMBEDDING_FILE, index=False)
    print(f">>> Computation complete, data saved to {EMBEDDING_FILE}")

unique_clusters = sorted(df['Cluster'].unique())
valid_clusters = [c for c in unique_clusters if c != -1]
n_clusters = len(valid_clusters)
print(f">>> Clustering result: these proteins naturally divide into {n_clusters} clusters (excluding noise points).")

centers = {}
for c in valid_clusters:
    sub_df = df[df['Cluster'] == c]
    centers[c] = (sub_df['Dim1'].mean(), sub_df['Dim2'].mean())

print(">>> Starting plotting...")
plt.figure(figsize=(16, 12), dpi=300)
ax = plt.gca()

for _, row in df.iterrows():
    c = row['Cluster']
    if c == -1: continue

    cx, cy = centers[c]
    ax.plot([row['Dim1'], cx], [row['Dim2'], cy],
            color='#D3D3D3', alpha=0.08, linewidth=0.1, zorder=1)

cmap = plt.get_cmap('tab20', max(1, n_clusters))
cluster_colors = {}

for i, c in enumerate(valid_clusters):
    r, g, b, a = cmap(i)
    if r > 0.7 and g < 0.4 and b < 0.4:
        cluster_colors[c] = 'gold'
    else:
        cluster_colors[c] = cmap(i)

noise_df = df[df['Cluster'] == -1]
ax.scatter(noise_df['Dim1'], noise_df['Dim2'],
           c='#E0E0E0', s=10, alpha=0.2, edgecolors='none', zorder=2)

bg_df = df[df['Highlight_Type'] == 'Background']
for c in valid_clusters:
    sub_df = bg_df[bg_df['Cluster'] == c]
    ax.scatter(sub_df['Dim1'], sub_df['Dim2'],
               c=[cluster_colors[c]], s=15, alpha=0.25, edgecolors='none', zorder=3)

for i, c in enumerate(valid_clusters):
    cx, cy = centers[c]
    ax.scatter(cx, cy, c='red', marker='*', s=200, edgecolors='k', linewidths=1.0,
               zorder=4, label='Cluster Center' if i == 0 else "")

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

ax.set_title("", fontsize=24, pad=20)
ax.set_xlabel("t-SNE 1", fontsize=20)
ax.set_ylabel("t-SNE 2", fontsize=20)
ax.tick_params(axis='both', which='major', labelsize=16)
ax.grid(True, linestyle='--', color='lightgray', alpha=0.5)

ax.legend(markerscale=1.5, fontsize=16, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False)

plt.tight_layout()
plt.savefig(OUTPUT_PLOT, bbox_inches='tight', transparent=True)
print(f">>> Plotting complete! Image saved as {OUTPUT_PLOT}")