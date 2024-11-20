# WhatsApp Chat Analyzer

A modern dashboard for analyzing WhatsApp chat data with beautiful visualizations.

## Features

- 📊 Interactive visualizations using Plotly
- 🌙 Modern dark theme interface
- 📱 Message type analysis
- 👥 User activity tracking
- 📈 Time-based analysis
- 🕒 Hourly chat patterns

## Setup

1. Clone the repository:
```bash
git clone https://github.com/keemsmile/alumni.git
cd alumni
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

## How to Use

1. Export your WhatsApp chat:
   - Open WhatsApp
   - Go to the chat/group you want to analyze
   - Click More options (⋮) > More > Export chat
   - Choose "Without media"
   - Save the exported file as `_chat.txt` in the project directory

2. Run the dashboard:
```bash
streamlit run chat_dashboard.py
```

> **Note:** For privacy reasons, the `_chat.txt` file is not included in the repository. Each user needs to provide their own chat export file to analyze.

## Components

- `chat_parser.py`: Core chat parsing functionality
- `chat_dashboard.py`: Streamlit dashboard interface
- `parse_chat.py`: Chat processing script

## Privacy

- The chat data (`_chat.txt`) is processed locally on your machine
- No chat data is uploaded or shared
- The file is excluded from git via `.gitignore`

## Screenshots

(Add screenshots of your dashboard here)
