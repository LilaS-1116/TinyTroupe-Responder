import os
import json

try:
    from tinytroupe.agent import TinyPerson
    import tinytroupe
except ImportError:
    TinyPerson = None

import openai

def answer_form_questions(questions_list, persona_desc="", iteration=0):
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set. TinyTroupe requires it to function.")
        
    background = persona_desc.strip() if persona_desc else "You are an average internet user, filling out a Google Form. You provide concise, realistic, and human-like answers."
    
    # Add iteration to introduce variability for bulk submissions
    if iteration > 0:
        background += f" For context, you are respondent #{iteration}. Try to vary your answers slightly from what a generic average user might say so that your answers are unique."
        
    results = []
    
    # --- FALLBACK: If tinytroupe is not available (e.g. on Vercel due to 250MB limit) ---
    if TinyPerson is None:
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # We maintain conversation history for context just like TinyTroupe does
        messages = [
            {"role": "system", "content": background}
        ]
        
        for q in questions_list:
            question_text = q['title']
            prompt = f"Please answer the following form question: '{question_text}'. If options are provided, you MUST exactly match one of the options character-by-character without any trailing periods. Just provide the final answer text without any conversational filler."
            messages.append({"role": "user", "content": prompt})
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # or standard gpt-4
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                answer_text = response.choices[0].message.content.strip(' "\'.')
                messages.append({"role": "assistant", "content": answer_text})
            except Exception as e:
                answer_text = "No response generated."
                
            results.append({
                "id": q["id"],
                "title": question_text,
                "answer": answer_text
            })
            
        return results
        
    # --- ORIGINAL TINYTROUPE LOGIC ---
    person = TinyPerson(f"FormResponder_{iteration}")
    person.define("background", background)
    
    for q in questions_list:
        question_text = q['title']
        prompt = f"Please answer the following form question: '{question_text}'. If options are provided, you MUST exactly match one of the options character-by-character without any trailing periods. Just provide the final answer text without any conversational filler."
        
        person.listen(prompt)
        actions = person.act(return_actions=True)
        
        # Try to extract the speech/text from the actions
        answer_text = "No response generated."
        
        if actions:
            # Depending on the tinytroupe version, it could be a list of dicts or objects
            for action in actions:
                # Common pattern in tinytroupe for speech action
                if isinstance(action, dict):
                    action_type = action.get("action", {}).get("type") or action.get("type")
                    if action_type == "TALK":
                        answer_text = action.get("action", {}).get("content") or action.get("content", answer_text)
                else:
                    # Object attribute access
                    try:
                        if hasattr(action, 'action') and hasattr(action.action, 'type') and action.action.type == 'TALK':
                            answer_text = action.action.content
                        elif hasattr(action, 'type') and action.type == 'TALK':
                            answer_text = action.content
                    except Exception:
                        pass
        
        # Cleanup potential surrounding quotes and trailing periods
        answer_text = answer_text.strip(' "\'.')
        
        results.append({
            "id": q["id"],
            "title": question_text,
            "answer": answer_text
        })
        
    return results
