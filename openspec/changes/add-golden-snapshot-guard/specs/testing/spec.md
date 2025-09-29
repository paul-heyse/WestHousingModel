## ADDED Requirements

### Requirement: Golden Snapshot Guard

Golden datasets SHALL be protected by automated diff guards that fail CI on unapproved changes and provide clear instructions for intentional updates.

#### Scenario: Tests detect unexpected golden changes
- **WHEN** golden-producing tests run without an acceptance flag
- **THEN** they SHALL fail if outputs differ from committed goldens and emit a diff summary for review.

#### Scenario: Intentional updates documented
- **WHEN** contributors regenerate goldens
- **THEN** they SHALL set an acceptance flag/command, update accompanying metadata, and note the rationale per documentation, ensuring CI passes.

#### Scenario: Reviewers see diffs
- **WHEN** CI encounters golden diffs
- **THEN** it SHALL attach or print human-readable summaries so reviewers can quickly assess the impact.
