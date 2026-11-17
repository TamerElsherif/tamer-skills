#!/usr/bin/env python3
"""Validate a SCORM 1.2 package (zip or unpacked folder): manifest structure + every referenced file exists.

Usage: .venv/bin/python skills/tcs-render-lesson/scripts/scorm_check.py <package.zip | folder>
Exit code 0 = OK (warnings allowed), 1 = errors.
Checks: imsmanifest.xml at root, IMS CP 1.1.2 + ADL CP 1.2 namespaces, schemaversion 1.2, default organization,
unique/valid identifiers, item identifierref -> resource, SCO resources have href, every <file>/href/dependency
resolves, masteryscore 0-100, SCO pages load an API wrapper that calls LMSInitialize/LMSFinish, no absolute
or parent-escaping paths, unlisted files (warning).
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

CP = "http://www.imsproject.org/xsd/imscp_rootv1p1p2"
ADL = "http://www.adlnet.org/xsd/adlcp_rootv1p2"
NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


class Pkg:
    def __init__(self, path: Path):
        self.path = path
        if path.is_dir():
            self.names = {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()}
            self.read = lambda n: (path / n).read_bytes()
        else:
            z = zipfile.ZipFile(path)
            self.names = {n for n in z.namelist() if not n.endswith("/")}
            self.read = z.read


def norm(base: str, href: str) -> str | None:
    href = href.split("#")[0].split("?")[0]
    if not href or re.match(r"^[a-z]+:", href) or href.startswith("/"):
        return None
    parts = []
    for seg in PurePosixPath(base, href).parts:
        if seg == "..":
            if not parts:
                return "<escapes package>"
            parts.pop()
        elif seg != ".":
            parts.append(seg)
    return "/".join(parts)


def check(path: Path) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    pkg = Pkg(path)
    if "imsmanifest.xml" not in pkg.names:
        return [f"imsmanifest.xml missing at package root (found {len(pkg.names)} files)"], warns
    try:
        root = ET.fromstring(pkg.read("imsmanifest.xml"))
    except ET.ParseError as e:
        return [f"imsmanifest.xml is not well-formed XML: {e}"], warns
    q = lambda t: f"{{{CP}}}{t}"
    if root.tag != q("manifest"):
        errs.append(f"root element is {root.tag}, expected manifest in {CP}")
    if not root.get("identifier"):
        errs.append("manifest has no identifier")
    sv = root.find(f"{q('metadata')}/{q('schemaversion')}")
    sc = root.find(f"{q('metadata')}/{q('schema')}")
    if sv is None or (sv.text or "").strip() != "1.2":
        errs.append("metadata/schemaversion must be 1.2")
    if sc is None or (sc.text or "").strip() != "ADL SCORM":
        warns.append("metadata/schema should be 'ADL SCORM'")

    ids = {}
    for el in root.iter():
        i = el.get("identifier")
        if i is None:
            continue
        if not NCNAME.match(i):
            errs.append(f"identifier '{i}' is not a valid xs:ID")
        if i in ids:
            errs.append(f"duplicate identifier '{i}'")
        ids[i] = el

    orgs = root.find(q("organizations"))
    if orgs is None or not orgs.findall(q("organization")):
        errs.append("no organizations/organization")
    else:
        d = orgs.get("default")
        if d and d not in ids:
            errs.append(f"organizations/@default '{d}' does not match an organization")
        for org in orgs.findall(q("organization")):
            if org.find(q("title")) is None:
                errs.append(f"organization {org.get('identifier')} has no title")

    resources = {r.get("identifier"): r for r in root.iter(q("resource"))}
    referenced, listed, sco_count = set(), set(), 0
    for item in root.iter(q("item")):
        iid = item.get("identifier")
        if item.find(q("title")) is None:
            errs.append(f"item {iid} has no title")
        ref = item.get("identifierref")
        children = item.findall(q("item"))
        if not ref and not children:
            errs.append(f"item {iid} has neither identifierref nor child items")
        if ref:
            if ref not in resources:
                errs.append(f"item {iid}: identifierref '{ref}' has no resource")
            referenced.add(ref)
        ms = item.find(f"{{{ADL}}}masteryscore")
        if ms is not None:
            try:
                v = float(ms.text)
                if not 0 <= v <= 100:
                    raise ValueError
            except (TypeError, ValueError):
                errs.append(f"item {iid}: masteryscore '{ms.text}' not a number 0-100")

    for rid, r in resources.items():
        st = r.get(f"{{{ADL}}}scormtype") or r.get(f"{{{ADL}}}scormType")
        if st not in ("sco", "asset"):
            errs.append(f"resource {rid}: adlcp:scormtype must be sco|asset (got {st})")
        if r.get("type") != "webcontent":
            warns.append(f"resource {rid}: type should be 'webcontent'")
        base = r.get("{http://www.w3.org/XML/1998/namespace}base") or ""
        href = r.get("href")
        if st == "sco":
            sco_count += 1
            if not href:
                errs.append(f"SCO resource {rid} has no href")
            if rid not in referenced:
                warns.append(f"SCO resource {rid} is not used by any item")
        if href:
            n = norm(base, href)
            if n is None or n.startswith("<"):
                errs.append(f"resource {rid}: href '{href}' is absolute or escapes the package")
            elif n not in pkg.names:
                errs.append(f"resource {rid}: href '{href}' not found in package")
        for f in r.findall(q("file")):
            n = norm(base, f.get("href", ""))
            if n is None or n.startswith("<"):
                errs.append(f"resource {rid}: file '{f.get('href')}' is absolute or escapes the package")
            elif n not in pkg.names:
                errs.append(f"resource {rid}: file '{f.get('href')}' not found in package")
            else:
                listed.add(n)
        for dep in r.findall(q("dependency")):
            if dep.get("identifierref") not in resources:
                errs.append(f"resource {rid}: dependency '{dep.get('identifierref')}' has no resource")
        if st == "sco" and href and norm(base, href) in pkg.names and href.endswith((".html", ".htm")):
            page = pkg.read(norm(base, href)).decode("utf-8", "replace")
            scripts = re.findall(r'<script[^>]+src="([^"]+)"', page)
            js = ""
            for s in scripts:
                n = norm(str(PurePosixPath(norm(base, href)).parent), s)
                if n and n in pkg.names:
                    js += pkg.read(n).decode("utf-8", "replace")
                elif n:
                    errs.append(f"SCO {rid}: script '{s}' not found in package")
            js += page
            for fn in ("LMSInitialize", "LMSFinish", "LMSSetValue", "LMSCommit"):
                if fn not in js:
                    errs.append(f"SCO {rid}: no call to {fn} found in the page or its scripts")
            for s in re.findall(r'(?:src|href)="([^"]+)"', page):
                n = norm(str(PurePosixPath(norm(base, href)).parent), s)
                if n and not n.startswith("<") and n not in pkg.names:
                    errs.append(f"SCO {rid}: page references missing file '{s}'")
    if sco_count == 0:
        errs.append("package has no SCO resources")
    unlisted = sorted(pkg.names - listed - {"imsmanifest.xml"} - {n for n in pkg.names if n.endswith(".xsd")})
    if unlisted:
        warns.append(f"{len(unlisted)} file(s) not listed in any resource, e.g. {unlisted[:3]}")
    return errs, warns


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    p = Path(sys.argv[1])
    errs, warns = check(p)
    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    print(f"{'FAIL' if errs else 'OK'}: {p} — {len(errs)} error(s), {len(warns)} warning(s)")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
