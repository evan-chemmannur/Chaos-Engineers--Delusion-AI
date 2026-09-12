"""Unit tests for AI service and prompt builders."""

import unittest
from app.ai.prompt_builder import (
    build_advisor_prompt,
    build_message_analysis_prompt,
    build_message_improvement_prompt,
    SYSTEM_PROMPT
)
from app.ai.ai_advisor import AIAdvisorService
from app.ai.message_assistant import MessageAssistantService

class TestAIService(unittest.TestCase):

    def test_prompt_builder_safety_injection(self):
        """All prompts must inject critical safety and consent guardrails."""
        adv_prompt = build_advisor_prompt(
            "Friend", "Often", ["Music"], "Ask them out", "We talk every day."
        )
        self.assertIn("CRITICAL SAFETY & ETHICAL BOUNDARIES", adv_prompt)
        self.assertIn("consent", adv_prompt.lower())
        self.assertIn("harassment", adv_prompt.lower())
        self.assertIn("Ask them out", adv_prompt)

    def test_ai_advisor_offline_generation(self):
        """Advisor must reliably produce structured 6-step roadmap offline."""
        success, msg, res = AIAdvisorService.generate_roadmap(
            relationship_status="Classmate",
            communication_freq="Sometimes",
            interests=["Coding", "Gaming"],
            goal="Ask them to hang out",
            situation="We sit together in computer lab.",
            api_key="" # Force offline engine
        )
        self.assertTrue(success)
        self.assertEqual(res["source"], "offline_engine")
        self.assertGreaterEqual(len(res["steps"]), 5)
        self.assertTrue(res["reminder"])
        
        # Check first step structure
        first_step = res["steps"][0]
        self.assertIn("step_num", first_step)
        self.assertIn("title", first_step)
        self.assertIn("description", first_step)

    def test_message_assistant_offline_analysis(self):
        """Message analysis must evaluate tone, clarity, pressure, and naturalness."""
        success, msg, res = MessageAssistantService.analyze_message(
            "Hey, let me know if you want to grab coffee sometime!", api_key=""
        )
        self.assertTrue(success)
        self.assertIn("tone", res)
        self.assertIn("clarity", res)
        self.assertIn("pressure", res)
        self.assertIn("naturalness", res)
        self.assertIn("feedback", res)

    def test_message_assistant_offline_improvement(self):
        """Message improvement must produce 3 distinct tone variations."""
        tones_to_test = ["Casual", "Funny", "Confident", "Sweet", "Direct", "Short"]
        for t in tones_to_test:
            success, msg, res = MessageAssistantService.improve_message(
                "do you want to hangout", tone=t, api_key=""
            )
            self.assertTrue(success)
            self.assertEqual(len(res["options"]), 3)
            for opt in res["options"]:
                self.assertTrue(len(opt) > 0)

if __name__ == "__main__":
    unittest.main()
