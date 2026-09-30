import sys
import unittest
import asyncio
from pathlib import Path
from starlette.requests import Request
from fastapi.testclient import TestClient

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))
from app.main import app
from app.database import get_submissions

client = TestClient(app)

class TestDainikJahanIPTV(unittest.TestCase):

    def test_01_health_check(self):
        res = client.get("/api/health-check")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["channels_online"], 19)

    def test_02_channels_api(self):
        res = client.get("/api/channels")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 19)

        # Test filter by category
        res_cat = client.get("/api/channels?category=News")
        self.assertEqual(res_cat.status_code, 200)
        self.assertGreaterEqual(res_cat.json()["count"], 5)

        # Test single channel
        res_ch = client.get("/api/channels/dainik-jahan-live")
        self.assertEqual(res_ch.status_code, 200)
        self.assertEqual(res_ch.json()["channel"]["name"], "দৈনিক জাহান লাইভ")

    def test_03_main_html_pages(self):
        pages = ["", "epg", "documentaries", "news", "discovery", "vod", "favorites", "submissions", "federation", "contact"]
        for p in pages:
            url = f"/{p}" if p else "/"
            res = client.get(url)
            self.assertEqual(res.status_code, 200, f"Page {url} failed with {res.status_code}")
            self.assertIn("দৈনিক জাহান", res.text)

    def test_04_policy_pages(self):
        policies = ["copyright", "privacy", "editorial", "distribution", "governance", "federation", "security", "terms", "opensource", "contact"]
        for p in policies:
            url = f"/policy/{p}"
            res = client.get(url)
            self.assertEqual(res.status_code, 200, f"Policy {url} failed with {res.status_code}")
            self.assertIn("দৈনিক জাহান", res.text)

    def test_05_submissions_api(self):
        payload = {
            "type": "channel_suggestion",
            "name": "টেস্ট ব্যবহারকারী",
            "email": "test@dainikjahan.com",
            "phone": "+8801700000000",
            "organization": "ঢাকা মিডিয়া",
            "title": "নতুন কমিউনিটি চ্যানেল প্রস্তাব",
            "details": "ময়মনসিংহ লোকগান সম্প্রচারের জন্য বিশেষ প্রস্তাবনা।",
            "source_url": "https://stream.example.org/live.m3u8"
        }
        res = client.post("/api/submissions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["tracking_id"].startswith("DJ-"))

        # Verify database record
        subs = get_submissions(limit=5)
        found = any(s["id"] == data["tracking_id"] for s in subs)
        self.assertTrue(found, "Submission not found in SQLite database")

    def test_06_node_registration_api(self):
        payload = {
            "name": "সিলেট কমিউনিটি নোড",
            "operator": "সিলেট ব্রডকাস্ট ট্রাস্ট",
            "endpoint_url": "https://sylhet.example.org/api",
            "region": "Sylhet, BD",
            "channels_count": 2
        }
        res = client.post("/api/federation/register", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["node_id"].startswith("NODE-"))

    def test_07_epg_and_news_apis(self):
        res_epg = client.get("/api/epg")
        self.assertEqual(res_epg.status_code, 200)
        self.assertIn("dainik-jahan-live", res_epg.json()["epg"])

        res_news = client.get("/api/news")
        self.assertEqual(res_news.status_code, 200)
        self.assertGreaterEqual(res_news.json()["count"], 5)

    def test_08_proxy_safe_api_routes(self):
        paths = [
            "/iptv-api/channels",
            "/iptv-api/channels/dainik-jahan-live",
            "/iptv-api/health-check",
            "/iptv-api/epg",
            "/iptv-api/vod",
            "/iptv-api/news",
            "/iptv-api/federation",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 200)

        payload = {
            "type": "channel_suggestion",
            "name": "টেস্ট ব্যবহারকারী",
            "email": "test@dainikjahan.com",
            "title": "রুট প্রিফিক্স পরীক্ষা",
            "details": "প্রকাশ্য IPTV API রুট পরীক্ষা।",
        }
        response = client.post("/iptv-api/submissions", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        submissions_page = client.get("/submissions")
        self.assertIn("/iptv-api/submissions", submissions_page.text)
        federation_page = client.get("/federation")
        self.assertIn("/iptv-api/federation/register", federation_page.text)

if __name__ == "__main__":
    unittest.main()
