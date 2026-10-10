# PV/energy monitoring & management platforms vs. Huawei FusionSolar: competitive landscape and rebuild building blocks (as of Oct 2026)

Research date: 2026-10-07. Builds on `/home/claude/research_notes/Nền tảng Huawei FusionSolar/` (market_users_vietnam.md, features_editions.md, api_integration.md, architecture_security.md). Facts from those notes are re-cited here only when needed for the comparison. They are not repeated in full.

Labels used:
- **FACT**: stated by the cited source. Every bullet under "Cited Findings" is FACT unless tagged otherwise.
- **INFERENCE**: my reasoning from several cited facts.
- **SPECULATION**: plausible but weakly supported.

Dates in brackets are publication dates. No prices have been invented. Where no price is published, the note says so.

---

## Q1. OEM platforms: segments, notable features, API openness, business model

### Takeaway
Every major inverter OEM bundles free owner and installer monitoring with its hardware: Huawei, Sungrow, SMA, SolarEdge, Enphase, Growatt, GoodWe, Solis and Deye/Solarman. They now compete on four things:
1. AI-branded diagnostics and schedulers (GoodWe SEMS+ Jan 2026, Huawei EMMA/AI Agent, SMA Energy Maximizer)
2. Smart I-V curve scanning (Huawei, Sungrow, Solis, GoodWe)
3. Home/C&I energy management (EV charger, heat pump, dynamic tariffs)
4. VPP/aggregator APIs (Enphase is the clearest)

API openness varies sharply. Enphase and SMA publish commercial API price models. SolarEdge, Growatt and Sungrow offer self-serve per-account keys/tokens. GoodWe needs an NDA and Solis needs a support ticket. Huawei is installer-gated with strict quotas. In 2025–2026 the trend was toward OAuth2 with owner consent: SolarEdge's V1 key API is retired in Nov 2026, Huawei OAuth Connect, SMA OAuth. I found no OEM offering outbound webhooks for monitoring data. Only Enphase's VPP plan advertises push-based telemetry.

### Cited Findings

**Huawei FusionSolar (baseline, see prior notes)**
- Free monitoring via app and web portal. Owner accounts are created and invited by the installer. — [basic-solar.de](https://basic-solar.de/shop/wechselrichter/zubehoer/huawei-smart-dongle-wlan-fe); [EWR helpdesk](https://helpdesk.one.ewr.de/hc/en-us/articles/31389751586450-Huawei-Fusion-Solar)
- Smart I-V Curve Diagnosis: scans all strings of a 5 MW plant within 5 minutes and produces a report within 15 min. 128 sampling points per curve. TÜV verified. Requires SmartLogger plus FusionSolar/NetEco1000S [2018 datasheet]. — [Huawei IV-Curve datasheet (Aug 2018)](https://solar.huawei.com/~/media/Solar/attachment/pdf/na/datasheet/IV-Curve.pdf)
- Northbound API: company-admin created, per-interface per-minute throttling, a daily per-user cap, pull-only, no webhooks. Control APIs only in OAuth Connect mode. — see api_integration.md; [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/)

**Sungrow iSolarCloud**
- New version launched 1 Sep 2023: Smart IV Curve Diagnosis "with over 90% accuracy", automatic fault-analysis reports, remote upgrade, fault warnings via app/email, a separate EV-charging interface, CO2 tracking. It "serves more than one million users in over 150 countries, with a total installed capacity of 56 GW". — [pv magazine USA press release (Sep 2023)](https://pv-magazine-usa.com/press-releases/sungrow-launches-new-version-of-its-management-and-monitoring-system-isolarcloud/)
- 2024 datasheet: 5-minute monitoring interval. Device types include inverters, EV chargers, weather stations, meters, transformers and circuit breakers. "Supports over 100 GW of maximum access", ">100 PB" storage, 99.99% uptime, "financial grade security". — [iSolarCloud Datasheet V3 (Apr 2024)](https://info-support.sungrowpower.com/application/pdf/2024/04/18/DS_20240417_iSolarCloud_Datasheet_V3_EN.pdf)
- Open API: the API key, access key and RSA key are obtained in iSolarCloud → Settings → Open API, used together with username/password. Third parties (Eniris) use it for active-power limiting, but "some older Sungrow firmwares don't respect active power limits". — [Eniris docs (NL)](https://docs.eniris.com/nl/Controller/Devices/Cloud/ISolarCloud)
- Hierarchical access management and redundant data storage over the inverter lifecycle. — [Sungrow blog (6 Dec 2024)](https://www.sungrowpower.com/en/blog-detail/5931/top-3-reasons-to-choose-sungrow-solar-operating-amp-monitoring-platform-isolarcloud)
- Pricing: no paid tier found. The SolarQuotes review treats iSolarCloud as the free bundled app and compares it with A$60/yr Solar Analytics. — [SolarQuotes (17 Jul 2023)](https://www.solarquotes.com.au/blog/solar-analytics-integrated/)

**SMA Sunny Portal powered by ennexOS**
- Segments: Home, Business, Large Scale. Live dashboards and energy-balance views. "Energy Maximizer" (Premium, SMA only) does predictive load shifting using PV forecast, tariff forecast and consumption. "Energy Planner" offers manual control. Dynamic tariffs are supported. Multi-system portfolio management. SMA 360° app for commissioning. A free basic tier exists. "SMA Smart Connected" is a paid service for automatic inverter monitoring and fault diagnosis with replacement. — [SMA America Sunny Portal page](https://www.sma-america.com/products/apps-software/sunny-portal)
- APIs: Monitoring API (historical), Live API (near real-time), GridControl API (remote control). OAuth 2.0 with "Code Flow" for end-user apps and "Custom Flow" for O&M partners. Owner consent is required. Consumption-based fees ("SMA charges for the consumption of a system in any given month"). Refresh is up to 2 h on classic systems (15 min with the Professional Package) and every 5 min on ennexOS. — [SMA developer FAQ](https://developer.sma.de/faq)
- Monitoring API fees via Solytic: "30€ per year per site" up to 200 kWp, 50 € for 201–625 kWp, 70 € above 625 kWp. After revocation, "the SMA API only allows a new request after a few days". — [Solytic KB (undated)](https://solytic.com/knowledge/set-up-api-access-sma-monitoring-api/)

**SolarEdge (Monitoring Platform / SolarEdge ONE)**
- Module-level monitoring, "free for 25 years". 1 million monitored sites reached in Apr 2019. — [QualEnergia (2 Apr 2019)](https://www.qualenergia.it/articoli/solaredge-and-its-1-million-monitored-pv-sites/)
- SolarEdge ONE for C&I (announced 20 Jun 2024): fleet management, integration of PV, storage, EV chargers and building assets, remote troubleshooting, live alerts. — [Slice of Energy (Jun 2024)](https://www.sliceofenergy.com/p/solaredge-launches-one-ci-energy-optimization-platform). Global rollout (3 Dec 2024): optimization modes (self-consumption, peak shaving), tariff optimization, grid participation. No pricing disclosed. — [BusinessWire (3 Dec 2024)](https://www.businesswire.com/news/home/20241203224482/en)
- ONE Controller for residential (24 Apr 2025): §14a EnWG compliance (Germany), EV chargers from ABB, MENNEKES and Wallbox, heat pumps via SG-ready/Vaillant, dynamic tariffs. — [BusinessWire (24 Apr 2025)](https://www.businesswire.com/news/home/20250424009890/en)
- Monitoring API: per-site API key from the portal (Admin > Site Access > API Access), "daily rate limit of 300 requests per day". — [Home Assistant SolarEdge integration docs](https://www.home-assistant.io/integrations/solaredge/)
- API change: the V1 key-based monitoring API is reported to be discontinued in Nov 2026 and replaced by V2 with OAuth2. Users report that the old admin-panel key route stopped working by 10 Sep 2026. — [Home Assistant community (Aug–Sep 2026)](https://community.home-assistant.io/t/solaredge-v1-retirement-what-are-other-home-assistant-users-doing/1022749) (community source; not confirmed on a SolarEdge page)

**Enphase (Enlighten / Enphase App / Installer Platform)**
- Free owner monitoring includes historical per-panel data. Real-time per-panel data is reserved for the paid "Enlighten Manager", "available for purchase by consumers as a subscription or one-time cost". No price given. — [Florida Solar Design Group (15 Jan 2023)](https://floridasolardesigngroup.com/enphase-lifetime-free-solar-monitoring-works/) (installer blog; the Enphase FAQ link redirected and was not read)
- Developer API plans: Watt (free, 10k hits/mo), Kilowatt ($25/mo), Megawatt ($250/mo), Gigawatt ($1,500/mo). — [Enphase developer plans](https://developer.enphase.com/plans) (from market_users_vietnam.md)
- VPP API plan: "Available only to aggregators/utilities/TPOs registered as Enphase Grid Services partners". Covers PV, battery, EVSE and heat-pump control, streaming API, "Push-based telemetry (1-min)", "OCPP-based EVSE control", VPP capacity forecast. Price: "Contact us". — [Enphase developer VPP plans](https://developer-v4.enphase.com/vpp-plans)
- European VPP expansion (14 Oct 2025): NL, DE, UK, BE. One-minute data streaming, VPP event alerts, solar curtailment, heat pump/EV charger control via partners (Kraken, NextEnergy, ison, LichtBlick). — [SolarQuarter (14 Oct 2025)](https://solarquarter.com/2025/10/14/enphase-expands-virtual-power-plant-capabilities-across-europe-with-advanced-grid-and-home-energy-controls/)

**GoodWe SEMS / SEMS+**
- Sep 2024 upgrade: automatic fault alerts, remote troubleshooting and parameter adjustment, customizable reports. The Ezlogger 3000C supports 100 devices. The article lists protocols "IEC104, Modbus-TCP, and IEEE 2030.5" (as written: "IEEE 2030.50"). — [Solar Power World (4 Sep 2024)](https://www.solarpowerworldonline.com/2024/09/goodwe-upgrades-inverter-monitoring-management-platform/)
- SEMS+ global launch on 6 Jan 2026 for owners, installers, O&M and multi-site operators. Features:
  - an AI Agent with natural-language troubleshooting
  - AI Scheduling (consumption, weather, tariffs → arbitrage)
  - AI Health Diagnosis "one-click"
  - IV Curve Diagnosis and battery consistency analysis
  - integration of "13+ device categories" including third-party equipment
  - Sankey diagrams and heatmaps
  - 10-second data refresh and 2-second remote-control response
  — [PV Time (Jan 2026)](https://www.pvtime.org/?p=25915)
- API access: contact sales and sign an NDA. Limit "3600 API calls per hour per GoodWe API account". — [Solytic KB](https://kb.solytic.com/en/knowledge/set-up-api-access-goodwe-api)

**Solis SolisCloud**
- Features: "Smart I-V curve scan, system health report, string-level fault finding", alarms with repair recommendations, customizable notifications, multi-device support (inverters, export power managers, weather stations), team management. — [Solis US SolisCloud page](https://www.solisinverters.com/us/accessories6/SolisCloud_us.html)
- API (US/Canada guide): email support and API is enabled within 24 h. KeyID, KeySecret and URL come from Service > API Management. Credentials can be shared so third parties can pull "many plants registered to multiple different Organization accounts". — [Solis US service: SolisCloud API Guide](https://usservice.solisinverters.com/support/solutions/articles/73000591225-soliscloud-api-guide)

**Growatt (ShineServer/OSS/ShinePhone/ShineTools)**
- OSS (Online Smart Service) offers remote diagnostics, parameter modification, firmware upgrades and Zendesk ticketing. ShineTools offers one-click remote diagnostic and remote parameter modification. — [IPS News (2 Jun 2026; sponsored content)](https://ipsnews.net/business/2026/06/02/why-australian-solar-installers-trust-growatt-support-tools-and-partner-benefits-in-2026/)
- API: the classic username/password API (same as the ShinePhone app) has "strict rate limits that can result in your account being locked out for up to 24 hours". The token-based OpenAPI v1 is "the officially supported method" and generated in the ShinePhone app. Write controls include charge/discharge power, SOC thresholds, AC-charge switch and time schedules. HA polls every 5 min. — [Home Assistant Growatt docs](https://www.home-assistant.io/integrations/growatt_server)
- AMMP describes ShineServer as "a closed system limited to Growatt hardware only". — [AMMP comparison page](https://ammp.io/compare/growatt) (competitor marketing)

**Deye / SOLARMAN**
- SOLARMAN describes itself as an IoT ecosystem provider (data loggers, gateways, meters, optimizers, C&I EMS) with SaaS platforms SOLARMAN Smart (residential), SOLARMAN Business (installers/distributors) and SOLARMAN Cloud/OpenAPI. It claims "190+ Countries & Regions" and "1.5M+ Trusted Global Users". — [SOLARMAN device manufacturers page](https://www.solarmanpv.com/?p=191)
- SOLARMAN Business manages "all SOLARMAN devices, third-party inverters, and smart loads". Its Smart O&M covers alerts, causes and maintenance suggestions. Claimed outcomes: diagnostics +60%, on-site maintenance cost −20%, generation +5–10% (vendor claims). No pricing published. — [SOLARMAN Business page](https://www.solarmanpv.com/products/solarman-business)
- OpenAPI docs are at doc.solarmanpv.com after "API activation". The FAQ does not describe the application process. — [SOLARMAN Help Center Open API FAQ](https://helpcenter.solarmanpv.com/portal/en/kb/articles/open-api-faq-summary)
- Deye has published a "Deye Cloud data migration announcement" in many languages, including Vietnamese. The page returned 403, so content and date are unverified. — [Deye (VI)](https://deye.com/vi/deye-cloud-data-migration-announcement/)

### Inferences
- **INFERENCE**: Monitoring is a free, hardware-subsidized commodity at the OEM level. Paid layers exist only where OEMs sell (a) API access to third parties (Enphase, SMA), (b) premium energy optimization (SMA Energy Maximizer Premium), (c) service/warranty bundles (SMA Smart Connected), or (d) installer real-time detail (Enphase Enlighten Manager). Huawei has none of these as visible public price lists.
- **INFERENCE**: Comparison matrix (✔ = evidenced; ? = not evidenced in this research):

| Capability | FusionSolar | iSolarCloud | SMA ennexOS | SolarEdge | Enphase | GoodWe SEMS+ | SolisCloud | Growatt | SOLARMAN |
|---|---|---|---|---|---|---|---|---|---|
| Free owner monitoring | ✔ | ✔ | ✔ | ✔ (25 yr) | ✔ | ? (implied) | ? (implied) | ? (implied) | ? |
| Module-level data | ✔ (optimizers) | ? | ? | ✔ native | ✔ native (real-time per-panel is paid) | ? | ? | ? | ? (optimizer HW) |
| Smart I-V scan | ✔ | ✔ | ? | n/a | n/a | ✔ | ✔ | ? | ? |
| AI scheduler / agent | ✔ EMMA, AI Agent | ? | ✔ Energy Maximizer | ✔ ONE | ? | ✔ | ? | ? | ✔ (claims) |
| EV charger in app | ✔ SCharger | ✔ | ? | ✔ | ✔ (VPP API) | ? | ? | ? | ? |
| VPP / aggregator API | ? | ? | ✔ GridControl API | ✔ "grid participation" | ✔ VPP plan, 1-min push | ? | ? | ? | ? |
| Third-party devices | ✔ (EMMA loads) | ? | ? | ✔ (chargers, HP) | ✔ via partners | ✔ 13+ categories | ✔ (meters, WS) | ✗ | ✔ |
| Published API pricing | ✗ | ✗ | ✔ (fees) | free key (300/day) | ✔ | ✗ (NDA) | ✗ | free token | ✗ |
| Webhooks/push | ✗ | ? | ? | ✗ | ✔ (VPP only) | ? | ? | ? | ? |

- **INFERENCE**: For a vendor-agnostic rebuild, the realistic data-acquisition order is: (1) local Modbus/SunSpec through your own edge gateway, which gives the best latency and independence; (2) OEM cloud APIs as importers (SolarEdge V2 OAuth, Growatt token, iSolarCloud Open API, SolisCloud key, SMA paid API, Huawei Northbound, GoodWe NDA, SOLARMAN OpenAPI); (3) FTP/CSV push as a fallback.

### Gaps
- No official 2025–2026 feature pages were fetched for Enphase's installer platform or for Growatt OSS beyond sponsored content. iSolarCloud's user/GW count after 2023 was not found.
- iSolarCloud's official developer portal terms, rate limits and pricing were not found.
- The SolarEdge V2 API rate limits and whether V2 is free were not found.
- The content of Deye Cloud's migration notice (403) is unknown.
- I found no OEM documenting outbound webhooks for standard monitoring. Absence is inferred, not confirmed.

---

## Q2. Vendor-agnostic platforms: pricing models and data acquisition

### Takeaway
Independent platforms sell per-kWp/MWp or per-site subscriptions, often with a base fee. They acquire data in three ways: (a) their own dataloggers/DAS (meteocontrol blue'Log, AlsoEnergy/Stem PowerTrack Logger, Solar-Log, Gantner Q.reader), which also act as power plant controllers for export limits; (b) OEM cloud API importers (VCOM imports Huawei, Sungrow, SMA, SolarEdge, Fronius, GoodWe); (c) SCADA/historian integration for utility scale (Power Factors). Published prices are rare. Solytic is the most transparent (€100/yr + €0.20/kWp). The differentiators over OEM apps are multi-brand portfolios, PR/availability KPIs against satellite irradiance, ticketing/CMMS, financial and contract reporting, and an open API.

### Cited Findings

**meteocontrol VCOM**
- VCOM Cloud covers monitoring, technical operations management and data hosting for plants or portfolios. It includes battery monitoring, a mobile app, the VCOM API and CMMS. blue'Log X-series dataloggers are "the heart of on-site monitoring" and "serve as the interface to grid integration". North America promo: 6 months free for one site with a 2-year or continuous license, billed on 3-month intervals. No list price. — [meteocontrol US switch page](https://www.meteocontrol.com/us/switch-now-to-vcom-cloud)
- VCOM import from the Huawei FusionSolar API: 5-min measuring interval, 15-min pull via HTTPS/JSON. A nightly job re-requests the past 7 days. The help center also lists imports for Sungrow iSolarCloud, SMA, SolarEdge, Fronius Solar.web and GoodWe APIs. — [meteocontrol help center](https://help-center.meteocontrol.com/en/vcom-cloud/latest/huawei-fusionsolar-api-1)
- Per Solytic's comparison, VCOM data resolution is 1/5/10/15 min. PR is "fully implemented". Snow/shading/soiling analysis is "optional". — [Solytic vs VCOM (undated, Solytic marketing)](https://solytic.com/vcom-by-meteocontrol-vs-solytic/)

**Solytic**
- Price: "€ 100 a year and € 0.2 per kWp". Hardware independent, "software only". Data from "1 min onwards". PR calculation "in beta" at the time of writing. Ticketing, unlimited users, string plans/digital twins, satellite weather data. — [Solytic vs VCOM](https://solytic.com/vcom-by-meteocontrol-vs-solytic/)
- Solytic's undated comparison of 24 platforms (based partly on pv magazine's Nov 2018 product database) gives per-MWp/yr prices: Solytic €200, Solar-Log WEB Enerest €1,600, SENS €312. It lists Power Factors at "$9.99/month", which looks implausible for a utility APM and is probably stale or misattributed. All others are "not publicly disclosed". It also says costs "vary with the size of your portfolio". — [Solytic PV monitoring software comparison](https://solytic.com/comparisons/pv-monitoring-software-comparison/) (treat prices as dated, likely 2019–2021)

**AlsoEnergy (Stem) PowerTrack**
- Scale: "200,000+ sites", "50+ countries", "25 GW", "15 years". Features: remote troubleshooting, PPC configuration, BESS remote control, "over a dozen templated reports" (financial reports, site validations, capacity tests), fault detection improving "signal-to-noise ratio by 50%", ESG sharing. — [AlsoEnergy PowerTrack flier (undated)](https://home.alsoenergy.com/resources/flier-alsoenergy-powertrack)
- DAS hardware: PowerTrack Logger, PowerLogger 1000, PowerManager 2200 (export control, high-frequency logging). "8,000+ drivers and point maps". Modbus TCP/RTU. Monitoring sold in "1 or 5 year terms", including data storage. No price published. — [Stem DAS and SCADA page](https://www.stem.com/?p=29316)

**Power Factors (Unity; Drive; 3megawatt BluePoint)**
- Acquired 3megawatt (BluePoint asset management) on 18 May 2021. Combined platform supports "some 110GW of solar and wind assets". BluePoint centralizes plant info and standardizes workflows and invoicing/reporting. — [PV Tech (May 2021)](https://pv-tech.org/power-factors-acquires-asset-management-software-firm-3megawatt); [Solar Power World](https://www.solarpowerworldonline.com/?p=94510)
- Unity suite: Monitoring & Control (local/central SCADA, PPC, EMS), Technical Asset Management (APM, Advanced Insights, Field Service Management), Commercial Asset Management (Asset Oversight, Invoice Management). "600+ global customers". AI assistant "REMI". — [Power Factors Unity page](https://powerfactors.com/?p=5335)
- European Energy chose Unity APM for 2.4 GW across 11 countries (9 Apr 2025), citing automated data-issue detection with "best-fit replacements". — [Power Factors news (Apr 2025)](https://www.powerfactors.com/news/european-energy-partners-with-power-factors-to-boost-asset-performance)
- 3megawatt alone reported 30 GW of assets in 2019. — [Solar Power World (Apr 2019)](https://www.solarpowerworldonline.com/2019/04/3megawatt-reaches-30-gw-renewable-energy-assets/) (headline only)

**Solar-Log**
- Solar-Log Base comes in 15 kWp, 100 kWp and 2 MWp variants, with expandable licenses (Base 15 to 30 kWp, Base 100 to 250 kWp). Interfaces: 2×RS485 or 1×RS422, 2×Ethernet, S0, USB. "Compatible with inverters from all the major manufacturers". Feed-in reduction with dynamic self-consumption allowance. Remote active/reactive power control. EnBW direct-marketing VPN. Cloud: WEB Enerest 4. — [Solar-Log Base datasheet (BayWa r.e.)](https://solar-distribution.baywa-re.de/out/media/1-SL_Base_SolarLog_Datasheet_Solar-Log_Base_EN.pdf)

**Solar Analytics (Australia, residential)**
- Inverter Integration (no hardware; Fronius, Sungrow, GoodWe, GE, LG): A$6/month, A$60/year or A$250 for 5 years, per inverter. Wattwatchers device renewals: A$10/mo or A$95/yr, with new installs unavailable after 1 Jul 2026. CATCH Control device: subscription free with the device. Data in "up to 5 second intervals", circuit-level monitoring, automated fault/shading diagnostics. — [Solar Analytics pricing](https://www.solaranalytics.com.au/pricing)
- Value over OEM apps: performance alerts against expected output (weather, history) and a Plan Optimizer for tariffs. — [SolarQuotes (17 Jul 2023)](https://www.solarquotes.com.au/blog/solar-analytics-integrated/)

**AMMP, SOLARMAN Business, others**
- AMMP integrates "30+ device brands" (Growatt, Huawei, SMA, SolarEdge…). It offers portfolio analytics, weather integration, custom alerting (email, Slack/Teams), financial/PPA reporting, API access, battery/generator monitoring and O&M ticketing. — [AMMP compare page](https://ammp.io/compare/growatt)
- pv magazine/Amperecloud's "PV Monitoring Software Comparison 2024" covers more than 10 providers (VCOM, Web Enerest, Amperecloud, Power Factors Unity…) across "over 40 features": alarms, CMMS, data management, reporting. — [pv magazine USA (26 Feb 2024)](https://pv-magazine-usa.com/?p=17311)

### Inferences
- **INFERENCE**: Pricing archetypes for a rebuild's business model:
  1. Per kWp/yr plus a base fee (Solytic: €0.20/kWp/yr + €100/yr; older Solar-Log WEB Enerest about €1.60/kWp/yr)
  2. Per site per year, tiered by size (the SMA API fee model: €30/50/70)
  3. Hardware plus a 1–5 year monitoring term (AlsoEnergy, Solar-Log)
  4. Per inverter per month for residential (Solar Analytics A$6/mo)
  5. Enterprise/quote-based for utility APM (Power Factors, VCOM)
- **INFERENCE**: Platforms that own a datalogger (meteocontrol, AlsoEnergy, Solar-Log, Gantner) can offer power plant control and zero-export, which pure API importers cannot. That matters directly in Vietnam (see Q6).
- **INFERENCE**: AlsoEnergy's "8,000+ drivers" shows that the device-driver library is the real moat of vendor-agnostic monitoring, not the dashboards.

### Gaps
- No current list prices found for VCOM, PowerTrack, Power Factors, SOLARMAN Business or Bluesky. The Solytic table is dated and partly suspect.
- "3megawatt Bluesky" as a product name was not found. Searches return BluePoint (3megawatt's product). It may be confused with another vendor.
- blue'Log XM/XC protocol support (IEC 104, IEC 61850, SunSpec) was not verified: the datasheet link returned 404.

---

## Q3. FusionSolar differentiators and weaknesses vs. these platforms

### Takeaway
FusionSolar's real differentiators come from end-to-end vertical integration: inverter firmware features (Smart I-V, AFCI, optimizer layout, grid-forming in FusionSolar 9.0), one app for PV + LUNA battery + SCharger + EMMA loads, deep remote commissioning and configuration, and batch upgrades up to 50,000 devices. Its weaknesses are on the openness side:
- installer-gated, strictly throttled, pull-only API
- one Modbus client at a time
- 15-month high-resolution retention (EU)
- no CSV export in the app
- regulatory and geopolitical exposure in the EU/US

Vendor-agnostic platforms win on multi-brand, PR/availability analytics, CMMS and finance. Other OEMs have caught up on I-V scanning (Sungrow, Solis, GoodWe) and AI scheduling (GoodWe, SMA, SolarEdge).

### Cited Findings
- Huawei SmartPVMS installer features: automatic device discovery by QR scan, SmartDesign layout sync, batch upgrade of up to 50,000 devices. C&I: I-V on all strings, module-level supervision up to 60 MW, four defect types at >90% accuracy. — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer); [Huawei C&I Smart PVMS (FR)](https://solar.huawei.com/fr/products/ci-smart-pv-management-system/) (via features_editions.md)
- FusionSolar 9.0 utility: grid-forming string inverters, "FusionSolar Agent" edge-to-cloud AI. Europe launch 29 Apr 2026. — [pv magazine (2 Dec 2025)](https://www.pv-magazine.com/2025/12/02/huawei-unveils-fusionsolar-9-0-platform-with-ai-grid-forming-tech/); [pv Europe (Apr 2026)](https://www.pveurope.eu/inverter/huawei-debuts-fusionsolar-90-grid-forming-string-inverters)
- Competitors' parity on I-V: Sungrow ">90% accuracy" (2023), Solis "Smart I-V curve scan", GoodWe SEMS+ "IV Curve Diagnosis" (2026). — [pv magazine USA](https://pv-magazine-usa.com/press-releases/sungrow-launches-new-version-of-its-management-and-monitoring-system-isolarcloud/); [Solis](https://www.solisinverters.com/us/accessories6/SolisCloud_us.html); [PV Time](https://www.pvtime.org/?p=25915)
- Weaknesses (from prior notes): Northbound per-minute/day quotas and session cap; 24 h refresh recommended by Solytic; no webhooks; owner-consent breakages (Sep 2025); EU retention of 15 months for device history; App Store complaints about no CSV export and limited SOC-based battery scheduling; the dongle allows only one Modbus client. — [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/); [Huawei EU Data Act](https://digitalpower.huawei.com/en/eu-data-act); [App Store JP](https://apps.apple.com/jp/app/id1529080383); [HA community](https://community.home-assistant.io/t/huawei-solar-integration-modbus-via-smart-dongle-blocks-fusion-solar-cloud-data/1014084)
- Geopolitics: Lithuania remote-access ban for Chinese vendors on systems over 100 kW (in force 1 May 2025, existing sites by 1 May 2026). EU funding restriction on high-risk-vendor inverters (May 2026, transition to 1 Nov 2026). — [PV Tech (Nov 2024)](https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation); [ESS News (4 May 2026)](https://www.ess-news.com/2026/05/04/eu-funding-ban-on-high-risk-inverters-including-chinese-suppliers-extends-to-bess-pcs/) (via architecture_security.md)
- Huawei utility management offers RESTful API and IEC 104 for third-party SCADA. — [Huawei Smart PV Plant Management System](https://solar.huawei.com/en/products/smart-pv-plant-management-system/) (via features_editions.md)

### Inferences
- **INFERENCE**: Only Huawei and Sungrow own the full stack across residential through utility at Huawei's scale. Huawei's unique selling points in the current market are breadth (residential to utility grid-forming) and the strength of installer remote configuration, not any single monitoring feature.
- **INFERENCE**: The geopolitical restrictions target the *remote-access channel* (vendor cloud → device). That creates demand for a third-party or locally hosted monitoring and control layer that reads Huawei, Sungrow and others locally. This is exactly the space a vendor-agnostic rebuild could occupy, especially for EU-exposed or security-sensitive customers.
- **SPECULATION**: Several OEMs are tightening their APIs: Huawei owner consent (2025), SolarEdge V1 → OAuth V2 (2026), Growatt classic → token. That raises the integration cost for vendor-agnostic platforms and may push them further toward their own dataloggers.

### Gaps
- No primary 2025–2026 Huawei page documents AFCI reporting in the portal (noted as a gap earlier).
- No independent benchmark compares the accuracy of I-V diagnosis across Huawei, Sungrow, Solis and GoodWe.

---

## Q4. Capabilities users expect but FusionSolar lacks (or makes hard)

### Takeaway
Based on user complaints and what competitors offer, the main missing or weak capabilities are:
- multi-brand portfolio monitoring
- bulk data export (CSV) and long-term raw data retention
- push/webhook integration and a self-serve owner API
- standardized PR/availability per IEC 61724 using measured or satellite irradiance
- CMMS/ticketing and work orders tied to alarms
- financial/PPA reporting
- flexible user-defined battery rules (SOC-based)
- a published, paid API tier with an SLA
- VPP/aggregator APIs with fast telemetry

### Cited Findings
- App reviews: no CSV export, no SOC-threshold battery scheduling, more taps to reach daily data. — [App Store JP](https://apps.apple.com/jp/app/id1529080383) (via market_users_vietnam.md)
- Vendor-agnostic platforms advertise ticketing/CMMS, PR, string plans/digital twins, satellite weather comparisons and portfolio views as core features. — [Solytic vs VCOM](https://solytic.com/vcom-by-meteocontrol-vs-solytic/); [meteocontrol](https://www.meteocontrol.com/us/switch-now-to-vcom-cloud); [AMMP](https://ammp.io/compare/growatt)
- PowerTrack offers financial reports, site validations and capacity tests. — [AlsoEnergy flier](https://home.alsoenergy.com/resources/flier-alsoenergy-powertrack)
- Enphase VPP API offers 1-minute push telemetry and OCPP-based EVSE control for aggregators. — [Enphase VPP plans](https://developer-v4.enphase.com/vpp-plans)
- Solar Analytics adds expected-vs-actual alerts and tariff plan optimization that OEM apps lack. — [SolarQuotes](https://www.solarquotes.com.au/blog/solar-analytics-integrated/)
- Huawei Northbound history is limited to "10 devices of the same type in three days" per call. — [SmartPVMS 24.2.0 NB API](https://support.huawei.com/enterprise/en/doc/EDOC1100358266/b9df65c2/monitoring) (via api_integration.md)
- EnergyID: legacy FusionSolar integrations stop syncing on 1 Dec 2026 after the move to a "new, more secure" method. — [EnergyID help](https://help.energyid.eu/en/apps/migrating-your-fusionsolar-integration-to-the-new-version)

### Inferences
- **INFERENCE**: Ranked list of FusionSolar gaps that a rebuild should close, first to last:
  1. Multi-vendor ingestion
  2. Raw-data ownership (unlimited retention, CSV/Parquet export, scheduled exports)
  3. Event-driven integration (webhooks, MQTT, Kafka out)
  4. IEC 61724 KPIs (PR, temperature-corrected PR, availability, expected yield)
  5. CMMS (alarm → ticket → work order → SLA)
  6. Rules engine for user-defined alarms and battery/load automation
  7. Financial/contract reporting (PPA, revenue, tariffs in VND)
  8. Open API with published quotas
  9. Aggregator/VPP interface
- **INFERENCE**: For ChinhTa's context (VOMS repair management, CPO tooling), the alarm → work-order bridge is the highest-leverage gap, since FusionSolar has no push and only polled `getAlarmList`.

### Gaps
- No structured survey of installer needs (e.g., Wood Mackenzie or SEIA). The ranking is inferred from features and complaints.

---

## Q5. Technical building blocks for a vendor-agnostic / OEM-style rebuild

### Takeaway
A rebuild needs six layers:
1. **Edge acquisition**: Modbus RTU/TCP with SunSpec models where available, vendor register maps (Huawei, Sungrow, …), meter protocols, store-and-forward buffering, and local control (export limit / PPC).
2. **Northbound to utilities/aggregators**: IEC 60870-5-104 for Vietnam EVN/dispatch; IEEE 2030.5 / OpenADR for VPP markets; OCPP 1.6/2.0.1/2.1 for chargers.
3. **Cloud ingestion** over MQTT/HTTPS, plus OEM-API importers with per-vendor rate-limit handling.
4. **Time-series storage**: public case studies show TimescaleDB/Postgres, InfluxDB, AWS Timestream/SiteWise, and S3 data lakes.
5. **Domain services**: asset model, alarm engine, KPI engine per IEC 61724, reports, CMMS.
6. **APIs and apps**.

Open-source references exist for the edge EMS (OpenEMS, EPL-2.0) and gateways (ThingsBoard IoT Gateway).

### Cited Findings

**Device protocols and standards**
- IEEE 1547-2018 names three DER communication interfaces: SunSpec Modbus ("a default communication and interoperability standard"), IEEE 2030.5 and IEEE 1815 (DNP3). SunSpec Modbus "is fully interoperable with IEEE 2030.5 and IEEE 1815". — [SunSpec 1547 initiative](https://sunspec.org/sunspec-1547-initiative/)
- The SunSpec Modbus 701–712 DER information models were approved in April 2021, replacing the 2009-era 100 series. They are referenced in IEEE 1547-2018. — [SunSpec (2021)](https://sunspec.org/sunspec-modbus-700-series-der-information-models-are-now-approved/)
- IEEE 2030.5 in practice (California Rule 21, Australia CSIP-AUS): "more than 80 percent of inverter manufacturers passed compliance via the gateway-attestation path". "IEEE 2030.5 lives at the gateway and at the aggregator, not at the inverter terminal". SunSpec Modbus ↔ 2030.5 translation is "structurally simpler" than cloud-API or OCPP translation. — [Codibly (7 May 2026)](https://codibly.com/blog/articles/ieee-2030-5-protocol-deployment-aggregator-boundary) (vendor blog)
- OpenADR 3 positions itself for DER management. — [OpenADR Alliance PDF](https://www.openadr.org/assets/OpenADR%203%20and%20DER%20Management_v1.0.pdf) (not read in full)
- OCPP 2.1 (Jan 2025) adds native bidirectional V2G/V2H via ISO 15118-20, DER grid-code settings on chargers, and local energy-management constraints from CSMS, local EMS or grid "via different protocols (OCPP, Modbus, etc.)". — [Trialog](https://www.trialog.com/en/how-ocpp-2-1-enables-bidirectional-charging-and-smarter-energy-management)
- Huawei SCharger can be controlled by third-party backends via OCPP (evcc "ocpp-huawei" template, dimming only). A Huawei FusionCharge AC OCPP 1.6 manual exists. — [evcc docs](https://docs.evcc.io/en/chargers/huawei-scharger-7ks-s0.md); [Huawei FusionCharge OCPP1.6 PDF (Solexis)](https://shop.solexis.ch/documents/file/mobilit%c3%a9%20%c3%a9lectrique/huawei/ma_en_huawei_fusionchargeac3pevcharger_ocpp1.6.pdf) (PDF not read)
- Huawei local Modbus: one client at a time; port 6607/502; read no faster than about every 5 s via the dongle. — [wlcrs/huawei_solar](https://github.com/wlcrs/huawei_solar); [evcc #1928](https://github.com/evcc-io/evcc/discussions/1928) (via api_integration.md)

**Edge gateway / datalogger options**
- Commercial loggers/PPCs: meteocontrol blue'Log XC used for "Monitoring and PPC (Zero-Feed-In)" in Vietnam. — [meteocontrol MP Pack reference](https://www.meteocontrol.com/en/company/references/zero-feed-in-and-monitoring-for-the-pv-plant-mp-pack). Solar-Log Base (RS485/Ethernet, feed-in management). — [datasheet](https://solar-distribution.baywa-re.de/out/media/1-SL_Base_SolarLog_Datasheet_Solar-Log_Base_EN.pdf). AlsoEnergy PowerTrack Logger/PowerManager 2200. — [Stem](https://www.stem.com/?p=29316). Gantner Q.reader + PPC. — [Gantner](https://www.gantner-environment.com/en/news/news-detail/gantner-supplies-to-five-large-rooftop-solar-power-plants-in-vietnam)
- Industrial gateways for EVN compliance: the Advantech ADAM-3600 is positioned for EVN Decision 1570 (protocol conversion Modbus TCP ↔ IEC 60870-5-104, multi-inverter management, remote dispatch, SD-card buffering during outages). The requirement page lists ≥64 kbps and ≤125 ms latency. — [Advantech VN](https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet)
- Open source: OpenEMS (Edge on site for device communication and control algorithms; Backend aggregates Edges; UI). Protocols: Modbus, SunSpec, MQTT, REST. EPL-2.0 (Edge/Backend), AGPL-3.0 (UI). Originated at FENECON (FEMS). — [OpenEMS GitHub fork README](https://github.com/GGBeer/openems)
- ThingsBoard IoT Gateway (Python, Modbus/MQTT connectors) is used in academic PV monitoring work. — [PyPI thingsboard-gateway](https://pypi.org/project/thingsboard-gateway/3.8.4/); [UFU thesis](https://repositorio.ufu.br/handle/123456789/26449)

**Time-series storage (evidence from public case studies only)**
- SolarNetwork (renewable energy data platform) uses TimescaleDB because "we already used Postgres" and it manages partitioning better. It evaluated Cassandra, Druid and CockroachDB. Benefits: hypertables, continuous aggregates. — [Tiger Data/Timescale case study (undated)](https://www.tigerdata.com/case-studies/solarnetwork)
- Enprove (Enelyzer, energy analytics) moved time series from SQL Server/Postgres to InfluxDB Cloud Dedicated. It has 75,000+ series and up to 6 years of history per customer. Telegraf ingests from MQTT/APIs/FTP/PLCs, Postgres holds context, Grafana and React/Highcharts handle display, Rust backend on AWS. — [InfluxData (24 Jul 2026)](https://www.influxdata.com/customer/enprove/)
- Bboxx (off-grid solar home systems): InfluxDB Cloud, about 30k active units reporting every 4 h via GSM, Python analytics on 7-day chunks. — [InfluxData webinar](https://www.influxdata.com/resources/bboxx-counts-influxcloud-optimize-performance-85000-solar-panels-rural-areas/) (undated, older)
- Amazon's own renewable-plant monitoring (2021, updated 2023): Greengrass, Lambda and Kinesis for ingestion; IoT SiteWise (asset model) plus Timestream (raw time series) plus S3; Managed Grafana. Hundreds of assets in more than 30 countries, up to 10,000 tags per asset. Protocols: OPC-UA, Modbus, DNP3, APIs, flat files. — [AWS for Industries (Oct 2021/Jan 2023)](https://aws.amazon.com/blogs/industries/amazon-achieves-near-real-time-renewable-energy-plant-monitoring-to-optimize-performance-using-aws)
- AWS reference (2020/2021): IoT Core → Kinesis/Firehose → S3 data lake, Aurora for Grafana, IoT Events for alarm state machines. — [AWS for Industries](https://aws.amazon.com/blogs/industries/real-time-operational-monitoring-of-renewable-energy-assets-with-aws-iot)
- Sungrow claims >100 PB storage and 99.99% uptime for iSolarCloud (technology not disclosed). — [iSolarCloud datasheet](https://info-support.sungrowpower.com/application/pdf/2024/04/18/DS_20240417_iSolarCloud_Datasheet_V3_EN.pdf)

**PV performance metrics standards**
- IEC 61724-1 PR = Yf / Yr = (E_out / P0) / (H_i / G_i,ref). Temperature-corrected PR'STC uses C_k = 1 + γ(T_mod,k − T_ref), with γ ≈ −0.3%/K typical. The Performance Index (PPI/EPI) is measured vs. expected output from a detailed model. — [Hukseflux application note](https://hukx.com/applications/how-to-calculate-pv-performance-ratio-and-performance-index)
- IEC 61724-1:2021 keeps two classes: Class A ("high", utility and large commercial) and Class B ("medium", rooftop/small-medium commercial). The 2017 Class C is no longer used. Class A requires heated/ventilated pyranometers, module/air temperature, wind and soiling measurements. — [Hukseflux IEC 61724-1:2021 explainer](https://hukx.com/applications/the-iec-61724-12021-standard-for-pv-monitoring-systems-a-quick-explanation)
- IEC TS 61724-3:2016 defines the energy evaluation method. — [IEC webstore](https://webstore.iec.ch/en/publication/25466) (not read)

### Inferences
- **INFERENCE: reference architecture for the rebuild.**
  - **Edge**: a Linux gateway (or OpenEMS Edge) with a driver framework (Modbus RTU/TCP, SunSpec auto-discovery, vendor maps), a local rule/PPC loop for export limits, an SQLite/RocksDB buffer, and an MQTT (TLS) uplink. Optionally an IEC 104 slave for EVN.
  - **Cloud ingest**: MQTT broker (EMQX/HiveMQ/AWS IoT Core) → Kafka/Kinesis → normalizer to a canonical data model (SunSpec-like point names).
  - **OEM importer workers**: one per vendor, each with token-bucket rate limiting and nightly back-fill, the same pattern as VCOM's 7-day re-request.
  - **Storage**: TimescaleDB (fits a Postgres/Spring team) for raw 1–5-min data with continuous aggregates for hour/day/month, plus object storage (Parquet) for long-term raw data.
  - **Services**: asset registry (portfolio → site → device → string/module), alarm engine (threshold, state-machine, comms-loss, expected-vs-actual), KPI engine (PR, PR_STC, availability, specific yield), report scheduler (PDF/XLSX/CSV), CMMS, notification (push/email/Zalo/webhook).
  - **APIs**: REST + webhooks + MQTT out. OCPP CSMS for chargers (reusable from ChinhTa's CPO work).
- **INFERENCE: MVP/V1/V2 mapping.**
  - **MVP**: Modbus/SunSpec edge for 2–3 top Vietnamese brands, plus OEM API importers (Huawei, Sungrow, Solis/Deye-Solarman), time-series storage, dashboards, comms-loss and fault alarms, daily/monthly reports, CSV export, owner/installer roles.
  - **V1**: PR/availability per IEC 61724 using satellite or on-site irradiance, CMMS/work orders (VOMS integration), webhooks, zero-export/PPC at the edge, an EVN IEC 104 gateway option, multi-tenant installer portal, mobile app.
  - **V2**: I-V/string analytics where the vendor exposes it, AI anomaly detection and expected-yield models, BESS/EV (OCPP) energy management, tariff optimization, aggregator/VPP interfaces (IEEE 2030.5/OpenADR) if the market requires them, white-label OEM mode.
- **INFERENCE**: Smart I-V scanning cannot be replicated vendor-agnostically, because it is an inverter-firmware function. A rebuild can only *trigger and ingest* it where the OEM exposes it, or approximate it with string-current statistics (coefficient-of-variation analysis, which Huawei's utility system also uses).

### Gaps
- I found no public engineering blog from Huawei, Sungrow, SolarEdge or Enphase describing their own time-series stack.
- The IEC TS 63019 (availability) and IEC 61724-2/-3 contents were not retrieved. The exact availability formula is a gap.
- The OpenADR 3 PDF and IEEE 2030.5 CSIP specifics were not read in depth.

---

## Q6. Relevance to Vietnam: platforms used locally, EVN/regulatory monitoring requirements

### Takeaway
Vietnam's 2025–2026 rooftop framework is Decree 58/2025 as amended by Decree 243/2026 of 26 Jun 2026. It raises the surplus-sale cap to 50% of output until 31 Dec 2030. It requires medium-voltage-and-above rooftop systems that sell surplus to install equipment connecting to the dispatch level's data-collection, monitoring and control system. MV+ systems that don't sell must install a dispatch-controllable "bật tắt phát ngược" (reverse-feed on/off) device. Low-voltage systems are exempt from both. EVN's technical guidance (Decision 1570/QĐ-EVN; "EVN-RTMS" in academic literature) specifies Modbus TCP and IEC 60870-5-104 for monitoring and control and IEC 62056 for metering. A rebuild targeting Vietnamese C&I therefore needs an IEC 104-capable gateway and remote setpoint control, not only cloud dashboards. Foreign vendor-agnostic platforms (meteocontrol, Gantner) have documented Vietnamese C&I references. I found no reliable data on the popularity of Solarman or iSolarCloud in Vietnam.

### Cited Findings
- Decree 243/2026/NĐ-CP (26 Jun 2026) amends Decree 58/2025/NĐ-CP. Surplus traded "không vượt quá 50%" (not exceeding 50%), with a transition to 31 Dec 2030 that allows higher shares if the grid permits. — [VOV](https://vov.vn/kinh-te/noi-quy-dinh-ban-dien-du-tu-dien-mat-troi-mai-nha-len-50-post1310254.vov); [Tuổi Trẻ (26 Jun 2026)](https://tuoitre.vn/dien-mat-troi-mai-nha-duoc-ban-toi-da-50-dien-du-100260626212633186.htm)
- Consolidated text (VBHN 52, Decree 58 + Decree 243), Art. 10(5): MV-and-above systems selling surplus must "trang bị thiết bị, phương tiện kết nối với hệ thống thu thập, giám sát, điều khiển của Cấp điều độ" (install equipment and means to connect to the dispatch level's data-collection, monitoring and control system). MV+ systems not selling surplus must install a "thiết bị bật tắt phát ngược" (reverse-feed on/off device) operated in "off" mode (export allowed) and switched on at the dispatcher's request. Low-voltage systems need neither. — [VBHN 52 (VNPT portal PDF, 30 Jun 2026)](https://storage-vnportal.vnpt.vn/gov-tnn/7350/FileQuanTriTinTuc/VBHN%2052%20Nghi%20dinh%2058%20va%20ND%20243%2030.6.pdf)
- This supersedes the 20% cap of Decree 135/2024 noted in market_users_vietnam.md. **INFERENCE**: that earlier note is now outdated on the cap.
- EVN Decision 1570/QĐ-EVN (per Advantech's summary): Modbus TCP and IEC 60870-5-104 for monitoring and control, IEC 62056 for meter data. Data includes power, PF, voltage, current, meter readings, events and inverter status. Network: ≥64 kbps, ≤125 ms latency. No capacity thresholds or dates are given on that page. — [Advantech VN](https://www.advantech.com/vi-vn/resources/industry-focus/quyet-dinh-1570qd-evn-dien-mat-troi-mai-nha-dieu-can-biet) (vendor summary, not the decision text)
- An academic paper on an "EVN-RTMS"-compliant rooftop monitoring and control system uses Modbus TCP/IP plus IEC 60870-5-104 over VPN with a control cabinet (2025). — [VJOL (2025)](https://vjol.info.vn/tctbgd/article/view/121843)
- Vendor-agnostic references in Vietnam:
  - meteocontrol blue'Log X for the 994 kWp Dong Nam Viet Packaging rooftop, Bến Cát (2020, ecoligo). — [meteocontrol](https://meteocontrol.com/en/company/references/pv-monitoring-for-dong-nam-viet-packaging)
  - blue'Log XC "Monitoring and PPC (Zero-Feed-In)" for the 256 kWp MP Pack, Đà Nẵng (2022). — [meteocontrol](https://www.meteocontrol.com/en/company/references/zero-feed-in-and-monitoring-for-the-pv-plant-mp-pack)
  - Gantner Q.reader + PPC + Gantner.webportal for "five of the largest… commercial rooftop Solar projects in Vietnam" (undated, about 2019). — [Gantner](https://www.gantner-environment.com/en/news/news-detail/gantner-supplies-to-five-large-rooftop-solar-power-plants-in-vietnam)
- Sungrow claimed 45% of Vietnam's rooftop segment in 2020 (vendor self-claim). — [pv magazine (Dec 2020)](https://www.pv-magazine.com/press-releases/sungrow-hit-2-gw-shipment-of-sg110cx-for-vietnam-rooftops/) (via market_users_vietnam.md). Sungrow signed a 100 MW C&I distribution deal with DAT in Vietnam. — [PV Tech](https://www.pv-tech.org/news/sungrow-signs-100mw-ci-distribution-deal-with-dat-in-vietnam) (headline only)
- Deye publishes a Vietnamese-language Deye Cloud migration notice. — [Deye VI](https://deye.com/vi/deye-cloud-data-migration-announcement/) (403, content unverified)

### Inferences
- **INFERENCE**: For Vietnamese C&I (typically MV-connected), the 2026 rules turn "monitoring" into "monitoring + dispatch connectivity + controllable export". FusionSolar covers this with SmartLogger (export limiting) and, on utility, IEC 104. A rebuild must provide: (a) an IEC 104 slave/gateway to the dispatch center, (b) remote active-power setpoints and on/off for reverse feed, and (c) evidence logs. These are V1 must-haves for C&I, not V2.
- **INFERENCE**: Household (LV) systems face no dispatch-connection requirement. There the competition is the free OEM apps (FusionSolar, iSolarCloud, SolisCloud, SOLARMAN/Deye), so a rebuild must offer multi-brand plus O&M value to installers rather than charge homeowners.
- **SPECULATION**: Solarman/Deye and Sungrow are likely widespread among Vietnamese residential installers, given Deye's Vietnamese-language site and Sungrow's historical rooftop share. This is not evidenced by any market-share data found.

### Gaps
- No 2024–2026 Vietnam inverter or monitoring-platform market-share data. IMARC reports are paywalled.
- The text of Decision 1570/QĐ-EVN itself (date, capacity thresholds, which dispatch level: A0/A1/A2/A3 or distribution DMS) was not read. Only a vendor summary was available.
- No Vietnamese domestic monitoring SaaS vendors were identified with reliable sources.
- Whether EVN accepts inverter/SmartLogger-based export limiting as the "thiết bị bật tắt phát ngược" is unverified.
