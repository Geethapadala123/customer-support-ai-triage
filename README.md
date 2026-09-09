# Customer Support AI 🤖

An AI-powered customer support chatbot with a premium dark-mode chat interface, intelligent FAQ matching, OpenAI GPT fallback, sentiment detection, and conversation history.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌐 Live Demo

[🚀 View Live Project](https://customer-support-ai-triage-1.onrender.com)

## ✨ Features

- **Smart FAQ Matching** — TF-IDF + cosine similarity with bigram support to match user queries against 23 FAQ entries across 7 categories.
- **OpenAI GPT Fallback** — When no FAQ matches, uses GPT-3.5-turbo to generate helpful responses (optional, works without API key).
- **Sentiment Detection** — Detects frustrated customers via keyword analysis and prioritizes human escalation.
- **Conversation Context** — Passes recent chat history to improve AI responses.
- **Premium Chat UI** — Dark glassmorphism design with gradient accents, typing indicators, and micro-animations.
- **Quick Replies** — Suggestion chips for common questions.
- **Chat History** — Session-based in-memory storage with timestamps.
- **Responsive** — Works beautifully on mobile, tablet, and desktop.

## 📁 Project Structure

```
customer-support-ai/
│
├── data/
│   └── faq.json                # 23 FAQ entries across 7 categories
│
├── static/
│   ├── css/
│   │   └── style.css           # Premium glassmorphism dark theme
│   └── js/
│       └── chat.js             # Chat client (send/receive, typing, history)
│
├── templates/
│   └── index.html              # Chat UI template
│
├── .env                        # API keys & Flask config
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── chat_store.py               # In-memory chat history storage
├── triage_engine.py            # FAQ matching, sentiment, OpenAI fallback
├── app.py                      # Flask web server & API
└── README.md                   # This file
```

## 🚀 Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment (optional)

Edit `.env` and add your OpenAI API key to enable AI-generated responses:

```
OPENAI_API_KEY=sk-your-key-here
```

> The app works fully without an API key — it will use FAQ matching only.

### 3. Run the app

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

## 🔌 API Endpoints

| Method | Endpoint        | Description                          |
|--------|-----------------|--------------------------------------|
| GET    | `/`             | Chat UI                              |
| POST   | `/chat`         | Send a message (with session history)|
| POST   | `/ask`          | Legacy stateless query               |
| GET    | `/history`      | Get chat history for current session |
| POST   | `/clear`        | Clear session chat history           |
| GET    | `/categories`   | List all FAQ categories              |
| GET    | `/suggestions`  | Get quick-reply suggestions          |
| GET    | `/health`       | Service health check                 |

### Example: POST `/chat`

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I track my order?"}'
```

**Response:**
```json
{
  "type": "faq",
  "sentiment": "neutral",
  "response": "Go to My Orders and click 'Track' next to your order...",
  "category": "Orders",
  "confidence": 0.85,
  "matched_question": "How do I track my order?"
}
```

## 🧠 How It Works

1. **User sends a message** → Flask `/chat` endpoint receives it.
2. **Sentiment check** → Keyword-based analysis flags frustrated customers for priority escalation.
3. **FAQ matching** → TF-IDF vectorizer + cosine similarity searches 23 FAQs.
4. **GPT fallback** → If no FAQ matches (and API key is set), OpenAI generates a response.
5. **Final fallback** → Suggests contacting a human agent.
6. **Response stored** → Both user and bot messages are saved to session history.

## 📦 Dependencies

- `flask` — Web framework
- `flask-cors` — Cross-origin request support
- `python-dotenv` — Environment variable loading
- `openai` — OpenAI GPT API client
- `scikit-learn` — TF-IDF vectorization and cosine similarity
