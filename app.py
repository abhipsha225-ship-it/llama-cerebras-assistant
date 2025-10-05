import streamlit as st
import requests
import json
import time

# --- Configuration (UPDATE THIS LATER) ---
# NOTE: Replace this with your actual Llama 4 Scout API Key when running locally.
API_KEY = "YOUR_LLAMA_4_SCOUT_API_KEY_HERE" 

# Base URL for the Cerebras API endpoint
# This should be updated to the specific endpoint for Llama 4 Scout as provided by the hackathon organizers.
LLAMA_API_URL = "https://api.cerebras.com/v1/llama-4-scout/generate" 

# --- Helper Function: Exponential Backoff ---

def _exponential_backoff_fetch(url, headers, payload, max_retries=5):
    """
    Handles API fetching with exponential backoff and retries for transient errors.
    This is mandatory for robust API communication.
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Successful response (2xx)
            if response.status_code == 200:
                return response
            
            # Server error or rate limit (retryable errors: 429, 5xx)
            elif response.status_code in [429, 500, 502, 503, 504]:
                st.warning(f"API Rate Limit/Server Error ({response.status_code}). Retrying in {2**attempt}s...")
                time.sleep(2 ** attempt)  # Exponential delay
                continue
                
            # Unrecoverable errors (4xx client errors)
            else:
                st.error(f"Unrecoverable API Error ({response.status_code}): {response.text}")
                return None
        
        except requests.exceptions.Timeout:
            st.error("API Request timed out. Retrying...")
            time.sleep(2 ** attempt)
            continue
        except requests.exceptions.RequestException as e:
            st.error(f"A general request error occurred: {e}")
            return None
    
    st.error("Failed to get a response from the Cerebras API after multiple retries.")
    return None

# --- Core LLM Function ---

def generate_docstring_via_llama_scout(code_block: str) -> str:
    """
    Constructs the prompt and calls the Llama 4 Scout API to generate a docstring.
    """
    if API_KEY == "YOUR_LLAMA_4_SCOUT_API_KEY_HERE" or not API_KEY:
        return "Error: Please replace 'YOUR_LLAMA_4_SCOUT_API_KEY_HERE' in app.py with your actual API key."
    
    # 1. Craft the Prompt (Long-Context Deep Dive)
    # This prompt tells Llama 4 Scout its persona and task, leveraging its context window.
    prompt = f"""
    You are an expert Python documentation specialist. Your task is to analyze the user-provided code block 
    and write a comprehensive Python docstring (using the NumPy style) for the primary function or class defined 
    within the code. Only return the docstring content, nothing else.

    CODE BLOCK TO ANALYZE:
    ---
    {code_block}
    ---

    GENERATED DOCSTRING (NumPy Style):
    """
    
    # 2. Prepare Headers and Payload
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.2,
        "stop": ["CODE BLOCK TO ANALYZE", "---"], # Helps prevent model from repeating the prompt
    }

    # 3. Call the API with Backoff
    response = _exponential_backoff_fetch(LLAMA_API_URL, headers, payload)

    if response is None:
        return "Docstring generation failed due to a critical API or network error."

    try:
        # Parse the JSON response
        result = response.json()
        
        # Extract the generated text from the model's response structure
        generated_text = result['choices'][0]['text'].strip()
        return generated_text
    
    except (KeyError, json.JSONDecodeError) as e:
        st.error(f"Error parsing API response. Response text: {response.text}")
        return f"Docstring generation failed due to invalid response format: {e}"


# --- Streamlit UI ---

st.title("💡 Llama 4 Scout Docstring Generator")
st.markdown("---")

st.markdown("""
This app uses **Llama 4 Scout** (via the Cerebras API) to analyze Python code 
and generate high-quality NumPy-style docstrings, leveraging its **long-context capabilities** for deep code understanding.
""")

code_input = st.text_area(
    "Paste your Python Code here:", 
    height=400,
    placeholder="def calculate_total(prices, tax_rate):\n    # Calculates total price after tax\n    total = sum(prices)\n    return total * (1 + tax_rate)"
)

if st.button("✨ Generate Docstring", type="primary"):
    if not code_input.strip():
        st.warning("Please paste some code to generate a docstring.")
    else:
        with st.spinner('Calling Llama 4 Scout for Deep Context Analysis...'):
            # Call the core function
            docstring = generate_docstring_via_llama_scout(code_input)
            
        if docstring.startswith("Error"):
            st.error(docstring)
        else:
            st.subheader("Generated Docstring")
            st.code(docstring, language="python")
            st.success("Docstring generation complete!")

st.markdown("---")
st.markdown("###### Status: Core API integration complete (Commit 4)")
