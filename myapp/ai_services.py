import requests
import json
import re
import time
from django.conf import settings

API_KEY = settings.GROQ_API_KEY

def call_groq_ai(prompt_text):
    """
    Sends a request to Groq's API using a chain of fallback models.
    """
    models_to_try = [
        "llama-3.3-70b-versatile",  # Smartest
        "llama-3.1-8b-instant",     # Fastest
        "mixtral-8x7b-32768"        # Reliable Backup
    ]
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful quiz generator. Output ONLY valid JSON."},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.5 
        }

        try:
            print(f"Contacting Groq ({model})...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"AI Success with {model}!")
                return response.json()
            elif response.status_code in [400, 404]:
                print(f"{model} unavailable. Switching to next model...")
                continue 
            elif response.status_code == 401:
                print(f"Error 401: Invalid API Key.")
                break 
            else:
                print(f"API Error {response.status_code}: {response.text}")
                continue

        except Exception as e:
            print(f"Connection Error: {e}")
    return None

def clean_json_text(text):
    return text.replace("```json", "").replace("```", "").strip()

# --- MOCK DATA FALLBACK ---
def get_mock_questions(topic, difficulty="Standard"):
    print(f" SERVING BACKUP QUESTIONS FOR {topic}")
    return [
        {"question": f"Backup ({difficulty}): What is {topic}?", "options": ["Topic", "Food", "Place", "Movie"], "answer": "Topic"},
        {"question": "Why backup?", "options": ["API Model Error", "Internet", "Test", "Bug"], "answer": "API Model Error"},
        {"question": "Which AI is active?", "options": ["Groq (Llama)", "Gemini", "GPT", "None"], "answer": "Groq (Llama)"},
        {"question": "Is Groq fast?", "options": ["Yes", "No", "Maybe", "Slow"], "answer": "Yes"},
        {"question": "Status 200 means?", "options": ["Success", "Error", "Forbidden", "Wait"], "answer": "Success"}
    ]

# --- MAIN GENERATOR FUNCTION ---
def generate_groq_response(topic_or_exam: str, num_questions: int, difficulty: str, exclude_questions: list = None) -> list:
    
    exclusion_text = ""
    if exclude_questions:
        exclusion_text = "Do not repeat these questions: " + ", ".join(exclude_questions)

    prompt = f"""
    You are an expert tutor for "{topic_or_exam}".
    Generate {num_questions} multiple-choice questions (Difficulty: {difficulty}).
    
    Your response MUST be a valid JSON array of {num_questions} objects.
    Each object must have these exact keys: "question", "options", "answer".
    - "options" must be an array of 4 strings.
    - "answer" must be a string that EXACTLY MATCHES one of the options.
    
    Format: [{{ "question": "...", "options": ["A","B","C","D"], "answer": "A" }}]
    {exclusion_text}
    """
    
    data = call_groq_ai(prompt)
    
    if not data: return "Something went wrong, please try again later."

    try:
        text = data['choices'][0]['message']['content']
        return json.loads(clean_json_text(text))
    except Exception as e:
        print(f"Parsing Error: {e}")
        return "Something went wrong, please try again later."

# --- WRAPPER FUNCTIONS (MATCHING VIEWS.PY) ---

def generate_question_batch(topic: str, difficulty: str, num_questions: int = 5, exclude_questions: list = None) -> list:
    return generate_groq_response(topic, num_questions, difficulty, exclude_questions)

def generate_questions_from_topic(topic: str, num_questions: int, difficulty: str) -> list:
    return generate_groq_response(topic, num_questions, difficulty)

def generate_exam_questions(exam_name: str) -> list:
    return generate_groq_response(exam_name, 5, "Hard")

# --- THIS WAS MISSING! I ADDED IT BACK ---
def generate_exam_question_batch(exam_name: str, exclude_questions: list = None) -> list:
    """
    Alias for generate_exam_questions to satisfy views.py call
    """
    return generate_groq_response(exam_name, 5, "Hard", exclude_questions)

def generate_single_question(topic: str, difficulty: str) -> dict:
    result = generate_groq_response(topic, 1, difficulty)
    return result[0] if result else get_mock_questions(topic)[0]

def get_ai_feedback(score: int, total_questions: int) -> str:
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    if percentage > 80:
        return f"Excellent work! You scored {score}/{total_questions}."
    elif percentage > 50:
        return f"Good effort! You scored {score}/{total_questions}."
    else:
        return f"You scored {score}/{total_questions}. Keep practicing!"