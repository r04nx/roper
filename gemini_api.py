import requests
import base64
import os
from dotenv import load_dotenv
import time
import threading
import logging
from datetime import datetime

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/roper.logs'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('roper.gemini_api')

# Load multiple API keys
GEMINI_API_KEYS = []
api_key_1 = os.getenv('GEMINI_API_KEY')
api_key_2 = os.getenv('GEMINI_API_KEY_2')
api_key_3 = os.getenv('GEMINI_API_KEY_3')
api_key_4 = os.getenv('GEMINI_API_KEY_4')
api_key_5 = os.getenv('GEMINI_API_KEY_5')

# Add available keys to rotation list
for key in [api_key_1, api_key_2, api_key_3, api_key_4, api_key_5]:
    if key and key.strip():
        GEMINI_API_KEYS.append(key.strip())

if not GEMINI_API_KEYS:
    print("⚠️ No valid API keys found! Add GEMINI_API_KEY in .env file")

# Smart API key management
active_key_index = 0
last_working_key = None
key_test_lock = threading.Lock()
key_status = {}  # Track status of each key

# Load model configurations
MCQ_MODEL = os.getenv('MCQ_MODEL', 'gemini-2.0-flash')
CODE_MODEL = os.getenv('CODE_MODEL', 'gemini-2.0-flash')

# Model URL mapping
MODEL_URLS = {
    'gemini-2.5-pro': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent',
    'gemini-2.5-flash': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
    'gemini-2.5-flash-lite': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent',
    'gemini-2.0-flash': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
    'gemini-1.5-pro': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent',
    'gemini-1.5-flash': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
}

logger.info(f"MCQ Model: {MCQ_MODEL}, CODE Model: {CODE_MODEL}")

SYSTEM_PROMPT = (
    "You are an expert test-taker. First, carefully analyze each MCQ question and think through the solution step by step. "
    "Then evaluate your reasoning to ensure it's correct. Finally, provide ONLY the answer in the specified format.\n\n"
    "CRITICAL INSTRUCTIONS:\n"
    "1. Think carefully before answering each question\n"
    "2. Evaluate your logic once more to ensure accuracy\n"
    "3. For single question: Answer format is just the letter (A, B, C, or D)\n"
    "4. For multiple questions: Format is <Question Number><Answer Letter> separated by spaces (example: 1A 2B 3C 4D)\n"
    "5. NO explanations, NO reasoning text in output, NO extra words\n"
    "6. If options are not clearly labeled, use A/B/C/D based on top-to-bottom order\n"
    "7. Double-check your final answer before responding"
)

CODE_PROMPT = (
    "You are an expert competitive programmer. Analyze the coding problem and provide the MOST OPTIMAL solution. "
    "Requirements: "
    "1. Use the most efficient algorithm and data structure "
    "2. Consider ALL edge cases and constraints "
    "3. Write code that passes ALL test cases "
    "4. Use correct syntax with proper operators (|| not >>, && not >>) "
    "5. NO markdown formatting, NO backticks, NO explanations "
    "6. Return ONLY clean, executable code with proper indentation "
    "7. Optimize for both time and space complexity "
    "8. Handle null/empty inputs and boundary conditions"
)

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def get_next_api_key():
    """Get next API key in rotation"""
    global current_key_index
    if not GEMINI_API_KEYS:
        return None
    key = GEMINI_API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
    return key

def test_api_key(api_key):
    """Test a single API key for validity"""
    headers = {
        "Content-Type": "application/json"
    }
    # Simple test with minimal data
    test_data = {
        "contents": [
            {
                "parts": [
                    {"text": "Test"}
                ]
            }
        ]
    }
    try:
        # Use MCQ model URL for testing with API key as query parameter
        base_url = MODEL_URLS.get(MCQ_MODEL, MODEL_URLS['gemini-2.0-flash'])
        test_url = f"{base_url}?key={api_key}"
        response = requests.post(test_url, json=test_data, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.debug(f"API key test failed: {e}")
        return False

def find_working_key():
    """Find and set the first working API key"""
    global last_working_key, active_key_index
    
    if not GEMINI_API_KEYS:
        logger.warning("No API keys available")
        print("⚠️ No API keys available")
        return False
        
    logger.info(f"Testing {len(GEMINI_API_KEYS)} API keys")
    print(f"🔍 Testing {len(GEMINI_API_KEYS)} API keys...")
    
    for i, key in enumerate(GEMINI_API_KEYS):
        logger.info(f"Testing API key {i+1}/{len(GEMINI_API_KEYS)}")
        print(f"Testing API key {i+1}/{len(GEMINI_API_KEYS)}...")
        if test_api_key(key):
            with key_test_lock:
                last_working_key = key
                active_key_index = i
                key_status[key] = True
            logger.info(f"Active API key set: Key {i+1}")
            print(f"✅ Active API key set: Key {i+1}")
            return True
    
    logger.error("No working API key found!")
    print("⚠️ No working API key found!")
    return False

def initialize_api_keys():
    """Initialize API keys and find working one"""
    global last_working_key
    if last_working_key is None and GEMINI_API_KEYS:
        find_working_key()

def make_api_request(data, prompt_type="MCQ"):
    """Make API request with current working key, switching if necessary"""
    global last_working_key, active_key_index
    
    # Initialize if not done
    if last_working_key is None:
        initialize_api_keys()
        if last_working_key is None:
            return "No working API keys available"
    
    # Select appropriate model URL based on prompt type
    if prompt_type == "MCQ":
        model_url = MODEL_URLS.get(MCQ_MODEL, MODEL_URLS['gemini-2.0-flash'])
        logger.info(f"Using MCQ model: {MCQ_MODEL}")
    else:
        model_url = MODEL_URLS.get(CODE_MODEL, MODEL_URLS['gemini-2.0-flash'])
        logger.info(f"Using CODE model: {CODE_MODEL}")
    
    max_retries = len(GEMINI_API_KEYS)
    current_retry = 0
    
    while current_retry < max_retries:
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            print(f"Using API key {active_key_index + 1} for {prompt_type}...")
            # Use query parameter format for API key
            url_with_key = f"{model_url}?key={last_working_key}"
            response = requests.post(url_with_key, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ Success with API key {active_key_index + 1}")
                    return result
                except Exception as e:
                    print(f"⚠️ Parse error: {str(e)}")
                    break
                    
            elif response.status_code in [429, 403, 400]:
                print(f"⚠️ API key {active_key_index + 1} error {response.status_code}, switching...")
                # Mark current key as failed and find next working key
                with key_test_lock:
                    key_status[last_working_key] = False
                    if not find_next_working_key():
                        return f"All API keys failed. Status: {response.status_code}"
                current_retry += 1
                continue
                
            else:
                print(f"⚠️ Unexpected error {response.status_code}: {response.text}")
                break
                
        except requests.exceptions.Timeout:
            print(f"⚠️ API key {active_key_index + 1} timed out, switching...")
            with key_test_lock:
                if not find_next_working_key():
                    return "All API keys timed out"
            current_retry += 1
            continue
            
        except Exception as e:
            print(f"⚠️ Error with API key {active_key_index + 1}: {str(e)}")
            break
    
    return "API request failed after all retries"

def find_next_working_key():
    """Find the next working API key after current one fails"""
    global last_working_key, active_key_index
    
    start_index = (active_key_index + 1) % len(GEMINI_API_KEYS)
    
    for i in range(len(GEMINI_API_KEYS)):
        test_index = (start_index + i) % len(GEMINI_API_KEYS)
        test_key = GEMINI_API_KEYS[test_index]
        
        # Skip if we know this key is not working
        if test_key in key_status and not key_status[test_key]:
            continue
            
        if test_api_key(test_key):
            last_working_key = test_key
            active_key_index = test_index
            key_status[test_key] = True
            print(f"✅ Switched to working API key {test_index + 1}")
            return True
        else:
            key_status[test_key] = False
    
    return False

def ask_gemini(image_path):
    logger.info(f"Processing MCQ request for image: {image_path}")
    img_b64 = image_to_base64(image_path)
    data = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"inline_data": {"mime_type": "image/png", "data": img_b64}}
                ]
            }
        ]
    }
    result = make_api_request(data, "MCQ")
    logger.info(f"MCQ API response: {result}")
    return result

def ask_gemini_code(image_path):
    logger.info(f"Processing CODE request for image: {image_path}")
    img_b64 = image_to_base64(image_path)
    data = {
        "contents": [
            {
                "parts": [
                    {"text": CODE_PROMPT},
                    {"inline_data": {"mime_type": "image/png", "data": img_b64}}
                ]
            }
        ]
    }
    result = make_api_request(data, "CODE")
    logger.info(f"CODE API response length: {len(result) if result else 0} characters")
    return result
