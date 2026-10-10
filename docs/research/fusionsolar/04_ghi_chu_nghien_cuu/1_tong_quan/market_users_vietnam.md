# Huawei FusionSolar: commercial access, market position, competitors, user feedback and Vietnam (as of Oct 2026)

Research date: 2026-10-07. All dates in brackets are publication dates of the source. About 30 tool calls were made. Several sub-questions had to be left as gaps, listed under each section.

## 1. Registration and access: owner vs. installer, cost, data retention

### Takeaway
FusionSolar uses an installer-led account model. A company (installer) account is registered on Huawei's Smart PV community/FusionSolar side. The installer commissions devices and creates plants, then invites the owner ("Invite user" with the Owner role). Basic monitoring through the app and web portal is free. I found no paid subscription tiers for the standard cloud. Huawei's EU Data Act disclosure says high-resolution device history is kept for only 15 months. Daily and monthly reports are kept for 5 years and yearly reports for 25 years.

### Cited Findings
- Huawei separates personal accounts from company accounts. A company administrator account can "manage the company and employee accounts associated with the company… and manage employee FusionSolar accounts". Company accounts that are certified as a "Certified Installer" can join the Rewards Mall, where points are earned by entering device SNs. — [Huawei Smart PV FAQ](https://solar.huawei.com/en/faqs)
- Owner accounts are created from the installer side. In the smartphone app, the installer selects "Invite user" and enters company, role (Owner), system and email. Installer or company-admin accounts cannot connect a third-party energy service directly. A dedicated Owner account with a verified email is required. — [EWR ONE helpdesk: Huawei Fusion Solar](https://helpdesk.one.ewr.de/hc/en-us/articles/31389751586450-Huawei-Fusion-Solar)
- Third-party access works through OAuth. The third party registers as an OAuth client, signs an "Agreement on Use of Huawei APIs" and needs explicit user authorization. The user can revoke it under "Me > Settings > Account Security > Authorization Management". — [Huawei Digital Power, EU Data Act pre-contractual information](https://digitalpower.huawei.com/en/eu-data-act)
- Retention: historical device data 15 months; daily/monthly reports 5 years; yearly reports 25 years; charger alarms 6 months; login and troubleshooting logs deleted within 6 months. Dynamic data is collected every 5 minutes (about 1–5 MB per day). EU data is "stored in the Open Telekom Cloud". — [Huawei Digital Power EU Data Act page](https://digitalpower.huawei.com/en/eu-data-act)
- Cost: a German distributor states "Die Überwachung läuft kostenlos über die Huawei-FusionSolar-App und das Webportal" (monitoring is free through the app and web portal) and says no separate paid software is needed for normal operation. — [basic-solar.de, Smart Dongle-WLAN-FE](https://basic-solar.de/shop/wechselrichter/zubehoer/huawei-smart-dongle-wlan-fe)
- Northbound API: a company administrator creates the API account in the FusionSolar portal under "System > Company Management > Northbound Management > Add". The API username must differ from the FusionSolar login. Query quotas are counted per system/user and are "subject to strict limitations". Solytic recommends a 24 h transmission interval or a separate account per system. — [Solytic: Set up API access – Huawei FusionSolar](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/)

### Inferences
- The model is free, hardware-bundled cloud monitoring. Revenue comes from inverters, dongles, SmartLoggers and batteries, not from subscriptions. The Rewards Mall points program is a loyalty program for installers, not a paid tier.
- The 15-month limit on fine-grained history matters for O&M and analytics use cases such as CPO-style operations tooling. Anyone who needs long 5-minute history must export it continuously via the Northbound API or local Modbus.
- The installer-centric hierarchy (company → plants → invited owners) gives installers strong control. Owners who change installer or want third-party access depend on the installer or Huawei support.

### Gaps
- I could not confirm the exact owner self-registration flow (scanning the dongle/inverter SN QR code in the app) from an official source in this session. Installer manuals ([Alternergy FusionSolar App Quick Guide PDF](https://www.alternergy.co.uk/media/mageplaza/product_attachments/attachment_file/h/u/huawei_fusionsolar_app_quick_guide_-_03_02_2021.pdf)) describe it, but I did not read them in full.
- I found no public evidence of paid tiers for C&I/utility, such as the SmartPVMS/NetEco on-premise licences or "advanced O&M" (e.g., AI I-V curve diagnosis licences), and no published prices. Utility plants commonly use SmartLogger plus SmartPVMS/NetEco, but I could not verify licensing costs here.
- I found no published numeric Northbound API rate limit.
- The 15-month retention figure is from the EU disclosure. Retention on the Asia-Pacific/Vietnam cloud region (e.g., intl.fusionsolar.huawei.com) may differ and was not confirmed.

## 2. Market position: inverter rankings and FusionSolar scale

### Takeaway
Huawei is the world's No. 1 PV inverter supplier by shipments. In 2024 it shipped 176 GWac of a 589 GWac market (about 30%), according to Wood Mackenzie. It was also ranked No. 1, narrowly ahead of Sungrow, in Wood Mackenzie's H1 2025 multi-criteria ranking. I found no current published figure for the number of plants, GW or users managed on FusionSolar.

### Cited Findings
- Global PV inverter shipments were 589 GWac in 2024 (+10% YoY). Huawei shipped 176 GWac and was No. 1 for the 10th consecutive year. Sungrow shipped 148 GWac and was No. 2. Together they hold 55% share. Solis was 3rd and Growatt 4th. Nine of the top 10 are Chinese, and no vendor beyond the top two exceeded 5% share. Asia Pacific was 69% of shipments (China 330 GWac). Europe declined by double digits. — [Wood Mackenzie press release, 10 Jul 2025](https://www.woodmac.com/press-releases/global-pv-inverter-shipments-grew-by-10-in-2024-to-589-gwac/)
- Wood Mackenzie's H1 2025 global solar inverter ranking scored 23 manufacturers on 8 criteria, including ESG, after-sales, R&D and supply chain. It is a ranking, not a shipment table. Huawei scored 93.9 and Sungrow 93.7. The rest of the top 10: SMA, Fronius, Solis, GoodWe, TMEIC/SolarEdge (tied 7th), Solplanet, Enphase. The top ten hold 71% of the market. — [pv magazine USA, 5 Jan 2026](https://pv-magazine-usa.com/2026/01/05/huawei-sungrow-lead-wood-mackenzies-inverter-market-ranking/)
- Wood Mackenzie also forecast a two-year decline in global inverter demand. — [pv magazine USA, 16 Dec 2025 (headline only; not fetched)](https://pv-magazine-usa.com/?p=19433)
- An older figure: the FusionSolar Smart PV Solution had "102 GW deployed globally through H1 2019". — [pv magazine Australia, Nov 2019](https://www.pv-magazine-australia.com/?p=11497)
- Huawei's "Top 10 FusionSolar trends 2025" release (Jan 2025) gives no platform-scale numbers such as plants, users or GW. — [Huawei Brazil news](https://solar.huawei.com/br/news/2025/10-tendencias-fusionsolar/)

### Inferences
- Huawei holds about 30% of the global inverter market, and connected plants default to FusionSolar. That makes FusionSolar very likely one of the largest PV monitoring clouds by installed capacity. This is an inference: Huawei does not publish an official current figure.

### Gaps
- I did not find S&P Global Commodity Insights' 2024/2025 inverter rankings in this session.
- Wood Mackenzie's full-year 2025 shipment ranking (expected around mid-2026) did not appear in my searches. As of Oct 2026 it may exist but is unverified.
- I found no official current number of FusionSolar plants, users or GW.

## 3. Comparison with competitors' monitoring platforms

### Takeaway
All the major inverter makers bundle free owner/installer monitoring. They differ mainly in API openness. Enphase publishes a self-serve developer API with paid tiers. SolarEdge offers a simple per-site API key with a low daily quota. Sungrow iSolarCloud has a developer-portal OpenAPI. FusionSolar's Northbound API is installer/company-admin gated and tightly rate-limited, and Huawei has restricted local Modbus access over time. Local integration is a recurring pain point for FusionSolar.

### Cited Findings
- Enphase Enlighten Systems API plans: Watt (free, 10 hits/min, 10,000/month, attribution required); Kilowatt ($25/month, 50/min, 25,000/month); Megawatt ($250/month, 100/min, 300,000/month); Gigawatt ($1,500/month, 300/min, 1.5M/month, uptime guarantee). Overage costs $0.001–0.002 per call. — [Enphase developer plans](https://developer.enphase.com/plans)
- FusionSolar Northbound API: company-admin created, strict per-user query quotas, 24 h refresh recommended by Solytic. — [Solytic](https://solytic.com/knowledge/set-up-api-access-huawei-fusionsolar-api/). Commercial monitoring platforms such as meteocontrol VCOM import FusionSolar through this API. — [meteocontrol VCOM import – Huawei FusionSolar API](https://zammad.meteocontrol.de/help/en-us/6-datalogger-import-configuration/179-vcom-import-huawei-fusionsolar-api)
- Sungrow iSolarCloud exposes an "Open API" that third-party energy management platforms (e.g., Eniris) and VCOM integrate with. — [meteocontrol VCOM import – Sungrow iSolarCloud API](https://zammad.meteocontrol.de/help/en-us/6-datalogger-import-configuration/152-vcom-import-sungrow-isolarcloud-api); [Eniris docs (search listing)](https://docs.eniris.be/nl/Controller/Devices/Cloud/ISolarCloud)
- Solis markets SolisCloud as its next-generation monitoring platform, with USP and country brochures from 2022–2024. — [Segen SolisCloud USP PDF](https://portal.segen.co.uk/reseller/docs/SolisCloud%20Monitoring%20Platform%20USP.pdf); [Canal Solar](https://canalsolar.com.br/en/soliscloud-nova-geracao-de-monitoramento-dos-inversores-solis)
- On local access, the Huawei Smart Dongle "serves only a very small number of Modbus connections". A Home Assistant Modbus-TCP session can "starve the cloud uplink" so FusionSolar stops receiving data. The community workaround is a Modbus proxy (ESP32 or Docker). — [Home Assistant community thread](https://community.home-assistant.io/t/huawei-solar-integration-modbus-via-smart-dongle-blocks-fusion-solar-cloud-data/1014084); similar report: [openHAB community, SDongle-A05](https://community.openhab.org/t/i-can-read-modbus-data-via-tcp-with-sdongle-a05-but-inverter-no-longer-sends-data-to-fusionsolar-server/153148)
- An App Store installer review says FusionSolar offers better remote configuration than competitors. — [Apple App Store (JP) FusionSolar listing](https://apps.apple.com/jp/app/id1529080383)

### Inferences
- FusionSolar's UX strengths are deep remote commissioning and configuration and an integrated PV, battery and charger ecosystem. Its weaknesses for integrators are API gating and quotas plus local-access contention. SolarEdge and Enphase are more developer-friendly for per-site owner access. Enphase is the only one with a clearly published commercial API price list.

### Gaps
- I did not verify specifics for SMA Sunny Portal/ennexOS (SMA moved to ennexOS/Sunny Portal powered by ennexOS, with an SMA developer API), SolarEdge ONE, Growatt ShinePhone/OSS or GoodWe SEMS in this session. Their feature and API details are not sourced here. SolarEdge's commonly cited limit of 300 requests/day per site appeared only in search titles and was not verified.
- I found no independent side-by-side UX benchmark of these vendor platforms. The pv magazine "PV monitoring software comparison 2024" covers third-party platforms such as VCOM and Solar-Log, not vendor apps. — [pv magazine USA, Feb 2024](https://pv-magazine-usa.com/?p=17311)

## 4. User and installer reviews

### Takeaway
Ratings are moderately positive (iOS JP store: 4.2/5 from about 3,083 ratings). The recurring complaints are UI changes that need extra taps, limited battery scheduling (no SOC-based rules), no CSV export, dongle and connectivity problems that leave data gaps, conflicts between local Modbus and the cloud, and weak support. Distribution through Google Play is also inconsistent in some markets.

### Cited Findings
- iOS App Store (JP): 4.2/5, 3,083 ratings, version 26.2.6.001 (Sep 27 [2026]), 27 languages including Vietnamese. Complaints: more taps needed to see daily data, no SOC-threshold battery scheduling, no CSV export, limited charge/discharge scheduling. One installer review praised remote configuration. — [Apple App Store JP](https://apps.apple.com/jp/app/id1529080383)
- A UK forum user, 15 months after installation, was happy with the PV and battery hardware. They said the FusionSolar app had become unreliable, support was "useless", and dongle/inverter issues were unresolved. — [ElectricianForum UK thread](https://electricianforum.co.uk/threads/huawei-monitoring-software.56990/) (undated; single user)
- Australian installer collateral (Catch Power) says the FusionSolar app "is not available on the Apple or Google stores" and must be installed from Huawei's app gallery. — [Catch Power configuration PDF](https://www.catchpower.com.au/_files/ugd/cfbb6e_5c0b11ddefbc471abd4bacdf8547db4c.pdf). This conflicts with the active iOS listing above, so availability likely varies by country and store, especially Google Play.
- Long-running Polish forum threads (elektroda.pl, "Huawei SUN2000" mega-thread with 1,000+ pages) document ongoing dongle, firmware and FusionSolar issues. — [elektroda.pl thread](https://www.elektroda.com/rtvforum/topic3721385-1140.html) (not read in detail)
- Home Assistant and openHAB users report that firmware updates and dongle limits break either local Modbus or FusionSolar uploads. — [HA community](https://community.home-assistant.io/t/huawei-solar-integration-modbus-via-smart-dongle-blocks-fusion-solar-cloud-data/1014084); [openHAB](https://community.openhab.org/t/i-can-read-modbus-data-via-tcp-with-sdongle-a05-but-inverter-no-longer-sends-data-to-fusionsolar-server/153148)

### Gaps
- I did not retrieve the Google Play rating or review count (the listing was not fetched). I fetched no Reddit r/solar, Photovoltaikforum or Whirlpool threads directly. The note on these is based on search snippets only.
- I found no quantitative analysis of review topics.

## 5. Vietnam: market share, distributors, Vietnamese support, projects, Decree 135 and zero export

### Takeaway
Huawei has a long presence in Vietnam. It reported 4.3 GW of inverters delivered by 2020, launched its residential FusionSolar line in HCMC in January 2021, and has an after-sales centre in Vietnam. The FusionSolar app supports Vietnamese. Decree 135/2024 caps surplus export from household systems under 100 kW at 20% of installed capacity and exempts systems with anti-backflow (zero-export) devices from licensing. Huawei implements export limiting or zero export with a Smart Power Sensor (DDSU666-H/DTSU666-H) or SmartLogger and the "Grid-tied point control" settings in the FusionSolar app. I found no current independent Vietnam market-share figure for Huawei.

### Cited Findings
- Huawei launched its FusionSolar residential solution in HCMC on 15 Jan 2021 (SUN2000-L1/M1 inverters, LUNA2000 batteries, optimizers). By 2020 it had "delivered a total capacity of 4.3 GW inverters in Vietnam". — [EQ Mag Pro (Huawei release)](https://www.eqmagpro.com/huawei-residential-smart-pv-solution-supports-vietnamese-households-to-optimize-the-use-of-solar-energy/); [Kyodo News PR Wire](https://kyodonewsprwire.jp/release/202101149785)
- Competitor context: in Dec 2020 Sungrow claimed 45% of Vietnam's rooftop segment and 25% of utility-scale, with 2 GW of SG110CX shipped for rooftops in 2020. This is a vendor self-claim. — [pv magazine press release, 8 Dec 2020](https://www.pv-magazine.com/press-releases/sungrow-hit-2-gw-shipment-of-sg110cx-for-vietnam-rooftops/). Sungrow distributes residential and commercial inverters in Vietnam through XBSolar. — [PV Time](https://www.pvtime.org/sungrow-partners-with-xbsolar-to-distribute-residential-and-commercial-inverters-in-vietnam/)
- Partnerships and projects:
  - Hexagon Peak (developer) and Huawei signed a 200 MW utility agreement for Vietnam (Nov 2019). The partner cited Huawei's "after-sales support center in Vietnam". — [pv magazine Australia](https://www.pv-magazine-australia.com/?p=11497)
  - Huawei, JJ-Lapp and Solar Electric Vietnam (SEV) signed a rooftop partnership covering technical support, installation and O&M (Sep 2023). — [Vietnam Energy](https://vietnamenergy.vn/huawei-jj-lapp-and-sev-commit-toward-the-state-of-the-art-solar-rooftop-projects-in-vietnam-31557.html)
  - Rạng Đông and Huawei partnered on rooftop PV plus storage for residential and commercial use, e.g., a 10 kWp home in HCMC and a 100 kWp workshop in the Central Highlands (Dec 2025). The article is dated 17 Apr 2026. — [Rạng Đông](https://en.rangdong.com.vn/news/rang-dong-huawei-in-vietnams-solar-energy-system-expansion)
  - Huawei Vietnam and Becamex VSIP Power signed a strategic cooperation on green energy and storage in Bình Dương (date not stated). — [Bizhub](https://bizhub.vn/huawei-vietnam-and-becamex-vsip-power-jsc-signstrategic-cooperation-agreement-post349288.html)
  - EVN and Huawei co-hosted a workshop on digital grids and energy storage. — [EVN](https://en.evn.com.vn/d/en-US/news/EVN-and-Huawei-co-host-technical-workshop-on-digital-power-grids-and-energy-storage-solutions-60-12-500873) (not fetched)
- Vietnamese language: the FusionSolar iOS app lists Vietnamese among its 27 languages. — [Apple App Store JP](https://apps.apple.com/jp/app/id1529080383)
- Decree 135/2024/NĐ-CP took effect 22 Oct 2024. Under it:
  - Household and individual rooftop systems under 100 kW may sell surplus to the grid, capped at 20% of installed capacity, paid at the previous year's average market price.
  - Systems with "protective devices preventing reverse electricity flow into the national grid" (anti-backflow, i.e., zero export) are exempt from electricity operation licences, and off-grid systems have no capacity limit.
  - Systems of 1,000 kW or more that sell surplus need a licence.
  — [Mekong ASEAN](https://mekongasean.vn/dien-mat-troi-mai-nha-tu-san-tu-tieu-duoc-ban-len-luoi-toi-da-20-cong-suat-34739.html); [VnEconomy](https://vneconomy.vn/ban-hanh-nghi-dinh-ve-co-che-khuyen-khich-phat-trien-dien-mat-troi-mai-nha-tu-san-xuat-tu-tieu-thu.htm)
- How Huawei does export limitation: install a Huawei Smart Power Sensor (e.g., DDSU666-H single-phase, DTSU666-H three-phase) at the grid connection point over RS485. Then in the FusionSolar app go to Quick Settings → Add Power Meter → Power Adjustment → Grid-tied Point Control → Active Power and set the export limit (zero or a cap). — [Catch Power configuration guide](https://www.catchpower.com.au/_files/ugd/cfbb6e_5c0b11ddefbc471abd4bacdf8547db4c.pdf); [Huawei DTSU666-H product page](https://solar.huawei.com/en/products/dtsu666-h-100a/). For C&I and multi-inverter sites, export limiting runs through the SmartLogger3000. — [BayWa r.e. SmartLogger3000 Export Limitation Configuration Guide](https://solar-distribution.baywa-re.de/out/media/23-LUNA2000B_Speicher_SmartLogger3000_Export_Limitation_Configuration_Guide.pdf); [Huawei SDongle/WebUI manual](https://support.huawei.com/enterprise/en/doc/EDOC1100173984/cee3f2b/setting-parameters-over-the-webui)

### Inferences
- Decree 135 makes zero-export or ≤20% export control a core requirement for Vietnamese rooftop systems. Huawei's meter-based Grid-tied Point Control, set via the FusionSolar app, maps directly onto it: a 0 W limit for license-exempt zero-export systems, or a cap of about 20% of kWp for households selling surplus. Whether Vietnamese grid companies (EVN PCs) formally accept Huawei's meter-based control as the "anti-backflow device", or require a separate certified relay, was not confirmed.
- Vietnam's market is dominated by Chinese inverter brands (Huawei, Sungrow, Solis, Growatt, etc.). Huawei's position is strongest in C&I and utility, though this is not quantified here.

### Gaps
- I found no reliable, current (2024–2026) Vietnam inverter market-share data for Huawei or competitors. Only old vendor self-claims exist (Sungrow 2020, Huawei 4.3 GW cumulative by 2020).
- I could not confirm the official Huawei distributors in Vietnam for 2025–2026. Vietnamese-language searches returned no distributor list, and Huawei's Vietnamese partner page was not reached.
- I found no Vietnamese-language Huawei or installer guide specific to configuring zero export for Decree 135. EVN's technical acceptance of inverter-based export limitation is unverified.
- I found no information on whether Vietnamese plants are hosted on Huawei's international (Singapore/Asia) FusionSolar region, or on any Vietnam-specific data-localisation issues.
