import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['axes.linewidth'] = 1.5

print("Reading raw data...")
file_path = 'input_data.xlsx'
df_raw = pd.read_excel(file_path)

habitat_order = [
    "Soil environment",
    "Plant-associated",
    "Agricultural facilities",
    "Animal and Food"
]
df_raw['Habitat'] = pd.Categorical(df_raw['Habitat'], categories=habitat_order, ordered=True)

color_dict = {
    "Soil environment": "#8B5A2B",
    "Plant-associated": "#2E8B57",
    "Agricultural facilities": "#DAA520",
    "Animal and Food": "#9370DB"
}

print("Drawing jittered scatter timeline...")
fig, ax = plt.subplots(figsize=(12, 6))

sns.stripplot(
    data=df_raw,
    x='Year',
    y='Habitat',
    hue='Habitat',
    palette=color_dict,
    size=7,
    jitter=0.25,
    alpha=0.75,
    edgecolor='white',
    linewidth=0.5,
    legend=False,
    ax=ax
)

ax.grid(axis='x', color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Year of Isolation', fontsize=17, fontweight='bold', labelpad=10)
ax.set_ylabel('Habitat', fontsize=17, fontweight='bold', labelpad=10)

ax.tick_params(axis='x', labelsize=15, labelrotation=45)
ax.tick_params(axis='y', labelsize=15)

plt.setp(ax.get_yticklabels(), fontweight='bold')

ax.set_title('Spatiotemporal Dynamics of Isolates', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()

plt.savefig('scatter_timeline.pdf', dpi=300, bbox_inches='tight')
plt.savefig('scatter_timeline.png', dpi=300, bbox_inches='tight')
plt.show()

print("Plotting complete. PDF and PNG files saved in the current directory.")