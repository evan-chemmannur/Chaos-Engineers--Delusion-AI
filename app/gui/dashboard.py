"""Dashboard view for LoveAI providing a high-level overview of all features."""

import customtkinter as ctk
from typing import Callable

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_SCORE, BORDER_SUBTLE, SUCCESS_GREEN
)
from app.gui.components import CardFrame, DisclaimerBanner
from app.config import APP_NAME, APP_TAGLINE, GENERAL_DISCLAIMER
from app.database.database import db

class DashboardView(ctk.CTkScrollableFrame):
    """Main dashboard displaying quick stats and shortcuts to core features."""

    def __init__(self, master, navigate_fn: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.navigate_fn = navigate_fn
        
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self):
        # 1. Hero Header Banner
        hero_card = CardFrame(self, fg_color="#181826", border_color="#332845")
        hero_card.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        hero_card.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(
            hero_card,
            text=f"💕 {APP_NAME}",
            font=("Segoe UI", 26, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        title_lbl.grid(row=0, column=0, padx=24, pady=(20, 2), sticky="w")
        
        tagline_lbl = ctk.CTkLabel(
            hero_card,
            text=APP_TAGLINE,
            font=FONT_SUBTITLE,
            text_color=ACCENT_PINK,
            anchor="w"
        )
        tagline_lbl.grid(row=1, column=0, padx=24, pady=(0, 6), sticky="w")
        
        sub_lbl = ctk.CTkLabel(
            hero_card,
            text="Your modern relationship companion for thoughtful communication and fun compatibility analysis.",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            anchor="w"
        )
        sub_lbl.grid(row=2, column=0, padx=24, pady=(0, 20), sticky="w")
        
        # 2. Grid of Feature Cards (2 columns)
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.grid(row=1, column=0, padx=20, pady=6, sticky="ew")
        grid_frame.grid_columnconfigure((0, 1), weight=1)
        
        # --- Card 1: 💘 Compatibility ---
        self.comp_card = CardFrame(grid_frame)
        self.comp_card.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        self.comp_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.comp_card, text="💘 Compatibility Analyzer", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        
        self.lbl_comp_summary = ctk.CTkLabel(
            self.comp_card,
            text="Deterministic name & shared interest synergy.",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.lbl_comp_summary.grid(row=1, column=0, padx=18, pady=(0, 10), sticky="w")
        
        self.lbl_comp_score = ctk.CTkLabel(
            self.comp_card, text="--%", font=FONT_SCORE, text_color=ACCENT_PINK
        )
        self.lbl_comp_score.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="w")
        
        ctk.CTkButton(
            self.comp_card,
            text="View Analysis →",
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            corner_radius=8,
            font=FONT_BODY_BOLD,
            command=lambda: self.navigate_fn("compatibility")
        ).grid(row=3, column=0, padx=18, pady=(0, 18), sticky="w")
        
        # --- Card 2: 📸 Image Similarity ---
        img_card = CardFrame(grid_frame)
        img_card.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        img_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            img_card, text="📸 Image Similarity", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        
        ctk.CTkLabel(
            img_card,
            text="Local OpenCV computer vision comparison using histograms, pixel metrics & ORB features.",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            wraplength=320,
            justify="left"
        ).grid(row=1, column=0, padx=18, pady=(0, 20), sticky="w")
        
        ctk.CTkButton(
            img_card,
            text="Compare Images →",
            fg_color=BG_CARD_HOVER,
            hover_color="#313348",
            corner_radius=8,
            border_width=1,
            border_color=BORDER_SUBTLE,
            font=FONT_BODY_BOLD,
            command=lambda: self.navigate_fn("image")
        ).grid(row=3, column=0, padx=18, pady=(0, 18), sticky="w")
        
        # --- Card 3: 🤖 AI Relationship Advisor ---
        adv_card = CardFrame(grid_frame)
        adv_card.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="nsew")
        adv_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            adv_card, text="🤖 AI Relationship Advisor", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        
        ctk.CTkLabel(
            adv_card,
            text="Personalized roadmaps for your specific relationship stage, respecting consent and personal boundaries.",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            wraplength=320,
            justify="left"
        ).grid(row=1, column=0, padx=18, pady=(0, 20), sticky="w")
        
        ctk.CTkButton(
            adv_card,
            text="Ask AI Advisor →",
            fg_color=ACCENT_PURPLE,
            hover_color=ACCENT_PURPLE_HOVER,
            corner_radius=8,
            font=FONT_BODY_BOLD,
            command=lambda: self.navigate_fn("advisor")
        ).grid(row=3, column=0, padx=18, pady=(0, 18), sticky="w")
        
        # --- Card 4: 💬 AI Message Assistant ---
        msg_card = CardFrame(grid_frame)
        msg_card.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="nsew")
        msg_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            msg_card, text="💬 AI Message Assistant", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        
        ctk.CTkLabel(
            msg_card,
            text="Analyze tone, clarity, and pressure of your messages, or generate rewrites in 7 customizable styles.",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            wraplength=320,
            justify="left"
        ).grid(row=1, column=0, padx=18, pady=(0, 20), sticky="w")
        
        ctk.CTkButton(
            msg_card,
            text="Open Assistant →",
            fg_color=BG_CARD_HOVER,
            hover_color="#313348",
            corner_radius=8,
            border_width=1,
            border_color=BORDER_SUBTLE,
            font=FONT_BODY_BOLD,
            command=lambda: self.navigate_fn("message")
        ).grid(row=3, column=0, padx=18, pady=(0, 18), sticky="w")
        
        # --- Card 5: ❤️ Relationship Journey Progress ---
        self.journey_card = CardFrame(self)
        self.journey_card.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.journey_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.journey_card, text="❤️ Relationship Journey Tracker", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        
        self.lbl_journey_status = ctk.CTkLabel(
            self.journey_card, text="Milestones completed: ...", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY
        )
        self.lbl_journey_status.grid(row=1, column=0, padx=18, pady=2, sticky="w")
        
        self.journey_prog = ctk.CTkProgressBar(
            self.journey_card,
            progress_color=ACCENT_PINK,
            fg_color=BG_INPUT,
            height=12,
            corner_radius=6
        )
        self.journey_prog.grid(row=2, column=0, padx=18, pady=8, sticky="ew")
        
        ctk.CTkButton(
            self.journey_card,
            text="View Timeline →",
            width=140,
            fg_color=BG_CARD_HOVER,
            hover_color="#313348",
            corner_radius=8,
            border_width=1,
            border_color=BORDER_SUBTLE,
            font=FONT_BODY_BOLD,
            command=lambda: self.navigate_fn("journey")
        ).grid(row=3, column=0, padx=18, pady=(4, 16), sticky="w")
        
        # 3. Product Disclaimer
        banner = DisclaimerBanner(self, GENERAL_DISCLAIMER)
        banner.grid(row=3, column=0, padx=20, pady=(8, 24), sticky="ew")

    def refresh_stats(self):
        """Updates dashboard with latest database figures."""
        # Update latest compatibility
        latest = db.get_latest_compatibility()
        if latest:
            score = latest["combined_score"]
            names = f"{latest['name1']} & {latest['name2']}"
            self.lbl_comp_score.configure(text=f"{score}%")
            self.lbl_comp_summary.configure(text=f"Latest: {names}")
        else:
            self.lbl_comp_score.configure(text="--%")
            self.lbl_comp_summary.configure(text="No compatibility calculations yet.")
            
        # Update journey milestones
        completed, total = db.get_journey_progress()
        pct = (completed / total) if total > 0 else 0
        self.journey_prog.set(pct)
        self.lbl_journey_status.configure(text=f"{completed} / {total} milestones completed ({int(pct*100)}%)")
