import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills" / "find-in-stratagraph" / "SKILL.md"


class FindInStratagraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.lower = cls.skill.lower()

    def test_semantic_search_is_the_discovery_layer(self):
        self.assertIn("search is always the discovery layer", self.lower)
        self.assertIn("chronology still starts with search", self.lower)
        self.assertIn(
            "treat `semantic_similarity` when supplied as relative proximity, not truth, confidence, relevance, or currentness.",
            self.lower,
        )
        self.assertIn(
            "never answer a substantive question from search snippets alone",
            self.lower,
        )

    def test_lineage_requires_a_useful_search_hit_and_available_fence(self):
        for contract in (
            "`strata_explore_lineage` is attached",
            "`lineage.state: available`",
            "`lineage.as_of_fence`",
            "`older_available`",
            "`newer_available`",
            "adjacent chronology would help",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, self.lower)

        self.assertIn(
            "the exact returned node key, the advertised direction, and the response-level fence",
            self.lower,
        )

    def test_lineage_paging_and_farther_steps_keep_the_snapshot(self):
        self.assertIn(
            "keep the same anchor node, direction, and fence, and add the returned cursor",
            self.lower,
        )
        self.assertIn(
            "use a relevant returned node that advertises the requested direction, omit the prior cursor, and retain the original fence",
            self.lower,
        )
        self.assertIn("do not expand chronology automatically", self.lower)

    def test_unavailable_or_expired_lineage_falls_back_to_search(self):
        for condition in (
            "lineage tool is absent",
            "lineage is unavailable",
            "the fence is null",
            "no useful direction is advertised",
            "exploration returns `expired`",
        ):
            with self.subTest(condition=condition):
                self.assertIn(condition, self.lower)
        self.assertIn("never reuse an expired fence", self.lower)

    def test_current_state_is_evidence_based_and_uncertain(self):
        for field in (
            "`occurred_at`",
            "`occurred_at_basis`",
            "`review`",
            "`admission_method`",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)
        self.assertIn(
            "mcp chronology cannot certify an authoritative current head",
            self.lower,
        )
        self.assertIn(
            "never treat the newest returned claim or the end of a lineage path as current",
            self.lower,
        )
        self.assertIn("state any remaining uncertainty", self.lower)

    def test_lineage_does_not_change_node_status(self):
        self.assertIn(
            "they do not hide, invalidate, or supersede any node",
            self.lower,
        )
        for limit in ("truth", "currentness", "completeness", "relevance"):
            with self.subTest(limit=limit):
                self.assertIn(limit, self.lower)


if __name__ == "__main__":
    unittest.main()
