"""Build the static /.well-known/skills endpoint using only the standard library."""

import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist" / "well-known-skills"


def skill_entries(skills_dir):
    entries = []
    for directory in sorted(skills_dir.iterdir()):
        if not directory.is_dir():
            continue
        if directory.is_symlink() or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", directory.name):
            raise ValueError(f"Invalid skill directory: {directory}")
        text = (directory / "SKILL.md").read_text(encoding="utf-8")
        # This repository uses plain, single-line YAML metadata. Fail rather than
        # silently misreading quoted or multiline YAML when that convention changes.
        match = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n", text)
        if not match or match[1] != directory.name or match[2][0] in "'\"|>{[&*!":
            raise ValueError(f"Expected plain name and single-line description: {directory}")
        files = []
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlinks cannot be published: {path}")
            if path.is_file():
                files.append(path.relative_to(directory).as_posix())
        entries.append({"name": directory.name, "description": match[2], "files": files})
    if not entries:
        raise ValueError("No skills found")
    return entries


def build(skills_dir=ROOT / "skills", output=OUTPUT):
    entries = skill_entries(skills_dir)
    if output.is_symlink() or output.parent.is_symlink():
        raise ValueError(f"Output must not be a symlink: {output}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for entry in entries:
        for filename in entry["files"]:
            target = output / entry["name"] / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(skills_dir / entry["name"] / filename, target)
    (output / "index.json").write_text(
        json.dumps({"skills": entries}, indent=2) + "\n", encoding="utf-8"
    )
    return output


def validate_index(output=OUTPUT, skills_dir=ROOT / "skills"):
    entries = skill_entries(skills_dir)
    actual = json.loads((output / "index.json").read_text(encoding="utf-8"))
    assert actual == {"skills": entries}, "Skills index differs from source metadata or files"
    expected = {"index.json"}
    for entry in entries:
        for filename in entry["files"]:
            relative = Path(entry["name"]) / filename
            expected.add(relative.as_posix())
            assert (output / relative).read_bytes() == (skills_dir / relative).read_bytes(), relative
    assert all(not path.is_symlink() for path in output.rglob("*")), "Symlink in output"
    assert {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()} == expected


if __name__ == "__main__":
    build()
    validate_index()
    print(f"Built and validated {OUTPUT}")
