"""
Triage Engine for Customer Support AI
Handles FAQ matching, sentiment analysis, and OpenAI GPT fallback.
"""

import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Sentiment keywords for basic sentiment detection
NEGATIVE_KEYWORDS = [
    "angry", "furious", "terrible", "worst", "hate", "awful", "horrible",
    "disgusting", "unacceptable", "pathetic", "useless", "scam", "fraud",
    "frustrated", "annoyed", "disappointed", "ridiculous", "outrageous",
    "never", "waste", "broken", "ruined", "complaint", "sue", "legal",
]

POSITIVE_KEYWORDS = [
    "thank", "thanks", "great", "awesome", "love", "excellent", "amazing",
    "perfect", "wonderful", "helpful", "appreciate", "good", "happy",
    "pleased", "fantastic", "brilliant", "outstanding", "satisfied",
]


class TriageEngine:
    def __init__(self, faq_path="data/faq.json"):
        self.faq_data = self._load_faq(faq_path)
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.questions = [item["question"] for item in self.faq_data]
        self.answers = [item["answer"] for item in self.faq_data]
        self.categories = [item.get("category", "General") for item in self.faq_data]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)

        # Check if OpenAI is available
        self.openai_client = None
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=api_key)
            except Exception:
                pass

    def _load_faq(self, path):
        """Load FAQ data from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def detect_sentiment(self, text):
        """
        Basic sentiment analysis using keyword matching.
        Returns: 'negative', 'positive', or 'neutral'
        """
        text_lower = text.lower()
        negative_count = sum(1 for word in NEGATIVE_KEYWORDS if word in text_lower)
        positive_count = sum(1 for word in POSITIVE_KEYWORDS if word in text_lower)

        if negative_count >= 2 or any(
            phrase in text_lower
            for phrase in ["i want to complain", "this is unacceptable", "speak to manager"]
        ):
            return "negative"
        elif positive_count >= 1:
            return "positive"
        return "neutral"

    def get_best_match(self, user_query, threshold=0.25):
        """
        Find the best matching FAQ for a user query.
        Returns the answer if similarity is above threshold, otherwise None.
        """
        query_vector = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        best_index = similarities.argmax()
        best_score = similarities[best_index]

        if best_score >= threshold:
            return {
                "matched_question": self.questions[best_index],
                "answer": self.answers[best_index],
                "category": self.categories[best_index],
                "confidence": round(float(best_score), 2),
            }
        return None

    def _get_gpt_response(self, user_query, context=None):
        """
        Use OpenAI GPT to generate a helpful response when FAQ doesn't match.
        Falls back to a static message if OpenAI is unavailable.
        """
        if not self.openai_client:
            return None

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and professional customer support assistant. "
                    "Provide helpful, concise answers. If you cannot help with something, "
                    "politely suggest the customer contact a human agent. "
                    "Keep responses under 3 sentences."
                ),
            }
        ]

        # Add conversation context if available
        if context:
            for msg in context:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})

        messages.append({"role": "user", "content": user_query})

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return None

    def classify_query(self, user_query, context=None):
        """
        Classify the query and return an appropriate response.

        Flow:
        1. Check sentiment — escalate if very negative
        2. Try FAQ matching
        3. Fall back to OpenAI GPT
        4. Final fallback: human escalation message
        """
        sentiment = self.detect_sentiment(user_query)

        # If customer is very frustrated, prioritize escalation
        if sentiment == "negative":
            match = self.get_best_match(user_query)
            answer_text = ""
            if match and match["confidence"] >= 0.4:
                answer_text = match["answer"] + " "

            return {
                "type": "escalation",
                "sentiment": sentiment,
                "response": (
                    f"I understand your frustration and I sincerely apologize for the inconvenience. "
                    f"{answer_text}"
                    f"I am prioritizing your request — a human support agent will be with you shortly. "
                    f"You can also reach us directly at support@example.com."
                ),
                "category": match["category"] if match else "General",
            }

        # Try FAQ match
        match = self.get_best_match(user_query)
        if match:
            return {
                "type": "faq",
                "sentiment": sentiment,
                "response": match["answer"],
                "category": match["category"],
                "confidence": match["confidence"],
                "matched_question": match["matched_question"],
            }

        # Try OpenAI GPT fallback
        gpt_response = self._get_gpt_response(user_query, context)
        if gpt_response:
            return {
                "type": "ai",
                "sentiment": sentiment,
                "response": gpt_response,
                "category": "General",
            }

        # Final fallback
        return {
            "type": "escalation",
            "sentiment": sentiment,
            "response": (
                "I appreciate your question! I wasn't able to find a specific answer for that. "
                "Let me connect you with a human support agent who can help you better. "
                "You can also email us at support@example.com or call +91-1234567890."
            ),
            "category": "General",
        }

    def get_categories(self):
        """Get all unique FAQ categories."""
        return sorted(set(self.categories))

    def get_suggestions(self):
        """Get a list of common questions as quick-reply suggestions."""
        suggestions = [
            "What are your business hours?",
            "How do I track my order?",
            "What is your refund policy?",
            "How do I reset my password?",
            "How much does shipping cost?",
        ]
        return suggestions
