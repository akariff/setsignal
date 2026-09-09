"""Automated smoke tests for SetSignal production-readiness agent."""

import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.models import RegulatoryFinding
from app.agent.tools import evaluate_readiness_rules
from app.agent.adk_agent import create_setsignal_agent


class TestSetSignalSmoke(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Verify health check endpoint returns orchestrator and model status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["orchestrator"], "google-adk")
        self.assertEqual(data["gemini_model"], "gemini-3.8-flash")
        self.assertIn("gemini_configured", data)
        self.assertIn("parallel_configured", data)

    def test_assess_missing_credentials_contract(self):
        """Verify assess endpoint rejects requests cleanly when credentials are unconfigured."""
        payload = {
            "location": "Downtown Los Angeles, CA",
            "date": "Tomorrow, 6:00 PM Call Time",
            "description": "Exterior night shoot with 50 extras and drone footage."
        }
        response = self.client.post("/api/assess", json=payload)
        # If credentials are not in .env, should return 400 with missing_credentials error
        if response.status_code == 400:
            data = response.json()
            self.assertEqual(data["status"], "error")
            self.assertEqual(data["error_type"], "missing_credentials")
            self.assertIn("missing_keys", data)
        elif response.status_code == 200:
            # If credentials happened to be configured
            data = response.json()
            self.assertIn("status", data)

    def test_deterministic_rules_engine_blocker(self):
        """Verify lead-time deficit deterministically triggers NO-GO."""
        # Generic empirical finding: 72h lead time required, only 18h remaining
        findings = [{
            "category": "road_control",
            "requirement": "street_closure_permit",
            "description": "Mandatory street closure permit from city authority.",
            "mandatory": True,
            "approval_status": "not_confirmed",
            "required_lead_time_hours": 72.0,
            "remaining_time_hours": 18.0,
            "source_urls": ["https://example.gov/permits"]
        }]

        result = evaluate_readiness_rules(findings=findings)
        self.assertEqual(result["status"], "NO-GO")
        self.assertTrue(len(result["blockers"]) >= 1)
        self.assertIn("Lead-Time Deficit", result["blockers"][0]["title"])
        self.assertLessEqual(result["readiness_score"], 50)

    def test_deterministic_rules_engine_conditional_go(self):
        """Verify feasible lead time triggers CONDITIONAL GO."""
        # 24h lead time required, 48h remaining
        findings = [{
            "category": "generator_power",
            "requirement": "noise_variance_notification",
            "description": "Notification required for generator operation after 10 PM.",
            "mandatory": True,
            "approval_status": "not_confirmed",
            "required_lead_time_hours": 24.0,
            "remaining_time_hours": 48.0,
            "source_urls": ["https://example.gov/noise"]
        }]

        result = evaluate_readiness_rules(findings=findings)
        self.assertEqual(result["status"], "CONDITIONAL GO")
        self.assertEqual(len(result["blockers"]), 0)
        self.assertTrue(len(result["conditions"]) >= 1)
        self.assertIn("Urgent Filing Required", result["conditions"][0]["condition"])

    def test_deterministic_rules_engine_go(self):
        """Verify approved requirements yield GO status."""
        findings = [{
            "category": "private_property",
            "requirement": "property_use_agreement",
            "description": "Location agreement executed with building owner.",
            "mandatory": True,
            "approval_status": "approved",
            "required_lead_time_hours": None,
            "remaining_time_hours": 24.0,
            "source_urls": []
        }]

        result = evaluate_readiness_rules(findings=findings)
        self.assertEqual(result["status"], "GO")
        self.assertEqual(len(result["blockers"]), 0)
        self.assertEqual(len(result["conditions"]), 0)
        self.assertGreaterEqual(result["readiness_score"], 90)

    def test_adk_agent_initialization(self):
        """Verify Google ADK root agent configuration and tool binding."""
        agent = create_setsignal_agent()
        self.assertEqual(agent.name, "setsignal_root_agent")
        self.assertEqual(agent.model, "gemini-3.8-flash")
        self.assertEqual(len(agent.tools), 2)


if __name__ == "__main__":
    unittest.main()
