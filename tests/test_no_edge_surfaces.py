import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def shipped_text_files():
    files = [
        ROOT / "README.md",
        ROOT / ".claude-plugin" / "marketplace.json",
        ROOT / ".codex-plugin" / "plugin.json",
    ]
    files.extend((ROOT / "skills").rglob("*.md"))
    files.extend((ROOT / "skills").rglob("*.yaml"))
    return sorted(set(files))


class NoEdgeSurfacesTests(unittest.TestCase):
    def test_shipped_skill_surfaces_are_edge_free(self):
        forbidden_literals = (
            "strata_list_edges",
            "strata_traverse",
            "strata_suggest_edges",
            "superseded_by",
            "edges_in_count",
            "edges_out_count",
            "edges_in",
            "edges_out",
            "edge_types",
            "edge_fields",
            "edge_count",
            "resolved_by",
            "observed_relation",
            "has_source_stale",
            "replace_reason",
            "edges_dropped",
            "countered, replaced, or resolved",
            "stratagraph can connect repeated support after import",
            "stratagraph connects it to relevant imported history",
        )
        forbidden_words = re.compile(
            r"\b(?:edge|edges|relationship|relationships)\b", re.IGNORECASE
        )

        violations = []
        for path in shipped_text_files():
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for literal in forbidden_literals:
                if literal in lowered:
                    violations.append(f"{path.relative_to(ROOT)}: {literal}")
            for match in forbidden_words.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                violations.append(
                    f"{path.relative_to(ROOT)}:{line}: {match.group(0)}"
                )

        self.assertEqual([], violations, "\n".join(violations))

    def test_all_five_skills_are_scanned(self):
        scanned = {
            path.parent.name
            for path in shipped_text_files()
            if path.name == "SKILL.md" and path.parent.parent.name == "skills"
        }
        self.assertEqual(
            {"find-in-stratagraph", "post", "post-nodes", "import", "gather"},
            scanned,
        )

    def test_required_import_references_are_scanned(self):
        scanned = set(shipped_text_files())
        required = {
            ROOT / "skills" / "import" / "references" / "evidence.md",
            ROOT / "skills" / "import" / "references" / "technical.md",
        }
        self.assertTrue(required <= scanned, required - scanned)

    def test_import_guidance_is_nodes_only(self):
        evidence = (
            ROOT / "skills" / "import" / "references" / "evidence.md"
        ).read_text(encoding="utf-8")
        skill = (ROOT / "skills" / "import" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Semantic indexing works at node level", evidence)
        self.assertIn("could change independently", evidence)
        self.assertIn(
            "keep each source-backed occurrence in a separate node",
            evidence,
        )
        self.assertIn(
            "its extracted nodes are indexed semantically alongside the imported nodes",
            skill,
        )

    def test_post_nodes_matches_the_nodes_only_receipt(self):
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
        self.assertIn(
            "This works for both `transcript` and `document` sources",
            skill,
        )


if __name__ == "__main__":
    unittest.main()
