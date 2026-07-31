# KML Philosophy

## Layers

| Layer | Role |
|---|---|
| **KML Studio** | Primary interface for authoring KML content |
| **Repository** | Storage layer (metadata, schemas, templates, source) |
| **Publishing Engine** | Transformation layer (packs → HTML and future outputs) |
| **Generated website** | Presentation layer (disposable output artifacts) |

## Studio philosophy

KML Studio is the primary interface for authoring KML content.

The repository is the storage layer.

The Publishing Engine is the transformation layer.

The generated website is the presentation layer.

The author should normally interact with Studio rather than the repository.

The repository should be organized for maintainability.

Studio should be organized for productivity.

Future improvements should favor improving the author experience rather than
increasing architectural complexity.

## Practical implications

1. Prefer Studio workflows (dashboard, validate, build) over hunting folders.
2. Keep metadata packs and schemas stable; evolve Studio UX freely.
3. Keep the Publishing Engine independent — CLI and Studio call the same API.
4. Do not hand-edit generated HTML; regenerate from metadata.
5. Add frameworks only when they clearly improve the author experience — Studio
   v1 stays on Python’s stdlib HTTP server plus the existing Jinja2 dependency
   shared with the Publishing Engine (no Flask/Django/etc.).

## Architecture Freeze v1

See [architecture_freeze_v1.md](architecture_freeze_v1.md).

The core platform is frozen. Prefer authoring experience, content, and tooling
over structural redesign unless real use demonstrates a hard limitation.
