"""Targeted non-live tests for the environment-gated UI preview system."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import config
from app.main import app
from app.models import ReadinessAssessment


class TestUiPreview(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_reports_preview_flag(self):
        with patch.object(config, "ENABLE_UI_PREVIEW", True):
            response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ui_preview_enabled"])

    def test_preview_endpoint_is_hidden_when_disabled(self):
        with patch.object(config, "ENABLE_UI_PREVIEW", False):
            response = self.client.get("/api/ui-preview/no-go")
        self.assertEqual(response.status_code, 404)

    def test_preview_fixtures_are_schema_valid_without_credentials(self):
        expected_status = {
            "no-go": "NO-GO",
            "conditional": "CONDITIONAL GO",
            "go": "GO",
        }

        with (
            patch.object(config, "ENABLE_UI_PREVIEW", True),
            patch.object(config, "GEMINI_API_KEY", ""),
            patch.object(config, "PARALLEL_API_KEY", ""),
        ):
            for scenario, status in expected_status.items():
                with self.subTest(scenario=scenario):
                    response = self.client.get(f"/api/ui-preview/{scenario}")
                    self.assertEqual(response.status_code, 200)
                    assessment = ReadinessAssessment.model_validate(response.json())
                    self.assertEqual(assessment.status, status)
                    self.assertGreaterEqual(len(assessment.evidence), 2)

    def test_unknown_preview_scenario_returns_404(self):
        with patch.object(config, "ENABLE_UI_PREVIEW", True):
            response = self.client.get("/api/ui-preview/not-a-scenario")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
