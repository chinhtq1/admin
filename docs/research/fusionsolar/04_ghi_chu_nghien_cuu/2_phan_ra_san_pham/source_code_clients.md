# FusionSolar from community source code: what open-source clients reveal about the platform (Oct 2026)

Scope and method. I cloned these repos (read-only, nothing was built or run, and no Huawei endpoint was called) into the scratchpad and read the source. Repo, branch and HEAD at the time of reading:
- `pjugowiec/fusion-solar-unofficial-client` (main @0bb1790, last commit 2023-06-18), **MIT**
- `guillaumeblanc/pyhfs` (main @e15b89d, last commit 2023-08-21, v0.1.2), **MIT**
- `tijsverkoyen/HomeAssistant-FusionSolar` (master @2235c79, last commit 2026-09-28), **MIT**
- `jgriss/FusionSolarPy` (PyPI `fusion_solar_py`) (main @3e02b9f, last commit 2026-04-25, v0.1.1), **MIT**
- `wlcrs/huawei-solar-lib` (develop @19dfcfb, last commit 2026-08-21), **AGPL-3.0**
- `wlcrs/huawei_solar` (main @22f7610, last commit 2026-09-29, manifest v2.1.5), **AGPL-3.0**

This note builds on `Nền tảng Huawei FusionSolar/api_integration.md` and `Phân rã sản phẩm FusionSolar/workflows_data_model.md` and records only what is new or corrected. Labels: **FACT** = seen directly in code or README. **INFERENCE** = my reading of how the code would behave, or a reasoned conclusion. **SPECULATION** = plausible but unverified. The GitHub REST/search API and the GitHub issue pages were not reachable from this session (403 / robots.txt), so I could not read star counts or issue threads. Commit messages from the clones were used to date breakages instead.

---

## 1. What pjugowiec/fusion-solar-unofficial-client is and how it works

### Takeaway
It is a small (≈514 LOC, 21 files) **Java 17 / Maven / Retrofit 2.9 + Gson + Lombok** wrapper around the **official Northbound API (`/thirdData/*`)**. It does not touch the web portal's internal endpoints (no `/rest/pvms/web`, `/unisso`, RSA, captcha or region redirect). It covers login plus 7 read endpoints at plant and device-list level. It has no device-KPI, alarm, paging, 305 re-login, 407 back-off or `failCode` handling, and it has not been updated since June 2023. It is useful as a DTO reference for a Java port, not as a production dependency.

### Cited Findings
**Stack and packaging**
- FACT: `groupId com.fusion`, `artifactId fusion-solar-unofficial-client`, `version 1.1.0`. Dependencies: `retrofit` 2.9.0, `converter-gson` 2.9.0, `gson` (version bound to `${retrofit.version}` = 2.9.0), `lombok` 1.18.22. Distributed via GitHub Packages (`maven.pkg.github.com/pjugowiec/...`) — [pom.xml](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/pom.xml)
- FACT: the pom sets `maven.compiler.source/target` = 17, but the `maven-compiler-plugin` configuration overrides this with `<source>8</source><target>8</target>`, while the code uses `String.isBlank()` (Java 11+) — [pom.xml](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/pom.xml); [FusionSolarUtil.java L12-20](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarUtil.java#L12-L20)
- FACT: commit history has only 9 commits: initial code 2022-03-29, refactor/rename + Maven wrapper + GitHub Packages 2023-06-18, MIT `LICENSE` added 2023-06-18 ("Copyright (c) 2023 Patryk Jugowiec"). There are no tests — `git log` of the clone; [LICENSE](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/LICENSE)
- FACT: the README says that to get an API account "you must write a mail with the SN of the inverter", after which support sends the API documentation and login data. It cites Huawei forum thread "communicate-with-fusionsolar-through-an-openapi-account" (591478-100027) — [README](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/README.md)

**API family and endpoints (all `POST`, JSON, Retrofit interface `FusionSolarRestClient`)** — [FusionSolarRestClient.java L9-35](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarRestClient.java#L9-L35)

| Method (Java) | Path | Request body | Response DTO |
|---|---|---|---|
| `login(userName, password)` | `/thirdData/login` | `LoginFusionSolar{userName, systemCode}` | `BaseResponse`; token read from the response **header** `xsrf-token` |
| `getStationList()` | `/thirdData/getStationList` | none (no `@Body`) | `StationList{data: List<Station>}` |
| `getStationRealKpi(stationCodes)` | `/thirdData/getStationRealKpi` | `BaseRequest{stationCodes}` | `StationRealKpiList` |
| `getStationHourKpi(codes, collectTime)` | `/thirdData/getKpiStationHour` | `BaseRequest{stationCodes, collectTime}` | `StationKpiList` |
| `getStationDayKpi` | `/thirdData/getKpiStationDay` | same | `StationKpiList` |
| `getStationMonthKpi` | `/thirdData/getKpiStationMonth` | same | `StationKpiList` |
| `getStationYearKpi` | `/thirdData/getKpiStationYear` | same | `StationKpiList` |
| `getDevList(stationCodes)` | `/thirdData/getDevList` | `BaseRequest{stationCodes}` | `DevList{data: List<DevItem>}` |

- FACT: every call after login sends the header `xsrf-token: <token>` (constant `XSRF_TOKEN = "xsrf-token"`) — [FusionSolarRestClient.java L10-34](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarRestClient.java#L10-L34)
- FACT: the default base URL is `https://eu5.fusionsolar.huawei.com`. Gson date format is `yyyy-MM-dd'T'HH:mm:ss.SSS` (unused, since all times are epoch ms) — [FusionSolarRestClientFactory.java L15-41](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarRestClientFactory.java#L15-L41)
- FACT: the Javadoc for `collectTime` says the hour query returns "hour KPI data for one day (the background processes milliseconds based on the time zone where the power station is located)". The same text is copy-pasted for the day, month and year methods — [FusionSolarClient.java L41-79](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarClient.java#L41-L79)

**Auth/session**
- FACT: `login()` builds `{userName, systemCode}`, executes the call, extracts the `xsrf-token` header (throwing `FusionSolarException("Token not exists in header")` if it is absent or blank), stores it in the instance field `token` and returns it. There is no logout, no expiry tracking and no re-login — [FusionSolarClientImpl.java L22-32](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarClientImpl.java#L22-L32); [FusionSolarUtil.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarUtil.java)
- Contrast: pyhfs reads the token from the **`XSRF-TOKEN` cookie**, while this client and the HA integration read it from the **`xsrf-token` response header**. Huawei therefore sends it in both places — [pyhfs session.py L64-71](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/session.py#L64-L71); [HA openapi_api.py L29-49](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py#L29-L49) (FACT that the clients differ; INFERENCE that both work)

**Data model (DTOs, package `...response`)**
- FACT `BaseResponse`: `success (boolean)`, `params (BaseParamsResponse)`, `message (String)`, `failCode (Integer)`, `buildCode (String)`. The `buildCode` field does not appear in the other clients — [BaseResponse.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/BaseResponse.java)
- FACT `BaseParamsResponse` (the echo of request parameters): `currentTime (Long)`, `collectTime (Long)`, `stationCodes (String)` — [BaseParamsResponse.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/BaseParamsResponse.java)
- FACT `Station`: `aidType (Integer)`, `buildState (String)`, `capacity (Double)`, `combineType (String)`, `linkmanPho`, `stationAddr`, `stationCode`, `stationLinkman`, `stationName` — [Station.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/Station.java)
- FACT `StationRealKpi{stationCode, dataItemMap: DataItemStationRealKpi}`. All `DataItemStationRealKpi` fields are **Strings**: `day_power, month_power, total_power, day_income, total_income, real_health_state` — [DataItemStationRealKpi.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/DataItemStationRealKpi.java)
- FACT `StationKpi{collectTime: Long, dataItemMap: DataItem}`. All `DataItem` fields are Doubles: `radiation_intensity, theory_power, inverter_power, ongrid_power, power_profit, installed_capacity, performance_ratio, use_power, perpower_ratio, reduction_total_co2, reduction_total_coal, reduction_total_tree`. `stationCode` is **not** mapped on `StationKpi`, although the real response carries it (see pyhfs fixtures, §4) — [StationKpi.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/StationKpi.java); [DataItem.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/DataItem.java)
- FACT `DevItem`: `devName`, `devTypeId (Double)`, `esnCode`, `id (Double)`, `invType`, `latitude`, `longitude`, `optimizerNumber (Double)`, `softwareVersion`, `stationCode`. **`optimizerNumber` is a device-list field not recorded in the earlier notes** — [DevItem.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/response/DevItem.java)

**Error handling, retries, rate limiting**
- FACT: `executeCall` throws `FusionSolarException` only when the HTTP status is not 2xx (`"Problem with execute call: " + message`) or on `IOException`. It never inspects `success` or `failCode`. The exception class is package-private — [FusionSolarClientImpl.java L96-106](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarClientImpl.java#L96-L106); [FusionSolarException.java](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarException.java)
- FACT: there is no retry, back-off, rate limiter, batching to 100 codes, timeout configuration or OkHttp interceptor anywhere in the source tree (entire `src/` read).
- FACT: the README and source mention no breakage. Issues could not be read (GitHub pages robots-blocked, API 403 in this session).

### Inferences
- INFERENCE (code reading): **`setBaseUrl()` does not affect an existing client.** `FusionSolarClientImpl` captures `restClient` in a `final` field at construction ([L15](https://github.com/pjugowiec/fusion-solar-unofficial-client/blob/main/src/main/java/com/fusionSolarUnofficialClient/FusionSolarClientImpl.java#L15)). `setBaseUrl` only replaces the static singleton in the factory. Changing region (e.g. `intl`, `au5`) works only if `setBaseUrl` is called on an existing client *before* a second client is created, and the base URL is global static state shared by all clients in the JVM.
- INFERENCE: because 305/407/20xxx come back as HTTP 200 with `success:false`, this client silently returns a DTO with `data == null` in those cases. Callers must check `getSuccess()`/`getFailCode()` themselves.
- INFERENCE: the `<source>8</source><target>8</target>` + `isBlank()` mismatch means the jar compiles on JDK 17 but would throw `NoSuchMethodError` on a Java 8 runtime. This is harmless on Java 11+.
- INFERENCE: mapping `id`/`devTypeId` to `Double` risks rendering IDs as `1.0E15`-style values when they are re-serialised into `devIds` strings for `getDevRealKpi`. A port should use `Long`/`Integer`.
- INFERENCE: the README's account-acquisition advice ("mail with SN of inverter") reflects the pre-2023 process. It is superseded by the installer-side Northbound Management flow and the 2025 owner-consent toggle documented in `api_integration.md`.

### Gaps
- Stars, forks, open issues and any user reports for the repo: GitHub API/HTML were not accessible from this session.
- Whether the GitHub Packages artifact is still downloadable without auth: not checked.

---

## 2. The four API surfaces seen in community code (Northbound, web-portal internal, kiosk, local Modbus) — new endpoints only

### Takeaway
Community code confirms four distinct surfaces with different auth, stability and data richness:
- **Northbound `/thirdData/*`**: POST JSON with an XSRF token, rate-limited and stable.
- **Web-portal internal `/rest/...` + `/unisso/*` SSO**: browser session, RSA-encrypted password, captcha, keep-alive, `roarand` header. It is the richest surface (energy-flow, per-signal history, battery modules, alarms, writes) and the most brittle.
- **Kiosk**: an anonymous GET with a share token.
- **Local Modbus**: TCP/RTU with a proprietary login and file-transfer extension (function 0x41).
New facts in this section: extra Northbound device-KPI endpoints and a `logout` endpoint (HA Postman collection), and the full web-portal endpoint list with parameters (FusionSolarPy).

### Cited Findings
**Northbound: endpoints not in earlier notes**
- FACT: the HA repo ships a Postman collection listing `POST /thirdData/logout` with body `{"xsrfToken": "..."}`. It also lists device-level history endpoints `getDevFiveMinutes`, `getDevKpiDay`, `getDevKpiMonth`, `getDevKpiYear`, each taking `{devIds, devTypeId, collectTime}`. This confirms the paths that `api_integration.md` §1 listed as a gap ("implied by Eniris but not confirmed") — [docs/postman_collection.json](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/postman_collection.json)
- FACT: the same collection shows `getAlarmList` with only `stationCodes`. The pyhfs fixture's echoed `params` additionally contain `sns`, `devTypes` ("1,2,38,46,62"), `levels` ("1,2,3,4"), `language`, `beginTime`, `endTime`. These are the optional alarm filters (filter by device SN, device types and severity levels) — [postman_collection.json](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/postman_collection.json); [pyhfs tests/data/getAlarmList.json](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/tests/data/getAlarmList.json)
- FACT: `stations` (paged) vs `getStationList` (legacy). On 2023-02-28 HA switched to `/thirdData/stations` for `au5.fusionsolar.huawei.com` because "getStationList is deprecated for certain devices". The current code calls `getStationList` first and falls back to `stations` when failCode 401 is returned — HA commit 85b742a (2023-02-28); [openapi_api.py L51-101](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py#L51-L101)
- FACT: HA requests the year KPI with `collectTime` set to **1 Jan of next year 00:00 UTC** — [openapi_api.py L112-124](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py#L112-L124)
- FACT: HA's device-type → label map additionally names 45 PLC, 46 Optimizer, 62 Dongle, 63 Distributed SmartLogger, 70 Safety box, 23070 EMMA. The types allowed for `getDevRealKpi` are 1, 10, 17, 38, 39, 41, 47, 23070 — [openapi/device.py L60-76](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/device.py#L60-L76); [device_real_kpi_coordinator.py L82-109](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/device_real_kpi_coordinator.py#L82-L109)
- FACT: EMMA (23070) real-time KPI keys used by HA (added 2026-07-05, PR #305): `ab_u, bc_u, ca_u, a_i, b_i, c_i, active_power, active_power_a/b/c, reactive_power, power_factor, active_cap, reverse_active_cap, positive_reactive_top, positive_reactive_valley, run_state`, plus **`ex_active_power, ex_active_cap, ex_reverse_active_cap`** ("External measurement (ex_ fields — secondary measurement point on EMMA)") — [sensor.py ~L655-760](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/sensor.py)

**Kiosk (new detail only)**
- FACT: the public kiosk page URL looks like `https://eu5.fusionsolar.huawei.com/pvmswebsite/nologin/assets/build/index.html#/kiosk?kk=XXX`. The integration regex-extracts `kk` and derives the API host from the URL's scheme and netloc — [README](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/README.md); [kiosk/kiosk.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/kiosk/kiosk.py)
- FACT: the README says kiosk "realtime" data "is cached at FusionSolars end for **30 minutes**", although the integration polls every 600 s. The kiosk JSON can be `null`, which was guarded against on 2026-06-10 — [README](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/README.md); [kiosk_api.py L22-51](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/kiosk/kiosk_api.py#L22-L51); HA commit log 2026-06-10

**Web-portal internal API (FusionSolarPy, v0.1.1)** — all on `https://{subdomain}.fusionsolar.huawei.com`; GET unless noted; `_=<epoch ms>` cache-buster on most calls — [client.py](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py)

| Purpose | Method + path | Key params | Key response fields |
|---|---|---|---|
| RSA key / login-mode probe | GET `eu5.../unisso/pubkey` (hard-coded eu5) | — | `enableEncrypt`, `pubKey`, `version`, `timeStamp` |
| Login (legacy) | POST `/unisso/v2/validateUser.action` | query `decision=1`, `service=https://{sub}/unisess/v1/auth?service=/netecowebext/home/index.html#/LOGIN`; JSON `{organizationName:"", username, password[, verifycode]}` | `errorCode`, `errorMsg`, `respMultiRegionName` |
| Login (encrypted, "v3") | POST `/unisso/v3/validateUser.action` | query `timeStamp` (from pubkey), `nonce` (16 random bytes hex); password RSA-encrypted | same |
| Captcha check / fetch / pre-validate | GET `/?service=%2Funisess%2Fv1%2Fauth...` (looks for `#verificationCodeInput`), GET `/unisso/verifycode?timestamp=`, POST `/unisso/preValidVerifycode` form `{verifycode, index:0}` | — | image bytes |
| Session alive | GET `/rest/dpcloud/auth/v1/is-session-alive` | — | `code` (0 = alive) |
| Keep-alive | GET `/rest/dpcloud/auth/v1/keep-alive` | — | `code`, `payload` → sent as header **`roarand`** |
| Current company | GET `/rest/neteco/web/organization/v2/company/current` | — | `data.moDn` (company DN); `exceptionId` "Query company failed."/"bad status" on wrong subdomain |
| Logout | GET `/unisess/v1/logout?service=https://{sub}` | — | — |
| Account-wide power | GET `/rest/pvms/web/station/v1/station/total-real-kpi` | `queryTime`, `timeZone` | `data.currentPower`, `dailyEnergy`, `cumulativeEnergy` |
| Plant real KPI | GET `/rest/pvms/web/station/v1/overview/station-real-kpi` | `stationDn`, `clientTime`, `timeZone` | `data` |
| Plant list | **POST** `/rest/pvms/web/station/v1/station/station-list` | JSON `{curPage, pageSize, gridConnectedTime, queryTime, timeZone, sortId:"createTime", sortDir:"DESC", locale}` | `success`, `data.list[]` (each with `dn`) |
| Device list | GET `/rest/neteco/web/config/device/v1/device-list` | `conditionParams.parentDn` (company or plant DN), `conditionParams.mocTypes=20814,20815,20816,20819,20822,50017,60066,60014,60015,23037` | `data[].mocTypeName`, `data[].dn` |
| Per-signal history | GET `/rest/pvms/web/device/v1/device-history-data` | repeated `signalIds` (default 30014, 30016, 30017; battery 30005, 30007), `deviceDn`, `date` | time series |
| Device real-time | GET `/rest/pvms/web/device/v1/device-realtime-data` | `deviceDn` | `data[i].signals[]` with `name`, `value`, `realValue` |
| Battery module signals | GET `/rest/pvms/web/device/v1/query-battery-dc` | `sigids` (CSV), `dn`, `moduleId` 1–4 | signal values |
| Alarms | **POST** `/rest/pvms/fm/v1/query` | JSON `{dataType:"CURRENT", domainType:"OC_SOLAR", pageNo, pageSize, nativeMeDn}` | alarm page |
| Energy-flow diagram | GET `/rest/pvms/web/station/v1/overview/energy-flow` | `stationDn` (e.g. `NE=33594051`) | `data.flow.nodes[]` (`name` e.g. contains `energy_store`, `devIds[]`) |
| Day energy balance | GET `/rest/pvms/web/station/v1/overview/energy-balance` | `stationDn`, `timeDim=2`, `queryTime` (day start), `timeZone`, `timeZoneStr` | `xAxis[]` + parallel series and day totals (below) |
| Optimizer layout | GET `/rest/pvms/web/station/v1/layout/optimizer-info` | `inverterDn` | optimizer list |
| **Write**: active power control | **POST** form `/rest/pvms/web/device/v1/deviceExt/set-config-signals` | `dn` = Dongle DN, `changeValues=[{"id":"230190032","value":"0|5|6|7"}]` (No limit / Zero export / Limited kW / Limited %) | — |

- FACT: the README documents the energy-balance keys `totalSelfUsePower, selfProvide, totalBuyPower, totalProductPower, totalUsePower, totalOnGridPower, onGridPowerRatio, buyPowerRatio, selfUsePowerRatioByProduct, existInverter, existCharge, existMeter, existEnergyStore, existUsePower, selfUsePower, dischargePower, chargePower, onGridPower, disGridPower, productPower, usePower`. Missing values come back as the string `"--"` — [README](https://github.com/jgriss/FusionSolarPy/blob/main/README.md); [client.py `get_last_plant_data`](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py)
- FACT: battery module signal IDs are a 9-digit family `2303202xx–2303206xx` (per module 1–4: DC/DC working status, SN, SOC, charge/discharge power, temperature, daily charge/discharge energy, bus V/A, "FE connection" with 0–23 link states, battery-pack SN/firmware/status/voltage/temps/capacity/SOC/fuse status) — [signals.md](https://github.com/jgriss/FusionSolarPy/blob/main/signals.md); [constants.py](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/constants.py)

**Local Modbus (huawei-solar-lib) — structure not already noted**
- FACT: registers are declared as typed `RegisterDefinition` objects (`U16Register`, `I32Register`, `U32Register`, `StringRegister`, period/TOU types). Each carries `register` address, `length`, `unit` (a string, an enum dict or a callable), `gain`, `writeable`, `readable`, and a `TargetDevice` flag (`SUN2000 | EMMA | SCHARGER | SDONGLE | SMARTLOGGER`) — [register_definitions/base.py](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/register_definitions/base.py); [registers.py](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/registers.py)
- FACT: the map is split into dicts merged into `REGISTERS`: inverter core (L41), `PV_REGISTERS` (L314), `BATTERY_REGISTERS` (L367), `CAPACITY_CONTROL_REGISTERS` (L650), `EMMA_REGISTERS` (L673), `SCHARGER_REGISTERS` (L908), `METER_REGISTERS` (L922), `SDONGLE_REGISTERS` (L950), `SMARTLOGGER_REGISTERS` (L1093), `SMARTLOGGER_POWER_METER_REGISTERS` (L1619). That is roughly 540 register entries (grep count). Examples: EMMA inverter active power 30364 (I32 W), EMMA external meter active power 30520. SCharger: ESN 30015, software version 30031, rated power 30076 (kW/10), model 30078, phase voltages 30500/30502/30504, total energy charged 30506 (kWh/1000), temperature 30508 — [registers.py L673-920](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/registers.py#L673-L920)
- FACT: device classes are chosen by model-name prefix: `SUN2000Device` (default), `EMMADevice` ("SmartHEMS"), `SChargerDevice` ("FusionCharge"), `SDongleDevice` ("SDongle"), `SmartLoggerDevice` ("SmartLogger"), `MeterDevice` ("PowerMeter"/"Meter"). Discovery uses Modbus "Read Device Identification" objects, parsed as `key=value;` strings (1 model, 2 software version, 3 interface protocol version, 4 ESN, 5 device id/unit, 6 feature version, 8 product type) — [device/__init__.py L43-60](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/device/__init__.py#L43-L60); [device_discovery.py](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/device_discovery.py)
- FACT: Huawei extends Modbus with **function code 0x41** sub-functions. 0x24 = login challenge and 0x25 = login (username + `HMAC-SHA256(key=SHA256(password), msg=challenge)`). 0x05/0x06/0x0C = start/frame/complete **file upload** with a CRC16 check, used for optimizer real-time data (file type 0x44) and optimizer system info (0x45). A **heartbeat** write to register **49999** every **15 s** keeps the installer login alive, and the client re-logs in after a reconnect — [modbus_pdu.py L21-75, L144-289](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/modbus_pdu.py); [modbus_client.py L38-50, ~L177-300](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/modbus_client.py); [device/base.py L25, L214-300](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/device/base.py); [files.py](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/files.py)
- FACT: transport defaults: `DEFAULT_TCP_PORT = 502`, `DEFAULT_UNIT_ID = 0`, `DEFAULT_TIMEOUT = 10` s ("especially the SDongle can react quite slowly"), `DEFAULT_WAIT_AFTER_CONNECT = 1.0` s, a 0.05 s cooldown between requests, a forced reconnect after 5 consecutive timeouts, and tenacity retries (exponential 1–10 s). The HA integration defaults to port 502 and slave ID 0. **Correction to `api_integration.md` §2**, which cited 6607 as primary and slave ID 1 from the wiki: the current code defaults are 502 / unit 0 — [modbus_client.py L38-50](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/modbus_client.py#L38-L50); [huawei_solar const.py L6-7](https://github.com/wlcrs/huawei_solar/blob/main/const.py#L6-L7)
- FACT: HA huawei_solar polling: inverter, meter and battery every **30 s**, configuration every 15 min, optimizers every 5 min. Write services: `forcible_charge(_soc)`, `forcible_discharge(_soc)`, `stop_forcible_charge`, `set_tou_periods`, `set_capacity_control_periods`, `set_fixed_charge_periods`, `set_maximum_feed_grid_power(_percent)`, `reset_maximum_feed_grid_power`, `set_zero_power_grid_connection`, `set_di_active_power_scheduling` — [const.py L20-44](https://github.com/wlcrs/huawei_solar/blob/main/const.py#L20-L44); [services.yaml](https://github.com/wlcrs/huawei_solar/blob/main/services.yaml)

**Other clients**
- FACT: a web search for Java/Node FusionSolar clients found only the Node-RED node `@hermannp/node-red-getproduction-fusionsolar` (already in `api_integration.md`) — [flows.nodered.org](https://flows.nodered.org/node/@hermannp/node-red-getproduction-fusionsolar). No other maintained Java client was found. GitHub repo search was not available in this session.

### Inferences
- INFERENCE: the web portal's device model uses **DNs** (`NE=<digits>`, `moDn`) and **MOC type IDs** (2081x/2082x family, plus 23037, 50017, 600xx) with **numeric signal IDs** (5-digit 300xx for KPIs, 9-digit 2301900xx/2303202xx for config and module signals). The Northbound API instead exposes a simplified `devTypeId` + snake_case `dataItemMap`. So the Northbound layer is a projection or adapter over an internal NetEco signal model, consistent with the "Device Type List" 2081x taxonomy noted in `workflows_data_model.md` §8.
- INFERENCE: writes such as active power control in the portal are "set config signal on the gateway (Dongle) DN". This matches the hypothesis in `workflows_data_model.md` that cloud commands are relayed through the communication device.

### Gaps
- Exact response shapes for `device-history-data`, `fm/v1/query` and `station-list`: there are no fixtures in FusionSolarPy, only parsing code.
- The meaning of most 300xx signal IDs: only a few are named in code (30005/30007 battery, 30014/30016/30017 defaults).

---

## 3. Authentication, session and region routing (new details)

### Takeaway
The Northbound login is a single POST that returns an XSRF token (header and cookie). The session can be ended explicitly with `/thirdData/logout`, and clients re-login on failCode 305. The web portal uses a CAS-like SSO (`/unisso` → `/unisess/v1/auth?service=…`). Since about Aug 2024 the password is RSA-OAEP(SHA-384)-encrypted with a server public key (the "v3" login). A multi-region response (`errorCode "470"` + `respMultiRegionName`) tells the client which regional host to finish the session on. A captcha appears when logins are too frequent, and the session must be kept alive by polling. Local Modbus has its own challenge-response installer login.

### Cited Findings
- FACT (pyhfs): `Session.post()` loops: on `_305_NotLogged` it calls `login()` again and retries, **without a retry cap**. `login()` clears cookies first. `logout()` only discards the `requests.Session` and does not call `/thirdData/logout` — [pyhfs session.py L52-108](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/session.py#L52-L108)
- FACT (HA): `_do_call` logs in lazily when the token is `None`. On 305 it nulls the token and recurses, also unbounded — [openapi_api.py L161-205](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py#L161-L205)
- FACT (Northbound logout): `POST /thirdData/logout {"xsrfToken": ...}` — [postman_collection.json](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/docs/postman_collection.json)
- FACT (portal login sequence): (1) GET `eu5…/unisso/pubkey` → `enableEncrypt`. (2) If true, POST `/unisso/v3/validateUser.action?timeStamp=…&nonce=…` with the password URL-encoded, split into 270-char chunks, each RSA-OAEP(MGF1-SHA384, SHA384)-encrypted and base64'd, joined with `"00000001"`, with `version` appended. Otherwise POST `/unisso/v2/validateUser.action` with plaintext password and a `service` redirect. (3) If `errorCode == "470"`, GET `https://{login_subdomain}{respMultiRegionName[1]}` to establish the session on the right region. (4) Non-empty `errorMsg` = failure; "incorrect verification code" triggers captcha solving. (5) `keep-alive` → `roarand` header. (6) `company/current` → `moDn` — [client.py L334-458](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py#L334-L458); [encryption.py L18-83](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/encryption.py#L18-L83)
- FACT (subdomain convention): the data host is e.g. `region01eu5` or `uni002eu5`. The login host strips the prefix (`region01eu5`[8:] → `eu5`, `uni002eu5`[6:] → `eu5`), i.e. SSO lives on the bare regional host and data on a numbered shard — [client.py L240-248](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py#L240-L248)
- FACT (session liveness): the docstrings say the web app calls `is-session-alive` "every 10 seconds" and `keep-alive` "around every 30 seconds". The `@logged_in` decorator checks `is-session-alive` before every call and re-logs in if `code != 0` — [client.py L150-174, L460-506](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py#L150-L174)
- FACT (captcha): "Sometimes, if logging in too often, the API will return a captcha… Reusing a session will significantly reduce the chance of getting a captcha, since the API counts logins, not hits for rate limiting." The project ships an ONNX CTC model (`models/captcha_huawei.onnx`, about 200 ms on CPU). Since v0.1.0 (2025-11-22) sessions are reused by exporting and importing cookies (`get_cookies()` / `cookies=`) — [README](https://github.com/jgriss/FusionSolarPy/blob/main/README.md); [CHANGELOG](https://github.com/jgriss/FusionSolarPy/blob/main/CHANGELOG.md)
- FACT (wrong region): `company/current` returns HTTP 500/400 with `exceptionId` "Query company failed." or "bad status", or a non-JSON body, when the subdomain is wrong — [client.py L425-455](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py#L425-L455)
- FACT (Modbus): the installer login is a 0x41/0x24 challenge followed by 0x41/0x25 with HMAC-SHA256. It is kept alive by a heartbeat to register 49999 every 15 s, and the client re-logs in on reconnect — see §2 citations.

### Inferences
- INFERENCE: the portal's `roarand` header plays the role of an anti-CSRF token for state-changing calls. It was `csrfToken` from `/unisess/v1/auth/session` until removed on 2026-04-25 (see §5), and is now the `keep-alive` payload.
- INFERENCE: Huawei shards tenants across numbered hosts (`region01eu5`, `uni00Xeu5`) behind a shared regional SSO. For a product clone, this means a global identity service plus regional or sharded data planes, with a redirect hint in the login response.
- SPECULATION: the `nonce` + `timeStamp` + server-supplied `version` in v3 login suggests server-side replay protection and key rotation.

### Gaps
- Northbound token lifetime (still unknown). No client hard-codes a TTL; all rely on 305.
- Whether `/thirdData/logout` frees one of the limited concurrent sessions (would mitigate 20400). This is untested in code.

---

## 4. Response data models seen in code and fixtures (new fields, units, quirks)

### Takeaway
Northbound responses share one envelope `{success, failCode, message, params{…echo, currentTime}, data, buildCode?}`. `data` is either a list of `{stationCode|devId, collectTime?, dataItemMap{snake_case → value}}` or a paged `{list, pageCount, pageNo, pageSize, total}`. Value types are inconsistent: plant real-time KPIs are strings, while historical KPIs are numbers or `null`. The web portal returns parallel arrays (`xAxis` + series) with `"--"` for missing values.

### Cited Findings
- FACT: `getStationRealKpi` fixture values are strings (`"day_power": "17543"`, `"total_power": "345732.000"`), with `real_health_state` "1" or "3". `params` echoes `stationCodes` and `currentTime` — [pyhfs getStationRealKpi.json](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/tests/data/getStationRealKpi.json)
- FACT: `getKpiStationHour` items carry only `radiation_intensity, theory_power, inverter_power, ongrid_power, power_profit`, and any of them can be `null`. Day, month and year items add `use_power, installed_capacity, perpower_ratio, performance_ratio, reduction_total_co2/coal/tree`. Every item has `stationCode` + `collectTime` (epoch ms). Every fixture timestamp falls at **16:00 UTC**, i.e. 00:00 in UTC+8: month 1501516800000 = 2017-07-31 16:00 UTC (= 2017-08-01 00:00 UTC+8), year 1483200000000 = 2016-12-31 16:00 UTC (= 2017-01-01 00:00 UTC+8), day 1501776000000 = 2017-08-03 16:00 UTC, hour 1501862400000 = 2017-08-04 16:00 UTC. The fixtures look like copies of Huawei's China-time doc examples — [pyhfs tests/data/getKpiStation*.json](https://github.com/guillaumeblanc/pyhfs/tree/main/pyhfs/tests/data)
- FACT: alarm item fields: `alarmCause, alarmId, alarmName, alarmType, causeId, devName, devTypeId, esnCode, lev, raiseTime, repairSuggestion, stationCode, stationName, status` — [pyhfs getAlarmList.json](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/tests/data/getAlarmList.json)
- FACT: `getDevRealKpi` items are keyed by `devId` with a `dataItemMap`. HA warns that `data: null` means "Check if you have sufficient permissions" — [device_real_kpi_coordinator.py L69-80](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/device_real_kpi_coordinator.py#L69-L80)
- FACT: device list adds `optimizerNumber`. Envelope adds `buildCode` — pjugowiec DTOs (§1).
- FACT: web-portal device real-time returns `data[i].signals[]` with `name`, `value` and `realValue`. `realValue` can contain `"-"`, which the client coerces to 0 — [client.py `get_battery_basic_stats`, ~L711-735](https://github.com/jgriss/FusionSolarPy/blob/main/src/fusion_solar_py/client.py)
- FACT: Modbus `Result{value, unit}` uses gain-scaled integers per register (e.g. SOC 37760 U16 %, gain 10) — [register_definitions/base.py](https://github.com/wlcrs/huawei-solar-lib/blob/develop/src/huawei_solar/register_definitions/base.py)

### Inferences
- INFERENCE: the fixture timestamps (all 16:00 UTC = local midnight in UTC+8) support the Javadoc claim that `collectTime` buckets are aligned to the plant's local midnight, not UTC. This contradicts or qualifies pyhfs's comment that times are "actually utc/gmt". Both are consistent if the value is a UTC epoch that marks local-midnight boundaries. Store as `Instant` + plant `ZoneId`.
- INFERENCE: real-time values as strings with 3 decimals plus a "health state" code suggest a cached aggregate computed server-side. Parse defensively (`BigDecimal`), tolerate `null`, `"--"` and `"-"`.

### Gaps
- No fixture for `getDevRealKpi`, `getDevHistoryKpi` or `getDevKpi*`. Units per key still have to come from the NBI PDF.

---

## 5. Rate limits, errors and breakages hit by the community (dated)

### Takeaway
On the Northbound side the problems are throttling (407 per interface per minute, which HA works around by rotating device types every 63 s), permission/consent changes and endpoint deprecation by region. On the portal side there is a steady stream of breakage: captcha (2023), the `uni` host migration (Jan 2024), encrypted v3 login (Aug 2024), the `roarand` header (Aug 2024), session-reuse changes (Nov 2025) and removal of `/unisess/v1/auth/session` (Apr 2026). The portal API changes every few months without notice. The Northbound API is far more stable.

### Cited Findings
- FACT (HA throttling design): `DeviceRealKpiDataCoordinator` runs every **63 s**, fetches **one devTypeId group per tick** (round-robin), and on 407 sets `skip` for `ceil(60/63)+1 = 2` ticks. The CLAUDE.md file states the API limit as "1-call/minute-per-endpoint". Station real KPI and kiosk run every 600 s, year KPI every 1 h. The code logs an error if there are more than 100 stations ("not a good idea") — [device_real_kpi_coordinator.py L20-121](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/device_real_kpi_coordinator.py#L20-L121); [CLAUDE.md](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/CLAUDE.md); [sensor.py L91, L755, L847, L945](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/sensor.py)
- FACT (pyhfs): the test helper `frequency_limit` treats `FrequencyLimit` (407/20618) as "cannot be considered as fails". CI runs against a live account, so even the author's CI hits the limits. There is no back-off in the library itself — [pyhfs tests/utils.py L9-18](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/tests/utils.py#L9-L18); [session.py](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/session.py)
- FACT (pyhfs failCode table, from the source): 305→internal re-login, 401→`Permission`, 407/20618→`FrequencyLimit`, 20001/20002/20003/20400/30029→`LoginFailed`, and anything else → `_InternalException`, re-raised as the generic `pyhfs.Exception`. An empty login body → `JSONDecodeError` → `LoginFailed` — [exception.py L35-59](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/exception.py#L35-L59); [session.py L72-78](https://github.com/guillaumeblanc/pyhfs/blob/main/pyhfs/session.py#L72-L78)
- FACT (HA error handling): 401 → `InvalidAccessToCurrentInterface` (used to fall back from `getStationList` to `stations`); 407 → `AccessFrequencyTooHigh`; any other non-zero → generic error that includes `data` as the message. The 407 response body puts the explanation in `data`, not `message` — [openapi_api.py L176-199](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py#L176-L199)
- FACT (dated breakages, from commit logs and CHANGELOG):
  - 2023-02-28: `getStationList` "deprecated for certain devices" on `au5` → switched to `stations` (HA 85b742a).
  - 2023-06-20: login issue with subdomain `intl` (FusionSolarPy 0.0.14).
  - 2023-08-13: captcha appears; ONNX solver and session reuse added (FusionSolarPy).
  - 2023-09-01: HA filters disabled stations and devices to save calls.
  - 2023-12-28: kiosk URL 1-year validity documented (HA).
  - 2024-01-12/21: new `uni…` subdomains with a new login procedure; `csrfToken` absent (FusionSolarPy 0.0.19–0.0.21, issue #23).
  - 2024-05-26: `keep-alive` / `is-session-alive` introduced (0.0.23).
  - 2024-08-11/13: encrypted "v3" login (#28/#29) and the `roarand` header required for several calls (#30) (0.0.25/0.0.26).
  - 2025-02-20: encryption fix (#34).
  - 2025-03-15: "new FusionSolar error messages" (0.0.27).
  - 2025-11-22: session reuse reworked to a cookie dict (0.1.0, #46).
  - 2026-04-25: "Adapted to a change in the API. roarand endpoint no longer seems to be supported" — the `/unisess/v1/auth/session` call was removed and HTTP 400 was added as a wrong-subdomain signal (0.1.1, commit e749718).
  - 2026-06-10: kiosk returning null JSON (HA).
  - 2026-07-05: EMMA (23070) support added to Northbound HA.
  — [FusionSolarPy CHANGELOG](https://github.com/jgriss/FusionSolarPy/blob/main/CHANGELOG.md); clone `git log` of FusionSolarPy and HA
- FACT: the README of pjugowiec mentions no rate limits and the code has no handling (§1).

### Inferences
- INFERENCE: the effective Northbound budget is about **1 call per minute per endpoint per account**. With N device types, the device real-time refresh period is about N minutes. Multi-plant products must batch up to 100 codes and spread endpoints across the minute.
- INFERENCE: Huawei treats the web portal as private and changes it roughly every 3–9 months (2023-08, 2024-01, 2024-05, 2024-08, 2025-03, 2025-11, 2026-04). A commercial integration should not depend on it.
- INFERENCE: login frequency, not request volume, triggers portal captchas. Long-lived sessions and keep-alive are the mitigation.

### Gaps
- GitHub issue threads with exact error payloads for 407/20618 and the daily cap value: not readable in this session.
- Whether OAuth Connect mode has different limits: no community client implements it.

---

## 6. Implications: (a) a Java/Spring integration, (b) designing an equivalent product

### Takeaway
(a) Build your own Spring client against Northbound `/thirdData/*`, using pjugowiec's DTO shapes as a starting checklist but fixing their types. Add envelope-level error mapping, single-flight re-login on 305, per-endpoint rate limiting with 407 back-off, batching, logout, and the device-KPI endpoints it lacks. Do not use the web-portal API commercially. Use local Modbus (via EMMA or SmartLogger) for second-level data or control. (b) A competing product should copy the layered model visible in the code (internal signal model → simplified northbound projection, gateway-relayed commands, share-token kiosk) but avoid Huawei's pain points: no webhooks, opaque limits, string-typed numbers, region guessing and session caps.

### Cited Findings
- FACT: pjugowiec shows that Retrofit + Gson + Lombok DTOs map 1:1 to the envelope and `dataItemMap`. It also shows the gaps: no `success`/`failCode` checks, no re-login, global static base URL, Double IDs — §1 citations.
- FACT: HA's round-robin-per-devTypeId scheduler and 407 skip logic are the most battle-tested throttling strategy in the community code — [device_real_kpi_coordinator.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/device_real_kpi_coordinator.py)
- FACT: huawei-solar-lib's typed register table (address, type, gain, unit, writeable, target device) plus the 0x41 login and file-transfer extensions are what a Java Modbus layer would need to replicate — §2 citations.
- FACT: licences differ. pjugowiec, pyhfs, HA FusionSolar and FusionSolarPy are MIT (porting is allowed with attribution). huawei-solar-lib and huawei_solar are **AGPL-3.0**, so copying their code into a closed-source or network-served product brings AGPL obligations — LICENSE files of each repo.

### Inferences
**(a) Java/Spring integration (INFERENCE)**
- Client: Spring `RestClient`/`WebClient` (or Retrofit as in pjugowiec) with one `FusionSolarSession` bean per Northbound account. Store the token from the `xsrf-token` header (fall back to the `XSRF-TOKEN` cookie). Guard re-login with a lock and cap retries at 1 per call, unlike pyhfs and HA, which recurse without a limit. Call `/thirdData/logout` on shutdown.
- Typed envelope `NbiResponse<T>{boolean success; int failCode; String message; Map<String,Object> params; T data; String buildCode}`. Map 305 → re-login, 401 → `PermissionDenied` (also try the `stations` fallback), 407 → `RateLimited` (retry after ≥60 s), 20618 → `DailyQuotaExceeded` (stop until next day), 20001–20003/20400/30029 → `AuthFailed` (alert, no retry). Treat `success:true` + `data:null` as a permission problem.
- Rate limiting: a Resilience4j `RateLimiter` per (account, endpoint) at 1 call per 60 s. Batch 100 `stationCodes`/`devIds`. Schedule `getDevRealKpi` round-robin by `devTypeId` as HA does. Run a nightly backfill with `getDevFiveMinutes`/`getDevKpiDay` and `getKpiStationHour`.
- Types: `Long` device IDs, `Integer` devTypeId, `BigDecimal` for KPI values parsed from string or number, nullable everywhere. `dataItemMap` as `Map<String, BigDecimal>` plus per-devTypeId typed views (do not hard-code a fixed POJO as pjugowiec does, since keys grow, e.g. 36 PV strings and EMMA `ex_*`). Times as `Instant` + plant `ZoneId`.
- Region: make the base URL per account (eu5, intl, au5, …), not static.
- Local path (VOMS/CPO-style O&M, EV-charging surplus): j2mod/digitalpetri against EMMA (unit 0, port 502), with one persistent connection, ≥1 s after connect, timeouts of about 10 s and reconnect after 5 timeouts. Implement 0x41 login + 49999 heartbeat only if writes are needed. SCharger data is readable via EMMA registers 30015–30508.

**(b) Equivalent product design (INFERENCE)**
- Internal model: devices identified by DN (`NE=…`), typed by MOC type, exposing numeric signal IDs with value/realValue/unit. Expose a stable public projection (devTypeId + named KPI keys) versioned separately, as Huawei does with `thirdData` vs `/rest/pvms/web`.
- Commands: model them as async tasks targeted at the gateway device (Dongle/EMMA/SmartLogger), with config-signal IDs (Huawei: 230190032 = active power control), a status query and per-plant mutual exclusion.
- Share links: an anonymous read-only token (`kk`) on a no-login SPA route, with a cached snapshot (Huawei: 30-min cache, 1-year expiry). Make expiry, revoke and refresh explicit.
- Identity: global SSO with regional data shards and a redirect hint in the login response (Huawei: `errorCode 470` + `respMultiRegionName`). Prefer a standard OAuth2/OIDC discovery over magic subdomains.
- Differentiators, i.e. avoiding Huawei's pain points: publish limits as headers (`Retry-After`, quota remaining) instead of failCode 407/20618 in HTTP 200 bodies; offer webhooks or MQTT for alarms and real-time data; return numbers as numbers; allow multiple concurrent API sessions per account; and document device and signal catalogues.

### Gaps
- No community implementation of OAuth Connect or the `/rest/openapi/pvms/nbi/v1|v2/control/*` APIs exists in these repos, so the write path via the cloud remains documented only in Huawei's references (see `api_integration.md`).
- Daily quota value (20618) and token TTL remain undocumented in all code read.
