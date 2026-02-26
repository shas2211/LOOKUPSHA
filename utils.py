import os
from tavily import TavilyClient
from groq import Groq
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

import streamlit as st

# --- GLOBAL CONFIGURATION ---
# We look for keys in environment variables (local .env) or Streamlit Secrets (Cloud)
def get_config(key):
    return os.getenv(key) or st.secrets.get(key)

TAVILY_API_KEY = get_config("TAVILY_API_KEY")
GROQ_API_KEY = get_config("GROQ_API_KEY")
EMAIL_SENDER = get_config("EMAIL_SENDER")
EMAIL_PASSWORD = get_config("EMAIL_PASSWORD")

def search_internet(query, depth):
    # Ensure keys are re-read if they were None/empty on import (Streamlit hot-reload behavior)
    tavily_key = TAVILY_API_KEY or get_config("TAVILY_API_KEY")
    groq_key = GROQ_API_KEY or get_config("GROQ_API_KEY")
    
    if not tavily_key or not groq_key:
        return {
            "text": """
            ### 🛠️ Configuration Required
            It looks like your API keys are missing. 
            
            **Local Users:** Check your `.env` file.
            **Cloud Users:** Add your keys to the **Streamlit Cloud Dashboard** under **Settings > Secrets**:
            ```toml
            TAVILY_API_KEY = "your-key"
            GROQ_API_KEY = "your-key"
            EMAIL_SENDER = "your-gmail@gmail.com"
            EMAIL_PASSWORD = "your-app-password"
            ```
            """,
            "image": None
        }

    # --- 1. RESEARCH PHASE ---
    tavily = TavilyClient(api_key=tavily_key)
    search_result = tavily.search(query=query, search_depth="advanced" if depth == "DEEP" else "basic", include_images=True)
    
    context = "\n".join([r['content'] for r in search_result['results']])
    
    # Grab the top relevant image to visualize the topic
    images = search_result.get('images', [])
    image_url = images[0] if isinstance(images, list) and len(images) > 0 else None

    # 2. Use Groq (free Llama 3.3) to synthesize the answer
    try:
        client = Groq(api_key=groq_key)
        prompt = f"""You are LOOKUPSHA, an intelligent research assistant.
Answer the query: "{query}"
Depth: {depth}

Context from web search:
{context}

Rules:
- SIMPLE: max 3 short paragraphs.
- DEEP: comprehensive with headers and detail.
Style: direct, professional, insightful."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024 if depth == "SIMPLE" else 2048,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"AI synthesis failed: {str(e)}"

    return {
        "text": answer,
        "image": image_url
    }

def generate_pdf(topic, content):
    # Sanitize filename for Windows
    safe_topic = "".join([c if c.isalnum() or c in " _-" else "_" for c in topic])
    filename = f"LOOKUPSHA_{safe_topic.replace(' ', '_')}.pdf"
    c = canvas.Canvas(filename, pagesize=LETTER)
    width, height = LETTER
    
    c.setFont("Times-Bold", 24)
    c.drawString(1*inch, height - 1*inch, "LOOKUPSHA REPORT")
    c.setFont("Times-Roman", 16)
    c.drawString(1*inch, height - 1.5*inch, f"TOPIC: {topic.upper()}")
    
    textobject = c.beginText(1*inch, height - 2*inch)
    textobject.setFont("Times-Roman", 11)
    textobject.setLeading(14)
    
    # Better line wrapping
    max_chars = 95
    import textwrap
    
    for paragraph in content.split('\n'):
        if paragraph.strip():
            wrapped_lines = textwrap.wrap(paragraph, width=max_chars)
            for line in wrapped_lines:
                if textobject.getY() < 1*inch: # New page if needed
                    c.drawText(textobject)
                    c.showPage()
                    textobject = c.beginText(1*inch, height - 1*inch)
                    textobject.setFont("Times-Roman", 11)
                    textobject.setLeading(14)
                textobject.textLine(line)
            textobject.textLine("") # Social spacing
        else:
            textobject.textLine("")

    c.drawText(textobject)
    c.showPage()
    c.save()
    return filename

def send_email(to_email, attachment_path):
    sender = EMAIL_SENDER or get_config("EMAIL_SENDER")
    password = EMAIL_PASSWORD or get_config("EMAIL_PASSWORD")
    
    if not sender or not password:
        return False, "Gmail credentials not found in Secrets/Environment."
    
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    msg = MIMEMultipart()
    msg['From'] = f"LOOKUPSHA <{sender}>"
    msg['To'] = to_email
    msg['Subject'] = f"LOOKUPSHA Report: {os.path.basename(attachment_path)}"

    body = f"Hello,\n\nPlease find attached your research report on {os.path.basename(attachment_path)}.\n\nSent via LOOKUPSHA."
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True, "Success"
    except Exception as e:
        return False, str(e)
