import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7})
B = json.load(open('results/bib_summary.json')); E = json.load(open('results/eurostat_summary.json'))
fig, ax = plt.subplots(figsize=(5.4, 2.3)); ax.set_xlim(0, 10); ax.set_ylim(0, 4.3); ax.axis('off')
boxes = [(0.2, 'AI adoption', '#dbe9fa'), (3.7, 'Digital\ntransformation', '#fdebd0'), (7.2, 'Organisational\nresilience', '#d8f1e6')]
for x, t, c in boxes:
    ax.add_patch(FancyBboxPatch((x, 2.3), 2.6, 1.2, boxstyle='round,pad=0.05,rounding_size=0.15', fc=c, ec='#52514e', lw=0.8))
    ax.text(x + 1.3, 2.9, t, ha='center', va='center', fontsize=8, fontweight='bold')
for x0, x1 in [(2.85, 3.65), (6.35, 7.15)]:
    ax.add_patch(FancyArrowPatch((x0, 2.9), (x1, 2.9), arrowstyle='-|>', mutation_scale=12, lw=1.2, color='#52514e'))
rd = B['res_dt']
ax.text(3.25, 1.95, 'Link 1', ha='center', fontsize=7, fontweight='bold')
ax.text(3.25, 1.05, f"Eurostat, EU-27, 2025:\nsmall-firm AI use vs. basic\ndigital intensity, ρ = {E['spearman_dii_ai_small'][0]:.2f}", ha='center', va='center', fontsize=6.2)
ax.text(6.75, 1.95, 'Link 2', ha='center', fontsize=7, fontweight='bold')
ax.text(6.75, 1.0, f"Literature: {rd['both']} papers mention both\n({rd['share_of_resilience_with_dt']:.0f}% of resilience papers);\n{B['subset64']['design'].get('quantitative', 0)} quantitative studies.\nNot measured by Eurostat.", ha='center', va='center', fontsize=6.2)
fig.savefig('figures/Fig1_concept.png', dpi=600, bbox_inches='tight', facecolor='white')
