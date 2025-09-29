## 1. Implementation

- [x] 1.1 Create `src/west_housing_model/config/registry_loader.py` with loader + merge logic.
- [x] 1.2 Validate required fields and enums; surface `RegistryError` with actionable messages.
- [x] 1.3 Produce a data dictionary object (list of sources with field meanings, cadence, TTL, license, last refresh if known).
- [x] 1.4 Export loader in `src/west_housing_model/config/__init__.py`.

## 2. Tests & Docs

- [x] 2.1 Unit tests for merge order, missing/unknown fields, and enum validation.
- [x] 2.2 Minimal `config/README.md` documenting fields and merge behavior for contributors.

## 3. Validation

- [x] 3.1 Run `openspec validate add-registry-loader-validation --strict` and resolve any issues.
