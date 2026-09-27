import json, numpy as np, pandas as pd, scipy.stats as st
d = pd.read_pickle('work/eb_ai.pkl'); e = pd.read_pickle('work/dii.pkl')
EU27 = ['AT','BE','BG','CY','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK']
g = lambda df, ind, size, yr, unit='PC_ENT': df[(df.indic_is == ind) & (df.unit == unit) & (df.size_emp == size) & (df.TIME_PERIOD == str(yr)) & df.geo.isin(EU27)].set_index('geo').v
X = pd.DataFrame({'ai': g(d, 'E_AI_TANY', '10-49', 2025), 'dii25': g(e, 'E_DI3_GELO', '10-49', 2025), 'dii22': g(e, 'E_DI4_GELO', '10-49', 2022)}).dropna()
R = {}
def ols(x, y):
    r = st.linregress(x, y); t = st.t.ppf(0.975, len(x) - 2); return {'n': len(x), 'slope': round(r.slope, 3), 'ci95': [round(r.slope - t * r.stderr, 3), round(r.slope + t * r.stderr, 3)], 'r': round(r.rvalue, 3), 'rho': round(st.spearmanr(x, y).statistic, 3)}
R['ols_2025'] = ols(X.dii25, X.ai)
ts = st.theilslopes(X.ai, X.dii25); R['theil_sen_2025'] = {'slope': round(ts.slope, 3), 'ci95': [round(ts.low_slope, 3), round(ts.high_slope, 3)]}
Y = X.drop(['DK', 'FI', 'LU', 'CY']); R['ols_2025_excl_DK_FI_LU_CY'] = ols(Y.dii25, Y.ai)
Y2 = X.drop(['BG', 'DK', 'FI', 'LU', 'CY']); R['ols_2025_excl_BG_DK_FI_LU_CY'] = ols(Y2.dii25, Y2.ai)
R['ols_dii2022_noAIitem'] = ols(X.dii22, X.ai)
# influence: Cook's distance
x = X.dii25.values; y = X.ai.values; Xm = np.c_[np.ones_like(x), x]; b = np.linalg.lstsq(Xm, y, rcond=None)[0]; res = y - Xm @ b
H = Xm @ np.linalg.inv(Xm.T @ Xm) @ Xm.T; h = np.diag(H); s2 = res @ res / (len(x) - 2); cook = res**2 / (2 * s2) * h / (1 - h)**2
R['cooks_top'] = dict(sorted(zip(X.index, np.round(cook, 3)), key=lambda z: -z[1])[:5]); R['cooks_threshold_4_n'] = round(4 / len(x), 3)
# zastavice pouzdanosti za HR i EU
F = d[d.geo.isin(['HR']) & (d.TIME_PERIOD == '2025') & d.size_emp.isin(['10-49', '50-249', 'GE250']) & d.OBS_FLAG.notna()]
R['flags_HR_2025'] = F.groupby(['indic_is', 'unit', 'size_emp']).OBS_FLAG.first().reset_index().query("indic_is.str.match('^E_AI_(B|P|T)[A-Z]+$')").values.tolist()
R['flag_values_all'] = d.OBS_FLAG.value_counts(dropna=False).to_dict()
json.dump(R, open('results/eurostat_robustness.json', 'w'), indent=1, default=str); print(json.dumps(R, indent=1, default=str))
