import io
from pypdf import PdfReader
import streamlit as st

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def get_custom_css():
    """Returns the custom CSS for styling the Streamlit app to look premium."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }
    
    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 0.85em;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.375rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .badge-strength {
        background-color: #10b981;
        color: #022c22;
    }
    .badge-missing {
        background-color: #ef4444;
        color: #450a0a;
    }
    .badge-secondary {
        background-color: #f59e0b;
        color: #451a03;
    }
    
    /* Agent Terminal Logs */
    .terminal {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9em;
        color: #38bdf8;
        max-height: 300px;
        overflow-y: auto;
    }
    .terminal-line {
        margin: 5px 0;
    }
    .terminal-timestamp {
        color: #94a3b8;
    }
    .terminal-agent {
        color: #e879f9;
        font-weight: bold;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }
    
    /* Cards */
    div[data-testid="stExpander"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    div[data-testid="stExpander"] summary {
        color: #f8fafc;
    }
    div[data-testid="stExpander"] div[role="region"] {
        color: #cbd5e1;
    }
    </style>
    """

def apply_custom_css():
    st.markdown(get_custom_css(), unsafe_allow_html=True)
