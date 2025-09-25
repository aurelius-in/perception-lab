# SBOM guidance

- Generate SBOM with Syft: `syft packages dir:. -o spdx-json > artifacts/sbom.spdx.json`
- Store SBOM as build artifact and attach to releases.
- Scan image with Grype in CI and fail on Critical severities.
