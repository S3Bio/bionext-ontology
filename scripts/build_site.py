"""Build the static site that resolves BioNExt term IRIs.

For every term in https://w3id.org/bionext/ontology/ it writes
  site/ontology/<Term>.html  human-readable page
  site/ontology/<Term>.ttl   the term's own triples (for content negotiation)
plus an index page and copies of the full ontology and release files.

Usage: python scripts/build_site.py [ontology.ttl] [out_dir]
"""

import html
import shutil
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS

BN = Namespace("https://w3id.org/bionext/ontology/")
ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "ontology" / "bne_ontology.ttl"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "site"

KINDS = [
    (OWL.Class, "Classes"),
    (OWL.ObjectProperty, "Object properties"),
    (OWL.DatatypeProperty, "Datatype properties"),
    (OWL.AnnotationProperty, "Annotation properties"),
    (OWL.NamedIndividual, "Individuals"),
]
SINGULAR = {"Classes": "Class", "Object properties": "Object property", "Datatype properties": "Datatype property",
            "Annotation properties": "Annotation property", "Individuals": "Individual"}
# Shown in the "Details" table, in this order; anything else goes under "Other".
FIELDS = [
    (RDFS.subClassOf, "Subclass of"),
    (RDFS.subPropertyOf, "Subproperty of"),
    (RDF.type, "Type"),
    (RDFS.domain, "Domain"),
    (RDFS.range, "Range"),
    (OWL.inverseOf, "Inverse of"),
    (OWL.equivalentClass, "Equivalent class"),
    (SKOS.altLabel, "Synonym"),
    (RDFS.seeAlso, "See also"),
]
SKIP = {RDFS.label, RDFS.comment, SKOS.definition, SKOS.prefLabel}

CSS = """
:root{--bg:#fff;--fg:#1d1f23;--muted:#5d6470;--line:#e3e6eb;--accent:#0b6bcb;--chip:#f2f4f7}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--fg:#e8eaed;--muted:#9aa1ab;--line:#2c3036;--accent:#6cb2ff;--chip:#22262b}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:32px 16px 64px}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header.top{font-size:14px;color:var(--muted);margin-bottom:24px}h1{margin:.1em 0 .2em;font-size:30px;line-height:1.2}
.iri{font:13px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--muted);word-break:break-all}
.kind{display:inline-block;font-size:12px;padding:2px 8px;border-radius:99px;background:var(--chip);color:var(--muted);margin-right:6px}
.def{font-size:17px;margin:18px 0 24px}table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;padding:8px 0;border-top:1px solid var(--line)}
th{width:170px;font-weight:600;color:var(--muted);font-size:14px;padding-right:12px}td div{margin-bottom:2px;word-break:break-word}
h2{font-size:18px;margin:32px 0 8px}ul.terms{columns:2 260px;padding-left:18px;margin:0}ul.terms li{break-inside:avoid}
.dl a{margin-right:14px}footer{margin-top:40px;font-size:13px;color:var(--muted)}input{width:100%;padding:8px 10px;font:inherit;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
"""


def local(iri):
    return str(iri)[len(BN):] if str(iri).startswith(str(BN)) else None


def curie(g, node):
    try:
        prefix, _, name = g.compute_qname(node)
        return f"{prefix}:{name}"
    except Exception:
        return str(node)


def render_node(g, node, depth):
    up = "../" * depth
    if isinstance(node, Literal):
        lang = f' <span class="kind">{node.language}</span>' if node.language else ""
        return html.escape(str(node)) + lang
    if isinstance(node, URIRef):
        name = local(node)
        if name:
            label = g.value(node, RDFS.label)
            text = html.escape(str(label) if label else name)
            return f'<a href="{up}ontology/{html.escape(name)}">{text}</a> <span class="iri">bn:{html.escape(name)}</span>'
        return f'<a href="{html.escape(str(node))}">{html.escape(curie(g, node))}</a>'
    return '<span class="iri">(anonymous expression)</span>'


def page(title, body, depth, description=""):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(description)}">
<style>{CSS}</style></head><body><main>
<header class="top"><a href="{up}">BioNExt Ontology</a></header>
{body}
<footer>BioNExt Ontology · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/S3Bio/bionext-ontology">source</a></footer>
</main></body></html>
"""


def term_kinds(g, s):
    return [label for k, label in KINDS if (s, RDF.type, k) in g]


def build_term(g, s, usages):
    name = local(s)
    label = g.value(s, RDFS.label) or name
    definition = g.value(s, SKOS.definition) or g.value(s, RDFS.comment)
    kinds = "".join(f'<span class="kind">{SINGULAR[k]}</span>' for k in term_kinds(g, s))

    rows = []
    seen = set(SKIP)
    for p, title in FIELDS:
        seen.add(p)
        vals = [o for o in g.objects(s, p) if not (p == RDF.type and o in {k for k, _ in KINDS})]
        if vals:
            rows.append((title, vals))
    other = defaultdict(list)
    for p, o in g.predicate_objects(s):
        if p not in seen:
            other[p].append(o)
    for p, vals in sorted(other.items(), key=lambda kv: curie(g, kv[0])):
        rows.append((render_node(g, p, 1), vals))
    subs = sorted(set(g.subjects(RDFS.subClassOf, s)), key=str)
    if subs:
        rows.append(("Subclasses", subs))
    if usages:
        rows.append(("Used by", sorted(usages, key=str)))

    table = "".join(
        f"<tr><th>{t}</th><td>{''.join(f'<div>{render_node(g, v, 1)}</div>' for v in sorted(vals, key=str))}</td></tr>"
        for t, vals in rows
    )
    body = f"""<div>{kinds}</div>
<h1>{html.escape(str(label))}</h1>
<div class="iri">{html.escape(str(s))}</div>
{f'<p class="def">{html.escape(str(definition))}</p>' if definition else ''}
<table>{table}</table>
<h2>Download</h2><p class="dl"><a href="{html.escape(name)}.ttl">This term (Turtle)</a><a href="../bionext.ttl">Full ontology (Turtle)</a><a href="../bionext.owl">Full ontology (RDF/XML)</a></p>"""
    return page(f"{label} · BioNExt", body, 1, str(definition or ""))


def term_graph(g, s):
    sub = Graph()
    for prefix, ns in g.namespaces():
        sub.bind(prefix, ns)
    stack, done = [s], set()
    while stack:  # concise bounded description: follow blank nodes only
        node = stack.pop()
        if node in done:
            continue
        done.add(node)
        for p, o in g.predicate_objects(node):
            sub.add((node, p, o))
            if not isinstance(o, (URIRef, Literal)):
                stack.append(o)
    return sub


def release_list():
    releases = sorted((ROOT / "releases").glob("v*/"), key=lambda p: [int(x) for x in p.name[1:].split(".")], reverse=True)
    if not releases:
        return ""
    items = "".join(
        f'<li>{r.name}: ' + " ".join(f'<a href="releases/{r.name}/{f.name}">{f.suffix[1:]}</a>' for f in sorted(r.glob("bionext.*"))) + "</li>"
        for r in releases
    )
    return f"<h2>Releases</h2><ul>{items}</ul>"


def build_index(g, terms):
    onto = BN[""]
    title = g.value(onto, RDFS.label) or "BioNExt Ontology"
    comment = g.value(onto, RDFS.comment) or ""
    version = g.value(onto, OWL.versionInfo) or ""
    sections = []
    for kind, heading in KINDS:
        members = [s for s in terms if (s, RDF.type, kind) in g and (kind != OWL.NamedIndividual or (s, RDF.type, OWL.Class) not in g)]
        if not members:
            continue
        items = "".join(
            f'<li data-q="{html.escape((local(s) + " " + str(g.value(s, RDFS.label) or "")).lower())}"><a href="ontology/{html.escape(local(s))}">{html.escape(str(g.value(s, RDFS.label) or local(s)))}</a></li>'
            for s in sorted(members, key=lambda s: str(g.value(s, RDFS.label) or local(s)).lower())
        )
        sections.append(f"<section><h2>{heading} ({len(members)})</h2><ul class=\"terms\">{items}</ul></section>")
    body = f"""<h1>{html.escape(str(title))}</h1>
<div class="iri">{html.escape(str(onto))} · version {html.escape(str(version))}</div>
<p class="def">{html.escape(str(comment).strip())}</p>
<p class="dl"><a href="bionext.ttl">Turtle</a><a href="bionext.owl">RDF/XML</a><a href="releases/v{html.escape(str(version))}/bionext.ttl">Release v{html.escape(str(version))}</a></p>
{release_list()}
<input id="q" type="search" placeholder="Filter {len(terms)} terms…" aria-label="Filter terms">
{''.join(sections)}
<script>
document.getElementById('q').addEventListener('input',e=>{{const q=e.target.value.toLowerCase();
document.querySelectorAll('li[data-q]').forEach(li=>li.hidden=!li.dataset.q.includes(q));}});
</script>"""
    return page(str(title), body, 0, str(comment).strip())


def main():
    g = Graph().parse(SRC)
    g.bind("obo", "http://purl.obolibrary.org/obo/")
    terms = sorted({s for s in g.subjects() if isinstance(s, URIRef) and local(s)}, key=str)

    usages = defaultdict(set)
    for s, p, o in g:
        if isinstance(s, URIRef) and local(s) and o in terms and s != o and p != RDFS.subClassOf:
            usages[o].add(s)

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "ontology").mkdir(parents=True)
    for s in terms:
        name = local(s)
        (OUT / "ontology" / f"{name}.html").write_text(build_term(g, s, usages[s]), encoding="utf-8")
        term_graph(g, s).serialize(OUT / "ontology" / f"{name}.ttl", format="turtle")
    (OUT / "index.html").write_text(build_index(g, terms), encoding="utf-8")
    (OUT / "ontology" / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../"><link rel="canonical" href="../">',
        encoding="utf-8",
    )
    shutil.copy(SRC, OUT / "bionext.ttl")
    owl = SRC.with_suffix(".owl")
    if owl.exists():
        shutil.copy(owl, OUT / "bionext.owl")
    releases = ROOT / "releases"
    if releases.exists():
        shutil.copytree(releases, OUT / "releases")
    (OUT / ".nojekyll").touch()
    print(f"Built {len(terms)} term pages into {OUT}")


if __name__ == "__main__":
    main()
