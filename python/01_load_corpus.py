# Ucitava OpenAlex stranice (data/openalex/corpus) u tablicu zapisa -> work/corpus_raw.pkl
import json, glob, os, pandas as pd
os.makedirs('work', exist_ok=True)
def abstract(ii):
    if not ii: return ''
    return ' '.join(w for p, w in sorted((p, w) for w, ps in ii.items() for p in ps))
recs = []
for p in sorted(glob.glob('data/openalex/corpus/page_*.json')):
    for w in json.load(open(p, encoding='utf-8'))['results']:
        pl = w.get('primary_location') or {}; src = pl.get('source') or {}
        recs.append(dict(id=w['id'].split('/')[-1], doi=w.get('doi'), year=w['publication_year'], type=w.get('type'), lang=w.get('language'),
                         title=w.get('title') or '', abstract=abstract(w.get('abstract_inverted_index')), source=src.get('display_name'),
                         countries=sorted({c for a in (w.get('authorships') or []) for c in (a.get('countries') or [])}),
                         kw=[k['display_name'].lower() for k in (w.get('keywords') or [])], cites=w.get('cited_by_count', 0),
                         src_core=src.get('is_core'), src_doaj=src.get('is_in_doaj'), src_lists=';'.join(src.get('listed_in') or []),
                         src_type=src.get('type'), publisher=src.get('host_organization_name'), issn_l=src.get('issn_l')))
R = pd.DataFrame(recs).drop_duplicates('id'); R.to_pickle('work/corpus_raw.pkl'); print('records', len(R))
