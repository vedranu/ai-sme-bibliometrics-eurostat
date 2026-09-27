# Eurostat: ucitavanje CSV-a (SDMX-CSV) i analiza korištenja AI-a prema velicini poduzeca
import os, pandas as pd
os.makedirs('work', exist_ok=True)
for f, o in [('data/eurostat/isoc_eb_ai.csv', 'work/eb_ai.pkl'), ('data/eurostat/isoc_e_dii.csv', 'work/dii.pkl')]:
    x = pd.read_csv(f, dtype=str); x['v'] = pd.to_numeric(x.OBS_VALUE, errors='coerce'); x.to_pickle(o)
import json, numpy as np, pandas as pd, scipy.stats as st
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from adjustText import adjust_text
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7, 'axes.linewidth': 0.5, 'axes.edgecolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})
CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']; HALO = [pe.withStroke(linewidth=2.2, foreground='white')]
OUT = 'results'; S = {}
def save(fig, n): fig.savefig(f'figures/{n}.png', dpi=600, bbox_inches='tight', facecolor='white'); plt.close(fig)
def clean(ax, grid='y'):
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.grid(axis=grid, color='#e6e5e0', lw=0.4); ax.set_axisbelow(True)
d = pd.read_pickle('work/eb_ai.pkl'); e = pd.read_pickle('work/dii.pkl')
EU27 = ['AT','BE','BG','CY','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK']
SZ = {'10-49': 'Small (10-49)', '50-249': 'Medium (50-249)', 'GE250': 'Large (250+)'}
def get(ind, unit='PC_ENT', geo=None, size=None, year=None, df=d):
    x = df[(df.indic_is == ind) & (df.unit == unit)]
    if geo is not None: x = x[x.geo.isin([geo] if isinstance(geo, str) else geo)]
    if size is not None: x = x[x.size_emp.isin([size] if isinstance(size, str) else size)]
    if year is not None: x = x[x.TIME_PERIOD == str(year)]
    return x
# ---- adoption by size, EU vs HR ----
T = get('E_AI_TANY', geo=['EU27_2020', 'HR'], size=list(SZ) + ['GE10']).pivot_table(index=['geo', 'size_emp'], columns='TIME_PERIOD', values='v')
T.to_csv(f'{OUT}/T_ai_by_size.csv'); S['ai_by_size'] = {f'{g}|{s}': r.round(2).to_dict() for (g, s), r in T.iterrows()}
for g in ['EU27_2020', 'HR']:
    S[f'gap_ratio_large_small_{g}'] = {y: round(T.loc[(g, 'GE250'), y] / T.loc[(g, '10-49'), y], 2) for y in T.columns}
    S[f'gap_pp_large_small_{g}'] = {y: round(T.loc[(g, 'GE250'), y] - T.loc[(g, '10-49'), y], 1) for y in T.columns}
fig, axs = plt.subplots(1, 2, figsize=(5.2, 2.4), sharey=True, gridspec_kw={'wspace': 0.12})
yrs = ['2021', '2023', '2024', '2025']
for ax, g, tt in zip(axs, ['EU27_2020', 'HR'], ['(a) EU-27', '(b) Croatia']):
    for i, s in enumerate(SZ):
        v = T.loc[(g, s), yrs]; ax.plot([int(y) for y in yrs], v.values, marker='o', ms=3.5, lw=1.8, color=CAT[i], label=SZ[s])
        ax.text(2025.15, v.iloc[-1], f'{v.iloc[-1]:.1f}', va='center', fontsize=6.3, color='#3b3a37')
    ax.axvspan(2021.2, 2022.8, color='#f1f0ec', zorder=0); ax.text(2022, 2, 'no survey\nmodule', ha='center', fontsize=5.5, color='#8a8984')
    ax.set_title(tt, loc='left', fontsize=7.5); ax.set_xticks([2021, 2022, 2023, 2024, 2025]); ax.set_xlim(2020.7, 2025.7); clean(ax)
axs[0].set_ylabel('Enterprises using at least one AI technology (%)'); axs[0].legend(frameon=False, fontsize=6.3, loc='upper left')
save(fig, 'Fig6_ai_by_size')
# ---- country cross-section 2025: small-firm AI vs small-firm digital intensity ----
ai_s = get('E_AI_TANY', geo=EU27, size='10-49', year=2025).set_index('geo').v
ai_l = get('E_AI_TANY', geo=EU27, size='GE250', year=2025).set_index('geo').v
dii_s = get('E_DI3_GELO', geo=EU27, size='10-49', year=2025, df=e).set_index('geo').v
X = pd.DataFrame({'ai_small': ai_s, 'ai_large': ai_l, 'dii_small': dii_s}).dropna(); X['gap_pp'] = X.ai_large - X.ai_small; X['ratio'] = X.ai_large / X.ai_small
X.round(2).to_csv(f'{OUT}/T_country_2025.csv')
r = st.spearmanr(X.dii_small, X.ai_small); pr = st.pearsonr(X.dii_small, X.ai_small); b = np.polyfit(X.dii_small, X.ai_small, 1)
S['country_n'] = int(len(X)); S['spearman_dii_ai_small'] = [round(r.statistic, 3), float(r.pvalue)]; S['pearson_dii_ai_small'] = [round(pr.statistic, 3), float(pr.pvalue)]
S['ols_slope_pp_per_pp'] = round(b[0], 3); S['r2'] = round(pr.statistic ** 2, 3)
r2 = st.spearmanr(X.ai_small, X.ratio); S['spearman_aismall_ratio'] = [round(r2.statistic, 3), float(r2.pvalue)]
S['HR_2025'] = X.loc['HR'].round(2).to_dict(); S['HR_rank_ai_small'] = int(X.ai_small.rank(ascending=False)['HR']); S['HR_rank_dii_small'] = int(X.dii_small.rank(ascending=False)['HR'])
S['ai_small_range'] = [X.ai_small.idxmin(), round(X.ai_small.min(), 1), X.ai_small.idxmax(), round(X.ai_small.max(), 1)]
fig, ax = plt.subplots(figsize=(4.6, 3.3))
xs = np.linspace(X.dii_small.min() - 2, X.dii_small.max() + 2, 50); ax.plot(xs, np.polyval(b, xs), color='#c3c2b7', lw=1, ls='--', zorder=1)
for c, rr in X.iterrows():
    ax.scatter(rr.dii_small, rr.ai_small, s=26, color=CAT[1] if c == 'HR' else CAT[0], edgecolor='white', lw=0.8, zorder=3)
tx = [ax.text(rr.dii_small, rr.ai_small, c, fontsize=5.8, fontweight='bold' if c == 'HR' else 'normal', path_effects=HALO, zorder=4) for c, rr in X.iterrows()]
adjust_text(tx, ax=ax, expand=(1.3, 1.5))
ax.set_xlabel('Small enterprises with at least basic digital intensity (%)'); ax.set_ylabel('Small enterprises using AI (%)'); clean(ax, 'both')
ax.text(0.02, 0.97, f'Spearman ρ = {r.statistic:.2f} (p {"< 0.001" if r.pvalue < 0.001 else "= %.3f" % r.pvalue}), n = {len(X)}', transform=ax.transAxes, fontsize=6.3, va='top', color='#3b3a37')
save(fig, 'Fig7_dii_vs_ai_countries')
# ---- AI use within digital-intensity levels (EU, 2025) ----
lev = {}
for L, lab in [('VLO', 'very low'), ('LO', 'low'), ('HI', 'high'), ('VHI', 'very high')]:
    for s in SZ:
        num = get(f'E_DI3_{L}_AI_TANY', geo='EU27_2020', size=s, year=2025).v; den = get(f'E_DI3_{L}', geo='EU27_2020', size=s, year=2025, df=e).v
        if len(num) and len(den): lev[(lab, s)] = round(float(num.iloc[0]) / float(den.iloc[0]) * 100, 1)
S['ai_rate_within_dii_EU_2025'] = {f'{a}|{b}': v for (a, b), v in lev.items()}
# ---- barriers (share of enterprises that considered AI), 2025 ----
BN = {'E_AI_BLE': 'Lack of relevant expertise', 'E_AI_BLEG': 'Unclear legal consequences', 'E_AI_BCDP': 'Data protection and privacy concerns', 'E_AI_BDDT': 'Data availability or quality',
      'E_AI_BINC': 'Incompatibility with existing systems', 'E_AI_BCST': 'Costs seem too high', 'E_AI_BEC': 'Ethical considerations', 'E_AI_BNU': 'AI not useful for the enterprise'}
B = pd.concat([get(k, unit='PC_ENT_AI_EC', geo=['EU27_2020', 'HR'], size=list(SZ), year=2025).assign(barrier=v) for k, v in BN.items()]).pivot_table(index='barrier', columns=['geo', 'size_emp'], values='v')
B = B.reindex(B[('EU27_2020', '10-49')].sort_values().index); B.round(1).to_csv(f'{OUT}/T_barriers_2025.csv'); S['barriers_2025'] = {f'{g}|{s}': B[(g, s)].round(1).to_dict() for g, s in B.columns}
ec = get('E_AI_EC', unit='PC_ENT_AI_TX', geo=['EU27_2020', 'HR'], size=list(SZ), year=2025).pivot_table(index='geo', columns='size_emp', values='v'); S['considered_among_nonusers_2025'] = ec.round(1).to_dict()
fig, axs = plt.subplots(1, 2, figsize=(5.2, 3.0), sharey=True, gridspec_kw={'wspace': 0.08}); yy = np.arange(len(B))
for ax, s, tt in zip(axs, ['10-49', 'GE250'], ['(a) Small enterprises (10-49)', '(b) Large enterprises (250+)']):
    for i, (g, lab) in enumerate([('EU27_2020', 'EU-27'), ('HR', 'Croatia')]):
        ax.scatter(B[(g, s)], yy + (0.12 if i else -0.12), s=22, color=CAT[i], edgecolor='white', lw=0.6, zorder=3, label=lab)
    for k in range(len(B)): ax.plot([B[('EU27_2020', s)].iloc[k], B[('HR', s)].iloc[k]], [k - 0.12, k + 0.12], color='#c3c2b7', lw=0.8, zorder=1)
    ax.set_title(tt, loc='left', fontsize=7.5); ax.set_xlim(0, 85); clean(ax, 'x'); ax.set_xlabel('% of enterprises that considered AI', fontsize=6.3)
axs[0].set_yticks(yy); axs[0].set_yticklabels(B.index); axs[0].legend(frameon=False, fontsize=6.3, loc='lower right')
save(fig, 'Fig8_barriers_2025')
# ---- purposes 2025 (share of AI users) ----
PN = {'E_AI_PMS': 'Marketing or sales', 'E_AI_PBAM': 'Business administration or management', 'E_AI_PITS': 'ICT security', 'E_AI_PFIN': 'Accounting, controlling or finance',
      'E_AI_PPP': 'Production processes', 'E_AI_PRDI': 'R&D or innovation', 'E_AI_PLOG': 'Logistics'}
P = pd.concat([get(k, unit='PC_ENT_AI_TANY', geo=['EU27_2020', 'HR'], size=list(SZ), year=2025).assign(purpose=v) for k, v in PN.items()]).pivot_table(index='purpose', columns=['geo', 'size_emp'], values='v')
P = P.reindex(P[('EU27_2020', '10-49')].sort_values(ascending=False).index); P.round(1).to_csv(f'{OUT}/T_purposes_2025.csv'); S['purposes_2025'] = {f'{g}|{s}': P[(g, s)].round(1).to_dict() for g, s in P.columns}
TN = {'E_AI_TTM': 'Text mining', 'E_AI_TNLG': 'Natural language generation', 'E_AI_TPVSG': 'Image, video or audio generation', 'E_AI_TSR': 'Speech recognition', 'E_AI_TPA': 'Workflow automation / decision support', 'E_AI_TML': 'Machine learning for data analysis', 'E_AI_TIR': 'Image recognition', 'E_AI_TAR': 'Autonomous robots, vehicles, drones'}
TT = pd.concat([get(k, geo=['EU27_2020', 'HR'], size=list(SZ), year=2025).assign(tech=v) for k, v in TN.items()]).pivot_table(index='tech', columns=['geo', 'size_emp'], values='v')
TT = TT.reindex(TT[('EU27_2020', '10-49')].sort_values(ascending=False).index); TT.round(1).to_csv(f'{OUT}/T_tech_2025.csv'); S['tech_2025'] = {f'{g}|{s}': TT[(g, s)].round(1).to_dict() for g, s in TT.columns}
json.dump(S, open(f'{OUT}/eurostat_summary.json', 'w'), indent=1, default=str); print(json.dumps(S, indent=1, default=str)[:7000])
