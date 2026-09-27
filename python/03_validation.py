# Preciznost i odziv strogog pravila na uzorku od 100 zapisa; dva neovisna ljudska kodera (author1 = V.U., author2 = D.M.), referenca = usuglašeno kodiranje (consensus), AI kodiranje samo dopunski
import json, math, pandas as pd
from sklearn.metrics import cohen_kappa_score as kappa
v = pd.read_csv('validation/precision_sample100_coded.csv'); s = v.strict_rule == 1; n = int(s.sum())
def wilson(tp, n, z=1.96):
    p = tp / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
out = {'n_sample': len(v), 'n_strict_in_sample': n,
       'agreement_author1_author2': round(float((v.coder_author1 == v.coder_author2).mean()), 3),
       'kappa_author1_author2': round(kappa(v.coder_author1, v.coder_author2), 3),
       'disagreements_author1_yes_author2_no': int(((v.coder_author1 == 1) & (v.coder_author2 == 0)).sum()),
       'disagreements_author1_no_author2_yes': int(((v.coder_author1 == 0) & (v.coder_author2 == 1)).sum())}
for k in ('consensus', 'author1', 'author2'):
    ref = v['coder_' + k]; tp = int((ref[s] == 1).sum())
    out[k] = {'relevant_in_sample': int(ref.sum()), 'tp': tp, 'precision_strict': round(tp / n, 3), 'precision_ci95_wilson': wilson(tp, n), 'recall_strict': round(tp / int(ref.sum()), 3),
              'agreement_with_ai': round(float((ref == v.coder_ai).mean()), 3), 'kappa_with_ai': round(kappa(ref, v.coder_ai), 3)}
json.dump(out, open('results/validation_summary.json', 'w'), indent=1); print(out)
