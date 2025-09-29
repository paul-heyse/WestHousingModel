## ADDED Requirements

### Requirement: Automated Security Scanning

The CI pipeline SHALL include static security analysis and dependency vulnerability auditing, with documented workflows for remediation and suppression.

#### Scenario: Security lint executes in CI
- **WHEN** CI runs for any branch or PR
- **THEN** a security lint stage SHALL execute (Bandit or Ruff security rules) against `src/` and fail the build on medium/high severity issues unless explicitly allowlisted.

#### Scenario: Dependency vulnerabilities audited
- **WHEN** the dependency audit job runs
- **THEN** it SHALL invoke `pip-audit` or `safety` against the locked dependency set and fail on high severity advisories unless a timeboxed allowlist entry exists.

#### Scenario: Developer workflow documented
- **WHEN** contributors consult project docs
- **THEN** they SHALL find instructions for running the security lint and dependency audit locally, along with guidance on adding justified suppressions and rotating allowlists.
