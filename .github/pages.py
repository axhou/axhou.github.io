#!/usr/bin/env python3
"""Build the static site, preserve old URLs, and check local HTML links."""

import argparse
import html
import json
import shutil
import tempfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://axhou.github.io"
PUBLIC = {
    ".html", ".css", ".js", ".json", ".txt", ".xml", ".pdf", ".ico",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif",
    ".woff", ".woff2", ".ttf", ".otf", ".webmanifest", ".mp4",
    ".webm", ".mp3", ".ogg", ".wav",
}
EXCLUDED = {"dist", "test", "tests", "output", "outputs", "node_modules", "__pycache__"}
STAMP = ".pages-build"


def safe_path(value):
    """A mapping path must be a plain, relative URL path."""
    if not isinstance(value, str) or not value or value.startswith("/"):
        raise ValueError(f"Invalid mapping path: {value!r}")
    if any(c in value for c in "\\?#%:<>\"'") or any(c.isspace() for c in value) or any(
        part in ("", ".", "..") for part in value.rstrip("/").split("/")
    ):
        raise ValueError(f"Unsafe mapping path: {value!r}")
    return PurePosixPath(value)


def output_file(directory, path):
    result = directory / path
    if result.is_dir() or str(path).endswith("/"):
        result /= "index.html"
    return result


def copy_public(directory, output):
    count = 0
    build_dirs = {output, *(marker.parent for marker in ROOT.rglob(STAMP))}
    for source in sorted(ROOT.rglob("*")):
        relative = source.relative_to(ROOT)
        if any(source == build or build in source.parents for build in build_dirs):
            continue
        if any(part in EXCLUDED or part.startswith(".") for part in relative.parts):
            if relative.as_posix() != ".nojekyll":
                continue
        if not source.is_file() or source.name.lower().startswith("readme"):
            continue
        if source.suffix.lower() not in PUBLIC and relative.as_posix() != ".nojekyll":
            continue
        if source.is_symlink():
            raise ValueError(f"Public files must not be symlinks: {relative}")
        destination = directory / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        count += 1
    (directory / ".nojekyll").touch()
    if not (directory / "index.html").is_file():
        raise ValueError("The site needs a root index.html")
    return count


def redirects(directory):
    directory = directory.resolve()
    mapping = json.loads((ROOT / ".github" / "links.json").read_text())
    if not isinstance(mapping, dict):
        raise ValueError("links.json must be an object mapping old paths to canonical paths")
    aliases = {}
    occupied = {p.relative_to(directory).as_posix().casefold() for p in directory.rglob("*")}
    plans = []
    for old, new in mapping.items():
        safe_path(old)
        safe_path(new)
        destination = directory / old
        if old.endswith("/"):
            destination /= "index.html"
        target = output_file(directory, new)
        if not target.is_file():
            raise ValueError(f"Alias {old}: canonical target does not exist: {new}")
        key = destination.relative_to(directory).as_posix().casefold()
        if key in occupied or any(p.is_file() for p in destination.parents):
            raise ValueError(f"Alias collides with another path: {old}")
        occupied.add(key)
        plans.append((old, new, destination, target))
    # Resolve all targets before writing any aliases, so aliases cannot be chained.
    for old, new, destination, target in plans:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if old.endswith("/") or destination.suffix.lower() in (".html", ".htm", ""):
            if target.suffix.lower() != ".html":
                raise ValueError(f"HTML alias {old} must point to an HTML page")
            url = "/" + new
            if (directory / new).is_dir() and not url.endswith("/"):
                url += "/"
            escaped = html.escape(url, quote=True)
            destination.write_text(
                '<!doctype html>\n<html lang="en">\n<head>\n'
                '<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                '<title>Page moved</title>\n'
                f'<link rel="canonical" href="{ORIGIN}{escaped}">\n'
                f'<meta http-equiv="refresh" content="0; url={escaped}">\n'
                '<script>location.replace('
                + json.dumps(url)
                + ' + location.search + location.hash);</script>\n'
                '</head>\n<body>\n'
                f'<p>This page has moved. <a href="{escaped}">Continue to the page</a>.</p>\n'
                '</body>\n</html>\n', encoding="utf-8"
            )
        else:
            shutil.copyfile(target, destination)
        aliases[destination] = target
    return aliases


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.feed(source.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id" or (tag == "a" and key == "name"):
                self.ids.add(value)
            if key in ("href", "src"):
                self.links.append((self.getpos()[0], value, tag, key))


def validate(directory, aliases):
    directory = directory.resolve()
    pages = {p: Page(p) for p in directory.rglob("*.html")}
    errors = []
    checked = 0
    blank_speakers = 0
    for source, page in pages.items():
        for line, value, tag, attribute in page.links:
            label = f"{source.relative_to(directory)}:{line}"
            if value is None or not value.strip():
                # Everytopic is preserved unchanged, including existing blank speaker links.
                if source.relative_to(directory).as_posix() == "everytopic.html" and (
                    tag == "a" and attribute == "href" and value == ""
                ):
                    blank_speakers += 1
                    continue
                errors.append(f"{label}: empty link")
                continue
            if tag == "base":
                errors.append(f"{label}: base URLs are not supported by this static link checker")
                continue
            try:
                url = urlsplit(value)
            except ValueError as error:
                errors.append(f"{label}: invalid URL {value!r}: {error}")
                continue
            if url.scheme or url.netloc:
                if url.hostname != "axhou.github.io" or url.scheme not in ("", "http", "https"):
                    continue
            path = unquote(url.path)
            if "\\" in path:
                errors.append(f"{label}: invalid backslash in local URL {value!r}")
                continue
            if not path:
                target = directory if url.netloc else source
            elif path.startswith("/") or url.netloc:
                target = directory / path.lstrip("/")
            else:
                target = source.parent / path
            target = target.resolve()
            if not target.is_relative_to(directory):
                errors.append(f"{label}: URL escapes the site: {value}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                errors.append(f"{label}: missing local target: {value}")
                continue
            target = aliases.get(target, target)
            fragment = unquote(url.fragment)
            if fragment and target.suffix.lower() == ".html" and fragment not in pages[target].ids:
                errors.append(f"{label}: missing anchor #{fragment} in {target.relative_to(directory)}")
            checked += 1
    if errors:
        raise ValueError("Local link validation failed:\n  " + "\n  ".join(errors))
    if blank_speakers:
        print(f"Note: preserved {blank_speakers} existing blank speaker links in everytopic.html")
    return len(pages), checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    requested_output = parser.parse_args().output
    output = requested_output.resolve()
    if output == ROOT or output in ROOT.parents or requested_output.is_symlink():
        raise ValueError("Output must be a separate build directory")
    if output.exists() and (not output.is_dir() or not (output / STAMP).is_file()):
        raise ValueError(f"Refusing to replace a directory not created by this builder: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".pages-", dir=output.parent) as temp:
        staging = Path(temp).resolve() / "site"
        staging.mkdir()
        count = copy_public(staging, output)
        aliases = redirects(staging)
        pages, links = validate(staging, aliases)
        (staging / STAMP).write_text("Generated by .github/pages.py\n")
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(staging), output)
    print(f"Built {count} public files and {len(aliases)} legacy URLs in {output}")
    print(f"Checked {links} local links across {pages} HTML pages")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
