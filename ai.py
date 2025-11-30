import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from config import settings

client = OpenAI(api_key = settings.OPENAI_API_KEY)

resume_eval_prompt = """
You are an expert hiring screener. Given the candidate resume text and a job description, evaluate candidate's fit.

Inputs (do not invent facts):
- RESUME_TEXT: {0}
- JOB_DESC: {1}

Return a JSON object with these fields:
{
  "overall_score": integer 0-100,  
  "strengths": [strings],         // 3 most important strengths
  "gaps": [strings],              // 3 main gaps or risks
  "match_by_section": {           // short mapping of job sections to match info
    "required_skills": "match summary",
    "experience_years": "match summary",
    "education": "match summary"
  },
  "rewrite_snippet": "one paragraph resume intro tailored to the job (50-70 words)",
  "actionable_recommendations": [strings]  // 3-5 concrete edits or next steps
}

Be concise. Use the resume text only for facts; do not hallucinate experience or dates. If the resume is very long, summarize conservatively.
"""


def build_system_and_user_messages(resume_text: str, job_desc: str):
    prompt = resume_eval_prompt.replace("{0}", resume_text).replace("{1}", job_desc)
    return [
        {"role": "system", "content": "You are a helpful, neutral, accurate recruiter assistant."},
        {"role": "user", "content": prompt}
    ]

def evaluate_resume_with_ai(resume_text: str, 
                            job_desc: str, 
                            model="gpt-4o-mini", temperature=0):
    messages = build_system_and_user_messages(resume_text, job_desc)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1000
    )
    return json.loads(resp.choices[0].message.content.strip())

class ReviewedApplication(BaseModel):
   revised_description: str
   overall_summary: str

class JDAnalysis(BaseModel):
    unclear_sections: List[str]
    jargon_terms: List[str]
    biased_language: List[str]
    missing_information: List[str]
    overall_summary: str

ANALYSIS_SYSTEM_PROMPT = """
You are an expert HR job description analyst specializing in inclusive hiring practices.

Analyze the provided job description for potential issues across these dimensions:

1. CLARITY: Identify sections with vague responsibilities, unclear expectations, or ambiguous requirements.
   Flag phrases like "various duties," "other tasks as assigned," or undefined acronyms.

2. JARGON: Flag unnecessarily technical language inappropriate for the role level.
   Consider whether terms would be understood by qualified candidates unfamiliar with internal terminology.

3. BIAS: Identify language that may discourage diverse candidates:
   - Gender-coded words (e.g., "rockstar," "ninja," "aggressive," "nurturing")
   - Age bias (e.g., "digital native," "recent graduate")
   - Exclusionary phrases (e.g., "culture fit," "work hard/play hard")
   - Excessive requirements (unnecessarily requiring degrees or years of experience)

4. MISSING INFORMATION: Note absent critical details:
   - Salary range or compensation structure
   - Work location/arrangement (remote/hybrid/onsite)
   - Reporting structure or team context
   - Clear distinction between required vs. preferred qualifications
   - Application process and timeline
   - Growth/development opportunities

5. SUMMARY: Provide 2-3 sentences describing overall quality and primary concerns.

For each issue you identify:
- Quote the exact problematic text
- Explain why it is problematic
- Suggest an improvement (when applicable)

Your output MUST be valid JSON that conforms exactly to the provided schema.
Do not include any text outside the JSON.

If information is missing, return empty arrays.
"""

ANALYSIS_USER_PROMPT = """
Analyze the following job description:

--- JOB DESCRIPTION ---
{job_description}
----------------------

Return only JSON.
"""

def review_application(job_description: str) -> ReviewedApplication:
    analysis_parser = PydanticOutputParser(pydantic_object=JDAnalysis)
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYSIS_SYSTEM_PROMPT),
        ("human", ANALYSIS_USER_PROMPT + "\n\n{format_instructions}"),
    ]).partial(format_instructions=analysis_parser.get_format_instructions())
    llm = ChatOpenAI(model="gpt-5.1", temperature=0, api_key=settings.OPENAI_API_KEY)

    analysis_chain = analysis_prompt | llm | analysis_parser
    analysis = analysis_chain.invoke({"job_description": job_description})
    revised_description = job_description
    overall_summary = analysis.overall_summary
    return ReviewedApplication(revised_description=revised_description, overall_summary=overall_summary)