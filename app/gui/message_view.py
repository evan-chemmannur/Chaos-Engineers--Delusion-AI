"""AI Message Assistant view for LoveAI."""

import threading
import customtkinter as ctk
from typing import List

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_SECTION, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, FONT_SCORE_MEDIUM, BORDER_SUBTLE,
    DANGER_RED, SUCCESS_GREEN
)
from app.gui.components import CardFrame, DisclaimerBanner
from app.config import MESSAGE_TONES, GENERAL_DISCLAIMER
from app.ai.message_assistant import MessageAssistantService
from app.core.validation import validate_message_text

class MessageView(ctk.CTkScrollableFrame):
    """View providing message analysis and tone-based message improvement."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.active_mode = "analyze" # 'analyze' or 'improve'
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self):
        # 1. Header Card
        header = CardFrame(self)
        header.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, text="💬 AI Message Assistant", font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 2), sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Craft smooth, authentic, and pressure-free messages tailored to your communication style.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        
        # 2. Segmented Mode Switcher (Analyze vs Improve)
        self.mode_switcher = ctk.CTkSegmentedButton(
            self,
            values=["🔍 Analyze Message", "✨ Improve Message"],
            command=self._on_mode_change,
            font=FONT_BODY_BOLD,
            selected_color=ACCENT_PINK,
            selected_hover_color=ACCENT_PINK_HOVER,
            unselected_color=BG_CARD,
            height=36
        )
        self.mode_switcher.set("🔍 Analyze Message")
        self.mode_switcher.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")
        
        # 3. Input Card
        self.input_card = CardFrame(self)
        self.input_card.grid(row=2, column=0, padx=20, pady=6, sticky="ew")
        self.input_card.grid_columnconfigure(0, weight=1)
        
        self.lbl_input_prompt = ctk.CTkLabel(
            self.input_card, text="Paste your draft message to analyze:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY
        )
        self.lbl_input_prompt.pack(anchor="w", padx=20, pady=(16, 6))
        
        self.txt_message = ctk.CTkTextbox(
            self.input_card,
            height=100,
            fg_color=BG_INPUT,
            border_width=1,
            border_color=BORDER_SUBTLE,
            font=FONT_BODY
        )
        self.txt_message.insert("1.0", "Hey! Are you free to grab coffee or study together this Thursday?")
        self.txt_message.pack(fill="x", padx=20, pady=(0, 10))
        
        # Tone Selector Frame (Visible only in Improve Mode)
        self.tone_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        ctk.CTkLabel(
            self.tone_frame, text="Select Desired Tone:", font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 4))
        
        self.tone_seg = ctk.CTkSegmentedButton(
            self.tone_frame,
            values=MESSAGE_TONES,
            selected_color=ACCENT_PURPLE,
            selected_hover_color=ACCENT_PURPLE_HOVER,
            unselected_color=BG_INPUT,
            font=FONT_SMALL
        )
        self.tone_seg.set("Casual")
        self.tone_seg.pack(fill="x", pady=(0, 8))
        # Initially not packed because default is analyze mode
        
        # Error / Status
        self.lbl_status = ctk.CTkLabel(self.input_card, text="", font=FONT_SMALL, text_color=DANGER_RED)
        self.lbl_status.pack(anchor="w", padx=20, pady=(0, 4))
        
        # Action Button
        self.btn_action = ctk.CTkButton(
            self.input_card,
            text="Analyze Message 🔍",
            font=FONT_BODY_BOLD,
            height=40,
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            corner_radius=8,
            command=self._on_action
        )
        self.btn_action.pack(fill="x", padx=20, pady=(4, 18))
        
        # 4. Results Card (Hidden initially)
        self.results_card = CardFrame(self, fg_color="#181826", border_color="#36284a")
        self.results_card.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.results_card.grid_columnconfigure(0, weight=1)
        self.results_card.grid_remove()
        
        # 5. Mandatory Disclaimer
        disclaimer = DisclaimerBanner(self, GENERAL_DISCLAIMER)
        disclaimer.grid(row=4, column=0, padx=20, pady=(10, 24), sticky="ew")

    def _on_mode_change(self, mode_val: str):
        self.results_card.grid_remove()
        self.lbl_status.configure(text="")
        
        if "Analyze" in mode_val:
            self.active_mode = "analyze"
            self.lbl_input_prompt.configure(text="Paste your draft message to analyze:")
            self.btn_action.configure(
                text="Analyze Message 🔍",
                fg_color=ACCENT_PINK,
                hover_color=ACCENT_PINK_HOVER
            )
            self.tone_frame.pack_forget()
        else:
            self.active_mode = "improve"
            self.lbl_input_prompt.configure(text="Enter your base message to rewrite:")
            self.btn_action.configure(
                text="Generate Tone Variations ✨",
                fg_color=ACCENT_PURPLE,
                hover_color=ACCENT_PURPLE_HOVER
            )
            self.tone_frame.pack(fill="x", padx=20, pady=(0, 10), before=self.lbl_status)

    def _on_action(self):
        msg = self.txt_message.get("1.0", "end").strip()
        valid, err, clean_msg = validate_message_text(msg)
        if not valid:
            self.lbl_status.configure(text=err, text_color=DANGER_RED)
            return
            
        self.lbl_status.configure(text="")
        self.results_card.grid_remove()
        self.btn_action.configure(state="disabled", text="Processing...")
        
        if self.active_mode == "analyze":
            threading.Thread(target=self._run_analyze_thread, args=(clean_msg,), daemon=True).start()
        else:
            tone = self.tone_seg.get()
            threading.Thread(target=self._run_improve_thread, args=(clean_msg, tone), daemon=True).start()

    def _run_analyze_thread(self, msg: str):
        success, res_msg, data = MessageAssistantService.analyze_message(msg)
        self.after(0, lambda: self._handle_analyze_result(success, res_msg, data))

    def _run_improve_thread(self, msg: str, tone: str):
        success, res_msg, data = MessageAssistantService.improve_message(msg, tone)
        self.after(0, lambda: self._handle_improve_result(success, res_msg, data))

    def _handle_analyze_result(self, success, msg, data):
        self.btn_action.configure(state="normal", text="Analyze Message 🔍")
        if not success:
            self.lbl_status.configure(text=msg, text_color=DANGER_RED)
            return
            
        for w in self.results_card.winfo_children():
            w.destroy()
            
        # Top title
        ctk.CTkLabel(
            self.results_card, text="📊 MESSAGE ANALYSIS", font=FONT_SUBTITLE, text_color=ACCENT_PINK
        ).pack(anchor="w", padx=20, pady=(16, 12))
        
        # 4 Metric Cards Grid
        grid = ctk.CTkFrame(self.results_card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 12))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        metrics = [
            ("Tone", data.get("tone", "Friendly")),
            ("Clarity", data.get("clarity", "High")),
            ("Pressure", data.get("pressure", "Low")),
            ("Naturalness", data.get("naturalness", "Natural"))
        ]
        
        for idx, (label, val) in enumerate(metrics):
            card = CardFrame(grid, fg_color=BG_CARD)
            card.grid(row=0, column=idx, padx=4, pady=4, sticky="nsew")
            ctk.CTkLabel(card, text=label, font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(10, 2))
            ctk.CTkLabel(card, text=val, font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY).pack(pady=(0, 10))
            
        # AI Feedback
        fb_box = CardFrame(self.results_card, fg_color=BG_CARD)
        fb_box.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(
            fb_box, text="💡 AI Feedback & Nuance:", font=FONT_BODY_BOLD, text_color=ACCENT_PURPLE
        ).pack(anchor="w", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            fb_box,
            text=data.get("feedback", ""),
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=640,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 12))
        
        self.results_card.grid()

    def _handle_improve_result(self, success, msg, data):
        self.btn_action.configure(state="normal", text="Generate Tone Variations ✨")
        if not success:
            self.lbl_status.configure(text=msg, text_color=DANGER_RED)
            return
            
        for w in self.results_card.winfo_children():
            w.destroy()
            
        ctk.CTkLabel(
            self.results_card,
            text=f"✨ ALTERNATIVE VARIATIONS ({data.get('tone', 'Casual')})",
            font=FONT_SUBTITLE,
            text_color=ACCENT_PURPLE
        ).pack(anchor="w", padx=20, pady=(16, 10))
        
        for idx, opt in enumerate(data.get("options", []), 1):
            opt_card = CardFrame(self.results_card, fg_color=BG_CARD)
            opt_card.pack(fill="x", padx=20, pady=5)
            
            top_bar = ctk.CTkFrame(opt_card, fg_color="transparent")
            top_bar.pack(fill="x", padx=14, pady=(10, 4))
            
            ctk.CTkLabel(
                top_bar, text=f"Option {idx}", font=FONT_BODY_BOLD, text_color=ACCENT_PINK
            ).pack(side="left")
            
            ctk.CTkButton(
                top_bar,
                text="📋 Copy",
                width=80,
                height=26,
                font=FONT_SMALL,
                fg_color=BG_CARD_HOVER,
                hover_color="#2c2d40",
                border_width=1,
                border_color=BORDER_SUBTLE,
                command=lambda t=opt: self._copy_text(t)
            ).pack(side="right")
            
            ctk.CTkLabel(
                opt_card,
                text=opt,
                font=FONT_BODY,
                text_color=TEXT_PRIMARY,
                wraplength=620,
                justify="left"
            ).pack(anchor="w", padx=14, pady=(0, 12))
            
        self.results_card.grid()

    def _copy_text(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.lbl_status.configure(text="✓ Option copied to clipboard!", text_color=SUCCESS_GREEN)
