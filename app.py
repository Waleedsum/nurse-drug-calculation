
import streamlit as st
import openai
import os

# =========================
# OpenAI Setup
# =========================
openai.api_key = os.getenv("OPENAI_API_KEY")

# =========================
# App Config
# =========================
st.set_page_config(
    page_title="AI Drug Calculator",
    page_icon="💊",
    layout="centered"
)
st.title("💊 AI Drug Calculator 👩‍🚀")
st.markdown("**Educational use only – follow hospital protocols**")
st.markdown("---")

# =========================
# Drug Database
# =========================
DRUGS = {
    "Dopamine": {"type": "inotrope"},
    "Dobutamine": {"type": "inotrope"},
    "Epinephrine": {"type": "inotrope"},
    "Fentanyl": {"type": "sedative"},
    "Propofol": {"type": "sedative"},
    "Midazolam": {"type": "sedative"},
    "Esmron or Rocuronium": {"type": "muscle_relaxant"},
    "Atracurium": {"type": "muscle_relaxant"}
}

TIME_MANDATORY_DRUGS = ["Dopamine", "Dobutamine", "Epinephrine"]

drug_tips = {
    "dopamine": "Ensure IV access is patent and monitor blood pressure closely.",
    "dobutamine": "Titrate gradually according to cardiac output and BP.",
    "epinephrine": "Prefer central line; peripheral acceptable short-term in emergencies.",
    "fentanyl": "Use 2 ampules (1000 mcg) + 30–40 mL NS in a 50 mL syringe.",
    "propofol": "Use 2 ampules (400 mg) = 40 ml in a 50 mL syringe.",
    "midazolam": "Use 3 ampules (45 mg): 9 mL drug + 36 mL NS → total 45 mg in 45 mL.",
    "rocuronium": "Ensure adequate sedation before paralysis. Use 5 ampules = 250 mg in 50 mL.",
    "esmron": "Same preparation as Rocuronium.",
    "atracurium": "Watch for hypotension and histamine release. Use 4 ampules (100 mg) + 40 mL NS.",
    "other": "Ensure dose and stock use the same units.",
    "Caution": "🛑Always follow up your hospital policies and procedures🛑"

}

# =========================
# AI Functions
# =========================
def ask_ai(drug, result, tip, calculation_type):
    prompt = f"""
You are an ICU clinical assistant.
Calculation type: {calculation_type}
Drug/Fluid: {drug}
Result: {result}
Clinical tip: {tip}
Explain clearly how this result is interpreted clinically.
Mention safety considerations.
Do NOT use formulas or code.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response["choices"][0]["message"]["content"]

def generate_med_policy(drug_name):
    prompt = f"""
You are an ICU clinical assistant.
Provide a detailed medication policy for: {drug_name}
Include:
- Clinical safety considerations
- Preparation guidance
- Administration tips
- Monitoring
Do NOT provide dose calculations.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response["choices"][0]["message"]["content"]

# =========================
# Calculation Engine
# =========================
def calculate_infusion(drug, dose, weight, stock, volume, time_min=None):
    if None in (dose, stock, volume):
        return None, None
    if drug in TIME_MANDATORY_DRUGS:
        if None in (weight, time_min) or time_min <= 0:
            return None, None
        total_ml = (dose * weight * volume * time_min) / (stock * 1000)
        return round(total_ml, 2), "mL (total)"
    if not time_min:
        return round((dose * volume) / stock, 2), "mL/hr"
    return round((dose * volume * time_min) / stock, 2), "mL (total)"

def calculate_parenteral(dose, stock, volume, weight=None):
    return (dose * weight / stock) * volume if weight else (dose / stock) * volume

def calculate_oral(dose, stock, volume, weight=None):
    return (dose * weight / stock) * volume if weight else (dose / stock) * volume

def calculate_tablet(dose, stock):
    return dose / stock

def calculate_iv_gravity(volume, drop_factor, time_value, time_unit="minutes"):
    if time_value <= 0:
        return None
    time_min = time_value * 60 if time_unit == "hours" else time_value
    return (volume * drop_factor) / time_min

def calculate_iv_pump(volume, time_hours):
    return volume / time_hours if time_hours > 0 else None


# Nurse Assistant Chat (BELOW RESULTS)
# =========================
st.markdown("---")
st.markdown("## 🤖 Nurse Assistant Chat")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def is_greeting(text):
    return text.strip().lower() in ["hi", "hello", "hey", "start"]

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Type Hi to start, or medication name, or question and press Enter 👩‍🚀:",
        key="chat_input"
    )
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.chat_history.append(("user", user_input))

    if is_greeting(user_input):
        st.session_state.chat_history.append(
            ("bot",
             "👋 Hello Nurse!\n\n"
             "I can explain medication policies.\n"
             "👉 Type a medication name to continue.")
        )
    else:
        tip = drug_tips.get(user_input.lower(), drug_tips["Caution"])
        st.session_state.chat_history.append(
            ("bot", f"🩺 Database Tip for **{user_input}**:\n{tip}")
        )
        policy = generate_med_policy(user_input)
        st.session_state.chat_history.append(
            ("bot", f"### 📄 Explain Medication Policy\n{policy}")
        )

# Display chat (scrollable, bottom-up)
chat_html = """
<div style='
    max-height:400px;
    overflow-y:auto;
    border:1px solid #ddd;
    padding:10px;
    border-radius:10px;
'>
"""
for role, msg in st.session_state.chat_history:
    if role == "bot":
        chat_html += f"<p><b>🤖 Bot:</b> {msg}</p>"
    else:
        chat_html += f"<p><b>👩‍⚕️ Nurse:</b> {msg}</p>"
chat_html += "</div>"

st.markdown(chat_html, unsafe_allow_html=True)



# =========================
# Tabs A–F
# =========================
tabs = st.tabs([
    "A – ICU Infusions",
    "B – Parenteral",
    "C – Oral",
    "D – Tablets",
    "E – IV rate drip",
    "F – IV rate Pump"
])

# ---- Tabs A–F REMAIN UNCHANGED FROM YOUR VERSION ----
# (Same exact logic, inputs, calculations, and AI buttons)


# --- Tab A – ICU Infusions ---
with tabs[0]:
    st.header("A – ICU Infusions")
    if "selected_drug" not in st.session_state:
        st.session_state.selected_drug = None
    with st.expander("💊 Select a drug"):
        all_drugs = list(DRUGS.keys()) + ["Other"]
        cols_per_row = 4
        for i in range(0, len(all_drugs), cols_per_row):
            cols = st.columns(cols_per_row, gap="large")
            for j, drug in enumerate(all_drugs[i:i + cols_per_row]):
                icon = "🔴" if drug in TIME_MANDATORY_DRUGS else "🟢" if DRUGS.get(drug, {}).get("type")=="sedative" else "🔵" if DRUGS.get(drug, {}).get("type")=="muscle_relaxant" else "✨"
                prefix = "✅ " if st.session_state.selected_drug==drug else ""
                button_label = f"{prefix}{icon}\n{drug}"
                if cols[j].button(button_label, key=f"drug_btn_{drug}"):
                    st.session_state.selected_drug = drug

    if st.session_state.selected_drug:
        drug = st.session_state.selected_drug
        st.subheader(f"Selected Drug: {drug}")
        drug_name = st.text_input("Medication name:", value=drug if drug!="Other" else "", key="A_other_name")
        tip = drug_tips.get(drug.lower(), drug_tips["other"])
        st.info(f"🩺 {tip}")

        # Dose inputs for ICU Infusions
        if drug in TIME_MANDATORY_DRUGS:
            dose = st.number_input("Dose (mcg/kg/min)", min_value=0.0, key="A_i_dose")
            weight = st.number_input("Weight (kg)", min_value=0.0, key="A_i_weight")
            stock = st.number_input("Stock (mg)", min_value=0.1, key="A_i_stock")
            volume = st.number_input("Dilution volume (mL)", min_value=1.0, key="A_i_volume")
            time_min = st.number_input("Time (minutes) *required*", min_value=1.0, key="A_i_time")
            if st.button("Calculate ICU Infusion", key="A_i_calc"):
                result, unit = calculate_infusion(drug, dose, weight, stock, volume, time_min)
                if result:
                    st.success(f"{result} {unit}")
                    st.markdown(ask_ai(drug_name, f"{result} {unit}", tip, "Inotrope infusion"))
        else:
            dose = st.number_input("Dose", min_value=0.0, key="A_o_dose")
            dose_unit = st.selectbox("Dose unit", ["mg", "mcg", "IU"], key="A_o_dose_unit")
            weight = st.number_input("Weight (kg) – optional", min_value=0.0, value=0.0, key="A_o_weight")
            stock = st.number_input("Stock", min_value=0.1, key="A_o_stock")
            stock_unit = st.selectbox("Stock unit", ["mg", "mcg", "IU"], key="A_o_stock_unit")
            volume = st.number_input("Dilution volume (mL)", min_value=1.0, key="A_o_volume")
            time_min = st.number_input("Time (minutes) – optional", min_value=0.0, value=0.0, key="A_o_time")
            # Unit conversion
            if dose_unit == "mg" and stock_unit == "mcg": dose *= 1000
            if dose_unit == "mcg" and stock_unit == "mg": stock *= 1000
            if st.button("Calculate ICU Infusion", key="A_o_calc"):
                result, unit = calculate_infusion(drug, dose, weight if weight>0 else None, stock, volume, time_min)
                if result:
                    st.success(f"{result} {unit}")
                    st.markdown(ask_ai(drug_name, f"{result} {unit}", tip, "ICU infusion"))

        # AI Policy button
        if st.button("Generate AI Medication Policy", key=f"A_policy_{drug_name}"):
            policy_text = explain_med_policy(drug_name)
            st.markdown(f"### 📄 AI-Generated Policy for {drug_name}\n{policy_text}")

# --- Tabs B–F (Parenteral, Oral, Tablets, IV Gravity, IV Pump) follow the same pattern ---
# Each tab: input fields → calculate → display result → AI Policy button

# Tab B – Parenteral
with tabs[1]:
    st.header("B – Parenteral (IV/IM/SC)")
    med = st.text_input("Medication name:", key="Bmed")
    tip = drug_tips.get(med.lower(), "Follow standard parenteral protocol.")
    dose = st.number_input("Dose:", 0.0, key="Bdose")
    stock = st.number_input("Stock:", 0.1, 50.0, key="Bstock")
    volume = st.number_input("Volume (mL):", 1.0, 50.0, key="Bvol")
    weight_input = st.text_input("Weight (kg) (optional):", key="Bweight")
    weight = float(weight_input) if weight_input else None
    if st.button("Calculate Parenteral", key="B_calc"):
        result = calculate_parenteral(dose, stock, volume, weight)
        if result:
            st.success(f"{med}: {result:.2f} mL")
            st.markdown(ask_ai(med, f"{result:.2f} mL", tip, "Parenteral injection"))
    if st.button("Generate AI Medication Policy", key="B_policy"):
        policy_text = generate_med_policy(med)
        st.markdown(f"### 📄 AI-Generated Policy for {med}\n{policy_text}")

# Tab C – Oral
with tabs[2]:
    st.header("C – Oral syrup / suspension")
    med = st.text_input("Medication name:", key="Cmed")
    tip = drug_tips.get(med.lower(), "Follow oral administration guidelines.")
    dose = st.number_input("Dose:", 0.0, key="Cdose")
    stock = st.number_input("Stock:", 0.1, 50.0, key="Cstock")
    volume = st.number_input("Volume (mL):", 1.0, 50.0, key="Cvol")
    weight_input = st.text_input("Weight (kg) (optional):", key="Cweight")
    weight = float(weight_input) if weight_input else None
    if st.button("Calculate Oral", key="C_calc"):
        result = calculate_oral(dose, stock, volume, weight)
        if result:
            st.success(f"{med}: {result:.2f} mL")
            st.markdown(ask_ai(med, f"{result:.2f} mL", tip, "Oral syrup calculation"))
    if st.button("Generate AI Medication Policy", key="C_policy"):
        policy_text = generate_med_policy(med)
        st.markdown(f"### 📄 AI-Generated Policy for {med}\n{policy_text}")

# Tab D – Tablets
with tabs[3]:
    st.header("D – Tablets / Capsules")
    med = st.text_input("Medication name:", key="Dmed")
    tip = drug_tips.get(med.lower(), "Follow tablet administration guidelines.")
    dose = st.number_input("Prescribed dose:", 0.0, key="Ddose")
    stock = st.number_input("Tablet strength:", 0.1, 50.0, key="Dstock")
    unit = st.text_input("Unit (mg/g):", "mg", key="Dunit")
    if st.button("Calculate Tablets", key="D_calc"):
        result = calculate_tablet(dose, stock)
        if result:
            st.success(f"{med}: {result:.2f} tablet(s) [{unit}]")
            st.markdown(ask_ai(med, f"{result:.2f} tablets", tip, "Tablet calculation"))
    if st.button("Generate AI Medication Policy", key="D_policy"):
        policy_text = generate_med_policy(med)
        st.markdown(f"### 📄 AI-Generated Policy for {med}\n{policy_text}")

# Tab E – IV Gravity
with tabs[4]:
    st.header("E – IV infusion (gravity)")
    fluid = st.text_input("Fluid name:", key="Efluid")
    tip = "Follow gravity IV protocol."
    volume = st.number_input("Total volume (mL):", 1.0, key="Evol")
    drop_factor = st.number_input("Drop factor:", 1.0, key="Edrop")
    time_unit = st.selectbox("Time unit:", ["minutes","hours"], key="E_time_unit")
    time_value = st.number_input(f"Time ({time_unit}):", 0.01, key="E_time_value")
    if st.button("Calculate IV Gravity", key="E_calc"):
        rate = calculate_iv_gravity(volume, drop_factor, time_value, time_unit)
        if rate:
            st.success(f"{fluid}: {rate:.1f} gtts/min")
            st.markdown(ask_ai(fluid, f"{rate:.1f} gtts/min", tip, "IV gravity calculation"))
    if st.button("Generate AI Medication Policy", key="E_policy"):
        policy_text = generate_med_policy(fluid)
        st.markdown(f"### 📄 AI-Generated Policy for {fluid}\n{policy_text}")

# Tab F – IV Pump
with tabs[5]:
    st.header("F – IV infusion (pump)")
    fluid = st.text_input("Fluid name:", key="Ffluid")
    tip = "Follow infusion pump protocol."
    volume = st.number_input("Total volume (mL):", 1.0, key="Fvol")
    time_hours = st.number_input("Time (hours):", 0.01, key="Ftime")
    if st.button("Calculate IV Pump", key="F_calc"):
        rate = calculate_iv_pump(volume, time_hours)
        if rate:
            st.success(f"{fluid}: {rate:.1f} mL/hr")
            st.markdown(ask_ai(fluid, f"{rate:.1f} mL/hr", tip, "IV pump calculation"))
    if st.button("Generate AI Medication Policy", key="F_policy"):
        policy_text = generate_med_policy(fluid)
        st.markdown(f"### 📄 AI-Generated Policy for {fluid}\n{policy_text}")

# =========================
# Disclaimer
# =========================

st.markdown("---")
st.markdown(
    "⚠️ This AI assistant is for **educational purposes only**. "
    "Always follow hospital protocols and verify with pharmacology manuals."
)


