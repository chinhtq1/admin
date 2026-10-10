# Huawei FusionSolar: Technical Integration Options for Third-Party Developers

Research scope: the Northbound API (SmartPVMS "thirdData" / OpenAPI), the OAuth Connect mode and control APIs, local Modbus integration (SmartLogger, SDongle, EMMA, inverter WiFi/RS485), community integrations, and known pain points. Status checked October 2026. Some Huawei support pages (support.huawei.com) returned HTTP 403 to my fetcher. In those cases I relied on page summaries that did load, on search-result titles, and on open-source client code that cites specific document sections. Where that matters, the item says so.

---

## 1. Northbound API: account, base URLs, auth flow, endpoints, devTypeIds, rate limits, latency, document versions

### Takeaway
The FusionSolar Northbound API is a POST/JSON API under `https://<region-host>/thirdData/`. You log in with `userName` + `systemCode` (the API password), and the server returns an `XSRF-TOKEN` cookie that must be sent back as a header on every later call. The account is created by a **company administrator** (installer company) under *System > Company Management > Northbound Management*. Since late 2024/2025 the plant **owner** must also explicitly grant API permission. Limits are strict: each interface is throttled per minute (failCode 407), there is a per-day cap per user (20618), and batches are capped (100 plants or devices per call for real-time data; history is 10 devices × 3 days at 5-minute resolution). Since SmartPVMS 24.x, Huawei also documents an **OAuth 2.0 "OAuth Connect" mode** and async **control APIs** (battery dispatch, battery mode, active-power limit) under `/rest/openapi/pvms/nbi/v1|v2/...`. Control APIs are available only in OAuth Connect mode. There are no webhooks; the API is pull-only.

### Cited Findings

**Account creation / who can create it**
- Menu path: **System > Company Management > Northbound Management > Add**. You create a separate API username/password (the password must be "8 to 32 characters"), select an associated user, set an expiration deadline, enable "Basic APIs", and authorize either all current and future plants of the company or specific plants — [Solytic KB](https://kb.solytic.com/en/knowledge/set-up-api-key-huawei-fusionsolar); [Solytic setup guide](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/)
- The associated user must be a **company administrator** with access to the needed plants — [Solytic KB](https://kb.solytic.com/en/knowledge/set-up-api-key-huawei-fusionsolar). meteocontrol: "A customer administrator login is required for setting up the NorthBound (API)" — [meteocontrol VCOM](https://zammad.meteocontrol.de/help/en-us/6-datalogger-import-configuration/179-vcom-import-huawei-fusionsolar-api)
- The HA FusionSolar integration tells end users to ask their installer to create credentials via System → Company Management → Northbound Management. The installer can scope them by device type: String Inverter, Residential Inverter, Battery, ESS, Power Sensor, Grid Meter, EMI — [tijsverkoyen/HomeAssistant-FusionSolar README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- Historical alternative path (EU): ask Huawei's service team at eu_inverter_support@huawei.com for an OpenAPI account and for the "SmartPVMS V300R006C00 Interface Reference" file — [huawei_client crate doc PDF "Communicate with FusionSolar through an openAPI account"](https://docs.rs/crate/huawei_client/latest/source/docs/Communicate%20with%20FusionSolar%20through%20an%20openAPI%20account.pdf); [olibos/Home-Assistant-FusionSolar-OpenApi](https://github.com/olibos/Home-Assistant-FusionSolar-OpenApi/). Eniris describes an "OpenAPI Application Form" plus a device-export Excel sent to eu_inverter_support@huawei.com — [Eniris wiki](https://wiki.eniris.be/wiki/publicinformation/view/Integraties/Huawei/Fusion%20Solar%20%26%20Neteco%20%28Huawei%29)
- **2025 owner-consent change.** Around 4 Sep 2025, existing integrations broke after Huawei made the owner grant API permission explicitly. Fix: "Login with the owner account, go to Plant management. There is a key icon in a circle under the operations… give api permission to the installer." Users confirmed it working again by 20 Sep 2025 — [HA community thread](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417)
- Mobile-app route (FusionSolar app 25.2.101.001): Me > Power plant management > Basic info > Set permissions > toggle API access, then wait about 30 min. Only Owner/End-User accounts see this setting — [tijsverkoyen issue #262](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/262)
- Earlier permission failures: failCode 20056 "exist resource that are not authorized by the owner", failCode 20010 on device list, and failCode 401 "Invalid access to current interface!". Owner-side enablement is under Plant → Plant Management — [tijsverkoyen issue #150](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/150)

**Base URLs / regions**
- Documentation pattern: `https://<Domain name of the management system>/thirdData/getStationRealKpi` (domain left generic) — [SmartPVMS 24.2.0 NB API Ref – Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring)
- `https://eu5.fusionsolar.huawei.com/thirdData/login` is used in Huawei's own "Communicate with FusionSolar through an openAPI account" guide — [huawei_client doc PDF](https://docs.rs/crate/huawei_client/latest/source/docs/Communicate%20with%20FusionSolar%20through%20an%20openAPI%20account.pdf); also in a Loxone forum walkthrough — [LoxForum](https://www.loxforum.com/forum/faqs-tutorials-howto-s-aa/255084-huawei-sun2000-inverter-fetching-data-through-openapi-with-changing-token)
- The HA integration uses `https://intl.fusionsolar.huawei.com/thirdData/`, "where `intl` reflects your regional prefix" — [tijsverkoyen README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- pyhfs defaults to `https://eu5.fusionsolar.huawei.com` and lets you override the base URL "to adapt to different location" — pyhfs 0.1.1 source (`session.py`), [PyPI](https://pypi.org/project/pyhfs/)
- The web portal (not the NB API) uses hosts like `region01eu5.fusionsolar.huawei.com` and newer `uni002eu5`-style hosts as accounts migrate — [fusion-solar-py](https://pypi.org/project/fusion-solar-py/0.0.22)
- meteocontrol's config asks for a "region/server selection" — [meteocontrol help center](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1)

**Auth flow (API-account mode)**
- `POST /thirdData/login` with JSON body `{"userName": "...", "systemCode": "..."}` — [huawei_client doc PDF](https://docs.rs/crate/huawei_client/latest/source/docs/Communicate%20with%20FusionSolar%20through%20an%20openAPI%20account.pdf); pyhfs `session.py` (`'userName': self.user, 'systemCode': self.password`)
- Token handling: pyhfs reads the **`XSRF-TOKEN` cookie** from the login response and sets it as the **`XSRF-TOKEN` request header** on later calls (`self.session.headers.update({'XSRF-TOKEN': response.cookies.get(name='XSRF-TOKEN')})`). The code comment cites "iMaster NetEco V600R023C00 Northbound Interface Reference-V6 (SmartPVMS)", EDOC1100261860, section "login-interface" — pyhfs 0.1.1 source, [PyPI](https://pypi.org/project/pyhfs/)
- The HA integration reads the `xsrf-token` response header and sends it back as the `xsrf-token` header — [openapi_api.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py)
- A Node-RED module failed with "Invalid credentials for openAPI login" because it expected the token in the response body. Huawei returns it in an HTTP cookie — [Node-RED forum](https://discourse.nodered.org/t/invalid-credentials-with-hermannp-node-red-getproduction-fusionsolar/78511)
- Response envelope: `{"data":..., "success":true|false, "failCode":0, "params":{}, "message":...}` — [issue #262](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/262); pyhfs checks `body.get('success')` and `failCode`
- Session expiry is signalled by failCode **305** ("You are not in the login state. You need to log in again."). pyhfs and the HA integration both re-login automatically on 305 — pyhfs `exception.py`; [openapi_api.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py)
- pyhfs notes a quirk: the NBI returns an empty JSON (not a failCode) when the user is unknown, "not the expected behavior described by documentation 7.1.1" — pyhfs `session.py`
- pyhfs also notes that timestamps are documented as plant time zone but are "actually utc/gmt" (epoch ms) — pyhfs `client.py`

**failCode list (from pyhfs, which cites EDOC1100261860 "error-code-list")**
- 305 not logged in / session expired; 401 "You do not have the related data interface permission"; **407 "The interface access frequency is too high"**; 20001 third-party system ID does not exist; 20002 third-party system forbidden; 20003 third-party system expired; **20400** wrong username/password, user locked, password expired, or "the number of online sessions reaches the upper limit"; **20618 "Maximum number of calls per user per day"**; 30029 authentication failed — pyhfs 0.1.1 `exception.py`, [PyPI](https://pypi.org/project/pyhfs/)
- The 25.x reference has FAQ pages titled "Why Does the Northbound API Return Error Code 401?" and "Handling the Exception Returned by Calling the Token Obtaining API" — [search-result titles, EDOC1100492747](https://support.huawei.com/enterprise/en/doc/EDOC1100492747/41019745/why-does-the-northbound-api-return-error-code-401) (page content not fetchable: 403)

**Main data endpoints (all POST under `/thirdData/`)**
- Listed in the 25.2.0 reference: `getDevRealKpi`, `getDevHistoryKpi`, `getDevList` (now with a model field), `getStationRealKpi`, `getAlarmList`, `getKpiStationHour`, `getKpiStationDay`, `getKpiStationMonth`, `getKpiStationYear`, `stations` (paginated plant list) — [SmartPVMS 25.2.0 NB API Reference](https://support.huawei.com/enterprise/en/doc/EDOC1100492747)
- The older plant list `getStationList` is still used by the HA integration alongside the newer `stations` — [openapi_api.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py); also [LoxForum](https://www.loxforum.com/forum/faqs-tutorials-howto-s-aa/255084-huawei-sun2000-inverter-fetching-data-through-openapi-with-changing-token)
- `stations` takes `{"pageNo": n, "pageSize": 100}` and returns `data.list` and `data.pageCount` — pyhfs `client.py`
- `getStationRealKpi`: `stationCodes` (mandatory, comma-separated). "Data of a maximum of 100 plants can be queried at a time" — [24.2.0 Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring)
- `getKpiStationHour/Day/Month/Year`: `stationCodes` + `collectTime` (epoch ms), batched 100 plants per call — pyhfs `client.py`
- `getDevRealKpi`: `devIds` or `sns` (one required) + `devTypeId` (mandatory). "Data of a maximum of 100 devices of the same type can be queried at a time" — [24.2.0 Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring)
- `getDevHistoryKpi`: `devIds`/`sns` + `devTypeId` + `startTime`/`endTime` (ms, mandatory). Returns "the 5-minute data of a maximum of 10 devices of the same type in three days" — [24.2.0 Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring)
- `getAlarmList`: `stationCodes`, `beginTime`, `endTime` (ms), `language` (zh_CN, en_US, ja_JP, it_IT, nl_NL, pt_BR, de_DE, fr_FR, es_ES, pl_PL) — pyhfs `client.py`
- 25.1.0 change: string inverters support up to 36 PV strings in the data model — [25.2.0 ref summary](https://support.huawei.com/enterprise/en/doc/EDOC1100492747)
- Eniris lists device-level KPI granularities (5-min, daily, monthly, yearly device data). This implies `getDevKpiDay/Month/Year`-style device endpoints exist, but Eniris does not name the paths — [Eniris wiki](https://wiki.eniris.be/wiki/publicinformation/view/Integraties/Huawei/Fusion%20Solar%20%26%20Neteco%20%28Huawei%29)

**devTypeId codes (from community code)**
- 1 = String inverter; 38 = Residential inverter; 39 = Battery; 41 = C&I/Utility ESS; 47 = Power sensor; 10 = EMI (environmental monitoring); 17 = Grid meter; 23070 = EMMA — [tijsverkoyen const.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/const.py)
- Huawei "Added devTypeId Reference Table Returned by the Device List API" in v24.6.0 — [25.1.0 ref change history](https://support.huawei.com/enterprise/en/doc/EDOC1100465337)

**Control APIs (async task model)**
- Active power: `POST /rest/openapi/pvms/nbi/v2/control/active-power-control/async-task` (v1 in 24.4.0) and `.../active-power-control/task-info` to query status. Tasks go to the communication device (Dongle, EMMA, SmartLogger). Modes are unlimited and limited feed-in (kW) — [25.2.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100492747); [24.4.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100366278)
- Battery: `/rest/openapi/pvms/nbi/v1/control/battery/battery-dispatch/async-task` (charge/discharge dispatch), `/rest/openapi/pvms/nbi/v1/control/battery/mode/async-task` (working mode), `/rest/openapi/pvms/nbi/v1/configuration/battery-mode` and `/rest/openapi/pvms/nbi/v1/configuration/active-power-control-mode` (queries). 24.5.0 also lists "Setting Battery Parameters" deliver/query APIs — [25.2.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100492747); [24.5.0 Control APIs](https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis)
- Constraint: "For the same battery [plant], do not call this API repeatedly before a task is complete" — [25.2.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100492747); [25.1.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100465337)
- The control APIs are "available only in OAuth Connect mode" — [24.5.0 Control APIs](https://support.huawei.com/enterprise/en/doc/EDOC1100379184/7a471100/control-apis)

**OAuth 2.0 / OAuth Connect**
- 24.4.0 (Release 02, 2024-05-14): "Optimized OAuth Connect and Flow Control Policy in OAuth Connect Mode" — [24.4.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100366278)
- 25.1.0 sections: "Creating an OAuth 2.0 Client for a Third-Party App", "Obtaining the Access Token of the Open API by a Third-Party App", "Initiating Authorization to a Third-Party App by an Owner", and "Revoking Authorization by an Owner" (added in 24.7.0) — [25.1.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100465337)
- 24.2.0 has a section titled "Integrating OAuth 2.0 to Third-Party Apps" — [search result title](https://support.huawei.com/enterprise/en/doc/EDOC1100358266/872e9abc/integrating-oauth-20-to-third-party-apps) (content returned 403)

**Rate limits / call frequency**
- "Third-party applications will be limited by one-minute access frequency when accessing the same northbound interface API" — [huawei_client doc PDF (Huawei guide)](https://docs.rs/crate/huawei_client/latest/source/docs/Communicate%20with%20FusionSolar%20through%20an%20openAPI%20account.pdf)
- failCode 407 = per-interface frequency too high; 20618 = daily per-user cap; 20400 includes "online sessions reaches the upper limit" — pyhfs `exception.py`
- HA integration: "very strict rate limits" and "a single login session limit". Running the same credentials from two places causes trouble, so create a second account for testing — [tijsverkoyen README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- Integrators: "The total number of data queries to the FusionSolar API is calculated per system/user and is subject to strict limitations." Solytic recommends a separate API account per system and a **24 h** transmission interval — [Solytic KB](https://kb.solytic.com/en/knowledge/set-up-api-key-huawei-fusionsolar). meteocontrol: "Huawei restricts the number of API requests per user… we recommend using a separate user for each system", and device definitions are cached and refreshed "only every 24h" — [meteocontrol help center](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1); [meteocontrol zammad](https://zammad.meteocontrol.de/help/en-us/6-datalogger-import-configuration/179-vcom-import-huawei-fusionsolar-api)

**Data granularity / latency**
- meteocontrol: measuring interval **5 minutes**, transmission interval **15 minutes**, HTTPS pull, JSON. A nightly job re-requests the past 7 days to fill gaps "when API limitations permit". After a logger swap, live data can take up to 24 h to appear — [meteocontrol help center](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1)
- HA integration: realtime device data "updated every minute per device group", total yields every 10 minutes — [tijsverkoyen README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- pyfusionsolardatarelay polls every 5 minutes by default (cron `*/5`) — [Docker Hub](https://hub.docker.com/r/jsprnl/pyfusionsolardatarelay)

**Document versions**
- Legacy: "SmartPVMS V300R006C00 Interface Reference" — [huawei_client doc PDF](https://docs.rs/crate/huawei_client/latest/source/docs/Communicate%20with%20FusionSolar%20through%20an%20openAPI%20account.pdf). "iMaster NetEco V600R023C00 Northbound Interface Reference-V6 (SmartPVMS)", EDOC1100261860 — [pyhfs](https://pypi.org/project/pyhfs/)
- Newer versioning: SmartPVMS 24.2.0 (EDOC1100358266), 24.4.0 (EDOC1100366278, 2024-05-14), 24.5.0 (EDOC1100379184, 2024-07-10), 24.6/24.7/24.8, 25.1.0 (EDOC1100465337), and **25.2.0 (EDOC1100492747), the latest found** — [25.2.0](https://support.huawei.com/enterprise/en/doc/EDOC1100492747); [25.1.0](https://support.huawei.com/enterprise/en/doc/EDOC1100465337); [24.5.0](https://support.huawei.com/enterprise/en/doc/EDOC1100379184/3055b7a9/api-reference)
- 24.5.0 splits the reference into "Basic APIs" and "Control APIs" — [24.5.0 API reference](https://support.huawei.com/enterprise/en/doc/EDOC1100379184/3055b7a9/api-reference)

### Inferences
- For a Spring app, wrap the API in a client that does the following. Log in once and cache the `XSRF-TOKEN` cookie value, sending it back as a header. Re-login only on failCode 305. Treat 407 as a retry-after-60s signal and 20618 as "stop until the next day". Serialize calls per interface (at most about one per minute per interface, based on the one-minute rule). Batch `stationCodes`/`devIds` up to 100 per call, and 10 devices × 3 days for history. A `RestClient` + Resilience4j RateLimiter keyed per endpoint fits this model.
- Use one API account per integration instance. Concurrent logins with the same account can invalidate each other's sessions or hit the session cap (20400).
- Do not treat `success:true` as proof of access. Issue #262 shows `success:true` with `data:null`, which happens when the owner has not granted permission.
- For writes (battery dispatch, export limiting), plan for OAuth Connect: register an OAuth client, get owner authorization, and accept that the token flow differs from the `thirdData/login` flow. I could not retrieve the exact OAuth endpoint URLs.
- Since there is no push or webhook (none documented in any version reviewed), near-real-time use cases such as EV-charging PV-surplus control should use local Modbus, not the cloud API.

### Gaps
- The exact OAuth 2.0 authorize/token endpoint paths, grant types, token lifetimes, and the "flow control policy in OAuth Connect mode" numbers. The Huawei pages returned 403 or were robots-blocked.
- The official per-interface frequency table (e.g. per-day call formulas) and the full failCode table straight from Huawei. The codes above come via pyhfs, which cites Huawei's error-code-list page.
- The full official devTypeId table, including codes for dongle, SmartLogger, optimizer, and charger. Only the community constants above were verifiable.
- A complete list of regional hosts. Only `eu5`, `intl`, and the web-portal `region01eu5`/`uni00Xeu5` were confirmed. `la5`, `sg5`, `au5` etc. could not be verified from sources.
- Exact paths for device-level day/month/year KPI endpoints (e.g. `getDevKpiDay`). They are implied by Eniris but not confirmed.
- Session timeout duration: not found.

---

## 2. Local integration: Modbus TCP/RTU via SmartLogger, Smart Dongle, EMMA, inverter WiFi

### Takeaway
Local access uses Huawei's Modbus register map ("Solar Inverter Modbus Interface Definitions", Issue 05, 2023-02-16). You can reach it over Modbus TCP via SDongle, EMMA, SmartLogger, the inverter's own AP, or the inverter LAN IP (newer firmware, port 6607 or 502), or over Modbus RTU on the RS485A1/B1 pins. The hard constraints: Huawei devices accept only one Modbus client at a time; Modbus TCP must be explicitly enabled ("Enable (Unlimited)") via the FusionSolar app or the SmartLogger web UI; and the dongle is slow and flaky (read every ≥5 s, 1-5 s connect delay).

### Cited Findings
- Register map document: "Solar Inverter Modbus Interface Definitions", **Issue 05, 2023-02-16**. Function codes 0x03 read, 0x06 write single, 0x10 write multiple — [PDF via ioBroker forum](https://forum.iobroker.net/assets/uploads/files/1699119419919-solar-inverter-modbus-interface-definitions-v5.pdf)
- Example registers: 32080 active power (I32, kW, gain 1000); 32064 input power (I32, kW, gain 1000); 37113 meter active power (I32, W; >0 feed-in, <0 import); 37760 battery SOC (U16, %, gain 10); 47086 battery working mode (U16; adaptive, fixed charge/discharge, TOU, etc.) — [same PDF](https://forum.iobroker.net/assets/uploads/files/1699119419919-solar-inverter-modbus-interface-definitions-v5.pdf)
- Connection options: direct inverter IP (firmware Q4 2022+), EMMA-02, SDongle ("least reliable"), inverter built-in AP `SUN2000-<serial>`, USB-RS485, or an RS485-to-TCP bridge (Elfin/Protoss) — [wlcrs/huawei_solar wiki "Connecting to the inverter"](https://github.com/wlcrs/huawei_solar/wiki/Connecting-to-the-inverter)
- Ports: **6607** is the primary Modbus TCP port (firmware from Dec 2021+); **502** is legacy/fallback. Default slave ID 1; try 0 on the inverter AP (host 192.168.200.1). Serial runs at 9600 baud — [huawei_solar wiki](https://github.com/wlcrs/huawei_solar/wiki/Connecting-to-the-inverter); [huawei_solar README](https://github.com/wlcrs/huawei_solar)
- Enabling: for a direct inverter connection, go to Device Commissioning > Settings > Router connection settings and enable "Local O&M". For the SDongle, set "Unrestricted Modbus TCP mode" — [huawei_solar wiki](https://github.com/wlcrs/huawei_solar/wiki/Connecting-to-the-inverter). Eniris: in the dongle parameter settings, select Modbus-TCP and set Connection to "Enable (Unlimited)". On the SmartLogger web UI, set the link setting to "Enable (Unlimited)" — [Eniris docs](https://docs.eniris.com/nl/Controller/Devices/PV-hybrid-and-battery-inverters/Huawei)
- Dongle firmware: SPC120 or newer is required. For **SPC124+**, "Modbus TCP must be activated locally via the FusionSolar APP" — [evcc discussion #1928](https://github.com/evcc-io/evcc/discussions/1928). openHAB users cite `SDongle_V100R001C00SPC120` as the firmware that enabled TCP — [openHAB community](https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu-with-json-configuration-for-full-giu-control/122737)
- Single connection: "Modbus devices only support one connection at a time" — [huawei_solar README](https://github.com/wlcrs/huawei_solar). "Huawei devices only support one connection at a time" — [huawei-solar-lib](https://github.com/wlcrs/huawei-solar-lib). evcc: parallel clients via a Modbus proxy "may cause communication errors" — [evcc docs](https://docs.evcc.io/en/meters/huawei-sun2000-hybrid-inverter)
- Dongle timing: "Read every 5 s and wait 2 s for the answer… Faster reading generates error!". Use a timeout of 1000 ms or more and a connect delay of 1-5 s. "First TX always fails" on a new socket — [evcc discussion #1928](https://github.com/evcc-io/evcc/discussions/1928). The `sun2000_modbus` lib has a `wait` parameter after connect for stability — [olivergregorius/sun2000_modbus](https://github.com/olivergregorius/sun2000_modbus)
- The SDongleA-05 and SDongleA-FE interfere with devices on RS485A1/B1, so you cannot combine the dongle with your own RS485 link. EMMA and the dongle restart periodically if they cannot reach the gateway or the Huawei cloud — [huawei_solar wiki](https://github.com/wlcrs/huawei_solar/wiki/Connecting-to-the-inverter)
- Cloud coexistence: with the dongle, data still flows to FusionSolar — [huawei_solar README](https://github.com/wlcrs/huawei_solar). One openHAB user lost cloud upload ("Abnormal communication between management system and equipment") after enabling Modbus TCP on an SDongleA-05. Recommissioning the dongle via the app (Me > Plant Management > Devices, scan QR) fixed it — [openHAB community](https://community.openhab.org/t/i-can-read-modbus-data-via-tcp-with-sdongle-a05-but-inverter-no-longer-sends-data-to-fusionsolar-server/153148)
- Firmware: huawei_solar "supports inverters running firmware versions released in 2023 and later" for full register coverage — [huawei_solar README](https://github.com/wlcrs/huawei_solar)
- Writes and battery control locally: huawei-solar-lib can write registers and perform the "installer"-level login sequence. It supports SUN2000, LUNA2000, EMMA, and SCharger (via EMMA) — [huawei-solar-lib](https://github.com/wlcrs/huawei-solar-lib). evcc supports external battery charge/discharge control and curtailment on Huawei hybrid inverters (port 502, ID 1). Grid metering needs a DTSU666/DDSU666 power sensor — [evcc docs](https://docs.evcc.io/en/meters/huawei-sun2000-hybrid-inverter)

### Inferences
- For a Java backend, use j2mod or digitalpetri modbus against EMMA or the SmartLogger where possible, since they are more stable than the dongle. Keep one persistent connection per device (never open/close per poll), poll every 5 s or slower, and run a single "Modbus owner" service that fans data out (e.g. via MQTT) instead of letting several clients connect.
- EMMA plus SCharger is relevant to EV-charging admin systems: huawei-solar-lib reads SCharger data through EMMA, so Huawei chargers are visible locally over Modbus.
- Commercial sites with a SmartLogger3000 are the most "enterprise" local path. Its Modbus TCP also carries the "Remote communication scheduling" active-power control (per Eniris).

### Gaps
- The exact SmartLogger3000 Modbus TCP specifics (port, unit-ID scheme, client whitelisting, max connections) were not retrieved from the Huawei manual (403).
- The SDongleA-05 connection count is documented only via community statements ("one connection"), not a Huawei spec.
- The registers and protocol for EMMA/SCharger beyond library support were not researched in depth.

---

## 3. Community integrations and what they reveal about the API

### Takeaway
There are three families. (a) Cloud **Northbound** clients (tijsverkoyen HA integration, pyhfs, olibos HA, ioBroker adapter, pyfusionsolardatarelay, meteocontrol/Solytic/Eniris commercial importers). (b) **Kiosk** scrapers, which use a public read-only URL. (c) Local **Modbus** stacks (wlcrs huawei_solar / huawei-solar-lib, evcc, openHAB Modbus binding, sun2000_modbus). A fourth, fragile option logs into the web portal directly (fusion_solar_py, with captcha solving). The community consensus: the cloud API is fine for daily/hourly energy reporting and alarms, and local Modbus is needed for second-level control.

### Cited Findings
- **tijsverkoyen/HomeAssistant-FusionSolar** offers two modes. Kiosk mode updates every 10 min and gives only realtime power plus day/month/year/lifetime energy. OpenAPI mode gives per-device data. The kiosk URL comes from Portal > plant > Monitoring > Kiosk button, and "The url is valid for 1 year" — [README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- Kiosk backend: `GET /rest/pvms/web/kiosk/v1/station-kiosk-file?kk=<id>`. The response `data` field is HTML-escaped JSON that must be `html.unescape`d and parsed again to get `realKpi` — [kiosk_api.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/kiosk/kiosk_api.py)
- The HA OpenAPI client handles failCodes 305 (re-login), 401, and 407 ("Access frequency to high") — [openapi_api.py](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/blob/master/custom_components/fusion_solar/fusion_solar/openapi/openapi_api.py). Recent releases (v3.x) added EMMA support — [releases](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/releases)
- **pyhfs** (Python): batches 100 plants per call, paginates `stations`, maps failCodes to exceptions, and states that timestamps are UTC epoch ms — [PyPI](https://pypi.org/project/pyhfs/) (source of v0.1.1 inspected)
- **fusion_solar_py** uses the web-portal session (`region01eu5`), not the NB API. It has optional ONNX captcha solving, and its authors are unsure it works on the new `uni…eu5` hosts — [PyPI](https://pypi.org/project/fusion-solar-py/0.0.22)
- **pyfusionsolardatarelay** (Docker): pulls from Northbound or Kiosk and relays to InfluxDB, PVOutput, and MQTT. Default base `https://eu5.fusionsolar.huawei.com`, polling every 5 min — [Docker Hub](https://hub.docker.com/r/jsprnl/pyfusionsolardatarelay)
- **Node-RED** `@hermannp/node-red-getproduction-fusionsolar` broke because the token is delivered as a cookie — [Node-RED forum](https://discourse.nodered.org/t/invalid-credentials-with-hermannp-node-red-getproduction-fusionsolar/78511)
- **Homey** "Huawei FusionSolar Manager" offers OpenAPI (needs "full rights on your installation", account code and station code) plus other connection methods. It points to Huawei's doc "FusionSolar SmartPVMS-Creating a Northbound API Account" — [Homey community](https://community.homey.app/t/huawei-fusionsolar-manager-looking-for-testers/153353)
- **Local**: wlcrs/huawei_solar (HA) and huawei-solar-lib — [GitHub](https://github.com/wlcrs/huawei_solar), [lib](https://github.com/wlcrs/huawei-solar-lib); evcc templates for SUN2000 with/without battery — [evcc docs](https://docs.evcc.io/en/meters/huawei-sun2000-inverter-without-battery); openHAB Modbus binding JSON configs — [openHAB community](https://community.openhab.org/t/reading-data-from-huawei-inverter-sun-2000-3ktl-10ktl-via-modbus-tcp-and-rtu-with-json-configuration-for-full-giu-control/122737)
- **Commercial importers**: meteocontrol VCOM (username + system code + station code `NE=…` + region; 5-min measurement, 15-min transmission) — [meteocontrol](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1); Solytic — [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/); Eniris (guest user or OpenAPI) — [Eniris wiki](https://wiki.eniris.be/wiki/publicinformation/view/Integraties/Huawei/Fusion%20Solar%20%26%20Neteco%20%28Huawei%29)

### Inferences
- Station codes have the form `NE=<digits>` (meteocontrol). Use them as the stable plant key in your DB.
- No Java/Spring client library was found among the main community projects. A Spring Boot integration would be custom, but the Python clients (pyhfs especially) are small enough to port directly.
- Commercial monitoring vendors settle on 15-min to 24-h sync intervals. That is a practical upper bound on how "live" a multi-plant cloud integration can be.

### Gaps
- An openHAB FusionSolar cloud binding: only Modbus-based setups were found.
- The ioBroker fusionsolar adapter's code and notes could not be read (forum robots-blocked).
- I did not verify any community integration that uses the OAuth Connect control APIs.

---

## 4. Known pain points: lockouts, kiosk, export, webhooks

### Takeaway
The main operational risks: permission breakage after Huawei backend or app changes (Sep 2025 owner-consent requirement), the session cap and lockouts (20400) from concurrent use of one account, per-minute (407) and per-day (20618) throttling, kiosk URLs that expire yearly, and no push/webhook mechanism, so everything is polling. Bulk history is easier via portal reports (subscribe/export) than via the API's 10-device × 3-day history window.

### Cited Findings
- Lockout/session cap: failCode 20400 covers "The user is locked", "The password has expired", and "The number of online sessions reaches the upper limit" — pyhfs `exception.py` (citing Huawei error-code-list). HA README: "single login session limit"; use separate accounts for test and prod — [README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- Sudden breakage from Huawei changes: Sep 2025 (owner must grant API permission) — [HA community](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417); FusionSolar app 25.2.101.001 permission toggle — [issue #262](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/262); earlier failures that resolved "after a Huawei system update without code changes" — [issue #150](https://github.com/tijsverkoyen/HomeAssistant-FusionSolar/issues/150)
- API account expiry is set at creation ("Set expiration deadline… preferably distant future"). failCode 20003 = third-party system expired — [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/); pyhfs
- Kiosk: read-only, 10-min updates, URL valid 1 year — [README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- Reports/export: SmartPVMS Report Management offers Plant, Inverter, PCS, and Battery reports by day/month/year, with the ability to "subscribe to and export reports". Export file formats are not stated in the excerpt — [SmartPVMS 24.2.0 User Manual](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report)
- Webhooks/push: none documented in the 25.1.0 change history — [25.1.0 ref](https://support.huawei.com/enterprise/en/doc/EDOC1100465337). Integrators describe the API as an "HTTPS pull" protocol — [meteocontrol](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1)
- After a logger or dongle replacement, data may take up to 24 h to reappear via the API — [meteocontrol](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1)
- Web-portal scraping is brittle (captcha, host migration to `uni…`) — [fusion_solar_py](https://pypi.org/project/fusion-solar-py/0.0.22)

### Inferences
- Build in: a health check that tells "success:true + data:null" (permission revoked) apart from real empty data; alerting on 20003 and 20400; a credential-rotation runbook; and a nightly back-fill job (like meteocontrol's 7-day re-request) to repair gaps caused by throttling.
- For alarm-driven workflows (e.g. pushing to an O&M/ticketing system like VOMS), poll `getAlarmList` on a schedule and de-duplicate. No push alternative was found.

### Gaps
- No official statement was found on whether FusionSolar offers any push/MQTT/webhook northbound for SmartPVMS (NetEco on-prem may differ). Absence is inferred from the docs reviewed.
- Report export formats (CSV vs XLSX) and scheduled e-mail options were not confirmed.
- Whether too many failed logins lock the account, and for how long, is unknown. Only the "user is locked" failCode is documented.
