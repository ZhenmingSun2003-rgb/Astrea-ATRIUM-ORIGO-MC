"""Offline .mrpack tests (no Modrinth API requests)."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("origo_builder", ROOT / "scripts/build_clients.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def fake_resolve(component):
    key = component.get("version_id") or component.get("version_number")
    kind = component["type"]
    extension = ".jar" if kind == "mod" else ".zip"
    loader = "fabric" if kind == "mod" else ("iris" if kind == "shaderpack" else "minecraft")
    return {
        "id": component.get("version_id"), "version_number": component.get("version_number"),
        "version_type": "release", "game_versions": ["26.2"], "loaders": [loader],
        "files": [{
            "primary": True, "filename": str(key) + extension, "size": 12345,
            "url": "https://cdn.modrinth.com/data/fake/" + str(key) + extension,
            "hashes": {"sha1": "a" * 40, "sha512": "b" * 128}
        }]
    }


class ClientTests(unittest.TestCase):
    def test_three_profiles_are_locked(self):
        for name in ("ethereal", "arcane", "origin"):
            profile = builder.read_profile(name)
            index = builder.build_index(profile, fake_resolve)
            self.assertEqual(index["formatVersion"], 1)
            self.assertEqual(index["dependencies"]["minecraft"], "26.2")
            self.assertEqual(index["dependencies"]["fabric-loader"], "0.19.5")
            self.assertTrue(any(file["path"].startswith("resourcepacks/") for file in index["files"]))
            self.assertTrue(any(file["path"].startswith("mods/") for file in index["files"]))

    def test_origin_has_manual_shader_instruction(self):
        profile = builder.read_profile("origin")
        self.assertEqual(profile["manual_shader"]["version"], "3.2.0")
        with tempfile.TemporaryDirectory() as folder:
            output = builder.build_pack(profile, Path(folder), fake_resolve)
            with zipfile.ZipFile(output) as z:
                manifest = json.loads(z.read("modrinth.index.json"))
                self.assertFalse(any(f["path"].startswith("shaderpacks/") for f in manifest["files"]))
                self.assertIn("iterationT", z.read("overrides/ORIGO-安装说明.txt").decode("utf-8"))

    def test_rejects_version_mismatch(self):
        component = builder.read_profile("ethereal")["components"][0]
        wrong = fake_resolve(component)
        wrong["game_versions"] = ["26.3"]
        with self.assertRaises(builder.BuildError):
            builder.make_file(component, wrong, "26.2")

    def test_rejects_unsafe_filename(self):
        component = builder.read_profile("ethereal")["components"][0]
        wrong = fake_resolve(component)
        wrong["files"][0]["filename"] = "../evil.jar"
        with self.assertRaises(builder.BuildError):
            builder.make_file(component, wrong, "26.2")


if __name__ == "__main__":
    unittest.main()
