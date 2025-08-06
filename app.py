import streamlit as st
import os
from dotenv import load_dotenv
import requests

# Load API key
load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Read prompt template file
def load_prompt(filename):
    with open(f"prompts/{filename}", "r") as file:
        return file.read()

# Generate text using Groq API
def generate_text(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    json_data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful and professional medical assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=json_data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Groq API error: {response.status_code} {response.text}")
        return ""

# Generate clinical note based on selected format
def generate_clinical_note(data, format_type):
    if format_type == "SOAP":
        template = load_prompt("soap_template.txt")
    elif format_type == "DAP":
        template = load_prompt("dap_template.txt")
    else:
        st.error("Unsupported format selected.")
        return ""

    prompt = template.format(**data)
    return generate_text(prompt)

# Generate patient-friendly summary
def generate_patient_summary(clinical_note):
    template = load_prompt("patient_summary_template.txt")
    prompt = template.format(clinical_note=clinical_note)
    return generate_text(prompt)

# Generate ICD-10 code
def generate_icd10_code(clinical_note):
    template = load_prompt("icd10_template.txt")
    prompt = template.format(clinical_note=clinical_note)
    return generate_text(prompt)

# Streamlit UI with enhanced UX
st.set_page_config(
    page_title="Clinical Note Generator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    # .section-header {
    #     color: #2c3e50;
    #     border-bottom: 2px solid #3498db;
    #     padding-bottom: 0.5rem;
    #     margin: 1.5rem 0 1rem 0;
    # }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: bold;
    }
    # .vital-container {
    #     background-color: #f8f9fa;
    #     padding: 1rem;
    #     border-radius: 8px;
    #     border: 1px solid #dee2e6;
    #     margin: 0.5rem 0;
    # }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>Clinical Note Generator</h1><p>Streamlined interface for faster clinical documentation</p></div>', unsafe_allow_html=True)

# Sidebar for settings and options
with st.sidebar:
    st.markdown("Generation Settings")
    
    # Note format selection with checkboxes
    st.markdown("**Note Formats:**")
    soap_format = st.checkbox("SOAP Note", value=True)
    dap_format = st.checkbox("DAP Note", value=False)
    
    st.markdown("**Additional Outputs:**")
    generate_summary = st.checkbox("Patient-Friendly Summary", value=True)
    generate_icd10 = st.checkbox("ICD-10 Code Prediction", value=False)
    
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.info("• All fields are optional - fill what you have\n• Use templates for instant pre-filling\n• Templates work immediately - no refresh needed\n• Generate multiple formats simultaneously")

# Main form with improved layout
with st.form("enhanced_note_form"):
    # Patient Demographics Section
    st.markdown('<h3 class="section-header">Patient Demographics</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name = st.text_input("Patient Name", 
                           value=st.session_state.get('template_name', ''),
                           placeholder="Enter patient's full name (optional)")
    
    with col2:
        # Age with slider as requested
        age = st.slider("Age", min_value=0, max_value=130, 
                       value=st.session_state.get('template_age', 35), step=1)
    
    # Gender with radio buttons (better than checkboxes for single selection)
    st.markdown("**Gender:**")
    gender = st.radio("", ["Male", "Female", "Other", "Prefer not to say"], 
                     horizontal=True, index=st.session_state.get('template_gender_idx', 0))
    
    # Clinical Information Section
    st.markdown('<h3 class="section-header">Clinical Information</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        complaint = st.text_input("Chief Complaint", 
                                value=st.session_state.get('template_complaint', ''),
                                placeholder="e.g., Chest pain, Headache, Fever")
        history = st.text_area("Medical History", 
                             value=st.session_state.get('template_history', ''),
                             placeholder="Previous conditions, surgeries, family history...", height=100)
        allergies = st.text_area("Known Allergies", 
                               value=st.session_state.get('template_allergies', ''),
                               placeholder="Drug allergies, food allergies, environmental...", height=80)
    
    with col2:
        symptoms = st.text_area("Present Symptoms", 
                              value=st.session_state.get('template_symptoms', ''),
                              placeholder="List current symptoms (comma-separated)", height=100)
        medications = st.text_area("Current Medications", 
                                 value=st.session_state.get('template_medications', ''),
                                 placeholder="List current medications with dosages...", height=100)
    
    # Vital Signs Section with individual text boxes as requested
    st.markdown('<h3 class="section-header">Vital Signs</h3>', unsafe_allow_html=True)
    st.markdown('<div class="vital-container">', unsafe_allow_html=True)
    
    vital_col1, vital_col2, vital_col3, vital_col4 = st.columns(4)
    
    with vital_col1:
        bp_systolic = st.text_input("BP Systolic", 
                                  value=st.session_state.get('template_bp_sys', ''),
                                  placeholder="120")
        temperature = st.text_input("Temperature (°F)", 
                                  value=st.session_state.get('template_temp', ''),
                                  placeholder="98.6")
    
    with vital_col2:
        bp_diastolic = st.text_input("BP Diastolic", 
                                   value=st.session_state.get('template_bp_dia', ''),
                                   placeholder="80")
        respiratory_rate = st.text_input("Respiratory Rate", 
                                       value=st.session_state.get('template_rr', ''),
                                       placeholder="16")
    
    with vital_col3:
        heart_rate = st.text_input("Heart Rate", 
                                 value=st.session_state.get('template_hr', ''),
                                 placeholder="72")
        oxygen_saturation = st.text_input("O2 Saturation (%)", 
                                        value=st.session_state.get('template_o2', ''),
                                        placeholder="98")
    
    with vital_col4:
        weight = st.text_input("Weight (lbs)", 
                             value=st.session_state.get('template_weight', ''),
                             placeholder="150")
        height = st.text_input("Height (in)", 
                             value=st.session_state.get('template_height', ''),
                             placeholder="68")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit section
    st.markdown("---")
    submitted = st.form_submit_button("Generate Clinical Note(s)", use_container_width=True)

# Quick Templates Section (Outside of form)
st.markdown('<h3 class="section-header">Quick Templates</h3>', unsafe_allow_html=True)

template_col1, template_col2, template_col3 = st.columns(3)

with template_col1:
    if st.button("Common Cold Template"):
        # Clear previous template data
        for key in list(st.session_state.keys()):
            if key.startswith('template_'):
                del st.session_state[key]
        # Apply new template
        st.session_state.update({
            'template_complaint': 'Upper respiratory symptoms',
            'template_symptoms': 'Runny nose, sore throat, cough, mild fever',
            'template_temp': '100.2',
            'template_hr': '78',
            'template_bp_sys': '118',
            'template_bp_dia': '75',
            'template_rr': '18',
            'template_applied': 'cold'
        })
        st.rerun()

with template_col2:
    if st.button("Hypertension Template"):
        # Clear previous template data
        for key in list(st.session_state.keys()):
            if key.startswith('template_'):
                del st.session_state[key]
        # Apply new template
        st.session_state.update({
            'template_complaint': 'Routine blood pressure check',
            'template_symptoms': 'No acute symptoms reported',
            'template_bp_sys': '150',
            'template_bp_dia': '95',
            'template_hr': '82',
            'template_temp': '98.4',
            'template_applied': 'hypertension'
        })
        st.rerun()

with template_col3:
    if st.button("Annual Physical Template"):
        # Clear previous template data
        for key in list(st.session_state.keys()):
            if key.startswith('template_'):
                del st.session_state[key]
        # Apply new template
        st.session_state.update({
            'template_complaint': 'Annual physical examination',
            'template_symptoms': 'No acute complaints',
            'template_temp': '98.6',
            'template_bp_sys': '120',
            'template_bp_dia': '80',
            'template_hr': '72',
            'template_rr': '16',
            'template_o2': '99',
            'template_weight': '165',
            'template_height': '68',
            'template_applied': 'physical'
        })
        st.rerun()

# Display template applied message
if 'template_applied' in st.session_state:
    template_type = st.session_state.template_applied
    if template_type == "cold":
        st.success("💡 Common Cold template applied! Fields have been pre-filled with typical values.")
    elif template_type == "hypertension":
        st.success("💡 Hypertension template applied! Fields have been pre-filled with elevated BP values.")
    elif template_type == "physical":
        st.success("💡 Annual Physical template applied! Fields have been pre-filled with normal values.")
    
    # Add button to clear template
    if st.button("Clear Template"):
        for key in list(st.session_state.keys()):
            if key.startswith('template_'):
                del st.session_state[key]
        st.rerun()

# Process form submission
if submitted:
    # Basic validation - at least one field should be filled for meaningful note generation
    if not any([name, complaint, symptoms, history, bp_systolic, heart_rate, temperature]):
        st.error("⚠️ Please fill in at least some basic information to generate a meaningful clinical note.")
    else:
        # Combine vitals into a formatted string (all optional)
        vitals_list = []
        if bp_systolic and bp_diastolic:
            vitals_list.append(f"BP: {bp_systolic}/{bp_diastolic} mmHg")
        elif bp_systolic:  # Just systolic
            vitals_list.append(f"BP: {bp_systolic}/? mmHg")
        elif bp_diastolic:  # Just diastolic
            vitals_list.append(f"BP: ?/{bp_diastolic} mmHg")
            
        if heart_rate:
            vitals_list.append(f"HR: {heart_rate} bpm")
        if temperature:
            vitals_list.append(f"Temp: {temperature}°F")
        if respiratory_rate:
            vitals_list.append(f"RR: {respiratory_rate}/min")
        if oxygen_saturation:
            vitals_list.append(f"O2 Sat: {oxygen_saturation}%")
        if weight:
            vitals_list.append(f"Weight: {weight} lbs")
        if height:
            vitals_list.append(f"Height: {height} in")
        
        vitals = ", ".join(vitals_list) if vitals_list else "Vitals not recorded"
        
        data = {
            "name": name or "Unknown Patient",
            "age": age,
            "gender": gender,
            "complaint": complaint or "General consultation",
            "symptoms": symptoms or "No specific symptoms reported",
            "history": history or "No significant medical history",
            "vitals": vitals,
            "medications": medications or "None reported",
            "allergies": allergies or "NKDA (No Known Drug Allergies)",
        }
        
        # Generate notes based on selected formats
        results = {}
        
        if soap_format:
            with st.spinner("Generating SOAP note..."):
                results['SOAP'] = generate_clinical_note(data, "SOAP")
        
        if dap_format:
            with st.spinner("Generating DAP note..."):
                results['DAP'] = generate_clinical_note(data, "DAP")
        
        # Display results in tabs
        if results:
            tabs = st.tabs(list(results.keys()) + 
                          (["Patient Summary"] if generate_summary else []) + 
                          (["ICD-10 Codes"] if generate_icd10 else []))
            
            # Display clinical notes
            for i, (format_name, note) in enumerate(results.items()):
                with tabs[i]:
                    st.subheader(f"{format_name} Clinical Note")
                    st.code(note, language="markdown")
                    st.download_button(
                        f"Download {format_name} Note",
                        note,
                        file_name=f"{name.replace(' ', '_')}_{format_name.lower()}_note.txt",
                        key=f"download_{format_name.lower()}"
                    )
            
            # Generate additional outputs
            tab_index = len(results)
            
            if generate_summary:
                with tabs[tab_index]:
                    with st.spinner("Generating patient-friendly summary..."):
                        # Use the first available clinical note for summary
                        first_note = list(results.values())[0]
                        patient_summary = generate_patient_summary(first_note)
                        st.subheader("Patient-Friendly Summary")
                        st.write(patient_summary)
                        st.download_button(
                            "Download Patient Summary",
                            patient_summary,
                            file_name=f"{name.replace(' ', '_')}_patient_summary.txt",
                            key="download_summary"
                        )
                tab_index += 1
            
            if generate_icd10:
                with tabs[tab_index]:
                    with st.spinner("🔍 Predicting ICD-10 codes..."):
                        # Use the first available clinical note for ICD-10 prediction
                        first_note = list(results.values())[0]
                        icd10_code = generate_icd10_code(first_note)
                        st.subheader("🔍 ICD-10 Code Prediction")
                        st.write(icd10_code)
                        st.download_button(
                            "Download ICD-10 Codes",
                            icd10_code,
                            file_name=f"{name.replace(' ', '_')}_icd10_codes.txt",
                            key="download_icd10"
                        )
        else:
            st.warning("⚠️ Please select at least one note format to generate.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "💡 <strong>Pro Tip:</strong> Save time by using keyboard shortcuts and templates for common cases!"
    "</div>", 
    unsafe_allow_html=True
)