"""Main entry point for LoveAI desktop application."""

import os
import sys
from pathlib import Path
import customtkinter as ctk
from PIL import Image

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import (
    APP_NAME, APP_TAGLINE, WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    ASSETS_DIR
)
from app.gui.theme import (
    BG_MAIN, BG_SIDEBAR, BG_CARD, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER_SUBTLE,
    FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from app.gui.dashboard import DashboardView
from app.gui.compatibility_view import CompatibilityView
from app.gui.image_view import ImageView
from app.gui.advisor_view import AdvisorView
from app.gui.message_view import MessageView
from app.gui.journey_view import JourneyView
from app.gui.settings_view import SettingsView

class LoveAIApp(ctk.CTk):
    """Main LoveAI desktop window."""

    def __init__(self):
        super().__init__()
        
        # Configure global appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Window attributes
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_MIN_WIDTH + 60}x{WINDOW_MIN_HEIGHT + 40}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=BG_MAIN)
        
        # Set window icon if available
        ico_path = ASSETS_DIR / "icon.ico"
        if ico_path.exists():
            try:
                self.iconbitmap(str(ico_path))
            except Exception as e:
                print(f"Could not load window icon: {e}")
                
        # Main layout grid: 2 columns (Sidebar, Main Content)
        self.grid_columnconfigure(0, weight=0) # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1) # Content expands
        self.grid_rowconfigure(0, weight=1)
        
        self.nav_buttons = {}
        self.views = {}
        self.current_view_key = ""
        
        self._build_sidebar()
        self._build_content_area()
        self.navigate("dashboard")

    def _build_sidebar(self):
        """Constructs the navigation sidebar according to PRD Section 5."""
        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=BG_SIDEBAR,
            border_width=1,
            border_color=BORDER_SUBTLE
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(8, weight=1) # Spacer before Settings
        
        # Brand Header with Logo
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=16, pady=(20, 16), sticky="w")
        
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            try:
                pil_logo = Image.open(logo_path)
                pil_logo.thumbnail((36, 36))
                ctk_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=pil_logo.size)
                lbl_logo = ctk.CTkLabel(brand_frame, image=ctk_logo, text="")
                lbl_logo.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")
                
        lbl_brand = ctk.CTkLabel(
            brand_frame,
            text=APP_NAME,
            font=("Segoe UI", 18, "bold"),
            text_color=TEXT_PRIMARY
        )
        lbl_brand.pack(side="left")
        
        # Navigation Items
        nav_items = [
            ("dashboard", "🏠  Dashboard"),
            ("compatibility", "💘  Compatibility"),
            ("image", "📸  Image Similarity"),
            ("advisor", "🤖  AI Advisor"),
            ("message", "💬  Message Assistant"),
            ("journey", "❤️  Journey"),
        ]
        
        for idx, (key, label) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=40,
                corner_radius=8,
                font=FONT_BODY_BOLD,
                fg_color="transparent",
                text_color=TEXT_SECONDARY,
                hover_color=BG_CARD,
                command=lambda k=key: self.navigate(k)
            )
            btn.grid(row=idx, column=0, padx=12, pady=4, sticky="ew")
            self.nav_buttons[key] = btn
            
        # Divider Line
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER_SUBTLE)
        sep.grid(row=7, column=0, padx=16, pady=12, sticky="ew")
        
        # Settings Button at bottom
        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text="⚙️  Settings",
            anchor="w",
            height=40,
            corner_radius=8,
            font=FONT_BODY_BOLD,
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD,
            command=lambda: self.navigate("settings")
        )
        self.btn_settings.grid(row=9, column=0, padx=12, pady=(0, 16), sticky="ew")
        self.nav_buttons["settings"] = self.btn_settings

    def _build_content_area(self):
        """Constructs the container frame for interchangeable views."""
        self.content_container = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # Instantiate views
        self.views["dashboard"] = DashboardView(self.content_container, navigate_fn=self.navigate)
        self.views["compatibility"] = CompatibilityView(self.content_container)
        self.views["image"] = ImageView(self.content_container)
        self.views["advisor"] = AdvisorView(self.content_container)
        self.views["message"] = MessageView(self.content_container)
        self.views["journey"] = JourneyView(self.content_container)
        self.views["settings"] = SettingsView(self.content_container)
        
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")
            view.grid_remove() # Hide initially

    def navigate(self, view_key: str):
        """Switches active view and highlights active sidebar button."""
        if view_key not in self.views:
            return
            
        # Hide previous
        if self.current_view_key and self.current_view_key in self.views:
            self.views[self.current_view_key].grid_remove()
            if self.current_view_key in self.nav_buttons:
                self.nav_buttons[self.current_view_key].configure(
                    fg_color="transparent",
                    text_color=TEXT_SECONDARY
                )
                
        # Show new
        self.current_view_key = view_key
        active_view = self.views[view_key]
        active_view.grid()
        
        # Highlight button
        if view_key in self.nav_buttons:
            self.nav_buttons[view_key].configure(
                fg_color=BG_CARD_HOVER,
                text_color=ACCENT_PINK
            )
            
        # Trigger view refreshes where relevant
        if view_key == "dashboard" and hasattr(active_view, "refresh_stats"):
            active_view.refresh_stats()
        elif view_key == "journey" and hasattr(active_view, "refresh_milestones"):
            active_view.refresh_milestones()

def main():
    """Application launcher."""
    app = LoveAIApp()
    app.mainloop()

if __name__ == "__main__":
    main()
