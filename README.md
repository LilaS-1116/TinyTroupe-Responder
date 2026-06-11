# TinyTroupe Responder for Google Forms

A modern web application built for the **Big Data Systems** Final Project. This tool allows researchers and product managers to instantly generate synthetic, persona-driven responses to any public Google Form by leveraging Microsoft's TinyTroupe and OpenAI.

## Features
- **URL Resolution**: Automatically parses and extracts questions from public Google Form URLs (including `forms.gle` shortlinks).
- **Persona-Driven Responses**: Define custom personas (e.g., "30-year-old software engineer") to simulate how different demographics might answer.
- **Multi-Persona Bulk Processing**: Add multiple persona groups in a single request (e.g., 50 software engineers, 25 teenagers).
- **Asynchronous Background Tasks**: Capable of generating and submitting up to 100 responses concurrently without timing out your browser.

## How to Run Locally

### Prerequisites
- Python 3.9+
- An OpenAI API Key

### 1. Clone the repository
```bash
git clone https://github.com/LilaS-1116/TinyTroupe-Responder.git
cd TinyTroupe-Responder
```

### 2. Create and activate a Virtual Environment
**Windows**:
```bash
python -m venv venv
.\venv\Scripts\activate
```
**Mac/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn pydantic requests beautifulsoup4 python-dotenv tinytroupe
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory and add your OpenAI API Key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 5. Start the Server
```bash
python main.py
```
*Note: The server will start running on `http://localhost:8000` or `http://0.0.0.0:8000`.*

### 6. Usage
1. Open a web browser and go to `http://localhost:8000`.
2. Paste the URL of a **publicly editable** Google Form.
3. Fill in the Persona Description and choose the Number of Submissions.
4. Click **Generate Answers**. The system will process the form, query OpenAI via TinyTroupe in the background, and seamlessly `POST` the synthetic responses back to your Google Form backend.
