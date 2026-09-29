# eMAG Price Tracker

An automated price-tracking pipeline that monitors product prices and voucher discounts on eMAG, stores tracking history, delivers notifications on price drops, and presents live product metrics through a web dashboard.

## Overview

The scraper extracts current listing prices and applicable promotional voucher discounts from targeted product pages. It records price states inside a local data file to establish baselines and detect changes over time. When a genuine price decrease occurs, an alert is dispatched via Telegram.

Automation runs through GitHub Actions on a scheduled cron workflow, executing checks autonomously and writing state updates back to the repository. The resulting dataset feeds directly into an interactive Streamlit application deployed to the web, displaying high-level summary metrics, direct store links, and individual product cards.

## Tech Stack

Python handles page scraping and data parsing using Requests and BeautifulSoup. Data manipulation and metric aggregation run on Pandas. The frontend interface is built with Streamlit. Background scheduling, secret storage, and repository commits are orchestrated through GitHub Actions.

## Setup and Local Execution

Clone the repository and install the dependencies from requirements.txt:

pip install -r requirements.txt

Create a .env file in the root directory containing your Telegram bot token and chat identification credentials:

TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

Run the price scraper manually:

python main.py

Launch the local web dashboard:

streamlit run dashboard.py
