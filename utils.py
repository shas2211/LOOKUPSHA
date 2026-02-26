import os
from tavily import TavilyClient
from groq import Groq
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

import streamlit as st

# --- GLOBAL CONFIGURATION ---
# We look for keys in environment variables (local .env) or Streamlit Secrets (Cloud)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or (st.secrets["TAVILY_API_KEY"] if "TAVILY_API_KEY" in st.secrets else None)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or (st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else None)
RESEND_API_KEY = os.getenv("RESEND_API_KEY") or (st.secrets["RESEND_API_KEY"] if "RESEND_API_KEY" in st.secrets else None)

def search_internet(query, depth):
    """
    Orchestrates the entire research flow:
    1. Fetches real-time web content & images via Tavily.
    2. Synthesizes an intelligent report via Groq.
    """
    if not TAVILY_API_KEY or not GROQ_API_KEY:
        return {
            "text": """
            ### 🛠️ Configuration Required
            It looks like your API keys are missing. 
            
            **Local Users:** Check your `.env` file.
            **Cloud Users:** Add your keys to the **Streamlit Cloud Dashboard** under **Settings > Secrets**:
            ```toml
            TAVILY_API_KEY = "your-key"
            GROQ_API_KEY = "your-key"
            RESEND_API_KEY = "your-key"
            ```
            """,
            "image": None
        }

    # --- 1. RESEARCH PHASE ---
    # Tavily provides advanced search depth to find high-quality information.
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    search_result = tavily.search(query=query, search_depth="advanced" if depth == "DEEP" else "basic", include_images=True)
    
    context = "\n".join([r['content'] for r in search_result['results']])
    
    # Grab the top relevant image to visualize the topic
    images = search_result.get('images', [])
    image_url = images[0] if isinstance(images, list) and len(images) > 0 else None

    # 2. Use Groq (free Llama 3.3) to synthesize the answer
    try:
        client = Groq(api_key=GROQ_API_KEY)
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
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    if not RESEND_API_KEY:
        # Fallback to module variable set by main.py
        import utils
        RESEND_API_KEY = getattr(utils, 'RESEND_API_KEY', None)
        
    if not RESEND_API_KEY:
        return False
    
    import resend
    import base64
    resend.api_key = RESEND_API_KEY
    
    with open(attachment_path, "rb") as f:
        pdf_content = base64.b64encode(f.read()).decode()
    
    params = {
        "from": "LOOKUPSHA <onboarding@resend.dev>",
        "to": [to_email],
        "subject": f"LOOKUPSHA: {os.path.basename(attachment_path)}",
        "html": f"<p>Attached is your research report on <strong>{os.path.basename(attachment_path)}</strong>.</p><p>Sent via LOOKUPSHA.</p>",
        "attachments": [
            {
                "filename": os.path.basename(attachment_path),
                "content": pdf_content,
            }
        ],
    }
    
    try:
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        return False
