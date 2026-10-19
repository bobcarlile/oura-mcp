"""The TypeScript build as npm runs it, not as the `.mcpb` runs it.

The `.mcpb` and every test start `node …/dist/main.js` by its own path. npm
does not: `npx -y @proscar87/oura-mcp` runs `node_modules/.bin/oura-mcp`, a
symlink whose name is the bin's, not the file's. The entry point compared the
file's name against `argv[1]`'s last segment to decide whether it was the main
module, so through the symlink it decided it was not, and exited 0 having done
nothing: no server, no `--check`, no error. Found by packing the tarball and
running it before the first npm publish.
"""

import json
import os
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).parent.parent
MAIN = ROOT / "ts" / "dist" / "main.js"

pytestmark = pytest.mark.skipif(
    not (shutil.which("node") and MAIN.exists()),
    reason="needs node and a compiled ts/dist (run `cd ts && npx tsc`)",
)


def test_the_entry_runs_through_the_bin_symlink(tmp_path):
    bin_ = tmp_path / "oura-mcp"
    bin_.symlink_to(MAIN)
    out = subprocess.run(["node", str(bin_), "--help"], capture_output=True,
                         text=True, timeout=30,
                         env={**os.environ, "OURA_SANDBOX": "1"})
    assert out.returncode == 0, out.stderr
    assert "oura-mcp --authorize" in out.stdout, \
        "through the symlink npm creates, the CLI did nothing and exited 0"


def test_the_npm_package_carries_the_icon():
    """`server.ts` embeds `../icon.png` from `dist/`. With `files: ["dist"]`
    alone, the npm package would leave it behind and every npm install would
    lose the icon without a word — the same failure
    `test_the_icon_ships_inside_the_installed_package` guards for PyPI."""
    pkg = json.loads((ROOT / "ts" / "package.json").read_text(encoding="utf-8"))
    assert "icon.png" in pkg["files"]
    assert (ROOT / "ts" / "icon.png").exists()
