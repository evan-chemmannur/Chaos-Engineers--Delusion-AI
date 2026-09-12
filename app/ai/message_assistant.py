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
        """Helper to invoke external LLM with support for Gemini, Ollama, and OpenAI."""
        prov = provider.lower().strip()
        if prov == "gemini" or prov == "":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
            }
            resp = requests.post(url, json=payload, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        elif prov == "ollama":
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": api_key if (api_key and not api_key.startswith("AIza")) else "llama3",
                "prompt": prompt,
                "stream": False
            }
            resp = requests.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json().get("response", "")
        else:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "gpt-4o-mini" if "gpt-4" in prov else "gpt-3.5-turbo",
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
        """Dynamic contextual NLP semantic analysis engine for Malayalam, Manglish, and English.
        Evaluates real parameters: tone, clarity, pressure, naturalness, intent, and actionable guidance."""
        text = message.strip()
        msg_lower = text.lower()
        msg_len = len(text)
        
        # 1. Detect language / script
        has_malayalam = bool(re.search(r"[\u0d00-\u0d7f]", text))
        
        # 2. Key patterns
        has_question = "?" in text or any(w in msg_lower for w in [
            "ഉണ്ടോ", "ആണോ", "വരുമോ", "കഴിയുമോ", "പറ്റുമോ", "തോന്നുന്നുണ്ടോ", "എപ്പോഴാ",
            "പോവാമോ", "ചെയ്യുമോ", "undo", "aano", "varumo", "patto", "kazhiyumo",
            "down to", "free to", "would you", "do you", "are you", "can you"
        ])
        
        has_softener = any(w in msg_lower for w in [
            "സമയം ഉണ്ടോ", "സൗകര്യമാണെങ്കിൽ", "വിഷമമില്ലെങ്കിൽ", "ഫ്രീയാണെങ്കിൽ", "താൽപര്യമുണ്ടെങ്കിൽ",
            "if you're free", "if you want", "no pressure", "no rush", "whenever", "no worries",
            "just wondering", "samayam undo", "free aanel", "freel aanel", "peace", "casual"
        ])
        
        has_urgency = any(w in msg_lower for w in [
            "ഇപ്പൊ തന്നെ", "വേഗം", "ഉടൻ", "മറുപടി തരൂ", "എന്താ മിണ്ടാത്തത്", "നിർബന്ധം",
            "reply now", "asap", "urgently", "answer me", "why didn't you", "why aren't you",
            "answer now", "pick up", "seen zone", "vegam", "ippo thanne", "udan"
        ])
        
        has_coffee_hangout = any(w in msg_lower for w in [
            "coffee", "tea", "ചായ", "കാപ്പി", "കുടിക്കാൻ", "കഴിക്കാമോ", "ഭക്ഷണം", "food",
            "പഠിക്കാൻ", "study", "meet", "hangout", "cinema", "ഒരുമിച്ച്", "കാണാൻ",
            "together", "orumich", "kudikkan", "padikkan"
        ])
        
        has_romance = any(w in msg_lower for w in [
            "ഇഷ്ടം", "സ്നേഹം", "പ്രണയം", "ഹൃദയം", "love", "crush", "cute", "miss you",
            "beautiful", "special", "feelings", "ishttam", "sneham", "date"
        ])
        
        has_anxiety = any(w in msg_lower for w in [
            "ദേഷ്യമാണോ", "വെറുപ്പാണോ", "sorry", "ക്ഷമിക്കണം", "do you hate me", "angry", "disturb", "വിഷമമായോ"
        ])
        
        has_specific_time = any(w in msg_lower for w in [
            "വ്യാഴാഴ്ച", "വെള്ളിയാഴ്ച", "ശനിയാഴ്ച", "ഞായറാഴ്ച", "തിങ്കളാഴ്ച", "ചൊവ്വാഴ്ച", "ബുധനാഴ്ച",
            "thursday", "friday", "saturday", "sunday", "monday", "tuesday", "wednesday",
            "ഇന്ന്", "നാളെ", "മറ്റന്നാൾ", "weekend", "വൈകുന്നേരം", "today", "tomorrow", "evening"
        ])
        
        exclamations = text.count("!")
        is_all_caps = text.isupper() and msg_len > 8
        
        # 3. Dynamic Pressure calculation
        if is_all_caps or has_urgency:
            pressure_val = "High (85%)"
        elif has_softener:
            pressure_val = "Low (15%)"
        elif has_question:
            pressure_val = "Low-Medium (28%)"
        elif exclamations >= 3:
            pressure_val = "Medium (55%)"
        else:
            pressure_val = "Medium (38%)"
            
        # 4. Dynamic Tone calculation
        if has_urgency or is_all_caps:
            tone_val = "Intense / Demanding"
        elif has_romance:
            tone_val = "Warm & Romantic"
        elif has_coffee_hangout and (has_softener or has_question):
            tone_val = "Warm & Casual"
        elif has_anxiety:
            tone_val = "Hesitant & Anxious"
        elif has_question:
            tone_val = "Friendly & Curious"
        else:
            tone_val = "Conversational & Casual"
            
        # 5. Dynamic Clarity calculation
        if has_specific_time and (has_coffee_hangout or has_question):
            clarity_val = "High (94%)"
        elif has_coffee_hangout or has_question or (15 <= msg_len <= 180):
            clarity_val = "High (82%)"
        elif msg_len < 10:
            clarity_val = "Low (35%)"
        else:
            clarity_val = "Moderate (68%)"
            
        # 6. Dynamic Naturalness calculation
        if is_all_caps or (exclamations > 3 and msg_len < 30):
            natural_val = "Awkward"
        elif has_malayalam or (has_coffee_hangout and has_softener):
            natural_val = "Natural & Authentic"
        else:
            natural_val = "Natural"
            
        # 7. Dynamic AI Feedback tailored to the exact message entities
        feedback_parts = []
        if has_coffee_hangout:
            if has_specific_time:
                feedback_parts.append(
                    "നിർദ്ദിഷ്ട ദിവസവും കാപ്പിയോ പഠനമോ പോലെ ഒരു casual activity-യും ഉൾപ്പെടുത്തിയത് വളരെ വ്യക്തവും ആകർഷകവുമാണ്."
                )
            else:
                feedback_parts.append(
                    "ഒരുമിച്ച് സമയം ചിലവഴിക്കാനുള്ള ആഗ്രഹം വളരെ സ്വാഭാവികമായി പങ്കുവെച്ചിട്ടുണ്ട്."
                )
        if has_softener:
            feedback_parts.append(
                "മറുപടി നൽകാൻ recipient-ന് മേൽ യാതൊരു സമ്മർദ്ദവും നൽകാതെ സ്വാതന്ത്ര്യം നൽകുന്നു (Low pressure)."
            )
        elif has_urgency:
            feedback_parts.append(
                "സന്ദേശത്തിൽ അല്പം തിടുക്കമോ അടിയന്തിര ഭാവമോ കാണപ്പെടുന്നു. ഇത് കുറച്ചുകൂടി ശാന്തമാക്കുന്നത് നന്നായിരിക്കും."
            )
        elif has_romance:
            feedback_parts.append(
                "മനസ്സിലുള്ള വികാരം മനോഹരമായി പ്രകടിപ്പിക്കുന്നു. മറ്റൊരാളുടെ പ്രതികരണത്തിന് സമയം നൽകി ക്ഷമയോടെ കാത്തിരിക്കുക."
            )
            
        if not feedback_parts:
            feedback_parts.append("സന്ദേശം വ്യക്തവും സൗഹൃദപരവുമാണ്.")
            
        feedback_parts.append("മറുപടി ഉടൻ വന്നില്ലെങ്കിലും പരിഭ്രാന്തരാകാതെ സമയം നൽകുക. All the best! 💕")
        feedback_str = " ".join(feedback_parts)
        
        return f"""Tone: {tone_val}
Clarity: {clarity_val}
Pressure: {pressure_val}
Naturalness: {natural_val}
AI Feedback: {feedback_str}"""

    @classmethod
    def _offline_improve(cls, message: str, tone: str) -> str:
        """Context-tailored, language-aware message rewrites for offline/live mode."""
        clean = message.strip().rstrip(".!?")
        tone_lower = tone.lower().strip()
        has_malayalam = bool(re.search(r"[\u0d00-\u0d7f]", clean))
        
        if has_malayalam:
            # Contextual Malayalam adaptations
            if "coffee" in clean.lower() or "പഠിക്കാൻ" in clean or "കുടിക്കാൻ" in clean:
                if tone_lower == "casual":
                    opt1 = "Hey! ഫ്രീയാണെങ്കിൽ നമുക്ക് ഒന്ന് meet ചെയ്താലോ? Coffee or casual study session?"
                    opt2 = "തിരക്കില്ലാത്തപ്പോഴേക്കും സമയം കിട്ടുമെങ്കിൽ ഒരു coffee കുടിക്കാം, what say?"
                    opt3 = "Hey, just checking — ഈ ആഴ്ച casual ആയി coffee കുടിക്കാൻ സമയമുണ്ടോ?"
                elif tone_lower == "friendly":
                    opt1 = "Hey! ഒരുമിച്ച് coffee കുടിക്കാനും സംസാരിക്കാനും താല്പര്യമുണ്ടെങ്കിൽ പറയണേ 😊"
                    opt2 = "കുറേ നാളായി സംസാരിച്ചിട്ട്! ഫ്രീയാണെങ്കിൽ ഒരുമിച്ച് പഠിക്കാനോ കാപ്പി കുടിക്കാനോ ഇറങ്ങാം."
                    opt3 = "Hey there! Hope your week is going great — coffee break-ന് സമയമുണ്ടോ?"
                elif tone_lower == "funny":
                    opt1 = "പഠിക്കാൻ ഒരു partner-നെ നോക്കുന്നു... കൂടെ ഒരു അടിപൊളി coffee-യും! Down ആണോ? 😄"
                    opt2 = "Plot twist: നമ്മൾ ഒരുമിച്ച് coffee കുടിക്കുന്നു! താല്പര്യമുണ്ടോ? 😂"
                    opt3 = "Scale of 1-10, ഈ ആഴ്ച ഒരു coffee break-ന് എത്ര മാർക്ക് കൊടുക്കും?"
                elif tone_lower == "confident":
                    opt1 = "നമുക്ക് ഒരുമിച്ച് coffee കുടിക്കാം. What time works best for you?"
                    opt2 = "ഒരുമിച്ച് പഠിക്കാനും സംസാരിക്കാനും നല്ലൊരു സമയമാണ്. എപ്പോൾ meet ചെയ്യാം?"
                    opt3 = "Let's grab a coffee this week! ഏത് ദിവസമാണ് കൂടുതൽ സൗകര്യം?"
                elif tone_lower == "sweet":
                    opt1 = "Hey! തിരക്കില്ലെങ്കിൽ ഒരുമിച്ച് coffee കുടിക്കാൻ സമയം കിട്ടുമോ? Looking forward to it ✨"
                    opt2 = "സംസാരിക്കാൻ എപ്പോഴും നല്ല സന്തോഷമാണ്. സൗകര്യപ്രദമായ സമയത്ത് ഒന്ന് കാണാമോ?"
                    opt3 = "ഒരു ചെറിയ coffee & study break കിട്ടിയാൽ വളരെ സന്തോഷമാകും 💕"
                elif tone_lower == "direct":
                    opt1 = "ഈ ആഴ്ച coffee കുടിക്കാൻ സമയമുണ്ടോ?"
                    opt2 = "ഒരുമിച്ച് പഠിക്കാനോ സംസാരിക്കാനോ free ആണോ? Let me know!"
                    opt3 = "Would you like to get coffee sometime this week?"
                elif tone_lower == "short":
                    opt1 = "Coffee & study? ഫ്രീയാണോ?"
                    opt2 = "ഈ ആഴ്ച coffee കുടിച്ചാലോ? ☕"
                    opt3 = "Free for coffee this week?"
                else:
                    opt1 = f"{clean} — സമയം കിട്ടുമ്പോൾ പറയണേ!"
                    opt2 = f"Hey! {clean} 😊"
                    opt3 = f"Free ആണെങ്കിൽ {clean}?"
            else:
                if tone_lower == "casual":
                    opt1 = f"Hey! {clean}, ഫ്രീയാണെങ്കിൽ പറയണേ!"
                    opt2 = f"Just checking — {clean}?"
                    opt3 = f"തിരക്കൊന്നുമില്ലെങ്കിൽ {clean}."
                elif tone_lower == "friendly":
                    opt1 = f"Hey there! {clean} 😊"
                    opt2 = f"{clean} — താല്പര്യമുണ്ടെങ്കിൽ പറയണേ!"
                    opt3 = f"Hope you're having a great day! {clean}?"
                elif tone_lower == "funny":
                    opt1 = f"Plot twist: {clean}! (Or is that too adventurous? 😄)"
                    opt2 = f"Promise this isn't spam, but {clean} 😂"
                    opt3 = f"Scale of 1-10, {clean} എത്ര മാർക്ക് കിട്ടും?"
                elif tone_lower == "confident":
                    opt1 = f"നമുക്ക് ഇത് ചെയ്യാം: {clean}. When works for you?"
                    opt2 = f"{clean} — I'd really love to make this happen."
                    opt3 = f"Let's catch up on this: {clean}."
                elif tone_lower == "sweet":
                    opt1 = f"Really enjoyed talking to you! {clean} ✨"
                    opt2 = f"{clean} — സമയം കിട്ടുമെങ്കിൽ വളരെ സന്തോഷം."
                    opt3 = f"Hope your day is going well! {clean} 💕"
                elif tone_lower == "direct":
                    opt1 = f"{clean} — താല്പര്യമുണ്ടോ?"
                    opt2 = f"Are you free for this: {clean}?"
                    opt3 = f"{clean}?"
                elif tone_lower == "short":
                    opt1 = f"{clean}?"
                    opt2 = f"Down for: {clean}?"
                    opt3 = f"Free for {clean}?"
                else:
                    opt1 = f"{clean} — let me know!"
                    opt2 = f"Hey! {clean}"
                    opt3 = f"{clean} whenever you're free."
        else:
            # English adaptations
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
                opt1 = f"Hey, let's {clean.lower()} sometime this week. Are you free?"
                opt2 = f"I'd really like to {clean.lower()} together. Let me know what works for you!"
                opt3 = f"Hey! Let's make time to {clean.lower()}. When works best?"
            elif tone_lower == "sweet":
                opt1 = f"Hey! Really enjoyed chatting with you and wanted to ask: {clean.lower()}? ✨"
                opt2 = f"Hope you're having a lovely day! Would be really nice if we could {clean.lower()}."
                opt3 = f"Hey, always appreciate talking to you. Would love to {clean.lower()} soon."
            elif tone_lower == "direct":
                opt1 = f"Hey, are you free to {clean.lower()}?"
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
        """Extracts key metrics and feedback from analysis text, handling varied markdown formats."""
        tone_m = re.search(r"\*{0,2}Tone\*{0,2}:\s*([^\n\r]+)", text, re.IGNORECASE)
        clarity_m = re.search(r"\*{0,2}Clarity\*{0,2}:\s*([^\n\r]+)", text, re.IGNORECASE)
        pressure_m = re.search(r"\*{0,2}Pressure\*{0,2}:\s*([^\n\r]+)", text, re.IGNORECASE)
        natural_m = re.search(r"\*{0,2}Naturalness\*{0,2}:\s*([^\n\r]+)", text, re.IGNORECASE)
        feedback_m = re.search(r"\*{0,2}AI Feedback\*{0,2}:\s*([\s\S]+)", text, re.IGNORECASE)
        
        def clean_val(val: str, default: str) -> str:
            if not val:
                return default
            v = val.strip().strip("*").strip("_").strip()
            return v if v else default

        return {
            "tone": clean_val(tone_m.group(1) if tone_m else "", "Warm & Friendly"),
            "clarity": clean_val(clarity_m.group(1) if clarity_m else "", "High (85%)"),
            "pressure": clean_val(pressure_m.group(1) if pressure_m else "", "Low (20%)"),
            "naturalness": clean_val(natural_m.group(1) if natural_m else "", "Natural"),
            "feedback": clean_val(feedback_m.group(1) if feedback_m else "", (
                "സന്ദേശം വ്യക്തവും സൗഹൃദപരവുമാണ്. മറ്റൊരാളുടെ സ്വാതന്ത്ര്യത്തെ മാനിക്കുന്ന നല്ലൊരു തുടക്കം! 💕"
            )),
        }

    @classmethod
    def _parse_improvements(cls, text: str, original: str, tone: str) -> List[str]:
        """Extracts the 3 generated rewrite options."""
        options = []
        matches = re.findall(r"(?:Option\s*\d+:?|\d+\.)\s*([^\n\r]+)", text, re.IGNORECASE)
        for m in matches:
            clean = m.strip().strip('"').strip("'").strip("*").strip()
            if clean and len(clean) > 3:
                options.append(clean)
                
        if not options:
            # Fallback if unformatted text
            lines = [l.strip().strip("*").strip() for l in text.split("\n") if l.strip() and not l.startswith("#")]
            options = lines[:3]
            
        while len(options) < 3:
            options.append(f"{original} ({tone} style)")
            
        return options[:3]
