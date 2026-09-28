"""Version local media and stylesheet/script URLs in the finished site HTML."""

from hashlib import sha256
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit


ASSET_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico",
    ".css", ".js", ".mp4", ".webm",
}
URL_ATTRIBUTES = {"src", "href", "poster", "data-src", "data-video"}
# Consume every attribute, including quoted text, so examples inside alt/title
# attributes cannot be mistaken for actual URLs.
ATTRIBUTE = re.compile(r'''(\s+)([^\s=/>]+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?''')


class AssetURLs(HTMLParser):
    def __init__(self, html, page, root, prefix, digests):
        super().__init__(convert_charrefs=False)
        self.html, self.page, self.root = html, page, root
        self.prefix, self.digests = prefix, digests
        self.offsets = [0]
        for line in html.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.edits = []

    def version(self, value):
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path:
            return value
        path = unquote(url.path)
        if Path(path).suffix.lower() not in ASSET_SUFFIXES:
            return value
        if path.startswith("/"):
            if not path.startswith(self.prefix):
                return value
            asset = self.root / path[len(self.prefix):]
        else:
            asset = self.page.parent / path
        asset = asset.resolve()
        if not asset.is_relative_to(self.root) or not asset.is_file():
            return value
        if asset not in self.digests:
            digest = sha256()
            with asset.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            self.digests[asset] = digest.hexdigest()[:16]
        query = [(key, val) for key, val in parse_qsl(url.query, keep_blank_values=True) if key != "v"]
        query.append(("v", self.digests[asset]))
        return urlunsplit(url._replace(query=urlencode(query)))

    def handle_starttag(self, tag, attrs):
        original = self.get_starttag_text()

        def replace(match):
            space, name, raw = match.groups()
            if name.lower() not in URL_ATTRIBUTES or raw is None:
                return match.group()
            value = unescape(raw[1:-1] if raw.startswith(('"', "'")) else raw)
            versioned = self.version(value)
            if versioned == value:
                return match.group()
            return f'{space}{name}="{escape(versioned, quote=True)}"'

        updated = ATTRIBUTE.sub(replace, original)
        if updated != original:
            line, column = self.getpos()
            start = self.offsets[line - 1] + column
            self.edits.append((start, start + len(original), updated))

    handle_startendtag = handle_starttag

    def rewrite(self):
        self.feed(self.html)
        self.close()
        result = self.html
        for start, end, updated in reversed(self.edits):
            result = result[:start] + updated + result[end:]
        return result


def on_post_build(config, **kwargs):
    # Run on final HTML so glightbox's href and the image's src get the same hash.
    # A fresh digest cache on every build also handles edits during mkdocs serve.
    root = Path(config["site_dir"]).resolve()
    prefix = urlsplit(config.get("site_url") or "/").path.rstrip("/") + "/"
    digests = {}
    for page in root.rglob("*.html"):
        original = page.read_text(encoding="utf-8")
        updated = AssetURLs(original, page, root, prefix, digests).rewrite()
        if updated != original:
            page.write_text(updated, encoding="utf-8")
