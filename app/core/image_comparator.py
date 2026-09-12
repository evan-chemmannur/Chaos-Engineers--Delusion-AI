"""Local computer-vision image similarity engine using OpenCV."""

import os
from typing import Tuple, Dict, Any
import numpy as np
import cv2

from app.core.validation import validate_image_file
from app.config import IMAGE_DISCLAIMER

class ImageComparator:
    """Compares two images locally using OpenCV computer vision techniques."""
    
    STANDARD_SIZE = (300, 300)
    
    @classmethod
    def load_image_safely(cls, image_path: str) -> np.ndarray:
        """Loads an image safely supporting Windows paths with Unicode characters."""
        # np.fromfile + cv2.imdecode avoids Windows Unicode file path bugs in standard cv2.imread
        with open(image_path, "rb") as f:
            bytes_data = bytearray(f.read())
        numpy_array = np.asarray(bytes_data, dtype=np.uint8)
        img = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not decode image at '{image_path}'.")
        return img
        
    @classmethod
    def compare_images(cls, path1: str, path2: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Compares two images using color histogram, pixel structure, and ORB features.
        
        Returns:
            (success, error_message, result_dict)
        """
        # Validate file 1
        v1, err1 = validate_image_file(path1)
        if not v1:
            return False, f"Image 1 error: {err1}", {}
            
        # Validate file 2
        v2, err2 = validate_image_file(path2)
        if not v2:
            return False, f"Image 2 error: {err2}", {}
            
        try:
            img1 = cls.load_image_safely(path1)
            img2 = cls.load_image_safely(path2)
        except Exception as e:
            return False, f"Failed to load image: {e}", {}
            
        # Check if identical files or identical pixel arrays
        if os.path.abspath(path1) == os.path.abspath(path2):
            return True, "", {
                "similarity_score": 100,
                "rating": "Identical Image",
                "breakdown": {
                    "color_similarity": 100,
                    "pixel_similarity": 100,
                    "feature_similarity": 100,
                },
                "disclaimer": IMAGE_DISCLAIMER,
            }
            
        try:
            # 1. Preprocessing & Normalization
            resized1 = cv2.resize(img1, cls.STANDARD_SIZE)
            resized2 = cv2.resize(img2, cls.STANDARD_SIZE)
            
            # Convert color spaces
            hsv1 = cv2.cvtColor(resized1, cv2.COLOR_BGR2HSV)
            hsv2 = cv2.cvtColor(resized2, cv2.COLOR_BGR2HSV)
            
            gray1 = cv2.cvtColor(resized1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(resized2, cv2.COLOR_BGR2GRAY)
            
            # 2. Color Histogram Comparison (HSV)
            hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256])
            hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
            
            # Correlation produces value between -1.0 and 1.0
            raw_hist_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            color_similarity = max(0.0, min(100.0, ((raw_hist_corr + 1.0) / 2.0) * 100.0))
            
            # 3. Pixel Structural Similarity (Normalized difference)
            abs_diff = cv2.absdiff(gray1, gray2)
            mean_diff = float(np.mean(abs_diff))
            pixel_similarity = max(0.0, min(100.0, 100.0 - (mean_diff / 255.0 * 100.0)))
            
            # 4. ORB Feature Matching
            orb = cv2.ORB_create(nfeatures=500)
            kp1, des1 = orb.detectAndCompute(gray1, None)
            kp2, des2 = orb.detectAndCompute(gray2, None)
            
            if des1 is not None and des2 is not None and len(des1) > 0 and len(des2) > 0:
                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
                matches = bf.knnMatch(des1, des2, k=2)
                
                # Apply Lowe's ratio test
                good_matches = []
                for m in matches:
                    if len(m) == 2:
                        if m[0].distance < 0.78 * m[1].distance:
                            good_matches.append(m[0])
                    elif len(m) == 1:
                        good_matches.append(m[0])
                        
                min_kp = max(1, min(len(kp1), len(kp2)))
                feature_similarity = min(100.0, (len(good_matches) / min_kp) * 180.0)
            else:
                # Fallback to structural score if no distinct keypoints
                feature_similarity = (color_similarity + pixel_similarity) / 2.0
                
            # 5. Composite Score Calculation
            composite = round(
                color_similarity * 0.45 +
                pixel_similarity * 0.35 +
                feature_similarity * 0.20
            )
            composite = max(0, min(100, composite))
            
            # 6. Rating classification
            if composite >= 80:
                rating = "നല്ല സാമ്യം"
            elif composite >= 55:
                rating = "മിതമായ സാമ്യം"
            else:
                rating = "വ്യത്യസ്തമായ Style"
                
            result = {
                "similarity_score": composite,
                "rating": rating,
                "breakdown": {
                    "color_similarity": round(color_similarity),
                    "pixel_similarity": round(pixel_similarity),
                    "feature_similarity": round(feature_similarity),
                },
                "disclaimer": IMAGE_DISCLAIMER,
            }
            
            return True, "", result
            
        except Exception as e:
            return False, f"Comparison error: {e}", {}
