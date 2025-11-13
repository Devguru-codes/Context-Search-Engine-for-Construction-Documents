import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from google.api_core import exceptions as google_exceptions

# Load environment variables from .env file
load_dotenv()

# --- API Key Configuration ---
# Load multiple Gemini keys from individual environment variables
GEMINI_API_KEYS = [
    key for key in [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3")
    ] if key is not None
]

if not GEMINI_API_KEYS:
    raise ValueError("No Gemini API keys found. Please set GEMINI_API_KEY_1, etc., in the .env file.")

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found. Fallback to Gemma will not be available.")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- State Management for API Keys ---
_current_gemini_key_index = 1 # Start with key index 1 (GEMINI_API_KEY_2)

def _log_ai_response(response_text, is_error=False, model_name=""):
    """Logs AI responses or errors to a file."""
    with open("ai_response_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"--- AI RESPONSE START ({model_name}) ---\n" if not is_error else f"--- ERROR ({model_name}) ---\n")
        log_file.write(response_text)
        log_file.write("\n--- AI RESPONSE END ---\n\n" if not is_error else "\n--- END ERROR ---\n\n")

def _log_ai_context(prompt):
    """Logs the full prompt sent to the AI."""
    with open("ai_context_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write("--- AI CONTEXT START ---\n")
        log_file.write(prompt)
        log_file.write("\n--- AI CONTEXT END ---\n\n")

def _get_next_gemini_key():
    """Rotates to the next available Gemini API key."""
    global _current_gemini_key_index
    _current_gemini_key_index = (_current_gemini_key_index + 1) % len(GEMINI_API_KEYS)
    return GEMINI_API_KEYS[_current_gemini_key_index]

def _extract_json_from_string(text):
    """
    Finds and extracts the first valid JSON array from a string.
    Handles cases where the AI includes text before or after the JSON.
    """
    # Find the starting bracket of the JSON array
    start_index = text.find('[')
    if start_index == -1:
        return None

    # Find the matching closing bracket for the array
    end_index = -1
    open_brackets = 0
    for i in range(start_index, len(text)):
        if text[i] == '[':
            open_brackets += 1
        elif text[i] == ']':
            open_brackets -= 1
            if open_brackets == 0:
                end_index = i + 1
                break
    
    if end_index == -1:
        return None

    # Return the extracted JSON string
    return text[start_index:end_index]


def refine_batch_with_ai(batch_data):
    """
    Sends a batch of data to AI for refinement.
    Cycles through Gemini keys on failure, then falls back to Gemma.
    """
    global _current_gemini_key_index

    if not batch_data:
        return []

    print(f"Starting AI refinement for a batch of {len(batch_data)} rows...")

    prompt_template = f"""
    You are an expert civil engineering assistant. Your task is to refine the following structured data, provided as a JSON array.
    The JSON must be perfectly formatted. Ensure all string values with double-quotes are properly escaped (e.g., "some \\"quoted\\" text").

    Data to refine:
    {json.dumps(batch_data, indent=2)}

    Follow these instructions for each object:
    1.  "Sl. No": Keep original value.
    2.  "Material Name": Keep original value.
    3.  "Test Name/Reference Code/Standard...": From the provided references, select the top 5 to 7 most relevant ones. Prioritize references that are specific (e.g., IS codes, table numbers, detailed section numbers) and directly support the "Any other relevant information" field. List each selected reference on a new line, numbered (1., 2., etc.). If fewer than 5 relevant references are found, list all that are relevant.
    4.  "Specific Material Type/Material Definition": Provide a concise definition. If none can be clearly determined, state "No specific definition could be determined from the context."
    5.  "Any other relevant information": Provide concise (1-2 paragraphs) details for a civil engineer.

    Your response MUST be ONLY the JSON array of objects. Do not include any explanatory text, comments, or any characters before or after the opening `[` and closing `]` of the JSON array.
    """

    refined_data = None
    
    # --- Try Gemini with Key Rotation ---
    gemini_is_down = False
    initial_key_index = _current_gemini_key_index
    
    for i in range(len(GEMINI_API_KEYS)):
        current_key_index = (_current_gemini_key_index + i) % len(GEMINI_API_KEYS)
        current_key = GEMINI_API_KEYS[current_key_index]
        
        try:
            print(f"Attempting Gemini API with key index: {current_key_index}...")
            genai.configure(api_key=current_key)
            _log_ai_context(prompt_template)
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt_template)
            
            _log_ai_response(response.text, model_name=f"Gemini (Key {current_key_index})")
            
            json_text = _extract_json_from_string(response.text)
            if json_text:
                refined_data = json.loads(json_text)
            else:
                raise json.JSONDecodeError("No valid JSON array found in the response.", response.text, 0)

            print("Gemini API response received successfully.")
            _current_gemini_key_index = current_key_index # Update current key index on success
            break  # Success, exit the loop

        except json.JSONDecodeError as e:
            error_message = f"Failed to decode JSON from Gemini response with key {current_key_index}: {e}"
            print(error_message)
            _log_ai_response(error_message, is_error=True, model_name=f"Gemini (Key {current_key_index})")
            continue # Try next key
        except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated, google_exceptions.ResourceExhausted) as e:
            error_message = f"Gemini API Key {current_key_index} failed: {e}"
            print(error_message)
            _log_ai_response(error_message, is_error=True, model_name=f"Gemini (Key {current_key_index})")
            continue # Try next key
        except google_exceptions.ServiceUnavailable as e:
            error_message = f"Gemini API service is unavailable: {e}"
            print(error_message)
            _log_ai_response(error_message, is_error=True, model_name="Gemini")
            gemini_is_down = True
            break # Service is down, no point rotating
        except Exception as e:
            error_message = f"An unexpected error occurred with Gemini: {e}"
            print(error_message)
            _log_ai_response(error_message, is_error=True, model_name="Gemini")
            gemini_is_down = True
            break # Assume a critical failure
    else: # This block runs if the for loop completes without a 'break'
        print("All Gemini keys failed. Falling back.")
        gemini_is_down = True

    if gemini_is_down:
        refined_data = None

    # --- Fallback to OpenRouter (Gemma) ---
    if refined_data is None:
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key":
            print("OpenRouter API key not configured. Cannot fall back to Gemma.")
            return batch_data

        print("Attempting OpenRouter (Gemma) for batch refinement...")
        _log_ai_context(prompt_template)
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "google/gemma-3n-e2b-it:free", "messages": [{"role": "user", "content": prompt_template}]}
        
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            
            gemma_text = response.json()['choices'][0]['message']['content']
            _log_ai_response(gemma_text, model_name="Gemma")
            
            json_text = _extract_json_from_string(gemma_text)
            if json_text:
                refined_data = json.loads(json_text)
            else:
                raise json.JSONDecodeError("No valid JSON array found in Gemma's response.", gemma_text, 0)

            print("OpenRouter (Gemma) API response received successfully.")
        except Exception as e:
            print(f"OpenRouter (Gemma) failed: {e}")
            _log_ai_response(str(e), is_error=True, model_name="Gemma")

    # --- Final Processing ---
    if refined_data:
        expected_columns = list(batch_data[0].keys())
        cleaned_data = [{key: item.get(key) for key in expected_columns} for item in refined_data]
        print("AI refinement for batch complete.")
        return cleaned_data
    else:
        print("AI refinement failed for the batch. Returning original batch data.")
        return batch_data

if __name__ == '__main__':
    # --- Example Usage ---
    sample_batch = [
        {"Sl. No": 1, "Material Name": "Cement", "Test Name/Reference Code/Standard as per the given document (with reference page number)": "1. 4.1. MATERIAL\n2. (c) Brick Aggregate...", "Specific Material Type/Material Definition": "No Info", "Any other relevant information": "Some details..."},
        {"Sl. No": 2, "Material Name": "Fine Aggregate", "Test Name/Reference Code/Standard as per the given document (with reference page number)": "Some ref", "Specific Material Type/Material Definition": "Sand", "Any other relevant information": "Passes sieve..."}
    ]

    print("--- SENDING BATCH DATA TO AI ---")
    refined_output = refine_batch_with_ai(sample_batch)

    if refined_output and refined_output != sample_batch:
        print("\n--- REFINED BATCH DATA RECEIVED ---")
        for row in refined_output:
            print(json.dumps(row, indent=2))
            print("-" * 30)
    else:
        print("\n--- FAILED TO GET REFINED BATCH DATA ---")
