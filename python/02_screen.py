# Probiranje: (1) pojam AI i pojam MSP u naslovu/sazetku, (2) strogo pravilo; uzorak od 100 zapisa za provjeru preciznosti
import re, pandas as pd
R = pd.read_pickle('work/corpus_raw.pkl'); T = (R.title + ' ' + R.abstract)
SME = r'small and medium|small- and medium|small-to-medium|small to medium|small business|small firm|micro.?enterprise|\bSMEs?\b|\bMSMEs?\b|small enterprises'
AI = r'artificial intelligence|machine learning|deep learning|generative ai|generative artificial|chatgpt|large language model|chatbot|\bAI\b|\bGenAI\b|\bLLMs?\b'
R['ok'] = (T.str.contains(SME, case=True, regex=True) | T.str.contains(SME.replace(r'\bSMEs?\b|\bMSMEs?\b|', ''), case=False, regex=True)) & T.str.contains(AI, case=False, regex=True)
C = R[R.ok].copy()
SMEr = re.compile(r'small and medium|small- and medium|small-to-medium|small to medium|small business|small firm|micro.?enterprise|\bSMEs?\b|\bMSMEs?\b|small enterprises|\bUMKM\b|\bPYMES?\b', re.I)
AIr = re.compile(AI, re.I)
def strict(r):
    t = r.title; a = r.abstract if isinstance(r.abstract, str) else ''
    return (bool(SMEr.search(t)) or len(SMEr.findall(a)) >= 2) and (bool(AIr.search(t)) or len(AIr.findall(a)) >= 2)
C['strict'] = [strict(r) for _, r in C.iterrows()]
C.to_pickle('work/corpus.pkl')
C.sample(100, random_state=7)[['id', 'year', 'title']].to_csv('work/precision_sample100_drawn.csv', index=False)
print('screened', len(C), 'strict', int(C.strict.sum()))
