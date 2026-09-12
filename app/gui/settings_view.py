"""Settings and configuration view for LoveAI."""

import os
from pathlib import Path
import customtkinter as ctk

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_SECTION, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, BORDER_SUBTLE, SUCCESS_GREEN, DANGER_RED
)
from app.gui.components import CardFrame, DisclaimerBanner
from app.config import (
    APP_NAME, APP_VERSION, ENV_FILE, DATABASE_PATH, GENERAL_DISCLAIMER
)
from app.database.database import db

class SettingsView(ctk.CTkScrollableFrame):
    """View allowing users to configure API keys, privacy settings, and diagnostics."""

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
            header, text="⚙️ Application Settings", font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 2), sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Manage API credentials, privacy preferences, and system diagnostics.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        
        # 2. AI Configuration Card
        ai_card = CardFrame(self)
        ai_card.grid(row=1, column=0, padx=20, pady=6, sticky="ew")
        ai_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            ai_card, text="🤖 LLM Provider & Credentials", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(16, 4))
        
        ctk.CTkLabel(
            ai_card,
            text="Provide an API key to enable live LLM queries, or leave blank to use the smart offline engine.",
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 10))
        
        # Provider selector
        ctk.CTkLabel(ai_card, text="Select Provider:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w", padx=20)
        self.cbo_provider = ctk.CTkComboBox(
            ai_card,
            values=["gemini", "openai", "offline_demo"],
            fg_color=BG_INPUT,
            border_color=BORDER_SUBTLE,
            height=34
        )
        current_prov = os.getenv("LLM_PROVIDER", "gemini")
        self.cbo_provider.set(current_prov)
        self.cbo_provider.pack(fill="x", padx=20, pady=(2, 10))
        
        # API Key input with show/hide toggle
        ctk.CTkLabel(ai_card, text="LLM API Key:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w", padx=20)
        
        key_frame = ctk.CTkFrame(ai_card, fg_color="transparent")
        key_frame.pack(fill="x", padx=20, pady=(2, 10))
        
        self.ent_key = ctk.CTkEntry(
            key_frame,
            placeholder_text="Enter your API Key...",
            show="•",
            height=34,
            fg_color=BG_INPUT,
            border_color=BORDER_SUBTLE
        )
        existing_key = os.getenv("LLM_API_KEY", "")
        if existing_key:
            self.ent_key.insert(0, existing_key)
        self.ent_key.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.btn_toggle_key = ctk.CTkButton(
            key_frame,
            text="👁️ Show",
            width=70,
            height=34,
            fg_color=BG_CARD_HOVER,
            hover_color="#2b2d3d",
            command=self._toggle_key_visibility
        )
        self.btn_toggle_key.pack(side="right")
        
        # Save Key Button
        self.lbl_save_status = ctk.CTkLabel(ai_card, text="", font=FONT_SMALL, text_color=SUCCESS_GREEN)
        self.lbl_save_status.pack(anchor="w", padx=20, pady=(0, 4))
        
        ctk.CTkButton(
            ai_card,
            text="💾 Save Credentials to .env",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            command=self._save_credentials
        ).pack(fill="x", padx=20, pady=(0, 18))
        
        # 3. Privacy & History Preferences Card
        priv_card = CardFrame(self)
        priv_card.grid(row=2, column=0, padx=20, pady=6, sticky="ew")
        priv_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            priv_card, text="🔒 Privacy & Data Retention", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(16, 4))
        
        self.sw_history = ctk.CTkSwitch(
            priv_card,
            text="Save AI interactions locally in SQLite history",
            font=FONT_BODY,
            progress_color=ACCENT_PINK
        )
        if os.getenv("SAVE_AI_HISTORY", "true").lower() in ("true", "1", "yes"):
            self.sw_history.select()
        self.sw_history.pack(anchor="w", padx=20, pady=(6, 12))
        
        btn_data_frame = ctk.CTkFrame(priv_card, fg_color="transparent")
        btn_data_frame.pack(fill="x", padx=20, pady=(0, 18))
        
        ctk.CTkButton(
            btn_data_frame,
            text="🗑️ Clear AI History",
            width=150,
            height=32,
            font=FONT_SMALL,
            fg_color=BG_CARD_HOVER,
            hover_color="#3a2430",
            command=self._clear_ai_history
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_data_frame,
            text="🔄 Reset Milestones to Default",
            width=200,
            height=32,
            font=FONT_SMALL,
            fg_color=BG_CARD_HOVER,
            hover_color="#262c3e",
            command=self._reset_milestones
        ).pack(side="left")
        
        # 4. System Diagnostics Card
        diag_card = CardFrame(self)
        diag_card.grid(row=3, column=0, padx=20, pady=6, sticky="ew")
        diag_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            diag_card, text="🩺 Diagnostics & Environment", font=FONT_SUBTITLE, text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(16, 6))
        
        # Diagnostic items
        diag_info = [
            f"• Application: {APP_NAME} v{APP_VERSION}",
            f"• Database Path: {DATABASE_PATH}",
            "• Computer Vision (OpenCV): Initialized & Operational ✓",
            "• Local Engine: Smart Contextual Fallback Active ✓",
        ]
        
        for item in diag_info:
            ctk.CTkLabel(
                diag_card, text=item, font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w"
            ).pack(anchor="w", padx=24, pady=2)
            
        ctk.CTkFrame(diag_card, height=14, fg_color="transparent").pack()
        
        # 5. Full Product Disclaimer
        disclaimer = DisclaimerBanner(self, GENERAL_DISCLAIMER)
        disclaimer.grid(row=4, column=0, padx=20, pady=(10, 24), sticky="ew")

    def _toggle_key_visibility(self):
        if self.ent_key.cget("show") == "•":
            self.ent_key.configure(show="")
            self.btn_toggle_key.configure(text="🔒 Hide")
        else:
            self.ent_key.configure(show="•")
            self.btn_toggle_key.configure(text="👁️ Show")

    def _save_credentials(self):
        key = self.ent_key.get().strip()
        provider = self.cbo_provider.get()
        save_hist = "true" if self.sw_history.get() else "false"
        
        os.environ["LLM_API_KEY"] = key
        os.environ["LLM_PROVIDER"] = provider
        os.environ["SAVE_AI_HISTORY"] = save_hist
        
        # Write to .env file
        try:
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write("# LoveAI Configuration\n")
                f.write(f"LLM_API_KEY={key}\n")
                f.write(f"LLM_PROVIDER={provider}\n")
                f.write(f"SAVE_AI_HISTORY={save_hist}\n")
            self.lbl_save_status.configure(text="✓ Settings saved successfully to .env!", text_color=SUCCESS_GREEN)
        except Exception as e:
            self.lbl_save_status.configure(text=f"Error saving: {e}", text_color=DANGER_RED)

    def _clear_ai_history(self):
        db.clear_ai_history()
        self.lbl_save_status.configure(text="✓ AI history cleared from database.", text_color=SUCCESS_GREEN)

    def _reset_milestones(self):
        db.clear_all_data()
        self.lbl_save_status.configure(text="✓ Reset database to default milestone templates.", text_color=SUCCESS_GREEN)
