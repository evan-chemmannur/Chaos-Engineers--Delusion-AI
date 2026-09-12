"""AI Relationship Advisor engine with API integration and smart offline fallback."""

import os
import re
import json
from typing import List, Dict, Any, Tuple
import requests

from app.ai.prompt_builder import build_advisor_prompt
from app.database.database import db

class AIAdvisorService:
    """Generates personalized relationship roadmaps using LLM or smart fallback."""
    
    @classmethod
    def generate_roadmap(
        cls,
        relationship_status: str,
        communication_freq: str,
        interests: List[str],
        goal: str,
        situation: str,
        api_key: str = "",
        provider: str = "gemini"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Generates a structured roadmap for the user's relationship situation.
        
        Returns:
            (success, message, result_dict)
        """
        prompt = build_advisor_prompt(
            relationship_status, communication_freq, interests, goal, situation
        )
        
        key_to_use = (api_key or os.getenv("LLM_API_KEY", "")).strip()
        raw_text = ""
        source = "offline_engine"
        
        # If API key is available, try external API call
        if key_to_use:
            try:
                raw_text = cls._call_external_llm(prompt, key_to_use, provider)
                source = "live_llm"
            except Exception as e:
                # Graceful fallback on API failure
                print(f"[AI Advisor] External API error: {e}. Switching to offline intelligence.")
                raw_text = cls._generate_offline_roadmap(
                    relationship_status, communication_freq, interests, goal, situation
                )
        else:
            # Intelligent offline fallback
            raw_text = cls._generate_offline_roadmap(
                relationship_status, communication_freq, interests, goal, situation
            )
            
        parsed_steps, reminder = cls._parse_roadmap_response(raw_text)
        
        # Save to database history if enabled
        if os.getenv("SAVE_AI_HISTORY", "true").lower() in ("true", "1", "yes"):
            summary = f"Status: {relationship_status} | Goal: {goal} | Situation: {situation[:60]}..."
            try:
                db.save_ai_history("advisor", summary, raw_text)
            except Exception as e:
                print(f"[AI Advisor] DB log error: {e}")
                
        result = {
            "source": source,
            "steps": parsed_steps,
            "reminder": reminder,
            "raw_text": raw_text,
            "goal": goal,
            "relationship_status": relationship_status,
        }
        
        return True, "Roadmap generated successfully.", result

    @classmethod
    def _call_external_llm(cls, prompt: str, api_key: str, provider: str) -> str:
        """Invokes external LLM API (Google Gemini or OpenAI compatible)."""
        if provider.lower() == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
            }
            resp = requests.post(url, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # OpenAI compatible endpoint
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are LoveAI, a helpful relationship guidance advisor."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    @classmethod
    def _generate_offline_roadmap(
        cls, status: str, freq: str, interests: List[str], goal: str, situation: str
    ) -> str:
        """Context-aware deterministic roadmap generator when offline or without API key."""
        int_str = interests[0] if interests else "shared interests"
        
        step_templates = [
            (
                "01 — Start natural, low-pressure conversations",
                f"Begin by making brief, casual remarks when opportunities naturally arise. Since you are currently {status.lower()}, keep the tone light and avoid over-investing in every message."
            ),
            (
                "02 — Build organic familiarity",
                f"Find common conversation hooks around {int_str}. Share interesting observations or ask open-ended questions about their opinions without interrogating them."
            ),
            (
                "03 — Observe and gauge mutual effort",
                "Pay attention to their engagement. Are they asking questions back, contributing energy, or keeping answers brief? Connection requires enthusiastic two-way participation."
            ),
            (
                "04 — Suggest a low-stakes casual activity",
                f"Towards your goal to '{goal.lower()}', propose something relaxed related to your topics (e.g. coffee, checking out {int_str}, or group study) with clear opt-out freedom."
            ),
            (
                "05 — Communicate your interest with honesty and clarity",
                "If conversations progress comfortably, be authentic about enjoying their company. Avoid mind games or ambiguity; clear intentions are attractive and respectful."
            ),
            (
                "06 — Respect their response with grace",
                "Whatever their reaction, receive it with maturity. If enthusiastic, celebrate the progress; if hesitant or declining, honor their boundaries immediately without pressure."
            )
        ]
        
        output_lines = ["🤖 YOUR PERSONALIZED ROADMAP\n"]
        for title, desc in step_templates:
            output_lines.append(f"{title}\n{desc}\n")
            
        output_lines.append(
            "Mindset Reminder: Genuine connection cannot be rushed or coerced. "
            "Stay true to yourself, respect their feelings, and remember your self-worth is independent of the outcome."
        )
        return "\n".join(output_lines)

    @classmethod
    def _parse_roadmap_response(cls, text: str) -> Tuple[List[Dict[str, str]], str]:
        """Parses formatted roadmap text into structured UI steps."""
        steps = []
        reminder = (
            "Genuine connection cannot be rushed. Respect boundaries and keep communication authentic."
        )
        
        # Regex to find steps like '01 — Title' or 'Step 1: Title'
        pattern = r"(?:(?:0?[1-6]|Step\s*[1-6])[\s:—\-]+)([^\n\r]+)([\s\S]*?)(?=(?:(?:0?[1-6]|Step\s*[1-6])[\s:—\-]+)|(?:Mindset\s*Reminder:?)|$)"
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        step_idx = 1
        for title, desc in matches:
            clean_title = title.strip().lstrip("—-: ").strip()
            clean_desc = desc.strip()
            if clean_title:
                steps.append({
                    "step_num": f"0{step_idx}" if step_idx < 10 else str(step_idx),
                    "title": clean_title,
                    "description": clean_desc
                })
                step_idx += 1
                
        # If regex missed or unusual LLM format, create readable fallback chunks
        if not steps:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for i, line in enumerate(lines[:6]):
                steps.append({
                    "step_num": f"0{i+1}",
                    "title": f"Step {i+1}",
                    "description": line
                })
                
        # Extract Mindset Reminder if present
        reminder_match = re.search(r"Mindset\s*Reminder:\s*([^\n\r]+.*)", text, re.IGNORECASE)
        if reminder_match:
            reminder = reminder_match.group(1).strip()
            
        return steps, reminder
