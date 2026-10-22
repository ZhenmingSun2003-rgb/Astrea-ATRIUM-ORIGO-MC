#!/usr/bin/env python3
"""Build ORIGO .mrpack manifests. Third-party binary assets are NOT embedded."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = ROOT / "clients"
DIST_DIR = ROOT / "dist"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX128 = re.compile(r"^[0-9a-f]{128}$")
SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class BuildError(RuntimeError):
    pass


def fetch_json(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Astrea-ORIGO-ModpackBuilder/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=25) as resp:
            return json.load(resp)
    except (urllib.error.URLError, ValueError, TimeoutError) as err:
        raise BuildError(f"Unable to fetch {url}: {err}") from err


def fetch_component(component):
    project = component["project"]
    version_id = component.get("version_id")
    version_number = component.get("version_number")
    if version_id and version_number:
        raise BuildError(f"{project}: both version_id and version_number")
    if version_id:
        if not SAFE_ID.fullmatch(version_id):
            raise BuildError(f"{project}: invalid version ID")
        url = "https://api.modrinth.com/v2/version/" + version_id
    elif version_number:
        if not SAFE_ID.fullmatch(version_number) or not SAFE_ID.fullmatch(project):
            raise BuildError(f"{project}: unsafe version number or project")
        url = f"https://api.modrinth.com/v2/project/{project}/version/{version_number}"
    else:
        raise BuildError(f"{project}: no pinned upstream version")
    return fetch_json(url)


def read_profile(profile_id, directory=PROFILES_DIR):
    if profile_id not in ("ethereal", "arcane", "origin"):
        raise BuildError("Unknown client profile: " + str(profile_id))
    with (directory / (profile_id + ".json")).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if data["id"] != profile_id or data["minecraft"] != "26.2":
        raise BuildError(f"{profile_id}: incorrect identity/game version")
    if data["fabric_loader"] != "0.19.5":
        raise BuildError(f"{profile_id}: unexpected Fabric Loader version")
    return data


def make_file(component, version, game_version):
    project = component["project"]
    if component.get("version_id") and version.get("id") != component["version_id"]:
        raise BuildError(f"{project}: mismatched version id")
    if component.get("version_number") and version.get("version_number") != component["version_number"]:
        raise BuildError(f"{project}: mismatched version number")
    if game_version not in version.get("game_versions", []):
        raise BuildError(f"{project}: not published for {game_version}")
    if version.get("version_type") != "release":
        raise BuildError(f"{project}: not a stable release")
    kind = component["type"]
    folder = {"mod": "mods", "resourcepack": "resourcepacks",
              "shaderpack": "shaderpacks"}.get(kind)
    if not folder:
        raise BuildError(f"Unknown component type: {kind}")
    if kind == "mod" and "fabric" not in version.get("loaders", []):
        raise BuildError(f"{project}: not a Fabric mod")
    if kind == "shaderpack" and "iris" not in version.get("loaders", []):
        raise BuildError(f"{project}: not an Iris shaderpack")
    options = version.get("files", [])
    primary = next((file for file in options if file.get("primary")), None)
    if primary is None and len(options) == 1:
        primary = options[0]
    if primary is None:
        raise BuildError(f"{project}: unable to uniquely resolve file")
    filename = primary.get("filename", "")
    if not filename or filename in (".", "..") or "/" in filename or "\\" in filename:
        raise BuildError(f"{project}: unsafe filename {filename!r}")
    extension = ".jar" if kind == "mod" else ".zip"
    if not filename.lower().endswith(extension):
        raise BuildError(f"{project}: expected {extension}")
    hashes = primary.get("hashes", {})
    if not HEX40.fullmatch(hashes.get("sha1", "")) or not HEX128.fullmatch(hashes.get("sha512", "")):
        raise BuildError(f"{project}: invalid sha1/sha512")
    url = primary.get("url", "")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "cdn.modrinth.com":
        raise BuildError(f"{project}: unexpected download host")
    size = primary.get("size")
    if type(size) is not int or size <= 0:
        raise BuildError(f"{project}: missing file size")
    return {
        "path": folder + "/" + filename,
        "hashes": {"sha1": hashes["sha1"], "sha512": hashes["sha512"]},
        "env": {"client": "required", "server": "unsupported"},
        "downloads": [url],
        "fileSize": size
    }


def build_index(profile, resolver=fetch_component):
    files = []
    destinations = set()
    for component in profile["components"]:
        if not component.get("version_id") and not component.get("version_number"):
            raise BuildError(f"{component['name']}: version is not locked")
        entry = make_file(component, resolver(component), profile["minecraft"])
        if entry["path"] in destinations:
            raise BuildError(f"Duplicate file path: {entry['path']}")
        destinations.add(entry["path"])
        files.append(entry)
    return {
        "formatVersion": 1, "game": "minecraft", "versionId": profile["pack_version"],
        "name": profile["name"], "summary": profile["notes"], "files": files,
        "dependencies": {
            "minecraft": profile["minecraft"], "fabric-loader": profile["fabric_loader"]
        }
    }


def build_pack(profile, directory=DIST_DIR, resolver=fetch_component):
    index = build_index(profile, resolver)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / f"ORIGO-{profile['id'].capitalize()}-{profile['pack_version']}.mrpack"
    instructions = [
        "ORIGO Client / " + profile["name"],
        "请在 Minecraft 游戏内手动启用对应的资源包与 Iris 光影。",
        "本整合包只保存官方 Modrinth 下载链接及哈希值，不重新打包第三方文件。"
    ]
    shader = profile.get("manual_shader")
    if shader:
        instructions.extend([
            f"必需手动安装的光影：{shader['name']} {shader['version']}",
            "官方入口：" + shader["url"],
            "请自行下载 ZIP，将 ZIP 不解压放入 shaderpacks/，然后在 Iris 中启用。",
            "该光影未包含在 .mrpack 内。"
        ])
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("modrinth.index.json", json.dumps(index, indent=2, ensure_ascii=False) + "\n")
        archive.writestr("overrides/ORIGO-安装说明.txt", "\n".join(instructions) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser(description="Build ORIGO client .mrpack files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--profile", choices=("ethereal", "arcane", "origin"))
    args = parser.parse_args()
    targets = ("ethereal", "arcane", "origin") if args.all else (args.profile,)
    try:
        for target in targets:
            print("Built:", build_pack(read_profile(target)))
    except (BuildError, OSError, KeyError, ValueError) as err:
        print("Build failed:", err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
