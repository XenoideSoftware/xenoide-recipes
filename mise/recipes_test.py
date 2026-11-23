#!/usr/bin/env python3
"""Build every recipe's test_package for the requested configs.

Usage: python mise/recipes_test.py [--config gcc-release] [--config msvc-release]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEVKIT = Path(".devkit")
CONFIGS = {
    "gcc-release": ("gcc", "release"),
    "gcc-debug": ("gcc", "debug"),
    "clang-release": ("clang", "release"),
    "msvc-release": ("msvc", "release"),
}


def run(cmd, cwd=None):
    print("+ " + " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def profile_args(config):
    toolchain, flavor = CONFIGS[config]
    base = DEVKIT / "conan" / "profiles"
    return [
        "-pr:h", str(base / "toolchain" / toolchain),
        "-pr:h", str(base / "flavor" / flavor),
        "-pr:b", str(base / "toolchain" / toolchain),
        "-s:b", "build_type=Release",
    ]


def recipe_versions(recipe_dir):
    config = recipe_dir / "config.yml"
    if not config.is_file():
        return []
    versions = []
    for line in config.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith('"') and stripped.endswith(":"):
            versions.append(stripped.strip('":'))
    return versions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="append", default=None,
                        choices=sorted(CONFIGS))
    args = parser.parse_args()
    configs = args.config or ["gcc-release"]

    recipes = Path("recipes")
    if not DEVKIT.is_dir():
        raise SystemExit(".devkit/ is missing; run `mise run devkit:sync` first")
    result = subprocess.run(
        ["conan", "remote", "add", "xenoide-recipes", str(Path.cwd().resolve()),
         "--type=local-recipes-index", "--index", "0", "--force"])
    if result.returncode != 0:
        raise SystemExit("could not register the local recipes remote")
    failures = []
    for recipe_dir in sorted(p for p in recipes.iterdir() if p.is_dir()):
        versions = recipe_versions(recipe_dir)
        if not versions:
            continue
        # Recipes live in recipes/<name>/all; `conan create recipes/<name>`
        # has no conanfile and always failed.
        conanfile_dir = recipe_dir / "all"
        if not (conanfile_dir / "conanfile.py").is_file():
            print(f"warning: {recipe_dir.name} has no all/conanfile.py; skipping")
            continue
        for version in versions:
            for config in configs:
                print(f"==> {recipe_dir.name}/{version} [{config}]")
                result = subprocess.run(
                    ["conan", "create", str(conanfile_dir), "--version", version,
                     *profile_args(config), "--build=missing"])
                if result.returncode != 0:
                    failures.append(f"{recipe_dir.name}/{version} [{config}]")
    if failures:
        print("Failed recipes:")
        for failure in failures:
            print("  " + failure)
        return 1
    print("All recipe test_packages passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
