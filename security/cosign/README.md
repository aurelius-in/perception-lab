# Cosign key management (summary)

- Generate key pair: `cosign generate-key-pair`
- Store private key in a secure secret manager (e.g., GitHub Actions secret)
- Sign: `cosign sign -y ghcr.io/OWNER/IMAGE:TAG`
- Verify: `cosign verify ghcr.io/OWNER/IMAGE:TAG`
