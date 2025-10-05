import os
import time
from flask import Flask, request, render_template
from cerebras.cloud.sdk import Cerebras  # Use the working SDK

# --- Configuration ---
# Your Cerebras API Key (Keep it hardcoded here for simplicity in the Docker environment)
API_KEY = "csk-ehevpr9wkrm9y43t2fdf2dwvepdk42r926n98y89ve8dyejh" 
MODEL_NAME = "llama-4-scout-17b-16e-instruct" 

app = Flask(__name__)

# --- Core LLM Generation Logic ---
def generate_docstring(function_code: str):
    """Generates a docstring for the given code using the Cerebras Llama API."""
    
    # Simple check to prevent empty requests
    if not function_code.strip():
        return "Please provide a function to analyze.", None
    
    PROMPT = (
        "You are an expert Python developer. Generate a comprehensive "
        "Google-style docstring for the following function. Only output the docstring. "
        f"Function:\n\n{function_code}"
    )

    try:
        # Initialize Cerebras client
        client = Cerebras(api_key=API_KEY)
        start_time = time.time()

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": PROMPT}
            ],
            temperature=0.1,
            max_tokens=256
        )

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        docstring_content = response.choices[0].message.content.strip()
        latency_str = f"{latency_ms:.2f}"

        return docstring_content, latency_str

    except Exception as e:
        # Catch any API or connection error
        return None, f"API Error: {e}"

# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    docstring = None
    latency = None
    input_code = request.form.get("code_input", "")
    error = None

    if request.method == "POST":
        if input_code:
            docstring, latency_or_error = generate_docstring(input_code)
            
            if docstring:
                latency = latency_or_error
            else:
                error = latency_or_error # If docstring is None, the second return value is the error string
        else:
            error = "Input code cannot be empty."

    # Render the main template with the results
    return render_template(
        "index.html", 
        docstring=docstring, 
        latency=latency, 
        input_code=input_code, 
        error=error
    )

if __name__ == "__main__":
    # When running locally (without Docker), Flask runs on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)