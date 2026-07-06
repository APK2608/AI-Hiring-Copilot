import json
import google.generativeai as genai
import datetime

DEFAULT_MODEL = "gemini-2.5-flash"

# Helper to invoke Gemini
def call_agent(model_name: str, system_instruction: str, prompt: str, is_json: bool = False):
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json" if is_json else "text/plain",
            temperature=0.2 if is_json else 0.7
        )
    )
    response = model.generate_content(prompt)
    if is_json:
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback parsing if model returned markdown wrapped json
            cleaned = response.text.strip().removeprefix('```json').removesuffix('```').strip()
            return json.loads(cleaned)
    return response.text

class ResumeParsingAgent:
    def __init__(self):
        self.system_prompt = """
        You are an expert Resume Parsing Agent. Your job is to extract detailed structured information from a raw resume text.
        Extract the following into a valid JSON object:
        - name (string)
        - email (string)
        - phone (string)
        - skills (list of strings)
        - education (list of objects with degree, institution, year)
        - experience (list of objects with title, company, duration, responsibilities(list))
        - certifications (list of strings)
        - projects (list of objects with name, description)
        Ensure the output is ONLY valid JSON.
        """
    def run(self, resume_text: str):
        return call_agent(DEFAULT_MODEL, self.system_prompt, f"Resume Text:\n{resume_text}", is_json=True)

class SkillMatchingAgent:
    def __init__(self):
        self.system_prompt = """
        You are a Skill Matching Agent. Compare the candidate's structured profile with the Job Description.
        Calculate a skill match percentage.
        Identify:
        - strengths (skills from JD that candidate has)
        - missing_skills (skills from JD that candidate lacks)
        - secondary_skills (other skills candidate has not in JD)
        
        Output a valid JSON object:
        {
            "match_score": integer (0-100),
            "strengths": [list of strings],
            "missing_skills": [list of strings],
            "secondary_skills": [list of strings],
            "reasoning": string
        }
        """
    def run(self, candidate_profile: dict, job_description: str):
        prompt = f"Candidate Profile:\n{json.dumps(candidate_profile, indent=2)}\n\nJob Description:\n{job_description}"
        return call_agent(DEFAULT_MODEL, self.system_prompt, prompt, is_json=True)

class CandidateRankingAgent:
    def __init__(self):
        self.system_prompt = """
        You are a Candidate Ranking Agent. Evaluate multiple candidates based on their skill match reports and profiles against the job description.
        Calculate a composite score out of 100 based on:
        - Skill match score (weight: 60%)
        - Experience relevance (weight: 20%)
        - Education (weight: 10%)
        - Certifications (weight: 10%)
        
        Output a valid JSON object which is a list of ranked candidates:
        [
            {
                "candidate_name": string,
                "composite_score": float,
                "ranking_justification": string
            }
        ]
        """
    def run(self, candidates_data: list, job_description: str):
        prompt = f"Job Description:\n{job_description}\n\nCandidates Data:\n{json.dumps(candidates_data, indent=2)}"
        return call_agent(DEFAULT_MODEL, self.system_prompt, prompt, is_json=True)

class InterviewQuestionAgent:
    def __init__(self):
        self.system_prompt = """
        You are an Expert Technical Interviewer Agent.
        Generate 5-8 tailored interview questions (technical and behavioral) based on the candidate's profile, skill match report, and job description.
        Focus heavily on missing skills and weak areas to probe their ability to learn or compensate.
        
        Output format: Markdown format with the question and a brief "What to look for in the answer" guide.
        """
    def run(self, candidate_profile: dict, match_report: dict, job_description: str):
        prompt = f"Candidate Profile:\n{json.dumps(candidate_profile, indent=2)}\n\nMatch Report:\n{json.dumps(match_report, indent=2)}\n\nJob Description:\n{job_description}"
        return call_agent(DEFAULT_MODEL, self.system_prompt, prompt, is_json=False)

class HiringReportAgent:
    def __init__(self):
        self.system_prompt = """
        You are a Senior Technical Recruiter Agent.
        Compile a final executive hiring report for the candidate based on all previous agent analyses.
        Provide a concise markdown report with:
        - Executive Summary
        - Key Strengths
        - Key Risks / Missing Areas
        - Interview Recommendations
        - Final Hiring Recommendation (Strong Hire, Hire, Hold, Reject)
        """
    def run(self, candidate_data: dict, job_description: str):
        prompt = f"Job Description:\n{job_description}\n\nCandidate Complete Data:\n{json.dumps(candidate_data, indent=2)}"
        return call_agent(DEFAULT_MODEL, self.system_prompt, prompt, is_json=False)

def run_hiring_pipeline(resumes_texts: dict, job_description: str, log_callback=None):
    """
    Orchestrates the multi-agent pipeline.
    resumes_texts: dict mapping filename to raw text.
    log_callback: function to send status messages to the UI.
    """
    def log(msg, agent_name="Orchestrator"):
        if log_callback:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_callback(f"<span class='terminal-timestamp'>[{timestamp}]</span> <span class='terminal-agent'>[{agent_name}]</span> {msg}")
    
    log("Starting PulseAgent Hiring Pipeline...")
    
    parsing_agent = ResumeParsingAgent()
    matching_agent = SkillMatchingAgent()
    ranking_agent = CandidateRankingAgent()
    interview_agent = InterviewQuestionAgent()
    report_agent = HiringReportAgent()
    
    processed_candidates = []
    
    for filename, text in resumes_texts.items():
        log(f"Processing resume: {filename}")
        
        # Agent 1: Parse
        log("Extracting structured candidate profile...", "ResumeParsingAgent")
        try:
            profile = parsing_agent.run(text)
            name = profile.get("name", filename)
            log(f"Extracted profile for {name}. Found {len(profile.get('skills', []))} skills.", "ResumeParsingAgent")
        except Exception as e:
            log(f"Failed to parse {filename}: {e}", "ResumeParsingAgent")
            continue
            
        # Agent 2: Match
        log(f"Comparing skills for {name} against Job Description...", "SkillMatchingAgent")
        try:
            match_report = matching_agent.run(profile, job_description)
            log(f"Match complete. Score: {match_report.get('match_score', 0)}%", "SkillMatchingAgent")
        except Exception as e:
            log(f"Failed to match skills for {name}: {e}", "SkillMatchingAgent")
            continue
            
        # Agent 4: Questions
        log(f"Generating tailored interview questions for {name} focusing on missing skills...", "InterviewQuestionAgent")
        try:
            questions = interview_agent.run(profile, match_report, job_description)
            log("Generated interview questions.", "InterviewQuestionAgent")
        except Exception as e:
            log(f"Failed to generate questions: {e}", "InterviewQuestionAgent")
            questions = "Could not generate questions."
            
        # Agent 5: Report
        log(f"Compiling final hiring report for {name}...", "HiringReportAgent")
        candidate_complete_data = {
            "profile": profile,
            "match_report": match_report,
            "interview_questions": questions
        }
        try:
            final_report = report_agent.run(candidate_complete_data, job_description)
            log("Final report generated.", "HiringReportAgent")
        except Exception as e:
            log(f"Failed to generate report: {e}", "HiringReportAgent")
            final_report = "Could not generate final report."
            
        processed_candidates.append({
            "filename": filename,
            "name": name,
            "profile": profile,
            "match_report": match_report,
            "interview_questions": questions,
            "final_report": final_report
        })
    
    # Agent 3: Rank
    log(f"Ranking {len(processed_candidates)} candidates...", "CandidateRankingAgent")
    ranking_input = []
    for c in processed_candidates:
        ranking_input.append({
            "name": c["name"],
            "profile": c["profile"],
            "match_report": c["match_report"]
        })
    
    try:
        rankings = ranking_agent.run(ranking_input, job_description)
        log("Ranking complete.", "CandidateRankingAgent")
        
        # Merge rankings back into processed_candidates
        for c in processed_candidates:
            c["composite_score"] = 0
            c["ranking_justification"] = ""
            for r in rankings:
                if r.get("candidate_name") == c["name"]:
                    c["composite_score"] = r.get("composite_score", 0)
                    c["ranking_justification"] = r.get("ranking_justification", "")
                    
    except Exception as e:
        log(f"Ranking failed: {e}", "CandidateRankingAgent")
        for c in processed_candidates:
            c["composite_score"] = c["match_report"].get("match_score", 0)
            c["ranking_justification"] = "Ranking failed, using raw match score."
            
    # Sort candidates by composite score descending
    processed_candidates.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
    
    log("Pipeline complete.", "Orchestrator")
    return processed_candidates
