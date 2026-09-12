"""AI Message Assistant supporting Analyze and Improve modes."""

import os
import re
from typing import Dict, Any, List, Tuple
import requests

from app.ai.prompt_builder import (
    build_message_analysis_prompt,
    build_message_improvement_prompt,
)
from app.database.database import db

class MessageAssistantService:
    """Provides message analysis and tone-based rewriting."""
    
    @classmethod
    def analyze_message(
        cls, message: str, api_key: str = "", provider: str = "gemini"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Analyzes tone, clarity, pressure, and naturalness of a message."""
        prompt = build_message_analysis_prompt(message)
        key_to_use = (api_key or os.getenv("LLM_API_KEY", "")).strip()
        
        raw_text = ""
        source = "offline_engine"
        
        if key_to_use:
            try:
                raw_text = cls._call_llm(prompt, key_to_use, provider)
                source = "live_llm"
            except Exception as e:
                print(f"[Message Assistant] API error: {e}. Using offline engine.")
                raw_text = cls._offline_analyze(message)
        else:
            raw_text = cls._offline_analyze(message)
            
        metrics = cls._parse_analysis(raw_text, message)
        
        if os.getenv("SAVE_AI_HISTORY", "true").lower() in ("true", "1", "yes"):
            try:
                db.save_ai_history("message_analysis", f"Msg: {message[:60]}...", raw_text)
            except Exception as e:
                print(f"[Message Assistant] DB save error: {e}")
                
        metrics["source"] = source
        metrics["raw_text"] = raw_text
        return True, "Analysis complete.", metrics

    @classmethod
    def improve_message(
        cls, message: str, tone: str, api_key: str = "", provider: str = "gemini"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Generates alternative versions of the message matching the selected tone."""
        prompt = build_message_improvement_prompt(message, tone)
        key_to_use = (api_key or os.getenv("LLM_API_KEY", "")).strip()
        
        raw_text = ""
        source = "offline_engine"
        
        if key_to_use:
            try:
                raw_text = cls._call_llm(prompt, key_to_use, provider)
                source = "live_llm"
            except Exception as e:
                print(f"[Message Assistant] API error: {e}. Using offline rewriter.")
                raw_text = cls._offline_improve(message, tone)
        else:
            raw_text = cls._offline_improve(message, tone)
            
        options = cls._parse_improvements(raw_text, message, tone)
        
        if os.getenv("SAVE_AI_HISTORY", "true").lower() in ("true", "1", "yes"):
            try:
                db.save_ai_history("message_improve", f"Tone: {tone} | {message[:50]}...", raw_text)
            except Exception as e:
                print(f"[Message Assistant] DB save error: {e}")
                
        return True, "Alternatives generated.", {
            "source": source,
            "tone": tone,
            "options": options,
            "raw_text": raw_text
        }

    @classmethod
    def _call_llm(cls, prompt: str, api_key: str, provider: str) -> str:
        """Helper to invoke external LLM."""
        if provider.lower() == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
            }
            resp = requests.post(url, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are LoveAI, an expert communication coach."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    @classmethod
    def _offline_analyze(cls, message: str) -> str:
        """Rule-based smart analysis when running offline."""
        msg_len = len(message)
        has_question = "?" in message
        is_all_caps = message.isupper() and msg_len > 6
        exclamation_count = message.count("!")
        
        # Pressure evaluation
        urgent_words = ["urgently", "now", "reply", "answer me", "asap", "why didn't you", "promise"]
        pressure_hits = sum(1 for w in urgent_words if w in message.lower())
        
        if is_all_caps or pressure_hits >= 2:
            pressure = "High"
            tone = "Intense / Demanding"
            naturalness = "Awkward"
            feedback = (
                "The message contains urgent phrasing that may feel pressured or overwhelming. "
                "Consider softening the request and giving the other person space to reply when free."
            )
        elif pressure_hits == 1 or exclamation_count > 3:
            pressure = "Medium"
            tone = "Eager"
            naturalness = "Acceptable"
            feedback = (
                "The message conveys enthusiasm, but could easily come across as slightly forward. "
                "Relaxing the exclamation marks will make it sound smoother."
            )
        else:
            pressure = "Low"
            tone = "Casual & Friendly"
            naturalness = "Natural"
            feedback = (
                "The message is relaxed, low-pressure, and conversational. "
                "It leaves room for the other person to respond naturally without feeling put on the spot."
            )
            
        clarity = "High" if (15 <= msg_len <= 250 and not is_all_caps) else ("Medium" if msg_len > 250 else "Moderate")
        
        return f"""Tone: {tone}
Clarity: {clarity}
Pressure: {pressure}
Naturalness: {naturalness}
AI Feedback: {feedback}"""

    @classmethod
    def _offline_improve(cls, message: str, tone: str) -> str:
        """Context-tailored message rewrites for offline mode."""
        clean = message.strip().rstrip(".!?")
        tone_lower = tone.lower()
        
        if tone_lower == "casual":
            opt1 = f"Hey, {clean.lower()} if you're free!"
            opt2 = f"Hey! Just wondering, {clean.lower()}?"
            opt3 = f"No rush at all, but {clean.lower()} whenever you're around."
        elif tone_lower == "friendly":
            opt1 = f"Hey there! Hope your week is going great — {clean.lower()}?"
            opt2 = f"Hey! Would love to catch up soon. {clean} 😊"
            opt3 = f"Hey, was just thinking of you! {clean}?"
        elif tone_lower == "funny":
            opt1 = f"Plot twist: {clean.lower()}? (Or is that too adventurous? 😄)"
            opt2 = f"Promise this isn't a spam bot, but {clean.lower()}? 😂"
            opt3 = f"Scale of 1-10, how down are you to {clean.lower()}?"
        elif tone_lower == "confident":
            opt1 = f"Hey, let's {clean.lower()} sometime this week. Are you free Thursday?"
            opt2 = f"I'd really like to {clean.lower()} together. Let me know what your schedule looks like!"
            opt3 = f"Hey! Let's make time to {clean.lower()}. When works best for you?"
        elif tone_lower == "sweet":
            opt1 = f"Hey! Really enjoyed our chat earlier and wanted to ask: {clean.lower()}? ✨"
            opt2 = f"Hope you're having a lovely day! Would be really nice if we could {clean.lower()}."
            opt3 = f"Hey, always appreciate talking to you. Would love to {clean.lower()} soon."
        elif tone_lower == "direct":
            opt1 = f"Hey, are you free to {clean.lower()} this weekend?"
            opt2 = f"Would you like to {clean.lower()} together?"
            opt3 = f"Let's {clean.lower()}. Let me know if you're interested!"
        elif tone_lower == "short":
            opt1 = f"Hey, down to {clean.lower()}?"
            opt2 = f"{clean.capitalize()}?"
            opt3 = f"Free to {clean.lower()} sometime?"
        else:
            opt1 = f"Hey, {clean}!"
            opt2 = f"Would love to {clean.lower()} when you're free."
            opt3 = f"Hey! Let me know if you'd like to {clean.lower()}."
            
        return f"""Option 1: {opt1}
Option 2: {opt2}
Option 3: {opt3}"""

    @classmethod
    def _parse_analysis(cls, text: str, original: str) -> Dict[str, str]:
        """Extracts key metrics and feedback from analysis text."""
        tone_m = re.search(r"Tone:\s*([^\n\r]+)", text, re.IGNORECASE)
        clarity_m = re.search(r"Clarity:\s*([^\n\r]+)", text, re.IGNORECASE)
        pressure_m = re.search(r"Pressure:\s*([^\n\r]+)", text, re.IGNORECASE)
        natural_m = re.search(r"Naturalness:\s*([^\n\r]+)", text, re.IGNORECASE)
        feedback_m = re.search(r"AI Feedback:\s*([\s\S]+)", text, re.IGNORECASE)
        
        return {
            "tone": tone_m.group(1).strip() if tone_m else "Friendly",
            "clarity": clarity_m.group(1).strip() if clarity_m else "High",
            "pressure": pressure_m.group(1).strip() if pressure_m else "Low",
            "naturalness": natural_m.group(1).strip() if natural_m else "Natural",
            "feedback": feedback_m.group(1).strip() if feedback_m else (
                "The message is conversational and clear. Keep it light and authentic!"
            ),
        }

    @classmethod
    def _parse_improvements(cls, text: str, original: str, tone: str) -> List[str]:
        """Extracts the 3 generated rewrite options."""
        options = []
        matches = re.findall(r"Option\s*\d+:?\s*([^\n\r]+)", text, re.IGNORECASE)
        for m in matches:
            clean = m.strip().strip('"').strip("'")
            if clean:
                options.append(clean)
                
        if not options:
            # Fallback if unformatted text
            lines = [l.strip() for l in text.split("\n") if l.strip() and not l.startswith("#")]
            options = lines[:3]
            
        while len(options) < 3:
            options.append(f"{original} ({tone} style)")
            
        return options[:3]
