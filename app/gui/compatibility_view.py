"""Compatibility Analyzer view for LoveAI."""

import customtkinter as ctk
from typing import List

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_SCORE, FONT_SCORE_MEDIUM, BORDER_SUBTLE, DANGER_RED
)
from app.gui.components import CardFrame, DisclaimerBanner, TagSelector
from app.config import DEFAULT_INTERESTS, COMPATIBILITY_DISCLAIMER
from app.core.compatibility import CompatibilityAnalyzer
from app.database.database import db

class CompatibilityView(ctk.CTkScrollableFrame):
    """View allowing users to calculate deterministic compatibility scores."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self):
        # 1. Header Card
        header = CardFrame(self)
        header.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, text="💘 Compatibility Analyzer", font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 2), sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Discover your entertainment synergy through name harmonics and shared passions.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        
        # 2. Input Card
        input_card = CardFrame(self)
        input_card.grid(row=1, column=0, padx=20, pady=6, sticky="ew")
        input_card.grid_columnconfigure((0, 1), weight=1)
        
        # Name 1
        ctk.CTkLabel(
            input_card, text="Your Name:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY
        ).grid(row=0, column=0, padx=20, pady=(16, 4), sticky="w")
        
        self.ent_name1 = ctk.CTkEntry(
            input_card,
            placeholder_text="e.g. Alex",
            font=FONT_BODY,
            height=38,
            fg_color=BG_INPUT,
            border_color=BORDER_SUBTLE
        )
        self.ent_name1.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="ew")
        
        # Name 2
        ctk.CTkLabel(
            input_card, text="Other Person's Name:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY
        ).grid(row=0, column=1, padx=20, pady=(16, 4), sticky="w")
        
        self.ent_name2 = ctk.CTkEntry(
            input_card,
            placeholder_text="e.g. Sam",
            font=FONT_BODY,
            height=38,
            fg_color=BG_INPUT,
            border_color=BORDER_SUBTLE
        )
        self.ent_name2.grid(row=1, column=1, padx=20, pady=(0, 12), sticky="ew")
        
        # Interests section
        ctk.CTkLabel(
            input_card, text="Shared Interests (Select all that apply):", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY
        ).grid(row=2, column=0, columnspan=2, padx=20, pady=(8, 4), sticky="w")
        
        self.tag_selector = TagSelector(input_card, available_tags=DEFAULT_INTERESTS)
        self.tag_selector.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 8), sticky="ew")
        
        # Custom interest addition
        custom_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        custom_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 14), sticky="w")
        
        self.ent_custom_interest = ctk.CTkEntry(
            custom_frame,
            placeholder_text="Add custom interest...",
            width=220,
            height=32,
            fg_color=BG_INPUT,
            border_color=BORDER_SUBTLE,
            font=FONT_SMALL
        )
        self.ent_custom_interest.pack(side="left", padx=(0, 8))
        
        ctk.CTkButton(
            custom_frame,
            text="+ Add Tag",
            width=90,
            height=32,
            font=FONT_SMALL,
            fg_color=BG_CARD,
            hover_color="#262837",
            border_width=1,
            border_color=BORDER_SUBTLE,
            command=self._add_custom_tag
        ).pack(side="left")
        
        # Error Label
        self.lbl_error = ctk.CTkLabel(
            input_card, text="", font=FONT_SMALL, text_color=DANGER_RED
        )
        self.lbl_error.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 4), sticky="w")
        
        # Calculate Button
        self.btn_calculate = ctk.CTkButton(
            input_card,
            text="Calculate Compatibility 💕",
            font=FONT_BODY_BOLD,
            height=40,
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            corner_radius=8,
            command=self._on_calculate
        )
        self.btn_calculate.grid(row=6, column=0, columnspan=2, padx=20, pady=(4, 18), sticky="ew")
        
        # 3. Results Container (Initially hidden until calculated)
        self.results_card = CardFrame(self, fg_color="#181826", border_color="#36284a")
        self.results_card.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.results_card.grid_columnconfigure((0, 1, 2), weight=1)
        self.results_card.grid_remove() # Hide initially
        
        # Verdict Banner
        self.lbl_verdict_title = ctk.CTkLabel(
            self.results_card, text="", font=FONT_SUBTITLE, text_color=ACCENT_PINK
        )
        self.lbl_verdict_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(16, 2), sticky="w")
        
        self.lbl_verdict_desc = ctk.CTkLabel(
            self.results_card, text="", font=FONT_BODY, text_color=TEXT_SECONDARY, wraplength=620, justify="left"
        )
        self.lbl_verdict_desc.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 14), sticky="w")
        
        # 3 Metric boxes
        # Box 1: Combined
        box_main = CardFrame(self.results_card, fg_color=BG_CARD)
        box_main.grid(row=2, column=0, padx=(16, 6), pady=(0, 16), sticky="nsew")
        ctk.CTkLabel(box_main, text="Overall Synergy", font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(12, 0))
        self.val_combined = ctk.CTkLabel(box_main, text="--%", font=FONT_SCORE, text_color=ACCENT_PINK)
        self.val_combined.pack(pady=(0, 12))
        
        # Box 2: Name
        box_name = CardFrame(self.results_card, fg_color=BG_CARD)
        box_name.grid(row=2, column=1, padx=6, pady=(0, 16), sticky="nsew")
        ctk.CTkLabel(box_name, text="Name Compatibility", font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(12, 0))
        self.val_name = ctk.CTkLabel(box_name, text="--%", font=FONT_SCORE_MEDIUM, text_color=TEXT_PRIMARY)
        self.val_name.pack(pady=(4, 12))
        
        # Box 3: Interests
        box_interests = CardFrame(self.results_card, fg_color=BG_CARD)
        box_interests.grid(row=2, column=2, padx=(6, 16), pady=(0, 16), sticky="nsew")
        ctk.CTkLabel(box_interests, text="Shared Interests", font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(12, 0))
        self.val_interests = ctk.CTkLabel(box_interests, text="--%", font=FONT_SCORE_MEDIUM, text_color=ACCENT_PURPLE)
        self.val_interests.pack(pady=(4, 12))
        
        # 4. Mandatory Disclaimer Banner
        disclaimer = DisclaimerBanner(self, COMPATIBILITY_DISCLAIMER)
        disclaimer.grid(row=3, column=0, padx=20, pady=(10, 24), sticky="ew")

    def _add_custom_tag(self):
        text = self.ent_custom_interest.get().strip()
        if text:
            clean = text.capitalize()
            if clean not in self.tag_selector.available_tags:
                self.tag_selector.available_tags.append(clean)
                self.tag_selector.selected_tags.add(clean)
                # Rebuild tags
                for child in self.tag_selector.winfo_children():
                    child.destroy()
                self.tag_selector._build_ui()
                self.tag_selector.select_tags(list(self.tag_selector.selected_tags))
            self.ent_custom_interest.delete(0, "end")

    def _on_calculate(self):
        name1 = self.ent_name1.get()
        name2 = self.ent_name2.get()
        interests = self.tag_selector.get_selected()
        
        success, err, result = CompatibilityAnalyzer.analyze(name1, name2, interests)
        if not success:
            self.lbl_error.configure(text=err)
            return
            
        self.lbl_error.configure(text="")
        
        # Display results
        self.val_combined.configure(text=f"{result['combined_score']}%")
        self.val_name.configure(text=f"{result['name_score']}%")
        self.val_interests.configure(text=f"{result['interest_score']}%")
        self.lbl_verdict_title.configure(text=result["verdict_title"])
        self.lbl_verdict_desc.configure(text=result["verdict_description"])
        
        # Save to database
        db.save_compatibility_result(
            name1=result["name1"],
            name2=result["name2"],
            name_score=result["name_score"],
            interest_score=result["interest_score"],
            combined_score=result["combined_score"]
        )
        
        # Show results
        self.results_card.grid()
