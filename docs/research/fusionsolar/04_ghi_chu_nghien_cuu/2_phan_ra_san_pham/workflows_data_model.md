# Huawei FusionSolar: Key User Journeys, Workflows and Domain Data Model (reverse-engineering notes, Oct 2026)

Scope: the installer, owner, O&M, reporting and data-ingestion workflows of FusionSolar (SmartPVMS cloud + FusionSolar app + devices), plus the domain data model inferred from them. This builds on `Nền tảng Huawei FusionSolar/api_integration.md` (endpoints, auth, failCodes) and `features_editions.md` (features) without repeating them.

**Label legend.** Every item carries one label:
- **[FACT]**: stated in a cited source.
- **[INFERENCE]**: a reasonable deduction from cited facts.
- **[SPECULATION]**: plausible, but with weak evidence.
- **[UNKNOWN]**: not found.

**Workflow stages.** Each workflow is broken into Trigger → Validation → Business Logic → External Integration → Persistence → Notification → Audit. For each stage the notes give **Observed** (backed by sources), **Likely implementation** (inference or speculation), and **Unknown**.

**Primary source used heavily.** Huawei's own *iMaster NetEco V600R022C00 Northbound Interface Reference-V6 (SmartPVMS)*, Issue 01, 2022-06-16, 143 pages. A copy is in the tijsverkoyen repo: [NBI-V6 PDF](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf). I read the full text. Its enumerations (alarm status, severity, alarm type, plant state, inverter state, battery mode, device types, error codes) are the strongest public evidence of the internal domain model. Note that it predates the 24.x/25.x docs. Huawei support pages (support.huawei.com / support.huawei.cn) returned 403 or were blocked by robots.txt, so I used document mirrors on distributor sites instead.

---

## 1. Installer onboarding: register account → create installer company → company admin adds employees

### Takeaway
Onboarding is company-centric. When the first installer registers, a **company (domain)** is created and that person becomes its administrator. That admin then adds or invites further installers and creates owner accounts. Companies form a hierarchy: level-2 companies have an administrator, and installers at any level manage their own company and the companies below it. Separately, Huawei's Smart PV *Community* site handles personal accounts, company verification and employee linking for incentive programmes.

### Cited Findings
- [FACT] "Creating the first installer account will generate a domain named after the company. The email address is the user name for logging in to the FusionSolar app." More installer accounts are created via "New User" — [FusionSolar App & SUN2000 App User Manual, Issue 07, 2020-05-15](https://www.energlaze.ie/wp-content/uploads/2022/02/FusionSolar-App-and-SUN2000-App-User-Manual-5.pdf)
- [FACT] In the newer app, the first installer registers via "No account?" → "I'm an installer". The system emails the username and initial password. Installers create owner or extra installer accounts from **Home > Plants > Add user**, and the system emails credentials to the address entered — [FusionSolar App User Manual, Issue 01, 2024-02-07](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] Scope rule: installers **assigned to plants** cannot create plants; installers **assigned to the company** can — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] Registering the first installer account also establishes the company account. More installers are added via "Add User" or "Invite User", depending on region. Login works with email or username, and the system forces a password change at first login — [FusionSolar App Quick Guide, Issue 09, 2023-12-22](https://doe-duurzaam.nl/wp-content/uploads/2025/06/FusionSolar-App-Quick-Guide.pdf)
- [FACT] There are three account categories: **Administrator user, Installer user, Owner user**. Company hierarchy: "Level-2 companies (with administrator) and level-3+ (no administrator)". "Installers at each level can manage and maintain the current and lower-level companies and users." — [FusionSolar SmartPVMS 7.0 After-sales Technical Training Slides](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Community-site path: register a personal account (pick a country), then create a company account from the "Registration & Verification" tab. Company Administrators "manage employee FusionSolar accounts", and employee accounts link to the company after approval. Changing country deletes points, certificates and personal info on the current site — [Huawei Solar FAQ](https://solar.huawei.com/en/faqs)
- [FACT] Northbound API accounts are another kind of user. A company admin creates them under System > Company Management > Northbound Management, setting a system name, deadline, username, password, interface list, and bound plants/devices. (The 2022 path was "System > Business Configuration > Northbound Management".) — [NBI-V6 PDF §1.3](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf); [Solytic KB](https://kb.solytic.com/en/knowledge/set-up-api-key-huawei-fusionsolar)

### Inferences
**Workflow 1: Installer onboarding**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | Self-registration in app ("I'm an installer") or on the web; admin "Add user"/"Invite user" [FACT] | Two entry points: self-service company creation and an admin-driven invitation | Whether self-registered companies need Huawei/distributor approval (the Community site says employee links need "approval") |
| Validation | Email used as username; forced password change at first login [FACT] | Email uniqueness per region/tenant; email verification code; password policy (8–32 chars is documented for NB accounts only) [INFERENCE] | Exact password policy for portal users; CAPTCHA (web scrapers report one: [fusion_solar_py](https://pypi.org/project/fusion-solar-py/0.0.22)) |
| Business logic | First user → company "domain" + admin role; hierarchy of sub-companies; scope = company vs. plant assignment [FACT] | Tenant = company tree (materialized path or closure table); RBAC role + data scope (company subtree or explicit plant list) [INFERENCE] | Full role list (e.g. separate "O&M engineer", "viewer" roles) |
| External integration | Region-specific portals (`intl`, `eu5`, `uni00Xeu5` hosts) [FACT, see api_integration.md] | Region chosen at registration pins the tenant to a regional data centre (EU data is on Open Telekom Cloud — [Huawei EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)) [INFERENCE] | Whether the Community-site account and the FusionSolar account share one identity provider |
| Persistence | Company, user, role, scope [INFERENCE] | `company(id, parent_id, level, name, admin_user_id, region)`; `user(id, email, phone, company_id, type)`; `user_scope` | — |
| Notification | Credentials or initial password emailed to the new user [FACT] | Templated transactional email | SMS option |
| Audit | — | Operation log of user creation [SPECULATION] | Any public description of the portal's operation/audit log |

- [INFERENCE] For the equivalent product, model **Company (tree) → User → Role + DataScope**, with a separate **ApiClient** principal (Northbound account or OAuth client) that has its own expiry, interface allow-list and plant/device bindings.

### Gaps
- [UNKNOWN] The official 25.x role catalogue and permission matrix. The installer user manual (EDOC1100462190 / EDOC1100515204) was not fetchable (403/robots).
- [UNKNOWN] Whether the company needs a business licence or VAT check, and whether a distributor approval step exists.
- [UNKNOWN] Session timeout, MFA, and SSO for installer accounts.

---

## 2. Plant creation & device commissioning on site

### Takeaway
Commissioning is **app-led and local-first**:
1. Scan the device QR code (SN plus the device WLAN credentials).
2. Join the inverter's or EMMA's own WLAN hotspot.
3. Log in locally as "Installer".
4. Run **Quick Settings**: grid code, time sync, router/4G networking, management-system domain/port, ESS working mode, meter, and power adjustment.
5. Add sub-devices (battery, meter, optimizers) and build the physical layout from photos of the optimizer SN labels.
6. Create a new plant or "Connect to existing plant", setting name, address/location, time zone, string capacity, and prices (currency, purchase price, feed-in tariff).
7. Invite or create the owner.

The dongle/inverter then registers with the cloud at the management-system domain (e.g. `intl.fusionsolar.huawei.com`, port 27250).

### Cited Findings
- [FACT] Quick Settings start automatically at first login. The steps are: scan the inverter QR code → connect to the router via WLAN or Ethernet (DHCP by default) or 4G (APN "Automatic" by default) → **set grid code (default "N/A")** → enable/disable phone time sync → configure the management system domain **"intl.fusionsolar.huawei.com" (Port: 27250)**. In cascade scenarios you upload an SN file to search for cascaded inverters. For battery setups you choose an "ESS Installation Environment" and the working mode. Physical layout: stick the optimizer SN labels on a template, photograph it, and upload; the system generates the layout — [FusionSolar App Quick Guide, Issue 09, 2023-12-22](https://doe-duurzaam.nl/wp-content/uploads/2025/06/FusionSolar-App-Quick-Guide.pdf)
- [FACT] Wizard path: **Home > Plants > "Setup wizard"** → scan the device QR code → connect to the device WLAN, whose SSID ends in the last six digits of the SN → log in as Installer (initial password "Changeme") → Quick Settings (router parameters; Device Management; Main Circuit Breaker Capacity; Meter Connection Mode; Charger Maximum Power; ESS Working Mode; Communications Networking) → **Connection Test** (device communication and WLAN signal strength) → Finish → connect the devices to a plant — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] Two ways to add devices: (1) in the Setup Wizard, scan → "Connect to existing plant" → choose the plant; (2) **Me > Plant management > target plant > Add devices > scan QR > Save**. When several installers are involved, "the owner may need to unbind/delete [the] device from one plant before rebinding to another" — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] Physical layout, automatic: upload photos of the optimizer SN labels and image recognition does the rest. Manual: add inverters and PV modules, adjust position, azimuth and tilt, and bind optimizers to modules 1:1 or 1:2 — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] Plant fields named in the manual: plant name, location/address (GPS by default), capacity, time zone, currency, and electricity prices "purchase price" and "feed-in tariff" (Tables 6-2, 6-3). Grid-connection date is not shown in the commissioning steps — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf). The 7.0 training lists the plant-creation steps as: plant information (with **mandatory authorization confirmation**), access devices (QR scan or SN entry), string capacity (batch setting supported), electricity prices (feed-in tariff and purchase price), address, and time zone — [SmartPVMS 7.0 training slides](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf). The older app gets the "current GPS coordinates by default" — [App Manual 2020](https://www.energlaze.ie/wp-content/uploads/2022/02/FusionSolar-App-and-SUN2000-App-User-Manual-5.pdf)
- [FACT] "A device qualifies only if the product SN is bound to the FusionSolar account". Path: "Setup Wizard > Scan to Create Plant > Add Plant or Connect to Existing Plant" — [Huawei Solar FAQ](https://solar.huawei.com/en/faqs)
- [FACT] Grid code: "Set this parameter based on the grid code of the country or region where the inverter is used and the inverter application scenario". Export limitation offers "Total power" (at the grid-tied point) or single-phase limitation. The closed-loop controller is either Inverter or SDongle/SmartLogger. "Add/Delete device" adds power meters, batteries, optimizers and safety shutdown boxes — [App Manual 2020](https://www.energlaze.ie/wp-content/uploads/2022/02/FusionSolar-App-and-SUN2000-App-User-Manual-5.pdf)
- [FACT] Export limitation path: **Power Adjustment > Grid-tied point control > Active Power**. Modes: "Unlimited", "Grid connected with zero power", and limited via "Maximum grid feed-in power". Closed-loop controller: "Inverter only" for a single unit, "S-Dongle/Smartlogger" for cascaded units. Restriction mode: Total power or Single-phase power. A smart meter on the inverter COM port is **mandatory**, added under Device Maintenance from the compatibility list — [Photomate KB](https://photomate.zendesk.com/hc/en-gb/articles/5701625507485-Export-limit-for-SUN2000-inverters-using-FusionSolar-app)
- [FACT] The installer marketing page lists automatic device discovery from one QR scan of the inverter or EMMA, one-click layout sync from SmartDesign, automatic time sync, and detection of connection problems — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer)
- [FACT] The NB plant list exposes `buildState` (0 not constructed, 1 under construction, 2 grid-connected) and `combineType` (1 utility, 2 C&I, 3 residential). The sample responses contain `"buildState":"3"`, a value outside the documented enum — [NBI-V6 §6.1.3](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)

### Inferences
**Workflow 2: Plant creation and commissioning**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | Installer taps Setup wizard and scans the device QR [FACT] | QR payload carries the SN plus the device WLAN SSID/key [INFERENCE from "SSID ends with last 6 SN digits"] | Exact QR payload format |
| Validation | Local device login (Installer / "Changeme"); Connection Test; SN must be bound to the account; grid code must be set (default N/A); meter required for export limit [FACT] | Cloud checks that the SN exists in the factory/ESN registry, is not bound to another plant, and that the user has scope over the target plant [INFERENCE]; rebinding requires an owner or previous-installer unbind [FACT/INFERENCE] | Server-side SN whitelist/anti-theft rules |
| Business logic | Quick Settings write device parameters locally (grid code, time, networking, ESS mode, power control); layout built from photos; plant creation with prices and time zone [FACT] | Two-phase model: (a) local Modbus/proprietary writes to the device, (b) cloud plant record plus device binding; the device later registers to `domain:27250` and the cloud links it by SN [INFERENCE] | Protocol on port 27250 (Huawei proprietary over TLS?) [UNKNOWN] |
| External integration | SmartDesign layout import; maps (Google/Baidu/Amap/Tencent listed as public URLs — [Huawei doc](https://info.support.huawei.com/DpinfoAppDoc/pre_erp_slice_00/doc/owner/pv_ess/en/en-us_topic_0000002307817397.html)) [FACT] | Image-recognition service for SN labels [INFERENCE] | — |
| Persistence | Plant (name, address, lat/long, capacity, time zone, currency, prices, build state, grid type), device binding, layout [FACT/INFERENCE] | `plant`, `device(sn, plant_id, parent_device_id)`, `pv_string(capacity)`, `layout_module(x, y, azimuth, tilt, optimizer_sn)`, `tariff` [INFERENCE] | Whether parameter changes made locally are mirrored to the cloud as a config snapshot |
| Notification | Owner invite / account creation email [FACT] | — | Installer notified when a device first comes online |
| Audit | "Mandatory authorization confirmation" when creating a plant [FACT] | Consent record (owner authorizes the installer to manage plant data) [INFERENCE] | Commissioning report/export (there is a log export: Me > About > Log Export) |

- [INFERENCE] Design the commissioning backend so the app can work offline on the device hotspot and sync to the cloud afterwards. Plant creation and device binding are cloud calls made once the phone is back on mobile data.
- [SPECULATION] Port 27250 suggests a custom device↔cloud protocol rather than MQTT 8883 or HTTPS 443.

### Gaps
- [UNKNOWN] The exhaustive "Create plant" field list in the 25.x portal: grid-connection date, contact, plant type, owner email, and whether "plant ID" is user-defined. `gridConnectionDate`/`gridConnectionTime` could not be confirmed in any public field list.
- [UNKNOWN] The device↔cloud protocol on port 27250.
- [UNKNOWN] The grid-code catalogue structure (an enum per firmware?). There is a public "grid code update" download — [Huawei doc](https://info.support.huawei.com/DpinfoAppDoc/pre_erp_slice_00/doc/owner/pv_ess/en/en-us_topic_0000002307817397.html).

---

## 3. Owner journey

### Takeaway
The owner joins through an invitation email or registration link, or an account the installer creates. They monitor energy flow and statistics, choose the battery working mode (Maximum self-consumption / Fully fed to grid / TOU), control the SCharger (start/stop, schedules, "Charging for the Next Trip", sharing the charger), and share a read-only Kiosk link. The owner also controls **consent**: O&M authorization for the installer, API permission (since Sep 2025), and OAuth app authorization with revoke.

### Cited Findings
- [FACT] After commissioning, the owner can "Register an account" via an invitation link, or the installer uses "Invite a user" (region-dependent) — [Quick Guide Issue 09](https://doe-duurzaam.nl/wp-content/uploads/2025/06/FusionSolar-App-Quick-Guide.pdf). The installer initiates the invitation, and the owner receives an email and registers — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] Owner home screen: PV yield, battery (SOC, charge/discharge), charger status. The energy-flow diagram shows real-time power direction (PV → loads, grid, battery). The Statistics tab shows yield, consumption, self-consumption rate and revenue — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] "Live data" button: it refreshes PV, grid, load and ESS power. "By default, the function is enabled for 1 minute each time. The function can be enabled for a maximum of 10 times per plant per day". On 4G, at most 3 MB of traffic per month — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] App ESS modes (Table 6-1): **"Maximum self-consumption"**, **"Fully fed to grid"**, **"TOU"** (manual charge/discharge time segments, with grid charging allowed in charge periods) — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] The NB data model enumerates the battery `ch_discharge_model` as 0 none, 1 forced charge/discharge, 2 time-of-use price, 3 fixed charge/discharge, 4 automatic charge/discharge. `battery_status` is 0 offline, 1 standby, 2 running, 3 faulty, 4 hibernating — [NBI-V6 §6.2.6](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] EV charger in the app: start/stop; Bluetooth authentication (auto-start when the phone is near); RFID card (pre-added); plug-and-play; scheduled charging; "Charging for the Next Trip" (set the trip time and kWh, and EMMA schedules the window). The owner can share the charger with registered users. A shared user registers via "Registering a Shared Account" and can start/stop and set the connector locking mode — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf); [Huawei SCharger page](https://solar.huawei.com/ie/products/SCharger-7KS-S0-22KT-S0/)
- [FACT] Owner authorizations to the installer: device parameter settings on some devices, and an **"O&M Authorization" toggle** — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf). API permission: Me > Power plant management > Basic info > Set permissions > API access (app 25.2.101.001), or the key icon under Plant management on the web — [tijsverkoyen issue #262](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/262); [HA community](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417)
- [FACT] Third-party sharing goes through OAuth. The owner directs the third party to register as an OAuth client, and can revoke under **Me > Settings > Account Security > Authorization Management > Revoke** — [Huawei EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)
- [FACT] Kiosk: "Owner users can share the plant running information in the Kiosk view. Other users can access the Kiosk view without logging in" — [SmartPVMS 7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf). The URL is valid for 1 year and data updates every 10 min. Endpoint `GET /rest/pvms/web/kiosk/v1/station-kiosk-file?kk=<id>` — [tijsverkoyen README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)

### Inferences
**Workflow 3a: Owner changes battery mode**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | Owner picks a mode in the app; or a third party calls `/rest/openapi/pvms/nbi/v1/control/battery/mode/async-task` [FACT, api_integration.md] | Same command service behind the app and the API [INFERENCE] | — |
| Validation | NB error codes: DOD 0–100 (20039), target SOC (20042), duration (20043), task ID (20044/20048), forced power (20047), unauthorized plant (20045/20046) [FACT, NBI §8] | Range checks against device capability; one pending task per plant ("do not call repeatedly before a task is complete") [FACT/INFERENCE] | Per-model capability matrix |
| Business logic | Async task → delivered to the communication device (Dongle/EMMA/SmartLogger) [FACT] | Command queue with states (created → delivered → succeeded/failed/timeout) [INFERENCE] | Retry/timeout values |
| External integration | Device Modbus register 47086 = battery working mode (locally) [FACT, api_integration.md] | The cloud sends the parameter write over the device-cloud channel, and the dongle writes the Modbus register [INFERENCE] | — |
| Persistence | Task-info query API exists [FACT] | `control_task(id, plant_id, type, params, status, requested_by, created_at, finished_at, result_code)` [INFERENCE] | Retention of task history |
| Notification | — | In-app result toast [SPECULATION] | — |
| Audit | 20049 "Failed to deliver the charging and discharging task" [FACT] | Operation log entry per control command [INFERENCE] | Owner-visible history |

**Workflow 3b: Kiosk share and installer/API authorization**
- [INFERENCE] Kiosk = a per-plant **share token** (`kk`) with a fixed 1-year expiry, read-only, served as a cached JSON snapshot refreshed about every 10 minutes. Model it as `share_link(token, plant_id, created_by, expires_at, revoked_at)`.
- [INFERENCE] Authorizations form a **consent ledger** keyed by (plant, grantee, scope): grantees are installer company, API account, or OAuth client; scopes are O&M, param-settings, API, or OAuth-scopes. Revocation is immediate, but propagation took about 30 min in practice ("wait about 30 min" — [issue #262](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/262)), which hints at a cached permission service.

### Gaps
- [UNKNOWN] Whether the owner can generate or revoke a kiosk link in the app or only on the web, and whether the 1-year expiry is configurable.
- [UNKNOWN] Data fields of a charging session (energy, start/end, auth method, user). Huawei states only that "charger alarms and usage data" are retained for 6 months — [EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act).
- [UNKNOWN] Whether a plant can have several owner accounts or family members beyond charger sharing.

---

## 4. Monitoring & alarm handling

### Takeaway
Devices raise alarms "on trigger". The cloud stores each alarm with a **severity** (1 critical, 2 major, 3 minor, 4 warning), an **alarm type** (1 transposition signal, 2 exception alarm, 3 protection event, 4 notification status, 5 alarm information), a localized **name, cause and repair suggestion** keyed by `alarmId`+`causeId`, and a **six-state lifecycle** that ties alarms to tickets: 1 active → 2 acknowledged → 3 being handled (defect-elimination ticket) → 4 handled; 5 cleared by user; 6 cleared automatically by the device. Notifications are configured as **push rules** (email + app). The cloud also derives a plant health state (1 disconnected, 2 faulty, 3 healthy).

### Cited Findings
- [FACT] `getAlarmList` returns `stationCode, stationName, alarmName, devName, repairSuggestion, esnCode, devTypeId, causeId, alarmCause, alarmType, raiseTime (ms), alarmId, lev, status`. Filters: `stationCodes, beginTime, endTime, language` (mandatory), plus optional `status, levels, devTypes, types, devName`. Limit: Roundup(plants/100) calls per 30 minutes. It returns "current (active) alarm information" — [NBI-V6 §6.1.7](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] Status enum: 1 not processed (active); 2 acknowledged (by the user); 3 being handled (transferred to a defect elimination ticket); 4 handled (defect handling has ended); 5 cleared (by the user); 6 cleared (automatically by the device). Severity `lev`: 1 critical, 2 major, 3 minor, 4 warning. Alarm types: 1 transposition signal, 2 exception alarm, 3 protection event, 4 notification status, 5 alarm information — [NBI-V6 §6.1.7](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] Sample alarm: `alarmId 2064, "The device is abnormal.", alarmType 2, causeId 5, lev 2, status 1, devTypeId 38, esnCode, raiseTime 1667179861000, repairSuggestion "Turn off the AC and DC switches, wait for 5 minutes…"`. A second sample (`alarmId 3011` "Battery expansion module undervoltage", `causeId 2`, `lev 4`) has a suggestion with placeholders "[CNo]…[SNo] (in the fault location information)" — pyhfs 0.1.1 test fixture `getAlarmList.json`, [PyPI](https://pypi.org/project/pyhfs/)
- [FACT] Plant real-time KPI `real_health_state`: 1 disconnected, 2 faulty, 3 healthy — [NBI-V6 §6.2.1](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] Inverter state enum (`inverter_state`), excerpt: 0–3 standby substates; 256 start; 512 grid-connected; 513 power limited; 514 self-derating; 768 shutdown on fault; 769 on command; 770 OVGR; 771 communication interrupted; 772 power limited; 773 manual startup required; 774 DC switch disconnected; 1025/1026 grid scheduling cosφ-P / Q-U; 1280/1281 terminal test; 1536 inspection; 1792 AFCI self-check; 2048 I-V scanning; 2304 DC input detection; 40960 standby no irradiation; 45056 communication interrupted (written by SmartLogger); 49152 loading — [NBI-V6 Table 6-1](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] In the app, active alarms show on the plant overview and under **Maintenance > Alarms**, with cause, handling suggestions and timestamp. Actions: **create defect elimination ticket, acknowledge, clear** (when the fault is fixed but not auto-cleared) — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf). The older app had "Alarm management" (active + historical alarms) and "Clear alarms" for historical alarms on the inverter — [App Manual 2020](https://www.energlaze.ie/wp-content/uploads/2022/02/FusionSolar-App-and-SUN2000-App-User-Manual-5.pdf)
- [FACT] The portal shows active alarms in four severities (Critical, Major/Severe, Minor, Warning) — [VP Solar](https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/). The 7.0 training mentions "Real-time alarm push and troubleshooting suggestions", a "Plant Alarm Center", and a New Ticket form (file upload, defect description, designated owner, handling suggestion) — [SmartPVMS 7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Notification rules: **Push Settings > Add** rule → Save. An Installer account is required. "The alarm push rule takes effect only for newly reported alarms". At most **1000** rules per system. Rules can be enabled/disabled, deleted, and exported/imported in bulk. Email alarm times use the server time zone — [Photomate KB "Configuring Alarm Email and App Notification Rules"](https://photomate.zendesk.com/hc/en-gb/articles/4630117770909-Configuring-Alarm-Email-and-App-Notification-Rules)
- [FACT] App push notifications cover faults and grid outages — [solaranlage-tipps.de, Jun 2026](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026). Alarm data is generated "on trigger" and is under 1 KB/day per device — [Huawei EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)
- [FACT] Alarm text is localized in 10 languages via the `language` parameter (zh_CN, en_US, ja_JP, it_IT, nl_NL, pt_BR, de_DE, fr_FR, es_ES, pl_PL) — [NBI-V6 §6.1.7](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)

### Inferences
**Workflow 4: Alarm lifecycle**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | The device raises an alarm event "on trigger" (alarmId + causeId + fault location info) [FACT] | Dongle/SmartLogger forwards the event immediately rather than in the 5-min batch [INFERENCE] | Transport latency |
| Validation | — | Dedup on (device SN, alarmId, causeId, raise time); drop if the device is unbound [INFERENCE] | — |
| Business logic | Severity and type come from a catalogue; name, cause and suggestion are localized per language; placeholders such as [CNo]/[SNo] are filled from location info [FACT] | **Alarm catalogue** table `(alarmId, causeId, devType, lev, type, i18n name/cause/suggestion)` joined at query time; plant health is recomputed from active alarms and comm state [INFERENCE] | Whether severity can be overridden per company |
| External integration | Email + app push via rules [FACT]; NB pull `getAlarmList` (no webhook) [FACT] | Push via Huawei Push Kit / APNs / FCM [SPECULATION] | SMS channel |
| Persistence | Six-state status; tickets linked (state 3/4) [FACT] | `alarm(id, plant_id, device_id, alarm_id, cause_id, lev, type, status, raise_time, ack_time, ack_by, clear_time, clear_by, clear_type(user/device), ticket_id, location_info)` [INFERENCE] | Retention of historical alarms (charger alarms: 6 months [FACT]; others unknown) |
| Notification | Rule-based; only new alarms; server time zone [FACT] | Rule = (scope: plants/company, severities, device types, recipients, channels, enabled) [INFERENCE] | Recovery (clear) notifications; escalation; quiet hours |
| Audit | Statuses distinguish "by the user" and "automatically by the device" [FACT] | Store actor and timestamp per transition [INFERENCE] | Portal audit-log UI |

- [INFERENCE] The lifecycle is effectively two orthogonal flags folded into one enum: *acknowledgement/handling* (1→2→3→4) and *clearance* (5 user, 6 device). A clean redesign would use separate `ack_state`, `handling_state` (ticket) and `clear_state` fields.
- [INFERENCE] `alarmId` identifies the alarm *type* in the catalogue, not the occurrence; both samples reuse catalogue IDs. The occurrence has no exposed unique ID in the NBI, so integrators must build a composite key (`esnCode`, `alarmId`, `causeId`, `raiseTime`).

### Gaps
- [UNKNOWN] Exact push-rule fields (severity filter, delay, recipients) — not in the public KB text.
- [UNKNOWN] Whether the cloud generates its own alarms (e.g. "plant disconnected", low-yield/PR anomaly) beyond device alarms. The `real_health_state = disconnected` suggests at least comm-loss detection [INFERENCE].
- [UNKNOWN] Alarm masking/suppression and alarm-storm handling.

---

## 5. O&M: remote parameters, firmware upgrade, Smart I-V diagnosis, tasks/work orders

### Takeaway
O&M features are: per-device **remote parameter settings** (model-dependent); **remote/batch firmware upgrade** (Huawei claims up to 50,000 devices with selective upgrade); **Smart I-V Curve Diagnosis** as a task (select plants/strings, cleaning status, environment parameters, 128-point scans, result codes, xls/pdf export); **remote switch on/off**; and a **task module** with *defect elimination* and *inspection* tickets that is linked to alarms.

### Cited Findings
- [FACT] Remote parameter path: **Devices > select device > :: > Parameter settings > modify > Confirm**. "Parameters that can be set vary with device model" — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf). "Users can remotely modify device configuration parameters"; batch setting is listed "to be implemented"; parameters are grouped for filtering — [SmartPVMS 7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] App "Upgrade device" upgrades the software of inverters, batteries and optimizers. Warning: "Delivering a restart, factory reset, shutdown, or upgrade command to the solar inverters may cause power grid connection failure." — [App Manual 2020](https://www.energlaze.ie/wp-content/uploads/2022/02/FusionSolar-App-and-SUN2000-App-User-Manual-5.pdf). "Batch upgrade of up to 50,000 devices with selective upgrade" — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer). The 2024 app manual also has "Upgrading the Charger Software Version" — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] NB error codes reveal server-side operations that the public V6 doc does not otherwise describe. Upgrade: 20020 "upgrade package corresponding to the device version cannot be found", 20021 "upgrade file does not exist", 20022 "upgrade records of the devices … not found". Switch: 20019 "1 and 2 indicate switch-on and switch-off". Batch: 20018 "A maximum of 10 devices can be operated at a time". I-V: 20030 "Failed to create the I-V curve diagnosis task", 20034 "task does not exist", 30009 `taskName`, 30010 `nds`, 30011 `cleanStatus`, 30012 `environmentalParameters`, 30013 `modulePlaneIrradiance`/`moduleBackSurfaceTemperature` required when environmentalParameters=1, **30014 `scanPointNum` must be 128**, 30019 back-surface temperature in [0.0, 100.0], **30020 irradiance in [600.0, 1500.0]**, 30017 `dns` ≤ 100 devices with permission. MPPT backfeed: 20035–20037 (current range (0, 15]), 30024–30028 (≤3 MPPTs per inverter, ≤32 per task) — [NBI-V6 §8 Error Code List](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] I-V (FusionSolar 6.0 manual). Path: **Intelligent O&M → Intelligent Diagnosis → Settings**, where you configure string parameters (string capacity = module rated power × number of modules, voltage, current). Then **New Task** → **Start Scanning** with fields Task Name; Select Device (**max 20 PV plants** per task); Component Cleaning; Environment parameter (automatic or manual irradiance/temperature). Conditions: sunny, stable, **≥600 W/m²**, clean dry modules, consistent cleaning status, same module type. The scan takes <1 s per string with **128 points**, 0.5% precision, and no shutdown needed. Rescan only ≥2 min after the last scan. Result IDs: 10000 normal, 10002 open circuit, 10005 current mismatch, 10006 abnormal module output, 10008 voltage abnormal, 10009 low Isc, 10010 low power, 10016 low parallel resistance, 10018 slight current mismatch, 10019 abnormal MPP curve, 10020 high series resistance. Export: fault list as **.xls**, string I-V comparison as **.pdf** — [FusionSolar 6.0 Smart I-V Curve Diagnosis User Manual](https://storage.googleapis.com/gator-users/user-510000/documents/2700a7434ade4853a8317f7870adf089/FusionSolar%206.0%20Smart%20PV%20Management%20System%20Smart%20I-V%20Curve%20Diagnosis%20User%20Manual.pdf)
- [FACT] The 7.0 I-V workflow: Smart Diagnosis > I-V Curve → Configure Strings → Add Diagnosis Task → Start I-V scanning. Requirements state the irradiance lower limit as **400 W/m²** — [SmartPVMS 7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf). This conflicts with the 600 W/m² in the 6.0 manual and the [600, 1500] API range. The threshold most likely changed between versions [INFERENCE].
- [FACT] Tasks. **Defect elimination**: Maintenance > Tasks > + > Defect elimination, with statuses *To be dispatched → In Elimination → To be approved*; the handler submits a description and result, and the creator approves. **Inspection**: Maintenance > Tasks > + > Inspection, with statuses *Not started → Inspection in progress → To be confirmed → Terminated*; the inspector fills in an inspection report — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] The inverter states include 2048 "I-V scanning" and 1792 "AFCI self-check", so the device reports when a diagnosis is running — [NBI-V6 Table 6-1](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] The SmartLogger3000 manual has sections "6.7.4.1 Upgrading the Device Firmware Version", "6.8.2 Setting Active Power Control" and "6.8.5 Setting Export Limitation Parameters" — [SmartLogger3000 User Manual Issue 20, 2024-04-15](https://ske-solar.com/productdata/SmartLogger/02_Manuals/UserManual_SmartLogger3000_V20_2024-04-15_EN.pdf)

### Inferences
**Workflow 5a: Remote parameter change / remote control**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | Installer edits parameters in the app/portal; owner toggles; API control task [FACT] | — | — |
| Validation | Model-dependent parameter set; owner "O&M Authorization"/param-setting consent; ≤10 devices per operation (20018) [FACT] | Parameter metadata per model and firmware (type, range, unit, group, write-permission level) [INFERENCE] | Whether a second approval exists for risky parameters (grid code) |
| Business logic | Grid-impact warning for restart/reset/shutdown/upgrade [FACT] | Command → device-cloud channel → dongle → Modbus write → read-back verification [INFERENCE] | — |
| Persistence | Async task + task-info API [FACT] | `device_command(id, device_id, type, payload, status, result, issued_by)` [INFERENCE] | Config snapshot history |
| Notification/Audit | — | Operation log [INFERENCE] | — |

**Workflow 5b: Batch firmware upgrade**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | Installer selects devices (up to 50k) [FACT] | Upgrade job wizard: select package/target version → select devices → schedule [INFERENCE] | Whether scheduling (e.g. night window) is supported |
| Validation | Package must match the device version (20020); file must exist (20021) [FACT] | Compatibility matrix (model × current version → target package) [INFERENCE] | Owner consent requirement |
| Business logic | Selective upgrade [FACT] | Job → per-device sub-tasks with state (waiting, downloading, upgrading, success, failed); dongle downloads the package and pushes it to inverters/batteries/optimizers [INFERENCE] | Concurrency/throttling rules |
| Persistence | "Upgrade records of the devices" exist (20022) [FACT] | `upgrade_job`, `upgrade_task(device_id, from_ver, to_ver, status, error)`; device `softwareVersion` updated afterwards [INFERENCE] | — |
| Notification/Audit | — | Job completion summary [SPECULATION] | — |

**Workflow 5c: Smart I-V diagnosis**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | New Task (≤20 plants, or ≤100 devices via API) [FACT] | — | Scheduled/periodic scans |
| Validation | Irradiance [600, 1500] W/m² (or ≥400 in 7.0), temperature [0, 100] °C, scanPointNum = 128, cleaning status, string config correct; permission to run I-V [FACT] | Pre-check of current irradiance from the EMI device (devTypeId 10) or manual entry [INFERENCE] | Licence model (C&I/utility; SmartLogger licence?) |
| Business logic | Inverter scans each string in <1 s; result codes 10000–10020 [FACT] | Server-side curve analysis/classification (four defect families at >90% accuracy per marketing — [Huawei C&I PVMS](https://solar.huawei.com/fr/products/ci-smart-pv-management-system/)) [INFERENCE] | Whether classification runs on the inverter or in the cloud |
| Persistence | Task, per-string results, curves [FACT/INFERENCE] | `iv_task(id, name, plants, clean_status, env_params, status)`, `iv_result(task_id, string_id, result_code, curve[128 points])` [INFERENCE] | Retention |
| Notification | — | Report available [SPECULATION] | — |
| Export | .xls fault list, .pdf string comparison [FACT] | — | — |

**Workflow 5d: Defect elimination ticket**
- [INFERENCE] Alarm → ticket linkage: creating a ticket from an alarm sets alarm status 3, and closing or approving the ticket sets status 4 ([NBI enum](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf) plus the [app task statuses](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)). Ticket fields: description, attachment, assignee ("designated owner"), handling suggestion, result, approver.

### Gaps
- [UNKNOWN] Upgrade package distribution (Huawei-hosted catalogue vs. installer upload), rollback, and staged-rollout rules.
- [UNKNOWN] Whether inspection tasks use templates/checklists, and SLA timers on tickets.
- [UNKNOWN] The I-V licensing model in the 24.x/25.x cloud editions.

---

## 6. Reporting

### Takeaway
Reports are **Plant / Inverter / PCS / Battery** reports at day, month, year and lifetime granularity, with **export** and **email subscription**. The underlying plant aggregates are exactly the NB hour/day/month/year KPI sets: yield, irradiation, theoretical yield, PR, feed-in, consumption, revenue, specific yield, CO2, coal and trees. Export formats for energy reports are not confirmed publicly. I-V exports are .xls/.pdf, and the on-prem NetEco1000S stores 25 years of data as CSV.

### Cited Findings
- [FACT] Report Management offers Plant, Inverter, PCS and Battery reports by day/month/year, with the ability to "subscribe to and export reports" — [SmartPVMS 24.2.0 User Manual](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report). The 7.0 training lists Plant, Inverter and Battery reports by day/month/year/**lifetime**, "Subscribe to reports by email and export reports"; the format is not specified — [SmartPVMS 7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Plant KPI keys by granularity:
  - **Real-time**: `day_power, month_power, total_power, day_income, total_income, real_health_state`.
  - **Hourly**: `radiation_intensity, theory_power, inverter_power, ongrid_power, power_profit`.
  - **Daily/Monthly/Yearly**: `installed_capacity, radiation_intensity, theory_power, performance_ratio, inverter_power, ongrid_power, use_power, power_profit, perpower_ratio, reduction_total_co2, reduction_total_coal, reduction_total_tree`.
  - Revenue is in "the currency specified in the management system".
  - Source: [NBI-V6 §6.2.1–6.2.5](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] Device-level aggregates (daily/monthly/yearly): inverters (1, 38) have `installed_capacity, product_power, perpower_ratio`; residential battery (39) has `charge_cap, discharge_cap, charge_time, discharge_time`; C&I ESS (41) has `charge_cap, discharge_cap`. Endpoints: `getDevKpiDay`, `getDevKpiMonth`, `getDevKpiYear`, `getDevFiveMinutes` — [NBI-V6 §3.3, §6.2.9–6.2.11](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf). *(This closes the "device day/month/year endpoint names" gap in api_integration.md.)*
- [FACT] Aggregation semantics: the backend works out the day (or month) from `collectTime` "and the time zone where the plant is located", returning n ≤ 24 hourly records or n ≤ 31 daily records — [NBI-V6 §6.1.4.2–6.1.4.3](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] Sample daily record: `inverter_power 18330, ongrid_power 623, use_power 231, power_profit 3432, performance_ratio 89, perpower_ratio 0.727, theory_power 659.36, radiation_intensity 0.6968, installed_capacity 252, reduction_total_co2 18.275…`. Real-time KPI values come back as **strings** (`"day_power":"17543"`) while day KPIs are numbers — pyhfs 0.1.1 fixtures, [PyPI](https://pypi.org/project/pyhfs/)
- [FACT] App statistics: energy per hour/day/month/year, revenue at the same intervals, and lifetime — [App Manual 2020](https://www.energlaze.ie/wp-content/uploads/2022/02/FusionSolar-App-and-SUN2000-App-User-Manual-5.pdf). NetEco1000S (utility) stores up to 25 years of data as CSV — [Huawei India Utility](https://solar.huawei.com/in/utilityscale)
- [FACT] Meter (17) real-time keys include TOU register splits: `positive_active_peak/power/valley/top` and `reverse_active_peak/power/valley/top` (peak/shoulder/off-peak/sharp) — [NBI-V6 §6.2.6](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)

### Inferences
**Workflow 6: Scheduled report**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | User exports on demand, or subscribes [FACT] | Cron per subscription (daily/monthly), evaluated in the plant/user time zone [INFERENCE] | Subscription frequency options |
| Validation | — | Scope check on the selected plants [INFERENCE] | Max plants per report |
| Business logic | Reports read pre-aggregated hour/day/month/year KPIs [FACT/INFERENCE] | Revenue = Σ(energy × tariff) per period, stored as `power_profit` at aggregation time, so tariff changes are not retroactive [SPECULATION] | Whether tariff changes recompute history |
| External integration | Email [FACT] | Attachment (xlsx) or link [SPECULATION] | Format |
| Persistence | — | `report_subscription(id, owner_user, report_type, granularity, plants, recipients, schedule, format)` [INFERENCE] | — |
| Notification/Audit | Email delivery [FACT] | — | — |

- [INFERENCE] `buy_power`/grid import and `self_use_power` do not exist in the 2022 V6 plant KPI set; `use_power` (consumption) and `ongrid_power` (feed-in) are present. Newer 24.x/25.x versions may have added import and self-consumption keys; the app does show self-consumption rate and grid import. This is unconfirmed.
- [INFERENCE] Units are inconsistent: `capacity` in `getStationList` is documented in **MW**, while `installed_capacity` in KPIs is in **kW**, and `performance_ratio` is labelled "kWh" while the sample value 89 looks like a %. A clean-room design should normalize units explicitly.

### Gaps
- [UNKNOWN] Report export formats (xlsx/csv/pdf) for energy and revenue reports. A YouTube tutorial "How To Export Reports on FusionSolar" exists, but I did not view it — [YouTube](https://www.youtube.com/watch?v=B2uvQBbqKaY).
- [UNKNOWN] Subscription options (frequency, recipients outside the company, attachment vs. link).
- [UNKNOWN] Custom/ad-hoc report builder.

---

## 7. Data ingestion, cadence, offline recovery and retention tiers

### Takeaway
Devices sample statistics **every 5 minutes**, while alarms are sent on trigger. The site gateway (Dongle/EMMA/SmartLogger) uploads to the management-system domain, e.g. port 27250. After an outage, the SmartLogger has a **data recovery** function: hourly data is summarized at the 5-minute mark of the next hour, recovery completes within 24 h, and day/month/year aggregates are recalculated nightly at **02:00**. On the device, logs, statistics and alarms sit in **ring buffers** ("overwritten cyclically"). Cloud retention, per Huawei's EU Data Act disclosure: **15 months** historical device data, **15 months** hourly report data, **5 years** daily and monthly report data, **25 years** yearly report data, and **6 months** charger alarms and usage. Unbound devices keep their data for 6 months.

### Cited Findings
- [FACT] "Statistics collected every 5 minutes"; alarm data generated "on trigger"; stored "Device-side local data storage" or in the FusionSolar Management System. Daily volumes per device: inverter statistics <50 KB, alarms <1 KB, logs <200 KB; dongle statistics <20 KB; LUNA2000A statistics <20 KB — [Huawei EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)
- [FACT] Retention: "15 months for historical device data, 15 months for hourly report data, 5 years for daily and monthly report data, 25 years for yearly report data, and 6 months for charger alarms and usage data". Device side: "Log, statistical and alarm data will be overwritten cyclically once reaching the maximum limit"; "Real-time operating data refreshes instantly without persistent storage"; configuration parameters persist until factory reset. FusionSolar EU data resides in "the Open Telekom Cloud". On account deletion, data is erased "except as required by law or for anonymized historical performance records" — [Huawei EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)
- [FACT] Unbound device data: "default data retention period is six months". If the device is rebound within that period it "inherits retained data". Permanently deleted device data is "deleted immediately" — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf)
- [FACT] "SmartLogger with the data recovery function to ensure the integrity of plant data". "Hourly data summarized at 5-minute mark of next hour; recovery completes within 24 hours". "Daily/monthly/yearly data recovered at 02:00 daily" — [SmartPVMS 7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf). A 25.4.0 installer-manual page titled "Data Recovery" exists (content blocked) — [Huawei EDOC1100541798](https://support.huawei.cn/enterprise/en/doc/EDOC1100541798/fe2c02f7/data-recovery)
- [FACT] NB query windows: 20026 "Only data of the latest 365 days can be queried"; 20027 "The query time period cannot span more than 31 days"; 30032 history "cannot be longer than three days"; 30031 ≤10 devices; `pageSize` ∈ {10, 20, 30, 50, 100} (30006); ESNs per query ≤50 (30002) — [NBI-V6 §8](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] NB quota formulas, which complement api_integration.md:
  - login: 5 per 10 min; 5 wrong passwords in 10 min → **locked 30 min**
  - `getStationList`: 24 per day
  - `getStationRealKpi`: Roundup(plants/100) per 5 min
  - `getDevList`: Roundup(plants/100)+24 per day
  - `getDevRealKpi`: Σ Roundup(devices of type/100) per 5 min
  - `getDevHistoryKpi`: Σ Roundup(devices of type/10)+24 per day
  - `getAlarmList`: Roundup(plants/100) per 30 min
  - restricted `cs/getInventerRealKpi` (running + alarm data for ≤100 inverters): once per hour
  - "Only one concurrent request is supported per minute"
  - The policy scales with resources for NB users created after **30 Jun 2022**; older users keep the legacy policy
  - Source: [NBI-V6 §1.3, §6.1.x, §6.3](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf)
- [FACT] Management-system domain `intl.fusionsolar.huawei.com`, port **27250**, set in Quick Settings — [Quick Guide Issue 09](https://doe-duurzaam.nl/wp-content/uploads/2025/06/FusionSolar-App-Quick-Guide.pdf). The SmartLogger SIM-sizing table assumes "Device performance data can be updated every 5 minutes" — [SmartLogger3000 User Manual Issue 20](https://ske-solar.com/productdata/SmartLogger/02_Manuals/UserManual_SmartLogger3000_V20_2024-04-15_EN.pdf)
- [FACT] On-demand "Live data" (1 min, ≤10×/plant/day) exists because normal telemetry is 5-min — [App User Manual 2024](https://e-solarshop.ro/wp-content/uploads/2025/07/fusionsolar-app-manual5925.pdf). "Offline" means the cloud link only, and the plant keeps generating — [Solarfox](https://www.solar-display.com/huawei-fusionsolar-issues-offline-status-no-data-delays-explained/)
- [FACT] pyhfs notes that timestamps are documented in plant time zone but are "actually utc/gmt" epoch ms — [pyhfs](https://pypi.org/project/pyhfs/). Integrators see a 5-min measurement interval with 15-min transmission — [meteocontrol](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1)

### Inferences
**Workflow 7: Telemetry ingestion**

| Stage | Observed | Likely implementation | Unknown |
|---|---|---|---|
| Trigger | 5-min sampling; event-driven alarms; on-demand live mode [FACT] | Gateway batches 5-min points and uploads them (possibly several per upload; meteocontrol sees 15-min transmission) [INFERENCE] | Exact upload batch interval for the SDongle |
| Validation | Device must be bound; "abnormal readings with rescan" detection [FACT, installer page] | SN authentication per connection (device certificate?); plausibility checks on counters [INFERENCE] | Device auth mechanism |
| Business logic | Hourly rollup at HH+1:05; nightly 02:00 recompute of day/month/year; 24-h recovery window [FACT] | Lambda-style pipeline: raw 5-min → hourly → daily (plant TZ) → monthly → yearly, with idempotent recompute when late data arrives [INFERENCE] | Gateway cache depth (hours/days) when offline |
| External integration | NB pull only; OAuth for third parties [FACT] | — | Webhooks (none documented) |
| Persistence | Retention tiers 15 mo / 15 mo / 5 y / 25 y; unbound 6 mo [FACT] | Time-series store with TTL per tier; KPI rows `(entity_id, granularity, collect_time, kpi_key, value)` or a wide dataItemMap JSON [INFERENCE] | Storage engine |
| Notification | Plant health → disconnected [FACT] | Comm-loss detector (no data for N intervals) [INFERENCE] | N |
| Audit | — | Ingestion lineage not exposed | — |

- [INFERENCE] The 365-day NB query limit sits inside the 15-month raw retention, so the API deliberately exposes less than is stored.
- [SPECULATION] The SDongle caches only a short window (hours) while inverters keep cyclic statistic buffers. Full recovery is documented only for the SmartLogger.

### Gaps
- [UNKNOWN] SDongle/EMMA offline cache depth and backfill behaviour. Only the SmartLogger "data recovery" is documented publicly.
- [UNKNOWN] The device↔cloud protocol and payload format ("Proprietary format data streams" per the [EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)).
- [UNKNOWN] Retention for alarms (non-charger), tickets, I-V results and logs in the cloud.

---

## 8. Domain data model (entities, attributes, relationships)

### Takeaway
The core aggregate is **Plant** (the API's `stationCode`/`plantCode`, e.g. `NE=33554434` or a 32-hex string). A plant belongs to a **Company** (tenant tree) and has **Owner** users. It contains a tree of **Devices** typed by `devTypeId`, with a communication gateway (Dongle 62 / SmartLogger 2 / EMMA 23070) as parent of inverters (1/38), which in turn parent batteries (39), meters (17/47), optimizers (46) and so on. Time series are stored as **KPI maps** (`dataItemMap` key→value) per entity, granularity and `collectTime`. **Alarms** reference a localized alarm catalogue and link to **Tasks** (defect elimination / inspection). Control actions are **async tasks**. Access to plants is governed by **consent/authorization** records (installer O&M, API, OAuth, kiosk share).

### Cited Findings
- [FACT] Plant (legacy `getStationList`): `stationCode, stationName, stationAddr, capacity (MW), buildState, combineType, aidType, stationLinkman, linkmanPho` — [NBI-V6 §6.1.3](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf). Plant (paged `stations`): `plantCode, plantName, plantAddress, longitude, latitude, aidType, capacity, combineType` plus page fields `pageCount, pageNo, pageSize, total` — pyhfs fixture `stations.json`, [PyPI](https://pypi.org/project/pyhfs/); the HA integration also reads `contactPerson` — [HA const.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/const.py). Note: in the pyhfs fixture, `longitude` = 45.72 and `latitude` = 5.93 for "Grésy sur Aix" (actually lat ≈45.7, lon ≈5.9), so the values are **swapped** in that sample.
- [FACT] Device (`getDevList`): `id (Long), devName, stationCode, esnCode (SN), devTypeId, softwareVersion, invType (inverter model), longitude, latitude`. 25.x adds a model field — [NBI-V6 §6.1.5](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf); [25.2.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100492747)
- [FACT] devTypeId enum (2022): 1 string inverter, 2 SmartLogger, 8 STS, 10 EMI, 13 protocol converter, 16 general device, 17 grid meter, 22 PID, 37 Pinnet SmartLogger, 38 residential inverter, 39 battery, 40 backup box, 41 ESS, 45 PLC, 46 optimizer, 47 power sensor, 62 Dongle, 63 distributed SmartLogger, 70 safety box. Separately, chapter 7 "Device Type List" gives a **second taxonomy**: 20811 MPPT, 20812 PV (string), 20813 PV module, 20814 optimizer, 20815 battery, 20816 meter, 20817 backup box, 20818 safety box, 20819 communication module, 20821 SmartLogger, 20822 inverter, 20824 EMI, 20825 PID, 20826 PLC, 20827 central inverter, 20828 DC combiner box, 20829 STS, 20830 STS meter, 20831 AC combiner box, 20833 communication management unit — [NBI-V6 §6.1.5, §7](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf). EMMA = 23070 — [HA const.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/const.py)
- [FACT] Device real-time KPI keys:
  - **Inverter (1/38)**: `inverter_state, ab_u, bc_u, ca_u, a_u, b_u, c_u, a_i, b_i, c_i, efficiency, temperature, power_factor, elec_freq, active_power (kW), reactive_power, day_cap, mppt_power, pv1..pv24_u, pv1..pv24_i, total_cap, open_time, close_time, mppt_total_cap, mppt_1..10_cap, run_state`
  - **EMI (10)**: `temperature, wind_speed, wind_direction, radiant_total, radiant_line, horiz_radiant_line, horiz_radiant_total`
  - **Grid meter (17)**: phase voltages/currents, `active_power, power_factor, active_cap, reactive_power, reverse_active_cap, forward/reverse_reactive_cap, active_power_a/b/c, reactive_power_a/b/c, total_apparent_power, grid_frequency`, plus TOU registers
  - **Power sensor (47)**: `meter_status, meter_u, meter_i, active_power (W), reactive_power, power_factor, grid_frequency, active_cap, reverse_active_cap`
  - **Battery (39)**: `battery_status, max_charge_power, max_discharge_power, ch_discharge_power, busbar_u, battery_soc, battery_soh, ch_discharge_model, charge_cap, discharge_cap`
  - **ESS (41)**: `ch_discharge_power, battery_soc, battery_soh, charge_cap, discharge_cap`
  - All types: `run_state` (0 disconnected, 1 connected)
  - Source: [NBI-V6 §6.2.6](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf). 25.1.0 extends inverters to 36 PV strings — [25.2.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100492747)
- [FACT] Alarm, plant KPIs, battery/inverter enums, I-V task parameters, control-task parameters, upgrade records, and the task/ticket statuses are all cited in sections 4–7 above.
- [FACT] Kiosk JSON (`realKpi`) exposes `realTimePower, dailyEnergy, monthEnergy, yearEnergy, cumulativeEnergy` — [HA const.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/const.py)
- [FACT] NB account attributes: system name, deadline (expiry), username, password (8–32 chars), interface allow-list, bound plants/devices, "Basic APIs" / "Control APIs" — [NBI-V6 §1.3](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/imaster-neteco-v600r022c00-northbound-interface-reference-v6.pdf); [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/)

### Inferences
**Inferred entity catalogue.** Each entity is labelled [F] = attribute names seen in sources, [I] = inferred, [S] = speculative.

| Entity | Key attributes | Relationships |
|---|---|---|
| **Company** [F/I] | id, name, parent_id, level (2 = top with admin), region/domain, admin_user_id | 1-N Company (children), 1-N User, 1-N Plant, 1-N NorthboundAccount |
| **User** [F/I] | id, username/email, phone, type (Administrator/Installer/Owner), company_id, language, time zone, status | N-M Role; N-M Plant (scope) |
| **Role / Permission / DataScope** [I] | role_code, permissions (e.g. run I-V, param settings, upgrade), scope = company subtree or plant list | — |
| **Plant (Station)** [F] | stationCode/plantCode (e.g. `NE=33554434`), name, address, latitude, longitude, capacity, buildState, combineType, aidType, contact person/phone, time zone [F, manual], currency [F], grid code (device-level) [F], created_at [I], grid connection date [UNKNOWN] | N-1 Company; N-M User (owners, installers); 1-N Device; 1-N Tariff; 1-N KPI; 1-N Alarm; 1-N Task; 1-N ShareLink; 1-N Consent |
| **Tariff / ElectricityPrice** [F/I] | plant_id, type (purchase, feed-in), price, currency, TOU segments [I], valid_from [S]; dynamic market link (OTE) in app 25.4 — [App Store](https://apps.apple.com/jp/app/id1529080383) | N-1 Plant |
| **Device** [F] | id (Long), esnCode (SN), devName, devTypeId, model/invType, softwareVersion, longitude, latitude, stationCode, parent_device_id [I], comm_mode (WLAN/FE/4G) [I], run_state | N-1 Plant; self-reference parent/child (Dongle/SmartLogger/EMMA → Inverter → Battery/Meter/Optimizer) [I]; 1-N KPI; 1-N Alarm |
| **Battery / ESS** [F] | (Device subtype 39/41) SOC, SOH, ch_discharge_model, max charge/discharge power, DOD [F, error 20039] | Child of Inverter [I] |
| **Meter / PowerSensor** [F] | (17/47) meter_status, energy registers incl. TOU | Child of Inverter or Logger [I] |
| **Optimizer / PV module / String / MPPT** [F/I] | optimizer SN, layout position (x, y), azimuth, tilt, module↔optimizer ratio 1:1 or 1:2; string capacity = rated module power × count; MPPT index | Optimizer → Inverter; String → MPPT → Inverter [I] |
| **Charger (SCharger)** [F/I] | device + connectors, locking mode, max power, auth methods (app/BT/RFID/plug&play) | 1-N ChargingSession [I]; N-M SharedUser [F]; 1-N RfidCard [F] |
| **ChargingSession** [I] | charger_id, user/RFID, start, end, kWh, mode (PV-preferred/scheduled/next-trip) | retained 6 months [F] |
| **KPI time series** [F] | entity (plant/device), granularity (realtime, 5-min, hour, day, month, year), collectTime (epoch ms, aggregated per plant TZ), dataItemMap{key:value} | retention 15 mo / 15 mo / 5 y / 25 y [F] |
| **AlarmDefinition (catalogue)** [I] | alarmId, causeId, devType, lev, alarmType, i18n {name, cause, repairSuggestion} | 1-N Alarm |
| **Alarm (occurrence)** [F] | stationCode, devName, esnCode, devTypeId, alarmId, causeId, lev, alarmType, status (1–6), raiseTime, (ack/clear time and actor [I]), location info ([CNo]/[SNo]) [I] | N-1 Device; 0-1 Task |
| **AlarmPushRule** [F/I] | name, enabled, plants/scope, severities, recipients, channels (email/app) [I]; ≤1000 per system [F] | N-1 Company |
| **Task (Ticket)** [F] | type (defect elimination / inspection), status (dispatch→elimination→approval; not started→in progress→to be confirmed→terminated), description, attachments, assignee, handling suggestion, result, approver | N-1 Plant; 0-N Alarm |
| **ControlTask** [F/I] | taskId (unique, 20048), type (battery dispatch / battery mode / active power / switch on-off / MPPT backfeed), params (power, target SOC, duration, DOD), status, result | N-1 Plant or Device |
| **UpgradeJob / UpgradeRecord** [F/I] | package/version, target devices, per-device status, from/to version | N-M Device |
| **IVTask / IVResult** [F] | taskName, plants (≤20) or devices (≤100), cleanStatus, environmentalParameters (auto/manual irradiance 600–1500, temperature 0–100), scanPointNum = 128; result per string: code 10000–10020, 128-point curve | N-1 Company; 1-N IVResult |
| **Report / ReportSubscription** [F/I] | type (plant/inverter/PCS/battery), granularity (day/month/year/lifetime), plants, recipients, schedule, format [UNKNOWN] | — |
| **NorthboundAccount** [F] | system name, username, password, deadline, interface list, bound plants/devices, policy generation (pre/post 30 Jun 2022) | N-1 Company |
| **OAuthClient / Authorization** [F] | client registration, owner grant, revoke | N-M Plant via owner consent |
| **ShareLink (Kiosk)** [F/I] | token `kk`, plant, expires (1 year), refresh 10 min | N-1 Plant |
| **Consent** [F/I] | plant, grantee (installer company / API / OAuth), scope (O&M, params, API), granted_by owner, timestamps | N-1 Plant |
| **Invitation** [F/I] | email, role (owner/installer), plant, status, expiry [S] | — |

- [INFERENCE] **Two device taxonomies** coexist: the legacy NB `devTypeId` (1, 38, 39, …, 62) and the 208xx model-type IDs, which add MPPT, PV string and PV module as first-class "devices". This suggests the internal model treats strings and modules as managed objects (needed for I-V and the module layout) while the legacy API flattens them. A redesign should model `DeviceType` as a table with a `category` and both code systems.
- [INFERENCE] The `NE=<number>` station code (seen in NB examples and meteocontrol configs) next to 32-hex codes suggests two ID schemes: a NetEco "network element" DN and a UUID. The `nds`/`dns` parameters in error codes 30010/30016/30017 are likely "DN" lists. In other words, everything in the internal model is a managed object addressed by a DN.
- [INFERENCE] `dataItemMap` key–value KPIs imply a schemaless KPI layer, which explains how new device types (EMMA, charger) are added without changing the API. Replicating it with a KPI-definition registry (key, unit, device type, granularity, aggregation function) plus narrow time-series rows would give the same flexibility.

### Gaps
- [UNKNOWN] A public ER model or the field list of the newer `stations` response beyond the fields above (e.g. `gridConnectionTime`, `contactMethod` were not found).
- [UNKNOWN] Device codes for SCharger and EMMA sub-devices in the 2024+ device-type table (only EMMA 23070 is known from community code).
- [UNKNOWN] Whether a Plant can belong to multiple companies (installer handover) or only transfers between them.
