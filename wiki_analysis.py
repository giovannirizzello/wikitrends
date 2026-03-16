import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from IPython.display import Markdown, display
from pathlib import Path
from fpdf import FPDF

# LOAD API KEY
load_dotenv()
API_KEY = os.getenv("API_KEY")
if API_KEY:
    print("Key loaded successfully!")
else:
    print("Did you put your api key in the .env?")


#DEFINE LLM MODEL and API
def define_llm(model_name, temperature, api_key, base_url):
    return init_chat_model(model_name, temperature=temperature, api_key=api_key, base_url=base_url)

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
        return history # This is now a list of your previous interactions
    else:
        # Create the file if it doesn't exist
        with open('memory.json', 'w') as fp:
            pass 
        return []

def collect_data(data_url):
    # Set the mandatory User-Agent for wikimedia API
    headers = {
        'User-Agent': 'WikiTrends/0.1 (mailto:giovannirizzello09@proton.me)'
    }
    
    try:
        # Pass headers into the get request
        r = requests.get(data_url, headers=headers)
        r.raise_for_status() 
        
        return r.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def filter_data(data):
    exclude_list = ["Main_Page", "Special:Search"]

    original_articles = data['items'][0]['articles']

    filtered_articles = [
        item for item in original_articles 
        if item['article'] not in exclude_list
    ]

    for index, item in enumerate(filtered_articles, start=1):
        item['rank'] = index

    data['items'][0]['articles'] = filtered_articles
    print(f"Filtering complete. Removed {len(original_articles) - len(filtered_articles)} entries.")

    return data

formato_memoria = "Previous statistics and trends: {statistics} - Previous analysis and prediction: {analysis}"
formato_prompt = """
PROMPT\n
Analyze this data, list the top 5 articles of the day, predict next day trends, and use memory to analyze trends over time. Reply shortly.\n

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
def invoke_analysis(statistics, memory_list, llm):
    memory_string = ""
    if isinstance(memory_list, list):
        recent_memory = memory_list[-5:] 
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
        statistics=json.dumps(statistics, indent=2),
        memory=memory_string
    )

    response = llm.invoke(prompt)
    with open("analysis_output.md", "w", encoding="utf-8") as md_file:
        md_file.write(response.content)
    return response.content

def save_to_memory(analysis_text, statistics):
    new_entry = {
        "timestamp": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        "statistics": statistics, 
        "analysis": analysis_text 
    }


    with open("memory.json", "a") as f:
        f.write(json.dumps(new_entry) + "\n")

def save_prompt():
    with open("prompt_test.txt", "w") as f:
        f.write(prompt)

def save_pdf(md_file):
    with open(md_file, "r", encoding="utf-8") as f:
        text = f.read()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.multi_cell(0, 10, txt=text)
    
    pdf.output("analysis_output.pdf")

def run_analysis():
    read_memory()
    collect_data()
    filter_data()
    analysis_result = invoke_analysis()
    save_to_memory(analysis_result)
    save_prompt()
    save_pdf()

if __name__ == "__main__":
    run_analysis()