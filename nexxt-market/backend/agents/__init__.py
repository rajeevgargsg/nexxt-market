"""
NexxtMarket AI Agents — Listing Optimizer, Buyer Matcher, Trust, Conversation
All use Groq (free tier) for LLM inference.
"""
import json
import httpx
import numpy as np
from typing import List, Optional
from config import get_settings

settings = get_settings()


# ─── Base LLM Call ────────────────────────────────────────────────────────────

async def groq_json(system: str, user: str, max_tokens: int = 500) -> dict:
    """Call Groq and expect JSON back."""
    headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        text = r.json()["choices"][0]["message"]["content"].strip()
        # Clean markdown fences if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)


# ─── 1. Listing Optimization Agent ────────────────────────────────────────────

LISTING_OPTIMIZER_SYSTEM = """You are a marketplace listing optimization expert.
You analyze listings and return ONLY valid JSON with these exact keys:
{
  "optimized_title": "...",
  "optimized_description": "...",
  "suggested_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "suggested_price": 0.0,
  "deal_score": 0,
  "weak_points": ["..."],
  "strong_points": ["..."],
  "conversion_probability": "low|medium|high"
}
Rules:
- Title: max 70 chars, include key specs
- Description: 3-4 sentences, highlight condition and value
- Tags: relevant search terms buyers use
- Deal score: 0-100 (100 = exceptional deal)
- Be specific and factual. No fluff."""


async def optimize_listing(listing_data: dict) -> dict:
    """Analyze and optimize a listing using AI."""
    user = f"""
Listing to optimize:
Title: {listing_data.get('title')}
Description: {listing_data.get('description')}
Price: ${listing_data.get('price')}
Category: {listing_data.get('category', 'General')}
Condition: {listing_data.get('condition', 'Not specified')}
Location: {listing_data.get('location', 'Not specified')}
Images count: {len(listing_data.get('images', []))}

Return optimized listing as JSON only.
"""
    try:
        return await groq_json(LISTING_OPTIMIZER_SYSTEM, user, max_tokens=600)
    except Exception as e:
        return {
            "optimized_title": listing_data.get("title"),
            "optimized_description": listing_data.get("description"),
            "suggested_tags": [],
            "suggested_price": listing_data.get("price"),
            "deal_score": 50,
            "weak_points": [],
            "strong_points": [],
            "conversion_probability": "medium",
            "error": str(e)
        }


# ─── 2. Buyer Matching Agent ───────────────────────────────────────────────────

async def get_hf_embedding(text: str) -> List[float]:
    """Get embedding from HuggingFace free API."""
    headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
    payload = {"inputs": text}
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            f"https://api-inference.huggingface.co/pipeline/feature-extraction/{settings.embedding_model}",
            headers=headers,
            json=payload,
        )
        data = r.json()
        if isinstance(data, list) and isinstance(data[0], list):
            return data[0]  # First sentence embedding
        return data


def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


async def rank_listings_for_user(user_history: List[str], listings: List[dict]) -> List[dict]:
    """
    Rank listings by semantic similarity to user's browsing history.
    Falls back to recency if HF key not set.
    """
    if not settings.huggingface_api_key or not user_history:
        return listings  # Fallback: return as-is

    # Build user preference embedding
    user_text = " ".join(user_history[:10])  # Last 10 interactions
    try:
        user_emb = await get_hf_embedding(user_text)
    except Exception:
        return listings

    # Score each listing
    scored = []
    for listing in listings:
        listing_text = f"{listing.get('title', '')} {listing.get('description', '')} {listing.get('category', '')}"
        try:
            listing_emb = await get_hf_embedding(listing_text)
            score = cosine_similarity(user_emb, listing_emb)
        except Exception:
            score = 0.5
        scored.append({**listing, "_match_score": score})

    scored.sort(key=lambda x: x.get("_match_score", 0), reverse=True)
    return scored


# ─── 3. Trust & Fraud Detection Agent ─────────────────────────────────────────

FRAUD_DETECTION_SYSTEM = """You are a marketplace fraud detection expert.
Analyze the listing and return ONLY valid JSON:
{
  "risk_level": "low|medium|high|critical",
  "risk_score": 0,
  "flags": ["..."],
  "recommendation": "approve|review|reject",
  "reason": "..."
}
Risk indicators: unrealistic pricing, suspicious descriptions, common scam patterns,
mismatched category/price, too-good-to-be-true offers, urgent pressure language."""


async def analyze_listing_trust(listing_data: dict) -> dict:
    """Analyze listing for fraud and trust signals."""
    user = f"""
Analyze this listing for fraud/trust issues:
Title: {listing_data.get('title')}
Description: {listing_data.get('description')}
Price: ${listing_data.get('price')}
Category: {listing_data.get('category')}
Seller history: {listing_data.get('seller_total_sales', 0)} sales, {listing_data.get('seller_trust_score', 50)} trust score

Return risk assessment as JSON only.
"""
    try:
        return await groq_json(FRAUD_DETECTION_SYSTEM, user, max_tokens=200)
    except Exception:
        return {"risk_level": "low", "risk_score": 20, "flags": [], "recommendation": "approve", "reason": "Standard listing"}


def calculate_seller_trust_score(seller_data: dict) -> float:
    """Rule-based seller trust score (0-100)."""
    score = 50.0

    # Positive signals
    score += min(seller_data.get("total_sales", 0) * 2, 20)
    score += 10 if seller_data.get("is_verified") else 0
    score += seller_data.get("response_rate", 0) * 10
    score -= max(0, (seller_data.get("avg_response_time_mins", 0) - 60) * 0.1)

    return max(0, min(100, score))


# ─── 4. Conversation Agent ────────────────────────────────────────────────────

CONVERSATION_SYSTEM = """You are a marketplace conversation assistant helping buyers close deals.
Generate a SHORT, helpful reply suggestion (max 30 words).
Be direct, friendly, and push toward a deal. No fluff."""


async def suggest_reply(
    listing_title: str,
    conversation_history: List[dict],
    role: str = "buyer"  # or "seller"
) -> str:
    """Suggest a reply in a conversation to move toward deal closure."""
    history_text = "\n".join([
        f"{m.get('role', 'user')}: {m.get('content', '')}"
        for m in conversation_history[-5:]  # Last 5 messages
    ])

    user = f"""
Listing: {listing_title}
Conversation so far:
{history_text}

You are the {role}. Suggest a short, helpful next message that moves toward closing the deal.
"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": settings.groq_model,
                    "messages": [
                        {"role": "system", "content": CONVERSATION_SYSTEM},
                        {"role": "user", "content": user}
                    ],
                    "max_tokens": 80,
                    "temperature": 0.8,
                }
            )
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        if role == "buyer":
            return "Is this still available? Can we arrange a viewing today?"
        return "Yes, still available! When would you like to meet?"


async def summarize_conversation(messages: List[dict]) -> str:
    """Summarize a conversation thread."""
    if not messages:
        return "No messages yet."

    history = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in messages])
    user = f"Summarize this marketplace conversation in 2 sentences:\n{history}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"},
                json={
                    "model": settings.groq_model,
                    "messages": [
                        {"role": "system", "content": "Summarize marketplace conversations concisely."},
                        {"role": "user", "content": user}
                    ],
                    "max_tokens": 100,
                }
            )
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return f"Conversation with {len(messages)} messages about the listing."
