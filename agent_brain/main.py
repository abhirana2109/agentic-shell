import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Configuration
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("FATAL: GEMINI_API_KEY environment variable not set.")
    exit()

app = FastAPI()

# Data Models for Multi-Step Plans
class Step(BaseModel):
    command: str
    explanation: str

class PlanResponse(BaseModel):
    plan: List[Step]

class UserQuery(BaseModel):
    query: str

# AI Logic
generation_config = {"temperature": 0.2, "top_p": 1, "top_k": 1, "max_output_tokens": 2048}
model = genai.GenerativeModel(model_name="gemini-2.5-flash", generation_config=generation_config)

# The Upgraded Multi-Step Prompt
PROMPT_TEMPLATE = """
You are an expert Bash/Zsh command line assistant. Your goal is to understand a user's natural language query and break it down into a sequence of simple, logical, executable commands.

Constraints:
1.  Output Format: You MUST respond with a single, valid JSON object.
2.  JSON Structure: The root JSON object must have a single key: "plan".
3.  Plan Structure: The value of "plan" must be a LIST of JSON objects.
4.  Step Structure: Each object in the "plan" list represents one step and must have two keys:
    - command: A string containing a single, simple shell command.
    - explanation: A brief, one-sentence string explaining what this specific command does.
5.  Simplicity: Prefer simple, atomic commands. Avoid complex chains with && unless absolutely necessary for a single logical operation. For example, instead of 'cd dir && ls', create two separate steps.
6.  No Plan: If the query is not a request for a shell command, return an empty list for the "plan".

Example:
User Query: "go into the 'docs' folder and list its contents"
Your JSON Response:
{{
  "plan": [
    {{
      "command": "cd docs",
      "explanation": "Changes the current directory to 'docs'."
    }},
    {{
      "command": "ls -l",
      "explanation": "Lists the contents of the current directory in a detailed format."
    }}
  ]
}}

User Query:
"{user_query}"

Your JSON Response:
"""

# Updated API Endpoint for Plans
@app.post("/get_plan", response_model=PlanResponse)
async def get_plan(user_query: UserQuery):
    prompt = PROMPT_TEMPLATE.format(user_query=user_query.query)
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        
        parsed_response = PlanResponse.parse_raw(cleaned_response)
        
        if not parsed_response.plan:
             raise ValueError("The generated plan is empty.")
             
        return parsed_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate or parse plan: {e}")