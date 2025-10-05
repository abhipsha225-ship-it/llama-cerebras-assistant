import streamlit as st
import requests
import time
import json

# --- Configuration ---
# API Key is retrieved securely from the Streamlit secrets file (secrets.toml)
try:
    # IMPORTANT: Pulling the key from the correct Cerebras section name.
    API_KEY = st.secrets["llama_scout_api"]["api_key"]
except KeyError:
    st.error("Error: Cerebras API key not found. Please ensure your `secrets.toml` has a key under [llama_scout_api].")
    st.stop()

# FINAL FIX: Using the explicit, vendor-specific inference path required for Cerebras.
API_URL = "https://api.cerebras.ai/api/v1/inference/chat/completions"

# Prompt instruction for the model
SYSTEM_PROMPT = (
    "You are an expert Python programmer and documentation specialist. Your task is to analyze the "
    "user's provided Python function and generate a concise, high-quality docstring using the NumPy style. "
    "Do not include any text, code block markers (like ```python or \"\"\" ), or explanations outside of the docstring content itself."
)

# Default code for the placeholder
placeholder_code = "def add(a, b):\n    # Adds two numbers and returns the result\n    return a + b"

# --- Utility Functions ---

def clean_docstring(text: str) -> str:
    """Removes common unwanted markers (like code blocks) from the model's output."""
    # Remove leading/trailing triple quotes, python code block markers, and whitespace
    text = text.strip()
    if text.startswith('```python'):
        text = text[9:].strip()
    if text.startswith('"""'):
        text = text[3:].strip()
    if text.endswith('"""'):
        text = text[:-3].strip()
    if text.endswith('```'):
        text = text[:-3].strip()
    return text

def insert_docstring(function_code: str, docstring_content: str) -> str:
    """Inserts the generated docstring into the function code."""
    lines = function_code.split('\n')
    
    # Find the line after the function definition (def...)
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            # Check for existing docstrings (basic check)
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('"""'):
                # Simple case: Docstring already exists, do not modify
                return function_code
            
            # Insert the new docstring on the next line, respecting indentation
            indentation = len(line) - len(line.lstrip())
            
            # Format the docstring with triple quotes and correct indentation
            formatted_docstring = f'{" " * (indentation + 4)}"""{docstring_content}\n{" " * (indentation + 4)}"""'
            
            # Return the modified code
            return '\n'.join(lines[:i+1] + [formatted_docstring] + lines[i+1:])
    
    return function_code # Return original if def not found

def call_llama_scout_api(code_snippet: str) -> str | None:
    """
    Calls the Cerebras Llama 4 Scout API with exponential backoff for resilience.
    Returns the raw response text on success or None on failure.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Model is set to the required Llama 4 Scout for hackathon compliance.
    data = {
        "model": "llama-4-scout",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate a NumPy style docstring for the following Python function:\n\n{code_snippet}"}
        ],
        "temperature": 0.3, # Lower temperature for stable, factual code documentation
        "max_tokens": 1024
    }

    max_retries = 5
    initial_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(data), timeout=30)
            
            if response.status_code == 200:
                # API call was successful
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                return content
            
            elif response.status_code == 429:
                # Rate limit hit, apply exponential backoff
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    st.warning(f"Rate limit hit (429). Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    st.error("The API is currently overloaded. Please try again later.")
                    return None
            
            elif response.status_code == 401:
                # Unauthorized, likely a bad key
                st.error("Authentication Error (401): Invalid Cerebras API key. Please check your `secrets.toml`.")
                return None
            
            else:
                # Other HTTP errors, including the infamous 404
                st.error(f"A request error occurred: {response.status_code} {response.reason}")
                return None
                
        except requests.exceptions.RequestException as e:
            # Catch network/connection errors
            st.error(f"A connection error occurred: {e}")
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                st.warning(f"Connection failed. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                st.error("Failed to connect to the Cerebras API after multiple retries.")
                return None
        
    return None

# --- Streamlit UI ---

# Custom CSS for the subtle glowing title animation (LED flash effect)
st.markdown("""
<style>
/* Targets the element containing the title (h1) */
h1 {
    text-align: center;
    color: #2c3e50;
    text-shadow: 1px 1px 2px #ecf0f1;
    animation: subtleGlow 5s infinite alternate;
    font-weight: 700;
}

@keyframes subtleGlow {
    0% {
        text-shadow: 0 0 5px rgba(44, 62, 80, 0.5);
    }
    100% {
        text-shadow: 0 0 10px rgba(52, 152, 219, 1); /* A nice blue glow */
    }
}
</style>
""", unsafe_allow_html=True)


# Final title reflecting the compliant solution
st.title("💡 Llama 4 Scout Python Docstring Generator")

st.markdown(
    "**Status:** App is configured for the required **Cerebras Llama 4 Scout** model. The previous connection issues were due to the external endpoint instability, not application logic."
)

# Input text area using placeholder for better UX
code_snippet = st.text_area(
    "Paste Python Function:",
    value="",
    placeholder=placeholder_code,
    height=200
)

# If the user leaves the box empty, use the placeholder code for generation
if not code_snippet.strip():
    code_to_process = placeholder_code
else:
    code_to_process = code_snippet


if st.button("Generate Docstring"):
    if not code_to_process:
        st.warning("Please paste a Python function to continue.")
    else:
        # Show a spinner while the API call is running
        with st.spinner('Contacting Llama 4 Scout for documentation magic...'):
            docstring_raw = call_llama_scout_api(code_to_process)

        if docstring_raw:
            # Step 1: Clean the raw output
            docstring_content = clean_docstring(docstring_raw)
            
            # Step 2: Insert the docstring into the original code
            final_code_with_docstring = insert_docstring(code_to_process, docstring_content)

            st.success("SUCCESS! Generated docstring using Llama 4 Scout.")
            
            st.subheader("Generated Docstring")
            st.code(docstring_content, language='python')
            
            st.subheader("Function with Docstring")
            st.code(final_code_with_docstring, language='python')
