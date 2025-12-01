# Lab 2: AI Review (Backend)

In this lab, we will build a backend API that will take a job description and return a review of the job description

First, install all the needed dependencies from terminal:

Update `requirements.txt` with this

```
langchain==1.1.0 # Langchain framework
langchain-openai==1.1.0 # Langchain Open AI interface
```

Then install dependencies

Mac:
```
> source ./.venv/bin/activate
> pip install -r requirements.txt
```

Windows:
```
> .\.venv\Scripts\activate
> pip install -r requirements.txt
```

Here are the steps to complete the lab:

1. In `main.py` create an API endpoint `api_create_job_post` for this feature
    * Path should be `/api/review-job-description`
    * Method type `POST`
    * It takes a single `str` field called `description`
    * It should call a function `review_application` from the `ai.py` file and pass the description
    * Return the result
2. In `ai.py` create the function `review_application`
    * It should take `job_description` as input
    * It should return a `ReviewedApplication` object (see below)
3. The `review_application` function will use `gpt-5.1` model to pass in the `job_description` to the LLM and get any problems in the job description.

This is the structure of `ReviewedApplication`. Create this in `ai.py`

```python
class ReviewedApplication(BaseModel):
    overall_summary: str
```

## Design

There are many ways to code this. I am using the following overall design for this feature.

The whole feature will be a 3 step process:

1. Prompt the LLM to review the given job description and find out what are the problems with it. This will be a detailed prompt, because we will need information for step 2 & 3. In this step I want the LLM to return structured output in JSON so that I can use it in step 2
2. Use the problems detected in step 1, and ask the LLM to rewrite the problem parts of the job description individually
3. Take the individual parts that have been rewritten and modify the original job description with the fixes

In this lab, we are only going to implement part 1

## High level approach

1. Create the endpoint. Create `ReviewdApplication` class. Make endpoint return "Hello world" for `overall_summary`. Test with Bruno
1. Create function `review_application` in `ai.py`. Move `ReviewedApplication` class to `ai.py`. Make the new function return "Hello world" for `overall_summary`. Change endpoint to call this function. Test with Bruno
1. Use ChatGPT metaprompting to explore ways to create a good prompt to review the job description. 
1. Test different prompts within chatgpt. Use this job description as a test case: 

```
We’re seeking a Forward Deployed Engineer. We want someone with 3+ years of software engineering experience with production systems. They should be rockstar programmers and problem solvers. They should have experience in a customer-facing technical role with a background in systems integration or professional services
```
1. Once you have got a good prompt template, modify `review_application` function to use langchain to pass the job description to the LLM and get the output. Test with Bruno

(Check Hints section to see the prompt that I am using, the instructions in the hints will use this structure)

## Hints

### What LLM prompt should I use?

<details>
<summary>Answer</summary>

This is the prompt that I will use in the lab

```python
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

{format_instructions}
"""
```
</details>

### What kind of output format should I have?

<details>
<summary>Answer</summary>

Matching my prompt is this output format

```python
class JDAnalysis(BaseModel):
    unclear_sections: List[str]
    jargon_terms: List[str]
    biased_language: List[str]
    missing_information: List[str]
    overall_summary: str
```
</details>

### How to create the dummy endpoint?

<details>
<summary>Answer</summary>

Add this code in `main.py`

```python
class JobDescriptionForm(BaseModel):
   description: str

class ReviewedApplication(BaseModel):
    overall_summary: str

@app.post("/api/review-job-description")
async def api_create_job_post(job_post_form: Annotated[JobDescriptionForm, Form()]):
   reviewed_application = ReviewedApplication(overall_summary="Hello World")
   return reviewed_application
```
</details>

### How to create the dummy review_application?

<details>
<summary>Answer</summary>

Add this in `ai.py`

```python
class ReviewedApplication(BaseModel):
    overall_summary: str

def review_application(job_description: str) -> ReviewedApplication:
    return ReviewedApplication(overall_summary="Hello World")
```
</details>

### How to create the real endpoint?

<details>
<summary>Answer</summary>

Delete `ReviewedApplication` class. Update the endpoint like this

```python
@app.post("/api/review-job-description")
async def api_create_job_post(job_post_form: Annotated[JobDescriptionForm, Form()]):
   reviewed_application = review_application(job_post_form.description)
   return reviewed_application
```

Don't forget to import `review_application` on the top
</details>

### How to call the LLM with langchain?

<details>
<summary>Answer</summary>

First import these at the top

```python
from typing import List, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
```

Then create a chain like this:

```
Chat Prompt Template --> LLM --> Output parser
```

Chat prompt template should have two messages:
* System prompt
* User message

System prompt should contain the system prompt. User message will have the job description.

LLM should be configured for `gpt-5.1`, temperature 0

Output parser should be `PydanticOutputParser` configured for `JDAnalysis` mentioned in Hint 2
</details>

### I need help with the output parser

<details>
<summary>Answer</summary>

```python
analysis_parser = PydanticOutputParser(pydantic_object=JDAnalysis)
```

See Hint 2 for how to create `JDAnalysis` if you haven't already created it
</details>

### I need help with the LLM component

<details>
<summary>Answer</summary>

```python
llm = ChatOpenAI(model="gpt-5.1", temperature=0, api_key=settings.OPENAI_API_KEY)
```
</details>

### I need help with the Chat Prompt Template

<details>
<summary>Answer</summary>

```python
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYSIS_SYSTEM_PROMPT),
        ("human", ANALYSIS_USER_PROMPT),
    ]).partial(format_instructions=analysis_parser.get_format_instructions())
```
</details>

### Show me how to integrate all the langchain components

<details>
<summary>Answer</summary>

```python
def review_application(job_description: str) -> ReviewedApplication:
    llm = ChatOpenAI(model="gpt-5.1", temperature=0, api_key=settings.OPENAI_API_KEY)

    analysis_parser = PydanticOutputParser(pydantic_object=JDAnalysis)
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYSIS_SYSTEM_PROMPT),
        ("human", ANALYSIS_USER_PROMPT),
    ]).partial(format_instructions=analysis_parser.get_format_instructions())
    analysis_chain = analysis_prompt | llm | analysis_parser
    analysis = analysis_chain.invoke({"job_description": job_description})

    overall_summary = analysis.overall_summary
    return ReviewedApplication(overall_summary=overall_summary)
```
</details>

## Discussion Questions

1. Why do a 3 part prompting? Why not do everything in a single prompt?
1. Why is the system prompt so huge?