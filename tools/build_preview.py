"""Bundle the local preview so it works without sibling files or network access."""
import base64
import mimetypes
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from static_preview import render_static

ROOT = Path(__file__).resolve().parents[1]


def data_url(relative):
    path = ROOT / relative
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


class Bundler(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.scripts = []

    def handle_decl(self, decl):
        self.output.append(f"<!{decl}>")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.scripts.append((ROOT / attrs["src"]).read_text())
            return
        if tag == "link" and attrs.get("rel") == "stylesheet":
            css = (ROOT / attrs["href"]).read_text()
            css = "\n".join(line for line in css.splitlines() if not line.startswith("@import "))
            self.output.append(f"<style>{css}</style>")
            return
        if tag == "img":
            attrs["src"] = data_url(attrs["src"])
        if tag == "link" and attrs.get("rel") == "icon":
            attrs["href"] = data_url(attrs["href"])
        if tag == "a" and "download" in attrs:
            attrs["href"] = data_url(attrs["href"])
            attrs["download"] = "README.md"
        attributes = "".join(f' {key}' if value is None else f' {key}="{escape(value, quote=True)}"' for key, value in attrs.items())
        self.output.append(f"<{tag}{attributes}>")

    def handle_endtag(self, tag):
        if tag == "script":
            return
        if tag == "body":
            for script in self.scripts:
                self.output.append("<script>" + script.replace("</", "<\\/") + "</script>")
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")


def build_preview(production=False):
    bundler = Bundler()
    bundler.feed(render_static((ROOT / "index.html").read_text(), ROOT))
    rendered = "".join(bundler.output)
    if production:
        rendered = rendered.replace('LOCAL PREVIEW', 'PUBLIC PROFILE').replace('>GITHUB README</button>', '>README</button>')
    (ROOT / "preview.html").write_text(rendered)
    (ROOT / "preview-v2.html").write_text(rendered)
    print("Built preview.html: embedded styles, scripts, data, images and README download.")


if __name__ == "__main__":
    build_preview()
