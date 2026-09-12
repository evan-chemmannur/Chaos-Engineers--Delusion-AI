"""AI Relationship Advisor view for LoveAI."""

import threading
import tkinter as tk
import customtkinter as ctk
from typing import List

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_SECTION, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, BORDER_SUBTLE, DANGER_RED, SUCCESS_GREEN
)
from app.gui.components import CardFrame, DisclaimerBanner, TagSelector
from app.config import (
    RELATIONSHIP_STATUSES, COMMUNICATION_FREQUENCIES, DEFAULT_INTERESTS,
    ADVISOR_GOALS, GENERAL_DISCLAIMER
)
from app.ai.ai_advisor import AIAdvisorService
from app.core.validation import validate_situation_text

class AdvisorView(ctk.CTkScrollableFrame):
    """View providing structured questionnaire and personalized AI roadmap."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.last_result = None
        self._build_ui()

    def _build_ui(self):
        # 1. Header Card
        header = CardFrame(self)
        header.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, text="🤖 AI Relationship Advisor", font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 2), sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Receive tailored, respectful, and boundary-focused guidance for your unique connection.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        
        # 2. Questionnaire Card
        form = CardFrame(self)
        form.grid(row=1, column=0, padx=20, pady=6, sticky="ew")
        form.grid_columnconfigure((0, 1), weight=1)
        
        # Current Status
        ctk.CTkLabel(form, text="Current Relationship:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=20, pady=(16, 4), sticky="w"
        )
        self.cbo_status = ctk.CTkComboBox(
            form, values=RELATIONSHIP_STATUSES, height=36, fg_color=BG_INPUT, border_color=BORDER_SUBTLE
        )
        self.cbo_status.set(RELATIONSHIP_STATUSES[1]) # Default: Classmate
        self.cbo_status.grid(row=1, column=0, padx=(20, 10), pady=(0, 12), sticky="ew")
        
        # Communication Frequency
        ctk.CTkLabel(form, text="Communication Frequency:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY).grid(
            row=0, column=1, padx=(10, 20), pady=(16, 4), sticky="w"
        )
        self.cbo_freq = ctk.CTkComboBox(
            form, values=COMMUNICATION_FREQUENCIES, height=36, fg_color=BG_INPUT, border_color=BORDER_SUBTLE
        )
        self.cbo_freq.set(COMMUNICATION_FREQUENCIES[1]) # Default: Sometimes
        self.cbo_freq.grid(row=1, column=1, padx=(10, 20), pady=(0, 12), sticky="ew")
        
        # Primary Goal
        ctk.CTkLabel(form, text="What is your primary goal?", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY).grid(
            row=2, column=0, columnspan=2, padx=20, pady=(4, 4), sticky="w"
        )
        self.cbo_goal = ctk.CTkComboBox(
            form, values=ADVISOR_GOALS, height=36, fg_color=BG_INPUT, border_color=BORDER_SUBTLE
        )
        self.cbo_goal.set(ADVISOR_GOALS[3]) # Default: Ask them to hang out
        self.cbo_goal.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
        
        # Shared Interests
        ctk.CTkLabel(form, text="Common Interests / Conversation Hooks:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY).grid(
            row=4, column=0, columnspan=2, padx=20, pady=(4, 4), sticky="w"
        )
        self.tags = TagSelector(form, available_tags=DEFAULT_INTERESTS[:8])
        self.tags.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
        
        # Situation Description
        ctk.CTkLabel(form, text="Describe your situation in detail:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY).grid(
            row=6, column=0, columnspan=2, padx=20, pady=(4, 4), sticky="w"
        )
        self.txt_situation = ctk.CTkTextbox(
            form,
            height=110,
            fg_color=BG_INPUT,
            border_width=1,
            border_color=BORDER_SUBTLE,
            font=FONT_BODY
        )
        self.txt_situation.insert(
            "1.0",
            "We sit next to each other in class and talk about assignments, but haven't hung out outside of college yet. I'd like to invite them for coffee or study session without making things awkward."
        )
        self.txt_situation.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
        
        # Status / Error Label
        self.lbl_status = ctk.CTkLabel(form, text="", font=FONT_SMALL, text_color=DANGER_RED)
        self.lbl_status.grid(row=8, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="w")
        
        # Submit Button
        self.btn_submit = ctk.CTkButton(
            form,
            text="Generate Personalized Roadmap 🤖",
            font=FONT_BODY_BOLD,
            height=42,
            fg_color=ACCENT_PURPLE,
            hover_color=ACCENT_PURPLE_HOVER,
            corner_radius=8,
            command=self._on_generate
        )
        self.btn_submit.grid(row=9, column=0, columnspan=2, padx=20, pady=(4, 20), sticky="ew")
        
        # 3. Loading Indicator Card
        self.loading_card = CardFrame(self, fg_color="#181826")
        self.loading_card.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.loading_card.grid_columnconfigure(0, weight=1)
        self.lbl_loading = ctk.CTkLabel(
            self.loading_card,
            text="🤖 AI is thinking...\nAnalyzing your situation and structuring a respectful roadmap...",
            font=FONT_BODY_BOLD,
            text_color=ACCENT_PURPLE
        )
        self.lbl_loading.pack(pady=24)
        self.loading_card.grid_remove() # Hidden initially
        
        # 4. Roadmap Results Container (Hidden initially)
        self.results_container = CardFrame(self, fg_color="#151622", border_color="#36294d")
        self.results_container.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.results_container.grid_columnconfigure(0, weight=1)
        self.results_container.grid_remove()
        
        # 5. Mandatory Disclaimer
        disclaimer = DisclaimerBanner(self, GENERAL_DISCLAIMER)
        disclaimer.grid(row=4, column=0, padx=20, pady=(10, 24), sticky="ew")

    def _on_generate(self):
        situation = self.txt_situation.get("1.0", "end").strip()
        valid, err, clean_situation = validate_situation_text(situation)
        if not valid:
            self.lbl_status.configure(text=err, text_color=DANGER_RED)
            return
            
        self.lbl_status.configure(text="")
        self.results_container.grid_remove()
        self.loading_card.grid()
        self.btn_submit.configure(state="disabled", text="Synthesizing Guidance...")
        
        status = self.cbo_status.get()
        freq = self.cbo_freq.get()
        goal = self.cbo_goal.get()
        interests = self.tags.get_selected()
        
        threading.Thread(
            target=self._run_advisor_thread,
            args=(status, freq, interests, goal, clean_situation),
            daemon=True
        ).start()

    def _run_advisor_thread(self, status, freq, interests, goal, situation):
        success, msg, result = AIAdvisorService.generate_roadmap(
            relationship_status=status,
            communication_freq=freq,
            interests=interests,
            goal=goal,
            situation=situation
        )
        self.after(0, lambda: self._handle_result(success, msg, result))

    def _handle_result(self, success, msg, result):
        self.btn_submit.configure(state="normal", text="Generate Personalized Roadmap 🤖")
        self.loading_card.grid_remove()
        
        if not success:
            self.lbl_status.configure(text=msg, text_color=DANGER_RED)
            return
            
        self.last_result = result
        
        # Clear existing steps in container
        for widget in self.results_container.winfo_children():
            widget.destroy()
            
        # Top Header Bar with Copy button
        top_bar = ctk.CTkFrame(self.results_container, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(16, 8))
        
        source_label = "Live LLM Engine" if result.get("source") == "live_llm" else "Offline Intelligence"
        ctk.CTkLabel(
            top_bar,
            text=f"🤖 YOUR PERSONALIZED ROADMAP ({source_label})",
            font=FONT_SUBTITLE,
            text_color=ACCENT_PURPLE
        ).pack(side="left")
        
        ctk.CTkButton(
            top_bar,
            text="📋 Copy Roadmap",
            width=120,
            height=30,
            font=FONT_SMALL,
            fg_color=BG_CARD_HOVER,
            hover_color="#2c2d40",
            border_width=1,
            border_color=BORDER_SUBTLE,
            command=self._copy_roadmap
        ).pack(side="right")
        
        # Render each roadmap step as a modern rounded card
        for step in result.get("steps", []):
            step_card = CardFrame(self.results_container, fg_color=BG_CARD)
            step_card.pack(fill="x", padx=20, pady=5)
            
            step_header = ctk.CTkFrame(step_card, fg_color="transparent")
            step_header.pack(fill="x", padx=14, pady=(10, 2))
            
            # Step badge
            badge = ctk.CTkLabel(
                step_header,
                text=step.get("step_num", "01"),
                font=FONT_SECTION,
                text_color=ACCENT_PINK,
                width=32
            )
            badge.pack(side="left", padx=(0, 8))
            
            # Step title
            title = ctk.CTkLabel(
                step_header,
                text=step.get("title", ""),
                font=FONT_BODY_BOLD,
                text_color=TEXT_PRIMARY,
                anchor="w"
            )
            title.pack(side="left", fill="x", expand=True)
            
            # Step description
            desc = ctk.CTkLabel(
                step_card,
                text=step.get("description", ""),
                font=FONT_BODY,
                text_color=TEXT_SECONDARY,
                wraplength=640,
                justify="left",
                anchor="w"
            )
            desc.pack(fill="x", padx=14, pady=(2, 12))
            
        # Mindset Reminder Banner
        reminder = result.get("reminder", "")
        if reminder:
            rem_card = CardFrame(self.results_container, fg_color="#1d1e2e", border_color="#45325c")
            rem_card.pack(fill="x", padx=20, pady=(8, 16))
            ctk.CTkLabel(
                rem_card, text="💡 Mindset Reminder:", font=FONT_BODY_BOLD, text_color=ACCENT_PINK
            ).pack(anchor="w", padx=14, pady=(10, 2))
            ctk.CTkLabel(
                rem_card, text=reminder, font=FONT_BODY, text_color=TEXT_MUTED, wraplength=640, justify="left"
            ).pack(anchor="w", padx=14, pady=(0, 10))
            
        self.results_container.grid()

    def _copy_roadmap(self):
        if self.last_result and self.last_result.get("raw_text"):
            self.clipboard_clear()
            self.clipboard_append(self.last_result["raw_text"])
            self.lbl_status.configure(text="✓ Roadmap copied to clipboard!", text_color=SUCCESS_GREEN)
