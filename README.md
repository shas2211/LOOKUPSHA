# 🔍 LOOKUPSHA

**Intelligent Research. Deep Analysis. Instant Delivery.**

LOOKUPSHA is a minimalist, high-speed research assistant designed with a strict Black & White aesthetic. It combines real-time internet search with ultra-fast AI synthesis to give you deep insights on any topic, delivered directly to your screen or your inbox.

---

## ✨ Features

- **Real-Time Research**: Powerered by **Tavily AI** for up-to-the-minute web search and image retrieval.
- **Deep Synthesis**: Uses **Groq (Llama 3.3)** for near-instant, insightful analysis.
- **Automated Depth**: The app automatically decides whether to provide a `SIMPLE` summary or a `DEEP` research paper based on your query.
- **PDF Reports**: Generate professional PDF reports of your findings with one click.
- **Email Delivery**: Send your reports directly to your email via **Resend**.
- **Monochrome Aesthetic**: A premium, distraction-free interface built for serious research.

---

## 🚀 Quick Start

### 1. Prerequisites
You will need API keys for the following (all have generous free tiers):
- [Groq](https://console.groq.com/keys) (AI Brain)
- [Tavily](https://app.tavily.com/home) (Internet Search)
- [Resend](https://resend.com/api-keys) (Email Delivery - Optional)

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/yourusername/lookupsha.git
cd lookupsha
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory and add your keys:
```env
TAVILY_API_KEY=your_tavily_key
GROQ_API_KEY=your_groq_key
RESEND_API_KEY=your_resend_key
```

### 4. Run the App
```bash
streamlit run main.py
```

---

## 🛠️ Tech Stack

- **Frontend/UI**: Streamlit (Python-only)
- **Search Engine**: Tavily API
- **AI Engine**: Groq (Llama 3.3-70b-versatile)
- **PDF Engine**: ReportLab
- **Email Engine**: Resend API

---

## 📜 License
MIT License. Feel free to use and modify for your own projects.
