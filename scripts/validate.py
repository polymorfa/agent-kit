import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
for path in root.rglob("*.json"):
    json.loads(path.read_text())
for path in (root / "skills").glob("*/SKILL.md"):
    assert path.read_text().startswith(f"---\nname: {path.parent.name}\n"), path
for filename in ("plugin.json", ".claude-plugin/plugin.json", ".cursor-plugin/plugin.json", "gemini-extension.json"):
    assert json.loads((root / filename).read_text())["version"] == "0.1.0", filename
print("Manifests and skills validated")
