# PulseAgent: Autonomous Multi-Agent Hiring Assistant

PulseAgent is a modern, Streamlit-based web application that utilizes a swarm of specialized AI agents to automate the recruitment process. Powered by the Google Gemini API, these agents collaborate to parse resumes, match skills against a job description, rank candidates, and generate personalized interview questions and hiring reports.

## Architecture

PulseAgent orchestrates 5 distinct AI agents:
1. **Resume Parsing Agent**: Extracts structured JSON data (skills, education, experience) from raw PDF/Text resumes.
2. **Skill Matching Agent**: Compares candidate skills with the provided job description and calculates a match percentage.
3. **Candidate Ranking Agent**: Evaluates all candidates and assigns a composite score for a ranked leaderboard.
4. **Interview Question Agent**: Generates 5-8 tailored behavioral and technical questions, focusing on the candidate's weak areas.
5. **Hiring Report Agent**: Compiles an executive summary and final hiring recommendation (e.g., Strong Hire, Reject).

## Setup & Installation

1. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Setup**:
   PulseAgent requires a Google Gemini API Key. You can set it in two ways:
   - **Method A (Recommended)**: Create a `.env` file in the root directory and add:
     `GEMINI_API_KEY=your_api_key_here`
   - **Method B (UI)**: Enter the API key directly in the application's sidebar.

   *You can get a free API key from [Google AI Studio](https://aistudio.google.com/).*

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Launch the app using Streamlit.
2. Ensure your Gemini API Key is configured in the sidebar.
3. Paste a target **Job Description** into the designated text area.
4. Upload one or more **PDF Resumes**.
5. Click **Run Agent Swarm**.
6. Watch the agents communicate in real-time in the Agent Terminal, and view the final results in the Leaderboard and Detailed Candidate Profiles.
