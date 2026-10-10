# FusionSolar from a second batch of public sources: the Huawei openAPI guide, the huawei_client crate, EnergyID, ChargeHQ bridge, IP-Symcon module, a mis-named ML repo, and a Tesla-style energy-flow card (Oct 2026)

Scope and method. This note adds only what is new relative to `source_code_clients.md`, `demo_observations.md` and `Nền tảng Huawei FusionSolar/api_integration.md` (plus `workflows_data_model.md`, which already holds the 2022 NBI-V6 quota formulas and error codes). Everything was read as data: repos cloned into empty scratch dirs, the crate tarball downloaded from crates.io and unpacked, PDFs converted with `pdftotext` and a few pages rendered to images to read screenshots. Nothing was built, run or imported. No FusionSolar login, no credentials, no Huawei endpoint contacted.

Sources and versions read:
- **`huawei_client` crate** v0.0.2 (crates.io, published 2022-12-18 by `n3wtron` = Igor Maculan; licence file is MIT "Copyright (c) 2022 ByteHunters", crates.io shows "non-standard"; no repository URL in the manifest). The tarball bundles two Huawei PDFs: **"Communicate with FusionSolar through an openAPI account"** (13 pp, Version 01, 26.12.2019, Huawei e84081311, footer eu_inverter_support@huawei.com; byte-identical (same MD5) to `2019FS026 …pdf` in the danwale repo) and **"SmartPVMS V500R007C00 NBI Reference"** (Issue 01, 2021-07-27, 157 pp) — [crate source](https://docs.rs/crate/huawei_client/latest/source/)
- **EnergieID/FusionSolar** (master @0ffcb7d, 14 commits, 2020-04-08 → **2022-02-11**), **MIT** (EnergieID cvba-so), PyPI `fusionsolar` 0.0.6
- **danwale/HuaweiFusionSolar-ChargeHQ-Integration** (main @23e59fc, 72 commits, 2022-11-12 → **2023-09-13**), **MIT** (Daniel Wale), C#/.NET + Docker. Its `docs/` bundles 5 PDFs, including Huawei's **"Create API account on FusionSolar Server (only Company Admin)"** (Version 01, 06.09.2022) and **"iMaster NetEco V600R023C00 Northbound Interface Reference-V6 (SmartPVMS)"** (Issue 01, 2023-01-19, 193 pp)
- **bresden5/Huawei-Fusion-Solar** (main @0f5962d, 11 commits, 2026-02-02 → **2026-05-30**), **no LICENSE file**
- **Joya-Biswas/solar-panel-efficiency-fusion** (main @e452bc7, 3 commits, all **2026-05-05**), **MIT**
- **reptilex/tesla-style-solar-power-card** (master @4881d8e, 175 commits, 2020-08-21 → **2024-06-23**), **Apache-2.0**

Labels: **FACT** = seen in source, PDF text or screenshot. **INFERENCE** = my reasoning from facts. **SPECULATION** = plausible, unverified.

---

## 1. Huawei's "Communicate with FusionSolar through an openAPI account" (2019) and the bundled V500R007C00 NBI Reference (2021): account creation, auth, token lifetime, limits, endpoints

### Takeaway
The PDF at the docs.rs URL is a 13-page Huawei EU support how-to from Dec 2019, not an API reference. It covers the legacy Northbound flow: email Huawei support for an account, `POST /thirdData/login {userName, systemCode}`, copy the `XSRF-TOKEN` into a header, then call 7 plant/device endpoints. It says the limit is one call per minute per interface and documents no OAuth, scopes or IP whitelist. The crate also bundles a full NBI Reference (V500R007C00, 2021), which answers several open gaps. The **XSRF-TOKEN is valid for 30 minutes as a sliding idle timeout**. **Each login consumes a "client login resource"**. A per-interface table gives per-minute limits and recommended cadences. The cookie-vs-header token divergence in community clients comes from a documented 2021 change. The reference also describes a separate, little-known **"V7" API on port 27200 (`/rest/openapi/pvms/v1/…`) with VPP endpoints**: owner-consented plant enrolment by SN or authorization code, battery forced charge/discharge tasks, DoD, DRM and inverter on/off. This predates the 24.x "OAuth Connect" control APIs already in `api_integration.md`.

### Cited Findings
**The 2019 guide (2019FS026)** — [PDF](https://docs.rs/crate/huawei_client/latest/source/docs/Communicate%20with%20FusionSolar%20through%20an%20openAPI%20account.pdf)
- FACT (p.2): "The access privilege to the northbound interface API is independent of third-party user accounts, and users must apply for it separately. Third-party applications will be limited by one-minute access frequency when accessing the same northbound interface API." Step 1: "Contact service team at eu_inverter_support@huawei.com to create an openAPI account for your plant."
- FACT (p.2, table): client → FusionSolar server, **destination port 27200**, HTTPS, "Port for logging in to the FusionSolar server open interface in TLS encryption mode", authentication "Username/password", encryption "TLS1.1&1.2". The guide still uses `https://eu5.fusionsolar.huawei.com/thirdData/...` (default port 443) in every example.
- FACT (p.3): a sequence diagram shows (1) Login with system number → (2) tokenID → (3) data request + tokenID → (4) response. It points to the chapter "Northbound Management" in the product document for configuring the third-party system. It also tells the user to **disable SSL certificate verification in Postman**.
- FACT (pp.4–5, screenshots): the login request body is raw JSON `{userName, systemCode}`. The response is HTTP 200 with body `{"buildCode":"2","data":null,"failCode":0,"message":"","params":null,"success":true}`. The response sets **3 cookies**: `web-auth=true` (HttpOnly, Secure), `XSRF-TOKEN` (**HttpOnly=false**, Secure) and `JSESSIONID` (HttpOnly, Secure), all session cookies ("Expires: Never" in Postman). Data calls carry the header `XSRF-TOKEN: <value>` + `Content-Type: application/json`.
- FACT (decoded from the p.5 screenshot): the visible `XSRF-TOKEN` value begins with `eyJhbGciOiJIUzI1NiJ9` = `{"alg":"HS256"}`. Its payload segment decodes to `{"randomKey":"<uuid>"}` and nothing else, so the JWT has no `exp` or user claims.
- FACT: endpoints walked through: `login`, `getStationList` (no body), `getStationRealKpi`, `getKpiStationHour/Day/Month/Year` (`stationCodes` + `collectTime`), `getDevList`. For device real-time data it says to "Ask the service team… to provide you the **SmartPVMS V300R006C00 Interface Reference**". On error: "login again and insert the new Token in Headers."
- FACT: the guide mentions no scopes, IP whitelist, OAuth, refresh token or explicit token TTL.

**SmartPVMS V500R007C00 NBI Reference (Issue 01, 2021-07-27)** — [PDF](https://docs.rs/crate/huawei_client/latest/source/docs/SmartPVMS%20V500R007C00%20NBI%20Reference_New.pdf) (also in [danwale/docs](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/tree/main/docs))
- FACT (§1): "The maximum number of access times of each API account is **10 per API per minute**. If the access frequency exceeds the limit, the interface returns error code 407." Access: "apply to the system administrator… The system administrator will assign an account with the required permission and password."
- FACT (§3.1 Login): "The validity period of the XSRF-TOKEN is **30 minutes**. If the XSRF-Token does not expire, it can be reused." Login: max **1/min**, "recommended that the interface be invoked every 30 minutes." (§5.1.1, V7 login): "Each time you successfully log in… a new XSRF-TOKEN message is returned, **consuming a client login resource**. The **idle timeout** interval… is 30 minutes… if XSRF-TOKEN is invalid, error 305 is returned." "The time starts when the system receives the **last interaction request**."
- FACT (§3.2): `POST /thirdData/logout {"xsrfToken": "..."}` makes the token "expire immediately". Max 1/min, "invoke… only when necessary."
- FACT (§2.3, Modified interfaces → Login), explaining the cookie vs header split among clients: "In V300R006C10SPC230, a northbound login request has multiple Set-Cookie headers, with first letters in upper case. The XSRF-TOKEN is put in the second Set-Cookie header. In V500R007C00SPC110, a northbound login request has only one set-cookie header, with all letters in lower case… An **xsrf-token is added to the response header**… the same as that of the XSRF-TOKEN in the set-cookie header. You are advised to use the new xsrf-token response header."
- FACT, per-interface limits and refresh cadence (§3.x "Access Restrictions"):

| Interface | Max/min per NBI account | Data refresh / recommended call rate |
|---|---|---|
| login / logout | 1 | login every 30 min |
| getStationList | 1 | not updated unless plant info changes; ≤1/h |
| getStationRealKpi | 10 | updated every 5 min; ≤ every 5 min |
| getKpiStationHour / Day | 1 | updated hourly; ≤1/h |
| getKpiStationMonth / Year | 1 | updated daily; ≤1/h |
| getDevList | 10 | ≤1/h |
| getDevRealKpi / getDevFiveMinutes | 10 | updated every 5 min |
| getDevKpiDay | 1 | updated hourly |
| getDevKpiMonth / Year | 1 | updated daily |
| getAlarmList | 1 | updated every 5 min |

- FACT (§2.3): device types allowed per interface in V500R007C00. `getDevList` supports 1, 2, 8, 10, 13, 16, 17, 22, 37, 38, 39, 40, 45, 46, 47, 62, 63, 70. `getDevRealKpi` and `getDevFiveMinutes` support only **1, 10, 17, 38, 39, 47**. `getDevKpiDay/Month/Year` support only **1, 38, 39**, and "production deviation / production reliability / communication reliability" cannot be queried for 1 or 38.
- FACT (§2.2): **deleted** in V500R007C00SPC110 with "The function of this interface is not implemented": `/thirdData/devOnOff`, `/thirdData/devUpgrade`, `/thirdData/getDevUpgradeInfo`. `/thirdData/snIsRegister` was replaced by `/rest/openapi/pvms/v1/community/snIsRegister`.
- FACT (§2.1 + §5, "V7 Interface Reference"): new endpoints, all POST at `https://x.x.x.x:27200/rest/openapi/pvms/v1/…`:
  - `login` (body `{username, password}`, lowercase and different from thirdData's `userName/systemCode`; returns XSRF-TOKEN in header), `logout`
  - `plants` (paged `pageNo/pageSize`; returns `plantCode, capacity (kWp), contactPerson, contactMethod, gridConnectionDate` as ISO-8601 with offset e.g. `2020-02-06T00:00:00+08:00`; 1/min)
  - `devices` (`plantCodes` ≤100, paged; returns `plantCode, deviceTypeId (208xx family), dn, sn, deviceName, dataItemMap` with static attributes, e.g. battery `model, ratedCapacity, usableCapacity (kWh), dod`, inverter `ratedPower (kW)`; 10/min)
  - VPP: `vpp/snEnrolment` and `vpp/acEnrolment`, `vpp/plants`, `vpp/plantRealtimeKpi`, `vpp/plantFiveMinutesKpi`, `vpp/chargeAndDischarge`, `vpp/chargeAndDischargeStatus`, `vpp/dod`, `vpp/drm`, `vpp/devOnOff`
  - `community/snIsRegister`
- FACT (§5.3.1–5.3.2) **VPP consent/enrolment**: `snEnrolment` "register[s] a power plant with no permission based on the device SN and authorize[s] the plant… to the VPP". It takes up to **1000** entries of `{sn, username | email | phone}`, where `sn` is the SN of any inverter, SmartLogger or Dongle and the identity must be the plant owner's verified username/email/phone. `acEnrolment` does the same with a device **authorization code (AC)** "correctly entered" by the installer. 10/min.
- FACT (§5.3.4) `vpp/plantRealtimeKpi` (≤100 plants, 10/min, data every 5 min) returns per-plant power-flow keys: `dayEnergy, monthEnergy, totalEnergy` (kWh); `pvPower` (kW); `meterPower` (kW; **<0 = drawn from grid, >0 = fed to grid**); `batteryPower` (kW; **>0 = discharge, <0 = charge**); `loadPower` (kW). `vpp/plantFiveMinutesKpi` returns ≤288 five-minute rows for one plant and one day (`startTime/endTime` same day), including grid line voltages.
- FACT (§5.3.6–5.3.9) **control**:
  - `chargeAndDischarge` (≤100 plants, **100/min**) takes `plantCodes, dispatchSwitch (0 stop / 1 forced charge / 2 forced discharge), controlType (1 SOC / 2 duration), targetSOC, dispatchTime (0–1440 min), powerDispatch (W, >0 charge, <0 discharge, clamped to max), requestID (Long, unique)`. It returns per inverter `{plantCode, sn, dispatchResult 0/1, remoteID}`. "If there are multiple ESSs in the power plant, the task is executed on every ESS." "do not invoke… repeatedly before a task is complete."
  - `chargeAndDischargeStatus` (by `requestID`, 100/min) returns subtask `status` 0 complete / 1 in progress / 2 timeout (timeout if not complete within 24 h).
  - `dod` takes `dns` (battery DN, `deviceTypeId 20815`, ≤100) and `dod` (int, clamped to nearest allowed). 10/min.
  - `devOnOff` takes `dns` (inverters ≤100) and `controlType` 1 on / 2 off. 10/min.
- FACT (§7 error list), codes not already in the notes: 20004 server abnormal; 20018 "A maximum of 10 devices can be operated at a time"; 20038 authorization-code list empty; 20049 "Failed to deliver the charging and discharging task"; 20050 task query parameter does not exist; 20051 failed to set DOD; **20403 "The login of the third-party system user is restricted"**; 30008 "Failed to invoke the internal interface".

### Inferences
- INFERENCE: the 2019 "one-minute" rule, the 2021 "10 per API per minute" table and the 2022+ resource-scaled daily formulas (in `workflows_data_model.md`) are successive policies. The V6 doc says NB users created before 30 Jun 2022 keep the legacy policy, so the V500R007C00 table above is very likely that legacy policy. The HA integration's "1 call/min per endpoint" is the conservative reading.
- INFERENCE: the token is an **opaque server-side session handle**. The JWT carries only a random key, and the 30-min idle timer resets on each request. Several clients send only the `XSRF-TOKEN` header with no cookie jar (`huawei_client` uses `reqwest::Client::new()` without cookies; bresden5 uses curl without cookies; pjugowiec uses Retrofit without a CookieJar). That suggests the header alone identifies the session, so it is not a pure double-submit CSRF check. "Consumes a client login resource" plus failCode 20400 "online sessions reaches the upper limit" (already noted) mean that **logging in on every poll leaks sessions**, and the token should be reused for up to 30 min idle.
- INFERENCE: port **27200** is the native SmartPVMS NBI/OpenAPI port on on-prem or managed deployments (`x.x.x.x:27200`). The public cloud (`eu5`, `intl`, …) fronts the same service on 443.
- INFERENCE: the V7 `/rest/openapi/pvms/v1/vpp/*` family (2021) is the ancestor of the 24.x `/rest/openapi/pvms/nbi/v1|v2/control/*` "Control APIs" that are "available only in OAuth Connect mode" (`api_integration.md`). Owner consent moved from "SN + owner identity" or an installer-entered authorization code to an OAuth grant. The V600R023C00 doc (2023-01) still lists `vpp/drm` (it adds `remoteId` and an async status query), so both families coexisted in 2023.
- INFERENCE: control is **task-based and asynchronous** (requestID → remoteID per inverter → status polled, 24 h timeout), with per-plant mutual exclusion. This is consistent with the gateway-relayed command model in `workflows_data_model.md`.

### Gaps
- OAuth Connect authorize/token URLs, grant type, refresh tokens and scopes are **not** in either PDF. The 2019 guide predates OAuth, and V500R007C00 and V600R023C00 only use XSRF login. A targeted web search returned nothing relevant. This remains open (see §3).
- IP whitelisting: not mentioned in any document read (2019 guide, 2021 V500R007C00, 2022 account-creation PDF, 2023 V600R023C00). I found no evidence it exists.
- The "SmartPVMS V300R006C00 Interface Reference" mentioned by the 2019 guide was not available.

---

## 2. The huawei_client Rust crate itself: endpoints, models, error handling

### Takeaway
It is a tiny (~600 LOC), async **reqwest + serde** wrapper for 5 legacy Northbound calls. It is notable for **proactive token renewal at 20 min** (rather than reacting to 305), a mockable trait, and typed `dataItemMap` structs for only two device types. Its `DeviceType` enum is `#[repr(u8)]` and has EMI = 9 (the doc says 10). Plants with EMMA (23070), ESS (41) or any unlisted type would therefore fail to deserialise.

### Cited Findings
- FACT: dependencies `reqwest 0.11 (json)`, `serde`, `serde_repr`, `thiserror`, `async-trait`, `mockall`, `strum`. Trait `HuaweiClient` (annotated `#[automock]`) has `get_station_list`, `get_realtime_station_data`, `get_device_list`, `get_realtime_residential_inverter_data`, `get_realtime_power_sensor_data` — [client.rs](https://docs.rs/crate/huawei_client/latest/source/src/client.rs); [Cargo.toml.orig](https://docs.rs/crate/huawei_client/latest/source/Cargo.toml.orig)
- FACT: endpoints wrapped: `/thirdData/login`, `getStationList` (no body), `getStationRealKpi` `{stationCodes}`, `getDevList` `{stationCodes}`, `getDevRealKpi` `{devIds, devTypeId}`. Default base URL `https://eu5.fusionsolar.huawei.com` — [client_impl.rs L36-L38, L40-L256](https://docs.rs/crate/huawei_client/latest/source/src/client_impl.rs)
- FACT: `login()` reads the **`xsrf-token` response header** and sets `login_expiration = now + 20*60 s`. `ensure_token()` re-logs in when that time passes and sends the header **`XSRF-TOKEN`**. The token is held in `Mutex<Option<String>>`. There is no 305 handling, no logout call (the `LogoutError` and `NotLogged` variants are unused), and no 407/back-off — [client_impl.rs L40-L96](https://docs.rs/crate/huawei_client/latest/source/src/client_impl.rs); [errors.rs](https://docs.rs/crate/huawei_client/latest/source/src/errors.rs)
- FACT: error handling maps non-200 HTTP to `GetDataError("Http error…")` and `success:false` to `GetDataError(message or "failCode:N")`. On success it does `resp.data.unwrap().first().unwrap()`, which panics when `data` is null or empty (e.g. the permission case where `data:null`) — [client_impl.rs L116-L134, L195-L206](https://docs.rs/crate/huawei_client/latest/source/src/client_impl.rs)
- FACT: models. Generic envelope `RootResponse<D,R>{fail_code: u16, message: Option<String>, success, params: R, data: Option<Vec<D>>}`. `RealtimeData` holds `day_power, month_power, total_power, day_income, total_income, real_health_state` as **f32**. `GetDevListData` holds `id: i64, dev_type_id: DeviceType, esn_code/inv_type/optimizer_number/software_version: serde_json::Value, latitude/longitude: f64`. Inverter item: `pv1..8_u/_i, mppt_1..4_cap, a/b/c_u, ab/bc/ca_u, a/b/c_i, active_power, reactive_power, power_factor, elec_freq, efficiency, temperature, day_cap, total_cap, mppt_power, inverter_state, run_state, open_time, close_time`. Power sensor item: `meter_status, meter_u, meter_i, active_power, reactive_power, power_factor, grid_frequency, active_cap, reverse_active_cap, run_state` — [api_responses.rs](https://docs.rs/crate/huawei_client/latest/source/src/api_responses.rs)
- FACT: `DeviceType` is `#[repr(u8)]` with `StringInverter=1, SmartLogger=2, TRANSFORMER=8, EMI=9, ProtocolConverter=13, GeneralDevice=16, GridMeter=17, PID=22, PinnetDataLogger=37, ResidentialInverter=38, Battery=39, BackupBox=40, PLC=45, Optimizer=46, PowerSensor=47, Dongle=62, DistributedSmartLogger=63, SafetyBox=70`. `get_data_item_type()` is `todo!()` for all but 38 and 47 — [api_requests.rs](https://docs.rs/crate/huawei_client/latest/source/src/api_requests.rs). The NBI doc lists EMI as **10** (V500R007C00 §2.3).
- FACT: the unit-test fixture (a real-looking `getDevRealKpi` response for devTypeId 38) has numeric (not string) values, `inverter_state: 512.0`, `open_time/close_time` epoch ms, `devId` 1000000035201360 (16 digits), and `params{currentTime, devIds, devTypeId}`. The test calls `get_device_list("NE=35201359")` — [client_impl_test.rs L55-L94](https://docs.rs/crate/huawei_client/latest/source/src/client_impl_test.rs)

### Inferences
- INFERENCE: `serde_repr` on a `u8` enum makes `getDevList` deserialisation fail for **any plant containing a device type outside the enum**. That includes EMI (10), ESS (41), and EMMA (23070, which cannot fit in u8). The crate therefore only works for simple residential plants.
- INFERENCE: `RealtimeData` as `f32` conflicts with the string-typed `getStationRealKpi` values in the pyhfs fixture (`source_code_clients.md` §4). Either Huawei returns numbers in some regions or versions, or the crate errors on that call. Either way a robust client must accept both.
- INFERENCE: the 20-min proactive renewal, also used by EnergieID (1200 s, §3), is a sound pattern given the documented 30-min idle TTL. It still needs a 305 fallback, because idle-time and server restarts can invalidate tokens early.

### Gaps
- No upstream repository is linked from the crate, so I could not check commit history or issues.

---

## 3. EnergieID/FusionSolar and the EnergyID "legacy stops 1 Dec 2026" migration

### Takeaway
The public EnergieID repo is EnergyID's **legacy** connector: a 2020–2022 Python client for the `thirdData` Northbound API (userName + systemCode, XSRF header), with simple 407 back-off and re-login on 305/306/307. It contains **no OAuth code**. The "new, more secure" EnergyID connection (since 16 Dec 2024) sends the owner to the **FusionSolar login screen to grant EnergieID permission** and requires the Owner role. That is an OAuth-style, owner-consent flow, very likely Huawei's OAuth Connect, but its implementation is not public.

### Cited Findings
- FACT: `Client(user_name, system_code, max_retry=10, base_url="https://intl.fusionsolar.huawei.com/thirdData")`. Login does `POST /login {userName, systemCode}`, clears cookies first, reads the **`XSRF-TOKEN` cookie** and sets it as the `XSRF-TOKEN` header. It sets `token_expiration_time = now + 1200 s` (20 min), and the `@authenticated` decorator re-logs in when that passes — [client.py L29-L41, L75-L111](https://github.com/EnergieID/FusionSolar/blob/master/fusionsolar/client.py#L29-L111)
- FACT: the `@throttle_retry` decorator, on failCode **407**, sleeps `i*3` s for i=1..10 (linear back-off, 3 s up to 30 s, about 165 s in total). On **305/306/307** it re-logs in and retries once. `_validate_response` maps 305, 306 and 307 all to `HTTPError306` (the separate 305/307 classes are never raised) and 401 to `HTTPError401` — [client.py L44-L71, L113-L137](https://github.com/EnergieID/FusionSolar/blob/master/fusionsolar/client.py#L44-L137)
- FACT: wrapped endpoints: `getStationList`, `getStationRealKpi`, `getKpiStationHour/Day/Month/Year`, `getDevList`, `getDevRealKpi`, `getDevFiveMinutes`, **`getDevKpiHour`**, `getDevKpiDay/Month/Year`, **`devOnOff`** `{devIds, devTypeId, controlType 1 on/2 off}`, **`devUpgrade`**, **`getDevUpgradeInfo`**. `collectTime` = `int(pd.Timestamp.timestamp())*1000`, i.e. tz-aware local midnight converted to epoch ms — [client.py L149-L238](https://github.com/EnergieID/FusionSolar/blob/master/fusionsolar/client.py#L149-L238)
- FACT: `PandasClient.get_kpi_day` flattens `data[].dataItemMap` + `collectTime` into a DataFrame indexed by UTC time, cast to float — [client.py L241-L260](https://github.com/EnergieID/FusionSolar/blob/master/fusionsolar/client.py#L241-L260)
- FACT: commit history: initial 2020-04-08; "Completed FusionSolar-API wrapper" 2020-07-29; base_url argument added 2021-01-11 because "for AU we use https://sg5.fusionsolar.huawei.com/thirdData"; "Added more 30x error codes" 2021-01-11; "update default URL" 2021-10-22; "add HTTP Error 401" 2022-02-11 (last) — `git log` of clone
- FACT: `_login.py` hard-codes the same example account shown in Huawei's 2019 guide screenshot against `eu5` — [_login.py](https://github.com/EnergieID/FusionSolar/blob/master/_login.py)
- FACT (EnergyID help): the new method has been available since **16 Dec 2024**, and legacy connections stop syncing on **1 Dec 2026**. For existing connections, users are redirected to "the FusionSolar login screen" to "Log in to FusionSolar with your personal login credentials and grant EnergieID permission to retrieve your FusionSolar data". The user must be the **Owner** of the installation. No technical details are given — [EnergyID help](https://help.energyid.eu/en/apps/migrating-your-fusionsolar-integration-to-the-new-version)

### Inferences
- INFERENCE: `getDevKpiHour` does not exist in either NBI reference read (V500R007C00 or V600R023C00; zero matches). `devOnOff`, `devUpgrade` and `getDevUpgradeInfo` were declared "not implemented" and deleted in V500R007C00SPC110. These four wrappers are dead code.
- INFERENCE: the 407 back-off (at most about 165 s) is too short for daily-quota exhaustion (20618) and wastes calls under a per-minute policy. A ≥60 s wait matches Huawei's documented window.
- INFERENCE (strong): EnergyID's new flow (redirect to the FusionSolar login, owner grants permission to a named app, Owner role required) matches Huawei's documented OAuth Connect sections "Creating an OAuth 2.0 Client for a Third-Party App" and "Initiating Authorization to a Third-Party App by an Owner" (24.x/25.x refs in `api_integration.md`). The 1 Dec 2026 cut-off suggests EnergyID is retiring its installer-issued Northbound accounts in favour of per-owner OAuth grants.
- SPECULATION: the date may reflect a Huawei-side deprecation of shared installer Northbound accounts for third-party apps, not only an EnergyID decision. No Huawei source found confirms this.

### Gaps
- EnergyID's OAuth client code, Huawei's authorize/token URLs and token lifetimes are not public in this repo or the help page.
- Whether Huawei itself announced an end date for `thirdData` userName/systemCode logins: not found.

---

## 4. danwale/HuaweiFusionSolar-ChargeHQ-Integration: an EV solar-surplus bridge

### Takeaway
A .NET/Docker service polls the legacy Northbound API **every 305 s** (hard-coded "5 minutes plus a bit", because Huawei data refreshes every 5 min). It reads the inverter, then the power sensor (47) **or** grid meter (17), then the battery (39) via `getDevRealKpi`. It maps these to **ChargeHQ's Push API** `siteMeters` (production, net import, consumption, battery SOC/power), which ChargeHQ uses to throttle Tesla charging to solar surplus. The bundled docs add first-hand facts on Northbound account creation: **max 5 Northbound accounts per company**, globally unique system names and usernames, and per-interface × per-device-type permission toggles. The code also shows typical pitfalls: unit and sign confusion, accepting any TLS certificate, and plant-selection bugs.

### Cited Findings
**Polling and rate-limit strategy**
- FACT: `HuaweiSettings.PollRate` is a getter that always returns **5** ("Huawei ask for this to be 5 minutes so it's hardcoded"). The timer is `PollRate * 61000` ms = **305 s** ("add a bit extra on to ensure it's greater than 5 minutes") — [HuaweiSettings.cs L30-L37](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/Models/Configuration/HuaweiSettings.cs#L30-L37); [HuaweiSolarPoller.cs L118](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiSolarPoller.cs#L118). Commit 2023-07-04: "Fixed the poll period to 5 minutes plus a few seconds… to avoid API poll period restrictions being imposed."
- FACT: `Constants.cs` comments: login "need to login every 30 minutes"; getDevList "can't call this more than 10 times a minute"; getDevRealKpi "can't call this more than once every 5 minutes" — [Constants.cs](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/Constants.cs)
- FACT: init sequence: login → `getStationList` → on failCode **401** fall back to paged `/thirdData/stations` → `getDevList` → pick devices by `devTypeId` 47, 17, 39, then 38 (else 1). The first poll is skipped unless only the inverter is used, "to prevent API over frequency use" — [HuaweiSolarPoller.cs L141-L248, L297-L394](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiSolarPoller.cs#L141-L394)
- FACT: each tick makes up to 3 sequential `getDevRealKpi` calls (one devTypeId each: inverter, then meter or sensor, then battery). On failCode **305** it re-logs in and resends. On HTTP non-200 or exceptions it retries every 5 s up to 5 times (a static `RetryCount` shared across calls), then returns a synthetic `failCode 1001`. There is no specific 407 handling — [HuaweiSolarPoller.cs L457-L522, L529-L812](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiSolarPoller.cs#L457-L812)
- FACT: token: the `XSRF-TOKEN` **cookie** from a `CookieContainer` is copied into default request headers — [HuaweiSolarPoller.cs L414-L449](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiSolarPoller.cs#L414-L449)
- FACT: `ServerCertificateCustomValidationCallback` returns `true`, so **all TLS certificates are accepted** — [HuaweiSolarPoller.cs L128-L139](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiSolarPoller.cs#L128-L139). This mirrors the 2019 Huawei guide's "disable SSL certificate verification" advice (§1).
- FACT: `HuaweiInvalidNAValueConverter` exists because the API returned the string **"N/A"** for `close_time`/`open_time` (epoch fields), which broke deserialisation. It is mapped to 0 — [HuaweiInvalidNAValueConverter.cs L6-L50](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiInvalidNAValueConverter.cs)

**Data mapping to ChargeHQ (EV-charging relevant)**
- FACT: ChargeHQ Push API `POST https://api.chargehq.net/api/public/push-solar-data` takes body `{apiKey, tsms?, error?, siteMeters{production_kw, net_import_kw (negative = export), consumption_kw, imported_kwh, exported_kwh, battery_discharge_kw, battery_soc, battery_energy_kwh}}`. Null fields are omitted. The `error` string is sent instead of data when polling fails — [SiteMeterPush.cs](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/Models/ChargeHQ/SiteMeterPush.cs); [SiteMeter.cs](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/Models/ChargeHQ/SiteMeter.cs); [ChargeHQSender.cs](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/ChargeHQSender.cs); [appsettings.json](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/appsettings.json)
- FACT: field mapping — [HuaweiSolarPoller.cs L596-L756](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/HuaweiSolarPoller.cs#L596-L756):
  - `tsms` = response `params.currentTime` (server time, not measurement time)
  - `production_kw` = inverter `active_power` (kW). `inverter_state != 512` is logged as "shutdown due to no sunlight"
  - `exported_kwh` = inverter `total_cap` (lifetime **yield**; the code comment admits this), overwritten by the meter's `active_cap` if > 0
  - Power sensor (47): `net_import_kw = -active_power/1000` (W→kW; the comment says positive `active_power` "is the excess solar"); `consumption_kw = production_kw - active_power/1000`; skipped if `meter_status == 0` (offline)
  - Grid meter (17): same formulas but **no /1000** (kW)
  - Battery (39): skipped if `battery_status == 0`. `battery_soc` is normalised to 0–1 heuristically ("if > 1 divide by 100"). `battery_energy_kwh = charge_cap`. `battery_discharge_kw = ch_discharge_power` with **no unit conversion**
- FACT: the NBI V6 doc lists power sensor `active_power` in **W** and battery `ch_discharge_power` in **W**, `battery_soc` in **%** — [V600R023C00 NBI-V6 §9.2.6](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/docs/iMaster%20NetEco%20V600R023C00%20Northbound%20Interface%20Reference-V6(SmartPVMS).pdf). Battery model fields and enums are in [DevRealKpiBattDataItemMap.cs](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/Models/Huawei/DevRealKpiBattDataItemMap.cs) (`battery_status` 0 offline/1 standby/2 running/3 faulty/5 hibernating; `ch_discharge_model` 0–4).

**Account-creation facts from the bundled docs**
- FACT (Huawei, "Create API account on FusionSolar Server (only Company Administrator)", 06.09.2022, a84160932): "Only the Company Administrator (**Installer who first registered the company** on FusionSolar server) has the right". Path: System > Company Management > **Northbound Management** > Add. Fields: System name, Username, Password, **Deadline** ("available until the deadline"), plant list under "Interface Status", then "Select the Interface Status according to the user necessities" — [PDF](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/docs/2022FSV8001%20Create%20API%20account%20on%20FusionSolar%20Server%20(only%20Company%20Admin....pdf)
- FACT (danwale's installer guide, 27 Feb 2023):
  - "Huawei's FusionSolar system only allows for a company to have **5 Northbound API accounts**"
  - **System name and Username are globally unique** (across all of FusionSolar)
  - Extra dialog fields: "System introduction" and "Associated account"
  - The password cannot be viewed after creation
  - Per-interface toggles: Plant list (pick the company root = all plants, or individual plants), Real-time/Hourly/Daily/Monthly/Yearly plant data, Device list, Real-time/Daily/Monthly/Yearly device data and **Historical Device Data**, each with **per-device-type tabs**, and Device alarm
  - The account shows Status "On" after creation
  - Regional portals: `intl` and `sg5` for Australian installers
  — [PDF](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/docs/Huawei%20FusionSolar%20Northbound%20API%20Account%20Procedures.pdf); [README](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/README.md)
- FACT: README: "In late 2022 Huawei changed the process… it now requires you to request an API account from the company that installed your Huawei solar system." It recommends one company-wide shared NB account per integration with deadline **2199-12-31**. It notes the service is "only needed while ChargeHQ doesn't support Huawei inverters directly". A successor multi-vendor project is linked (`danwale/SolarUseOptimiser`, `IDataSource`/`IDataTarget`) — [README](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/README.md)

### Inferences
- INFERENCE (bugs, from code reading):
  1. `StationCode = stationListResponse.data[0].stationCode` takes the **first** plant even after matching by name (L153-L158), so multi-plant accounts get the wrong plant.
  2. `GetPlantInformation(pageNumber++)` passes the unincremented value (L274), so it recurses on page 1 forever if the plant is not on page 1.
  3. `battery_discharge_kw` is sent in W, not kW (×1000 error per the doc's unit).
  4. `exported_kwh` = inverter lifetime yield is semantically wrong when no meter exists.
  5. `battery_energy_kwh = charge_cap` (cumulative charged energy), not stored energy.
  6. The battery sign convention is not checked.
- INFERENCE: 3 `getDevRealKpi` calls per 305 s (different devTypeIds) fit both the 2021 "10/min" table and the V6 formula Σ Roundup(devices/100) per 5 min **per device type**. Adding device types adds calls, not latency.
- INFERENCE (EV-charging pattern): cloud-API solar-surplus charging has **5–10 min effective latency**: Huawei aggregates every 5 min, the poll is offset by up to 305 s, and ChargeHQ then adjusts. Good enough for slow "soak up surplus" charging. Not good enough for zero-export or fast load following, which need local Modbus via EMMA/SmartLogger (huawei-solar-lib, `source_code_clients.md` §2). The 5-account cap and shared password make the installer-issued NB account a poor fit for a per-customer EV app. That is a structural reason for OAuth Connect (§3).

### Gaps
- ChargeHQ's own Huawei support status in 2026 (the README said "on the roadmap") was not checked.
- The sign of `ch_discharge_power` (charge vs discharge) in the Northbound API was not confirmed from the doc text extracted.

---

## 5. bresden5/Huawei-Fusion-Solar: what it is

### Takeaway
It is an **IP-Symcon** (German home-automation platform, ≥7.1) PHP module from Feb–May 2026, about 300 LOC. It polls the legacy Northbound `thirdData` API to show PV, house, grid import/export and battery as Symcon variables. It shows that **userName/systemCode Northbound clients were still being written in 2026**. It also shows how easy it is to get key names, units and sign conventions wrong.

### Cited Findings
- FACT: the config form has `BaseUrl` (default `https://eu5.fusionsolar.huawei.com`), `Username` ("API-Kontoname"), `Password` ("API-SystemCode"), optional `StationCode`, and `UpdateInterval` 60–900 s (default **300**). The README is the unfilled Symcon template — [module.php L13-L17](https://github.com/bresden5/Huawei-Fusion-Solar/blob/main/Huawei%20Fusion%20Solar/module.php#L13-L17); [form.json](https://github.com/bresden5/Huawei-Fusion-Solar/blob/main/Huawei%20Fusion%20Solar/form.json); [README](https://github.com/bresden5/Huawei-Fusion-Solar/blob/main/Huawei%20Fusion%20Solar/README.md)
- FACT: flow: `login` (token from the `xsrf-token` response header) → `/thirdData/stations {pageNo:1}` (first `plantCode`, cached) → `getDevList` (called **every update**) → `getDevRealKpi` batched per devTypeId for `[1, 17, 38, 39, 47]`. On 305 it clears the token and recurses without a cap. Any other non-zero failCode throws. No 407 handling — [module.php L68-L163, L178-L308](https://github.com/bresden5/Huawei-Fusion-Solar/blob/main/Huawei%20Fusion%20Solar/module.php#L68-L308)
- FACT: mapping: inverter (1/38) `active_power` kW→W, summed into `TotalPV`, plus a per-inverter variable. Battery (39) reads keys **`soc`** and **`charge_discharge_power`**. Grid (17 or 47) `active_power` is used raw, with **positive = import** (`GridImport = max(grid,0)`). House = `PV + import − export − max(bat,0) + max(−bat,0)` — [module.php L110-L158](https://github.com/bresden5/Huawei-Fusion-Solar/blob/main/Huawei%20Fusion%20Solar/module.php#L110-L158)

### Inferences
- INFERENCE: the NBI keys are `battery_soc` and `ch_discharge_power` (§4 doc citation), so the battery variables will always read 0. Power sensor 47 reports W while grid meter 17 reports kW, but both are treated the same. danwale and Huawei's V7 `meterPower` treat **positive = export**, so bresden5's import/export are probably inverted. Calling `getDevList` every 5 min also ignores Huawei's "≤1/h" recommendation.
- INFERENCE: for product design, three independent hobby clients (bresden5, danwale, HA) each re-derive "house load = PV + grid − battery" with different sign conventions. A platform that publishes a **pre-computed, signed energy-flow object** (Huawei's V7 `plantRealtimeKpi` does this; `thirdData` does not) removes a whole class of integration bugs.

### Gaps
- Whether the module is in the Symcon Module Store and has users: not checked.

---

## 6. Joya-Biswas/solar-panel-efficiency-fusion: what it is

### Takeaway
It is **not related to Huawei FusionSolar**. "Fusion" means multimodal **late fusion** (EfficientNet-B3 image features + XGBoost tabular features) for predicting soiling-related panel efficiency. It runs on **synthetic** data that mimics the Deep Solar Eye dataset. It has no FusionSolar data fields, API usage or device model.

### Cited Findings
- FACT: README: "late-fusion multimodal architecture combining visual features (EfficientNet-B3) and tabular sensor features (XGBoost)", "Synthetic data generator mirroring Deep Solar Eye statistics", reported R² 0.941 / 0.910 / 0.970. No "huawei" or "fusionsolar" string appears in the repo — [README](https://github.com/Joya-Biswas/solar-panel-efficiency-fusion/blob/main/README.md); grep of `solar_fusion.py`
- FACT: constants `P_RATED 250 W`, `TEMP_COEFF −0.004/°C` (IEC 61215), irradiance quality filter `G ≥ 203 W/m²` (cites IEC 61724-1). Synthetic soiling ramps 0–60% over 7 days. Features: `eta_loss, delta_T, eta_loss², eta_loss×delta_T, irradiance_G`; target `eta_true` — [solar_fusion.py L73-L182](https://github.com/Joya-Biswas/solar-panel-efficiency-fusion/blob/main/solar_fusion.py#L73-L182)
- FACT: `eta_loss = 100 − eta_true` (L145) and is used as the primary feature for predicting `eta_true` — [solar_fusion.py L139-L178](https://github.com/Joya-Biswas/solar-panel-efficiency-fusion/blob/main/solar_fusion.py#L139-L178)

### Inferences
- INFERENCE: the target leaks directly into the features, so the reported accuracy says nothing about real-world prediction. Do not use it as a benchmark.
- INFERENCE (tangential product idea): soiling and temperature-corrected PR is an analytics feature that FusionSolar only partly supports. The demo showed PR 0.00 without an EMI sensor (`demo_observations.md` §3), and the NB API exposes `performance_ratio` and `radiation_intensity` only with an EMI. A competitor could offer soiling-loss estimation from inverter data plus satellite irradiance.

### Gaps
- None material for FusionSolar.

---

## 7. reptilex/tesla-style-solar-power-card: energy-flow UI model (reference for a FusionSolar-like widget)

### Takeaway
The card models energy flow as **7 directed, non-negative edge flows** between 4 fixed nodes (Grid, Generation, House, Battery), plus 2 optional appliance leaves on House (e.g. an EV charger). **Node values are derived** as signed sums of incident edges. Animation speed or line thickness is proportional to each edge's power. Signed meter readings must first be split into directional flows, and the README's "APF" templates give the algorithm, including an explicit inverter-loss term. There is no dedicated generator node: "generation" is generic (solar or wind).

### Cited Findings
- FACT: "6 bubbles with 4 main icons and 2 extra appliances". Main nodes: Grid, Generation ("usually solar"), House, Battery. Appliances are "attached to the house" and "controlled directly by their consumption" (e.g. `appliance1_icon: 'mdi:car-sports'`) — [README L21-L47, L180-L188](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md)
- FACT: the 7 main flows are `generation_to_grid`, `generation_to_battery`, `generation_to_house`, `grid_to_battery`, `grid_to_house`, `battery_to_grid`, `battery_to_house`. "You need at least one". Extra per-node text entities (e.g. battery SOC, which also swaps the battery icon) and clickable entities are optional — [README L35-L68, L100-L129](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md)
- FACT: node values come from `calculateIconBubbleData` summing configured edges, where a `-` prefix means subtract, truncated to 2 decimals and converted W→kW above a threshold — [TeslaStyleSolarPowerCard.ts L433-L475](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/TeslaStyleSolarPowerCard.ts#L433-L475):
  - Generation = g→grid + g→house + g→battery
  - Grid = −g→grid + grid→house − battery→grid + grid→battery
  - House = g→house + grid→house + battery→house (optionally − appliances)
  - Battery = g→battery + grid→battery − battery→house − battery→grid
  — [L350-L415](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/TeslaStyleSolarPowerCard.ts#L350-L415)
- FACT: animation: a dot per edge moves at `speed = speedFactor × value / 1000` (default 0.04), driven by `setInterval(…,15)` + `requestAnimationFrame`. Alternative `energy_flow_diagramm` mode sets SVG stroke width ∝ power (factor 2, minimum 0.1 px). Options: `hide_inactive_lines`, `show_gap`, `threshold_in_k`, and `change_house_bubble_color_with_flow` (House coloured by its dominant source: solar/grid/battery) — [SensorElement.ts L78-L90](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/models/SensorElement.ts#L78-L90); [TeslaStyleSolarPowerCard.ts L66-L71, L498-L646](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/src/TeslaStyleSolarPowerCard.ts#L498-L646); [README L130-L180](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md)
- FACT: "here all sensors need to be positive values, so create template sensors". The "APF (Actual PowerFlow)" templates take signed grid (− import / + export), house, generation and battery (+ charge / − discharge). They compute `Inverter Power Consumption = generation − battery − house − grid` (losses and rounding) and `Real House Load = house + inverter consumption`. They then allocate directional flows with min/max rules (e.g. Grid2House = min(grid import, real house load); Batt2Grid for forced discharge). The README notes battery→grid "only happens with battery or other power generator users" — [README L193-L340](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/README.md)
- FACT: no `generator` node or entity exists in `src/` (grep). It is a Lit 2 web component, Apache-2.0 — [package.json](https://github.com/reptilex/tesla-style-solar-power-card/blob/master/package.json)

### Inferences
- INFERENCE (UI design): FusionSolar's plant energy-flow widget (`demo_observations.md` §5.1: PV, Battery with SOC + kW, Grid, Load, animated lines) is the node-centric version of the same idea. FusionSolarPy shows Huawei's backend returns `flow.nodes[]` with device IDs (`source_code_clients.md` §2). An equivalent product should store **signed node powers** (as Huawei's V7 `plantRealtimeKpi`: `pvPower, meterPower, batteryPower, loadPower`) and **derive directed edges** server-side with an APF-like allocator: PV serves load first, then battery, then grid; battery discharge serves load first, and any excess goes to grid. Then UIs, reports ("self-consumption", "from PV vs from grid", as in the demo's energy-management split) and third parties all share one consistent decomposition, including an explicit loss/imbalance term instead of silently mismatched totals.
- INFERENCE (EV/CPO extension): the card's appliance leaf (car) is the minimal EV hook. For a CPO-grade product, the EV charger should be a **first-class node** with its own edges (PV→EV, grid→EV, battery→EV) so "solar share of each charging session" can be computed and billed. Huawei is moving in this direction: the C&I dashboard covers PV + ESS + charger (`demo_observations.md` §7, 2025-03), generator→ESS charging (2025-12) and EV-charger-only plants (§8). Generator and third-party-inverter nodes should be generic "source" nodes, not hard-coded.

### Gaps
- No quantitative usability data. The card is a design reference only.

---

## 8. Additional facts from the bundled V600R023C00 NBI-V6 (2023-01-19) not already in the notes

### Takeaway
The 2023 V6 reference (bundled in danwale's repo) adds a **plant-creation API with an "EV-charger-only plant" flag and tariff configuration**. It formally marks `getStationList` and `getDevFiveMinutes` as going offline. It also states that **new Northbound users cannot call interfaces declared end-of-life**.

### Cited Findings
- FACT (§1.4): "APIs that are reaching the end of lifecycle will be declared in this document… **New northbound users cannot invoke the APIs whose end-of-lifecycle is declared**." §2.3: `getStationList` "is about to go offline" (replacement `/thirdData/stations`, "Queries the plant list based on the grid connection time"). §9.4 "To-Be-Offline Interfaces" lists `getDevFiveMinutes` (limit Σ Roundup(devices of type/10)+24 per day). `getAlarmList` gains query by device SN list — [V600R023C00 NBI-V6](https://github.com/danwale/HuaweiFusionSolar-ChargeHQ-Integration/blob/main/docs/iMaster%20NetEco%20V600R023C00%20Northbound%20Interface%20Reference-V6(SmartPVMS).pdf)
- FACT (§9.3.2, restricted interface; an administrator must authorise it): `POST /thirdData/createStation` creates one plant per call. Limits are 10/min and **1000 plants/day per user** (error 26001). The NB user must have authorised a company, and the plant binds to the first one. Body:
  - `basicConfig{stationName ≤80 chars, stationType 1 residential/2 C&I/3 utility, `**`pureCharge`**` 0/1 = "EV-charger-only plant" (residential only), connectTime (s), linkman, linkmanPho}`
  - `deviceConfig[]{esn, registerCode}` (the SN of any device on a communication module suffices; a registration code is needed for non-directly-connected inverters outside China)
  - `storageConfig{totalStorage kWp | per-device PV params}` (not allowed for charger-only)
  - tariff config with **feed-in and purchase price tables by month/day range × hour range**
  - `additionConfig{areaCode, timeZoneCode, safeRunning, loadStatus}`
  — same PDF, §9.3.2

### Inferences
- INFERENCE: Huawei treats an **EV charger as a plant type** ("pureCharge"), not only as a device inside a PV plant. For a CPO (the reader's domain), this means FusionSolar can host standalone Huawei SCharger sites and expose them through the same Northbound plant/device model. A comparable product should support charger-only sites with no PV capacity or grid-connection date.
- INFERENCE: TOU tariffs (month/day × hour ranges, separate buy and sell) are part of the plant aggregate at creation time, consistent with the demo's per-plant currency and revenue (`demo_observations.md` §5.1).

### Gaps
- Response schema of `createStation` and the full field list for `storageConfig`/`PVParams` were not extracted in detail.

---

## 9. Cross-check: demo-observed internal web endpoints vs FusionSolarPy (v0.1.1, 2026-04-25)

### Takeaway
They share the same namespace and conventions (`/rest/dpcloud`, `/rest/pvms/web`, `/rest/pvms/fm`, `/rest/neteco/web`, DN-keyed GET params, numeric signal IDs). **7 paths match exactly**, and parameters are compatible. The main divergence is the **plant overview/energy flow**. On 2026-10-07 the demo page polled `/rest/dp/pvms/station/v1/overview/running-status` (new `dp/pvms` prefix). FusionSolarPy uses `/rest/pvms/web/station/v1/overview/{energy-flow, energy-balance, station-real-kpi}`, which the demo page did not call.

### Cited Findings
- FACT: FusionSolarPy endpoint list (`grep` of `client.py`, commit 3e02b9f) — [client.py](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py); demo list — `demo_observations.md` §8.

| Path | Demo (2026-10-07) | FusionSolarPy | Note |
|---|---|---|---|
| `/rest/dpcloud/auth/v1/keep-alive` | ✔ | ✔ (L491) | exact |
| `/rest/dpcloud/auth/v1/is-session-alive` | ✔ | ✔ (L471) | exact |
| `/rest/pvms/web/station/v1/station/total-real-kpi` | ✔ `queryTime, timeZone=7` | ✔ `queryTime, timeZone=1` (L514-L519) | exact; `timeZone` is an integer hour offset |
| `/rest/pvms/web/station/v1/station/station-list` (POST) | ✔ | ✔ (L586) | exact |
| `/rest/neteco/web/config/device/v1/device-list` | ✔ `parentDn, signals=…, noIncludeMocIds, maintenance` | ✔ `parentDn, mocTypes=…` (L613) | same path, different filters |
| `/rest/pvms/web/device/v1/device-history-data` | ✔ `showDst=true, signalIds=30014&30017, deviceDn, date` | ✔ `signalIds` (30014/30016/30017), `deviceDn, date` (L639-L648) | exact; demo adds `showDst` |
| `/rest/pvms/web/device/v1/device-realtime-data` | ✔ `displayAccessModel=true` | ✔ `deviceDn` (L663) | exact path |
| `/rest/pvms/fm/v1/statistic` vs `/rest/pvms/fm/v1/query` (POST) | statistic | query (L682) | same FM service, different operation |
| `/rest/neteco/web/organization/v2/check-shared-mo` vs `…/v2/company/current` | check-shared-mo | company/current (L426) | same family |
| `/rest/pvms/web/station/v1/layout/*` | sheet/query-sheets, device-tree-page, device-energy, … | optimizer-info (L1090) | same family |
| `/rest/dp/pvms/station/v1/overview/running-status` | ✔ (polled ~5 s) | ✗ | demo-only |
| `/rest/pvms/web/station/v1/overview/energy-flow`, `/energy-balance`, `/station-real-kpi` | ✗ not seen | ✔ (L946, L976, L542) | FusionSolarPy-only |
| `/rest/pvms/web/device/v1/query-battery-dc`, `/deviceExt/set-config-signals` | ✗ (no battery module page / write as guest) | ✔ (L861, L926) | FusionSolarPy-only |
| `/unisso/*`, `/unisess/*` | ✗ (demo used guest auto-login) | ✔ (L273-L359) | FusionSolarPy-only |

- FACT: signal IDs agree: 30014 and 30017 are defaults in both (demo labels: "Công suất thuần" = active power and "Tổng công suất đầu vào" = total input power).

### Inferences
- INFERENCE: the demo's `timeZone=7` (viewer in UTC+7) vs FusionSolarPy's `1`/`2` (Europe) confirm that `timeZone` is the client's integer UTC offset. Data aggregation therefore depends on a client-supplied offset, and DST is a separate flag (`showDst`, and `timeZoneStr` in energy-balance).
- INFERENCE: the overview energy flow appears to have moved, at least for this account or tenant type, to a `dp/pvms` "running-status" endpoint. FusionSolarPy's `energy-flow` may still work for other tenants (it was last confirmed working 2026-04-25 per its changelog) or may be a legacy path. This is the kind of churn `source_code_clients.md` §5 documents, and it reinforces "do not build commercial integrations on the portal API".

### Gaps
- Whether `/rest/pvms/web/station/v1/overview/energy-flow` still answers on intl today: not tested (no login allowed).

---

## 10. Implications: (a) Java/Spring integration, (b) designing an equivalent product

### Takeaway
(a) Treat Huawei's Northbound as three generations and code to them deliberately:
- legacy `thirdData` with an installer-issued account: works today, but is capped at 5 accounts per company, uses a shared password, and its third-party use is being retired by partners such as EnergyID
- `thirdData`-V6 with resource-based quotas and end-of-life rules for new users
- OAuth Connect (owner consent) with async control APIs

Implement token reuse for up to 30 min idle, per-interface rate limits taken from the documented table, and async task tracking for control.

(b) Build an equivalent product around a server-side, signed energy-flow model with derived directed edges, owner-consent grants, explicit async command tasks, and first-class EV-charger nodes and sites.

### Cited Findings
- FACT: token TTL 30 min idle, login 1/min, session resource per login (§1). 20-min proactive renewal in huawei_client and EnergieID (§2, §3). Per-interface limits and refresh cadences (§1 table). End-of-life interfaces are blocked for new NB users (§8). VPP/control as async tasks with requestID/remoteID/status (§1). EnergyID moved to an owner-login grant and retires legacy on 1 Dec 2026 (§3). Max 5 NB accounts per company with globally unique names (§4). Unit and sign pitfalls in three community clients (§4, §5).
- FACT (licences): EnergieID, danwale, huawei_client and Joya-Biswas are MIT. Tesla card is Apache-2.0 (patent grant, NOTICE obligations). bresden5 has **no licence** (all rights reserved by default, so do not copy code).

### Inferences
**(a) Java/Spring (INFERENCE)**
- Auth: `NorthboundSession` per (region host, account). Read the token from the `xsrf-token` response header and fall back to the `XSRF-TOKEN` cookie (the 2021 change, §1). Send it as the `XSRF-TOKEN` header. Renew proactively at about 20–25 min of **idle** time; any request extends the session. Handle 305 with a single-flight re-login capped at 1 retry. Call `/thirdData/logout` on shutdown to free the "client login resource". Never log in per poll. Guard login with a 1/min limiter.
- Rate limiting: Resilience4j `RateLimiter` per (account, interface) using the table in §1. Also use a scheduler that follows the documented **data refresh cadence**: real-time KPIs every 5 min (305 s, as danwale does), hour/day aggregates hourly, month/year daily, plant/device lists hourly at most. Treat 407 as wait ≥60 s and 20618 as stop until the next day, as already noted.
- Version awareness: prefer `stations` over `getStationList` and `getDevHistoryKpi` over `getDevFiveMinutes`. New NB users are blocked from end-of-life calls (§8). Do not wrap `devOnOff`, `devUpgrade`, `getDevUpgradeInfo` or `getDevKpiHour` (§3).
- Deserialisation: Jackson with `devTypeId` as an `int` code mapped to an extensible enum with an `UNKNOWN` fallback (avoid huawei_client's u8 enum failure). Use `BigDecimal` that accepts number or string, and treat `"N/A"`, `"--"`, `"-"` and `null` as null (danwale, FusionSolarPy). Use `Long` device IDs. Normalise units per (devTypeId, key) from the NBI indicator tables: e.g. power sensor 47 `active_power` W vs grid meter 17 kW, battery `ch_discharge_power` W, SOC %. Normalise signs to one documented convention, e.g. grid + = export as in V7 `meterPower`.
- TLS: never copy the "disable certificate verification" advice (2019 guide, danwale). Use the JVM truststore.
- Control (OAuth Connect / V7-style): model `ControlTask{requestId (unique Long), plantCodes ≤100, type, params, perDeviceRemoteIds, status}`. Poll status (0/1/2, 24 h timeout) at most 100/min, and reject a new task for a plant while one is in progress.
- EV/CPO use: for solar-surplus charging at a CPO site with Huawei PV, the cloud path yields about 5–10 min latency (§4). Use it for reporting and slow surplus allocation. Use EMMA/SmartLogger Modbus (`source_code_clients.md` §2) or Huawei SCharger local control for minute-level load following. Push to the charging backend through an internal `SiteMeter`-like DTO (production, net import, consumption, battery SOC/power), mirroring ChargeHQ's push contract, which is simple, vendor-neutral and has an explicit `error` field.

**(b) Equivalent product (INFERENCE)**
- Energy-flow model: store signed node powers per 5-min (or faster) sample. Compute directed edges server-side with an explicit loss term (the APF approach, §7) and expose both. Render the UI with edge-proportional animation or line width. Treat EV chargers and generators as first-class nodes, and support charger-only sites (Huawei `pureCharge`, §8).
- Consent and access: per-owner OAuth grants with scopes (read / control), not shared installer accounts capped at 5 with a shared password (§4). Keep SN + owner-identity or authorization-code enrolment as a bulk on-ramp for aggregators (Huawei V7 `snEnrolment`/`acEnrolment`, §1).
- Public API hygiene, avoiding Huawei's pain points: publish limits and refresh cadences per endpoint (Huawei does this in the PDF, but enforces them through HTTP 200 + failCode). Return numbers with units in the schema. Use one sign convention. Include `measuredAt` separately from `serverTime` (danwale had to use `params.currentTime`). Declare deprecations with dates. Offer webhooks or MQTT so EV-surplus apps do not need 305-s polling.

### Gaps
- OAuth Connect endpoint URLs, token lifetimes and flow-control numbers are still not found in any public source read (§1, §3).
- Real behaviour of legacy `thirdData` accounts after 1 Dec 2026 (whether Huawei or only EnergyID ends them) is unknown.
