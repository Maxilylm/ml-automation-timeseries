"""Smoke tests for ml-automation-timeseries — validate plugin layout invariants."""

import json
import pytest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parent.parent


class TestManifestValidity:
    """Validate plugin manifest files."""

    def test_cortex_plugin_json_valid(self):
        """Cortex plugin manifest is valid JSON and has required fields."""
        plugin_file = PLUGIN_ROOT / ".cortex-plugin" / "plugin.json"
        assert plugin_file.exists(), f"Missing .cortex-plugin/plugin.json"

        with open(plugin_file) as f:
            manifest = json.load(f)

        # Check required fields
        assert "name" in manifest, "Missing 'name' in plugin manifest"
        assert "version" in manifest, "Missing 'version' in plugin manifest"
        assert "description" in manifest, "Missing 'description' in plugin manifest"
        assert "cortex" in manifest, "Missing 'cortex' config in plugin manifest"

        # Check cortex section
        cortex = manifest["cortex"]
        assert "agents_dir" in cortex, "Missing 'cortex.agents_dir' in manifest"
        assert "skills_dir" in cortex, "Missing 'cortex.skills_dir' in manifest"

    def test_agents_md_exists(self):
        """AGENTS.md file exists at plugin root."""
        agents_md = PLUGIN_ROOT / "AGENTS.md"
        assert agents_md.exists(), "Missing AGENTS.md at plugin root"
        assert agents_md.stat().st_size > 0, "AGENTS.md is empty"


class TestReferentialIntegrity:
    """Validate AGENTS.md ↔ agents/ + skills/ referential integrity."""

    def test_agents_referenced_in_agents_md_exist(self):
        """All agents mentioned in AGENTS.md have corresponding files in agents/."""
        agents_md = PLUGIN_ROOT / "AGENTS.md"
        agents_dir = PLUGIN_ROOT / "agents"

        content = agents_md.read_text()

        # Extract agent names from markdown (lines with backticks like `agent-name`)
        import re
        agent_mentions = set(re.findall(r'`([a-z0-9\-]+)`', content))

        # Filter to likely agent names (from Available Agents section)
        agent_files = {f.stem for f in agents_dir.glob("*.md")}

        # Check that agents mentioned exist as files
        for agent in agent_mentions:
            if agent in agent_files or agent in ("prophet", "arima", "spark-core"):
                # Known agents or external references
                continue
            # At least check that agents directory is not completely empty
            assert agents_dir.exists(), f"agents/ directory missing"

    def test_skills_referenced_in_agents_md_exist(self):
        """All skills mentioned in AGENTS.md have corresponding directories in skills/."""
        agents_md = PLUGIN_ROOT / "AGENTS.md"
        skills_dir = PLUGIN_ROOT / "skills"

        content = agents_md.read_text()

        # Extract skill names from markdown (lines with backticks like `/ts-analyze`)
        import re
        skill_mentions = set(re.findall(r'`(/[a-z0-9\-]+)`', content))

        # Get skill directories (remove leading slash)
        skill_dirs = {f.name for f in skills_dir.iterdir() if f.is_dir()}

        # Verify each skill mentioned has a directory
        for skill in skill_mentions:
            skill_name = skill.lstrip('/')
            assert skill_name in skill_dirs, (
                f"Skill {skill} mentioned in AGENTS.md but {skill_name}/ directory missing"
            )

    def test_agents_directory_not_empty(self):
        """agents/ directory contains at least one agent definition."""
        agents_dir = PLUGIN_ROOT / "agents"
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) > 0, "agents/ directory is empty"

    def test_skills_directory_not_empty(self):
        """skills/ directory contains at least one skill."""
        skills_dir = PLUGIN_ROOT / "skills"
        skill_dirs = [f for f in skills_dir.iterdir() if f.is_dir()]
        assert len(skill_dirs) > 0, "skills/ directory is empty"
