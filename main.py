import streamlit as st
import os
from dotenv import load_dotenv
import utils

# Load environment variables from .env if present
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
            st.subheader("LIKE THIS? GET THE PDF.")
            st.write("Enter your email below to receive a professional PDF report of this research.")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                email = st.text_input("Email", placeholder="your@email.com", key="email_input")
            with col2:
                st.write("") # Social spacing to align button
                if st.button("SEND PDF", key="send_button"):
                    if not utils.RESEND_API_KEY:
                        st.error("Email service not configured. Please add your RESEND_API_KEY to the .env file.")
                    elif email:
                        with st.spinner("GENERATING AND SENDING..."):
                            pdf_path = utils.generate_pdf(query, result['text'])
                            success, error_msg = utils.send_email(email, pdf_path)
                            
                            if success:
                                st.success("SENT ✓ Check your inbox!")
                            else:
                                st.error(f"FAILED: {error_msg}")
                    else:
                        st.warning("Please enter a valid email address first.")

if __name__ == "__main__":
    main()
