# BioNExt Ontology — term resolver

This repository publishes a page for every term in the BioNExt Ontology, so that each
term IRI resolves to something a person or a machine can read.

| IRI | Resolves to |
|---|---|
| `https://w3id.org/bionext/ontology/` | ontology overview (or the full `.ttl` / `.owl`) |
| `https://w3id.org/bionext/ontology/<Term>` | term page (or the term's own Turtle) |
| `https://w3id.org/bionext/releases/v<version>/bionext.<ttl\|owl\|rdf\|json>` | versioned release |

Browsers get HTML. Clients sending `Accept: text/turtle` or `application/rdf+xml` get RDF
(see [`w3id/.htaccess`](w3id/.htaccess)). The underlying site is
<https://s3bio.github.io/bionext-ontology/>.

## Layout

- `ontology/bne_ontology.ttl`, `ontology/bne_ontology.owl`: the current ontology, copied from
  [S3Bio/BioNExt](https://github.com/S3Bio/BioNExt) (where it is built)
- `releases/v<version>/`: released files, copied from S3Bio/BioNExt. v1.0.0 still uses the
  old `jamiesilakom618.github.io/BioNExt/` IRIs; v1.1.0 is the first release with w3id IRIs
- `scripts/build_site.py`: generates `site/` (one HTML + one Turtle file per term)
- `.github/workflows/pages.yml`: builds and deploys to GitHub Pages on every push to `main`
- `w3id/.htaccess`: redirect rules registered at [perma-id/w3id.org](https://github.com/perma-id/w3id.org)

## Updating

After a new build or release in S3Bio/BioNExt, copy its `ontology/` files and the new
`releases/v<version>/` folder here and push. The pages rebuild automatically. To preview locally:

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
