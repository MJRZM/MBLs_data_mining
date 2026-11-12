import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import textwrap

input_file = 'samples.xlsx'
shapefile_path = 'ne_10m_admin_0_countries.shp'
output_image = 'final_labeled_map.png'

df = pd.read_excel(input_file)
df.columns = df.columns.str.strip()

grid_size = 8.0
df['Lon_approx'] = (df['Longitude'] / grid_size).round() * grid_size
df['Lat_approx'] = (df['Latitude'] / grid_size).round() * grid_size

def format_proteins_wrap(x):
    prots = sorted(set(x.astype(str)))
    full_text = ", ".join(prots)
    return textwrap.fill(full_text, width=25)

grouped = df.groupby(['Lon_approx', 'Lat_approx', 'Phylum']).agg({
    'Longitude': 'mean',
    'Latitude': 'mean',
    'Protein': format_proteins_wrap,
    'Genome_Accession': 'count'
}).reset_index()
grouped.rename(columns={'Genome_Accession': 'Count'}, inplace=True)

unique_phyla = grouped['Phylum'].unique()
colors = plt.cm.tab10.colors[:len(unique_phyla)]
phylum_color_map = dict(zip(unique_phyla, colors))

world = gpd.read_file(shapefile_path)

fig, ax = plt.subplots(figsize=(18, 9))
world.plot(ax=ax, color='#E0E0E0', edgecolor='white', linewidth=0.8)

texts = []
for _, row in grouped.iterrows():
    p_color = phylum_color_map[row['Phylum']]

    ax.scatter(row['Longitude'], row['Latitude'],
               color=p_color, s=70, zorder=5, alpha=0.9, edgecolors='white', linewidths=1.5)

    label_text = f"{row['Phylum']} (n={row['Count']})\n{row['Protein']}"

    t = ax.text(row['Longitude'], row['Latitude'], label_text,
                fontsize=7, color='black', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="#FAFAFA", ec=p_color, lw=1.2, alpha=0.95))
    texts.append(t)

adjust_text(texts, ax=ax,
            arrowprops=dict(arrowstyle='-', color='#888888', lw=1.2, alpha=0.8),
            force_points=0.5, force_text=2.5,
            expand_points=(1.5, 1.5), expand_text=(1.2, 1.2),
            max_iterations=3000)

ax.set_xlim([-175, 175])
ax.set_ylim([-55, 85])

ax.grid(False)
ax.set_axis_off()

plt.savefig(output_image, dpi=300, transparent=True)
print(f"Map saved successfully: {output_image}")