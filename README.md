# WikiTrends
**(almost)Live updates on the trending Wikipedia articles**

<img width="1401" height="764" alt="image" src="https://github.com/user-attachments/assets/8714e94b-3869-4f3e-b7d8-b705782950fe" />

### Why?
Well, first of all, why not?

But really, why? Because deep inside we all are wiki nerds a little bit.\
I made this so i can collect the trending articles from the Wikipedia most visited ones, analyze them and predict what's gonna be trending later on.
But I didn't wanna do that by myself every single day, so here it is.

**Features:**\
Well, it's almost entirely modular, meaning you can just grab a piece of my code (e.g. the wiki_analysis library, and use it in your own code to grab cool data from wikipedia.
It's analyzed by a Deepseek v3.1-671b model (or any of your choice), which provides in depth analysis and then makes it short and readable so that you can absorb it.\
\
You can check the results either via the web page, or by subscribing to the Telegram bot that will send you a brief explanation of what's going on/trending these days.\
<img width="462" height="214" alt="image" src="https://github.com/user-attachments/assets/8d9a27ab-d813-4e45-aca1-25e26ecd330c" />

# Demo
My demo is currently under the testers' reviewing process, and will be available asap.

# Installation (self-host)

First thing to do, install python if you haven't already. I recommend python 3.13 for best compatibility.\
I'll follow the entire process by uing PyEnv ([Guide here](https://github.com/pyenv/pyenv))\
```
pyenv install 3.13.12
```
Use a virtual environment if you have other python versions already installed:
```
pyenv virtualenv 3.13.12 wikitrends
```

and make it the default venv for the project (clone the repo first):
```
cd wikitrends
pyenv local wikitrends
```
if needed restart your shell and reopen the directory to activate it.

Set your .env file this way:
```
OLLAMA_API_KEY = "your_api_key"
TG_API_ID = your_id
TG_API_HASH = "your_hash"
BOT_TOKEN = "your:token"
```
> Note: you can either download Ollama and keep it open (no api key needed, just edit the BASE_URL in main.py to http://localhost:11434/)
> Or get your cloud API key from the [Ollama website](https://ollama.com/settings/keys) to use the cloud models as i did without downloading any client.

Now install the requirements and you're ready to go:
```
pip install -r requirements.txt
python main.py
```

**That should be it! Hope you enjoy**

## Credits
@gvrz on HackClub's Slack workspace, made for FlavorTown YSWS <3
