# tests/security — security (marker `security`)

MQTT ACL positive/negative per user, identity from topic not payload (A1-BUG-04), anonymous refused, command anti-replay,
no default credentials. `make test-security` also runs bandit, pip-audit and gitleaks (if installed).
