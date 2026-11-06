# BioNExt Ontology v1.0.0

Released: 2026-07-13

## Release contents

- `bionext.ttl` — Turtle
- `bionext.owl` — RDF/XML (OWL)
- `bionext.rdf` — RDF/XML
- `bionext.json` — JSON-LD
- 1535 base graph RDF triples before serialization-specific metadata

## Companion modules

The generated module files are distributed separately in `output/modules/`:

- `cellular-location.ttl`
- `complex.ttl`
- `controlled-vocabulary.ttl`
- `core.ttl`
- `dna.ttl`
- `edge-entity.ttl`
- `entity.ttl`
- `gene.ttl`
- `influence.ttl`
- `interaction.ttl`
- `node-entity.ttl`
- `organism.ttl`
- `ortholog-group.ttl`
- `pathway-module.ttl`
- `protein.ttl`
- `provenance.ttl`
- `reaction.ttl`
- `region-type.ttl`
- `relationship-type.ttl`
- `rna.ttl`
- `small-molecule.ttl`

## Changes

- Added the canonical `bn` ontology and `bnr` resource namespaces.
- Added ontology provenance and version metadata.
- Added OWL 2 DL declarations and automated profile validation.
- Added combined ROBOT OWL 2 DL and HermiT validation reporting.
- Added companion hierarchy-based ontology modules.
- Added Turtle, OWL, RDF/XML, and JSON-LD release serializations.
