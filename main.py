import os
import json
import telebot
import requests
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from IPython.display import Markdown, display
from pathlib import Path
from fpdf import FPDF

prompt = ""

# DEFAULT VALUES
default_time = "daily"
data_date = datetime.today().strftime('%Y-%m-%d')
data_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/2026/03/04"

# LOAD API KEY
load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY:
    print("Key loaded successfully!")
else:
    print("Did you put your api key in the .env?")


#DEFINE LLM MODEL and API
MODEL = "ollama:deepseek-v3.1:671b-cloud"
TEMPERATURE = 1
BASE_URL = "http://localhost:11434/"

llm = init_chat_model(MODEL, temperature = TEMPERATURE, api_key = API_KEY, base_url = BASE_URL)


# MEMORY AND DATA COLLECTION
memory = ""
statistics = ""

def read_memory():
    global memory
    memory_path = Path('memory.json')
    history = [] # Temporary list to store entries
    
    if memory_path.is_file():
        with open("memory.json", "r") as f:
            for line in f:
                if line.strip(): # Skip empty lines
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue # Skip lines that got corrupted previously
        memory = history # This is now a list of your previous interactions
    else:
        # Create the file if it doesn't exist
        with open('memory.json', 'w') as fp:
            pass 
        memory = []

def collect_data():
    global statistics
    global data_url

    # 1. Set the mandatory User-Agent for wikimedia API
    headers = {
        'User-Agent': 'WikiTrends/0.1 (mailto:giovannirizzello09@proton.me)'
    }
    
    try:
        # 2. Pass headers into the get request
        r = requests.get(data_url, headers=headers)
        r.raise_for_status() 
        
        statistics = r.json()
        
        with open("data.json", "w") as f:
            json.dump(statistics, f, indent=4)
            
        print("Data successfully saved to data.json")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def filter_data():
    global statistics
    with open("data.json", "r") as f:
        data = json.load(f)
    exclude_list = ["Main_Page", "Special:Search"]

    original_articles = data['items'][0]['articles']

    filtered_articles = [
        item for item in original_articles 
        if item['article'] not in exclude_list
    ]

    for index, item in enumerate(filtered_articles, start=1):
        item['rank'] = index

    data['items'][0]['articles'] = filtered_articles

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    statistics = data

    print(f"Filtering complete. Removed {len(original_articles) - len(filtered_articles)} entries.")

formato_memoria = "Previous statistics and trends: {statistics} - Previous analysis and prediction: {analysis}"
formato_prompt = """
PROMPT\n
{question}\n

reply to the user's prompt exclusively if the topic is wikipedia top articles, analysys and prediction of them, and anything related to those.

INSTRUCTIONS\n
the response MUST be in markdown. no json or html, ONLY MARKDOWN.\n

DATA\n
This is the latest statistics and data.\n
{statistics}\n

MEMORY
These (MEMORY) are the previous trending articles with their corresponding dates, and previous analysis, use them for more in depth analysis:\n
{memory}
"""
def invoke_analysis():
    global prompt
    global memory
    question = "Analyze this data, list the top 5 articles of the day, predict next day trends, and use memory to analyze trends over time. Reply shortly."

    memory_string = ""
    if isinstance(memory, list):
        recent_memory = memory[-5:] 
        for entry in recent_memory:
            #Get the stats from the entry
            stats = entry.get('statistics', {})
            item = stats.get('items', [{}])[0] # Get the first data item
            
            #date for previous analysis
            date = f'"year": "{item.get("year")}", "month": "{item.get("month")}", "day": "{item.get("day")}"'
            
            items = stats.get('items', []) if isinstance(stats, dict) else []
            if items and isinstance(items[0], dict):
                articles_list = items[0].get('articles', [])
                top_10 = [a.get('article', 'Unknown') for a in articles_list[:10]]
                memory_string += f"- Date: {{{date}}} | Top 10: {', '.join(top_10)}\n"
            else:
                memory_string += f"- Date: {date} | No article data found\n"
    else:
        memory_string = "No previous memory available."

    prompt = formato_prompt.format(
        question=question, 
        statistics=json.dumps(statistics, indent=2),
        memory=memory_string
    )

    response = llm.invoke(prompt)
    with open("analysis_output.md", "w", encoding="utf-8") as md_file:
        md_file.write(response.content)
    return response.content

def save_to_memory(analysis_text):
    global memory
    new_entry = {
        "timestamp": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        "statistics": statistics, 
        "analysis": analysis_text 
    }


    with open("memory.json", "a") as f:
        f.write(json.dumps(new_entry) + "\n")
    
    memory.append(new_entry)

def save_prompt():
    with open("prompt_test.txt", "w") as f:
        f.write(prompt)

def save_pdf():
    with open("analysis_output.md", "r", encoding="utf-8") as f:
        text = f.read()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.multi_cell(0, 10, txt=text)
    
    pdf.output("analysis_output.pdf")
    

read_memory()
collect_data()
filter_data()
analysis_result = invoke_analysis()
save_to_memory(analysis_result)
save_prompt()
save_pdf()