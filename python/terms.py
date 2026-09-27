import re
# kontrolirani rjecnik tema (regex nad naslovom i sazetkom), grupa: (oznaka, regex)
TERMS = {
 'Technology': {
  'generative AI / LLM': r'generative (ai|artificial)|chatgpt|large language model|\bllms?\b|\bgenai\b|\bgpt',
  'machine learning': r'machine learning|random forest|support vector|xgboost|gradient boosting',
  'deep learning': r'deep learning|neural network|convolutional|\blstm\b|transformer model',
  'chatbots / conversational AI': r'chatbot|conversational (ai|agent)|virtual assistant',
  'NLP / text analytics': r'natural language processing|\bnlp\b|text mining|sentiment analysis',
  'computer vision': r'computer vision|image (recognition|classification|processing)|defect detection|visual inspection',
  'process automation / RPA': r'robotic process automation|\brpa\b|process automation|automat(e|ion) of (routine|repetitive|business)|workflow automation',
  'big data / analytics': r'big data|business analytics|data analytics|business intelligence|predictive analytics',
  'cloud computing': r'cloud computing|\bcloud\b|software as a service|\bsaas\b',
  'IoT': r'internet of things|\biot\b|\biiot\b',
  'blockchain': r'blockchain|distributed ledger',
  'Industry 4.0': r'industry 4\.0|smart manufacturing|smart factor',
 },
 'Function': {
  'marketing': r'marketing|advertis|social media|customer engagement',
  'e-commerce': r'e-commerce|ecommerce|online (sales|shop|retail)|electronic commerce',
  'customer service / CRM': r'customer (service|relationship|support|experience)|\bcrm\b',
  'accounting / finance': r'accounting|financial reporting|audit|bookkeeping',
  'credit risk / fintech': r'credit (risk|scoring|rating)|default prediction|fintech|lending|loan|bankruptcy|financial distress',
  'supply chain / logistics': r'supply chain|logistic|inventory|procurement|demand forecast',
  'manufacturing / quality': r'manufactur|production (process|planning|line)|quality control|predictive maintenance|maintenance',
  'human resources': r'human resource|\bhrm\b|recruit|talent management|workforce',
  'decision-making': r'decision[- ]making|decision support',
  'innovation': r'innovation|innovative',
  'business model': r'business model',
  'sustainability / ESG': r'sustainable development|sustainability report|environmental sustainab|social sustainab|\besg\b|green (innovation|finance|supply|technolog|practice|economy|transition|product|procurement|ai)|circular economy|carbon|climate|environmental (performance|impact|management)|triple bottom line|\bsdgs?\b|corporate social responsibility|\bcsr\b',
 },
 'Adoption': {
  'adoption models (TOE/TAM/UTAUT)': r'\btoe\b|technology.organi[sz]ation.environment|\btam\b|technology acceptance|utaut|diffusion of innovation',
  'adoption / intention': r'adoption|intention to use|acceptance',
  'readiness / maturity': r'readiness|digital maturity|maturity model|preparedness',
  'skills / competences': r'skill|competenc|literacy|expertise|upskill|reskill|employee training|staff training|training programme|training program',
  'barriers / challenges': r'barrier|obstacle|impediment|inhibitor|hinder|constraint|(adoption|implementation|integration) challenge|challenges? (of|in|to|for|related to|when|associated with) (the )?(adopt|implement|integrat|us|deploy)',
  'cost / investment': r'\bcosts?\b|investment|return on investment|\broi\b|financial resources',
  'data privacy / security': r'privacy|data protection|\bgdpr\b|cybersecurity|cyber security|cyber-security|data security|information security',
  'ethics / trust': r'ethic|trust|responsible ai|bias|transparen',
  'regulation / policy': r'regulat|\bai act\b|public policy|government support|policy makers|policymakers',
 },
 'Outcome': {
  'digital transformation': r'digital transformation|digitali[sz]ation|digiti[sz]ation',
  'resilience': r'resilien',
  'crisis / COVID-19': r'covid|pandemic|crisis|crises|disruption|uncertaint',
  'dynamic capabilities': r'dynamic capabilit|absorptive capacity|resource.based view|\brbv\b',
  'firm performance': r'firm performance|business performance|organi[sz]ational performance|financial performance|performance of (smes|small)',
  'productivity / efficiency': r'productivity|efficiency',
  'competitiveness': r'competitive',
  'entrepreneurship': r'entrepreneur|start-?up',
  'internationalisation': r'internationali[sz]ation|export|global market',
  'emerging economies': r'emerging econom|developing (countr|econom)|low- and middle-income',
 },
}
FLAT = {k: (g, re.compile(v, re.I)) for g, d in TERMS.items() for k, v in d.items()}
def tag(text):
    return sorted(k for k, (g, r) in FLAT.items() if r.search(text))
GROUP = {k: g for k, (g, r) in FLAT.items()}
