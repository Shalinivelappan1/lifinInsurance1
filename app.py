import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="LiFin Insurance Lab", layout="wide")
st.title("🛡️ LiFin Insurance Lab — Developed by Prof.Shalini Velappan, IIM Trichy")

# =====================================================
# Shared Personal Profile
# =====================================================
st.sidebar.header("👤 Personal Profile (Common)")

age = st.sidebar.slider("Age", 18, 65, 30)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
smoker = st.sidebar.selectbox("Smoker?", ["No", "Yes"])
health = st.sidebar.selectbox("Health Condition", ["Good", "Average", "Poor"])

income = st.sidebar.number_input("Annual Income (₹)", value=800_000, step=50_000)
dependents = st.sidebar.number_input("Dependents", 0, 6, 2)

discount_rate = st.sidebar.slider("Discount Rate (%)", 1.0, 20.0, 8.0)

# =====================================================
# Policy A Inputs
# =====================================================
st.sidebar.header("📜 Policy A")

policyA_type = st.sidebar.selectbox("Policy A Type", ["Term Insurance", "Whole Life"])
termA = st.sidebar.slider("Policy A Term", 5, 80, 30)
coverA = st.sidebar.number_input("Policy A Cover (₹)", value=5_000_000, step=500_000)
premA = st.sidebar.number_input("Policy A Premium (₹)", value=20_000, step=1_000)
accA = st.sidebar.checkbox("Policy A: Accidental Rider", value=False)
ciA = st.sidebar.checkbox("Policy A: Critical Illness Rider", value=False)

# =====================================================
# Policy B Inputs
# =====================================================
st.sidebar.header("📜 Policy B")

policyB_type = st.sidebar.selectbox("Policy B Type", ["Term Insurance", "Whole Life"])
termB = st.sidebar.slider("Policy B Term", 5, 80, 40)
coverB = st.sidebar.number_input("Policy B Cover (₹)", value=7_500_000, step=500_000)
premB = st.sidebar.number_input("Policy B Premium (₹)", value=35_000, step=1_000)
accB = st.sidebar.checkbox("Policy B: Accidental Rider", value=True)
ciB = st.sidebar.checkbox("Policy B: Critical Illness Rider", value=True)

# =====================================================
# Mortality Model (Teaching)
# =====================================================
def base_mortality(age, year, gender):
    current_age = age + year
    base = 0.0015 if gender == "Female" else 0.002
    slope = 0.00025
    p = base + slope * max(current_age - 30, 0)
    return min(p, 0.25)

def risk_multiplier(smoker, health):
    m = 1.0
    if smoker == "Yes":
        m *= 1.5
    if health == "Average":
        m *= 1.3
    elif health == "Poor":
        m *= 1.8
    return m

# =====================================================
# NPV Engine
# =====================================================
def insurance_npv(age, term, coverage, premium, discount_rate, gender, smoker, health,
                  accidental, critical, policy_type):

    r = discount_rate / 100
    pv_benefit = 0
    pv_premium = 0
    survival = 1.0
    mult = risk_multiplier(smoker, health)

    effective_term = term if policy_type == "Term Insurance" else 100

    for t in range(1, effective_term + 1):
        p_death = base_mortality(age, t, gender) * mult

        payout = coverage
        if accidental:
            payout *= 1.5

        expected_payout = survival * p_death * payout

        if critical:
            ci_prob = 0.10
            expected_payout += survival * ci_prob * 0.3 * coverage

        pv_benefit += expected_payout / ((1 + r) ** t)

        if policy_type == "Term Insurance" and t <= term:
            pv_premium += premium / ((1 + r) ** t)
        elif policy_type == "Whole Life" and t <= 60:
            pv_premium += premium / ((1 + r) ** t)

        survival *= (1 - p_death)

    return pv_benefit - pv_premium

# =====================================================
# Compute Both NPVs
# =====================================================
npvA = insurance_npv(age, termA, coverA, premA, discount_rate, gender, smoker, health, accA, ciA, policyA_type)
npvB = insurance_npv(age, termB, coverB, premB, discount_rate, gender, smoker, health, accB, ciB, policyB_type)

utilA = coverA * max(dependents,1) / (abs(npvA) + 1)
utilB = coverB * max(dependents,1) / (abs(npvB) + 1)

# =====================================================
# Dashboard
# =====================================================
st.subheader("📊 Policy Comparison Dashboard")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### 🅰️ Policy A")
    st.metric("NPV (₹)", f"{npvA:,.0f}")
    st.metric("Utility Score", f"{utilA:,.1f}")
    st.write("Type:", policyA_type)

with c2:
    st.markdown("### 🅱️ Policy B")
    st.metric("NPV (₹)", f"{npvB:,.0f}")
    st.metric("Utility Score", f"{utilB:,.1f}")
    st.write("Type:", policyB_type)

# =====================================================
# Verdict
# =====================================================
st.markdown("## 🏁 Verdict")

if npvA > npvB:
    st.success("💰 Financially, **Policy A** is better (higher NPV).")
else:
    st.success("💰 Financially, **Policy B** is better (higher NPV).")

if utilA > utilB:
    st.info("🛡️ From protection view, **Policy A** is safer.")
else:
    st.info("🛡️ From protection view, **Policy B** is safer.")

# =====================================================
# Compare Curves
# =====================================================
st.subheader("📈 NPV vs Term (Both Policies)")

terms = np.arange(5, 81)

npvA_terms = [insurance_npv(age, t, coverA, premA, discount_rate, gender, smoker, health, accA, ciA, policyA_type) for t in terms]
npvB_terms = [insurance_npv(age, t, coverB, premB, discount_rate, gender, smoker, health, accB, ciB, policyB_type) for t in terms]

plt.figure()
plt.plot(terms, npvA_terms, label="Policy A")
plt.plot(terms, npvB_terms, label="Policy B")
plt.axhline(0)
plt.xlabel("Term")
plt.ylabel("NPV")
plt.title("NPV vs Term: Policy A vs Policy B")
plt.legend()
st.pyplot(plt.gcf())
plt.clf()

# =====================================================
# Philosophy
# =====================================================
st.markdown("""
---

## 🧠 How to Think About Insurance

- **Higher NPV** = financially less bad deal  
- **Higher Utility** = better protection against ruin  

> The best insurance is rarely the best investment.  
> It is the one that keeps your life from breaking.

---

⚠️ This is a **teaching simulator**, not an actuarial pricing engine.
""")
