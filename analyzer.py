import re

# CBC
# -------------------------
# CBC ANALYSIS
# -------------------------
def analyze_cbc(text):
    result = []
    explanation = []

    def extract(pattern):
        match = re.search(pattern, text)
        return float(match.group(1).replace(',', '')) if match else None

    # Hemoglobin
    hb = extract(r'(?:hb|hemoglobin|haemoglobin)[^\d]{0,10}([0-9]+\.?[0-9]*)')
    if hb:
        if hb < 12:
            result.append(f"Hemoglobin LOW ({hb} g/dL)")
            explanation.append("Low Hb → anemia, weakness")
        else:
            result.append(f"Hemoglobin NORMAL ({hb} g/dL)")

    # WBC
    wbc = extract(r'(?:wbc|leucocytes)[^\d]{0,10}([0-9,]+)')
    if wbc:
        wbc = int(wbc)
        if wbc > 10000:
            result.append(f"WBC HIGH ({wbc})")
            explanation.append("High WBC → infection")
        else:
            result.append(f"WBC NORMAL ({wbc})")

    # Platelets
    platelets = extract(r'(?:platelets)[^\d]{0,10}([0-9,]+)')
    if platelets:
        platelets = int(platelets)
        if platelets < 150000:
            result.append(f"Platelets LOW ({platelets})")
            explanation.append("Low platelets → dengue risk")
        else:
            result.append(f"Platelets NORMAL ({platelets})")

    return result, explanation


# -------------------------
# SUGAR TEST
# -------------------------
def analyze_sugar(text):
    result = []
    explanation = []

    sugar = re.search(r'(?:glucose|sugar)[^\d]{0,10}([0-9]+)', text)
    if sugar:
        value = int(sugar.group(1))

        if value < 70:
            result.append(f"Sugar LOW ({value})")
            explanation.append("Low sugar → hypoglycemia")
        elif value > 140:
            result.append(f"Sugar HIGH ({value})")
            explanation.append("High sugar → diabetes risk")
        else:
            result.append(f"Sugar NORMAL ({value})")

    return result, explanation


# -------------------------
# LIVER FUNCTION
# -------------------------
def analyze_liver(text):
    result = []
    explanation = []

    bilirubin = re.search(r'bilirubin[^\d]{0,10}([0-9.]+)', text)
    if bilirubin:
        value = float(bilirubin.group(1))
        if value > 1.2:
            result.append(f"Bilirubin HIGH ({value})")
            explanation.append("Liver issue or jaundice")
        else:
            result.append(f"Bilirubin NORMAL ({value})")

    return result, explanation


# -------------------------
# KIDNEY FUNCTION
# -------------------------
def analyze_kidney(text):
    result = []
    explanation = []

    creatinine = re.search(r'creatinine[^\d]{0,10}([0-9.]+)', text)
    if creatinine:
        value = float(creatinine.group(1))
        if value > 1.3:
            result.append(f"Creatinine HIGH ({value})")
            explanation.append("Kidney stress")
        else:
            result.append(f"Creatinine NORMAL ({value})")

    return result, explanation


# -------------------------
# DISEASE DETECTION (VALUE-BASED ONLY)
# -------------------------
def analyze_diseases(text):
    result = []
    explanation = []

    # Dengue via platelets
    platelets = re.search(r'platelets[^\d]{0,10}([0-9,]+)', text)
    if platelets:
        value = int(platelets.group(1).replace(',', ''))
        if value < 100000:
            result.append("Possible Dengue Pattern")
            explanation.append("Low platelets detected")

    # Infection via WBC
    wbc = re.search(r'(?:wbc|leucocytes)[^\d]{0,10}([0-9,]+)', text)
    if wbc:
        value = int(wbc.group(1).replace(',', ''))
        if value > 12000:
            result.append("Possible Infection")
            explanation.append("High WBC count")

    return result, explanation


# -------------------------
# MAIN ANALYZER (CALL ALL)
# -------------------------
def analyze_report(text):

    text = text.lower()

    final_result = []
    final_explanation = []

    functions = [
        analyze_cbc,
        analyze_sugar,
        analyze_liver,
        analyze_kidney,
        analyze_diseases
    ]

    for func in functions:
        r, e = func(text)
        final_result.extend(r)
        final_explanation.extend(e)

    if not final_result:
        final_result.append("No major abnormality detected. Your Reports are Normal")

    final_explanation.append("⚠️ This is an automated analysis. Consult your doctor.")

    return final_result, final_explanation


