from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import time

# Initialize Flask app
app = Flask(__name__)

# Create the variables to store the conversation context
context = ""

# Define prompt templates in a dictionary
prompt_templates = {
    "default": """
Your name is MathBot. You help students manage group projects. Do not greet the user repeatedly. Avoid making unnecessary assumptions and ask clarifying questions instead.

Conversation History: {context}

Student Question: {question}

Your Response:
""",
    "project_planning": """
Your name is MathBot. You help students with project planning and scheduling. Do not greet the user repeatedly. Focus on providing practical planning advice and ask clarifying questions if details are not clear.

Conversation History: {context}

Student Question: {question}

Your Response:
""",
    "math_topics": """
Your name is MathBot. You assist students in finding topics for their presentations. Do not greet the user repeatedly. Focus on helping them select engaging and relevant presentation topics, and ask clarifying questions to understand their interests. For responses that have lists, put each item of the list on a new line in your answer.

Conversation History: {context}

Student Question: {question}

Your Response:
""",
    "other": """
Your name is MathBot. You help students with other queries in Math 1102 at UNC Charlotte. Do not greet the user repeatedly. Avoid unnecessary details unless asked.

Conversation History: {context}

Student Question: {question}

Your Response:
"""
}

model = OllamaLLM(model="llama3.2:1b")
prompt = ChatPromptTemplate.from_template(prompt_templates["default"])
chain = prompt | model

# Store selected template
selected_template = prompt_templates["default"]

@app.route("/")
def select_prompt():
    """Render the prompt selection interface."""
    return render_template("select_prompt.html")

@app.route("/set_prompt", methods=["POST"])
def set_prompt():
    """Set the selected prompt template."""
    global selected_template, prompt, chain, context
    selected_prompt = request.form["prompt"]

    if selected_prompt in prompt_templates:
        selected_template = prompt_templates[selected_prompt]
    else:
        selected_template = prompt_templates["default"]

    prompt = ChatPromptTemplate.from_template(selected_template)
    chain = prompt | model

    # Reset the context when a new prompt is selected
    context = ""

    return redirect(url_for("chat_screen"))

@app.route("/chat_screen")
def chat_screen():
    """Render the chat interface."""
    return render_template("chatBotHomescreen.html")

# Initialize a flag for the introduction
has_introduced = False

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests with streaming."""
    global context, has_introduced
    user_message = request.form["user-input"].strip("?!.")

    # Define common greetings to filter out
    greetings = ["hello", "hi", "hey", "greetings"]

    # Check if the user's message is a greeting, and skip adding it to the context if so
    if user_message.lower() in greetings and not has_introduced:
        # Add a single greeting response if it's the first greeting
        response = "Hello! How can I assist you today?"
        has_introduced = True
        return Response(response, content_type='text/plain')
    
    # Continue with normal conversation if it's not a greeting
    def generate_response():
        global context

        # Pass the user's message and existing context to the model
        result = chain.invoke({"context": context, "question": user_message})
        # print(result)
        
        # Add the user's input and the bot's response to the context
        context += f"\nUser: {user_message}\nAI: {result}"

        # Format the result to preserve newlines and indentation
        formatted_result = result.replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")

        # Stream the bot's response to the client
        for token in formatted_result.split():
            if token:  # Ensure token is not empty or undefined
                yield token + ' '
            time.sleep(0.1)  # Adjust the sleep time for your desired streaming speed

    return Response(generate_response(), content_type='text/html')

@app.route("/summarize", methods=["POST"])
def summarize():
    """Summarize the session."""
    global context
    summary_prompt = f"Summarize the following conversation:\n{context}\nSummary:"
    summary_result = chain.invoke({"context": context, "question": summary_prompt})
    return jsonify({"summary": summary_result})

if __name__ == "__main__":
    app.run(debug=True)


# Progress bar for Summarize button
