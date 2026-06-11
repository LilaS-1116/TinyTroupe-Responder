from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from form_parser import parse_google_form, submit_google_form
from troupe_agent import answer_form_questions
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Google Form TinyTroupe Responder")

# Mount the static files directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

from typing import List

class PersonaGroup(BaseModel):
    description: str = ""
    count: int = 1

class FormRequest(BaseModel):
    url: str
    personas: List[PersonaGroup]

async def process_bulk_submissions(resolved_url: str, questions: list, personas: List[PersonaGroup]):
    async def process_single(persona_desc: str, index: int):
        try:
            results = await asyncio.to_thread(answer_form_questions, questions, persona_desc, index)
            await asyncio.to_thread(submit_google_form, resolved_url, results)
            print(f"Successfully processed bulk submission for persona '{persona_desc[:10]}...' (Index {index})")
        except Exception as e:
            print(f"Bulk submission failed for persona '{persona_desc[:10]}...' (Index {index}): {e}")

    # Collect all tasks across all personas
    tasks = []
    global_index = 1
    for p in personas:
        for _ in range(p.count):
            tasks.append(process_single(p.description, global_index))
            global_index += 1
            
    # Use asyncio.gather to run them all concurrently in the background
    await asyncio.gather(*tasks)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/process-form")
async def process_form(request: FormRequest, background_tasks: BackgroundTasks):
    try:
        # 1. Parse the Google Form
        form_data = parse_google_form(request.url)
        
        # 2. Extract Questions
        questions = form_data.get("questions", [])
        if not questions:
            return {"form_title": form_data.get("title"), "results": [], "message": "No input questions found on this form."}
        
        resolved_url = form_data.get("resolved_url", request.url)
        
        # Calculate total count requested
        total_count = sum(p.count for p in request.personas)
        
        if total_count > 100:
            raise ValueError("The maximum allowed number of overall submissions is 100.")
        
        # Handle Bulk Processing
        if total_count > 1:
            background_tasks.add_task(process_bulk_submissions, resolved_url, questions, request.personas)
            return {
                "form_title": form_data.get("title", "Unknown Form"),
                "form_description": form_data.get("description", ""),
                "status": "processing",
                "message": f"Bulk submission started. Generating and submitting {total_count} unique responses across {len(request.personas)} persona groups concurrently in the background."
            }

        # Single Processing (Wait for result)
        persona_desc = request.personas[0].description if request.personas else ""
        results = await asyncio.to_thread(answer_form_questions, questions, persona_desc, 0)
        
        # 3. Auto-submit the form
        try:
            await asyncio.to_thread(submit_google_form, resolved_url, results)
            submitted = True
        except Exception as e:
            print(f"Submission error: {e}")
            submitted = False
        
        return {
            "form_title": form_data.get("title", "Unknown Form"),
            "form_description": form_data.get("description", ""),
            "results": results,
            "submitted": submitted
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
