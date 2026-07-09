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

    def test_icao_fpl_validation_schema_pins_non_operational_flags(self) -> None:
        schema_path = (
            Path(__file__).resolve().parent.parent
            / "json-schema"
            / "icao-fpl-validation"
            / "v1.json"
        )
        schema = json.loads(schema_path.read_text())

        properties = schema["properties"]
        self.assertIs(properties["filing_enabled"]["const"], False)
        self.assertIs(properties["operational_use_enabled"]["const"], False)

        required = schema["required"]
        self.assertIn("filing_enabled", required)
        self.assertIn("operational_use_enabled", required)

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
