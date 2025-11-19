#!/usr/bin/env python

"""
Generate SVG previews. Update README.
"""

from functools import partial
from glob import glob
import ast
import os
import re
import hashlib

repo_url = "https://github.com/quark-zju/homecad"


def example_table():
    yield table(
        thead(
            tr(
                # th("File"),
                th("Description"),
                th("Rendered Preview"),
            )
        ),
        tbody(map(example_row, sorted(glob("src/*.py")))),
    )


def example_row(path):
    docstring = parse_docstring(path)
    if not docstring:
        return
    img_md, size_md = preview_md(path)
    return tr(
        # td(name_md(path)),
        td(description_md(docstring), size_md),
        td(img_md),
    )


def name_md(path):
    url = f"{repo_url}/blob/master/{path}"
    md = f"[{os.path.basename(path)}]({url})"
    return markdown(md)


def description_md(docstring):
    lines = docstring.strip().splitlines(True)
    first_line = lines[0].strip()
    rest = "".join(lines[1:]).strip()
    # Assume first_line is not markdown
    return details(summary(first_line), markdown(rest))


# See https://cadquery.readthedocs.io/en/latest/importexport.html#exporting-svg
SVG_OPTS = {
    "width": 800,
    "height": 600,
    "showAxes": False,
    "projectionDir": (0.4, 0.5, -0.3),
}
SVG_OPTS_BYTES = repr(SVG_OPTS).encode()


def preview_md(src_path):
    img_path = src_path.replace("src/", "img/").replace(".py", ".svg")
    img_data = try_read(img_path)
    expected_hash = hash_path(src_path, SVG_OPTS_BYTES)
    got_hashes = re.findall("HASH=([^;]+)", img_data)
    size_strs = re.findall("SIZE=([^;]+)", img_data)
    if expected_hash in got_hashes and size_strs:
        # Image is up-to-date and size is known.
        size_str = size_strs[0]
    else:
        size_str = generate_preview_svg(src_path, img_path)
        if not size_str:
            # No image generated.
            return None
        with open(img_path, "a", newline="\n") as f:
            f.write(f"\n<!-- SRC_HASH={expected_hash}; -->\n")
            f.write(f"\n<!-- SIZE={size_str}; -->\n")
    img_url = f"{repo_url}/raw/master/{img_path}"
    src_url = f"{repo_url}/blob/master/{src_path}"
    img_md = f"![]({img_url})"
    size_md = f"[{size_str}]({src_url})"
    return markdown(img_md), markdown(size_md)


def generate_preview_svg(src_path, img_path):
    from cadquery import exporters

    real_export = exporters.export
    old_pwd = os.getcwd()

    # Replace export to figure out what to export.
    objects = []

    def captured_object(obj, *args, **kwargs):
        objects.append(obj)

    exporters.export = captured_object

    try:
        mod = type(os)("obj")
        src_full_path = os.path.realpath(src_path)
        mod.__file__ = src_full_path
        mod.show_object = captured_object
        code = compile(try_read(src_full_path), src_path, "exec")
        os.chdir(os.path.dirname(src_full_path))
        eval(code, mod.__dict__, mod.__dict__)
    finally:
        exporters.export = real_export
        os.chdir(old_pwd)

    if not objects:
        return None

    obj = objects[-1]
    print(f"Generating SVG for {src_path}...")
    preview_obj = getattr(mod, "preview_obj", None)
    if preview_obj:
        obj = preview_obj(obj)
    bbox = obj.val().BoundingBox()
    obj = obj.translate(-bbox.center)
    exporters.export(
        obj,
        img_path,
        exporters.ExportTypes.SVG,
        opt={**SVG_OPTS, **getattr(mod, "SVG_OPTS", {})},
    )
    sizes = [bbox.xmax - bbox.xmin, bbox.ymax - bbox.ymin, bbox.zmax - bbox.zmin]
    size_str = " x ".join("%.1f" % s for s in sizes) + " mm"
    return size_str


def hash_path(path, extra=b""):
    with open(path, "rb") as f:
        return hashlib.blake2s(f.read() + extra).hexdigest()


def try_read(path):
    try:
        with open(path, newline="\n") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def html_tag(name, *args):
    yield f"<{name}>"
    yield args
    yield f"</{name}>"


def markdown(*args):
    yield ""
    yield args
    yield ""


table = partial(html_tag, "table")
thead = partial(html_tag, "thead")
tbody = partial(html_tag, "tbody")
tr = partial(html_tag, "tr")
td = partial(html_tag, "td")
th = partial(html_tag, "th")
details = partial(html_tag, "details")
summary = partial(html_tag, "summary")


def render(obj, w):
    if isinstance(obj, str):
        w(obj + "\n")
    elif obj is None:
        pass
    elif callable(obj):
        render(obj(), w=w)
    else:
        for subobj in iter(obj):
            render(subobj, w=w)


def render_to_string(obj):
    out = []
    render(obj, out.append)
    return "".join(out)


def parse_docstring(path):
    with open(path) as f:
        source = f.read()
    tree = ast.parse(source, path)
    return ast.get_docstring(tree)


def main():
    readme = try_read("README.md")
    splitter = "\n<!-- generated-examples -->\n"
    parts = readme.split(splitter)
    example_table_html = render_to_string(example_table)
    parts[1] = example_table_html
    new_readme = splitter.join(parts)
    if new_readme != readme:
        print("Updating README")
        with open("README.md", "w", newline="\n") as f:
            f.write(new_readme)
    else:
        print("README is up-to-date")


if __name__ == "__main__":
    main()
