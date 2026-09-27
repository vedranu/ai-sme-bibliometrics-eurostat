# -*- coding: utf-8 -*-
# Revidirana bibliometrijska analiza (nakon recenzije). Pokretati s PYTHONHASHSEED=0.
import sys, json, math, itertools, collections, re
sys.path.insert(0, 'python'); from terms import tag, GROUP, TERMS
import numpy as np, pandas as pd, networkx as nx, scipy.stats as st
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patheffects as pe
from matplotlib.path import Path; from matplotlib.patches import PathPatch
from networkx.algorithms.community import louvain_communities
from sklearn.metrics import adjusted_rand_score
from adjustText import adjust_text
OUT = 'results'; SEED = 20260927; HALO = [pe.withStroke(linewidth=2.2, foreground='white')]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7, 'axes.linewidth': 0.5, 'axes.edgecolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})
CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
S = {}
def save(fig, n): fig.savefig(f'figures/{n}.png', dpi=600, bbox_inches='tight', facecolor='white'); plt.close(fig)
def clean(ax, g='y'):
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.grid(axis=g, color='#e6e5e0', lw=0.4); ax.set_axisbelow(True)
# ---------------- korpusi ----------------
ALL = pd.read_pickle('work/corpus.pkl'); ALL = ALL[ALL.year <= 2025].copy()
ALL['t'] = (ALL.title + '. ' + ALL.abstract.fillna('')).apply(tag)
ALL['jrnl'] = ALL.src_type.isin(['journal', 'conference'])
C = ALL[ALL.strict & ALL.jrnl].copy()          # analizirana jezgra
SCR = ALL[ALL.jrnl].copy()                      # osjetljivost: pročišćeni skup (samo časopisi)
S['n_screened_all'] = int(len(ALL)); S['n_strict_all'] = int(ALL.strict.sum())
S['excluded_repository_or_nosource_in_strict'] = int((ALL.strict & ~ALL.jrnl).sum()); S['n_core'] = int(len(C)); S['n_screened_journal'] = int(len(SCR))
C.to_pickle('work/core_final.pkl')
# ---------------- rast i baze ----------------
oa = pd.read_csv('data/openalex/openalex_annual.csv').set_index('year')
sc = pd.read_csv('data/scopus_wos/scopus_annual.csv').set_index('year').scopus; wo = pd.read_csv('data/scopus_wos/wos_annual.csv').set_index('year').wos
Y = list(range(2010, 2026))
A = pd.DataFrame({'openalex_raw': oa.core.reindex(Y), 'scopus': sc.reindex(Y, fill_value=0), 'wos': wo.reindex(Y, fill_value=0),
                  'openalex_core': C.year.value_counts().reindex(Y, fill_value=0), 'openalex_core_cwts': C[C.src_core.fillna(False).astype(bool)].year.value_counts().reindex(Y, fill_value=0),
                  'sme_all': oa.sme_all.reindex(Y)})
A.to_csv(f'{OUT}/T_annual_counts.csv')
cagr = lambda s, a=2019, b=2025: (s[b] / s[a]) ** (1 / (b - a)) - 1
S['cagr_2019_2025'] = {k: round(cagr(A[k]) * 100, 1) for k in A.columns}
S['totals'] = {k: int(A[k].sum()) for k in A.columns}
L = np.log(A[['openalex_raw', 'scopus', 'wos']].loc[2016:2025]).diff().dropna()   # log-rast 2017-2025, n = 9
S['logdiff_corr_2017_2025'] = {f'{a}~{b}': round(float(np.corrcoef(L[a], L[b])[0, 1]), 2) for a, b in [('openalex_raw', 'scopus'), ('openalex_raw', 'wos'), ('scopus', 'wos')]}
S['mean_logdiff_2017_2025'] = {k: round(float(np.exp(L[k].mean()) - 1) * 100, 1) for k in L}
S['ratio_oa_raw_to_scopus'] = {int(y): round(A.openalex_raw[y] / A.scopus[y], 2) for y in [2019, 2021, 2023, 2024, 2025]}
S['penetration_per1000'] = {int(y): round(A.openalex_core[y] / A.sme_all[y] * 1000, 2) for y in [2019, 2023, 2025]}
# izvori po razdobljima
def per(y): return '2010-2020' if y <= 2020 else ('2021-2023' if y <= 2023 else ('2024' if y == 2024 else '2025'))
Z = ALL[ALL.strict].assign(p=lambda d: d.year.apply(per), repo=lambda d: ~d.jrnl, core=lambda d: d.src_core.fillna(False).astype(bool), doaj=lambda d: d.src_doaj.fillna(False).astype(bool))
SRC = Z.groupby('p').agg(n=('year', 'size'), repository_or_none=('repo', 'mean'), cwts_core=('core', 'mean'), doaj=('doaj', 'mean')).round(3)
SRC.to_csv(f'{OUT}/T_sources_by_period.csv'); S['sources_by_period'] = SRC.to_dict('index')
top = {p: d[d.jrnl].source.value_counts().head(10) for p, d in Z.groupby('p')}
pd.concat({p: v.reset_index().rename(columns={'source': 'journal', 'count': 'n'}) for p, v in top.items()}).to_csv(f'{OUT}/T_top_sources_by_period.csv')
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.4, 2.4), gridspec_kw={'wspace': 0.36})
yy = list(range(2015, 2026))
for k, lab, c in [('openalex_raw', 'OpenAlex (query result)', CAT[0]), ('scopus', 'Scopus', CAT[1]), ('wos', 'Web of Science', CAT[2])]:
    a1.plot(yy, A[k].loc[yy], marker='o', ms=3, lw=1.6, color=c, label=lab)
    a2.plot(L.index, L[k] * 100, marker='o', ms=3, lw=1.6, color=c, label=lab)
a1.set_ylabel('Articles and reviews per year'); a1.set_title('(a) Annual output, same query', loc='left', fontsize=7.5)
a2.set_ylabel('Growth, 100 × Δ ln(count)'); a2.set_title('(b) Annual growth rates', loc='left', fontsize=7.5); a2.axhline(0, color='#c3c2b7', lw=0.6)
for ax in (a1, a2): clean(ax); ax.set_xticks(range(2015, 2026, 2) if ax is a1 else range(2017, 2026, 2))
a1.legend(frameon=False, fontsize=6.2, loc='upper left'); save(fig, 'Fig2_growth_databases')
# ---------------- teme ----------------
MINF = 20
def counts(df): return collections.Counter(k for ts in df.t for k in ts)
cnt = counts(C); N = len(C)
allthemes = [k for g, d in TERMS.items() for k in d]
FT = pd.DataFrame({'group': [GROUP[k] for k in allthemes], 'papers': [cnt.get(k, 0) for k in allthemes]}, index=allthemes)
FT['share_pct'] = (FT.papers / N * 100).round(1); FT['in_network'] = FT.papers >= MINF
FT['regex'] = [TERMS[GROUP[k]][k] for k in allthemes]; FT.to_csv(f'{OUT}/T_theme_frequencies.csv')
S['dropped_themes'] = FT[~FT.in_network].papers.to_dict()
def graph(df, nodes):
    c = counts(df); n = len(df); G = nx.Graph(); G.add_nodes_from(nodes)
    for ts in df.t:
        for a, b in itertools.combinations(sorted(set(ts) & set(nodes)), 2): G.add_edge(a, b, weight=G[a][b]['weight'] + 1 if G.has_edge(a, b) else 1)
    for a, b, d in G.edges(data=True): d['assoc'] = d['weight'] * n / (c[a] * c[b])
    return G, c
nodes = sorted(k for k in allthemes if cnt.get(k, 0) >= MINF); G, _ = graph(C, nodes)
S['n_nodes'] = len(G); S['n_edges'] = G.number_of_edges()
def part(G, res, seed): return louvain_communities(G, weight='assoc', seed=seed, resolution=res)
def labels(parts, order): lab = {k: i for i, cs in enumerate(parts) for k in cs}; return [lab[k] for k in order]
# stabilnost i rezolucija
grid = {}
for res in [1.0, 1.1, 1.15, 1.2, 1.25, 1.5]:
    Ps = [labels(part(G, res, s), nodes) for s in range(50)]; ks = [len(set(p)) for p in Ps]
    ari = [adjusted_rand_score(Ps[i], Ps[j]) for i in range(50) for j in range(i + 1, 50)]
    Q = [nx.algorithms.community.modularity(G, part(G, res, s), weight='assoc') for s in range(10)]
    grid[res] = {'k_median': float(np.median(ks)), 'k_range': [int(min(ks)), int(max(ks))], 'ari_mean': round(float(np.mean(ari)), 3), 'modularity': round(float(np.mean(Q)), 3)}
S['louvain_grid'] = grid
RES = 1.0; S['resolution'] = RES
# koliko cesto su DT i otpornost u istom klasteru (preko sjemena, rezolucija i skupova)
co = {}
for nm, gg in [('core', G)]:
    for r in [1.0, 1.1, 1.15, 1.2, 1.25]:
        same = [any(('digital transformation' in c) and ('resilience' in c) for c in part(gg, r, s)) for s in range(50)]
        co[f'{nm}_{r}'] = round(float(np.mean(same)), 2)
S['dt_res_same_cluster_rate'] = co
# konsenzusna particija: najčešća particija (modalna) preko 50 sjemena
Ps = [tuple(labels(part(G, RES, s), nodes)) for s in range(50)]
def canon(p): m = {}; return tuple(m.setdefault(x, len(m)) for x in p)
mode = collections.Counter(canon(p) for p in Ps).most_common(1)[0]; S['modal_partition_share'] = round(mode[1] / 50, 2)
lab = dict(zip(nodes, mode[0])); comm = [set(k for k in nodes if lab[k] == i) for i in set(mode[0])]
comm = sorted(comm, key=lambda s: -sum(cnt[k] for k in s)); S['clusters'] = [sorted(cs, key=lambda k: -cnt[k]) for cs in comm]
# osjetljivost na pročišćeni skup (3.0xx)
G2, c2 = graph(SCR, nodes)
P2 = collections.Counter(canon(tuple(labels(part(G2, RES, s), nodes))) for s in range(50)).most_common(1)[0][0]
S['sensitivity_ARI_core_vs_screened'] = round(adjusted_rand_score(list(mode[0]), list(P2)), 3)
S['dt_res_same_cluster_rate']['screened_1.0'] = round(float(np.mean([any(('digital transformation' in c) and ('resilience' in c) for c in part(G2, 1.0, s)) for s in range(50)])), 2)
# tematska karta
TM = []
for i, cs in enumerate(comm):
    ext = sum(d['assoc'] for a, b, d in G.edges(data=True) if (a in cs) != (b in cs)); inn = [d['assoc'] for a, b, d in G.edges(data=True) if a in cs and b in cs]
    TM.append(dict(cluster=f'C{i+1}', label=', '.join(sorted(cs, key=lambda k: -cnt[k])[:2]), papers=int(C.t.apply(lambda ts: bool(set(ts) & cs)).sum()),
                   n_themes=len(cs), centrality=ext / len(cs), density=float(np.mean(inn)) if inn else 0.0, themes='; '.join(sorted(cs, key=lambda k: -cnt[k]))))
TM = pd.DataFrame(TM); TM.to_csv(f'{OUT}/T_clusters.csv', index=False); S['thematic_map'] = TM.round(3).drop(columns='themes').to_dict('records')
# slika 2: mreza
col = {k: CAT[i % len(CAT)] for i, cs in enumerate(comm) for k in cs}
pos = nx.kamada_kawai_layout(G, weight=None, pos=nx.spring_layout(G, weight='assoc', seed=SEED, k=2.2 / math.sqrt(len(G)), iterations=500))
fig, ax = plt.subplots(figsize=(6.4, 5.6))
E = [(a, b, d) for a, b, d in G.edges(data=True) if d['assoc'] >= 1.6 and d['weight'] >= 10]; wmax = max(d['weight'] for *_, d in E)
for a, b, d in sorted(E, key=lambda e: e[2]['weight']):
    ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color='#8a8984', lw=0.2 + 2.2 * d['weight'] / wmax, alpha=0.22, zorder=1)
km = max(cnt[k] for k in G); cx = np.mean([p[0] for p in pos.values()]); cy = np.mean([p[1] for p in pos.values()])
for k in G: ax.scatter(*pos[k], s=14 + 480 * cnt[k] / km, color=col[k], edgecolor='white', lw=0.6, zorder=3)
OVR = {'readiness / maturity': ('U', 0), 'ethics / trust': ('R', 0), 'process automation / RPA': ('D', 0), 'cost / investment': ('R', 0), 'human resources': ('D', 0), 'marketing': ('L', 0), 'digital transformation': ('U', 0)}
tx = []
for k in G:
    x, y = pos[k]; rad = math.sqrt(14 + 480 * cnt[k] / km) / 2 + 2.5
    side = OVR.get(k, (None, 0))[0] or ('R' if x >= cx else 'L'); dy = OVR.get(k, (None, 0))[1]
    if side == 'U': xy, ha, va = (0, rad), 'center', 'bottom'
    elif side == 'D': xy, ha, va = (0, -rad), 'center', 'top'
    else: xy, ha, va = ((rad, dy) if side == 'R' else (-rad, dy)), ('left' if side == 'R' else 'right'), 'center'
    tx.append(ax.annotate(k, (x, y), xytext=xy, textcoords='offset points', ha=ha, va=va, fontsize=6.2, zorder=4, path_effects=HALO))
fig.canvas.draw()
# razmakni preklapajuce oznake okomito
for it in range(200):
    moved = False; bbs = [t.get_window_extent() for t in tx]
    for i in range(len(tx)):
        for j in range(i + 1, len(tx)):
            if bbs[i].overlaps(bbs[j]):
                oi = tx[i].xyann; oj = tx[j].xyann; up = 1 if bbs[i].y0 >= bbs[j].y0 else -1
                tx[i].xyann = (oi[0], oi[1] + 1.2 * up); tx[j].xyann = (oj[0], oj[1] - 1.2 * up); moved = True
    if not moved: break
    fig.canvas.draw()
ax.axis('off')
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], marker='o', ls='', color=CAT[i % len(CAT)], ms=5, label=f'C{i+1}: ' + ', '.join(sorted(cs, key=lambda k: -cnt[k])[:2])) for i, cs in enumerate(comm)],
          frameon=False, fontsize=6.2, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2)
save(fig, 'Fig3_theme_network')
# slika 3: tematska karta
fig, ax = plt.subplots(figsize=(4.6, 3.5)); mx, my = TM.centrality.median(), TM.density.median()
ax.axvline(mx, color='#c3c2b7', lw=0.7, ls='--'); ax.axhline(my, color='#c3c2b7', lw=0.7, ls='--')
for i, t in TM.iterrows(): ax.scatter(t.centrality, t.density, s=40 + 650 * t.papers / TM.papers.max(), color=CAT[i % len(CAT)], alpha=0.85, edgecolor='white', lw=1.5)
tt = [ax.text(t.centrality, t.density, t.cluster + '\n' + t.label.replace(', ', '\n'), fontsize=5.6, ha='center', va='center', path_effects=HALO) for _, t in TM.iterrows()]
adjust_text(tt, ax=ax, expand=(1.5, 1.9), arrowprops=dict(arrowstyle='-', color='#8a8984', lw=0.3)); ax.margins(0.18)
ax.set_xlabel('Centrality (external association per theme)'); ax.set_ylabel('Density (mean internal association)')
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
save(fig, 'Fig4_thematic_map')
# ---------------- tematska evolucija ----------------
PER = [(2010, 2020), (2021, 2023), (2024, 2025)]
def coword(sub):
    c = counts(sub); nd = sorted(k for k, v in c.items() if v >= max(5, 0.03 * len(sub))); g, _ = graph(sub, nd)
    Pc = collections.Counter(canon(tuple(labels(part(g, RES, s), nd))) for s in range(30)).most_common(1)[0][0]
    cm = [set(k for k, l in zip(nd, Pc) if l == i) for i in set(Pc)]
    return c, [s for s in sorted(cm, key=lambda s: -sum(c[k] for k in s)) if len(s) >= 2][:7]
pc = []; S['period_n'] = []
for a, b in PER:
    sub = C[C.year.between(a, b)]; S['period_n'].append(int(len(sub))); c2_, cm = coword(sub)
    pc.append([(set(cs), ', '.join(sorted(cs, key=lambda k: -c2_[k])[:2]), int(sub.t.apply(lambda ts: bool(set(ts) & cs)).sum())) for cs in cm])
S['evolution'] = [[dict(label=l, n=n, themes=sorted(A_)) for A_, l, n in cl] for cl in pc]
links = [(p, i, j, len(A1 & B1) / min(len(A1), len(B1))) for p in range(len(PER) - 1) for i, (A1, _, _) in enumerate(pc[p]) for j, (B1, _, _) in enumerate(pc[p + 1]) if len(A1 & B1) / min(len(A1), len(B1)) >= 0.25]
S['evolution_links'] = [dict(frm=pc[p][i][1], to=pc[p + 1][j][1], period=p, inclusion=round(v, 2)) for p, i, j, v in links]
# boja slijedi klaster nasljednik: zadnje razdoblje dobiva boje, ranija razdoblja nasljeduju boju najjaceg izlaznog toka
colr = {(len(PER) - 1, i): CAT[i % len(CAT)] for i in range(len(pc[-1]))}
for p in range(len(PER) - 2, -1, -1):
    for i in range(len(pc[p])):
        out = [(inc, j) for pp, ii, j, inc in links if pp == p and ii == i]
        colr[(p, i)] = colr[(p + 1, max(out)[1])] if out else '#b5b4ae'
fig, ax = plt.subplots(figsize=(6.2, 4.4)); yc = {}
for p, cl in enumerate(pc):
    tot = sum(n for *_, n in cl); y = 0
    for i, (A1, l, n) in enumerate(cl):
        h = n / tot * 0.86; yc[(p, i)] = (y, y + h); ax.add_patch(plt.Rectangle((p * 2.2, y), 0.1, h, color=colr[(p, i)]))
        ax.text(p * 2.2 + 0.14, y + h / 2, l.replace(', ', ',\n') + f'\n(n = {n})', fontsize=5.3, va='center', ha='left', linespacing=1.0, bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.9), zorder=5)
        y += h + 0.14 / len(cl)
    ax.text(p * 2.2, 1.06, f'{PER[p][0]}-{PER[p][1]}  (n = {S["period_n"][p]})', fontsize=7, fontweight='bold')
for p, i, j, inc in links:
    y0 = sum(yc[(p, i)]) / 2; y1 = sum(yc[(p + 1, j)]) / 2; x0 = p * 2.2 + 1.38; x1 = (p + 1) * 2.2
    ax.add_patch(PathPatch(Path([(x0, y0), (x0 + 0.4, y0), (x1 - 0.4, y1), (x1, y1)], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]), fc='none', ec=colr[(p + 1, j)], lw=0.5 + 6 * inc, alpha=0.45))
ax.set_xlim(-0.1, 2.2 * len(PER) - 0.35); ax.set_ylim(-0.03, 1.12); ax.axis('off'); save(fig, 'Fig5_thematic_evolution')
KT = pd.DataFrame({f'{a}-{b}': [C[C.year.between(a, b)].t.apply(lambda ts: k in ts).mean() * 100 for k in nodes] for a, b in PER}, index=nodes).round(1)
KT['change_pp'] = (KT.iloc[:, 2] - KT.iloc[:, 1]).round(1); KT['group'] = [GROUP[k] for k in KT.index]; KT.to_csv(f'{OUT}/T_theme_trends.csv')
S['trend_rise'] = KT.sort_values('change_pp', ascending=False).head(6).iloc[:, [1, 2, 3]].to_dict('index')
S['trend_fall'] = KT.sort_values('change_pp').head(5).iloc[:, [1, 2, 3]].to_dict('index')
S['trend_selected'] = KT.loc[[k for k in ['generative AI / LLM', 'resilience', 'digital transformation', 'machine learning', 'crisis / COVID-19', 'skills / competences', 'sustainability / ESG', 'barriers / challenges'] if k in KT.index]].iloc[:, :4].to_dict('index')
# ---------------- otpornost x DT ----------------
res = C.t.apply(lambda ts: 'resilience' in ts); dt = C.t.apply(lambda ts: 'digital transformation' in ts); both = res & dt
S['res_dt'] = {'resilience': int(res.sum()), 'dt': int(dt.sum()), 'both': int(both.sum()), 'both_share_core': round(both.mean() * 100, 1),
               'share_of_resilience_with_dt': round(both.sum() / res.sum() * 100, 1), 'share_of_dt_with_resilience': round(both.sum() / dt.sum() * 100, 1),
               'assoc_strength': round(both.sum() * N / (res.sum() * dt.sum()), 2)}
B = C[both].copy(); TX = (B.title + '. ' + B.abstract.fillna(''))
def rx(p): return TX.str.contains(p, case=False, regex=True)
typ = np.select([rx(r'systematic (literature )?review|bibliometric|literature review|meta-analys|scoping review'),
                 rx(r'survey|questionnaire|structural equation|\bsem\b|pls-sem|partial least squares|regression|panel data|respondents|sample of \d'),
                 rx(r'case stud|interview|qualitative|focus group')], ['review', 'quantitative', 'qualitative'], 'conceptual/other')
B['design'] = typ; B['mediation'] = rx(r'mediat'); B['res_construct'] = rx(r'(organi[sz]ational|business|firm|enterprise|sme|smes\'?|operational|supply chain) resilience')
B['res_title'] = B.title.str.contains('resilien', case=False)
S['subset64'] = {'n': int(len(B)), 'design': B.design.value_counts().to_dict(), 'mediation': int(B.mediation.sum()), 'resilience_as_construct': int(B.res_construct.sum()), 'resilience_in_title': int(B.res_title.sum()),
                 'years': B.year.value_counts().sort_index().to_dict()}
B[['id', 'year', 'title', 'source', 'design', 'mediation', 'res_construct', 'res_title']].to_csv(f'{OUT}/T_subset_resilience_dt.csv', index=False)
json.dump(S, open(f'{OUT}/bib_summary.json', 'w'), indent=1, default=str)
print(json.dumps(S, indent=1, default=str)[:9000])
