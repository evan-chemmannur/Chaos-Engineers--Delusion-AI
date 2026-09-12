"""Unit tests for OpenCV image comparator."""

import os
import unittest
import numpy as np
from PIL import Image

from app.core.image_comparator import ImageComparator
from app.config import IMAGE_DISCLAIMER

class TestImageComparator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create synthetic test images in scratch folder."""
        cls.test_dir = os.path.join(os.path.dirname(__file__), "test_assets")
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Image 1: Solid red circle on blue background
        img1 = Image.new("RGB", (200, 200), (30, 40, 180))
        cls.img1_path = os.path.join(cls.test_dir, "test1.png")
        img1.save(cls.img1_path)
        
        # Image 2: Similar colors
        img2 = Image.new("RGB", (200, 200), (35, 45, 175))
        cls.img2_path = os.path.join(cls.test_dir, "test2.png")
        img2.save(cls.img2_path)
        
        # Image 3: Completely different color (bright yellow)
        img3 = Image.new("RGB", (200, 200), (250, 240, 20))
        cls.img3_path = os.path.join(cls.test_dir, "test3.png")
        img3.save(cls.img3_path)

    @classmethod
    def tearDownClass(cls):
        """Cleanup test images."""
        for p in [cls.img1_path, cls.img2_path, cls.img3_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        if os.path.exists(cls.test_dir):
            try:
                os.rmdir(cls.test_dir)
            except Exception:
                pass

    def test_identical_images(self):
        """Comparing an image to itself must yield 100% similarity."""
        success, err, res = ImageComparator.compare_images(self.img1_path, self.img1_path)
        self.assertTrue(success)
        self.assertEqual(res["similarity_score"], 100)
        self.assertEqual(res["disclaimer"], IMAGE_DISCLAIMER)

    def test_similar_vs_different_images(self):
        """Similar colored images should score higher than contrasting images."""
        s_sim, _, res_sim = ImageComparator.compare_images(self.img1_path, self.img2_path)
        s_diff, _, res_diff = ImageComparator.compare_images(self.img1_path, self.img3_path)
        
        self.assertTrue(s_sim)
        self.assertTrue(s_diff)
        self.assertGreater(res_sim["similarity_score"], res_diff["similarity_score"])

    def test_missing_file_handling(self):
        """Non-existent file should be caught gracefully without crashing."""
        success, err, res = ImageComparator.compare_images("non_existent_file.png", self.img1_path)
        self.assertFalse(success)
        self.assertTrue("not exist" in err.lower() or "error" in err.lower())

if __name__ == "__main__":
    unittest.main()
