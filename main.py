from wiki_analysis import *
from telegram_daily import notify
import os
import datetime
import file_actions
import dotenv
import web_serve

dotenv.load_dotenv()
API_KEY = os.getenv("OLLAMA_API_KEY")
if API_KEY:
    print("Key loaded successfully!")
else:
    print("Did you put your api key in the .env?")


# LLM settings
MODEL = "ollama:deepseek-v3.1:671b-cloud"
TEMPERATURE = 1
BASE_URL = "https://ollama.com/"
llm = define_llm(MODEL, TEMPERATURE, API_KEY, BASE_URL)
print("Set LLM settings")

# Date and url settings
yesterday = datetime.date.today() - datetime.timedelta(days=1)
before_yesterday = datetime.date.today() - datetime.timedelta(days=2)
wanted_date = yesterday.strftime('%Y/%m/%d')
url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/" + wanted_date

print("Set date and url settings")


# Move old output to archive
file_actions.move_file("analysis_output.html", "outputs/analysis_output_" + before_yesterday.strftime('%Y-%m-%d') + ".html")
print("Old outpud moved")

# Analysis
history = read_memory()
raw_stats = collect_data(url)
clean_stats = filter_data(raw_stats)
analysis_text = invoke_analysis(clean_stats, history, llm)
save_to_memory(analysis_text, clean_stats)
print("Analysis complete")


### Notifications and apps part

# copy output to web server
file_actions.copy_file("analysis_output.html", "templates/short.html")
print("Output copied to frontend")

# notify via telegram
with open("analysis_output.html", "r") as f:
    html_content = f.read()

message = gen_telegram_msg(html_content, llm)
notify(message)
print("Message sent")

with open("templates/index.html", "w") as indexfile:
    indexfile.write(gen_index(analysis_text, llm))

web_serve.run_server(port=1149)