## 1. Implementation
- [x] 1.1 Extend `build_ops_features` to optionally accept source metadata and return `(frame, provenance)`.
- [x] 1.2 Add `extract_ops_provenance` helper that normalizes `source_id`, `as_of`, and transformation notes.
- [x] 1.3 Update CLI feature generation and valuation pipeline helpers to capture and persist ops provenance.

## 2. Tests
- [x] 2.1 Unit: verify provenance values for combinations of utilities/broadband/zoning inputs.
- [x] 2.2 CLI & golden snapshot: ensure outputs include the new provenance data and manifests remain stable.

## 3. Documentation
- [x] 3.1 Update ops features spec and architecture references with provenance expectations.
