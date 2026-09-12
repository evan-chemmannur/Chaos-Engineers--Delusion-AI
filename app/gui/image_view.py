"""Image Similarity view for LoveAI using OpenCV."""

import os
import threading
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image

from app.gui.theme import (
    BG_MAIN, BG_CARD, BG_INPUT, BG_CARD_HOVER, ACCENT_PINK, ACCENT_PINK_HOVER,
    ACCENT_PURPLE, ACCENT_PURPLE_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_SCORE, FONT_SCORE_MEDIUM, BORDER_SUBTLE, DANGER_RED
)
from app.gui.components import CardFrame, DisclaimerBanner
from app.config import IMAGE_DISCLAIMER
from app.core.image_comparator import ImageComparator

class ImageView(ctk.CTkScrollableFrame):
    """View allowing users to compare visual similarity of two local images."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.img1_path = ""
        self.img2_path = ""
        self.preview1_img = None
        self.preview2_img = None
        
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self):
        # 1. Header Card
        header = CardFrame(self)
        header.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, text="📸 Image Similarity Engine", font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 2), sticky="w")
        
        ctk.CTkLabel(
            header,
            text="Local OpenCV computer vision comparison: Color histograms, pixel structural delta, and ORB feature keypoints.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        
        # 2. Dual Upload Grid (Two Columns)
        upload_grid = ctk.CTkFrame(self, fg_color="transparent")
        upload_grid.grid(row=1, column=0, padx=20, pady=6, sticky="ew")
        upload_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Upload Box 1
        self.box1 = CardFrame(upload_grid)
        self.box1.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="nsew")
        self.box1.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.box1, text="Image 1", font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY).pack(pady=(14, 6))
        
        self.lbl_preview1 = ctk.CTkLabel(
            self.box1,
            text="No Image Selected\n(Click Browse Below)",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            width=180,
            height=140,
            fg_color=BG_INPUT,
            corner_radius=8
        )
        self.lbl_preview1.pack(padx=20, pady=4)
        
        self.lbl_path1 = ctk.CTkLabel(self.box1, text="No file chosen", font=FONT_SMALL, text_color=TEXT_MUTED)
        self.lbl_path1.pack(pady=(4, 6))
        
        ctk.CTkButton(
            self.box1,
            text="📁 Select Image 1",
            font=FONT_SMALL,
            fg_color=BG_CARD_HOVER,
            hover_color="#2f3144",
            border_width=1,
            border_color=BORDER_SUBTLE,
            command=self._select_image1
        ).pack(padx=20, pady=(0, 16))
        
        # Upload Box 2
        self.box2 = CardFrame(upload_grid)
        self.box2.grid(row=0, column=1, padx=(10, 0), pady=4, sticky="nsew")
        self.box2.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.box2, text="Image 2", font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY).pack(pady=(14, 6))
        
        self.lbl_preview2 = ctk.CTkLabel(
            self.box2,
            text="No Image Selected\n(Click Browse Below)",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            width=180,
            height=140,
            fg_color=BG_INPUT,
            corner_radius=8
        )
        self.lbl_preview2.pack(padx=20, pady=4)
        
        self.lbl_path2 = ctk.CTkLabel(self.box2, text="No file chosen", font=FONT_SMALL, text_color=TEXT_MUTED)
        self.lbl_path2.pack(pady=(4, 6))
        
        ctk.CTkButton(
            self.box2,
            text="📁 Select Image 2",
            font=FONT_SMALL,
            fg_color=BG_CARD_HOVER,
            hover_color="#2f3144",
            border_width=1,
            border_color=BORDER_SUBTLE,
            command=self._select_image2
        ).pack(padx=20, pady=(0, 16))
        
        # Error / Status Label
        self.lbl_status = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=DANGER_RED)
        self.lbl_status.grid(row=2, column=0, padx=20, pady=(6, 2), sticky="w")
        
        # Compare Button
        self.btn_compare = ctk.CTkButton(
            self,
            text="Run Visual Comparison 📸",
            font=FONT_BODY_BOLD,
            height=42,
            fg_color=ACCENT_PINK,
            hover_color=ACCENT_PINK_HOVER,
            corner_radius=8,
            command=self._on_compare
        )
        self.btn_compare.grid(row=3, column=0, padx=20, pady=(4, 12), sticky="ew")
        
        # 3. Results Card (Hidden initially)
        self.results_card = CardFrame(self, fg_color="#181826", border_color="#36284a")
        self.results_card.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.results_card.grid_columnconfigure((0, 1, 2), weight=1)
        self.results_card.grid_remove()
        
        # Rating Banner
        self.lbl_rating = ctk.CTkLabel(
            self.results_card, text="", font=FONT_SUBTITLE, text_color=ACCENT_PINK
        )
        self.lbl_rating.grid(row=0, column=0, columnspan=3, padx=20, pady=(16, 2), sticky="w")
        
        # Metric Breakdown
        box_total = CardFrame(self.results_card, fg_color=BG_CARD)
        box_total.grid(row=1, column=0, padx=(16, 6), pady=(4, 16), sticky="nsew")
        ctk.CTkLabel(box_total, text="Visual Similarity", font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(12, 0))
        self.val_total = ctk.CTkLabel(box_total, text="--%", font=FONT_SCORE, text_color=ACCENT_PINK)
        self.val_total.pack(pady=(0, 12))
        
        box_hist = CardFrame(self.results_card, fg_color=BG_CARD)
        box_hist.grid(row=1, column=1, padx=6, pady=(4, 16), sticky="nsew")
        ctk.CTkLabel(box_hist, text="Color Palette Match", font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(12, 0))
        self.val_hist = ctk.CTkLabel(box_hist, text="--%", font=FONT_SCORE_MEDIUM, text_color=TEXT_PRIMARY)
        self.val_hist.pack(pady=(4, 12))
        
        box_feat = CardFrame(self.results_card, fg_color=BG_CARD)
        box_feat.grid(row=1, column=2, padx=(6, 16), pady=(4, 16), sticky="nsew")
        ctk.CTkLabel(box_feat, text="Feature & Pixel Match", font=FONT_SMALL, text_color=TEXT_MUTED).pack(pady=(12, 0))
        self.val_feat = ctk.CTkLabel(box_feat, text="--%", font=FONT_SCORE_MEDIUM, text_color=ACCENT_PURPLE)
        self.val_feat.pack(pady=(4, 12))
        
        # 4. Mandatory Disclaimer Banner
        disclaimer = DisclaimerBanner(self, IMAGE_DISCLAIMER)
        disclaimer.grid(row=5, column=0, padx=20, pady=(10, 24), sticky="ew")

    def _select_image1(self):
        path = filedialog.askopenfilename(
            title="Select First Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All Files", "*.*")]
        )
        if path:
            self.img1_path = path
            self.lbl_path1.configure(text=os.path.basename(path))
            self._update_preview(1, path)

    def _select_image2(self):
        path = filedialog.askopenfilename(
            title="Select Second Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All Files", "*.*")]
        )
        if path:
            self.img2_path = path
            self.lbl_path2.configure(text=os.path.basename(path))
            self._update_preview(2, path)

    def _update_preview(self, box_num: int, path: str):
        try:
            pil_img = Image.open(path)
            pil_img.thumbnail((160, 130))
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            if box_num == 1:
                self.preview1_img = ctk_img
                self.lbl_preview1.configure(image=ctk_img, text="")
            else:
                self.preview2_img = ctk_img
                self.lbl_preview2.configure(image=ctk_img, text="")
        except Exception as e:
            print(f"Error creating thumbnail: {e}")

    def _on_compare(self):
        if not self.img1_path or not self.img2_path:
            self.lbl_status.configure(text="Please select both images before running comparison.", text_color=DANGER_RED)
            return
            
        self.lbl_status.configure(text="Processing images with OpenCV...", text_color=ACCENT_PURPLE)
        self.btn_compare.configure(state="disabled", text="Analyzing Visual Features...")
        
        # Run in thread so GUI remains responsive
        threading.Thread(target=self._run_comparison_thread, daemon=True).start()

    def _run_comparison_thread(self):
        success, err, result = ImageComparator.compare_images(self.img1_path, self.img2_path)
        
        # Schedule GUI update on main thread
        self.after(0, lambda: self._handle_result(success, err, result))

    def _handle_result(self, success, err, result):
        self.btn_compare.configure(state="normal", text="Run Visual Comparison 📸")
        if not success:
            self.lbl_status.configure(text=err, text_color=DANGER_RED)
            return
            
        self.lbl_status.configure(text="")
        
        score = result["similarity_score"]
        rating = result["rating"]
        breakdown = result["breakdown"]
        
        self.lbl_rating.configure(text=f"Result: {rating} ({score}%)")
        self.val_total.configure(text=f"{score}%")
        self.val_hist.configure(text=f"{breakdown['color_similarity']}%")
        self.val_feat.configure(text=f"{breakdown['feature_similarity']}%")
        
        self.results_card.grid()
