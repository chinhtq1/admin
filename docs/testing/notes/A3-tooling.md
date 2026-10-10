# A3 — Chọn công cụ kiểm thử cho EMS (PoC Python hôm nay, Java/Spring + Angular sau)

- Ngày: 2026-10-10 · Vai trò: test tooling researcher · Trạng thái: **đã cài và chạy thử thật** các công cụ chính (log lệnh ở [§7](#7-nhật-ký-lệnh-đã-chạy)).
- Phạm vi: chọn công cụ cho automation test của `simulators/vsite`, `edge/bridge`, `ingest`, `simulators/evse`, `tools/ems_cli.py`, `infra/`; thiết kế để Java/Spring Boot + Angular cắm vào sau.
- Nhãn bằng chứng: **FACT** (có file:dòng hoặc output lệnh), **INFERENCE** (suy luận), **UNKNOWN** (chưa kiểm được).
- Môi trường thử: Linux, 4 CPU, Python 3.13.16 trên host (container dùng 3.12), Docker 29.8.2, Go 1.24.7 (tự tải toolchain 1.26.9), Node 22.22.0, Playwright (Node) 1.56.1 + Chromium 141 tại `/opt/pw-browsers`.
- Ràng buộc mạng đã quan sát (FACT): PyPI, npm, `proxy.golang.org`, Docker Hub, `mirror.gcr.io` đi được; **`github.com/.../releases` bị proxy trả 403**, **`gh api` bị chặn cho repo ngoài**, **`semgrep.dev` bị 403**, `ghcr.io` bị chặn (theo đề bài). Vì vậy mọi binary Go được cài bằng `go install` hoặc lấy image Docker Hub.

## Mục lục

1. [Tóm tắt quyết định](#1-tóm-tắt-quyết-định)
2. [Bảng quyết định](#2-bảng-quyết-định)
3. [Phân tích theo nhóm](#3-phân-tích-theo-nhóm)
4. [Phát hiện phụ khi chạy công cụ trên repo](#4-phát-hiện-phụ-khi-chạy-công-cụ-trên-repo)
5. [GitHub Actions: lưu ý](#5-github-actions-lưu-ý)
6. [Lộ trình khi có Java/Spring + Angular](#6-lộ-trình-khi-có-javaspring--angular)
7. [Nhật ký lệnh đã chạy](#7-nhật-ký-lệnh-đã-chạy)

---

## 1. Tóm tắt quyết định

- **Runner:** `pytest 9.1.1` + `pytest-xdist` (song song), `pytest-timeout` (bắt treo MQTT/Modbus), `pytest-cov`, `pytest-randomly` (lộ phụ thuộc thứ tự), `pytest-rerunfailures` **chỉ theo marker** (chính sách §3.2), `pytest-repeat` cho săn flaky ban đêm. Báo cáo: **JUnit XML + pytest-html** (self-contained); Allure để sau.
- **Property-based:** `hypothesis` — đã chứng minh giá trị: 300 ví dụ sinh ngẫu nhiên kiểm `Aggregator` (edge/bridge) theo JSON Schema của 07 (§3.3).
- **Hợp đồng:** `jsonschema` lấy schema **trực tiếp từ doc 07** (MQTT, không có consumer/provider HTTP tách đội) — **không dùng Pact lúc này**; xét lại khi có REST API Java ↔ Angular.
- **Hạ tầng test:** `testcontainers-python` cho test thành phần cô lập (Mosquitto, TimescaleDB + `infra/db/init.sql`) — chạy được, Ryuk dọn rác; **docker compose (project `emspoc`)** cho E2E toàn stack, do agent sở hữu Docker khởi động.
- **Client giao thức:** `paho-mqtt 2.1.0` (đã là dependency sản phẩm), `aiomqtt 2.5.1` (asyncio, bọc paho) cho tải; `pymodbus 3.15.0` client.
- **Tải MQTT ingest:** **bộ sinh tải asyncio tự viết (aiomqtt)** — 1 process giả 1.000 edge đạt ~32k mẫu/s (mục tiêu NFR-PERF-004 = 35k). **Không chọn k6/xk6-mqtt** vì chỉ MQTT 3.1.1 (không có Message Expiry/Correlation Data/User Property) và giấy phép AGPL-3.0; **Locust** để dành cho HTTP API sau này.
- **Mutation:** **mutmut 3.8.0** (chạy được trên 3.13, nhanh ~30× cosmic-ray trên cùng module).
- **Tĩnh/bảo mật:** `ruff 0.17.0` (lint+format), `bandit 1.9.4` (SAST gate, offline), `semgrep 1.180.0` chỉ với **rule nội bộ** (registry bị chặn ở đây), `pip-audit 2.10.1`, `gitleaks v8.30.1` (gate) + `trufflehog 3.99.2` (quét định kỳ), `trivy 0.69.3` (image scan, Docker Hub image), `actionlint 1.7.12`.
- **Tiêm lỗi mạng (thay toxiproxy GHCR):** `toxiproxy v2.12.0` cài bằng `go install` (đã chứng minh latency 200 ms); `iptables DROP` trong netns container qua sidecar `nicolaka/netshoot` (blackhole); `docker pause`/`network disconnect`. **`tc netem` KHÔNG chạy trên host này** (kernel thiếu `sch_netem`).
- **UI/doc:** Playwright Python 1.56.0 dùng chung Chromium 1194 ở `/opt/pw-browsers` — mở wireframe được.

## 2. Bảng quyết định

Cột "Cài đặt đã kiểm?" = đã chạy lệnh cài và lệnh dùng thật trong phiên này (FACT, xem §7).

| Công cụ | Mục đích | Phiên bản | Giấy phép | Chọn? | Vì sao | Cài đặt đã kiểm? |
|---|---|---|---|---|---|---|
| pytest | Runner chung (unit → E2E) | 9.1.1 | MIT | **Có** | Chuẩn Python; marker phân tầng; plugin phong phú | Có — `pip install pytest==9.1.1` |
| pytest-xdist | Chạy song song `-n auto` | 3.8.0 | MIT | **Có** (unit/contract) | 4 CPU local, 4 vCPU runner; E2E chạy tuần tự vì dùng chung stack | Có — demo `-n 2`, `-n 4` pass |
| pytest-timeout | Cắt test treo (socket MQTT/Modbus) | 2.4.0 | MIT | **Có** | Treo là lỗi phổ biến nhất của test mạng | Có |
| pytest-cov (coverage 7.16.2) | Coverage in-process | 7.1.0 | MIT | **Có** | Coverage trong container cần `COVERAGE_PROCESS_START`, để giai đoạn 2 | Có — 100% trên demo |
| pytest-randomly | Xáo thứ tự + seed cố định in ra | 5.0.0 | MIT | **Có** (unit) | Lộ phụ thuộc thứ tự; tắt cho E2E bằng `-p no:randomly` | Có — chạy cùng xdist OK |
| pytest-rerunfailures | Rerun test flaky | 16.7 | MPL-2.0 | **Có, có điều kiện** | Chỉ `@pytest.mark.flaky(reruns=2)` trên E2E có lý do + issue; cấm `--reruns` toàn cục | Có — `--reruns 1` chạy |
| pytest-repeat | Săn flaky `--count N` | 0.9.4 | MPL-2.0 | **Có** (nightly) | Lặp test nghi flaky trước khi gắn quarantine | Có — `--count 3` = 12 pass |
| pytest-html | Báo cáo HTML 1 file | 4.2.0 | MPL-2.0 | **Có** | Artifact CI xem được không cần server | Có — `--self-contained-html` |
| JUnit XML (built-in) | Báo cáo máy đọc | — | — | **Có** | GitHub/Jenkins/Allure đều đọc; dùng chung cho Java sau | Có |
| allure-pytest | Báo cáo Allure | 2.16.2 | Apache-2.0 | Chưa | Cần Allure CLI (Java) để render; giá trị khi có nhiều stack (JUnit5, Playwright TS) | Có (plugin ghi kết quả); CLI chưa thử |
| hypothesis | Property-based | 6.168.5 | MPL-2.0 | **Có** | Bất biến cửa sổ/quality/dấu; đã chạy 300 ví dụ trên `Aggregator` | Có |
| testcontainers | Container ephemeral cho test thành phần | 4.15.0 (Ryuk 0.8.1) | Apache-2.0 | **Có** | Cô lập, cổng ngẫu nhiên, tự dọn; Mosquitto + TimescaleDB chạy được | Có — 2 test pass |
| docker compose fixture | E2E toàn stack `emspoc` | Compose v2 (Docker 29.8.2) | Apache-2.0 | **Có** (E2E) | Stack đã định nghĩa ở `infra/docker-compose.yml`; một nguồn sự thật | Không chạy (không sở hữu stack) |
| jsonschema | Contract test payload MQTT | 4.26.0 | MIT | **Có** | Schema có sẵn trong 07; Draft-7 validator | Có |
| Pact (pact-python) | Consumer-driven contract | 3.4.1 (+ffi 0.5.8.0) | MIT | Không (giờ) | Không có cặp consumer/provider tách đội; MQTT message pact lợi ít hơn schema 07; xét lại cho REST Java↔Angular | Chỉ `pip install --dry-run` (resolve OK) |
| paho-mqtt | Client MQTT 5 cho test | 2.1.0 | EPL-2.0 / BSD-3 | **Có** | Trùng dependency sản phẩm; MQTT5 properties đầy đủ | Có — roundtrip QoS1 + CorrelationData |
| aiomqtt | Client asyncio (tải) | 2.5.1 | BSD-3-Clause | **Có** (load) | 1.000 kết nối trong 1 process; bọc paho 2 nên cùng ngữ nghĩa | Có — 1.000 edge chạy |
| pymodbus (client) | Đọc/ghi register vsite | 3.15.0 | BSD-3-Clause | **Có** | Trùng phiên bản server SimDevice | Có (import + khởi tạo client) |
| mutmut | Mutation testing | 3.8.0 | BSD-3-Clause | **Có** (nightly, module lõi) | Py3.13 OK; 193 mutant trong ~2,3 s | Có |
| cosmic-ray | Mutation testing | 8.7.0 | MIT | Không | Py3.13 OK nhưng 287 job mất 74 s trên cùng module (chạy tuần tự, 1 subprocess/mutant) | Có |
| ruff | Lint + format | 0.17.0 | MIT | **Có** | Nhanh; thay flake8/isort/black | Có — 20 phát hiện trên code |
| bandit | SAST Python (gate) | 1.9.4 | Apache-2.0 | **Có** | Offline, không cần registry | Có — 11 phát hiện (0 High) |
| semgrep | SAST + rule tuỳ biến | 1.180.0 | LGPL-2.1 (engine) | **Có, giới hạn** | Viết rule hợp đồng riêng (QoS, DSN mặc định); registry `p/python` bị 403 ở đây | Có — rule cục bộ chạy |
| pip-audit | CVE dependency Python | 2.10.1 | Apache-2.0 | **Có** | Quét từng `requirements.txt` | Có — 0 lỗ hổng × 5 file |
| gitleaks | Secret scan (gate PR) | v8.30.1 | MIT | **Có** | Nhanh (66 commit 11,4 s), cấu hình allowlist đơn giản | Có — `go install` + image Docker Hub `zricethezav/gitleaks:v8.30.1` |
| trufflehog | Secret scan sâu (định kỳ) | 3.99.2 | AGPL-3.0 | **Có** (nightly, chỉ dùng như tool) | Detector theo loại (Postgres, AMQP); có verify | Có — image Docker Hub `trufflesecurity/trufflehog` |
| trivy | Quét image/IaC | 0.69.3 | Apache-2.0 | **Có** | Image Docker Hub `aquasec/trivy`; DB từ `mirror.gcr.io` (không cần GHCR) | Có — quét 3 image |
| k6 | Tải HTTP (sau này) | v2.3.0 (image) | AGPL-3.0 | Để sau | Hợp cho REST Java; không dùng cho MQTT | Có — `grafana/k6` chạy `version` |
| xk6-mqtt (grafana) | k6 MQTT | v0.3.3 | AGPL-3.0 | **Không** | README:156 "MQTT v5 is not supported yet" — hợp đồng 07 cần MQTT 5 | Đọc mã nguồn từ Go proxy; không build |
| locust | Tải HTTP Python | 2.46.7 | MIT | Để sau | MQTT phải tự viết User; với asyncio thuần đơn giản hơn | Có (`pip install`) |
| toxiproxy | Proxy tiêm lỗi TCP | v2.12.0 (`go install`) | MIT | **Có** | Latency/timeout/bandwidth userspace, không cần kernel module | Có — latency 7 ms → 208 ms |
| iptables trong netns (netshoot) | Blackhole/drop | nicolaka/netshoot:v0.15 | Apache-2.0 | **Có** | Mô phỏng "treo im lặng" — `TimeoutError` sau 3 s | Có |
| docker pause / network disconnect | Mất kết nối thô | Docker 29.8.2 | — | **Có** | Không cần image phụ | Có |
| tc netem | Trễ/mất gói ở kernel | — | — | Không (local) / Có thể (CI) | Host này: "Specified qdisc kind is unknown" | Có — **thất bại** |
| pumba | Chaos Docker (netem/pause) | 0.11.6 | Apache-2.0 | Không | Netem phụ thuộc kernel như trên; pause đã có sẵn | Chỉ pull image |
| shopify/toxiproxy (Docker Hub) | Toxiproxy image | 2.1.4 | MIT | Không | Bản 2019, cũ; dùng bản `go install` | Chỉ pull image |
| Playwright (Python) + pytest-playwright | Kiểm wireframe/HTML doc | 1.56.0 / 0.10.0 | Apache-2.0 | **Có** | Cùng pytest; dùng chung Chromium 1194 (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) | Có — mở UI-03 |
| Playwright (Node) | UI test Angular sau này | 1.56.1 (global) | Apache-2.0 | Để sau | Hợp với Angular/TS | Có — mở 05-domain-model.html, 0 pageerror |
| actionlint | Lint workflow GHA | v1.7.12 | MIT | **Có** | Bắt script injection, input sai | Có — `go install` + image `rhysd/actionlint:1.7.12` |

## 3. Phân tích theo nhóm

### 3.1 Runner và phân tầng

- Marker đề xuất: `unit`, `property`, `contract`, `component` (testcontainers), `integration`/`e2e` (stack `emspoc`), `ui`, `load`, `chaos`. CI chọn theo marker (§5).
- `pytest-randomly` + `pytest-xdist` chạy cùng nhau được (FACT: `pytest demo -n 2 -p randomly ... → 4 passed`). E2E dùng chung một stack nên tắt `-n` và `randomly`.
- `pytest-timeout`: mặc định 60 s cho unit, 300 s cho E2E; luôn dùng `timeout_method=thread` khi test có thread paho (INFERENCE: `signal` không ngắt được thread nền).

### 3.2 Chính sách rerun / flaky

1. Cấm `--reruns` toàn cục. Chỉ `@pytest.mark.flaky(reruns=2, reruns_delay=2)` cho test E2E/thời gian thực, kèm comment link issue.
2. Mọi lần rerun phải hiện trong báo cáo (pytest-rerunfailures ghi outcome `R`); job tổng kết đếm rerun, > 0 → cảnh báo.
3. Nightly: `pytest -m "e2e" --count 20 -x -p no:randomly` (pytest-repeat) cho test nghi flaky; flaky xác nhận → marker `quarantine` + issue; quarantine > 14 ngày phải sửa hoặc xoá.
4. Không rerun unit/contract/property — fail ở đó là bug thật hoặc test sai.

### 3.3 Property-based (hypothesis) + contract (jsonschema)

- FACT: test thử sinh 300 chuỗi đọc ngẫu nhiên (ts, value None/float, quality GOOD/BAD/UNCERTAIN; lớp C1/C2/C3) cho bản sao `edge/bridge/bridge/aggregate.py`, `flush()` rồi validate từng mẫu với **JSON Schema gauge của 07** (`docs/research/ems/07-device-integration.md:962-985`) → **pass**.
- FACT: schema 07 **không hợp lệ theo Draft 2020-12** (mặc định của `jsonschema.validate` khi không có `$schema`): `$id: "ems.telemetry.v1#/gaugeSample"` có fragment không rỗng → `SchemaError ... does not match '^[^#]*#?$'`. Hợp lệ với `Draft7Validator`. → Test phải dùng `Draft7Validator` tường minh, hoặc 07 sửa `$id` + thêm `$schema` (báo cho chủ 07).
- Pact: dry-run `pact-python 3.4.1` resolve được, nhưng (INFERENCE) hiện chỉ có một đội, hợp đồng là văn bản 07 + broker MQTT; Pact message-pact thêm broker/pactflow mà không thêm thông tin so với schema. Khi có REST Spring ↔ Angular thì cân nhắc Pact (hoặc Spring Cloud Contract) cho HTTP.

### 3.4 testcontainers vs docker compose

| Tiêu chí | testcontainers 4.15.0 | docker compose (`emspoc`) |
|---|---|---|
| Phạm vi | 1–2 dịch vụ, cấu hình riêng mỗi test | Toàn stack như demo |
| Thời gian | Mosquitto+test 3,7 s; TimescaleDB + `init.sql` 4,75 s (FACT) | Phút (build + healthcheck) |
| Cô lập | Cổng ngẫu nhiên, Ryuk tự dọn (FACT: không còn container sau test) | Chung, phải reset dữ liệu giữa test |
| Rủi ro | Cần pull `testcontainers/ryuk:0.8.1` từ Docker Hub (429?) | Chỉ agent sở hữu được start/stop |

- Quyết định: **cả hai**, phân theo marker. Fixture E2E **chỉ attach** vào stack đã chạy (đọc `infra/.env`, kiểm health), không tự `up`/`down` ở local; trong CI job riêng khởi động compose.
- FACT: `testcontainers.postgres` đã deprecated trong 4.15 → dùng `testcontainers.community.postgres`; truyền `driver=None` để lấy URL `postgresql://` dùng cho psycopg 3.
- FACT: chạy `infra/db/init.sql` trên `timescale/timescaledb:2.17.2-pg16` tạo bảng `command, command_ack, edge_state, event, telemetry, telemetry_batch`; hypertable: `telemetry`.

### 3.5 MQTT 5 và tải ingest

- FACT (broker Mosquitto 2.0.20 ném đi, cấu hình mặc định `max_queued_messages` = 1000): bắn 2.000 tin QoS1 liên tục → subscriber chỉ nhận **1.745/2.000**; đặt `max_queued_messages 100000` → nhận đủ 2.000 trong 0,54 s (~3.700 msg/s, 1 cặp pub/sub). Hệ quả cho test: tải phải kiểm **mất tin ở phía broker** khi consumer chậm; PoC đặt `max_queued_messages 10000` (`infra/mosquitto/mosquitto.conf:13`) — cần test dựng ingest chậm để xem NFR-REL-016 ("event, cmd-ack, state không bao giờ bị bỏ") có giữ không.
- FACT: prototype `aiomqtt` — 1.000 client MQTT 5 trong 1 process, mỗi edge 1 tin/s × 35 mẫu, 20 s → `19975 msgs, 31972 samples/s over 21.9s` (gồm thời gian kết nối). Mục tiêu NFR-PERF-004: 35.000 mẫu/s cho 1.000 site (`docs/research/ems/04-business-requirements.md:1944`). INFERENCE: 1 process đủ cho hồ sơ danh định; hồ sơ backfill 5–10× cần 2–4 process (`multiprocessing`) hoặc nhiều runner.
- k6 + xk6-mqtt: FACT `github.com/grafana/xk6-mqtt v0.3.3` dùng `paho.mqtt.golang v1.5.1`, README dòng 156: "MQTT v5 is not supported yet"; LICENSE AGPL-3.0. Hợp đồng 07 bắt buộc Message Expiry, Correlation Data, User Property `schema`/`edge_seq` → **loại**.
- Locust 2.46.7: cài được; INFERENCE: mô hình gevent + thread paho dễ sai số đo; để dành cho HTTP.

### 3.6 Mutation testing

| | mutmut 3.8.0 | cosmic-ray 8.7.0 |
|---|---|---|
| Python 3.13 | Cài + chạy OK | Cài + chạy OK |
| Cùng module `aggregate.py` + 2 test | 193 mutant, 87 killed / 106 survived, ~83 mutant/s (~2,3 s) | 287 job, 178 survived (62%), 74 s |
| Cấu hình | `[tool.mutmut]` trong pyproject; 3.8 cảnh báo `paths_to_mutate`/`tests_dir` deprecated → dùng `source_paths`, `pytest_add_cli_args_test_selection` | TOML riêng + sqlite session |

→ Chọn **mutmut**, chạy nightly cho module lõi (`edge/bridge/bridge/{aggregate,commands,store}.py`, `ingest/ingest.py` logic seq/ack). Không làm gate PR. Tỷ lệ survived cao trên demo là do chỉ 2 test — dùng để đo chất lượng test về sau.

### 3.7 Tĩnh, bảo mật, dependency

- **ruff 0.17.0** không có file cấu hình trong repo (FACT: `find` không thấy `pyproject.toml`/`ruff.toml`), bộ rule mặc định của 0.17 rộng hơn E/F (FACT: `--show-settings` liệt kê YTT…). Kết quả: 20 phát hiện (UP017, SIM115, I001, UP041, FURB162, ASYNC230…). → Thêm cấu hình `select` tường minh ở root khi dựng framework.
- **bandit 1.9.4**: 11 phát hiện (Medium 10, Low 1, High 0). Đa số chấp nhận được trong container (B104 bind 0.0.0.0, B108 file health `/tmp`). B608 `edge/bridge/bridge/store.py:67` là **false positive** (`op` chỉ là `">="`/`"<"` từ ternary dòng 64) → `# nosec B608` có lý do.
- **semgrep 1.180.0**: engine chạy offline với rule cục bộ (FACT: rule `env-default-credential-dsn` bắt 2 vị trí). `--config p/python` lỗi vì `semgrep.dev` bị 403 ở môi trường này; trên GitHub Actions dự kiến đi được (INFERENCE). Dùng cho rule riêng của dự án (QoS bắt buộc, không publish `down/cmd` ngoài dispatcher…), không làm gate SAST chính.
- **pip-audit 2.10.1**: 0 lỗ hổng cho cả 5 file requirements (FACT).
- **gitleaks v8.30.1** (gate): `gitleaks git .` → 66 commit, 1 phát hiện `curl-auth-user` tại `docs/research/ems/notes/E3-simulator-handson.md:182` (`curl -u admin:admin` — mật khẩu mặc định công khai của OpenEMS lab) → thêm fingerprint vào `.gitleaksignore`.
- **trufflehog 3.99.2** (nightly): 3 phát hiện chưa verify: Postgres DSN `ingest/ingest.py:42`, `tools/ems_cli.py:34`, AMQP URL trong E3 dòng 251.
- **trivy 0.69.3** (HIGH/CRITICAL, vuln OS): `ems-poc/edge-bridge:0.1.0` 44 HIGH, `ems-poc/ingest:0.1.0` 44 HIGH — **đều chưa có bản sửa** (Debian 13 base); `eclipse-mosquitto:2.0.20` 16 HIGH + 2 CRITICAL **có bản sửa** (libssl3/libcrypto3 3.3.3-r0 → 3.3.7-r0, cjson, musl, zlib), base **Alpine 3.20.6 đã EOSL**. Gate đề xuất: `--ignore-unfixed --severity CRITICAL --exit-code 1`; HIGH chỉ báo cáo.
  - Lưu ý môi trường này: proxy TLS-intercept → phải truyền `HTTPS_PROXY`, `--network host` và mount CA (`SSL_CERT_FILE`) vào container trivy, nếu không lỗi `x509: certificate signed by unknown authority` khi tải DB từ `mirror.gcr.io` (FACT). Trên GitHub Actions không cần.
- **Không có GHCR:** gitleaks/trufflehog/trivy/actionlint đều có image trên Docker Hub (FACT: pull được) hoặc `go install` từ `proxy.golang.org`. Release binary trên GitHub bị 403 ở đây. `go install` kéo toolchain go1.26.9 tự động (GOTOOLCHAIN=auto) vì module yêu cầu go ≥ 1.26.

### 3.8 Tiêm lỗi mạng (thay toxiproxy GHCR)

| Kỹ thuật | Kết quả trên host này (FACT) | Dùng cho |
|---|---|---|
| toxiproxy v2.12.0 (`go install github.com/Shopify/toxiproxy/v2/cmd/server@v2.12.0`) | MQTT CONNECT 7 ms → 208 ms với toxic `latency=200`; gỡ toxic → 7 ms | Trễ, timeout, cắt băng thông, reset giữa phiên giữa bridge↔broker, bridge↔vsite (Modbus) |
| iptables trong netns container (`docker run --cap-add NET_ADMIN --network container:X nicolaka/netshoot:v0.15 iptables -A INPUT -p tcp --dport 1883 -j DROP`) | Kết nối → `TimeoutError` sau 3 s; `iptables -F` khôi phục | "Mất mạng im lặng" (half-open), watchdog edge |
| `docker pause` | Qua cổng publish (docker-proxy) client nhận `ConnectionResetError` chứ không treo | Đóng băng tiến trình (SIGSTOP) — không thay được blackhole |
| `docker network disconnect` | `ConnectionRefusedError` | Mất cloud/broker rõ ràng |
| `tc qdisc ... netem` | **Thất bại**: `Specified qdisc kind is unknown` (kernel 6.18 của sandbox thiếu `sch_netem`; không có `/lib/modules`) | Có thể dùng trên runner Ubuntu (INFERENCE — kernel Ubuntu thường có `sch_netem`; UNKNOWN cho đến khi chạy CI) |

→ Mặc định dùng **toxiproxy** (không phụ thuộc kernel, đặt giữa các dịch vụ bằng cách trỏ host/port qua env) + **iptables/netshoot** cho blackhole. Lưu ý: chỉ agent sở hữu stack `emspoc` được chèn toxiproxy vào compose (override file `docker-compose.chaos.yml`).

### 3.9 UI / doc (Playwright)

- FACT: Node Playwright 1.56.1 mở `docs/research/ems/05-domain-model.html` (title "Mô hình miền EMS", 0 `pageerror`, Chromium 141.0.7390.37).
- FACT: Python `playwright==1.56.0` dùng được trình duyệt có sẵn (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, revision 1194) — mở `wireframes/UI-03-site-dashboard.html` ("UI-03 Dashboard site"). **Phải pin Python Playwright cùng minor với browser có sẵn (1.56)**, nếu không sẽ đòi tải browser mới.
- Hiện dùng Python (một runner pytest) để kiểm wireframe/doc: không lỗi JS, link nội bộ không gãy, mermaid render. Khi có Angular: chuyển UI test sang Playwright TS (`@playwright/test`) trong repo frontend.

## 4. Phát hiện phụ khi chạy công cụ trên repo

Không sửa code sản phẩm (không thuộc thư mục của A3). Báo cho orchestrator:

1. **[Doc 07] JSON Schema gauge không hợp lệ theo Draft 2020-12** — `docs/research/ems/07-device-integration.md` khoảng dòng 966: `$id` có fragment `#/gaugeSample`. FACT: `Draft202012Validator.check_schema` → INVALID; `Draft7Validator` → OK. Sửa đề xuất: `"$schema": "http://json-schema.org/draft-07/schema#"` hoặc `$id` không fragment + `$defs`.
2. **[ingest, tools] DSN mặc định có mật khẩu cứng** — `ingest/ingest.py:42`, `tools/ems_cli.py:34`: `ENV("DATABASE_URL", "postgresql://ems:ems@db:5432/ems")`. Compose luôn truyền `DATABASE_URL` với `${DB_PASSWORD}` (`infra/docker-compose.yml:93,147`) nên không lộ mật khẩu thật, nhưng trái quy tắc "không secret cứng" và bị trufflehog/semgrep cờ. Đề xuất: không có default, fail-fast khi thiếu env.
3. **[infra] `eclipse-mosquitto:2.0.20` trên Alpine 3.20.6 EOSL, 2 CRITICAL có bản sửa (OpenSSL 3.3.3)** — nâng tag Mosquitto mới hơn (UNKNOWN: tag cụ thể nào hết CVE — cần quét lại sau khi chọn).
4. **[edge/bridge] bandit B608 false positive** `edge/bridge/bridge/store.py:67` — nên thêm `# nosec B608` kèm lý do để gate sạch.
5. **[docs] gitleaks cờ** `docs/research/ems/notes/E3-simulator-handson.md:182` (`admin:admin` mặc định OpenEMS) — cần `.gitleaksignore` trước khi bật gate.
6. **[test design] Mất tin QoS1 do hàng đợi broker** (§3.5) — không phải bug PoC (PoC đặt 10000), nhưng là ca test bắt buộc cho NFR-REL-016.

## 5. GitHub Actions: lưu ý

- **Runner:** `ubuntu-24.04` (pin thay vì `ubuntu-latest` để tránh đổi image ngầm); có Docker Engine + Compose v2 sẵn (INFERENCE từ tài liệu runner image; xác nhận ở lần chạy đầu). 4 vCPU/16 GB cho repo public, 2 vCPU cho private (UNKNOWN — tuỳ gói; đặt `-n auto`).
- **Job tách theo tầng:** `static` (ruff, bandit, pip-audit, gitleaks, actionlint) → `unit` (unit+property+contract, matrix Python `3.12` = container, `3.13` = host) → `component` (testcontainers) → `integration` (compose `emspoc`, `--wait`, timeout 30') → nightly (`load`, `chaos`, mutmut, trufflehog, trivy full, `pytest --count`).
- **Secrets cho stack CI:** sinh `.env` tạm từ `.env.example` bằng `openssl rand -hex 16` trong job — không lưu secret repo cho stack test.
- **Cache:** `actions/setup-python` `cache: pip` với `cache-dependency-path: tests/requirements-test.txt`; cache `~/.cache/trivy` (DB ~ vài trăm MB) theo ngày; `~/.cache/ms-playwright` nếu cài browser; Docker layer: `docker/build-push-action` + `cache-from: type=gha` cho 5 image `ems-poc/*` (INFERENCE: tiết kiệm build pip trong image).
- **Docker Hub 429:** runner dùng IP chung → `docker/login-action` với token Docker Hub read-only (secret `DOCKERHUB_TOKEN`) + retry/backoff khi pull; pin tag + digest (vd. `trufflesecurity/trufflehog@sha256:47a84bc1…`, `grafana/k6@sha256:e66db15b…` — FACT từ `docker image inspect`).
- **Artifacts:** `actions/upload-artifact@v4` `if: always()` cho `reports/` (JUnit, pytest-html, coverage.xml, `compose logs` khi fail, kết quả trivy SARIF); `retention-days: 14`. Có thể đẩy SARIF (trivy/bandit/semgrep) lên code scanning.
- **Matrix:** Python `[3.12, 3.13]` cho unit; không matrix E2E (tốn, và stack là 3.12 trong container). `fail-fast: false`.
- **Bảo mật workflow:** `permissions: contents: read` mặc định; `concurrency` hủy run cũ; actionlint bắt script injection (FACT: cờ `${{ github.event.pull_request.title }}` trong `run:`). actionlint cần `shellcheck` để kiểm `run:` — host này không có shellcheck (FACT: `which shellcheck` rỗng); runner Ubuntu có sẵn (INFERENCE).
- **Pin action theo SHA** (khuyến nghị bảo mật) — chưa lấy SHA vì `gh api` bị chặn ở đây (UNKNOWN).
- FACT: một workflow mẫu 3 job (static/unit matrix/integration với compose + artifacts) viết trong scratch đã qua `actionlint` (exit 0). Phần khung:

```yaml
jobs:
  unit:
    runs-on: ubuntu-24.04
    strategy: { fail-fast: false, matrix: { python: ["3.12", "3.13"] } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python }}", cache: pip, cache-dependency-path: tests/requirements-test.txt }
      - run: pip install -r tests/requirements-test.txt
      - run: pytest -m "unit or property or contract" -n auto --junitxml=reports/junit-${{ matrix.python }}.xml --cov --cov-report=xml
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: "unit-${{ matrix.python }}", path: reports/, retention-days: 14 }
  integration:
    needs: [unit]
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    env: { COMPOSE_PROJECT_NAME: emspoc }
    steps:
      - uses: actions/checkout@v4
      - run: |
          cp infra/.env.example infra/.env
          for k in DB_PASSWORD MQTT_PASS_EDGE_VSITE01 MQTT_PASS_EDGE_EV01 MQTT_PASS_INGEST MQTT_PASS_DISPATCHER MQTT_PASS_HEALTH GRAFANA_ADMIN_PASSWORD; do
            sed -i "s/^$k=.*/$k=$(openssl rand -hex 16)/" infra/.env
          done
      - run: docker compose -f infra/docker-compose.yml up -d --build --wait
      - run: pytest -m "integration or e2e" -p no:randomly --timeout=300 --junitxml=reports/junit-int.xml
      - if: failure()
        run: docker compose -f infra/docker-compose.yml logs --no-color > reports/compose.log
      - if: always()
        run: docker compose -f infra/docker-compose.yml down -v
```

### Gói pin đề xuất cho `tests/requirements-test.txt`

Đã cài vào venv chung `/home/user/admin/.venv` (FACT: `pip check` → "No broken requirements found"; cùng tồn tại với `paho-mqtt 2.1.0`, `pymodbus 3.15.0`):

```
pytest==9.1.1
pytest-xdist==3.8.0
pytest-timeout==2.4.0
pytest-cov==7.1.0
pytest-randomly==5.0.0
pytest-rerunfailures==16.7
pytest-repeat==0.9.4
pytest-html==4.2.0
hypothesis==6.168.5
testcontainers==4.15.0
jsonschema==4.26.0
aiomqtt==2.5.1
playwright==1.56.0
pytest-playwright==0.10.0
ruff==0.17.0
bandit==1.9.4
pip-audit==2.10.1
# + product deps: paho-mqtt==2.1.0 pymodbus==3.15.0 psycopg[binary]==3.2.10 PyYAML==6.0.3
```

Cài riêng (không vào venv chung): `mutmut==3.8.0` (venv nightly), `semgrep==1.180.0` (nhiều dependency, cài bằng `pipx`/venv riêng). Binary Go: `actionlint v1.7.12`, `gitleaks v8.30.1`, `toxiproxy v2.12.0` qua `go install`; image Docker Hub: `aquasec/trivy:0.69.3`, `trufflesecurity/trufflehog:3.99.2`, `zricethezav/gitleaks:v8.30.1`, `rhysd/actionlint:1.7.12`, `nicolaka/netshoot:v0.15`.

`.gitignore` hiện có `.venv/`, `test-results/` (FACT). Đề xuất thêm: `.hypothesis/`, `mutants/`, `reports/`, `.coverage*`, `.pytest_cache/`.

## 6. Lộ trình khi có Java/Spring + Angular

- **Báo cáo chung:** JUnit XML từ pytest, Maven Surefire/Failsafe và Playwright TS → một bước tổng hợp (Allure hoặc `dorny/test-reporter`); đây là lý do chọn JUnit XML ngay từ đầu.
- **Java:** JUnit 5 + Testcontainers Java (cùng mô hình với testcontainers-python, cùng Ryuk), jqwik (property), PIT (mutation), JaCoCo, ArchUnit; contract REST: Pact JVM hoặc Spring Cloud Contract; MQTT tests dùng HiveMQ/Paho Java MQTT5. Schema 07 dùng chung từ một thư mục `contracts/` (JSON Schema Draft-7) cho cả Python và Java (networknt json-schema-validator).
- **Angular:** Playwright TS (`@playwright/test` 1.56.x khớp browser), Vitest/Jest unit; Lighthouse/axe cho NFR UI.
- **Tải HTTP:** k6 (image `grafana/k6`, đã chạy được) cho REST/GraphQL Java — chỉ dùng như công cụ, AGPL không ảnh hưởng mã sản phẩm (INFERENCE, cần pháp chế xác nhận). Tải MQTT giữ bộ sinh aiomqtt.
- **Bảo mật:** thêm OWASP Dependency-Check hoặc `trivy fs` cho Maven/npm; gitleaks/trivy/actionlint giữ nguyên.

## 7. Nhật ký lệnh đã chạy

Biến: `S=/tmp/claude-0/-home-user-admin/6aedd770-de72-529c-acf2-87df83aa2b49/scratchpad/a3` (venv ném đi `tv`, `mm`, `cr`, `sg`).

| # | Lệnh (rút gọn) | Kết quả |
|---|---|---|
| 1 | `python3 -m venv $S/tv && $S/tv/bin/pip install pytest pytest-xdist pytest-timeout pytest-cov pytest-randomly pytest-rerunfailures pytest-repeat pytest-html hypothesis testcontainers jsonschema ruff bandit pip-audit allure-pytest paho-mqtt==2.1.0 pymodbus==3.15.0 locust` | OK trên Python 3.13.16; phiên bản như bảng §2 |
| 2 | `pytest demo -q -n 2 -p randomly --timeout 10 --cov=demo --junitxml=... --html=... --self-contained-html --alluredir=...` | **4 passed** |
| 3 | `pytest demo -q --count 3 --reruns 1 -p no:randomly` | **12 passed** |
| 4 | `ruff check --statistics edge ingest simulators tools` | 20 errors (12 fixable) |
| 5 | `bandit -r edge ingest simulators tools` | 11 issues: High 0, Medium 10, Low 1 |
| 6 | `pip-audit -r <file>` × 5 requirements | 5 × "No known vulnerabilities found" |
| 7 | `python3 -m venv $S/mm && pip install mutmut`; `mutmut run` (bản sao aggregate.py + 2 test) | mutmut 3.8.0; 193 mutant: 87 killed, 106 survived; 82.98 mutations/s |
| 8 | `python3 -m venv $S/cr && pip install cosmic-ray`; `cosmic-ray init/exec`; `cr-report` | 8.7.0; 287 job, 178 survived (62.02%), real 1m14s |
| 9 | `pip install semgrep`; `semgrep scan --config p/python` | 1.180.0; registry **403** (`semgrep.dev`) |
| 10 | `semgrep scan --config $S/sg-rules.yml --metrics off` | 2 phát hiện (DSN mặc định) |
| 11 | `gh api repos/<tool>/releases/latest`; `curl -I github.com/rhysd/actionlint/releases/latest` | 403 (bị chặn) |
| 12 | `GOBIN=$S/bin go install github.com/rhysd/actionlint/cmd/actionlint@latest github.com/zricethezav/gitleaks/v8@latest` | actionlint v1.7.12, gitleaks v8.30.1 (go1.26.9) |
| 13 | `gitleaks git . --redact` / `gitleaks dir . --redact` | 66 commit, 1 leak (E3:182) / 1 leak |
| 14 | `docker pull aquasec/trivy:0.69.3 trufflesecurity/trufflehog:latest zricethezav/gitleaks:v8.30.1 grafana/k6:latest rhysd/actionlint:1.7.12` | Tất cả pull OK từ Docker Hub |
| 15 | `docker run trufflesecurity/trufflehog:3.99.2 git file:///repo --no-verification --json` | 0 verified, 3 unverified |
| 16 | `docker run --network host -e HTTPS_PROXY -e SSL_CERT_FILE=/ca.crt -v ca:/ca.crt aquasec/trivy:0.69.3 image --scanners vuln --severity HIGH,CRITICAL <img>` | Lần đầu không proxy/CA: x509 lỗi; sau đó OK, số liệu §3.7 |
| 17 | `pytest test_tc.py` (testcontainers Mosquitto + paho MQTT5) | Lần 1 **failed** (1745/2000, broker queue mặc định); lần 2 (`max_queued_messages 100000`) **1 passed**, 3701 msg/s |
| 18 | `pytest test_db.py` (testcontainers TimescaleDB + `infra/db/init.sql`) | **1 passed** (4,75 s) |
| 19 | netshoot `tc qdisc add dev eth0 root netem delay 200ms` | **Thất bại**: "Specified qdisc kind is unknown" |
| 20 | netshoot `iptables -A INPUT ... DROP`; `docker pause`; `docker network disconnect` | Timeout 3 s / Reset / Refused |
| 21 | `go install github.com/Shopify/toxiproxy/v2/cmd/{server,cli}@v2.12.0`; toxic latency 200 | CONNECT 7 → 208 → 7 ms |
| 22 | `pip install aiomqtt`; `python loadgen.py 1000 20 18832` | `1000 edges, 19975 msgs, 31972 samples/s over 21.9s` |
| 23 | Node `chromium.launch()` mở 05-domain-model.html; Python `playwright==1.56.0` mở UI-03 | OK, Chromium 141.0.7390.37 |
| 24 | `pytest tests/test_prop.py` (hypothesis 300 ví dụ + schema 07, Draft7) | Lần 1 failed (lỗi test của tôi: sort None; và SchemaError 2020-12); sửa → **3 passed** (cả thư mục) |
| 25 | `actionlint -no-color -oneline` trên workflow mẫu / workflow lỗi cố ý | exit 0 / 2 lỗi đúng (script injection, input `fetch_depth`) |
| 26 | `/home/user/admin/.venv/bin/pip install <gói pin §5>`; `pip check` | No broken requirements found |
| 27 | `.venv/bin/pytest -q -n 4 --timeout 120 demo mutdemo/tests tc -p randomly` | **9 passed** in 7.37s |

Mọi container ném đi (`a3-*`, testcontainers) đã xoá; không đụng stack `emspoc`.
