import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills" / "find-in-stratagraph" / "SKILL.md"


class FindInStratagraphTests(unittest.TestCase):
    """Pin the MCP contract tokens the skill teaches: tool names, field
    names, and gating conditions. Prose wording is free to change."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_PATH.read_text(encoding="utf-8")
        cls.lower = cls.skill.lower()

    def test_read_tools_are_documented(self):
        for tool in (
            "`strata_search_nodes`",
            "`strata_get_node`",
            "`strata_get_nodes`",
            "`strata_get_document`",
            "`strata_list_documents`",
            "`strata_list_briefs`",
            "`strata_get_brief`",
            "`strata_get_graph_schema`",
            "`strata_explore_lineage`",
        ):
            with self.subTest(tool=tool):
                self.assertIn(tool, self.skill)

    def test_lineage_gate_conditions(self):
        for condition in (
            "`strata_explore_lineage` is attached",
            "`lineage.state: available`",
            "`lineage.as_of_fence`",
            "`lineage_context.path_count` is greater than zero",
        ):
            with self.subTest(condition=condition):
                self.assertIn(condition, self.lower)

    def test_lineage_response_fields(self):
        for field in (
            "`paths`",
            "`page`",
            "`origin_context`",
            "`span.complete: false`",
            "`path_count_basis` is `lower_bound`",
            "`paths_truncated`",
            "`continues_before`",
            "`continues_after`",
            "`continuation.members_truncated`",
            "`expired`",
            "cursor",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.lower)

    def test_evidence_fields(self):
        for field in (
            "`semantic_similarity`",
            "`occurred_at`",
            "`occurred_at_basis`",
            "`review`",
            "`admission_method`",
            "`truncated: true`",
            "`document_date`",
            "`record_created`",
            "`speaker`",
        ):
            with self.subTest(field=field):
                self.assertIn(field, self.skill)

    def test_admission_contract_values(self):
        self.assertIn(
            "`admission_method` is `import` and `review` is `unreviewed`",
            self.lower,
        )
        self.assertIn("`admission_method` is absent", self.lower)
        self.assertIn("`imported`", self.lower)


if __name__ == "__main__":
    unittest.main()
