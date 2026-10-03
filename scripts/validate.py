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
for filename, transport in [("mcp.json", "streamable-http"), (".mcp.json", "http")]:
    servers = json.loads((root / filename).read_text())["mcpServers"]
    assert servers == {"polymorfa-docs": {"type": transport, "url": "https://docs.polymorfa.com/mcp"}}, filename
for filename in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"):
    manifest = json.loads((root / filename).read_text())
    assert (root / manifest["mcpServers"]).is_file(), filename
    assert (root / manifest["skills"]).is_dir(), filename
