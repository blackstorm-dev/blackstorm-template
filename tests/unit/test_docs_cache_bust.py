"""Regression checks for stale documentation assets and lightbox links."""

from hashlib import sha256
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
import unittest


HOOK = runpy.run_path(str(Path(__file__).resolve().parents[2] / "docs/hooks/cache_bust.py"))


class DocsCacheBustTests(unittest.TestCase):
    def test_changed_image_updates_both_links_and_keeps_other_assets_stable(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources").mkdir()
            page = root / "operators/secrets/index.html"
            page.parent.mkdir(parents=True)
            image = root / "resources/secrets.png"
            image.write_bytes(b"old image")
            (root / "resources/logo.svg").write_text("<svg/>")
            page.write_text(
                '<a href="../../resources/secrets.png"><img src="../../resources/secrets.png"></a>'
                '<img src="/resources/logo.svg">'
            )
            config = {"site_dir": directory, "site_url": "https://docs.example.com/"}
            HOOK["on_post_build"](config)
            first = page.read_text()
            old_hash = sha256(b"old image").hexdigest()[:16]
            self.assertEqual(first.count(f"secrets.png?v={old_hash}"), 2)
            HOOK["on_post_build"](config)
            self.assertEqual(first, page.read_text())
            image.write_bytes(b"new image")
            HOOK["on_post_build"](config)
            self.assertEqual(page.read_text(), first.replace(old_hash, sha256(b"new image").hexdigest()[:16]))

    def test_urls_and_markup_survive_versioning(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "photo name.svg").write_text("<svg/>")
            page = root / "index.html"
            untouched = '''<!doctype html>
<!-- <img src="photo%20name.svg"> -->
<script>const example = '<img src="photo%20name.svg">';</script>
<img src="https://example.com/photo.png"><img src="//example.com/photo.png">
<img src="data:image/png;base64,abc"><a href="#photo.png">anchor</a>
<img src="missing.png"><a href="guide.html">guide</a>
<img src="/outside/photo.png" title='example src="photo%20name.svg"'>
'''
            page.write_text(untouched + '<video poster="/manual/photo%20name.svg?size=large&amp;v=old#view"></video>')
            HOOK["on_post_build"]({"site_dir": directory, "site_url": "https://docs.example.com/manual/"})
            result = page.read_text()
            self.assertTrue(result.startswith(untouched))
            digest = sha256(b"<svg/>").hexdigest()[:16]
            self.assertIn(f'poster="/manual/photo%20name.svg?size=large&amp;v={digest}#view"', result)


if __name__ == "__main__":
    unittest.main()
