# Huawei FusionSolar: Product Scope, Features, Editions and Apps (as of Oct 2026)

## 1. What exactly is "FusionSolar"? Brand vs. the Smart PV Management System (portal + app)

### Takeaway
"FusionSolar" is used at two levels. It is Huawei Digital Power's umbrella brand for its whole smart PV + storage line (inverters, optimizers, LUNA2000 ESS, SCharger, EMMA, SmartLogger, utility platforms such as "FusionSolar 9.0"). It is also the name of the cloud monitoring/O&M software, officially the "FusionSolar Smart PV Management System" (SmartPVMS): the web portal (e.g. intl.fusionsolar.huawei.com, region-specific) plus the "FusionSolar" mobile app. In 2019 that software replaced the older NetEco portal and FusionHome app.

### Cited Findings
- Huawei product pages name the software "FusionSolar Smart PV Management System (Installer)" / "(Owner)", shown with the "FusionSolar app" and "Smart PVMS" — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer); [Huawei SmartPVMS Owner](https://solar.huawei.com/en/products/smart-pv-management-system-owner)
- The brand covers hardware as well. Huawei country sites title product pages "… | Huawei FusionSolar" (e.g. the SCharger EV charger, C&I Smart PVMS) — [Huawei SCharger page](https://solar.huawei.com/ie/products/SCharger-7KS-S0-22KT-S0/); [Huawei C&I Smart PVMS (FR)](https://solar.huawei.com/fr/products/ci-smart-pv-management-system/)
- "FusionSolar 9.0" is a utility-scale solar-plus-storage platform generation (smart string inverter, sub-array controller, plant-level controller, integrated PV management system, plus the "FusionSolar Agent" AI layer). It is a solution generation, not a version of the app — [pv magazine, 2 Dec 2025](https://www.pv-magazine.com/2025/12/02/huawei-unveils-fusionsolar-9-0-platform-with-ai-grid-forming-tech/)
- History: between 30 Apr and 30 Jul 2019 the NetEco portal was phased out and the FusionHome app was updated/merged into FusionSolar, giving one platform for installers and customers. The unified EU URL is intl.fusionsolar.huawei.com (older info, 2021 article) — [VP Solar, 2021](https://www.vpsolar.com/en/fusion-solar-huaweis-new-solution-for-managing-its-plant/)
- The App Store publisher is "Huawei Digital Power Technologies Co., Ltd.". The app's own description: "FusionSolar, manage your smart PV plant anytime, anywhere". It lets installers and owners monitor plants, view real-time/historical data, manage production/consumption, do local commissioning and do maintenance — [App Store listing](https://apps.apple.com/cd/app/fusionsolar/id1529080383)
- Regional hosting: Huawei's FAQ lists region sites across Asia Pacific (Australia, China, Japan, Singapore), Europe (Germany, France, Spain), LatAm (Brazil, Mexico), MEA (UAE, South Africa, Egypt). A 2026 German guide says EU installations use cloud servers inside the EU, with encrypted transmission — [Huawei FAQ](https://solar.huawei.com/en/faqs); [solaranlage-tipps.de, Jun 2026](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026)

### Inferences
- When writing, keep three things apart: (a) the FusionSolar brand/solution generations (e.g. "FusionSolar 9.0" for utility); (b) the SmartPVMS cloud (portal + app) used mostly by residential and C&I; (c) on-prem or plant-level management systems for utility (NetEco1000S, Smart PV Plant Management System).
- The listed regional sites suggest several regional cloud instances (intl / eu5 / region-specific domains). I could not find an official list of domains.

### Gaps
- No official Huawei page found that gives a canonical list of FusionSolar cloud domains/regions (e.g. intl. vs eu5. vs region5.). Region data comes from the community FAQ only.
- No official statement on whether the SmartPVMS cloud carries its own platform version (e.g. "SmartPVMS V300R0xx") in 2026.

## 2. Main features of the web portal and app

### Takeaway
The portal and app cover plant KPI dashboards, an energy-flow graph, yield/revenue statistics, alarms by severity, device management, remote parameter setting, batch firmware upgrade, LUNA2000 battery monitoring, SCharger EV charger control, smart-load control via EMMA, and AI-based energy scheduling. Installers also get QR-scan commissioning, automatic device discovery and SmartDesign layout sync. Commercial/utility editions add Smart I-V Curve Diagnosis and module-level layout views.

### Cited Findings
**Monitoring and dashboards**
- Portal: real-time and historical data; plant KPI summary (yield, revenue, power); real-time status across plants; active alarms in four severities (Critical, Severe/Major, Minor, Warning); yield by day/month/year/lifetime; CO2 and coal-saved equivalents; per-plant device layout view — [VP Solar, 13 Jan 2025](https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/)
- Owner view: generation and revenue in real time by day/month/year; "all the power generation, electricity consumption, and storage data in one graph" (energy flow) — [Huawei SmartPVMS Owner](https://solar.huawei.com/en/products/smart-pv-management-system-owner)
- App (2026 guide): current generation in W, grid import/feed-in, day/month/year yields with CO2 savings, self-consumption ratio, LUNA2000 SOC and power flow, push notifications for faults and grid outages. The web portal holds multi-year history and full parameter access — [solaranlage-tipps.de, Jun 2026](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026)

**Installer / device management**
- Automatic device discovery by scanning the QR code on the inverter or EMMA. One scan adds all devices on the site. One-click sync of the physical PV-module layout from SmartDesign to mobile. Automatic time sync. Detection of device connection problems. Batch upgrade of up to 50,000 devices with selective upgrade. ESS monitoring with daily charge/discharge data. Detection of abnormal readings with rescan — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer)
- Support channels: 24/7 chatbot customer service, video tutorials, user guides, FAQs — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer)
- Huawei publishes a "FusionSolar Smart PV Management System Connection User Manual (Inverters + SDongle)" that covers setting parameters over the app — [Huawei support EDOC1100173984](https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app)

**Energy management / smart home (EMMA)**
- Remote control of third-party sockets, relays and circuit breakers from the app. Load-priority list (heat pumps, EV chargers, air conditioners, sockets). "Scheduled Green Electricity Usage". EMMA's AI forecasts PV surplus, reserves storage for outages, and uses consumption patterns, weather and price signals — [Huawei SmartPVMS Owner](https://solar.huawei.com/en/products/smart-pv-management-system-owner)
- Recommended residential hardware for SmartPVMS: SUN2000-5/6/8/10/12K-MAP0 (Smart Energy Controller), SUN2000-450W-P2 / 600W-P (Smart Module Controller, i.e. optimizer), LUNA2000-7/14/21-S1 (Smart String ESS), SmartGuard-63A-T0/AUT0 (backup box) — [Huawei SmartPVMS Installer](https://solar.huawei.com/en/products/smart-pv-management-system-installer)

**EV charger (SCharger)**
- SCharger-7KS-S0 (7 kW, 1-phase) and SCharger-22KT-S0 (22 kW, 3-phase; can drop to 1.4 kW by switching from 3-phase to 1-phase). Three authentication modes: FusionSolar app, RFID card, Bluetooth. The app shows real-time charging status and history, offers scheduled charging and account-based sharing with other users, has a "PV power preferred" surplus-charging mode, and does dynamic load balancing against household load. IP54, Red Dot 2023 — [Huawei SCharger page](https://solar.huawei.com/ie/products/SCharger-7KS-S0-22KT-S0/)

**Dynamic tariffs**
- App v25.4.100.011 (Jan 2026) release notes: "Connected to OTE dynamic electricity market" (OTE = Czech electricity market operator) — [App Store JP version history](https://apps.apple.com/jp/app/id1529080383)

**Smart I-V Curve Diagnosis / module-level (C&I / utility)**
- C&I Smart PVMS: online I-V curve analysis on all strings. Module-level supervision up to 60 MW. Detects four defect types at >90% accuracy. Cuts inspection and fault-location time by 50%. Cell-level ESS visibility (SOC, SOH, voltage, temperature). SmartEMO energy-management optimization, with automatic peak-shaving adjustment from historical data — [Huawei C&I Smart PVMS (FR)](https://solar.huawei.com/fr/products/ci-smart-pv-management-system/)

### Inferences
- AFCI and Smart I-V diagnosis run in the inverter firmware. The portal/app show the results and alarms, and I-V scans are started from the management system (C&I/utility).
- Optimizers (SUN2000-450W-P2/600W-P, MERC-1100/1300W-P) show up in the portal's physical-layout view at module level. This is consistent with the "abnormal reading" and SmartDesign layout-sync features.

### Gaps
- No primary 2025–2026 source found that describes AFCI reporting in the FusionSolar portal.
- No source found for a named "Smart Assistant" feature in the app. Huawei's AI branding found is "EMMA" (Smart Energy Management Assistant) and the "FusionSolar AI Agent" (see section 5).
- Google Play listing (package com.huawei.smartpvms) could not be fetched (permission timeout). Android version/date not checked.
- Did not fetch the full SmartPVMS user manual (EDOC1100173984), so full menu structure (Monitoring / Device Management / Alarms / Reports / System) is not confirmed from the document text.

## 3. How Residential, C&I and Utility-scale offerings differ

### Takeaway
Residential runs inverter + Smart Dongle (WLAN/4G) → FusionSolar cloud. EMMA handles home energy and the owner uses the app. C&I uses SmartLogger5000B / SmartMGC5000B as the site gateway, with the C&I SmartPVMS adding I-V diagnosis, module-level layout and SmartEMO peak shaving. Utility uses SmartLogger3000B plus plant-level management systems (NetEco1000S, which can be deployed on-premise; "Smart PV Plant Management System"), with RESTful API/IEC 104 SCADA integration and AI tracker/I-V features. The 2025–2026 utility generation is "FusionSolar 9.0" with grid-forming string inverters.

### Cited Findings
**Residential**
- Communication hub: Smart Dongle, either WLAN (2.4 GHz only) or 4G/LTE (needs SIM). Most connection problems come from the Dongle losing Wi-Fi after a router or password change — [solaranlage-tipps.de, Jun 2026](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026)
- The commissioning guide requires a 2.4 GHz WLAN and recommends WPA/WPA2, not WEP or WPA-TKIP — [Huawei Commissioning Guide EDOC1100273864, Aug 2025](https://support.huawei.com/enterprise/en/doc/EDOC1100273864/5eeb2586/downloading-and-installing-the-app)

**C&I**
- Hardware: SmartLogger5000B / SmartMGC5000B, inverter SUN2000-150K-MG0, optimizer MERC-1100/1300W-P, ESS LUNA2000-241 series. Features: Smart IV Diagnosis, module-level supervision up to 60 MW, SmartEMO, peak-demand reduction — [Huawei C&I Smart PVMS (FR)](https://solar.huawei.com/fr/products/ci-smart-pv-management-system/)

**Utility**
- SmartLogger3000B: communication manager, data logger and Ethernet switch (RS485, FE, SFP). Supports up to 200 devices, of which up to 150 inverters. NetEco1000S PVMS: mobile access, proactive yield/alarm reporting, Smart String I-V Diagnosis, up to 25 years of data storage as CSV. Inverters: SUN2000-200KTL-H3/H2, SUN2000-185KTL-INH0, SUN2000-100KTL-INM0 (India page, likely older) — [Huawei India Utility](https://solar.huawei.com/in/utilityscale)
- Smart PV Plant Management System (utility): monitoring at system, sub-array, device and module level. Visualized fault pre-warning. AI tracker-angle optimization (claims +1% yield). Smart I-V Curve Diagnosis (CGC L4 certified). Coefficient-of-variation analysis. Partner drone integration (96% accuracy, +80% O&M efficiency). RESTful API and IEC 104 for third-party systems — [Huawei Smart PV Plant Management System](https://solar.huawei.com/en/products/smart-pv-plant-management-system/)
- FusionSolar 9.0 (utility): 460 kW smart string inverter, sub-array controller, plant-level controller, integrated PVMS. Kilovolt-class AC (>800 V) with about 30% lower cable losses. Peak efficiency >99%. IP66, −25 to 60 °C. Grid-forming functions: short-circuit contribution, virtual inertia, damping, frequency response, black start, on/off-grid transition. "FusionSolar Agent" edge-to-cloud AI layer for state analysis, fault prediction, component-level MPPT and lifecycle management. Announced June 2025 at SNEC Shanghai, rollout from Dec 2025 — [pv magazine, 2 Dec 2025](https://www.pv-magazine.com/2025/12/02/huawei-unveils-fusionsolar-9-0-platform-with-ai-grid-forming-tech/)
- European launch of FusionSolar 9.0 was 29 Apr 2026 in Frankfurt, aimed at utilities, developers and plant operators. Specs: 506KTL string inverter (first grid-forming string inverter), 1,000 V AC, transformer stations of 3/7/11 MVA, reactive power response <10 ms, virtual inertia 0–20 s, Smart Hybrid Cooling (+30% heat dissipation), SSLD v2.0 three-stage DC protection, BoS saving of 0.27–0.55 €ct/W, about €70k commissioning saving per 200 MW (no diesel gensets), >10 GW of projects under construction — [pv Europe, Apr 2026](https://www.pveurope.eu/inverter/huawei-debuts-fusionsolar-90-grid-forming-string-inverters)
- Middle East launch of FusionSolar 9.0 was 16 Jul 2026 at a Dubai summit. Grid-forming validated by simulation (Saudi Arabia) and tests in Germany, with independent assessments by Go2Power and DNV — [Gulf Business, Jul 2026](https://gulfbusiness.com/en/2026/energy/huawei-launches-fusionsolar-9-0-to-strengthen-renewable-energy-grids-in-middle-east/)
- Mexico: Huawei news page headline "Huawei presenta FusionSolar 9.0 en FES México 2026" (only the search snippet seen) — [Huawei Mexico news](https://solar.huawei.com/mx/news/)

### Inferences
- FusionSolar 9.0 seems to have launched region by region: China/SNEC June 2025, global rollout Dec 2025, Europe Apr 2026, MEA Jul 2026, Mexico 2026. Sources disagree on inverter rating: pv magazine (2025) says 460 kW, while 2026 European sources say 506 kW (SUN2000-506KTL). That may be a newer model or a regional variant. pv Europe's "China deployment October 2024" also conflicts with pv magazine's June 2025 announcement. Treat the dates with care.
- The utility management stack (NetEco1000S / Smart PV Plant Management System) is separate from the residential/C&I FusionSolar cloud, which suits sites that need on-prem deployment and SCADA integration (IEC 104).

### Gaps
- No 2025–2026 official page found that says whether NetEco1000S is still sold or has been rebranded into the "Smart PV Plant Management System". The India utility page may be outdated.
- "FusionSolar Utility Smart String Grid-Forming ESS" product names (e.g. LUNA2000-5015/"LUTERRA") are only partly confirmed. Huawei's Intersolar 2026 page names "LUTERRA" as a next-generation grid-forming ESS launched 23 Jun 2026 — [Huawei Intersolar 2026](https://solar.huawei.com/en/events/intersolar2026/). How it integrates with the management portal is not documented.

## 4. User roles and the account/plant creation flow

### Takeaway
There are two main roles: Installer (company) and Owner. On the Smart PV community site an installer first registers a personal account, then a company account with a Company Administrator who manages employee FusionSolar accounts. On site, the installer uses the app's Setup Wizard → "Scan to Create Plant", then "Add Plant" or "Connect to Existing Plant", binding device serial numbers to the account. Owners get a dedicated account with limited functions.

### Cited Findings
- Personal accounts are created on the Smart PV Community site (pick a country, then Register). A company account is then created from the "Registration & Verification" tab. Company Administrators can manage the company and employee accounts, take part in incentives and "manage employee FusionSolar accounts". Employee accounts link to the company after approval — [Huawei FAQ](https://solar.huawei.com/en/faqs)
- Plant creation in the app: "Setup Wizard > Scan to Create Plant > Add Plant or Connect to Existing Plant". A device qualifies only if "the product SN is bound to the FusionSolar account" — [Huawei FAQ](https://solar.huawei.com/en/faqs)
- Changing country deletes community points, event records, learning progress, installer engineer certificates and personal info on the current site — [Huawei FAQ](https://solar.huawei.com/en/faqs)
- Portal roles: Installers have full admin over multiple plants. System owners get a "dedicated account … with limited functions" — [VP Solar, Jan 2025](https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/)
- Owner setup flow (2026 consumer guide): create account → connect Smart Dongle to WLAN → assign the plant by inverter serial number. Roles are "Endkunde" (owner) and "Installer mode" — [solaranlage-tipps.de, Jun 2026](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026)
- Commissioning apps: Huawei's "FusionSolar App and SUN2000 App Device Commissioning Guide" (EDOC1100273864, dated 6 Aug 2025) still treats both apps as commissioning options. Both need Android 8.0+/iOS 13.0+ (iPhone SE not supported). iOS cannot do local commissioning of iSitePower-M, so Android is needed for that. Downloads: Huawei AppGallery, App Store, or a browser download for other Android phones (implying the app is not distributed through Google Play in some regions) — [Huawei Commissioning Guide](https://support.huawei.com/enterprise/en/doc/EDOC1100273864/5eeb2586/downloading-and-installing-the-app)

### Inferences
- The SUN2000 app has not been formally retired. As of Aug 2025 it was still documented next to the FusionSolar app, which has absorbed local commissioning (its "Device Commissioning" entry) for most residential and C&I use.
- Third-party integrations (e.g. EnergyID) pull data from FusionSolar. A "new, more secure" connection method arrived on 16 Dec 2024, and legacy integrations stop syncing on 1 Dec 2026 — [EnergyID help](https://help.energyid.eu/en/apps/migrating-your-fusionsolar-integration-to-the-new-version). This points to a change in Huawei's Northbound/OpenAPI access, but the article gives no technical detail.

### Gaps
- No official 2026 document found that gives the exact role list (e.g. Company Admin, Installer, O&M personnel, Owner, Guest/visitor) in the SmartPVMS portal.
- No confirmation of a formal end-of-life date for the SUN2000 app.

## 5. What changed in 2025–2026

### Takeaway
Main 2025–2026 changes: FusionSolar 9.0 utility platform with grid-forming string inverters and the "FusionSolar Agent" AI (SNEC 2025 → global 2025–2026). "FusionSolar AI Agent" for installer productivity and O&M (Installer Summit, Mar 2026). App version scheme moved to 26.x (26.1.1.013 in Apr 2026 → 26.2.6.001 in late Sep 2026). Dark mode and energy-flow redesign (Nov 2025). Dynamic-tariff integration (OTE, Jan 2026). New hardware at Intersolar 2026: LUTERRA grid-forming ESS, SUN2000-506KTL, 22 kW AC chargers, 800 W optimizers, LUNA S2 residential battery.

### Cited Findings
- App version history (iOS): 25.3.100.013 (11 Nov 2025: energy-flow diagram optimization, dark mode support); 25.3.101.001 (5 Dec 2025); 25.4.100.011 (4 Jan 2026: connected to OTE dynamic electricity market); 25.4.101.007 (9 Feb 2026); 26.1.1.013 (2 Apr 2026: "optimized details for smoother experience"); 26.1.2.008 (22 May); 26.1.3.002 (4 Jun); 26.1.6.001 (29 Jun); 26.2.1.009 (2 Jul); 26.2.1.010 (13 Jul); 26.2.3.001 (4 Aug); 26.2.5.003 (21 Sep); 26.2.6.001 (27 Sep 2026, current, 372.1 MB). Most notes just say "Fixed known issues" — [App Store JP](https://apps.apple.com/jp/app/id1529080383)
- iOS compatibility: iOS 13.0+, Apple-silicon Macs (macOS 11+), visionOS 1.0+. Thai language added in 24.8.100.008 (older, 2024) — [App Store CD](https://apps.apple.com/cd/app/fusionsolar/id1529080383)
- Another listing says the dark mode was for residential plants — [App Store CD](https://apps.apple.com/cd/app/fusionsolar/id1529080383)
- 6th Global Installer Summit (27 Mar 2026, Songshan Lake, Dongguan; 500+ partners from 29 countries) launched the "FusionSolar AI Agent" to raise productivity and cut O&M costs, "Installer Voice Loop" (AI platform for collecting and acting on installer feedback), and "One-Fits-All" residential and C&I solutions — [AAP/Cision, 27 Mar 2026](https://www.aap.com.au/aapreleases/cision20260327ae21040)
- FusionSolar 9.0 "FusionSolar Agent" (edge-to-cloud AI): real-time state analysis, fault prediction, component-level MPPT, digital lifecycle management — [pv magazine, Dec 2025](https://www.pv-magazine.com/2025/12/02/huawei-unveils-fusionsolar-9-0-platform-with-ai-grid-forming-tech/)
- Intersolar Europe 2026 (Munich, June 2026): LUTERRA grid-forming ESS (launched 23 Jun 2026), SUN2000-506KTL (won The smarter E AWARD) — [Huawei Intersolar 2026](https://solar.huawei.com/en/events/intersolar2026/). Press coverage also lists LUNA S2 (residential battery), LUNA 241 (C&I, hybrid air+liquid cooling), 22 kW AC charging, new optimizers for panels up to 800 W, C&I inverters up to 150 kW, and a 5 MWh container ESS. The app/EMMA optimizes using production, consumption, battery state and live energy prices, and controls heat pumps and EV charging — [touchit.sk, 16 Jul 2026](https://touchit.sk/huawei-na-intersolar-2026-fotovoltika-bude-inteligentnejsia-kompaktnejsia-a-bezpecnejsia/889554/) (note: this source calls the inverter "SUN2000-500KTL" with 506 kW output, while Huawei's page says SUN2000-506KTL)
- 3rd Global C&I Visionaries Summit was held in May 2026 (headline only, content not fetched) — [AAP/Cision, 25 May 2026](https://www.aap.com.au/aapreleases/cision20260525ae67179/)
- Third-party API: new secure integration method from 16 Dec 2024. Legacy connections stop on 1 Dec 2026 — [EnergyID help](https://help.energyid.eu/en/apps/migrating-your-fusionsolar-integration-to-the-new-version)

### Inferences
- The app numbering seems to follow YY.Release.Patch.Build. "26.x" marks the 2026 release train, with roughly 2–4 week patch cadence.
- AI features fall into three layers: EMMA (home energy optimization for residential), the FusionSolar AI Agent (installer/O&M productivity, 2026), and the FusionSolar Agent in 9.0 (utility plant intelligence). Huawei's terms overlap, so the report should name each layer explicitly.

### Gaps
- App Store release notes are generic, so specific 2026 UI changes (new home page, AI assistant inside the app) could not be confirmed from primary sources.
- No primary source found on discontinued features in 2025–2026.
- Not verified: a "next generation FusionSolar Residential Smart PV solution" launch (PV Tech event page) and a Nov/Dec 2025 South Africa launch (Engineering News) — [PV Tech](https://www.pv-tech.org/events/huawei-launches-next-generation-fusionsolar-residential-smart-pv-solution-2); [Engineering News, Dec 2025](https://www.engineeringnews.co.za/print-version/huawei-fusionsolar-hosts-innovative-product-launch-and-partner-year-end-gala-2025-12-02). Neither was fetched.
