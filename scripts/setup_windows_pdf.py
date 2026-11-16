"""Install pinned MSYS2 PDF libraries inside ignored .tools, without admin rights."""

import hashlib
import json
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / ".tools" / "windows-pdf"


def install(package: dict[str, str]) -> str:
    name = package["filename"]
    if PurePosixPath(name).name != name:
        raise ValueError("Invalid package filename")
    archive = DESTINATION / "downloads" / name
    if not archive.exists():
        url = "https://repo.msys2.org/mingw/mingw64/" + name
        with urllib.request.urlopen(url, timeout=60) as response:
            archive.write_bytes(response.read())
    if hashlib.sha256(archive.read_bytes()).hexdigest() != package["sha256"]:
        raise ValueError(f"Checksum mismatch for {name}; remove the failed download.")
    members = subprocess.check_output(["tar", "-tf", str(archive)], text=True)
    for member in members.splitlines():
        path = PurePosixPath(member)
        if path.is_absolute() or ".." in path.parts or "\\" in member:
            raise ValueError("Unsafe archive member")
    # Only DLLs and font configuration are used, without installing native apps.
    wanted = [
        m
        for m in members.splitlines()
        if (m.startswith("mingw64/bin/") and m.endswith(".dll"))
        or m.startswith("mingw64/etc/fonts/")
    ]
    if wanted:
        subprocess.run(
            ["tar", "-xf", str(archive), "-C", str(DESTINATION), *wanted], check=True
        )
    return package["name"]


def main() -> None:
    (DESTINATION / "downloads").mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "config/windows_pdf_packages.json").read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name in pool.map(install, manifest["packages"]):
            print(f"Verified {name}")
    print("PDF DLL directory: .tools/windows-pdf/mingw64/bin")
    print("Use WEASYPRINT_DLL_DIRECTORIES with that absolute directory.")


if __name__ == "__main__":
    main()
