import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['axes.linewidth'] = 1.2

print("Parsing hierarchical location data...")
df = pd.read_excel('input_data.xlsx')


def split_hierarchy(loc):
    loc = str(loc).strip()
    if pd.isna(loc) or loc == 'nan': return 'Unknown', 'Unknown'

    if ':' in loc:
        parts = loc.split(':', 1)
        return parts[0].strip(), parts[1].strip()
    else:
        return loc, 'Unspecified'


df['Country'], df['Detail'] = zip(*df['Location'].apply(split_hierarchy))
df = df[df['Country'] != 'Unknown']

habitat_order = ["Soil environment", "Plant-associated", "Agricultural facilities", "Animal and Food"]
color_dict = {
    "Soil environment": "#8C6D51",
    "Plant-associated": "#4E8752",
    "Agricultural facilities": "#D4A35B",
    "Animal and Food": "#80709C"
}

df_country = df.groupby(['Country', 'Habitat']).size().unstack(fill_value=0)
for h in habitat_order:
    if h not in df_country.columns: df_country[h] = 0
df_country = df_country[habitat_order]
df_country['Total'] = df_country.sum(axis=1)
df_country = df_country.sort_values('Total', ascending=False).drop(columns='Total')

df_usa = df[df['Country'] == 'USA'].copy()


def clean_usa_states(detail):
    if 'IA' in detail: return 'IA'
    if 'IL' in detail: return 'IL'
    if 'NC' in detail or 'North Carolina' in detail: return 'NC'
    if 'NY' in detail or 'New York' in detail: return 'NY'
    if 'MN' in detail: return 'MN'
    if 'IN' in detail: return 'IN'
    if 'Wisconsin' in detail: return 'WI'
    if 'OH' in detail: return 'OH'
    if 'MO' in detail: return 'MO'
    return 'Other US Sites'


df_usa['State'] = df_usa['Detail'].apply(clean_usa_states)
df_state = df_usa.groupby(['State', 'Habitat']).size().unstack(fill_value=0)

for h in habitat_order:
    if h not in df_state.columns: df_state[h] = 0
df_state = df_state[habitat_order]
df_state['Total'] = df_state.sum(axis=1)
df_state['is_other'] = df_state.index == 'Other US Sites'
df_state = df_state.sort_values(by=['is_other', 'Total'], ascending=[True, False])
df_state = df_state.drop(columns=['Total', 'is_other'])

print("Generating high-resolution split-panel figure...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [1, 1.5]})
colors = [color_dict[col] for col in habitat_order]

df_country.plot(kind='bar', stacked=True, color=colors, ax=ax1, edgecolor='white', linewidth=0.5)
ax1.set_title('Global Distribution (Country-level)', fontsize=17, fontweight='bold', pad=15)
ax1.set_xlabel('Country', fontsize=17, fontweight='bold')
ax1.set_ylabel('Number of Isolates', fontsize=17, fontweight='bold')
ax1.tick_params(axis='x', labelsize=15, rotation=45)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.get_legend().remove()

df_state.plot(kind='bar', stacked=True, color=colors, ax=ax2, edgecolor='white', linewidth=0.5)
ax2.set_title('State-level Distribution (USA)', fontsize=17, fontweight='bold', pad=15)
ax2.set_xlabel('US State', fontsize=17, fontweight='bold')
ax2.set_ylabel('')
ax2.tick_params(axis='x', labelsize=15, rotation=45)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

ax2.legend(title='Habitat', title_fontsize=17, fontsize=15,
           frameon=False, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()

plt.savefig('split_resolution_panels.pdf', dpi=300, bbox_inches='tight')
plt.savefig('split_resolution_panels.png', dpi=300, bbox_inches='tight')
plt.show()

print("Plotting complete.")