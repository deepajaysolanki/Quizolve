import google.generativeai as genai
from django.conf import settings
import json, re

# Configure the API key
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

def generate_question_batch(topic: str, difficulty: str, num_questions: int = 10, exclude_questions: list = None) -> list:
    """
    Generates a BATCH of quiz questions.
    """
    exclusion_prompt_part = ""
    if exclude_questions:
        # Format the list of questions to be included in the prompt
        formatted_exclusions = "\n".join([f"- {q}" for q in exclude_questions])
        exclusion_prompt_part = f"""
        CRITICALLY IMPORTANT: Do not generate any of the following questions as they have already been asked:
        {formatted_exclusions}
        """

    prompt = f"""
    You are a helpful quiz generator.
    Generate {num_questions} multiple-choice questions about the topic: "{topic}".
    The difficulty level should be {difficulty}.
    Each question must have 4 options and a single correct answer.
    Provide your response exclusively in a valid JSON format, as an array of objects.
    Do not include any text outside of the JSON array.
    {exclusion_prompt_part}
    """
    try:
        response = model.generate_content(prompt)
        # Clean up the response to extract only the JSON part
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        questions = json.loads(json_response)
        return questions
    except Exception as e:
        print(f"Error generating question batch: {e}")
        return [] # Return empty list on error

def generate_questions_from_topic(topic: str, num_questions: int, difficulty: str) -> list:
    """
    Generates quiz questions from a given topic using the AI model.
    """
    prompt = f"""
    You are a helpful quiz generator.
    Generate {num_questions} multiple-choice questions about the topic: "{topic}".
    The difficulty level should be {difficulty}.
    Each question must have 4 options and a single correct answer.
    Provide your response exclusively in a valid JSON format, as an array of objects.
    Each object should have the following keys: "question", "options" (as an array of 4 strings), and "answer" (the string of the correct option).
    Do not include any text outside of the JSON array.

    Example format:
    [
      {{
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris"
      }}
    ]
    """
    try:
        response = model.generate_content(prompt)
        # Clean up the response to extract only the JSON part
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        questions = json.loads(json_response)
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return [] # Return empty list on error

# def generate_questions_from_document(document_text: str, num_questions: int) -> list:
#     """
#     Generates quiz questions from a given document text.
#     """
#     prompt = f"""
#     Based on the following document, generate {num_questions} multiple-choice questions.
#     Each question must be directly answerable from the text provided.
#     Each question must have 4 options and a single correct answer.
#     Provide your response exclusively in a valid JSON format, as an array of objects.
#     Each object should have "question", "options" (array of 4 strings), and "answer" keys.

#     Document:
#     ---
#     {document_text}
#     ---
#     """
#     try:
#         response = model.generate_content(prompt)
#         json_response = response.text.strip().replace("```json", "").replace("```", "")
#         questions = json.loads(json_response)
#         return questions
#     except Exception as e:
#         print(f"Error generating from document: {e}")
#         return []

def get_ai_feedback(score: int, total_questions: int) -> str:
    """
    Generates general feedback based on the user's quiz score.
    """
    percentage = (score / total_questions) * 100
    prompt = f"""
    A user just completed a quiz. They scored {score} out of {total_questions}, which is {percentage:.2f}%.
    Write a short, encouraging, and helpful feedback message for the user.
    If they did well, praise them. If they struggled, give them some motivation.
    Keep the feedback to 2-3 sentences.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating feedback: {e}")
        return "Great effort on the quiz!"
    

def generate_single_question(topic: str, difficulty: str) -> dict:
    """
    Generates a single multiple-choice question from a given topic.
    Returns a dictionary, or None on error.
    """
    prompt = f"""
    You are a helpful quiz generator.
    Generate ONE multiple-choice question about the topic: "{topic}".
    The difficulty level should be {difficulty}.
    The question must have 4 options and a single correct answer.
    Provide your response exclusively in a valid JSON format for a single object.
    Do not include any text, markdown, or array brackets outside of the JSON object.

    Example format:
    {{
      "question": "What is the capital of France?",
      "options": ["Berlin", "Madrid", "Paris", "Rome"],
      "answer": "Paris"
    }}
    """
    try:
        response = model.generate_content(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        question = json.loads(json_response)
        return question
    except Exception as e:
        print(f"Error generating single question: {e}")
        return None
    
# generate 50 questions for a specific Indian national exam
def generate_exam_questions(exam_name: str) -> list:
    """
    Generates 50 high-quality questions for a specific Indian national exam.
    """
    prompt = f"""
    You are an expert tutor specializing in Indian competitive exams.
    Your task is to generate 50 high-quality, multiple-choice questions for the "{exam_name}" exam.
    The questions must be highly relevant to the official {exam_name} syllabus.
    Prioritize questions that have appeared in previous years or cover core concepts that are frequently tested.
    The difficulty should match the standard of the actual {exam_name} exam.
    
    Provide your response exclusively as a valid JSON array of 50 objects.
    Each object must have "question", "options" (an array of 4 strings), and "answer" keys.
    Do not include any introductory text or summaries outside of the JSON array.
    """
    response = model.generate_content(prompt)
    json_response = response.text.strip().replace("```json", "").replace("```", "")
    questions = json.loads(json_response)
    return questions
   
def generate_exam_question_batch(exam_name: str, exclude_questions: list = None) -> list:
    exclusion_prompt_part = ""
    if exclude_questions:
        formatted_exclusions = "\n".join([f"- {q}" for q in exclude_questions])
        exclusion_prompt_part = f"\nCRITICALLY IMPORTANT: Do not generate any of the following questions again:\n{formatted_exclusions}"

    # NEW, MORE DETAILED PROMPT
    prompt = f"""
    You are an expert tutor for the "{exam_name}" exam in India.
    Generate 10 high-quality, multiple-choice questions relevant to the {exam_name} syllabus.

    Your response MUST be a valid JSON array of 10 objects.
    Each object must have these exact keys: "question", "options", "answer".
    - The "question" value must be a string.
    - The "options" value must be a JSON array of 4 strings.
    - The "answer" value must be a string that EXACTLY MATCHES one of the 4 strings in the "options" array.
    
    Example of a single object:
    {{
        "question": "What is the capital of India?",
        "options": ["Mumbai", "New Delhi", "Kolkata", "Chennai"],
        "answer": "New Delhi"
    }}

    Your response must begin with [ and end with ]. Do not include any other text.
    {exclusion_prompt_part}
    """
    # Put the try...except block back in
    try:
        response = model.generate_content(prompt)
        
        # A more robust way to find and extract the JSON
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON array found in the AI response.")
        
        json_response = match.group(0)
        questions = json.loads(json_response)
        return questions

    except Exception as e:
        print("\n--- FAILED AI RESPONSE ---")
        # Use repr() to make hidden characters like newlines visible
        if 'response' in locals():
            print(repr(response.text))
        print("--------------------------\n")
        print(f"Error generating exam question batch: {e}")
        return []