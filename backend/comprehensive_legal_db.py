"""
Comprehensive Indian Legal Database
Complete coverage of all major Indian law topics with detailed information
"""

# Define specialized legal areas
SPECIALIZED_LEGAL_AREAS = {
    "detailed_solutions": "Legal solutions with step-by-step procedures",
    "case_law": "Legal precedents and landmark judgments",
    "procedural_law": "Court procedures and legal processes"
}

# COMPREHENSIVE INDIAN LEGAL DATABASE - 200+ TOPICS

COMPREHENSIVE_LEGAL_FAQ = {
    
    # ==================== CONSTITUTIONAL LAW ====================
    "fundamental_rights": "Fundamental Rights under Articles 12-35 include Right to Equality (14-18), Right to Freedom (19-22), Right against Exploitation (23-24), Right to Freedom of Religion (25-28), Cultural and Educational Rights (29-30), and Right to Constitutional Remedies (32).",
    
    "directive_principles": "Directive Principles of State Policy under Articles 36-51 are non-justiciable guidelines for governance including social justice, economic welfare, and international peace. Key principles include uniform civil code, prohibition of cow slaughter, and separation of judiciary from executive.",
    
    "fundamental_duties": "Fundamental Duties under Article 51A include respecting Constitution and national symbols, cherishing noble ideals of freedom struggle, protecting sovereignty and integrity, defending the country, promoting harmony, preserving composite culture, protecting environment, developing scientific temper, safeguarding public property, and striving for excellence.",
    
    "emergency_provisions": "Emergency provisions under Articles 352-360 include National Emergency (Article 352), President's Rule in states (Article 356), and Financial Emergency (Article 360). During emergency, fundamental rights can be suspended and Centre gets extensive powers.",
    
    "amendment_procedure": "Constitutional amendment under Article 368 requires special majority (2/3rd of present and voting + majority of total membership) in both houses. Some amendments also need ratification by half the state legislatures.",
    
    "judicial_review": "Judicial review is the power of courts to examine constitutionality of laws and executive actions. Supreme Court is the final interpreter of Constitution. Landmark cases include Kesavananda Bharati (1973) establishing basic structure doctrine.",
    
    "separation_powers": "Separation of powers divides government into Legislature (law-making), Executive (law-implementing), and Judiciary (law-interpreting). Indian system has separation with checks and balances, not rigid separation like USA.",
    
    "federalism": "Indian federalism under Articles 245-263 divides powers between Centre and States through Union List (97 subjects), State List (66 subjects), and Concurrent List (47 subjects). Residuary powers vest with Centre.",
    
    # ==================== CRIMINAL LAW ====================
    "indian_penal_code": "Indian Penal Code 1860 defines crimes and punishments. Contains 511 sections covering offenses against state, public tranquility, human body, property, marriage, defamation, and other crimes with corresponding punishments.",
    
    "criminal_procedure": "Criminal Procedure Code 1973 provides procedure for investigation, inquiry, trial, and appeals in criminal cases. Contains provisions for arrest, bail, trial procedure, evidence, and execution of sentences.",
    
    "evidence_act": "Indian Evidence Act 1872 governs admissibility of evidence in courts. Defines facts, relevancy, oral and documentary evidence, burden of proof, presumptions, and examination of witnesses.",
    
    "murder_law": "Murder under IPC Section 300/302 requires intention to cause death or knowledge that act is likely to cause death. Punishment is death or life imprisonment. Culpable homicide not amounting to murder under Section 304 has lesser punishment.",
    
    "theft_robbery": "Theft (Section 378) is dishonestly taking movable property. Robbery (Section 390) is theft with violence or threat. Dacoity (Section 391) is robbery by 5 or more persons. Punishments range from 3 years to life imprisonment.",
    
    "fraud_cheating": "Cheating under Section 420 involves deceiving someone to deliver property or do/omit something. Punishment is imprisonment up to 7 years and fine. Criminal breach of trust (Section 405) involves dishonest misappropriation of entrusted property.",
    
    "sexual_offenses": "Sexual offenses include rape (Section 375), sexual harassment, acid attacks, voyeurism, and stalking. POCSO Act 2012 specifically deals with child sexual abuse. Punishments range from 7 years to death penalty.",
    
    "dowry_laws": "Dowry Prohibition Act 1961 and IPC Section 498A criminalize dowry demands and harassment. Dowry death under Section 304B presumes culpability if woman dies within 7 years of marriage due to dowry cruelty.",
    
    "corruption_laws": "Prevention of Corruption Act 1988 deals with public servant corruption. Offenses include taking bribes, criminal misconduct, and disproportionate assets. Lokpal and Lokayuktas Act 2013 provides institutional mechanism against corruption.",
    
    "cybercrime_laws": "IT Act 2000 and amendments deal with cybercrimes including hacking (Section 66), identity theft (66C), phishing (66D), and cyber terrorism (66F). Punishments include imprisonment and fines.",
    
    "narcotics_laws": "Narcotic Drugs and Psychotropic Substances Act 1985 prohibits cultivation, production, sale, and consumption of drugs. Punishments are severe, ranging from 10 years to death penalty depending on quantity.",
    
    "terrorism_laws": "Unlawful Activities Prevention Act 1967 deals with terrorism and unlawful activities. NIA Act 2008 establishes National Investigation Agency. Punishments include life imprisonment and death penalty.",
    
    "fir_filing": "FIR (First Information Report) filing procedure: 1) Visit nearest police station, 2) Provide written complaint with details of incident, 3) Police must register FIR for cognizable offenses, 4) Get FIR copy with number, 5) If police refuse, approach Magistrate under Section 156(3) CrPC. FIR must be filed immediately after incident. No fees required. Essential details: date, time, place, nature of offense, witnesses.",
    
    "police_complaint": "To file police complaint: 1) Visit police station in whose jurisdiction crime occurred, 2) Submit written application with incident details, 3) For cognizable offenses, FIR will be registered, 4) For non-cognizable offenses, NC report will be made, 5) Get acknowledgment receipt, 6) Follow up on investigation. Required information: complainant details, incident description, evidence, witness details.",
    
    "bail": "Bail is the temporary release of an accused person awaiting trial. Types include regular bail (Section 437), anticipatory bail (Section 438), and default bail (Section 167). Bail is generally granted except for serious offenses.",
    
    # ==================== CIVIL LAW ====================
    "contract_law": "Indian Contract Act 1872 governs agreements and contracts. Essential elements include offer, acceptance, consideration, capacity, free consent, lawful object, and certainty. Breach attracts damages or specific performance.",
    
    "tort_law": "Law of torts provides remedy for civil wrongs. Major torts include negligence, defamation, trespass, nuisance, and assault. Consumer Protection Act also covers service deficiency and product liability.",
    
    "property_law": "Transfer of Property Act 1882 governs sale, mortgage, lease, gift, and exchange of immovable property. Registration Act 1908 mandates registration of property transactions above ₹100.",
    
    "succession_laws": "Hindu Succession Act 1956 governs inheritance among Hindus. Indian Succession Act 1925 applies to Christians and Parsis. Muslim Personal Law governs Muslim inheritance. Wills and intestate succession are covered.",
    
    "family_laws": "Personal laws govern marriage, divorce, maintenance, and adoption. Hindu Marriage Act 1955, Muslim Personal Law, Indian Christian Marriage Act 1872, and Parsi Marriage and Divorce Act 1936 are applicable.",
    
    # ==================== DETAILED FAMILY LAW TOPICS ====================
    "divorce_procedure": "Divorce procedure in India: 1) File petition in family court with jurisdiction, 2) Serve notice to spouse, 3) Attend counseling sessions (mandatory), 4) Present evidence and arguments, 5) Court grants decree if grounds proved. Mutual consent divorce takes 6-18 months, contested divorce takes 2-5 years. Required documents: marriage certificate, income proof, property details, evidence of cruelty/desertion.",
    
    "mutual_consent_divorce": "Mutual consent divorce under Section 13B: Both spouses jointly file petition agreeing to divorce. Procedure: 1) File joint petition with settlement terms, 2) Wait 6-month cooling period, 3) File second motion confirming decision, 4) Court grants decree. Faster process (6-12 months), lower costs, privacy maintained. Settlement should cover alimony, child custody, property division.",
    
    "contested_divorce": "Contested divorce when one spouse opposes: Grounds include cruelty, desertion (2+ years), adultery, conversion, mental disorder, incurable disease. Procedure: 1) File petition with evidence, 2) Serve notice to respondent, 3) Respondent files reply, 4) Evidence recording, 5) Arguments, 6) Judgment. Takes 2-5 years, higher costs, public proceedings.",
    
    "divorce_grounds": "Grounds for divorce under Hindu Marriage Act: 1) Adultery, 2) Cruelty (physical/mental), 3) Desertion for 2+ years, 4) Conversion to another religion, 5) Mental disorder, 6) Leprosy, 7) Venereal disease, 8) Renunciation of world. Additional grounds for wife: husband's bigamy, rape/sodomy/bestiality, non-resumption of cohabitation after maintenance order.",
    
    "alimony_maintenance": "Alimony/maintenance in divorce: Wife entitled to maintenance during and after divorce proceedings. Factors considered: husband's income, wife's needs, lifestyle, age, health, earning capacity. Types: 1) Interim maintenance during case, 2) Permanent alimony after divorce, 3) Lump sum or monthly payments. Amount: typically 25-33% of husband's income. Can be modified based on changed circumstances.",
    
    "child_custody_divorce": "Child custody in divorce cases: Court's primary concern is child's welfare. Types: 1) Physical custody (where child lives), 2) Legal custody (decision-making rights), 3) Joint custody (both parents share). Factors: child's age, preference (if 9+ years), parents' financial status, moral character. Mother usually gets custody of children under 5 years. Father liable for maintenance regardless of custody.",
    
    "child_maintenance": "Child maintenance obligations: Both parents responsible for child's expenses including education, medical, clothing, shelter. Amount depends on: 1) Parents' income and assets, 2) Child's needs and lifestyle, 3) Standard of living before divorce. Maintenance continues until child becomes self-dependent or completes education (usually 18-25 years). Can be enforced through salary attachment.",
    
    "property_division_divorce": "Property division in divorce: No automatic 50-50 division in India. Court considers: 1) Contribution to property acquisition, 2) Financial and non-financial contributions, 3) Future needs of parties. Separate property remains with owner. Joint property divided based on contribution. Streedhan (wife's personal property) remains with wife. Maintenance different from property settlement.",
    
    "domestic_violence_divorce": "Domestic violence as divorce ground: Physical, mental, sexual, economic abuse constitutes cruelty. Evidence required: 1) Medical reports of injuries, 2) Police complaints/FIR, 3) Witness statements, 4) Photos/videos, 5) Hospital records. Can file under Domestic Violence Act 2005 simultaneously. Protection orders, residence orders, monetary relief available. Cruelty is valid ground for divorce.",
    
    "dowry_harassment_divorce": "Dowry harassment in marriage: Demanding dowry is criminal offense under Dowry Prohibition Act. Evidence: 1) Demand letters/messages, 2) Witness testimonies, 3) Audio/video recordings, 4) Financial transaction records. Can file: 1) Criminal case under IPC 498A, 2) Divorce petition on cruelty grounds, 3) Domestic violence case. Punishment: 3 years imprisonment and fine.",
    
    "limitation_act": "Limitation Act 1963 prescribes time limits for filing suits and applications. General period is 3 years for most civil suits. Property suits have 12 years limitation. Criminal cases generally have no limitation.",
    
    "specific_relief": "Specific Relief Act 1963 provides remedies like specific performance of contracts, rectification of instruments, cancellation of documents, and declaratory decrees when monetary compensation is inadequate.",
    
    "civil_procedure": "Civil Procedure Code 1908 provides procedure for civil suits including jurisdiction, pleadings, discovery, trial, decree, appeal, and execution. Order and Rules provide detailed procedures.",
    
    # ==================== COMMERCIAL LAW ====================
    "company_law": "Companies Act 2013 governs incorporation, management, and winding up of companies. Provides for different types of companies, board governance, audit requirements, and investor protection measures.",
    
    "partnership_law": "Partnership Act 1932 governs partnership firms. Limited Liability Partnership Act 2008 provides for LLPs. Partners have unlimited liability in partnerships but limited liability in LLPs.",
    
    "insolvency_law": "Insolvency and Bankruptcy Code 2016 provides time-bound resolution of insolvency. Corporate Insolvency Resolution Process (CIRP) must be completed within 330 days including litigation.",
    
    "securities_law": "Securities and Exchange Board of India (SEBI) Act 1992 regulates securities market. SEBI protects investor interests, promotes market development, and regulates intermediaries like brokers and mutual funds.",
    
    "banking_law": "Banking Regulation Act 1949 governs banking operations. RBI Act 1934 establishes Reserve Bank as central bank. SARFAESI Act 2002 enables banks to recover secured loans without court intervention.",
    
    "competition_law": "Competition Act 2002 prohibits anti-competitive practices, abuse of dominant position, and regulates combinations. Competition Commission of India (CCI) enforces the Act and promotes competition.",
    
    "arbitration_law": "Arbitration and Conciliation Act 2015 provides alternative dispute resolution mechanism. Arbitral awards are binding and enforceable like court decrees. International commercial arbitration is also covered.",
    
    "intellectual_property": "Intellectual property laws include Patents Act 1970, Trade Marks Act 1999, Copyright Act 1957, and Designs Act 2000. These protect inventions, brands, creative works, and industrial designs respectively.",
    
    "foreign_exchange": "Foreign Exchange Management Act 1999 regulates foreign exchange transactions. RBI issues regulations for current and capital account transactions, foreign investment, and external commercial borrowings.",
    
    # ==================== LABOUR LAW ====================
    "industrial_relations": "Industrial Disputes Act 1947 provides machinery for investigation and settlement of industrial disputes through conciliation, arbitration, and adjudication. Covers retrenchment, lay-off, and closure.",
    
    "wages_law": "Minimum Wages Act 1948 ensures minimum wage rates. Payment of Wages Act 1936 regulates wage payments and deductions. Equal Remuneration Act 1976 prohibits gender discrimination in wages.",
    
    "social_security": "Employees' Provident Fund Act 1952 mandates PF contributions. Employees' State Insurance Act 1948 provides medical benefits. Payment of Gratuity Act 1972 provides retirement benefits.",
    
    "working_conditions": "Factories Act 1948 regulates working conditions in factories. Contract Labour Act 1970 regulates contract workers. Shops and Establishments Acts regulate working hours and conditions in commercial establishments.",
    
    "employment_rights": "Employment rights include fair wages, reasonable working hours, safe working conditions, social security benefits, and protection against discrimination and harassment.",
    
    "trade_unions": "Trade Unions Act 1926 provides for registration and regulation of trade unions. Workers have right to form unions, collective bargaining, and strike (with restrictions in essential services).",
    
    "maternity_benefits": "Maternity Benefit Act 2017 provides 26 weeks paid maternity leave. Includes 8 weeks pre-natal and 18 weeks post-natal leave. Also provides for miscarriage and tubectomy leave.",
    
    "sexual_harassment": "Sexual Harassment of Women at Workplace Act 2013 mandates zero tolerance policy. Every workplace must have Internal Complaints Committee (ICC) for redressal of complaints.",
    
    # ==================== DETAILED EMPLOYMENT TOPICS ====================
    "job_termination": "Employment termination laws: 1) Termination with notice (30 days for monthly paid employees), 2) Termination with payment in lieu of notice, 3) Summary dismissal for misconduct, 4) Retrenchment with compensation. Industrial Disputes Act protects workers in establishments with 100+ employees. Domestic inquiry mandatory before dismissal for misconduct. Wrongful termination attracts reinstatement and back wages.",
    
    "workplace_harassment": "Workplace harassment includes: sexual harassment, bullying, discrimination, hostile work environment. Remedies: 1) Internal complaint to ICC/HR, 2) External complaint to Local Complaints Committee, 3) Police complaint for criminal acts, 4) Civil suit for damages. Employer liable for providing safe workplace. Complaint must be filed within 3 months of incident.",
    
    "salary_disputes": "Salary disputes remedies: 1) Raise grievance with HR/management, 2) File complaint with Labour Commissioner, 3) Approach Labour Court under Industrial Disputes Act, 4) File case under Payment of Wages Act. Employer must pay wages within 7 days (monthly paid) or 10 days (weekly paid). Deductions limited to specific purposes. Interest payable on delayed wages.",
    
    "pf_withdrawal": "PF withdrawal procedure: 1) Submit Form 19 for full withdrawal or Form 31 for partial withdrawal, 2) Attach required documents (Aadhaar, bank details, employment proof), 3) Get employer attestation, 4) Submit to PF office or online through UAN portal. Full withdrawal allowed after 2 months of unemployment. Partial withdrawal for specific purposes like marriage, education, medical emergency.",
    
    "gratuity_claim": "Gratuity claim procedure: Employee eligible after 5 years of service. Amount: 15 days salary for each year of service. Procedure: 1) Submit Form I within 30 days of leaving, 2) Employer must pay within 30 days, 3) If denied, approach Controlling Authority. Maximum gratuity: ₹20 lakhs. Gratuity payable on retirement, resignation, death, disablement.",
    
    "employment_contract": "Employment contract essentials: 1) Job role and responsibilities, 2) Salary and benefits structure, 3) Working hours and leave policy, 4) Termination conditions and notice period, 5) Confidentiality and non-compete clauses, 6) Probation period terms. Contract should comply with labour laws. Oral contracts valid but written contracts provide clarity and protection.",
    
    # ==================== TAX LAW ====================
    "income_tax": "Income Tax Act 1961 levies tax on income of individuals, companies, and other entities. Provides for different tax slabs, exemptions, deductions, and assessment procedures.",
    
    "goods_services_tax": "Goods and Services Tax implemented through multiple Acts levies tax on supply of goods and services. GST rates vary from 0% to 28% based on product category and essentiality.",
    
    "customs_law": "Customs Act 1962 regulates import and export of goods. Levies customs duty on imported goods and provides procedures for clearance, warehousing, and duty drawback.",
    
    "central_excise": "Central Excise Act 1944 (now subsumed in GST) levied tax on manufacture of goods. Provided for registration, assessment, payment, and refund of excise duty.",
    
    "service_tax": "Service Tax (now subsumed in GST) was levied on specified services. Covered various services like telecommunications, banking, insurance, and professional services.",
    
    "wealth_tax": "Wealth Tax Act 1957 (abolished in 2015) levied tax on net wealth exceeding specified limit. Covered assets like house property, motor cars, jewellery, and cash.",
    
    "tax_procedures": "Tax procedures include registration, filing returns, assessment, payment of tax, appeals, and penalties. Different procedures apply for different taxes and categories of taxpayers.",
    
    # ==================== ENVIRONMENTAL LAW ====================
    "environment_protection": "Environment Protection Act 1986 provides framework for environmental protection. Empowers Centre to take measures for protecting and improving environment quality.",
    
    "pollution_control": "Water (Prevention and Control of Pollution) Act 1974 and Air (Prevention and Control of Pollution) Act 1981 establish pollution control boards and regulate water and air pollution.",
    
    "forest_conservation": "Forest Conservation Act 1980 restricts diversion of forest land for non-forest purposes. Requires prior approval of Central Government for diversion of forest land.",
    
    "wildlife_protection": "Wildlife Protection Act 1972 protects wild animals and birds. Provides for establishment of national parks, wildlife sanctuaries, and regulation of trade in wildlife products.",
    
    "coastal_regulation": "Coastal Regulation Zone Notification regulates activities in coastal areas. Classifies coastal areas into different zones with varying restrictions on construction and industrial activities.",
    
    "environmental_clearance": "Environmental Impact Assessment Notification requires environmental clearance for specified projects. Projects are categorized based on potential environmental impact.",
    
    "green_tribunal": "National Green Tribunal Act 2010 establishes specialized tribunal for environmental disputes. NGT has jurisdiction over environmental matters and can award compensation for environmental damage.",
    
    # ==================== ADMINISTRATIVE LAW ====================
    "administrative_law": "Administrative law governs functioning of administrative agencies. Principles include natural justice, reasonableness, proportionality, and procedural fairness in administrative actions.",
    
    "right_to_information": "Right to Information Act 2005 empowers citizens to seek information from public authorities. Promotes transparency and accountability in governance with time-bound response mechanism.",
    
    "public_interest_litigation": "Public Interest Litigation allows any citizen to approach courts for public causes. Relaxed standing requirements enable access to justice for marginalized sections and public causes.",
    
    "ombudsman": "Lokpal and Lokayuktas Act 2013 establishes Lokpal at Centre and Lokayuktas in states to investigate corruption complaints against public servants including Prime Minister and Chief Ministers.",
    
    "central_vigilance": "Central Vigilance Commission Act 2003 establishes CVC as apex integrity institution. CVC exercises superintendence over vigilance administration and investigates corruption in Central Government.",
    
    "service_law": "Government service is governed by service rules, conduct rules, and disciplinary procedures. Provides for recruitment, promotion, transfer, and disciplinary action against government employees.",
    
    # ==================== INFORMATION TECHNOLOGY LAW ====================
    "it_act": "Information Technology Act 2000 provides legal framework for electronic governance and e-commerce. Recognizes digital signatures, electronic records, and provides for cybercrimes and penalties.",
    
    "data_protection": "Personal Data Protection Bill (proposed) aims to protect personal data and privacy rights. Provides for data localization, consent requirements, and rights of data principals.",
    
    "electronic_governance": "Electronic governance involves use of IT for delivering government services. IT Act provides legal validity to electronic records and digital signatures for government transactions.",
    
    "cyber_security": "Cyber security involves protecting computer systems and networks from cyber attacks. IT Act provides for appointment of CERT-In as national nodal agency for cyber security.",
    
    "digital_india": "Digital India is government initiative to transform India into digitally empowered society. Focuses on digital infrastructure, digital literacy, and digital delivery of services.",
    
    # ==================== MOTOR VEHICLE LAW ====================
    "motor_vehicles_act": "Motor Vehicles Act 1988 regulates road transport vehicles. Covers licensing of drivers and vehicles, insurance, traffic rules, offenses, and accident compensation.",
    
    "driving_license": "Driving license application requires: 1) Form 1 application, 2) Age proof (18+ for car, 16+ for two-wheeler), 3) Address proof, 4) Medical certificate, 5) Passport photos, 6) Learning license (held for 30 days), 7) Driving test at RTO. Fees: ₹200 for two-wheeler, ₹500 for car. Valid for 20 years, renewable before expiry.",
    
    "driving_license_procedure": "Step-by-step process: 1) Apply for learner's license with documents, 2) Pass written test on traffic rules, 3) Practice driving for minimum 30 days, 4) Book slot for driving test, 5) Pass practical driving test, 6) Submit required documents and fees, 7) Get permanent driving license issued. Required documents: Form 1, age proof, address proof, medical certificate, passport photos.",
    
    "vehicle_insurance": "Motor vehicle insurance is mandatory under Motor Vehicles Act. Third-party insurance covers liability while comprehensive insurance covers own damage too.",
    
    "traffic_violations": "Traffic violations include speeding, signal jumping, drunk driving, and driving without license. Penalties include fines, license suspension, and imprisonment for serious offenses.",
    
    "accident_compensation": "Motor accident compensation is governed by Motor Vehicles Act. Compensation depends on injury severity, income loss, and degree of negligence. No-fault liability applies in certain cases.",
    
    # ==================== CONSUMER PROTECTION LAW ====================
    "consumer_rights": "Consumer Protection Act 2019 protects consumer rights including right to safety, information, choice, redressal, consumer education, and healthy environment.",
    
    "consumer_disputes": "Consumer disputes include defective goods, deficient services, unfair trade practices, and misleading advertisements. Three-tier redressal mechanism exists with district, state, and national commissions.",
    
    "product_liability": "Product liability provisions hold manufacturers, service providers, and sellers liable for harm caused by defective products or deficient services to consumers.",
    
    "e_commerce_protection": "E-commerce transactions are covered under Consumer Protection Act. Additional protections include return policies, grievance redressal, and liability of e-commerce platforms.",
    
    "consumer_complaint_filing": "Consumer complaint filing procedure: 1) File complaint within 2 years of cause of action, 2) Pay nominal fee (free up to ₹5 lakhs), 3) Attach purchase receipt and evidence, 4) Serve notice to opposite party, 5) Attend hearings, 6) Get compensation order. Can file online through e-daakhil portal. District forum for claims up to ₹1 crore, state commission up to ₹10 crore, national commission above ₹10 crore.",
    
    "defective_product_remedy": "Defective product remedies: 1) Replacement of defective product, 2) Refund of purchase price with interest, 3) Compensation for loss/injury, 4) Punitive damages for gross negligence, 5) Removal of defect at seller's cost. Evidence required: purchase receipt, warranty card, product photos, expert opinion, medical reports (if injury caused).",
    
    "service_deficiency_complaint": "Service deficiency includes: inadequate service, overcharging, delay, negligence, unfair practices. Examples: banking services, insurance, telecom, electricity, medical, education, transport. Remedies: service correction, compensation, refund, punitive damages. No need for lawyer in consumer forums.",
    
    # ==================== REAL ESTATE LAW ====================
    "real_estate_regulation": "Real Estate (Regulation and Development) Act 2016 regulates real estate sector. Mandates registration of projects, protects homebuyer interests, and establishes regulatory authorities.",
    
    "property_registration": "Property registration under Registration Act 1908 is mandatory for immovable property transactions above ₹100. Provides legal validity and prevents disputes.",
    
    "stamp_duty": "Stamp duty is levied on property transactions under Indian Stamp Act 1899. Rates vary by states and type of transaction. E-stamping facility is available in most states.",
    
    "property_purchase_procedure": "Property purchase procedure: 1) Verify title documents and ownership, 2) Check property approvals and clearances, 3) Conduct due diligence on encumbrances, 4) Negotiate price and terms, 5) Execute sale agreement, 6) Pay stamp duty and registration fees, 7) Register property at sub-registrar office, 8) Obtain registered sale deed. Essential documents: title deed, property tax receipts, NOC from society, building approvals.",
    
    "property_disputes": "Property disputes include: title disputes, boundary disputes, possession disputes, partition suits, landlord-tenant conflicts. Remedies: 1) File civil suit for declaration and possession, 2) Seek injunction to prevent interference, 3) Criminal complaint for trespass, 4) Mediation and arbitration. Evidence: title documents, survey records, possession proof, witness statements.",
    
    "landlord_tenant_rights": "Landlord-tenant rights under Rent Control Acts: Landlord rights: receive rent, evict for non-payment, recover possession for personal use. Tenant rights: peaceful enjoyment, protection from arbitrary eviction, fair rent fixation. Eviction grounds: non-payment of rent, subletting without consent, damage to property, personal necessity. Notice period varies by state (1-6 months).",
    
    "rent_agreement": "Rent agreement essentials: 1) Parties' details and property description, 2) Rent amount and payment terms, 3) Security deposit (usually 2-10 months rent), 4) Duration and renewal terms, 5) Maintenance responsibilities, 6) Termination conditions. Registration mandatory if rent exceeds ₹500/month or term exceeds 11 months. Stamp duty: 0.25% of annual rent in most states.",
    
    "property_inheritance": "Property inheritance laws: Hindu Succession Act 1956 governs Hindu inheritance. Legal heirs: spouse, children, parents. Equal rights for sons and daughters in ancestral property. Muslim inheritance follows Shariat law with specific shares. Christian inheritance under Indian Succession Act. Will can override succession laws. Succession certificate required for claiming assets.",
    
    "urban_land_ceiling": "Urban Land Ceiling and Regulation Act (repealed in most states) imposed ceiling on urban land holdings. Excess land was acquired by government for public purposes.",
    
    # ==================== BANKING AND FINANCE LAW ====================
    "banking_regulation": "Banking Regulation Act 1949 governs banking operations in India. RBI regulates banks through licensing, supervision, and monetary policy measures.",
    
    "sarfaesi_act": "Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act 2002 enables banks to recover secured loans without court intervention.",
    
    "debt_recovery": "Debt Recovery Tribunals established under Recovery of Debts Due to Banks and Financial Institutions Act 1993 provide speedy recovery mechanism for banks and financial institutions.",
    
    "negotiable_instruments": "Negotiable Instruments Act 1881 governs cheques, bills of exchange, and promissory notes. Cheque bounce is criminal offense under Section 138 with punishment up to 2 years.",
    
    "foreign_investment": "Foreign investment in India is regulated under FEMA 1999. FDI policy allows foreign investment in most sectors with sectoral caps and approval requirements in sensitive sectors.",
    
    # ==================== AGRICULTURAL LAW ====================
    "land_reforms": "Land reform laws vary by states and include land ceiling, tenancy regulation, and consolidation of holdings. Aim to ensure equitable distribution of agricultural land.",
    
    "agricultural_marketing": "Agricultural Produce Market Committee (APMC) Acts regulate marketing of agricultural produce. Recent farm laws aimed to liberalize agricultural marketing (now repealed).",
    
    "crop_insurance": "Pradhan Mantri Fasal Bima Yojana provides crop insurance to farmers against natural calamities, pests, and diseases. Premium is subsidized by government.",
    
    "water_rights": "Water rights are governed by state laws and Indian Easements Act. Riparian rights, prior appropriation, and beneficial use principles determine water allocation.",
    
    # ==================== EDUCATION LAW ====================
    "right_to_education": "Right to Education Act 2009 provides free and compulsory education to children aged 6-14 years. Mandates 25% reservation in private schools for economically weaker sections.",
    
    "higher_education": "Higher education is regulated by University Grants Commission, All India Council for Technical Education, and other regulatory bodies. Provides for establishment and recognition of universities.",
    
    "professional_education": "Professional education in medicine, engineering, law, and other fields is regulated by respective councils like Medical Council of India, Bar Council of India, etc.",
    
    # ==================== HEALTH LAW ====================
    "medical_negligence": "Medical negligence involves breach of duty of care by healthcare professionals. Compensation is available under Consumer Protection Act and tort law principles.",
    
    "drugs_control": "Drugs and Cosmetics Act 1940 regulates manufacture, sale, and distribution of drugs and cosmetics. Central and state drug controllers ensure compliance with quality standards.",
    
    "clinical_trials": "Clinical trials are regulated by Central Drugs Standard Control Organization. Good Clinical Practice guidelines ensure ethical conduct and participant safety in trials.",
    
    "mental_health": "Mental Healthcare Act 2017 protects rights of persons with mental illness. Provides for advance directives, nominated representatives, and prohibition of unmodified electroconvulsive therapy.",
    
    # ==================== MEDIA AND ENTERTAINMENT LAW ====================
    "press_freedom": "Press freedom is protected under Article 19(1)(a) but subject to reasonable restrictions. Press Council of India regulates print media and ensures journalistic ethics.",
    
    "broadcasting_law": "Broadcasting is regulated by Ministry of Information and Broadcasting. Cable Television Networks Act and Telecom Regulatory Authority regulate cable and DTH services.",
    
    "film_certification": "Cinematograph Act 1952 provides for film certification by Central Board of Film Certification. Films are certified as U, U/A, A, or S based on content.",
    
    "advertising_standards": "Advertising Standards Council of India regulates advertising content. Consumer Protection Act also covers misleading advertisements and unfair trade practices.",
    
    # ==================== SPORTS LAW ====================
    "sports_governance": "Sports governance involves regulation of sports federations, anti-doping measures, and dispute resolution. Sports Code provides guidelines for national sports federations.",
    
    "anti_doping": "National Anti-Doping Agency (NADA) implements anti-doping measures in Indian sports. World Anti-Doping Code is followed for testing and sanctions.",
    
    "sports_disputes": "Sports disputes are resolved through Sports Authority of India, national federations, and Court of Arbitration for Sport. Alternative dispute resolution is preferred.",
    
    # ==================== DISASTER MANAGEMENT LAW ====================
    "disaster_management": "Disaster Management Act 2005 provides for disaster management at national, state, and district levels. Establishes National Disaster Management Authority headed by Prime Minister.",
    
    "emergency_powers": "Emergency powers during disasters include evacuation, requisition of resources, and regulation of movement. Compensation is provided for loss of life and property.",
    
    # ==================== TRIBAL AND MINORITY RIGHTS ====================
    "scheduled_tribes": "Scheduled Tribes are protected under Fifth and Sixth Schedules of Constitution. Special provisions include reservation in education and employment, and protection of land rights.",
    
    "forest_rights": "Scheduled Tribes and Other Traditional Forest Dwellers Act 2006 recognizes forest rights of tribal communities. Provides for individual and community forest resource rights.",
    
    "minority_rights": "Religious and linguistic minorities are protected under Articles 29-30. National Commission for Minorities investigates complaints and recommends measures for minority welfare.",
    
    "scheduled_castes": "Scheduled Castes are protected under constitutional provisions and Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act 1989. Special courts try atrocity cases.",
    
    # ==================== WOMEN AND CHILD RIGHTS ====================
    "women_rights": "Women's rights are protected through various laws including Domestic Violence Act, Sexual Harassment Act, and Maternity Benefit Act. National Commission for Women promotes women's rights.",
    
    "child_rights": "Child rights are protected under Juvenile Justice Act 2015, POCSO Act 2012, and Child Labour (Prohibition and Regulation) Act 1986. National Commission for Protection of Child Rights monitors implementation.",
    
    "human_trafficking": "Human trafficking is criminalized under Immoral Traffic (Prevention) Act 1956 and IPC provisions. Trafficking includes forced labor, sexual exploitation, and organ harvesting.",
    
    # ==================== SENIOR CITIZENS RIGHTS ====================
    "elderly_rights": "Maintenance and Welfare of Parents and Senior Citizens Act 2007 mandates children to maintain elderly parents. Provides for maintenance tribunals and old age homes.",
    
    # ==================== DISABILITY RIGHTS ====================
    "disability_rights": "Rights of Persons with Disabilities Act 2016 ensures equal opportunities and non-discrimination. Provides for accessibility, education, employment, and social security rights.",
    
    # ==================== INTERNATIONAL LAW ====================
    "extradition": "Extradition Act 1962 provides for extradition of fugitive criminals to foreign countries. India has extradition treaties with various countries for mutual legal assistance.",
    
    "diplomatic_immunity": "Diplomatic Relations (Vienna Convention) Act 1972 provides diplomatic immunity to foreign diplomats. Covers immunity from jurisdiction and inviolability of diplomatic premises.",
    
    "foreign_awards": "Foreign Awards (Recognition and Enforcement) Act 1961 provides for recognition and enforcement of foreign arbitral awards in India based on reciprocity principle.",
    
    # ==================== DRIVING LICENCE & VEHICLE LAWS ==============
    "driving_licence": "A driving licence is an official government document that permits a person to legally drive motor vehicles on Indian roads. It is issued by the Regional Transport Office (RTO) after verifying eligibility, documents, and driving skills.",
    
    "types_driving_licence": "India issues licences based on vehicle class such as two-wheeler (with gear/without gear), four-wheeler LMV, transport/commercial vehicles, heavy motor vehicles, e-rickshaw, tractor, and special category vehicles. Each class allows driving only that specific vehicle type.",
    
    "learners_licence_eligibility": "A learner's licence (LL) can be obtained at age 16 for gearless 50cc two-wheelers, 18 for LMV (car/bike), and 20 for commercial vehicles. Applicants must know basic traffic rules and pass the LL test.",
    
    "driving_licence_documents": "Common documents include Aadhaar or ID proof, age proof, address proof, passport-size photos, medical certificate (Form 1A for transport vehicles), and application forms. States may ask for additional documents if needed.",
    
    "dl_renewal": "DL renewal is done online or at the RTO by submitting the renewal form, medical certificate, old DL, photos, and fee. After verification, the renewed licence is issued digitally or physically.",
    
    "duplicate_driving_licence": "A duplicate licence is issued if the original is lost, stolen, or damaged. The applicant submits an FIR (if lost), ID proof, address proof, application form, and pays the fee to get a fresh copy.",
    
    "driving_licence_fees": "Fees vary by state but generally include application fee, test fee, slot booking charges, smart card fee, and renewal charges. Transport licences have higher fees than personal licences.",
    
    "driving_test_process": "LL test is an online or written test on traffic signs and rules. DL test is a practical riding/driving test where the RTO inspector checks control, road sense, and maneuvering skills.",
    
    "driving_forms": "Form 1 is a self-declaration of physical fitness. Form 1A is a medical certificate signed by a registered doctor. Form 4 is the main application form for driving licence issuance.",
    
    "slot_booking_problems": "Slot booking failures usually happen due to high traffic, server issues, or lack of available dates. Trying during non-peak hours or switching RTOs often solves the issue.",
    
    # ==================== TRAFFIC & VEHICLE REGULATIONS ==============
    "challan_types": "Challans include traffic rule violation challans, e-challans issued through cameras, spot challans by police, court challans requiring appearance, and vehicle-related challans like PUC or insurance lapses.",
    
    "echallan": "An e-challan is a digital traffic ticket issued through CCTV, ANPR cameras, or handheld devices. It records the offence, vehicle number, and fine, which can be paid online.",
    
    "check_challan_online": "Challans can be checked on Parivahan portal or state transport websites by entering vehicle number, DL number, or challan number. Details of offence and payment options appear instantly.",
    
    "motor_vehicles_act": "The Motor Vehicles Act, 1988 regulates road safety, traffic rules, vehicle registration, licences, penalties, and transport regulations across India. It is the primary law governing vehicles in the country.",
    
    "no_parking_fine": "No Parking fines vary by state but generally range from ₹200–₹1000. Repeat violations or towing charges may increase the total payable amount.",
    
    "overspeeding_penalty": "Overspeeding attracts penalties from ₹1000 to ₹4000 depending on vehicle type and speed limit. High-speed cases may also involve license suspension.",
    
    "triple_riding_penalty": "Triple riding on a two-wheeler is illegal and usually fined ₹500–₹2000 depending on state rules. It is treated as a safety violation.",
    
    "puc_rules": "A valid Pollution Under Control (PUC) certificate is mandatory for all vehicles. It checks carbon emissions and must be renewed every 3–12 months based on vehicle type and fuel.",
    
    "rc_renewal": "Registration Certificate (RC) must be renewed after 15 years and then every 5 years. The vehicle is inspected for fitness before renewal.",
    
    "vehicle_ownership_transfer": "Ownership transfer is done by submitting Form 29 & 30, buyer and seller details, insurance copy, PUC, and RC at the RTO. A new RC is issued in the buyer's name.",
    
    # ==================== POLICE & FIR ==============
    "fir": "An FIR (First Information Report) is a written complaint registered by police for cognizable offences. It starts the formal criminal investigation process.",
    
    "fir_compulsory": "Police must register an FIR when a cognizable offence occurs—like theft, assault, accident causing injury, cheating, or serious crimes—without delay.",
    
    "online_fir": "Many states allow online FIR or e-FIR through police portals. Users fill details, upload evidence, and receive an acknowledgement number.",
    
    "fir_vs_complaint": "An FIR is for serious (cognizable) offences and leads to immediate investigation. A complaint is for minor (non-cognizable) offences and may require a court order to investigate.",
    
    "police_complaint_types": "Complaints include general complaints, cyber complaints, missing person reports, domestic violence complaints, and anonymous reports depending on the issue.",
    
    "zero_fir": "Zero FIR is filed at any police station regardless of jurisdiction. It is later transferred to the correct station, ensuring no delay in reporting serious crimes.",
    
    "police_refuse_fir": "A complaint can be escalated to higher police officers, Superintendent of Police, or filed directly before a Magistrate under Section 156(3) CrPC.",
    
    "fir_copy": "A copy of FIR is free and can be obtained from the police station or downloaded from the state police website using FIR number.",
    
    "ncr": "NCR (Non-Cognizable Report) is recorded for minor offences where arrest cannot be made without court order. Police prepare a report but investigation needs court approval.",
    
    "bailable_nonbailable": "Bailable offences allow bail as a matter of right, while non-bailable offences require court discretion. The severity of the crime determines the category.",
    
    # ==================== INDIAN CONSTITUTION (ENHANCED) ==============
    "fundamental_duties": "These duties require citizens to respect the Constitution, protect national symbols, promote harmony, safeguard environment, and follow civic responsibilities.",
    
    "directive_principles": "Directive Principles guide the government to create welfare policies like equal pay, health care, education, and social justice, though they are not legally enforceable.",
    
    "article_14": "Article 14 ensures equal protection of laws and prohibits discrimination on any grounds. It promotes fairness in government action.",
    
    "article_19": "This right provides freedom of speech, movement, residence, profession, and assembly, subject to reasonable restrictions for public interest.",
    
    "article_21": "Article 21 protects life and personal liberty. It includes rights like privacy, clean environment, dignity, and fair procedure.",
    
    "article_21a": "This guarantees free and compulsory education to children aged 6–14 years as a fundamental right introduced via the 86th Amendment.",
    
    "emergency_provisions": "The Constitution allows National, State, and Financial emergencies during security threats or breakdown of governance. Powers shift to the Centre temporarily.",
    
    "president_powers": "The President has executive, legislative, judicial, diplomatic, and emergency powers including ordinance-making and pardoning authority.",
    
    "supreme_court_powers": "The Supreme Court has original, appellate, and advisory jurisdiction. It protects fundamental rights and acts as the final interpreter of the Constitution.",
    
    # ==================== PROPERTY & RENT ==============
    "rent_agreement": "A rent agreement is a legal contract between landlord and tenant defining rent amount, duration, responsibilities, and property terms.",
    
    "registered_notarized_agreement": "Registered agreements are legally stronger and recorded with the Registrar, while notarized agreements only certify signatures and have limited legal weight.",
    
    "lease_vs_rent": "Lease is long-term (usually 11+ months to years) with strong protections and fixed terms. Rent agreements are shorter and more flexible.",
    
    "noc": "NOC (No Objection Certificate) is a written declaration permitting a person to undertake a particular action without objection from the issuing authority.",
    
    "property_tax": "Property tax is levied by municipal authorities on owned property based on size, usage, location, and built-up area.",
    
    "mutation_property": "Mutation updates ownership details in land records after sale, inheritance, gift, or transfer to show the new owner for revenue purposes.",
    
    "gift_deed": "A gift deed transfers property ownership voluntarily without money. It must be registered and stamped to be legally valid.",
    
    "rent_agreement_tenure": "Most rent agreements are made for 11 months to avoid mandatory registration, though parties may choose longer periods.",
    
    "security_deposit": "Security deposit is usually 1–6 months' rent depending on state. It must be refunded after deductions for damages, if any.",
    
    "eviction_notice": "Landlords must give 15–30 days' notice depending on contract terms. Court eviction may be needed in disputes.",
    
    # ==================== CYBER CRIME ==============
    "cyber_fraud": "Cyber fraud involves cheating through digital means such as phishing, fake links, UPI scams, identity theft, and online impersonation.",
    
    "report_cybercrime": "Complaints can be filed at cybercrime.gov.in or the nearest cyber cell. Victims can also call the national helpline for quick action.",
    
    "helpline_1930": "1930 is India's national cyber fraud helpline used to stop and freeze fraudulent transactions quickly before money is withdrawn.",
    
    "online_payment_fraud": "Victims should immediately call 1930, report on the cyber portal, save evidence, inform the bank, and avoid deleting messages or screenshots.",
    
    "cyberstalking": "Cyberstalking involves repeated online harassment, tracking, threats, or unwanted communication causing fear or disturbance.",
    
    "otp_fraud": "Never share OTPs with anyone, even claiming to be bank officials. Use official apps, avoid unknown links, and enable two-step authentication.",
    
    "upi_fraud": "Banks treat UPI fraud as unauthorized transactions if reported quickly. Users are protected under RBI guidelines for zero-liability cases.",
    
    "social_media_harassment": "Online abuse, threats, or obscene messages can be reported under IT Act and IPC. Police and cyber cells can take action.",
    
    # ==================== COURT & LEGAL PROCEDURES ==============
    "legal_notice": "A legal notice is a formal written communication informing the opposite party of a dispute and demanding resolution before approaching court.",
    
    "chargesheet": "A chargesheet is the police report filed after investigation detailing evidence, accused details, and charges to be tried in court.",
    
    "cognizable_noncognizable": "Cognizable offences allow police to arrest without warrant; non-cognizable offences require court permission to investigate.",
    
    "anticipatory_bail": "Anticipatory bail protects a person from arrest in a non-bailable offence in case they fear arrest.",
    
    "court_hierarchy": "Supreme Court → High Courts → District Courts → Magistrate Courts. Cases escalate through appeals at each level.",
    
    "limitation_period": "It is the legally prescribed time within which a case must be filed. After expiry, courts may not accept the case unless special reasons exist.",
    
    "lok_adalat": "Lok Adalat is a people's court that settles disputes quickly and mutually without lengthy court procedures.",
    
    "fake_lawyers": "Check bar registration number, state bar council ID, and certificate of practice. Genuine lawyers appear in official bar council lists.",
    
    "affidavit": "An affidavit is a sworn written statement confirmed by oath, used as evidence in legal matters.",
    
    "stamp_paper": "Stamp papers do not expire, but documents executed on them must meet legal requirements. Old stamp papers can still be used.",
    
    "court_summons": "A court summons is an official order requiring a person to appear in court on a specific date for testimony or proceedings.",
    
    "arbitration": "Arbitration is an alternative dispute resolution method where an appointed arbitrator settles disputes outside traditional courts."
}

# Additional specialized legal areas (this is a duplicate definition - the main one is at the top)

def get_comprehensive_legal_info(query: str) -> str:
    """Get comprehensive legal information for any query"""
    query_lower = query.lower().strip()
    
    # Exact phrase matching first (highest priority)
    exact_matches = {
        # Motor Vehicle
        "how to apply for driving license": "driving_license",
        "driving license application": "driving_license", 
        "driving license procedure": "driving_license_procedure",
        "how to get driving license": "driving_license",
        "dl application": "driving_license",
        
        # Criminal Law
        "how to file fir": "fir_filing",
        "how to file a fir": "fir_filing",
        "fir filing procedure": "fir_filing",
        "file police complaint": "police_complaint",
        "how to register fir": "fir_filing",
        "police complaint procedure": "police_complaint",
        
        # Family Law
        "how to file divorce": "divorce_procedure",
        "divorce procedure": "divorce_procedure",
        "mutual consent divorce": "mutual_consent_divorce",
        "contested divorce": "contested_divorce",
        "how to get alimony": "alimony_maintenance",
        "child custody": "child_custody_divorce",
        "child maintenance": "child_maintenance",
        
        # Property Law
        "how to buy property": "property_purchase_procedure",
        "property registration": "property_registration",
        "rent agreement": "rent_agreement",
        "landlord tenant dispute": "landlord_tenant_rights",
        "property dispute": "property_disputes",
        
        # Employment Law
        "wrongful termination": "job_termination",
        "pf withdrawal": "pf_withdrawal",
        "gratuity claim": "gratuity_claim",
        "salary dispute": "salary_disputes",
        "workplace harassment": "workplace_harassment",
        
        # Consumer Law
        "consumer complaint": "consumer_complaint_filing",
        "defective product": "defective_product_remedy",
        "service deficiency": "service_deficiency_complaint"
    }
    
    # Check exact phrase matches first
    for phrase, key in exact_matches.items():
        if phrase in query_lower:
            if key in COMPREHENSIVE_LEGAL_FAQ:
                return COMPREHENSIVE_LEGAL_FAQ[key]
            elif key in SPECIALIZED_LEGAL_AREAS:
                return SPECIALIZED_LEGAL_AREAS[key]
    
    # Keyword-based matching (more precise)
    keyword_mappings = {
        # Motor Vehicle
        "driving license": "driving_license",
        "driving licence": "driving_license", 
        "dl": "driving_license",
        
        # Criminal Law
        "fir": "fir_filing",
        "first information report": "fir_filing",
        "police complaint": "police_complaint",
        "bail": "bail",
        "arrest": "bail",
        "detention": "bail",
        "custody": "bail",
        
        # Family Law
        "divorce": "divorce_procedure",
        "alimony": "alimony_maintenance",
        "maintenance": "alimony_maintenance",
        "child custody": "child_custody_divorce",
        "custody": "child_custody_divorce",
        
        # Property Law
        "property": "property_purchase_procedure",
        "rent": "rent_agreement",
        "landlord": "landlord_tenant_rights",
        "tenant": "landlord_tenant_rights",
        "inheritance": "property_inheritance",
        
        # Employment Law
        "termination": "job_termination",
        "pf": "pf_withdrawal",
        "provident fund": "pf_withdrawal",
        "gratuity": "gratuity_claim",
        "salary": "salary_disputes",
        "harassment": "workplace_harassment",
        
        # Consumer Law
        "consumer": "consumer_complaint_filing",
        "defective": "defective_product_remedy",
        
        # Administrative Law
        "rti": "right_to_information",
        "right to information": "right_to_information"
    }
    
    # Check keyword mappings
    for keyword, key in keyword_mappings.items():
        if keyword in query_lower:
            if key in COMPREHENSIVE_LEGAL_FAQ:
                return COMPREHENSIVE_LEGAL_FAQ[key]
            elif key in SPECIALIZED_LEGAL_AREAS:
                return SPECIALIZED_LEGAL_AREAS[key]
    
    # Fallback to original broad search (lowest priority)
    for key, value in COMPREHENSIVE_LEGAL_FAQ.items():
        # More restrictive matching - require at least 2 character overlap
        key_words = key.split('_')
        if any(word in query_lower and len(word) > 2 for word in key_words):
            return value
    
    # Search in specialized areas
    for key, value in SPECIALIZED_LEGAL_AREAS.items():
        key_words = key.split('_')
        if any(word in query_lower and len(word) > 2 for word in key_words):
            return value
    
    return None
