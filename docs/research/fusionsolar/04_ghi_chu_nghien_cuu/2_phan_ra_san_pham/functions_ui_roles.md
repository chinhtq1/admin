# Huawei FusionSolar SmartPVMS (web portal + FusionSolar app): functions, information architecture and role/permission model

Research date: 2026-10-07. Scope: menus, screens, functions and roles only. Earlier notes in `research_notes/Nền tảng Huawei FusionSolar/` already cover the high-level feature list, editions, the Northbound/OAuth API, the kiosk API endpoint, the September 2025 owner-consent breakage, data retention and the app version history. Those topics are referenced here but not repeated.

**Labels used in this file**
- **[FACT]**: stated by a cited source. The source's date or version is given where it matters.
- **[INFERENCE]**: a reasoned conclusion from several cited facts.
- **[SPECULATION]**: a plausible guess with no direct evidence. Verify it before using it in design.

**Source caveats (read first)**
- support.huawei.com / support.huawei.cn returned HTTP 403 or robots-disallow for almost every 25.x manual page in this session. Only two pages of the SmartPVMS 24.2.0 manual (EDOC1100331328) and one 24.5.0 page (EDOC1100376808) were readable. For 25.1–25.4, only **section titles** were recovered, from search-engine result titles. The page bodies were not readable.
- The richest single source on menu paths is Huawei's **FusionSolar Smart PV Management System 7.0 after-sales training deck** (about 2021–2022, hosted by a distributor). It describes the **older UI**. Its menu labels (Home > KPI View / Dashboard / List View / Map View; Maintenance; Inspection; Task Management; Smart Diagnosis) are probably renamed in 24.x/25.x, where the top-level entry is "Monitoring". Older-UI items are marked **(OLD UI v7.0)**.
- App-side details come mostly from the **FusionSolar App & SUN2000 App User Manual of 15 Dec 2021** (OLD UI, app tabs "Home / O&M / Device / Me") and from 2025–2026 third-party integrator and help-desk pages.
- Scribd copies of the SmartPVMS 24.4.0, 24.5.0 and 25.1.0 manuals exist, but Scribd served a JS challenge and the content could not be read.

---

## 1. Web portal: top-level menu and sub-menus (sitemap)

### Takeaway
For 24.x/25.x the portal is organised around a **Monitoring** area (plant list → plant detail with overview/energy flow, devices, layout, reports, alarms, kiosk sharing, EMMA, SmartEMO), plus **Reports**, **Plants / Plant management** (create plant, plant settings, device management, data repair), **Maintenance / O&M** (alarms, tasks, inspection, Smart I-V diagnosis, upgrades), **Value-added services / Business operation**, and **System** (Company management incl. company authentication and Northbound management; Personal settings). The older v7.0 UI used Home (KPI / Dashboard / List / Map views), Plants, Reports, Maintenance, Inspection, Task Management, Smart Diagnosis and System.

### Cited Findings

**1a. Current-generation (24.x/25.x) manual structure: section titles recovered**
- [FACT] SmartPVMS 24.2.0 User Manual, chapter "Monitoring", has sub-sections: **Plant Overview; Viewing and Managing Devices; Viewing and Managing Plant Layouts; Viewing and Managing Report; Viewing and Managing Alarm; Sharing Plant Running Information; Enabling EMMA; SmartEMO for C&I PV Plants** — [SmartPVMS 24.2.0 User Manual – Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/49fc5dd1/monitoring)
- [FACT] Report entry point in 24.2.0: "Choose **Monitoring > Monitoring** or **Reports > Reports** from the main menu". So reports are reachable both from the plant monitoring view and from a top-level **Reports** menu — [SmartPVMS 24.2.0 – Viewing and Managing Report](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report)
- [FACT] Since 25.1.0 the manual is split into **"FusionSolar SmartPVMS User Manual (Installer)"** (EDOC1100462190 = 25.1.0; EDOC1100488068 = 25.2.0; EDOC1100515204 = 25.3.0; EDOC1100541798 = 25.4.0) and **"FusionSolar SmartPVMS User Manual (Owner)"** (EDOC1100488067 = 25.2.0). This confirms two distinct product surfaces/personas. Section titles seen in search results: "Overview", "Manual Aggregation", "Monitoring", "Viewing and Managing Alarms", "Managing Plants", "Company Authentication", "Setting String Details", "Data Repair", "Managing a Northbound API Account" (Installer manuals); "Battery Control Parameters" (Owner manual, 25.2.0); "Visualizzare un layout fisico" (Italian 25.2.0 installer manual) — [search result titles: 25.1.0 Overview](https://support.huawei.cn/enterprise/en/doc/EDOC1100462190/c39dc276/overview); [25.1.0 Manual Aggregation](https://support.huawei.com/enterprise/en/doc/EDOC1100462190/1a45e7bd/manual-aggregation); [25.1.0 Viewing and Managing Alarms](https://support.huawei.cn/enterprise/en/doc/EDOC1100462190/69134877/viewing-and-managing-alarms); [25.2.0 Managing Plants](https://support.huawei.cn/enterprise/en/doc/EDOC1100488068/16e4e3e0/managing-plants); [25.2.0 Company Authentication](https://support.huawei.cn/enterprise/en/doc/EDOC1100488068/f322e0fa/company-authentication); [25.3.0 Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100515204/61186f0/monitoring); [25.3.0 Setting String Details](https://support.huawei.cn/enterprise/en/doc/EDOC1100515204/2cd10883/setting-string-details); [25.4.0 Data Repair](https://support.huawei.cn/enterprise/en/doc/EDOC1100541798/ea4fbfa/data-repair); [25.4.0 Managing a Northbound API Account](https://support.huawei.cn/enterprise/en/doc/EDOC1100541798/76091675/managing-a-northbound-api-account); [25.2.0 Owner – Battery Control Parameters](https://support.huawei.cn/enterprise/en/doc/EDOC1100488067/118cf11f/battery-control-parameters); [25.2.0 IT – physical layout](https://support.huawei.cn/enterprise/it/doc/EDOC1100489437/c9d0422)
- [FACT] Northbound account path (2025 integrator guide): **System > Company Management > Northbound Management > Add** — [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/) (already in the API notes; listed here for the sitemap)
- [FACT] Device export: top menu **Plants → Device Management → "Export Basic Info"** produces an Excel file of device basic info — [Eniris wiki](https://wiki.eniris.be/wiki/publicinformation/view/Integraties/Huawei/Fusion%20Solar%20%26%20Neteco%20%28Huawei%29)
- [FACT] Owner portal: **Plant management** list, with a key icon in the "operations" column used to grant API permission to the installer (Sep 2025). Owner e-mail verification lives under **System → Personal Settings** — [HA community, Sep 2025](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417); [enerix help desk](https://control.enerix.de/hc/en-us/articles/31389765064338-Huawei-Fusion-Solar)
- [FACT] Kiosk button: Portal > plant > Monitoring > **Kiosk** — [tijsverkoyen README](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- [FACT] EMMA activation is reached via **Monitoring > Monitoring**. It needs a plant invitation code activated through "Business Operation" pages and "Value-Added Services" provisioning — [SmartPVMS 24.5.0 – Enabling EMMA](https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma)

**1b. Huawei marketing sitemap (2020 datasheet, consistent with 2023 FR brochure)**
- [FACT] Menu blocks named in the official SmartPVMS datasheet "01 – (202004)": **Homepage; PV Plants List; Add Plant; Report Management** (Plant Report, Inverter Report, Battery Report); **Device Management** (Device Details, Remote Parameter Setting, Remote Optimizer Search); **Intelligent O&M** (Real-time Status, Alarm Management, Task Management, Smart IV-Curve Diagnose); **KPI Dashboard; Energy Management; Plant Management; Company Management; Demo Site**. Named screens: "Homepage of Single Plant", "Energy Flow", "Plant Layout", "Kiosk Mode" — [Huawei SmartPVMS datasheet 2020](https://solar.huawei.com/-/media/Solar/attachment/pdf/eu/datasheet/SmartPVManagementSystem.pdf); same blocks in French ("Page d'accueil, Liste des centrales PV, Ajouter une centrale, Gestion des rapports, Gestion d'appareils, O&M intelligent, Panneau de commande KPI, Paramètre du système") — [Huawei FR brochure](https://solar.huawei.com/admin/asset/v1/pro/view/9d3805d1d84045518c2b4068131be18d.pdf); also [Photomate download](https://www.photomate.eu/photomate-download/390)

**1c. OLD UI v7.0 menu paths (training deck)**
- [FACT] (OLD UI v7.0) Home: **Home > KPI View** (plant planning, rankings, environmental benefits); **Home > Dashboard** (company- or plant-level big screen, minimum 1920×1080); **Home > List View** (plants, KPIs, alarms; refreshes every 3 min); **Home > Map View** (Google/AutoNavi maps) — [FusionSolar SmartPVMS 7.0 training slides](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] (OLD UI v7.0) **Reports > Plant Report / Inverter Report / Battery Report**; **Plants > Plant Management** (device binding, string capacity, pricing); **Plants > Default Electricity Prices** (TOU tariff); **Plants > Plan Management** (annual yield plan); **Plants > Device > Device Management** (parameter settings, batch operations); **Plants > Device > Device > Real-Time Info**; **Maintenance > Real-Time Status** (plant comparison, alarm center); **Inspection > Task List**; **Task Management > Defect Elimination**; **Smart Diagnosis > I-V Curve**; **System > Company Management** (multi-level organisations) — [same deck](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)

### Inferences
- [INFERENCE] **Draft sitemap for 24.x/25.x** (to draw the IA), merging 1a–1c. Items marked (old) are attested only in v7.0:
  1. **Home / Overview** (company-level): KPI cards, plant status donut, active alarms by severity, yield statistics, environmental benefits; plus Map view and big-screen Dashboard (old).
  2. **Monitoring**: plant list → **Plant detail** with tabs/areas: Overview (KPIs + energy flow), Devices, Layout (physical layout / optimizer map), Reports, Alarms, Kiosk sharing; EMMA panel (residential); SmartEMO (C&I).
  3. **Reports**: Plant / Inverter / PCS / Battery reports; day / month / year / lifetime; export; subscribe.
  4. **Plants (Plant management)**: Add plant, plant list management, plant settings (address, capacity, electricity prices, yield plan), String details, Device management (bind/replace devices, export basic info, remote parameter setting, batch settings), Data repair (25.4.0).
  5. **Maintenance / Intelligent O&M**: Alarm management (active/historical), Task management (defect-elimination tickets, inspection tasks), Smart I-V curve diagnosis, upgrade management (batch firmware upgrade), logs.
  6. **Value-added / Business operation**: VIP/value-added services (EMMA, SmartEMO, I-V), invitation codes.
  7. **System**: Company management (company info, Company Authentication, sub-companies, users/roles, Northbound Management), Personal settings (profile, e-mail verification, notifications).
- [INFERENCE] The split into Installer and Owner manuals from 25.1.0 suggests the Owner portal is a reduced sitemap: Monitoring (own plants), Plant management (incl. authorization key icon), Reports, battery/EMMA control, System > Personal settings.
- [INFERENCE] "Manual Aggregation" (25.1.0) is probably a document-assembly page, not a UI menu. Do not put it in the sitemap.

### Gaps
- No 2025–2026 primary source with the exact top-level menu labels as shown in the live 25.x portal. 25.x page bodies were all 403 / robots-blocked. Labels for "Maintenance" vs "O&M" vs "Intelligent O&M" in 25.x are unconfirmed.
- No source confirms an "Upgrade Management" / "Log Management" menu name in the portal. Batch firmware upgrade (up to 50,000 devices) is confirmed as a function in the earlier notes, but its menu location is not.
- Exact plant-detail tab names in 25.x (e.g., "Overview / Energy Flow / Devices / Layout / Alarms / Reports / Plant Settings") are unverified.

---

## 2. Per-screen purpose, components and actions

### Takeaway
Screens follow a consistent pattern. Company home has KPI cards, a status distribution, an alarm summary and a yield chart. The plant list is a table with KPIs and alarms, plus a map toggle. Plant overview has an energy-flow diagram, a yield/revenue chart and environmental benefits. Device screens show real-time info, history and parameters. Reports are time-dimension tables with export and e-mail subscription. Alarm screens hold active and historical lists with severities and a "New Ticket" action. Tasks cover inspection and defect-elimination workflows.

### Cited Findings
- [FACT] Company home components: **Plant's KPI** ("energy yields and revenue for all plants, current power, daily yields and revenue, nominal inverter power, nominal ESS capacity"); **Plant Status** (real-time status of all plants); **Active Alarms** (all plants, Critical / Severe / Minor / Warning); **Yield Statistics** (day / month / year / lifetime); **Plant Overview** (status of each plant and its devices); **Environmental Benefits** (CO2 reduction, coal saved, equivalent trees) — [VP Solar, Jan 2025](https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/)
- [FACT] (OLD UI v7.0) List View refreshes every **3 minutes** (changed from 1 min in v7.0). Dashboard requires ≥1920×1080. Map View supports Google / AutoNavi maps — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Reports (24.2.0): **Plant report** (yield, consumption, revenue by time or by plant); **Inverter report** (yield and running status by day/month/year); **PCS report** (energy yield, peak AC power, supply from grid); **Battery report** (charge/discharge by day/month/year). The chapter intro says users can "subscribe to and export reports". There is also a currency selection — [SmartPVMS 24.2.0 – Report](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report)
- [FACT] (OLD UI v7.0) Plant report adds a **lifetime** dimension and e-mail subscription. "Data of the previous hour is summarized at the fifth minute of the next hour" — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Monitoring (24.2.0): real-time device monitoring with exception handling; current and historical alarms with "real-time tracing"; kiosk view to share plant data without logging in — [SmartPVMS 24.2.0 – Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/49fc5dd1/monitoring)
- [FACT] (OLD UI v7.0) Alarm → ticket: in the plant alarm center, "Click the **New Ticket** button" to create a defect ticket with description, assignee (owner/handler) and handling suggestions. Alarms carry troubleshooting suggestions — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] (OLD UI v7.0) Inspection: "Add an inspection task" with preset inspection items, plant selection, description and task name. There is a flowchart/status view and inspection reports. Defect elimination: handler assignment per workflow node, device selection, defect/solution record, completion-progress dashboard — [same](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] (OLD UI v7.0) Smart I-V Curve: "Configure Strings" dialog. Prerequisites: irradiance ≥400 W/m², clean strings, correct string configuration. A charged value-added feature — [same](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf). "Setting String Details" remains a 25.3.0 manual section — [25.3.0 title](https://support.huawei.cn/enterprise/en/doc/EDOC1100515204/2cd10883/setting-string-details)
- [FACT] Device management: "Device Details, Remote Parameter Setting, Remote Optimizer Search" — [2020 datasheet](https://solar.huawei.com/-/media/Solar/attachment/pdf/eu/datasheet/SmartPVManagementSystem.pdf); "Export Basic Info" to Excel — [Eniris wiki](https://wiki.eniris.be/wiki/publicinformation/view/Integraties/Huawei/Fusion%20Solar%20%26%20Neteco%20%28Huawei%29)
- [FACT] EMMA panel (24.5.0): revenue metrics, with/without-EMMA comparison, 24 h generation/consumption forecast against history, battery charge/discharge cycles, price-aware savings analysis. **Once disabled, EMMA cannot be re-enabled in the same calendar month** — [SmartPVMS 24.5.0 – Enabling EMMA](https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma)
- [FACT] SmartEMO (C&I) and other "VIP functions" are "advanced FusionSolar functions" that are currently free but may be charged later — [SmartPVMS 24.2.0 – Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/49fc5dd1/monitoring)

### Inferences
- [INFERENCE] Component kit a product team would need: KPI stat cards; donut/status distribution; severity-coloured alarm counters; time-dimension bar/line charts (day/month/year/lifetime toggle); animated energy-flow node diagram (PV, inverter, battery, load, meter, grid; EV charger and smart loads on EMMA plants); map with plant pins; paginated tables with filters, search and export; module-level physical-layout canvas; I-V curve chart; workflow/ticket forms.
- [INFERENCE] Plant-level report export goes to a spreadsheet file (the device "Export Basic Info" is Excel). That export uses the same format is likely but unconfirmed.

### Gaps
- Export file formats for reports (XLSX vs CSV vs PDF) are not confirmed for 24.x/25.x.
- Exact alarm actions in 25.x (acknowledge / clear / mask / export) could not be read. The 25.1.0 "Viewing and Managing Alarms" page was robots-blocked.
- No source describes the 25.x "Data Repair" screen. [SPECULATION] It probably re-imports or fills gaps in historical data after communication loss.

---

## 3. Mobile app: tabs, installer flows, local commissioning

### Takeaway
The installer-oriented app (2021 manual) has permission-gated bottom tabs **Home / O&M / Device / Me**. Me holds messages, the local commissioning tool, plant management, owner management, company info and personal settings. On-site work runs through **Setup Wizard** (scan-to-create plant) and **Device Commissioning** (local WLAN/QR connection to the inverter or dongle, used to set grid-tied control, battery and TOU parameters). Owners get a reduced app (plant home, device, account and plant info settings). Services offers a Document Center, a chatbot and feedback. I found no 2025–2026 source that lists the current bottom-tab labels.

### Cited Findings
- [FACT] (OLD UI 2021) Bottom-level permission categories: **"Home, O&M, Device, and Me"**. "Users without assigned permissions cannot perform corresponding operations." Home: **Plant screen** (real-time info, plant views) and **Statistics screen** ("energy yield, revenue statistics, PV plant ranking on the current day, and social contribution"). Home quick actions: create plant, add user, map view of plant distribution, plant filter. **O&M**: plant status, device alarms, diagnostic warnings, online diagnostics, I-V curves, mobile O&M. **Device**: device info, parameters, replacement. **Me**: user information, messages, local commissioning tool, PV plant management, owner management, company information, personal settings — [FusionSolar App & SUN2000 App User Manual, 15 Dec 2021](https://www.alternergy.co.uk/media/mageplaza/product_attachments/attachment_file/h/u/huawei_fusionsolar_app_and_sun2000_app_user_manual_-_15_12_2021.pdf)
- [FACT] (OLD UI 2021) Energy-flow diagram nodes: PV, Inverter, Battery, Power Load, Meter, Grid, Output, On-grid Power. Alarm management: "On the home screen, tap Alarm management. You can query active and historical alarms." Local login: initial password "00000a" for all local user roles, which must be changed at first login. Local device user levels: "Common User", "Advanced User", "Special User" — [same manual](https://www.alternergy.co.uk/media/mageplaza/product_attachments/attachment_file/h/u/huawei_fusionsolar_app_and_sun2000_app_user_manual_-_15_12_2021.pdf)
- [FACT] Installer account registration in-app, plus "New User" to create more installer accounts. Commissioning can be done in three ways: FusionSolar app with internet, FusionSolar app without internet, or the standalone SUN2000 app — [same](https://www.alternergy.co.uk/media/mageplaza/product_attachments/attachment_file/h/u/huawei_fusionsolar_app_and_sun2000_app_user_manual_-_15_12_2021.pdf)
- [FACT] Quick Guide Issue 10 (2020-12-25) TOC: download app; log in and start **Setup Wizard**; Quick Settings; register installer account; physical layout design on the **WebUI** or with **Device Commissioning**; check device status; **Setting Export Limitation Parameters**; **Setting Voltage Rise Suppression Q-U Curve**. Installer functions: "power station homepage, power station view, equipment management, report management, smart operation and maintenance, system setting". Owner functions: "power station homepage, equipment management, user account settings and power station information settings" — [FusionSolar App Quick Guide Issue 10 (solartraders PDF)](https://solartraders.com/uploads/production/data_sheet/file/20856/manual.pdf?locale=en)
- [FACT] Current app user manual (EDOC1100096889, updated 31 Jul 2025) has a **Services** area: Most Visited; **Device Commissioning** entry ("deployment and commissioning, and local O&M"); **Document Center** (video tutorials, after-sales quick guides); **Help and Feedback**; Customer Service **Chatbot**; Contact Us — [FusionSolar App User Manual – Services](https://support.huawei.com/enterprise/en/doc/EDOC1100096889/b7403273/services)
- [FACT] Parameters over the app: FusionSolar app → **Device Commissioning** → grid-tied control modes "Grid connection with zero power", "Grid connection with limited power (kW)", "Grid connection with limited power (%)", plus fail-safe parameters (communication disconnection detection default 3 s, "Active power output limit for fail-safe") — [Connection User Manual (Inverters + SDongle)](https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app)
- [FACT] Owner-reachable TOU path (2025 community wiki): **Devices → Connected devices → Dongle → ⋮ (top right) → Parameter settings** — [wlcrs/huawei_solar wiki – TOU control](https://github.com/wlcrs/huawei_solar/wiki/Time-of-Use-control)
- [FACT] Owner creation is done only in the smartphone app ("web portal unavailable for this"): **Invite user** → company, role **Owner**, system (plant), e-mail — [enerix help desk](https://control.enerix.de/hc/en-us/articles/31389765064338-Huawei-Fusion-Solar)
- [FACT] App flow "Setup Wizard > Scan to Create Plant > Add Plant / Connect to Existing Plant" is already documented in the earlier notes — [Huawei FAQ](https://solar.huawei.com/en/faqs)
- [FACT] 2026 consumer guide: owner app shows real-time W, feed-in, consumption, yields with CO2, self-consumption ratio and LUNA2000 SOC. It sends **push notifications** for faults, grid outages and inverter offline. The setup flow is: install and create account → "Geräte-Inbetriebnahme" (connect inverter/dongle) → assign plant — [solaranlage-tipps.de, Jun 2026](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026)

### Inferences
- [INFERENCE] App IA for an equivalent product: **(Installer)** Home (portfolio KPIs, plant list/map, + create plant / add user) · O&M (alarms, tasks, I-V, diagnostics) · Devices · Services (Device Commissioning, docs, chatbot) · Me (company, owners, messages, settings). **(Owner)** Home/plant (energy flow, statistics) · Devices (incl. battery, EV charger, EMMA smart loads) · Alarms/messages · Me (account security → authorization management, plant info).
- [INFERENCE] "Device Commissioning" is a separate offline-capable sub-app inside FusionSolar. It connects over the inverter/dongle WLAN hotspot (QR or manual SSID), uses its own local user levels (Common/Advanced/Special, from the older SUN2000 model) and works without cloud login.
- [SPECULATION] The 2025–2026 owner app probably uses a different tab set (e.g., Home / Devices / Smart / Me) since the energy-flow redesign in 25.3.100. No evidence found.

### Gaps
- No 2025–2026 source (manual body, screenshots text or app-store screenshot captions) confirms the current bottom-tab labels for installer or owner. The Apple US listing returned 404. Google Play is not used in many regions.
- Setup Wizard step-by-step screens in 25.x/26.x (e.g., network config, optimizer search, layout) were not read.

---

## 4. Roles, permissions, hierarchy, authorization and sharing

### Takeaway
The account model is **company (installer) tree → users with roles → plants**. There is a Company Administrator, installer/engineer roles, Owner accounts (limited, created by invitation) and a demo/guest site. v7.0 removed custom-role creation, keeping only the default roles and existing custom roles. Companies can be multi-level (sub-companies with inherited permissions). Since **Sep 2025** owners must explicitly authorize installer/API data access per plant (key icon in Plant management, or the app's "Authorization Management" with two switches). Third-party apps use OAuth with owner consent. Public read-only sharing goes through the **kiosk** link generated from the plant overview.

### Cited Findings
- [FACT] (OLD UI v7.0) Three primary roles: **Administrator/Installer** (company management, device parameters, all reports, inspection/defect tasks, Smart I-V); **Owner** (plant overview, kiosk sharing, basic plant changes such as electricity price and address, read-only device data); **Guest** (demo site access, cannot create plants). "Defines multiple roles for proper permission assignment to user accounts". Multi-level company hierarchy with inherited permissions. **Custom role permissions deprecated in v7.0**: only default roles and already-existing custom roles are kept. Company branding and e-mail customization were removed in favour of a unified system mailbox — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Company Administrator (community account) manages the company and employee accounts and "manage[s] employee FusionSolar accounts". Employees join after approval — [Huawei FAQ](https://solar.huawei.com/en/faqs). In the portal the matching step is "Company Authentication" (25.2.0 section) — [25.2.0 title](https://support.huawei.cn/enterprise/en/doc/EDOC1100488068/f322e0fa/company-authentication)
- [FACT] Owner vs installer feature sets (Quick Guide Issue 10, 2020): installer gets homepage, plant view, equipment, reports, smart O&M, system settings. Owner gets homepage, equipment, user account settings, plant info settings — [Quick Guide](https://solartraders.com/uploads/production/data_sheet/file/20856/manual.pdf?locale=en)
- [FACT] Owners get "a dedicated account … with limited functions" — [VP Solar, Jan 2025](https://www.vpsolar.com/en/huawei-fusionsolar-softwares-app-and-smartpvms-portal/)
- [FACT] Invite flow: app → Invite user → Company, Role = Owner, System, E-mail. Installer or company-admin accounts cannot authorize third-party energy services; that requires an Owner account with a verified e-mail ("System → Personal Settings") — [enerix help desk](https://control.enerix.de/hc/en-us/articles/31389765064338-Huawei-Fusion-Solar); [EWR help desk](https://helpdesk.one.ewr.de/hc/en-us/articles/31389751586450-Huawei-Fusion-Solar)
- [FACT] Owner consent scopes shown on the OAuth consent screen: "Access to real-time monitoring, reports and alarm data" and "Remote control of systems, including battery charge/discharge configuration". Troubleshooting note: in authorization management, "both switches must be on" — [enerix](https://control.enerix.de/hc/en-us/articles/31389765064338-Huawei-Fusion-Solar). The owner revokes access at **Me > Settings > Account Security > Authorization Management** — [Huawei EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)
- [FACT] Sep 2025 owner→installer authorization: owner logs into the web app → **Plant management** → key icon (in a circle) in the "operations" column → grant API permission to installer. Breakage reported 4 Sep 2025, workaround confirmed 20 Sep 2025 — [HA community](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417)
- [FACT] EMMA requires "owner authorization for management functions" — [SmartPVMS 24.5.0 – Enabling EMMA](https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma)
- [FACT] Northbound account: created by the company admin, bound to an "associated user", scoped to all current and future plants or to selected plants, with an expiry date — [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/)
- [FACT] Kiosk (OLD UI v7.0): log in as owner → Home > List View → plant → **Overview** tab → **Kiosk** produces a public link that shows real-time energy flow, yield, revenue and environmental benefits — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf). In 24.2.0 the "Sharing Plant Running Information" section is owner-level — [24.2.0 Monitoring](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/49fc5dd1/monitoring). The URL is valid 1 year with 10–30 min refresh (see earlier notes).
- [FACT] Integrator Eniris offers a "guest user" connection method in which the plant administrator adds a user with chosen access level. The guide does not give exact menu or role names — [Eniris wiki](https://wiki.eniris.be/wiki/publicinformation/view/Integraties/Huawei/Fusion%20Solar%20%26%20Neteco%20%28Huawei%29)
- [FACT] App permissions are category-gated (Home / O&M / Device / Me); missing permission means no access — [2021 app manual](https://www.alternergy.co.uk/media/mageplaza/product_attachments/attachment_file/h/u/huawei_fusionsolar_app_and_sun2000_app_user_manual_-_15_12_2021.pdf)

### Inferences
- [INFERENCE] Permission model to replicate: RBAC with **menu/function permission sets per role** (role → set of menu nodes) × **data scope by organisation subtree and plant assignment**, plus a separate **owner consent layer** (per-plant, per-grantee toggles: data read, remote control) that overrides installer-side access since Sep 2025.
- [INFERENCE] Default role set for 24.x/25.x is most likely: Company Administrator (system admin of the installer company), Installer/Engineer (plant creation and commissioning), O&M personnel (alarms/tasks), Owner, plus visitor/guest (read-only). The O&M role is inferred from the v7.0 task-handler workflow. I found no direct 25.x citation for an "O&M personnel" role name.
- [INFERENCE] The multi-level dealer hierarchy is implemented as nested companies under "System > Company Management". Inherited permissions (v7.0) mean a parent company sees its sub-companies' plants.

### Gaps
- No 24.x/25.x role list or permission matrix was readable. Role names "O&M personnel", "Visitor", "Guest" in the current portal are unconfirmed.
- Whether custom roles can be created again in 24.x/25.x is unknown. v7.0 deprecated them.
- Whether owners can invite family members or share with other owner accounts (beyond the kiosk and the EV-charger "account-based sharing" in the earlier notes) is unconfirmed.

---

## 5. Notification channels, alarm subscription, report scheduling

### Takeaway
Confirmed channels are **app push** (faults, grid outage, inverter offline) and **e-mail** (alarm push and report subscription, sent from a unified Huawei system mailbox since v7.0). SMS/phone-number login is attested only for China. Report subscription (scheduled e-mail of plant reports) exists. Configuration details are unconfirmed.

### Cited Findings
- [FACT] "Real-time alarm push" and "Report subscription" are listed as system capabilities — [2020 datasheet](https://solar.huawei.com/-/media/Solar/attachment/pdf/eu/datasheet/SmartPVManagementSystem.pdf); "Instant alarm notifications and subscriptions" — [FR brochure](https://solar.huawei.com/admin/asset/v1/pro/view/9d3805d1d84045518c2b4068131be18d.pdf)
- [FACT] (OLD UI v7.0) "Subscription-based email push for alarms and reports". Plant report supports e-mail subscription. Company-specific e-mail customization removed in favour of a unified system mailbox. Mobile-number login added for China, e-mail elsewhere — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Reports can be subscribed and exported (24.2.0) — [24.2.0 Report](https://support.huawei.com/enterprise/en/doc/EDOC1100331328/90b9638d/viewing-and-managing-report)
- [FACT] App push for faults, grid outages and inverter offline (2026) — [solaranlage-tipps.de](https://www.solaranlage-tipps.de/blog/huawei-fusionsolar-app-anleitung-2026)
- [FACT] App "Me" includes **Messages** (2021) — [2021 app manual](https://www.alternergy.co.uk/media/mageplaza/product_attachments/attachment_file/h/u/huawei_fusionsolar_app_and_sun2000_app_user_manual_-_15_12_2021.pdf)

### Inferences
- [INFERENCE] Alarm subscription is likely set per user (severity filter and plant scope) under Personal settings or the alarm module, because subscriptions are described as user-based e-mail pushes.
- [SPECULATION] SMS alarm notification outside China is probably not offered. No source found.

### Gaps
- Exact screens and fields for alarm subscription (severity, plants, recipients, quiet hours) and report-subscription frequency (daily/weekly/monthly) are not documented in the readable sources.
- No webhook channel (consistent with the earlier API notes).

---

## 6. Owner-side energy functions

### Takeaway
Owners see a real-time energy-flow view, which Huawei markets as updating every second on EMMA plants. They can control battery working modes, the EV charger (SCharger) and smart loads through EMMA (priorities, Scheduled Green Electricity Usage). Dynamic tariffs are integrated (Nord Pool, ESIOS, EPEX Spot, TGE, OTE). EMMA analytics give forecasts, revenue and with/without-EMMA comparison. Battery mode names differ between the inverter-managed and EMMA-managed paths.

### Cited Findings
- [FACT] Battery working modes as exposed by a 2026 Homey integration that reads the device registers. **Inverter-managed LUNA2000**: "Adaptive", "Fixed Charge/Discharge", "Maximise Self-Consumption", "Time of Use (LG/LUNA2000)", "Fully Fed to Grid", "Third-party Scheduling". **EMMA-managed**: "Maximise Self-Consumption", "Fully Fed to Grid", "Time of Use", "Third-party Scheduling". Controls: force charge/discharge (Stop / Force Charge / Force Discharge); "Excess PV energy use in TOU: Feed to Grid · Charge Battery"; max grid charging power (kW) — [Homey community, FusionSolar Manager](https://community.homey.app/t/153353). Note: the source says "7 modes" but lists six.
- [FACT] The Owner manual 25.2.0 has a "Battery Control Parameters" section. Its content could not be read — [title](https://support.huawei.cn/enterprise/en/doc/EDOC1100488067/118cf11f/battery-control-parameters)
- [FACT] TOU schedule is set as start–end / weekdays / charge(+) or discharge(−). In the app: Devices → Connected devices → Dongle → ⋮ → Parameter settings — [wlcrs wiki](https://github.com/wlcrs/huawei_solar/wiki/Time-of-Use-control)
- [FACT] Owner smart-home page: "Energy Flow at a Glance" with "real-time updates every second"; "24/7 Intelligent Scheduling"; dynamic pricing support for "Nord Pool, ESIOS, EPEX Spot, and TGE"; "Dynamic Multi-level Power Priority"; control of EVs, heat pumps, chargers and appliances; essential-load protection during outages; per-module performance and shade detection — [Huawei IE Smart Home Energy Management](https://solar.huawei.com/ie/products/smart-pv-management-system). OTE (CZ) dynamic market was added in app 25.4.100.011 (earlier notes).
- [FACT] EMMA analytics: 24 h forecast, revenue, with/without comparison, battery cycles; owner authorization required; cannot re-enable in the same month — [24.5.0 Enabling EMMA](https://support.huawei.com/enterprise/en/doc/EDOC1100376808/a3411c60/enabling-emma)
- [FACT] Owner portal (OLD UI v7.0) can change electricity price and plant address. TOU tariffs are set under Plants > Default Electricity Prices — [7.0 training](https://solisdepot.com/wp-content/uploads/2023/03/FusionSolar-Smart-PV-Management-System-7.0-After-sales-Technical-Training-Slides.pptx.pdf)
- [FACT] Grid export limitation (zero export / kW / %) is set by the installer via Device Commissioning — [Connection User Manual](https://support.huawei.com/enterprise/en/doc/EDOC1100173984/6d72858a/setting-parameters-over-the-app)
- (Already in earlier notes, not repeated: SCharger app control (schedule, PV-preferred, sharing, RFID/Bluetooth), Scheduled Green Electricity Usage, smart sockets/relays.)

### Inferences
- [INFERENCE] Owner IA should include: Energy flow (home), Statistics (production / consumption / self-consumption, day–lifetime), Battery (mode selector + TOU editor + backup SOC), EV charger (start/stop, schedule, PV-surplus mode), Smart loads (priority list, schedules), Tariff (fixed / TOU / dynamic market), EMMA insights (forecast, savings), Authorization management (installer / third-party switches), Kiosk share.
- [INFERENCE] There is a split between installer-level parameters (grid code, export limit, Q-U curve via Device Commissioning) and owner-level parameters (battery mode, TOU, charger, loads). An equivalent product needs per-parameter permission flags, not just per-screen ones.

### Gaps
- Exact owner-app screen names and layout for battery mode selection in 26.x, and which modes are owner-settable vs installer-only, are unconfirmed.
- "Consumption analysis" as a named owner screen is unconfirmed beyond the self-consumption ratio and the consumption fields in the plant report.
