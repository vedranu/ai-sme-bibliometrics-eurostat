# Zajednicki blokovi upita (OpenAlex title_and_abstract.search), identicni onima u radu (Prilog A)
$AI  = '("artificial intelligence" OR "machine learning" OR "deep learning" OR "generative AI" OR "generative artificial intelligence" OR ChatGPT OR "large language model" OR "large language models" OR chatbot OR chatbots)'
$SME = '("small and medium-sized enterprises" OR "small and medium sized enterprises" OR "small and medium enterprises" OR "small and medium-sized enterprise" OR "small and medium enterprise" OR SME OR SMEs OR MSME OR MSMEs OR "small business" OR "small businesses" OR "small firms" OR "micro enterprises" OR microenterprises)'
$NOISE = '("subject matter expert" OR "subject matter experts" OR "shape memory" OR "standard molar enthalpy")'
$DT  = '("digital transformation" OR digitalization OR digitalisation OR "digital maturity" OR "industry 4.0")'
$RES = '(resilience OR resilient OR "business continuity" OR crisis OR COVID-19 OR pandemic OR disruption)'
$CORE = "$AI AND $SME NOT $NOISE"
# OpenAlex API kljuc (neobavezno): postavite varijablu okruzenja OPENALEX_API_KEY
$KEY = ''; if ($env:OPENALEX_API_KEY) { $KEY = '&api_key=' + $env:OPENALEX_API_KEY }
$MAIL = if ($env:OPENALEX_MAIL) { $env:OPENALEX_MAIL } else { 'you@example.org' }
$FILT = ',type:article|review,is_retracted:false'
