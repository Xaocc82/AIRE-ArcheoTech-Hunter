# Source Access Policy

Every source adapter is read-only and targets only official public APIs,
catalogues, IIIF endpoints, or user-provided files that the user is entitled
to process. An adapter records its terms reference, rights policy, limits,
source URL, retrieval time, HTTP status, and raw response artifact.

The project forbids uncontrolled crawling, hidden-URL discovery, bypassing
authentication or paywalls, processing leaks, and access to restricted
collections. Adapters must use an allowlist, a descriptive User-Agent,
timeouts, bounded retries, rate limits, result limits, document limits, and
byte limits. A missing or prohibitive rights condition blocks download.

Downloaded originals, generated CAS objects, and protected source content are
never committed to Git. Only code, synthetic fixtures, public manifests where
permitted, hashes, and source references may enter the repository.
