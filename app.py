import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
from utils import apply_custom_css, extract_text_from_pdf
from agents import run_hiring_pipeline

# Configure page
st.set_page_config(page_title="PulseAgent | Autonomous Hiring", page_icon="🤖", layout="wide")

# Load environment variables (if any)
load_dotenv()

# Apply custom premium styling
apply_custom_css()

# -- Sidebar: Configuration & Info --
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4233/4233830.png", width=60)
    st.title("PulseAgent Settings")
    st.markdown("Configure your Multi-Agent hiring assistant.")
    
    # API Key Configuration
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("🤖 API Key: Configured from environment")
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="Get your key from Google AI Studio. It will not be saved.")
        if api_key:
            genai.configure(api_key=api_key)
    
    st.markdown("---")
    st.markdown("""
    ### Agent Architecture
    1. **Parsing Agent**: Extracts JSON profiles.
    2. **Matching Agent**: Scores skills vs JD.
    3. **Ranking Agent**: Computes composite rank.
    4. **Interview Agent**: Generates custom questions.
    5. **Report Agent**: Compiles executive summary.
    """)

# -- Main Content --
st.title("PulseAgent: Autonomous Multi-Agent Recruitment")
st.markdown("Upload candidate resumes and a job description. The agent swarm will parse, match, rank, and generate tailored reports automatically.")

if not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
    st.stop()

# Inputs
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Job Description")
    job_description = st.text_area("Paste the job description here...", height=250, value="We are looking for a Senior Python Developer with experience in Streamlit, AI/LLMs, and REST APIs. Must have 5+ years of experience and strong problem-solving skills. Knowledge of Google Cloud is a plus.")

with col2:
    st.subheader("2. Candidate Resumes")
    uploaded_files = st.file_uploader("Upload PDF Resumes", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Run Agent Swarm", use_container_width=True, type="primary"):
    if not job_description or not uploaded_files:
        st.error("Please provide both a Job Description and at least one Resume.")
    else:
        # Process files
        resumes_texts = {}
        for file in uploaded_files:
            text = extract_text_from_pdf(file.read())
            if text:
                resumes_texts[file.name] = text
        
        if not resumes_texts:
            st.error("Could not extract text from uploaded resumes.")
            st.stop()
            
        # UI for Terminal logs
        st.markdown("### 🤖 Agent Communication Terminal")
        terminal_container = st.empty()
        
        # We will collect logs to display in the terminal
        logs = []
        def log_callback(msg):
            logs.append(f"<div class='terminal-line'>{msg}</div>")
            # Update terminal live
            terminal_html = f"<div class='terminal'>{''.join(logs)}</div>"
            terminal_container.markdown(terminal_html, unsafe_allow_html=True)
            
        with st.spinner("Agents are collaborating..."):
            try:
                results = run_hiring_pipeline(resumes_texts, job_description, log_callback=log_callback)
            except Exception as e:
                st.error(f"An error occurred during pipeline execution: {e}")
                st.stop()
                
        st.success("Analysis Complete!")
        
        # Results Dashboard
        st.markdown("---")
        st.header("🏆 Candidate Leaderboard")
        
        if results:
            # Create a dataframe for the leaderboard
            df_data = []
            for idx, r in enumerate(results):
                df_data.append({
                    "Rank": idx + 1,
                    "Candidate Name": r.get("name", "Unknown"),
                    "Composite Score": f"{r.get('composite_score', 0)} / 100",
                    "Skill Match": f"{r.get('match_report', {}).get('match_score', 0)}%",
                    "Strengths Found": len(r.get("match_report", {}).get("strengths", [])),
                    "Missing Skills": len(r.get("match_report", {}).get("missing_skills", []))
                })
            df = pd.DataFrame(df_data)
            # Display styled dataframe
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.header("📄 Detailed Candidate Profiles")
            for c in results:
                with st.expander(f"{c['name']} - Score: {c['composite_score']}/100", expanded=False):
                    tab1, tab2, tab3 = st.tabs(["Skill Match", "Interview Questions", "Hiring Report"])
                    
                    with tab1:
                        match = c.get("match_report", {})
                        st.subheader(f"Skill Match: {match.get('match_score', 0)}%")
                        st.markdown("**Justification**: " + match.get("reasoning", ""))
                        
                        st.markdown("#### Strengths")
                        for s in match.get("strengths", []):
                            st.markdown(f"<span class='badge badge-strength'>{s}</span>", unsafe_allow_html=True)
                            
                        st.markdown("#### Missing Skills")
                        for s in match.get("missing_skills", []):
                            st.markdown(f"<span class='badge badge-missing'>{s}</span>", unsafe_allow_html=True)
                            
                        st.markdown("#### Secondary/Other Skills")
                        for s in match.get("secondary_skills", []):
                            st.markdown(f"<span class='badge badge-secondary'>{s}</span>", unsafe_allow_html=True)
                            
                    with tab2:
                        st.markdown(c.get("interview_questions", "No questions generated."))
                        
                    with tab3:
                        st.markdown(c.get("final_report", "No report generated."))
