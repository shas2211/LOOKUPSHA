import streamlit as st
import os
from dotenv import load_dotenv
import utils

# Load environment variables from .env if present
# Forced update: 2026-02-27 00:46
load_dotenv(override=True)

# Page Config
st.set_page_config(page_title="LOOKUPSHA", layout="centered")

# Custom CSS for Minimalist B&W Aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap');

    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput > div > div > input {
        border-radius: 0px;
        border: none;
        border-bottom: 2px solid #000000;
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        padding: 10px 0px;
        background: transparent;
        box-shadow: none !important;
    }
    .stTextInput > div > div > input:focus {
        border-bottom: 2px solid #000000;
    }
    .stButton > button {
        border-radius: 0px;
        background-color: #000000;
        color: #FFFFFF;
        border: none;
        width: 100%;
        font-family: 'Inter', sans-serif;
        letter-spacing: 2px;
        font-size: 12px;
        padding: 10px;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background-color: #333333;
        color: #FFFFFF;
    }
    h1 {
        font-family: 'Playfair Display', serif;
        font-size: 60px !important;
        letter-spacing: 4px;
        font-weight: 700;
    }
    h2, h3 {
        font-family: 'Playfair Display', serif;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    hr {
        border-color: #000000;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Centered Title and Caption for a premium feel
    st.title("LOOKUPSHA")
    st.caption("SEARCH ANYTHING. GET DEPTH. GET PDF.")

    st.write("")

    # Main search bar - the core interaction
    query = st.text_input("Search Query", placeholder="What do you want to learn about today?", label_visibility="collapsed", key="search_query")

    if query:
        with st.spinner("RESEARCHING..."):
            # Intelligent depth control: if query is long, assume the user wants a deep dive
            depth = "DEEP" if len(query) > 25 else "SIMPLE"
            result = utils.search_internet(query, depth)

            # --- DISPLAY RESULTS ---
            st.divider()
            st.subheader(f"{depth} ANALYSIS")
            st.markdown(f"### {query.upper()}")
            st.write(result['text'])

            # Display the relevant visual if found
            if result.get('image'):
                st.image(result['image'], use_column_width=True, caption=f"Visual context for '{query}'")

            # --- PDF & EMAIL ACTION ---
            st.divider()
            st.subheader("GET YOUR REPORT")
            st.write("Download the PDF directly or have it delivered to your inbox via Gmail.")

            # 1. Generate PDF (we do this once so it's ready for both download and email)
            pdf_path = utils.generate_pdf(query, result['text'])
            
            # 2. Download Button (Instant gratification)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 DOWNLOAD PDF REPORT",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )

            st.write("") # Spacing

            # 3. Email Delivery (For later reference)
            col1, col2 = st.columns([3, 1])
            with col1:
                email = st.text_input("Email", placeholder="friend@example.com", key="email_input")
            with col2:
                st.write("") # Alignment
                if st.button("SEND PDF", key="send_button"):
                    # Use getattr to avoid 'AttributeError' if the cloud app is still reloading the utils module
                    sender = getattr(utils, 'EMAIL_SENDER', None)
                    password = getattr(utils, 'EMAIL_PASSWORD', None)

                    if not sender or not password:
                        st.error("Email service not initialized. If you just updated your Secrets, please wait 30 seconds and refresh the page.")
                    elif email:
                        with st.spinner("SENDING VIA GMAIL..."):
                            success, error_msg = utils.send_email(email, pdf_path)
                            if success:
                                st.success("SENT ✓ Anyone can receive this now!")
                            else:
                                st.error(f"FAILED: {error_msg}")
                    else:
                        st.warning("Please enter a valid email address.")

if __name__ == "__main__":
    main()
