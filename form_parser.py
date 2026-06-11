import requests
import json
import re

def parse_google_form(url: str):
    """
    Fetches a Google Form and extracts its questions and corresponding entry IDs.
    Returns a dictionary of the form:
    {
        "title": "Form Title",
        "description": "Form Description",
        "questions": [
            {
                "id": "entry.123456",
                "title": "Question Text",
                "type": "TEXT" # simplified for now
            }
        ]
    }
    """
    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    # Extract the FB_PUBLIC_LOAD_DATA_ JSON
    match = re.search(r'var FB_PUBLIC_LOAD_DATA_ = (.*?);', html, re.DOTALL)
    if not match:
        raise ValueError("Could not find form data in the URL provided.")

    data_str = match.group(1)
    # The JSON string might have some formatting that json.loads doesn't like, but usually it's fine
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse form data.")

    form_title = data[3]
    form_description = data[1][0]
    
    questions = []
    
    # data[1][1] contains the list of form items
    if len(data[1]) > 1 and data[1][1]:
        for item in data[1][1]:
            # item[3] is the type of the question
            # type 0: short text
            # type 1: paragraph
            # type 2: multiple choice
            # type 3: dropdown
            # type 4: checkboxes
            
            # For simplicity, we just extract the title and the first entry ID
            if len(item) > 4 and item[4]:
                item_title = item[1]
                # item[4][0][0] is the entry ID
                entry_id = f"entry.{item[4][0][0]}"
                
                # Extract options if it's a multiple choice/dropdown question
                options = []
                if len(item[4][0]) > 1 and isinstance(item[4][0][1], list):
                    for opt in item[4][0][1]:
                        if isinstance(opt, list) and len(opt) > 0 and opt[0]:
                            options.append(opt[0])
                
                if options:
                    item_title += f" (Options: {', '.join(options)})"
                
                questions.append({
                    "id": entry_id,
                    "title": item_title
                })

    return {
        "title": form_title,
        "description": form_description,
        "questions": questions,
        "resolved_url": response.url
    }

def submit_google_form(url: str, answers: list):
    """
    Submits answers to the Google Form.
    answers: list of dicts [{"id": "entry.1234", "answer": "My answer"}]
    """
    # Strip query parameters if appending
    base_url = url.split("?")[0]
    
    # Convert viewform to formResponse if needed
    if "viewform" in base_url:
        submit_url = base_url.replace("viewform", "formResponse")
    else:
        submit_url = base_url
        if not submit_url.endswith("/"):
            submit_url += "/"
        submit_url += "formResponse"

    payload = {}
    for item in answers:
        payload[item["id"]] = item["answer"]
        
    response = requests.post(submit_url, data=payload)
    response.raise_for_status()
    return response.status_code
