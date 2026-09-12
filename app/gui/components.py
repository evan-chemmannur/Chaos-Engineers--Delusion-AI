"""Reusable modern GUI components for LoveAI built with CustomTkinter."""

import customtkinter as ctk
from typing import List, Callable, Optional
from app.gui.theme import (
    BG_CARD, BG_CARD_HOVER, BG_INPUT, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, BORDER_SUBTLE, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_MUTED, TEXT_DIM, FONT_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_BODY_BOLD, FONT_SMALL, FONT_SCORE, SUCCESS_GREEN,
    WARNING_AMBER, DANGER_RED
)

class CardFrame(ctk.CTkFrame):
    """Modern rounded card container with subtle border."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=kwargs.pop("fg_color", BG_CARD),
            corner_radius=kwargs.pop("corner_radius", 14),
            border_width=kwargs.pop("border_width", 1),
            border_color=kwargs.pop("border_color", BORDER_SUBTLE),
            **kwargs
        )


class StatCard(CardFrame):
    """Card displaying a metric value with a title and description."""
    def __init__(self, master, title: str, value: str, subtext: str = "", accent_color: str = ACCENT_PINK, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.lbl_title = ctk.CTkLabel(
            self, text=title, font=FONT_SMALL, text_color=TEXT_MUTED, anchor="w"
        )
        self.lbl_title.grid(row=0, column=0, padx=16, pady=(14, 2), sticky="w")
        
        # Value
        self.lbl_val = ctk.CTkLabel(
            self, text=value, font=FONT_SCORE, text_color=accent_color, anchor="w"
        )
        self.lbl_val.grid(row=1, column=0, padx=16, pady=2, sticky="w")
        
        # Subtext
        if subtext:
            self.lbl_sub = ctk.CTkLabel(
                self, text=subtext, font=FONT_SMALL, text_color=TEXT_SECONDARY, anchor="w"
            )
            self.lbl_sub.grid(row=2, column=0, padx=16, pady=(2, 14), sticky="w")

    def update_value(self, new_val: str, new_subtext: Optional[str] = None):
        self.lbl_val.configure(text=new_val)
        if new_subtext is not None and hasattr(self, "lbl_sub"):
            self.lbl_sub.configure(text=new_subtext)


class DisclaimerBanner(CardFrame):
    """Notice banner for mandatory product disclaimers."""
    def __init__(self, master, text: str, **kwargs):
        super().__init__(
            master,
            fg_color="#181924",
            border_color="#3b2b3d",
            corner_radius=10,
            **kwargs
        )
        self.grid_columnconfigure(1, weight=1)
        
        icon = ctk.CTkLabel(self, text="ℹ️", font=("Segoe UI", 14))
        icon.grid(row=0, column=0, padx=(12, 6), pady=10, sticky="nw")
        
        msg = ctk.CTkLabel(
            self,
            text=text,
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            wraplength=600,
            justify="left",
            anchor="w"
        )
        msg.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="w")


class TagSelector(ctk.CTkFrame):
    """Pill-style selectable tags container."""
    def __init__(self, master, available_tags: List[str], on_change: Optional[Callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.available_tags = available_tags
        self.selected_tags = set()
        self.on_change = on_change
        self.buttons = {}
        
        self._build_ui()

    def _build_ui(self):
        row = 0
        col = 0
        max_cols = 5
        
        for tag in self.available_tags:
            btn = ctk.CTkButton(
                self,
                text=tag,
                width=80,
                height=28,
                corner_radius=14,
                font=FONT_SMALL,
                fg_color=BG_CARD,
                text_color=TEXT_SECONDARY,
                border_width=1,
                border_color=BORDER_SUBTLE,
                hover_color=BG_CARD_HOVER,
                command=lambda t=tag: self._toggle_tag(t)
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="w")
            self.buttons[tag] = btn
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _toggle_tag(self, tag: str):
        btn = self.buttons.get(tag)
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            if btn:
                btn.configure(
                    fg_color=BG_CARD,
                    text_color=TEXT_SECONDARY,
                    border_color=BORDER_SUBTLE
                )
        else:
            self.selected_tags.add(tag)
            if btn:
                btn.configure(
                    fg_color=ACCENT_PURPLE,
                    text_color=TEXT_PRIMARY,
                    border_color=ACCENT_PINK
                )
        if self.on_change:
            self.on_change(list(self.selected_tags))

    def get_selected(self) -> List[str]:
        return list(self.selected_tags)

    def select_tags(self, tags: List[str]):
        for t in tags:
            if t in self.buttons and t not in self.selected_tags:
                self._toggle_tag(t)
