import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def shipped_text_files():
    files = [
        ROOT / "README.md",
        ROOT / ".claude-plugin" / "marketplace.json",
        ROOT / ".codex-plugin" / "plugin.json",
    ]
    for pattern in ("*.md", "*.yaml", "*.yml", "*.py"):
        files.extend((ROOT / "skills").rglob(pattern))
    return sorted(set(files))


class NoEdgeSurfacesTests(unittest.TestCase):
    def test_shipped_surfaces_name_no_retired_tools_or_fields(self):
        # Retired MCP tool and field identifiers. Substring matching, so
        # singular entries also cover their plural and suffixed forms
        # (edge_type covers edge_types, edges_in covers edges_in_count).
        forbidden_tokens = (
            "strata_list_edges",
            "strata_traverse",
            "strata_suggest_edges",
            "superseded_by",
            "edges_in",
            "edges_out",
            "edge_type",
            "edge_field",
            "edge_count",
            "edges_dropped",
            "edges_created",
            "similarity_edges",
            "resolved_by",
            "observed_relation",
            "has_source_stale",
            "replace_reason",
        )

        violations = []
        for path in shipped_text_files():
            lowered = path.read_text(encoding="utf-8").lower()
            for token in forbidden_tokens:
                if token in lowered:
                    violations.append(f"{path.relative_to(ROOT)}: {token}")

        self.assertEqual([], violations, "\n".join(violations))

    def test_every_canonical_skill_is_scanned(self):
        canonical = {
            path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")
        }
        scanned = {
            path.parent.name
            for path in shipped_text_files()
            if path.name == "SKILL.md" and path.parent.parent.name == "skills"
        }
        self.assertTrue(canonical)
        self.assertEqual(canonical, scanned)

    def test_import_helper_script_is_scanned(self):
        self.assertIn(
            ROOT / "skills" / "import" / "scripts" / "import.py",
            set(shipped_text_files()),
        )

    def test_post_nodes_documents_the_receipt_fields(self):
        skill = (ROOT / "skills" / "post-nodes" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        for field in (
            "`candidates_created`",
            "`near_duplicates_flagged`",
            "`quotes_dropped`",
        ):
            with self.subTest(field=field):
                self.assertIn(field, skill)


if __name__ == "__main__":
    unittest.main()
