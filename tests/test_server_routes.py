"""Tests for web server route endpoints and SPA page routing."""

import unittest
from app.server import app

class TestServerRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_route(self):
        """Home path '/' should return index.html with 200 OK."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"LOVEAI", response.data)
        self.assertIn(b"hero-landing", response.data)

    def test_home_named_route(self):
        """'/home' and '/dashboard' paths should also return 200 OK."""
        for path in ["/home", "/dashboard"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"hero-landing", response.data)

    def test_feature_routes(self):
        """Feature paths like '/compatibility', '/message' should return 200 OK."""
        routes = [
            "/compatibility",
            "/message",
            "/journey",
            "/milestones"
        ]
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"LOVEAI", response.data)

    def test_removed_routes_redirect(self):
        """Removed paths ('/image', '/advisor') should redirect to '/' with 302."""
        for path in ["/image", "/advisor"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers["Location"], "/")

    def test_settings_route_removed(self):
        """The '/settings' path should no longer exist and return 404."""
        response = self.client.get("/settings")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
