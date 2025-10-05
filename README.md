Llama 4 Scout Python Docstring Generator

Project Overview and Purpose

This application is a simple yet powerful tool designed to enhance code quality and documentation speed for Python developers. It is built using Streamlit for the front-end user interface and utilizes the Cerebras Llama 4 Scout large language model for its core functionality.

The primary purpose of this project is to automate the tedious task of writing detailed documentation. By leveraging the advanced code comprehension capabilities of Llama 4 Scout, the application takes raw Python functions and instantly generates high-quality docstrings formatted in the widely recognized NumPy style. This saves development time, maintains consistency across a codebase, and ensures that functions are well-documented and easy to understand.

Quick Setup

To run this application locally, you need Python installed and must follow these steps to secure your API key.

Prerequisites

Dependencies: Install the required Python libraries.

pip install streamlit requests

API Key Configuration (Secrets)
For security, the application reads your Cerebras API key from a secrets file.

Create the necessary configuration directory inside your project 

root:mkdir .streamlit
Create a file named secrets.toml inside the newly created .streamlit directory.
Paste your API key into this file using the following structure, replacing the placeholder with 
your actual key:

[llama_scout_api]
api_key = "csk-YOUR-API-KEY-GOES-HERE"

Launching the Application

Start the Streamlit application from the root of your project directory:

streamlit run app.py

The application will automatically open in your web browser.

Instructions for UsageThe interface is designed for simplicity:

Input Code: Locate the text area labeled "Paste Python Function:". This area shows a simple def add(a, b): placeholder. You can begin typing or paste your own Python function directly into this box; the placeholder text will disappear automatically. 

Generate: Click the "Generate Docstring" button. The application will securely send your code to the Llama 4 Scout model.

Review Output: The results will appear below in two sections:Generated Docstring: Shows the clean, raw docstring content (Parameters, Returns, Examples, etc.).Function with Docstring: Shows your original function with the new docstring inserted in the correct position, ready to be copied and used in your source code.