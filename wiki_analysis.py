import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pathlib import Path

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

tg_msg_format = """
rewrite this HTML code i'll give you in the right format for a readable and nice telegram message, content MUST be the same and output MUST NOT contain anything else.

{html_input}

"""

index_page_format = """
Based on the following data, generate a clean HTML <div> containing a summary 
of the top trending Wiki articles and an in depth analysis with prediction of future trends in a separate div under the main one.
Use <h3> for the title and a <ul> for the list. 
Response must contain ONLY the HTML <div> code, nothing else.

DATA SOURCE:
{data_source}
"""

formato_prompt = """
PROMPT\n
Analyze this data, list the top 5 articles of the day, predict next day trends, and use memory to analyze trends over time. Response must be very short and brief, short enough to be shown in an application when the user opens a notification.\n

reply to the user's prompt exclusively if the topic is wikipedia top articles, analysys and prediction of them, and anything related to those.

INSTRUCTIONS\n
the response MUST be in html. titles in <b>, top 5 in a list, prediction in a <p>, use <br> to add a break after each separate thing, for every article name, make it an URL with <a href=""> and this format https://en.wikipedia.org/wiki/(article name that you get from the json data). note that the data is from yesterday, so don't say today. make it user friendly (interesting and appealing to read) no json or markdown, ONLY HTML.\n

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
    with open("analysis_output.html", "w", encoding="utf-8") as md_file:
        md_file.write(response.content)
    return response.content

def gen_telegram_msg(source, llm):
    prompt = tg_msg_format.format(
        html_input = source
    )

    response = llm.invoke(prompt)
    return response.content


def gen_index(source, llm):
    INDEX_SHELL = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiTrends</title>
    <style>
        :root {{
            --primary: #0088cc; /* Telegram Blue */
            --bg: #f4f7f6;
            --text: #333;
            --white: #ffffff;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg);
            margin: 0;
            color: var(--text);
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}

        nav {{
            width: 100%;
            background: var(--white);
            padding: 1rem 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
            margin-bottom: 2rem;
        }}

        nav a {{
            text-decoration: none;
            color: var(--text);
            margin: 0 15px;
            font-weight: 600;
            transition: color 0.3s;
        }}

        nav a:hover {{
            color: var(--primary);
        }}

        .container {{
            width: 90%;
            max-width: 800px;
            background: var(--white);
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}

        h1 {{
            color: var(--primary);
            text-align: center;
            margin-top: 0;
        }}

        /* Styling for the LLM's generated content */
        .analysis-content h3 {{
            border-bottom: 2px solid var(--bg);
            padding-bottom: 10px;
            color: var(--primary);
        }}

        ul {{
            list-style: none;
            padding: 0;
        }}

        li {{
            background: var(--bg);
            margin: 10px 0;
            padding: 12px;
            border-radius: 8px;
            transition: transform 0.2s;
        }}

        li:hover {{
            transform: translateX(5px);
        }}

        a {{
            color: var(--primary);
            text-decoration: none;
        }}

        footer {{
            margin-top: auto;
            padding: 2rem;
            color: #888;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>

    <nav>
        <a href="/">Home</a>
        <a href="/short">Short Version</a>
        <a href="/subscribe">Telegram Bot</a>
    </nav>

    <div class="container">
        <h1>WikiTrends</h1>
        <div class="analysis-content">
            {dynamic_content}
        </div>
    </div>

    <footer>
        &copy; 2026 WikiTrends • Data from Wikipedia API
    </footer>

</body>
</html>
    """


    prompt = index_page_format.format(
        data_source = source
    )

    response = llm.invoke(prompt)
    snippet = response.content

    full_html = INDEX_SHELL.format(dynamic_content=snippet)
    return full_html



def save_to_memory(analysis_text, statistics):
    new_entry = {
        "timestamp": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
        "statistics": statistics, 
        "analysis": analysis_text 
    }


    with open("memory.json", "a") as f:
        f.write(json.dumps(new_entry) + "\n")

def run_analysis():
    read_memory()
    collect_data()
    filter_data()
    analysis_result = invoke_analysis()
    save_to_memory(analysis_result)

if __name__ == "__main__":
    run_analysis()