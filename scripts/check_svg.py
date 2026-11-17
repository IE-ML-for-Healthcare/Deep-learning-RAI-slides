#!/usr/bin/env python3
"""Inspect local SVG files without network access or file modification."""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


RASTER_PATTERN = re.compile(r"\.(?:apng|avif|bmp|gif|jpe?g|png|tiff?|webp)(?:[?#].*)?$", re.IGNORECASE)
REMOTE_PATTERN = re.compile(r"(?:https?:)?//", re.IGNORECASE)
FONT_PATTERN = re.compile(r"@font-face|font-family|font:\s*[^;]+|\.woff2?(?:[?#].*)?$|\.ttf(?:[?#].*)?$", re.IGNORECASE)


def local_name(value: str) -> str:
    """Return an XML local name without its namespace."""
    return value.rsplit("}", 1)[-1].lower()


def valid_viewbox(value: str | None) -> bool:
    """Accept four finite values with positive width and height."""
    if value is None:
        return False
    parts = re.split(r"[\s,]+", value.strip())
    if len(parts) != 4:
        return False
    try:
        numbers = [float(part) for part in parts]
    except ValueError:
        return False
    return all(math.isfinite(number) for number in numbers) and numbers[2] > 0 and numbers[3] > 0


def href_values(element: ET.Element) -> list[str]:
    """Return href and xlink:href values from an element."""
    return [value.strip() for key, value in element.attrib.items() if local_name(key) == "href" and value.strip()]


def inspect_svg(path: Path, allow_raster_wrapper: bool) -> tuple[list[str], list[str]]:
    """Return structural errors and review warnings for one SVG."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [f"XML parse failure: {exc}"], warnings

    if local_name(root.tag) != "svg":
        errors.append("root element is not <svg>")
    if not valid_viewbox(root.attrib.get("viewBox")):
        errors.append("missing or invalid viewBox")

    image_count = 0
    raster_wrapper = False
    for element in root.iter():
        tag = local_name(element.tag)
        if tag == "script":
            errors.append("contains <script> element")
        for key, value in element.attrib.items():
            attribute = local_name(key)
            text = value.strip()
            if attribute.startswith("on"):
                errors.append(f"contains executable event attribute '{attribute}'")
            if REMOTE_PATTERN.search(text):
                errors.append(f"contains external network reference '{text}'")
            if FONT_PATTERN.search(text):
                warnings.append(f"contains possible font dependency in '{attribute}'")

        content = (element.text or "").strip()
        if REMOTE_PATTERN.search(content):
            errors.append("contains external network reference in element content")
        if FONT_PATTERN.search(content):
            warnings.append("contains possible font dependency in element content")

        if tag != "image":
            continue
        image_count += 1
        values = href_values(element)
        if not values:
            warnings.append("contains <image> without an href")
            continue
        for href in values:
            lowered = href.lower()
            if lowered.startswith("data:image/"):
                raster_wrapper = True
                detail = "embedded base64 raster payload" if ";base64," in lowered else "embedded raster data URI"
                warnings.append(f"contains {detail}")
            elif RASTER_PATTERN.search(lowered):
                raster_wrapper = True
                warnings.append(f"contains linked raster image '{href}'")

    if image_count and not raster_wrapper:
        warnings.append("contains <image> element that requires manual inspection")
    if raster_wrapper and allow_raster_wrapper:
        warnings.append("raster-wrapper fallback explicitly accepted")
    return sorted(set(errors)), sorted(set(warnings))


def paths_from(arguments: list[str]) -> list[Path]:
    """Expand file and directory inputs into deterministic SVG paths."""
    paths: list[Path] = []
    for raw_path in arguments:
        path = Path(raw_path)
        if path.is_dir():
            paths.extend(sorted(item for item in path.rglob("*.svg") if item.is_file()))
        else:
            paths.append(path)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect local SVG integrity without modifying files")
    parser.add_argument("paths", nargs="+", help="SVG file or directory to inspect")
    parser.add_argument(
        "--allow-raster-wrapper",
        action="store_true",
        help="accept a reported raster-wrapper fallback after human review",
    )
    arguments = parser.parse_args()
    paths = paths_from(arguments.paths)
    if not paths:
        print("ERROR: no SVG files found", file=sys.stderr)
        return 1

    status = 0
    for path in paths:
        print(f"\n{path}")
        if not path.is_file():
            print("ERROR: file does not exist or is not readable")
            status = 1
            continue
        errors, warnings = inspect_svg(path, arguments.allow_raster_wrapper)
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARNING: {message}")
        accepted_raster_messages = {
            "contains embedded base64 raster payload",
            "contains embedded raster data URI",
            "raster-wrapper fallback explicitly accepted",
        }
        unresolved_warnings = warnings
        if arguments.allow_raster_wrapper:
            unresolved_warnings = [message for message in warnings if message not in accepted_raster_messages and not message.startswith("contains linked raster image")]
        if errors:
            status = 1
        elif unresolved_warnings:
            status = max(status, 2)
        else:
            print("PASS: SVG structure accepted")

    if status == 2:
        print("\nREVIEW REQUIRED: inspect warnings or rerun with --allow-raster-wrapper after accepting the fallback")
    return status


if __name__ == "__main__":
    sys.exit(main())
