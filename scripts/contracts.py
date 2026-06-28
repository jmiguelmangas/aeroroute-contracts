from __future__ import annotations

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def contract_files(root: Path = ROOT) -> list[Path]:
    candidates = [
        *(root / "json-schema").rglob("*.json"),
        *(root / "openapi").rglob("*.json"),
    ]
    return sorted(path for path in candidates if not path.name.startswith("._"))


def validate_contracts(root: Path = ROOT) -> list[Path]:
    paths = contract_files(root)
    if not paths:
        raise ValueError("No contract documents found")
    for path in paths:
        document = json.loads(path.read_text())
        relative = path.relative_to(root)
        if relative.parts[0] == "json-schema" and "$schema" not in document:
            raise ValueError(f"{relative}: missing $schema")
        if relative.parts[0] == "openapi" and "openapi" not in document:
            raise ValueError(f"{relative}: missing openapi version")
    return paths


def format_contracts(root: Path = ROOT) -> None:
    for path in validate_contracts(root):
        document = json.loads(path.read_text())
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


def build_bundle(root: Path = ROOT, output: Path | None = None) -> Path:
    paths = validate_contracts(root)
    version = (root / "VERSION").read_text().strip()
    destination = output or root / "dist" / f"aeroroute-contracts-{version}.zip"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        archive.write(root / "VERSION", "VERSION")
        for path in paths:
            archive.write(path, path.relative_to(root))
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "format", "validate"))
    command = parser.parse_args().command
    if command == "format":
        format_contracts()
        return
    if command == "build":
        output = build_bundle()
        print(f"Built {output.relative_to(ROOT)}")
        return
    paths = validate_contracts()
    print(f"Validated {len(paths)} contract documents")


if __name__ == "__main__":
    main()
