#!/usr/bin/env bash
# LEGACY (2026-10-10): kept until tests/system e2e (pytest, marker e2e) covers D1-D6 with JUnit output;
# then removed. Run via `make test-smoke-legacy`. See docs/testing/02-strategy.md (regression).
# Smoke test tự động cho PoC hạ tầng EMS (bước 2–4 của README "Kết quả chạy thử").
#   tests/smoke.sh          # stack đã chạy (docker compose up -d trong infra/)
#   tests/smoke.sh --up     # tự build + up trước
# Exit != 0 khi có bước thất bại.
set -uo pipefail
cd "$(dirname "$0")/../infra"
[ -f .env ] || { echo "thiếu infra/.env (cp .env.example .env và đặt mật khẩu)"; exit 2; }
if [ "${1:-}" = "--up" ]; then docker compose up -d --build --wait || exit 1; fi
T() { docker compose --profile tools run --rm -q tools "$@" 2>&1 | grep -v -E '^ ?Container '; return "${PIPESTATUS[0]}"; }
retry() { local n=$1; shift; for i in $(seq "$n"); do T "$@" > /tmp/smoke.out && { cat /tmp/smoke.out; return 0; }; sleep 10; done; cat /tmp/smoke.out; return 1; }
fail=0
step() { echo; echo "=== $1"; }

step "2a. Telemetry PV, BESS, công tơ, EV có trong DB"
retry 18 coverage --minutes 10 || fail=1
step "2b. Cân bằng công suất tại công tơ POC (đợi đủ phút trọn vẹn)"
retry 24 balance --minutes 5 --max-err-pct 3 || fail=1

step "3. Lệnh SET_ESS_P -100 kW 10 phút: RECEIVED -> ACCEPTED -> DISPATCHED -> APPLIED"
T send-ess-p --p-kw -100 --minutes 10 --expect APPLIED || fail=1
sleep 35
T check-ess --expect-p-kw -100 --tol-kw 5 --seconds 30 || fail=1

step "4a. Lệnh đã hết hạn -> REJECTED_STALE, không DISPATCHED/APPLIED"
T send-ess-p --p-kw 80 --expired --expect REJECTED_STALE || fail=1
step "4b. Gửi trùng command_id -> chỉ thực thi một lần"
T send-ess-p --p-kw -60 --minutes 5 --repeat 2 --expect APPLIED || fail=1

step "Dọn: SET_ESS_P 0 (đường an toàn hóa)"
T send-ess-p --p-kw 0 --minutes 1 --expect APPLIED || fail=1

echo
if [ $fail -eq 0 ]; then echo "SMOKE: PASS"; else echo "SMOKE: FAIL"; fi
exit $fail
