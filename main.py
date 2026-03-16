from wiki_analysis import *
import datetime
import telebot

MODEL = "ollama:deepseek-v3.1:671b-cloud"
TEMPERATURE = 1
BASE_URL = "http://localhost:11434/"

yesterday = datetime.date.today() - datetime.timedelta(days=1)
wanted_date = yesterday.strftime('%Y/%m/%d')

url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/" + wanted_date

llm = define_llm(MODEL, TEMPERATURE, API_KEY, BASE_URL)

history = read_memory()

raw_stats = collect_data(url)
clean_stats = filter_data(raw_stats)

analysis_text = invoke_analysis(clean_stats, history, llm)

save_to_memory(analysis_text, clean_stats)

