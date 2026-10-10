# Huawei FusionSolar: architecture, cloud regions and data residency, security posture, and geopolitical/regulatory context (status as of October 2026)

## Q1. Architecture layers: devices, communication, cloud vs. on-premise, protocols to the cloud

### Takeaway
FusionSolar works in three tiers. SUN2000/SUN5000 inverters, LUNA2000 batteries, meters and optimizers sit at the bottom. They talk to a gateway: the Smart Dongle (WLAN-FE/4G) for residential and C&I, or the SmartLogger3000 for C&I and utility plants (which also supports PLC over AC cables). The gateway connects to the Huawei-hosted "FusionSolar Smart PV Management System" (SmartPVMS), which users reach through the FusionSolar app or web portal. Huawei's documentation says the SmartLogger connects to the Huawei management system on default port 27250 using "Encrypted Modbus TCP" with SSL/TLS on by default (TLS 1.2+ recommended). Plain Modbus TCP, IEC 104 and IEC 103 are offered for third-party SCADA/NMS links.

### Cited Findings
- SmartLogger3000 manual, "Setting parameters for connecting to the management system": the Server field takes the IP or domain of the management system. The recommended protocol is "Encrypted Modbus TCP" with SSL encryption enabled by default and a "second challenge authentication" (default enabled). Unencrypted Modbus TCP is a legacy option, disabled by default, limited to 5 third-party management systems, and comes with the warning that "data transmitted over this protocol is not encrypted". IEC 104 is supported for up to 5 third-party connections. TLS encryption toward "Management System-1" is on by default, and "TLS1.2 or a later version is recommended". — [Huawei SmartLogger3000 User Manual](https://support.huawei.com/enterprise/en/doc/EDOC1100108365/4fbe151e/setting-parameters-for-connecting-to-the-management-system-v300r001c00)
- FusionSolar app / SUN2000 app commissioning guide: "When the SmartLogger connects to the Huawei NMS, retain the default value 27250 for Port number". For a third-party NMS, the port depends on that NMS. Disabling TLS means "data will be transmitted without being encrypted, which may pose security risks". Protocols listed: Modbus-RTU (slave to third-party), Modbus-TCP, IEC104, IEC103. — [FusionSolar App and SUN2000 App Device Commissioning Guide](https://support.huawei.com/enterprise/en/doc/EDOC1100273864/2b6a3248/set)
- The Smart Dongle SDongleA-05 (WLAN-FE) links to the management system over WLAN (802.11b/g/n, 2.4 GHz) or a 10/100M Ethernet port. The quick guide gives no server domains or ports. — [Huawei SDongleA-05 Quick Guide (PDF)](https://solar.huawei.com/admin/asset/v1/pro/view/c36e7035f1a64443831dd9cb2431ce34.pdf)
- A TÜV SÜD RED type-examination certificate (No. TPS-RED500957 i02) covers eight SUN2000/SUN5000 Wi-Fi inverter models "plus compatible Smart Dongle accessories". This confirms the dongle is part of the inverter's radio/network attack surface. — [TÜV SÜD certificate (PDF via distributor)](https://cdn.contentspeed.ro/pimromstal.websales.ro/cs-content/cs-docs/products/35fv1635569certificateredforsun2000map0sun5000map0_78205_21_1784579986.pdf)
- Cloud access layers seen by integrators: a Northbound/OpenAPI at `https://[region].fusionsolar.huawei.com/thirdData/` (e.g., `/thirdData/login`, `getDevRealKpi`) with installer-provisioned credentials, "strict rate limits" and a single-login-session limit. There is also a public "Kiosk" dashboard URL (`/pvmswebsite/nologin/...#/kiosk?kk=`) that anyone with the link can open; its data is cached 30 minutes and the URL expires after 1 year. — [tijsverkoyen/homeassistant-fusionsolar (GitHub)](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- In September 2025 a FusionSolar platform update added a new authorization step. Owners must explicitly grant API access to the installer account (Plant Management → key icon). Until they did, third-party OpenAPI/Northbound integrations such as Home Assistant stopped working (reported 4 Sep 2025, workaround posted 20 Sep 2025). — [Home Assistant community thread](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417)
- Huawei markets the SmartPVMS (installer edition) around "one-click connection to the PV cloud", device discovery, monitoring and remote management. The product page says nothing about deployment model, security or data centers. — [Huawei Smart PV Management System for Installers](https://solar.huawei.com/en/products/smart-pv-management-system-installer); [Huawei SmartPVMS for Owners](https://solar.huawei.com/en/products/smart-pv-management-system-owner)
- Integrators can also pull data locally from the SmartLogger without the Huawei cloud, e.g., by configuring FTP/SFTP export to a third-party energy-management platform. — [Spacewell support: Gateway – Huawei – FusionSolar – SmartLogger](https://support.spacewell.com/hc/en-001/articles/28356570657436-Gateway-Huawei-FusionSolar-SmartLogger)

### Inferences
- The cloud link is an outbound, gateway-initiated session (SmartLogger/Dongle → `*.fusionsolar.huawei.com:27250`, TLS-wrapped Modbus-TCP-style protocol). That is why remote parameter changes and firmware upgrades through the app are possible. This is the "remote access" pathway that the regulators in Q4 focus on.
- Because the SmartLogger supports Modbus TCP, IEC 104 and SFTP northbound, utility owners can run an independent SCADA in parallel with, or instead of, the Huawei cloud. Huawei's public pages, however, do not document a supported fully on-premise SmartPVMS product for Europe.

### Gaps
- Port 16100 could not be confirmed in any Huawei document found. Only 27250 (SmartLogger → Huawei NMS) is documented. Dongle → cloud ports and protocols for residential systems are not in public quick guides.
- I found no current official Huawei page describing an on-premise/private-deployment edition of SmartPVMS (as opposed to the cloud). Historically, "NetEco" was Huawei's locally deployable NMS, but I found no 2024–2026 source confirming an on-premise FusionSolar option for EU customers.
- PLC between inverters and SmartLogger is known from product literature but was not verified in this round of fetching.

## Q2. Cloud regions, data centers, data residency/GDPR, and hosting

### Takeaway
FusionSolar runs on regional hostnames under `fusionsolar.huawei.com`: `intl`, `eu5` / `region01eu5` / `uni00Xeu5` for Europe, and others. Huawei's Smart PV privacy notices list storage in five regions: China (Dongguan), Singapore, Germany, Brazil and Dubai. The German FusionSolar site says data is stored in Frankfurt and not accessed from China. Other Huawei Smart PV notices, however, say personal data "will be shared with Huawei Technologies Co., Ltd in the People's Republic of China" for maintenance. This contradiction needs flagging.

### Cited Findings
- The Huawei Smart PV Community privacy notice (controller: Huawei Digital Power Technologies Co., Ltd. and global affiliates) lists data storage in "People's Republic of China (Dongguan), Asia Pacific (Singapore), Europe (Germany), Latin America (Brazil), and Middle East and Africa (Dubai)". It also says personal data "will be shared with Huawei Technologies Co., Ltd in the People's Republic of China who will provide you with maintenance service". The notice covers the FusionSolar user account used for login. — [Huawei Smart PV Community Privacy Notice (updated June 2025)](https://solar.huawei.com/en/community-privacy)
- German FusionSolar privacy statement (controller: Huawei Technologies Deutschland GmbH, Düsseldorf): "Alle Daten werden sicher in Frankfurt in Deutschland gespeichert", and customer data "nicht von China aus zugegriffen wird". It also says no cross-border transfer takes place during processing. Retention is 2 years. Caveat: the data categories listed (name, email, event registration, cookies) suggest this statement covers the solar.huawei.com marketing/website context rather than plant telemetry. — [Datenschutzerklärung – FusionSolar Deutschland](https://solar.huawei.com/de/privacy/)
- The Dutch Huawei privacy page says personal data "worden opgeslagen in de EU", but its scope is explicitly the Huawei Store only, and it refers the FusionSolar app to separate terms. — [Privacy – FusionSolar Nederland](https://solar.huawei.com/nl/privacy/)
- The FusionSolar iOS app developer is Huawei Digital Power Technologies Co., Ltd. The app's privacy policy is hosted at `intl.fusionsolar.huawei.com`. Declared data collected: precise location, contact info, photos/videos, user/device IDs, search history, usage data and diagnostics. — [App Store: FusionSolar](https://apps.apple.com/cd/app/fusionsolar/id1529080383)
- European endpoints used by integrations: `region01eu5.fusionsolar.huawei.com` is the default for the fusion-solar-py client. Accounts "moved to a new version of the web application" use `uni00Xeu5` hosts (e.g., uni002eu5). — [fusion-solar-py on PyPI](https://pypi.org/project/fusion-solar-py/0.0.25); `eu5` and `intl` are cited as region prefixes in [homeassistant-fusionsolar](https://github.com/tijsverkoyen/homeassistant-fusionsolar)
- Huawei Cloud has a Frankfurt PoP/region presence. — [Netify: Huawei Cloud – Frankfurt](https://www.netify.ai/resources/hosting/huawei-cloud/pop/frankfurt) (this does not by itself prove FusionSolar EU runs on Huawei Cloud Frankfurt)
- Contrast with a competitor: SMA emphasizes operating "only with servers located within the EU". — [Zonnefabriek (Feb 2026)](https://www.zonnefabriek.nl/en/news/will-chinese-inverters-be-banned-in-the-eu)
- In August 2026 analysis, Germany's BSI-aligned position favors local control through smart-meter gateways (§14a EnWG) instead of control paths through manufacturer clouds. — [innobu (7 Aug 2026)](https://www.innobu.com/en/articles/chinese-inverters-security-risk-high-risk-list-2026.html)
- Australia: Huawei's residential presence moved to an OEM "iStore" brand. In tests, historical FusionSolar data did not transfer to the iStore platform (the publisher marks this a dated record). — [McKercher Corporation (2023, updated Aug 2026)](https://mckerchercorporation.com/huawei-fusionsolar-vacating-australian-solar-market/)

### Inferences
- The best-supported reading is that the EU tenant ("eu5") is hosted in Germany (Frankfurt), matching the "Europe (Germany)" entry in Huawei's own storage list. But Huawei's privacy text also allows maintenance access by Huawei Technologies Co., Ltd in China. That clause is the crux of EU regulators' concern, which is about remote access and not just where data sits.
- The "la5", "sg5", "au5" naming for other regions is plausible given the five-region list (Brazil, Singapore, Dubai, Dongguan), but I could not verify it.

### Gaps
- I could not open the FusionSolar app privacy policy hosted on intl.fusionsolar.huawei.com (fetch blocked), so its exact data-center wording is unverified.
- No source confirmed whether FusionSolar runs on Huawei Cloud, Equinix or other colocation, or a Netherlands location. No DNS/ASN data was retrievable.
- No independent audit of Huawei's EU data-residency claims was found.

## Q3. Security posture: certifications, white papers, CVEs/PSIRT advisories, research findings

### Takeaway
Huawei's verifiable security credentials for FusionSolar are product-compliance certificates rather than cloud-service attestations:
- TÜV SÜD type examination for EU RED Article 3.3(d) (network protection, EN 18031-1:2024), valid from 21 Aug 2025
- UK PSTI statements of compliance (April and August 2024) with security updates promised to 31 Dec 2029
- A 2023 TÜV Rheinland/Huawei "All-Scenario Security White Paper" (mostly safety-focused)

I found no public NVD CVEs specific to SUN2000, SmartLogger or the FusionSolar app/cloud. Major 2025–2026 inverter vulnerability research (Forescout SUN:DOWN; CCC on Hoymiles) did not name Huawei.

### Cited Findings
- TÜV SÜD Product Service (Notified Body 0123), EU-type examination certificate TPS-RED500957 i02: covers eight Huawei SUN2000/SUN5000 Wi-Fi inverter models plus compatible Smart Dongles under RED 2014/53/EU Article 3.3(d) "in respect to network protection", standard EN 18031-1:2024. Valid from 2025-08-21 with a 5-year monitoring period to 2030-08-20. EN 303 645 and Article 3.3(e)/(f) are not listed. — [TÜV SÜD certificate (PDF)](https://cdn.contentspeed.ro/pimromstal.websales.ro/cs-content/cs-docs/products/35fv1635569certificateredforsun2000map0sun5000map0_78205_21_1784579986.pdf)
- UK PSTI statements of compliance from Huawei Technologies Co., Ltd., signed by Quan Sun, President of Residential Smart PV Business:
  - April 2024: single-phase SUN2000 2–10K, optimizers, power sensors, communication devices, LUNA2000
  - August 2024: three-phase SUN2000/SUN5000 5–25K, LUNA2000, SmartGuard
  - Defined security-update support period: "5 years (until 31/12/2029)"
  — [Huawei Solar UK PSTI Statement of Compliance](https://solar.huawei.com/en/service-support/tsc/warranty-terms-and-conditions)
- 13 June 2023: TÜV Rheinland and Huawei jointly released an "All-Scenario Security White Paper", which says FusionSolar all-scenario solutions met security standards "in all dimensions". Huawei describes a "5+4" multi-level security design. The public summaries are about electrical/fire safety more than cybersecurity. — [Huawei news 2023-06-13](https://solar.huawei.com/en/news/2023/news-20230613/); [Huawei DE news 2023-06-15](https://solar.huawei.com/de/news/2023/news-20230615/)
- Forescout Vedere Labs "SUN:DOWN" (27 Mar 2025): 46 new vulnerabilities in Sungrow, Growatt and SMA products, all patched. Huawei is not among the affected vendors. 80% of solar-system vulnerabilities disclosed in the prior three years were high/critical. 53% of inverter makers and 58% of storage makers are China-based. — [Forescout press release](https://forescout.com/press-releases/forescout-vedere-labs-uncovers-severe-systemic-security-risks-in-global-solar-power-infrastructure)
- Chaos Computer Club (2026) found unauthenticated firmware updates and remote control in Hoymiles microinverters. It was reported Feb 2026, and Hoymiles reacted only after BSI contacted CNCERT in June 2026. Huawei was not implicated. — [Cybernews (8 Jul 2026)](https://cybernews.com/security/china-solar-inverters-hack/)
- Dutch RDI: a 2023 investigation found none of the examined inverters met security standards (brands not specified in source). From 1 Aug 2025 the RED cybersecurity requirements apply and RDI can fine, ban or recall. — [Solar Magazine NL (Jul 2025)](https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al)
- Searches for "SmartLogger"/"SUN2000" CVEs returned only unrelated Huawei CVEs. CVE-2021-22310 and CVE-2021-22356 affect Huawei USG/NIP firewalls, not solar products. — [INCIBE CVE-2021-22310](https://www.incibe.es/en/incibe-cert/early-warning/vulnerabilities/cve-2021-22310); [INCIBE CVE-2021-22356](https://www.incibe.es/index.php/incibe-cert/alerta-temprana/vulnerabilidades/cve-2021-22356)
- Competitor benchmark: Sungrow obtained ISO/IEC 27019 and other BSI-issued cybersecurity management certifications. This shows the kind of certification EU buyers increasingly expect. — [Sungrow press release](https://dl.sungrowpower.com/en/sungrow-achieves-iso-iec-27019-and-multiple-cybersecurity-management-system-certifications-from-bsi)

### Inferences
- Huawei's public posture leans on product-level conformity (RED/EN 18031, UK PSTI). I found no public ISO 27001/27701, CSA STAR or IEC 62443 certificate scoped to the FusionSolar cloud. Such certificates may exist (Huawei Cloud holds many), but they are not presented on FusionSolar pages.
- The lack of published CVEs could reflect genuinely fewer findings, less researcher access, or disclosure handled privately through Huawei PSIRT. It should not be read as proof of security.

### Gaps
- I did not find a Huawei PSIRT advisory specific to SUN2000, SmartLogger or FusionSolar. The Huawei PSIRT portal was not directly searchable in this session.
- I found no evidence for ISO 27001, ISO 27701, CSA STAR, IEC 62443-4-1/4-2 or ETSI EN 303 645 certification of FusionSolar. These need checking on Huawei's trust center or with certifiers.
- The full TÜV Rheinland white paper content was not retrieved.

## Q4. Geopolitics and regulation 2024–2026 (with dates)

### Takeaway
Between November 2024 and October 2026, pressure on Huawei inverters moved from national measures to EU-level policy:
- Lithuania banned remote access by Chinese firms to systems over 100 kW (law of 12 Nov 2024; in force 1 May 2025 for new plants, 1 May 2026 for existing ones).
- The Huawei bribery probe (March 2025) led the Commission to restrict contacts with Huawei-linked associations. SolarPower Europe expelled Huawei on 28 Apr 2025.
- Reuters' unconfirmed May 2025 "rogue communication devices" report (no vendor named) fueled concern. A January 2026 DOE review found no definitive evidence of malicious hidden devices.
- The EU named inverters a high-risk dependency (Dec 2025) and proposed a Cybersecurity Act revision with a high-risk-vendor mechanism (20 Jan 2026). It restricted EU/EIB funding for projects using inverters from China, Russia, Iran and North Korea (announced 4–5 May 2026), with a transitional cut-off of 1 Nov 2026.
- In the US, an FCC import ban on Chinese inverters was reported in draft (June 2026).

Huawei denies any backdoors and calls the EU measure origin-based discrimination.

### Cited Findings
**Lithuania**
- The Seimas passed an amendment to the Law on Electricity on 12 Nov 2024 (79 for, 1 against, 6 abstentions). It bans remote access by Chinese companies to solar, wind and storage systems over 100 kW. It does not ban installing Chinese equipment and does not require removal; operators must add cyber safeguards instead. The law took effect 1 May 2025. — [LRT](https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems)
- Compliance deadlines: new plants over 100 kW by 1 May 2025, existing sites by 1 May 2026. — [PV Tech (13 Nov 2024)](https://pv-tech.org/lithuania-to-block-chinese-inverters-with-cybersecurity-legislation)
- Conflict: Defense News describes the law as effectively excluding Chinese inverters and requiring retrofits of existing projects, which goes further than LRT's account. — [Defense News (29 May 2025)](https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/)

**Huawei bribery probe and the association expulsions (confirmed facts; the bribery itself is an allegation)**
- 13 Mar 2025: Belgian federal police (about 100 officers, 21 searches in Belgium and Portugal) made arrests over suspected bribery of current or former MEPs by Huawei lobbyists, allegedly since 2021. On 14 Mar 2025 the European Parliament suspended Huawei lobbyists' access. Huawei said it took the allegations seriously and would "urgently communicate" with investigators. — [BreakingNews.ie / AP](https://breakingnews.ie/world/huawei-lobbyists-banned-from-accessing-european-parliament-after-bribery-arrests-1740707.html)
- 28 Apr 2025: SolarPower Europe removed Huawei as a member, its first ever removal. SPE said this followed "the European Commission's decision to restrict meetings with associations who have Huawei in their membership". DigitalEurope and BusinessEurope also suspended Huawei. Huawei declined comment and said it has "zero-tolerance" for bribery. — [pv magazine (8 May 2025)](http://www.pv-magazine.com/2025/05/08/solarpower-europe-expels-huawei-amid-eu-bribery-probe/)
- Eurelectric reportedly considered suspending Huawei as well. — [DigiTimes (12 May 2025)](https://www.digitimes.com/news/a20250512PD231.html)

**Industry warnings and "rogue devices" reports (allegations vs. confirmations)**
- 30 Apr 2025: ESMC said Huawei and Sungrow "control remote access to 168 GW of PV capacity in Europe" (more than 200 GW linked to Chinese inverters, projected above 400 GW by 2030). It called for an EU "Inverter Security Toolbox" and wider use of the Lithuanian model. — [ESMC](https://esmc.solar/restrict-remote-access-of-pv-inverters-from-high-risk-vendors/)
- 14–15 May 2025: Reuters reported that US energy officials, over the prior nine months, found undocumented communication devices (including cellular radios) in some Chinese inverters and batteries. No manufacturer was named; the report relied on two unnamed sources. pv magazine said it "cannot verify this information". The DOE said functionality "may not have malicious intent". — [Hawaii Tribune-Herald / Reuters](https://www.hawaiitribune-herald.com/2025/05/15/nation-world-news/rogue-communication-devices-found-in-chinese-solar-power-inverters/); [pv magazine](https://www.pv-magazine.com/2025/05/14/hidden-devices-found-in-chinese-made-inverters-in-the-us-reports-reuters/)
- Huawei Austria spokesperson Michael Nowak: "the inverters meet all European standards and backdoors can be ruled out". — [Vienna.at](https://www.vienna.at/triggering-a-blackout-possible-usa-discovered-hidden-radio-modules-in-inverters-from-china/9414809)
- November 2024: inverters in the US, UK and Pakistan were disabled remotely from China. Investigations pointed to a commercial dispute, not a state attack. This source does not name the vendor and does not implicate Huawei. Other reporting attributes it to a dispute between Deye and Sol-Ark, but I did not verify that here. — [Defense News](https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/)
- 29 Jan 2026: a DOE and National Labs analysis of about 30 inverters found two cases where communications "differed from official documentation". These were judged "non-malicious" and "non-intentional", with no evidence of malicious wireless functions. The DOE still warned that coordinated manipulation could have larger effects. — [pv magazine India (29 Jan 2026)](https://www.pv-magazine-india.com/2026/01/29/u-s-authorities-find-no-definitive-evidence-of-hidden-devices-in-chinese-solar-inverters)

**Netherlands**
- 28 May 2025: MP Jesse Six Dijkstra (NSC) filed a motion to ban foreign suppliers' remote on/off "kill switch" capability in inverters and heat pumps. — [Solar Magazine NL](https://solarmagazine.nl/nieuws-zonne-energie/i40683/nsc-wil-kill-switch-in-omvormers-zonnepanelen-verbieden)
- 9 Jul 2025: Minister Hermans told parliament that hidden remote on/off functionality is already prohibited under EU law. RED cybersecurity requirements apply from 1 Aug 2025, with RDI enforcement (fines, sales bans, recalls). The CRA applies from December 2027. The cabinet cited Lithuania's 100 kW rule as a possible model. — [Solar Magazine NL](https://solarmagazine.nl/nieuws-zonne-energie/i41070/kabinet-verscherpt-toezicht-op-chinese-omvormers-zonnepanelen-verbod-kill-switch-bestaat-al)

**Czech Republic**
- September 2025: NÚKIB issued a "High" threat warning on data transfers to, and remote administration from, the PRC, Hong Kong and Macau. Regulated entities must account for it in procurement. The warning does not specifically name solar inverters. — [WorldECR (11 Sep 2025)](https://www.worldecr.com/news/czech-republic-issues-high-risk-warning-on-chinese-data-transfers-after-cyberattacks/)

**Estonia**
- Late 2024: intelligence chief Kaupo Rosin warned that Chinese tech in solar farms could expose Europe to blackmail. — [Defense News](https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/)

**EU institutions**
- 27 Oct 2025: Politico/E&E reported Huawei's dominance as a feared "next dependency crisis". — [E&E News](https://www.eenews.net/articles/huaweis-solar-tech-sparks-fears-of-europes-next-dependency-crisis)
- 10 Nov 2025: more than 30 MEPs wrote to the Commission. They said 80% of new EU inverter capacity in 2024 came from China and that Huawei held over 115 GW of Europe's inverter market (2023). — [Mercom India](https://mercomindia.com/eu-lawmakers-want-chinese-solar-inverters-restricted-on-security-concerns)
- December 2025: a Commission joint communication identified solar inverters as a "high-risk dependency" (China, Russia, Iran, North Korea). — [EU Perspectives (May 2026)](https://euperspectives.eu/2026/05/the-green-transition-has-a-backdoor-europe-is-moving-to-close-it/)
- 20 Jan 2026: the Commission presented its Cybersecurity Act revision with a "high-risk vendors list" mechanism that could bar vendors from the EU market. EVP Henna Virkkunen cited solar inverters as an example. — [pv magazine (20 Jan 2026)](http://www.pv-magazine.com/2026/01/20/eu-to-ban-chinese-inverters-commission-proposal-in-cybersecurity-mulls-high-risk-vendors-list/)
  - The proposal was slightly delayed from 14 Jan because of member-state disagreement. Parliament pushed EU-hosted cloud for certification. — [PV Time](https://www.pvtime.org/?p=24724)
  - It was in first reading in Parliament as of May 2026. — [EU Perspectives](https://euperspectives.eu/2026/05/the-green-transition-has-a-backdoor-europe-is-moving-to-close-it/)

**EU funding restriction**
- Commission spokesperson Siobhan McGarry confirmed on 5 May 2026 that EU funding is blocked for inverters from high-risk vendors "including China's Huawei". Exceptions for ongoing projects are to be decided by 1 Nov 2026. — [E&E News](https://www.eenews.net/articles/commission-blocks-eu-funding-for-huawei-solar-tech/)
- Scope and timeline:
  - Covers EIB/EIF funding, solar, wind and BESS (including PCS), and companies owned or controlled from China, Russia, Iran or North Korea, with no power-class exemption.
  - Implementation began 1 May 2026; grandfathering applications were due 1 Sep 2026, with final approvals by 1 Nov 2026.
  - Non-EU grid-connected projects (North Africa, Western Balkans) must phase out by 15 Apr 2027.
  - The EIB funded about 20% of EU solar in 2025.
  — [ESS News (4 May 2026)](https://www.ess-news.com/2026/05/04/eu-funding-ban-on-high-risk-inverters-including-chinese-suppliers-extends-to-bess-pcs/)
- Euronews gives the timeline as: review of ongoing activities by 1 Jul 2026, transition ends 1 Nov 2026, stricter phase-in from April 2027. — [Euronews (4 May 2026)](https://euronews.com/2026/05/04/eu-moves-to-ban-high-risk-inverters-from-china-over-cybersecurity-threats)
- Conflicting dates for the decision itself: "early April 2026" ([Bluewin](https://www.bluewin.ch/en/news/international/brussels-stops-eu-funding-for-projects-with-technology-from-china-li.3218431)) vs. 23 Apr 2026 ([innobu](https://www.innobu.com/en/articles/chinese-inverters-security-risk-high-risk-list-2026.html)). innobu also says private systems under 30 kW are exempt, which conflicts with ESS News's "no exemptions based on power class".

**Germany**
- September 2026: Berlin endorses the EU position. The Economy Ministry, Interior Ministry, BNetzA and BSI are examining whether §41 BSIG allows restricting such components in energy infrastructure. — [CleanThinking (Sep 2026)](https://www.cleanthinking.de/?p=1072975)

**China's response**
- 7–11 May 2026: MOFCOM "firmly opposes" the EU funding block, saying the EU labeled China "high-risk" "without any concrete evidence". — [Caixin (11 May 2026)](https://www.caixinglobal.com/2026-05-11/beijing-hits-back-at-eu-funding-block-for-projects-using-chinese-inverters-102442951.html)
- The China Chamber of Commerce to the EU urged "technology neutrality". — [Euronews](https://euronews.com/2026/05/04/eu-moves-to-ban-high-risk-inverters-from-china-over-cybersecurity-threats)

**United States**
- Huawei withdrew from the US inverter market in 2019. — [Vienna.at](https://www.vienna.at/triggering-a-blackout-possible-usa-discovered-hidden-radio-modules-in-inverters-from-china/9414809)
- Late June 2026: Reuters reported that the FCC, with the National Energy Dominance Council and Commerce, was drafting a ban on imports of new foreign/Chinese inverter models, still in draft and possibly to be modified or shelved. Huawei was named as a leading maker. — [KSL / Reuters (30 Jun 2026)](https://www.ksl.com/article/51582258/us-is-working-on-ban-targeting-chinese-energy-inverters-sources-say)
- The DOD's list of Chinese military companies includes Huawei, with a DOD business ban from 2027. — [pv magazine India (1 Jul 2026)](http://www.pv-magazine-india.com/2026/07/01/trump-administration-reportedly-drafting-ban-on-chinese-solar-inverters/)

**Huawei's own responses**
- Huawei "repeatedly denied that its equipment poses any security threat". — [EU Perspectives](https://euperspectives.eu/2026/05/the-green-transition-has-a-backdoor-europe-is-moving-to-close-it/)
- Huawei rejected the EU funding directive as "origin discrimination without objective basis" and noted that Austria's national EAG subsidies are unaffected. — [CleanThinking (Sep 2026)](https://www.cleanthinking.de/?p=1072975)
- EU data localization: the German privacy page says data is stored in Frankfurt and not accessed from China. — [Huawei DE privacy](https://solar.huawei.com/de/privacy/)

### Inferences
- The regulatory trajectory points at the cloud and remote-access channel (gateway → vendor cloud → firmware/parameter control), not just the hardware. Lithuania's model and Germany's §14a/smart-meter-gateway approach both aim to cut or locally mediate the manufacturer's remote path. For FusionSolar this pressures toward EU-only operations, local or offline control modes, or third-party SCADA via SmartLogger northbound interfaces.
- The legally binding measures in force as of October 2026 are Lithuania's law and the EU funding restrictions. The Cybersecurity Act high-risk vendor list is still a legislative proposal. The Reuters "rogue devices" claim remains unattributed to Huawei and was largely deflated by the DOE's January 2026 review.

### Gaps
- No primary Commission document for the funding guidance was retrieved; dates come from press. The exact decision date (early April vs. 23 Apr 2026) and any small-system exemption are unresolved.
- I found no evidence that Huawei announced a specific EU-only operations entity, an offline/local mode, or an "EU data boundary" for FusionSolar in response to 2025–2026 measures. This needs checking.
- I found no confirmed Commission ban on Huawei inverters for the Commission's internal use. The confirmed April 2025 action was restricting meetings with Huawei-linked associations.
- Status of the Cybersecurity Act revision in Council/Parliament after May 2026 is unknown.
- Poland, Italy, the UK (beyond PSTI) and Denmark actions were not researched in depth.

## Q5. Outages and incidents involving the FusionSolar cloud

### Takeaway
I found no widely reported major outage of the FusionSolar cloud in 2024–2026. Reported user-facing disruptions are limited to planned maintenance and the September 2025 API-authorization change that broke third-party integrations. The sources I found do not link the November 2024 remote-disabling incident to Huawei.

### Cited Findings
- 4–20 Sep 2025: a FusionSolar platform update added owner-granted API authorization, which broke Home Assistant OpenAPI/Northbound integrations until owners authorized installers. — [Home Assistant community](https://community.home-assistant.io/t/fusion-solar-doesnt-work-anymore/927417)
- Users in community forums report platform maintenance windows. — [Bricozone (BE) thread](https://www.bricozone.be/t/maintenance-de-la-plateforme-huawei-pour-les-panneaux.147869/)
- The November 2024 remote disabling of inverters in the US, UK and Pakistan from China was linked to an industry dispute, and no Huawei involvement was reported. — [Defense News](https://www.defensenews.com/global/europe/2025/05/29/chinese-hold-on-solar-power-tech-raises-fresh-sabotage-fears-in-europe/)

### Inferences
- Third-party integrations depend on FusionSolar's cloud API policies (rate limits, single session, CAPTCHA, owner authorization), so operators who need resilience typically use local Modbus TCP via the dongle or SmartLogger.

### Gaps
- No official FusionSolar status page or incident history was found. I found no reliable source on any multi-hour regional cloud outage.
