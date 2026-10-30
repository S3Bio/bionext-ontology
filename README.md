# BioNExt Ontology — term resolver

This repository publishes a page for every term in the BioNExt Ontology, so that each
term IRI resolves to something a person or a machine can read.

| IRI | Resolves to |
|---|---|
| `https://w3id.org/bionext/ontology/` | ontology overview (or the full `.ttl` / `.owl`) |
| `https://w3id.org/bionext/ontology/<Term>` | term page (or the term's own Turtle) |
| `https://w3id.org/bionext/releases/v1.0.0/bionext.ttl` | versioned release |

Browsers get HTML. Clients sending `Accept: text/turtle` or `application/rdf+xml` get RDF
(see [`w3id/.htaccess`](w3id/.htaccess)). The underlying site is
<https://s3bio.github.io/bionext-ontology/>.

## Layout

- `ontology/bne_ontology.ttl`, `ontology/bne_ontology.owl`: the ontology (source of truth)
- `scripts/build_site.py`: generates `site/` (one HTML + one Turtle file per term)
- `.github/workflows/pages.yml`: builds and deploys to GitHub Pages on every push to `main`
- `w3id/.htaccess`: redirect rules registered at [perma-id/w3id.org](https://github.com/perma-id/w3id.org)

## Updating

Edit the files in `ontology/` and push. The pages rebuild automatically. To preview locally:

```sh
pip install -r requirements.txt
python scripts/build_site.py
python -m http.server -d site
```

Note: `bn:CellularLocation` (class) and `bn:cellularLocation` (property) differ only in
case, so their generated files collide on case-insensitive filesystems such as macOS's
default. The CI build on Linux is unaffected.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
