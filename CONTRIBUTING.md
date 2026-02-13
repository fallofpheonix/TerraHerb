# Contributing to TerraHerb

Thanks for contributing.

## Development setup
1. `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb`
2. `docker compose up -d postgres redis`
3. `cd backend && ./scripts/migrate.sh`
4. `cd backend && go test ./...`
5. `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb && flutter pub get`
6. `cd /Users/fallofpheonix/AndroidStudioProjects/terraherb && flutter analyze && flutter test`

## Branch and PR guidelines
1. Create focused branches per feature or fix.
2. Keep PRs small and include a clear problem statement.
3. Add or update tests when behavior changes.
4. Document any API contract or migration changes in the PR description.

## Commit guidance
- Use clear, scoped commit messages.
- Include migration notes when SQL files change.
- Avoid unrelated formatting-only churn.

## Code standards
- Keep backend handlers thin; move business logic to service layer.
- Keep repository SQL deterministic and parameterized.
- Preserve fallback behavior in Flutter UI when backend is unavailable.

## Reporting bugs
Open an issue with:
- expected behavior
- actual behavior
- reproduction steps
- logs/screenshots if relevant
