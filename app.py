"""
Customer Support AI - Flask Application
Main entry point for the web server with chat UI, history, and API endpoints.
"""

import os
import uuid
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from dotenv import load_dotenv
from triage_engine import TriageEngine
from chat_store import ChatStore

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")
CORS(app)

engine = TriageEngine()
chat_store = ChatStore()


def _get_session_id():
    """Get or create a unique session ID."""
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


# ── Pages ──

@app.route("/")
def home():
    """Serve the chat UI."""
    return render_template("index.html")


# ── Chat API ──

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle a chat message. Stores conversation history and returns a response.
    Expects JSON: { "query": "user's question" }
    """
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Please provide a 'query' field in the request body."}), 400

    user_query = data["query"].strip()
    if not user_query:
        return jsonify({"error": "Query cannot be empty."}), 400

    sid = _get_session_id()

    # Store user message
    chat_store.add_message(sid, "user", user_query)

    # Get conversation context for AI
    context = chat_store.get_recent_context(sid)

    # Classify and respond
    result = engine.classify_query(user_query, context=context)

    # Store bot response
    chat_store.add_message(sid, "bot", result["response"], metadata={
        "type": result.get("type"),
        "category": result.get("category"),
        "confidence": result.get("confidence"),
    })

    return jsonify(result)


@app.route("/ask", methods=["POST"])
def ask():
    """Legacy API endpoint — works without session/history."""
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Please provide a 'query' field in JSON body."}), 400

    user_query = data["query"]
    result = engine.classify_query(user_query)
    return jsonify(result)


# ── History API ──

@app.route("/history")
def history():
    """Get chat history for the current session."""
    sid = _get_session_id()
    messages = chat_store.get_history(sid)
    return jsonify({"history": messages})


@app.route("/clear", methods=["POST"])
def clear():
    """Clear chat history for the current session."""
    sid = _get_session_id()
    chat_store.clear_session(sid)
    return jsonify({"status": "cleared"})


# ── Data API ──

@app.route("/categories")
def categories():
    """Get all FAQ categories."""
    return jsonify({"categories": engine.get_categories()})


@app.route("/suggestions")
def suggestions():
    """Get quick-reply suggestion questions."""
    return jsonify({"suggestions": engine.get_suggestions()})


# ── Health Check ──

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Customer Support AI",
        "openai_enabled": engine.openai_client is not None,
        "faq_count": len(engine.questions),
        "categories": engine.get_categories(),
        "active_sessions": chat_store.get_session_count(),
    })


# ── Error Handlers ──

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error. Please try again."}), 500


if __name__ == "__main__":
    print("\n[BOT] Customer Support AI is starting...")
    print(f"  FAQ entries loaded: {len(engine.questions)}")
    print(f"  Categories: {', '.join(engine.get_categories())}")
    print(f"  OpenAI enabled: {engine.openai_client is not None}")
    print(f"  Server: http://localhost:5000\n")
    app.run(debug=True, port=5000)
