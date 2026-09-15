#!/usr/bin/env python3
"""生成 21 条参考文献的 RIS 文件（供 Zotero 一键导入；Zotero 本地 API 未启用，故不代写库）。
数据源：07_参考文献清单.md（卷期页已由 PubMed 核验）
输出：/Users/mac/Desktop/文稿库/人工智能临床应用/参考文献_21条_P2.ris
"""
import pathlib, re

ART = pathlib.Path("/Users/mac/Desktop/文稿库/人工智能临床应用")
md7 = (ART / "07_参考文献清单.md").read_text()

def val(pat, s, default=""):
    m = re.search(pat, s)
    return m.group(1).strip() if m else default

# 元数据表（与 07 清单一一对应；title/journal/year/vol/issue/pages/doi/authors 均已核验）
REFS = [
 ("Van Gelder IC","Rienstra M","Bunting KV","2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the European Association for Cardio-Thoracic Surgery (EACTS)","Eur Heart J","2024","45","36","3314-3414","10.1093/eurheartj/ehae176","JOUR"),
 ("Perez MV","Mahaffey KW","Hedlin H","Large-Scale Assessment of a Smartwatch to Identify Atrial Fibrillation","N Engl J Med","2019","381","20","1909-1917","10.1056/NEJMoa1901183","JOUR"),
 ("Lubitz SA","Faranesh AZ","Selvaggi C","Detection of Atrial Fibrillation in a Large Population Using Wearable Devices: The Fitbit Heart Study","Circulation","2022","146","19","1415-1424","10.1161/CIRCULATIONAHA.122.060291","JOUR"),
 ("Attia ZI","Noseworthy PA","Lopez-Jimenez F","An artificial intelligence-enabled ECG algorithm for the identification of patients with atrial fibrillation during sinus rhythm: a retrospective analysis of outcome prediction","Lancet","2019","394","10201","861-867","10.1016/S0140-6736(19)31721-0","JOUR"),
 ("Healey JS","Lopes RD","Granger CB","Apixaban for Stroke Prevention in Subclinical Atrial Fibrillation","N Engl J Med","2024","390","2","107-117","10.1056/NEJMoa2310234","JOUR"),
 ("Kirchhof P","Toennis T","Goette A","Anticoagulation with Edoxaban in Patients with Atrial High-Rate Episodes","N Engl J Med","2023","389","13","1167-1179","10.1056/NEJMoa2303062","JOUR"),
 ("Guo Y","Lane DA","Wang L","Mobile Health Technology to Improve Care for Patients With Atrial Fibrillation","J Am Coll Cardiol","2020","75","13","1523-1534","10.1016/j.jacc.2020.01.052","JOUR"),
 ("Guo Y","Corica B","Romiti GF","Mobile health technology integrated care in atrial fibrillation patients with diabetes mellitus in China: A subgroup analysis of the mAFA-II cluster randomized clinical trial","Eur J Clin Invest","2023","53","9","e14031","10.1111/eci.14031","JOUR"),
 ("Collins GS","Moons KGM","Dhiman P","TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods","BMJ","2024","385","","e078378","10.1136/bmj-2023-078378","JOUR"),
 ("Wolff RF","Moons KGM","Riley RD","PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies","Ann Intern Med","2019","170","1","51-58","10.7326/M18-1376","JOUR"),
 ("Zech JR","Badgeley MA","Liu M","Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study","PLoS Med","2018","15","11","e1002683","10.1371/journal.pmed.1002683","JOUR"),
 ("Clifford GD","Liu C","Moody B","AF classification from a short single lead ECG recording: the PhysioNet/Computing in Cardiology Challenge 2017","2017 Computing in Cardiology (CinC)","2017","44","","1-4","10.22489/CinC.2017.065-469","CPAPER"),
 ("Wang Y","Liu S","Jia H","A two-step method for paroxysmal atrial fibrillation event detection based on machine learning","Math Biosci Eng","2022","19","10","9877-9894","10.3934/mbe.2022460","JOUR"),
 ("Zhao Z","Li Q","Li S","Evaluation of an algorithm-guided photoplethysmography for atrial fibrillation burden using a smartwatch","Pacing Clin Electrophysiol","2024","47","4","511-517","10.1111/pace.14951","JOUR"),
 ("Zuo S","Wang J","Wang X","A Dual-Modal Wearable PPG Smartwatch with AI-Enhanced Correction for High-Accuracy and Continuous AF Burden Assessment","Adv Sci (Weinh)","2026","","","e76627","10.1002/advs.76627","JOUR"),
 ("Armoundas AA","Avari Silva JN","Baykaner T","HRS scientific statement on artificial intelligence integration framework into clinical electrophysiology workflows","Heart Rhythm","2026","23","9","e2235-e2250","10.1016/j.hrthm.2026.04.013","JOUR"),
 ("Pundi K","Gandotra C","Sanders W","Considerations for using atrial fibrillation burden as a surrogate endpoint: A report from the Cardiovascular Sciences Research Consortium","Am Heart J","2026","301","","107516","10.1016/j.ahj.2026.107516","JOUR"),
 ("Wachter R","Haag P","Uhe T","Catheter ablation for symptomatic atrial fibrillation (PVI-SHAM-AF): a randomised, double-blind, sham-controlled, multicentre trial","Lancet","2026","408","10559","999-1009","10.1016/S0140-6736(26)01558-8","JOUR"),
 ("Wagner P","Strodthoff N","Bousseljot R","PTB-XL, a large publicly available electrocardiography dataset (version 1.0.3)","PhysioNet","2022","","","","10.13026/kfzx-aw45","DATA"),
 ("Clifford GD","Liu C","Moody B","AF Classification from a Short Single Lead ECG Recording: The PhysioNet/Computing in Cardiology Challenge 2017 (version 1.0.0)","PhysioNet","2017","","","","10.13026/d3hm-sf11","DATA"),
 ("Wang X","Ma C","Zhang X","Paroxysmal Atrial Fibrillation Events Detection from Dynamic ECG Recordings: The 4th China Physiological Signal Challenge 2021 (version 1.0.0)","PhysioNet","2021","","","","10.13026/ksya-qw89","DATA"),
]

lines = []
for (a1, a2, a3, title, journal, year, vol, iss, pages, doi, typ) in REFS:
    lines += [f"TY  - {typ}", f"TI  - {title}",
              f"AU  - {a1}", f"AU  - {a2}", f"AU  - {a3}", "AU  - et al.",
              f"JO  - {journal}", f"PY  - {year}"]
    if vol:   lines.append(f"VL  - {vol}")
    if iss:   lines.append(f"IS  - {iss}")
    if pages: lines.append(f"SP  - {pages}")
    if doi:   lines.append(f"DO  - {doi}")
    if typ == "DATA":
        lines.append("PB  - PhysioNet"); lines.append("ET  - 1")
    lines.append("ER  - ")
    lines.append("")

out = ART / "参考文献_21条_P2.ris"
out.write_text("\n".join(lines))
print("saved:", out, "| 条目数:", len(REFS))
