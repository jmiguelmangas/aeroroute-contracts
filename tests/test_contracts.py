import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.contracts import build_bundle, contract_files, validate_contracts


class ContractTests(unittest.TestCase):
    def test_appledouble_metadata_is_not_treated_as_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "openapi").mkdir()
            (root / "openapi" / "api.json").write_text(
                json.dumps({"openapi": "3.1.0"})
            )
            (root / "openapi" / "._api.json").write_bytes(b"\x00\x05\x16\x07")

            self.assertEqual(
                contract_files(root), [root / "openapi" / "api.json"]
            )

    def test_repository_contracts_are_valid(self) -> None:
        self.assertEqual(len(validate_contracts()), 11)

    def test_schema_marker_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "json-schema" / "invalid.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"type": "object"}))
            (root / "openapi").mkdir()

            with self.assertRaisesRegex(ValueError, "missing \\$schema"):
                validate_contracts(root)

    def test_bundle_contains_version_and_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "contracts.zip"
            build_bundle(output=output)

            with ZipFile(output) as archive:
                names = set(archive.namelist())
            self.assertIn("VERSION", names)
            self.assertIn("openapi/aeroroute-v1.json", names)


if __name__ == "__main__":
    unittest.main()
