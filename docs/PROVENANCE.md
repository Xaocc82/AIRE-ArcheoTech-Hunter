# Provenance Policy

Original artifacts are immutable and addressed by SHA-256. Derived artifacts
such as embedded PDF text, OCR, translations, thumbnails, and model outputs
reference their input artifact hash and record the producing tool, version,
parameters, and creation time.

An archival assertion is evidential only when it resolves to the source URL,
original artifact hash, document, physical page, and exact evidence span.
Translations and analyst interpretations are separate from original source
statements. Each research run stores its configuration, source queries,
artifacts, code commit, environment fingerprint, and result manifest.
