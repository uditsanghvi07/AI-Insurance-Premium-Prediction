import streamlit as st
import requests

API_URL = "http://localhost:8000/predict"

st.set_page_config(
    page_title="Insurance Premium Predictor",
    page_icon="🏥",
    layout="centered"
)

st.title("🏥 Insurance Premium Category Predictor")
st.markdown("Enter your details below to predict your insurance premium category:")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=1, max_value=119, value=30)
    weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0, step=0.5)
    height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7, step=0.01)

with col2:
    income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0, step=0.5)
    smoker_choice = st.selectbox("Are you a smoker?", options=["No", "Yes"])
    smoker = True if smoker_choice == "Yes" else False

city = st.text_input("City", value="Mumbai", placeholder="Enter your city name")
occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job']
)

st.markdown("---")

if st.button("🔮 Predict Premium Category", type="primary", use_container_width=True):
    if not city.strip():
        st.error("❌ Please enter a city name")
    else:
        input_data = {
            "age": int(age),
            "weight": float(weight),
            "height": float(height),
            "income_lpa": float(income_lpa),
            "smoker": bool(smoker),
            "city": str(city.strip()),
            "occupation": str(occupation)
        }
        
        with st.spinner('🔄 Analyzing your profile...'):
            try:
                response = requests.post(API_URL, json=input_data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "response" in result:
                        prediction_data = result["response"]
                    else:
                        prediction_data = result
                    
                    prediction = prediction_data.get("predicted_category", "Unknown")
                    
                    st.success(f"### ✅ Predicted Premium Category: **{prediction}**")
                    
                    if "confidence" in prediction_data and prediction_data["confidence"]:
                        confidence = prediction_data["confidence"] * 100
                        st.metric("Confidence", f"{confidence:.1f}%")
                    
                    if "class_probabilities" in prediction_data and prediction_data["class_probabilities"]:
                        st.markdown("### 📊 Category Probabilities")
                        probs = prediction_data["class_probabilities"]
                        
                        for category, prob in probs.items():
                            st.progress(prob, text=f"{category}: {prob*100:.1f}%")
                    
                    with st.expander("🔧 API Response (Debug)"):
                        st.json(result)
                
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    try:
                        error_detail = response.json()
                        st.write(error_detail)
                    except:
                        st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the API server.")
                st.info("Make sure the FastAPI server is running: `docker run -p 8000:8000 uditsanghvi07/insurance-premium-api:latest`")
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <small>Insurance Premium Predictor v1.0</small>
    </div>
    """,
    unsafe_allow_html=True
)