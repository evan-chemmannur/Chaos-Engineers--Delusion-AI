"""Relationship Journey Tracker view for LoveAI."""

from datetime import datetime
import customtkinter as ctk
from typing import Optional, Dict, Any

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_SECTION, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, BORDER_SUBTLE, SUCCESS_GREEN, DANGER_RED
)
from app.gui.components import CardFrame, DisclaimerBanner
from app.database.database import db

class MilestoneDialog(ctk.CTkToplevel):
    """Modal dialog to add or edit a relationship milestone."""

    def __init__(self, parent, milestone: Optional[Dict[str, Any]] = None, on_save = None):
        super().__init__(parent)
        self.milestone = milestone
        self.on_save = on_save
        self.title("Edit Milestone" if milestone else "Add Milestone")
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.configure(fg_color=BG_MAIN)
        self._build_ui()

    def _build_ui(self):
        container = CardFrame(self, fg_color=BG_CARD)
        container.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Title
        title_text = "Edit Milestone" if self.milestone else "Add New Milestone"
        ctk.CTkLabel(container, text=title_text, font=FONT_SUBTITLE, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=16, pady=(14, 10)
        )
        
        # Field: Title
        ctk.CTkLabel(container, text="Milestone Title:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w", padx=16)
        self.ent_title = ctk.CTkEntry(container, height=34, fg_color=BG_INPUT, border_color=BORDER_SUBTLE)
        self.ent_title.pack(fill="x", padx=16, pady=(2, 8))
        if self.milestone:
            self.ent_title.insert(0, self.milestone.get("title", ""))
            
        # Field: Date
        ctk.CTkLabel(container, text="Date (YYYY-MM-DD):", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w", padx=16)
        self.ent_date = ctk.CTkEntry(container, height=34, fg_color=BG_INPUT, border_color=BORDER_SUBTLE)
        self.ent_date.pack(fill="x", padx=16, pady=(2, 8))
        today = datetime.now().strftime("%Y-%m-%d")
        self.ent_date.insert(0, self.milestone.get("event_date", today) if self.milestone else today)
        
        # Field: Description
        ctk.CTkLabel(container, text="Description:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w", padx=16)
        self.ent_desc = ctk.CTkEntry(container, height=34, fg_color=BG_INPUT, border_color=BORDER_SUBTLE)
        self.ent_desc.pack(fill="x", padx=16, pady=(2, 8))
        if self.milestone:
            self.ent_desc.insert(0, self.milestone.get("description", ""))
            
        # Field: Notes
        ctk.CTkLabel(container, text="Personal Notes / Memories:", font=FONT_SMALL, text_color=TEXT_SECONDARY).pack(anchor="w", padx=16)
        self.ent_notes = ctk.CTkEntry(container, height=34, fg_color=BG_INPUT, border_color=BORDER_SUBTLE)
        self.ent_notes.pack(fill="x", padx=16, pady=(2, 12))
        if self.milestone:
            self.ent_notes.insert(0, self.milestone.get("notes", ""))
            
        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(10, 14))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            fg_color=BG_CARD_HOVER,
            hover_color="#2c2e40",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="Save Milestone",
            width=140,
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            command=self._save
        ).pack(side="right")

    def _save(self):
        title = self.ent_title.get().strip()
        if not title:
            return
            
        date = self.ent_date.get().strip()
        desc = self.ent_desc.get().strip()
        notes = self.ent_notes.get().strip()
        
        if self.milestone:
            db.update_milestone(
                milestone_id=self.milestone["id"],
                title=title,
                description=desc,
                event_date=date,
                notes=notes,
                completed=self.milestone.get("completed", 0)
            )
        else:
            db.add_milestone(
                title=title,
                description=desc,
                event_date=date,
                notes=notes,
                completed=0
            )
            
        if self.on_save:
            self.on_save()
        self.destroy()


class JourneyView(ctk.CTkScrollableFrame):
    """Timeline view tracking relationship milestones."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self):
        # 1. Header Card
        header = CardFrame(self)
        header.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        top_bar = ctk.CTkFrame(header, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(16, 4))
        
        ctk.CTkLabel(
            top_bar, text="❤️ Relationship Journey", font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).pack(side="left")
        
        ctk.CTkButton(
            top_bar,
            text="+ Add Milestone",
            width=130,
            height=32,
            font=FONT_BODY_BOLD,
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            command=self._open_add_dialog
        ).pack(side="right")
        
        ctk.CTkLabel(
            header,
            text="Chronicle your shared memories and celebrate steps along the path of connection.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 12))
        
        # 2. Progress Tracker Card
        self.progress_card = CardFrame(self, fg_color="#181926")
        self.progress_card.grid(row=1, column=0, padx=20, pady=4, sticky="ew")
        self.progress_card.grid_columnconfigure(0, weight=1)
        
        self.lbl_progress = ctk.CTkLabel(
            self.progress_card, text="Journey Progress: 0 / 0", font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY
        )
        self.lbl_progress.pack(anchor="w", padx=20, pady=(14, 4))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_card,
            progress_color=ACCENT_PINK,
            fg_color=BG_INPUT,
            height=12,
            corner_radius=6
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 14))
        
        # 3. Timeline Items Container
        self.timeline_container = ctk.CTkFrame(self, fg_color="transparent")
        self.timeline_container.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        self.timeline_container.grid_columnconfigure(0, weight=1)
        
        # Initial render
        self.refresh_milestones()

    def refresh_milestones(self):
        """Reloads all milestones from SQLite and updates progress."""
        for w in self.timeline_container.winfo_children():
            w.destroy()
            
        milestones = db.get_all_milestones()
        completed_cnt, total_cnt = db.get_journey_progress()
        
        pct = (completed_cnt / total_cnt) if total_cnt > 0 else 0
        self.progress_bar.set(pct)
        self.lbl_progress.configure(
            text=f"Journey Progress: {completed_cnt} / {total_cnt} milestones completed ({int(pct*100)}%)"
        )
        
        for idx, m in enumerate(milestones):
            is_done = bool(m["completed"])
            
            card = CardFrame(self.timeline_container, fg_color=BG_CARD)
            card.pack(fill="x", pady=6)
            
            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=14, pady=10)
            
            # Checkbox
            cb = ctk.CTkCheckBox(
                row_frame,
                text="",
                width=24,
                checkbox_width=22,
                checkbox_height=22,
                checkmark_color=TEXT_PRIMARY,
                fg_color=ACCENT_PINK,
                hover_color=ACCENT_PINK_HOVER,
                command=lambda mid=m["id"]: self._toggle_milestone(mid)
            )
            if is_done:
                cb.select()
            else:
                cb.deselect()
            cb.pack(side="left", padx=(0, 10))
            
            # Title & details
            details_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="x", expand=True)
            
            title_text = m["title"]
            title_color = TEXT_PRIMARY if is_done else TEXT_SECONDARY
            lbl_title = ctk.CTkLabel(
                details_frame,
                text=f"{'✓ ' if is_done else '○ '}{title_text}",
                font=FONT_BODY_BOLD,
                text_color=title_color,
                anchor="w"
            )
            lbl_title.pack(anchor="w")
            
            sub_parts = []
            if m.get("event_date"):
                sub_parts.append(m["event_date"])
            if m.get("description"):
                sub_parts.append(m["description"])
            if sub_parts:
                ctk.CTkLabel(
                    details_frame,
                    text=" — ".join(sub_parts),
                    font=FONT_SMALL,
                    text_color=TEXT_MUTED,
                    anchor="w"
                ).pack(anchor="w")
                
            if m.get("notes"):
                ctk.CTkLabel(
                    details_frame,
                    text=f"Note: {m['notes']}",
                    font=FONT_SMALL,
                    text_color=ACCENT_PURPLE,
                    anchor="w"
                ).pack(anchor="w", pady=(2, 0))
                
            # Edit & Delete Buttons
            ctk.CTkButton(
                row_frame,
                text="✏️",
                width=32,
                height=28,
                fg_color=BG_CARD_HOVER,
                hover_color="#2c2e40",
                command=lambda item=m: self._open_edit_dialog(item)
            ).pack(side="right", padx=(4, 0))
            
            ctk.CTkButton(
                row_frame,
                text="🗑️",
                width=32,
                height=28,
                fg_color=BG_CARD_HOVER,
                hover_color="#3d2026",
                text_color=DANGER_RED,
                command=lambda mid=m["id"]: self._delete_milestone(mid)
            ).pack(side="right")

    def _toggle_milestone(self, milestone_id: int):
        db.toggle_milestone(milestone_id)
        self.refresh_milestones()

    def _delete_milestone(self, milestone_id: int):
        db.delete_milestone(milestone_id)
        self.refresh_milestones()

    def _open_add_dialog(self):
        MilestoneDialog(self, milestone=None, on_save=self.refresh_milestones)

    def _open_edit_dialog(self, item: Dict[str, Any]):
        MilestoneDialog(self, milestone=item, on_save=self.refresh_milestones)
