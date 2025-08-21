import streamlit as st
import tempfile
import os
import json
from agents import create_cv_subgraph, create_workflow, EmailSchema, send_email_directly, DataExtractSchema

# ----------------- Initialize Session State -----------------
def initialize_session_state():
    defaults = {
        'workflow_step': 1,
        'api_key': '',
        'gmail_email': '',
        'gmail_password': '',
        'cv_uploaded': False,
        'cv_parsed': False,
        'parsed_cv': None,
        'job_text': '',
        'email_draft': None,
        'temp_cv_path': None,
        'wf': None,
        'config': {"configurable": {"thread_id": "streamlit_session"}}
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# ----------------- UI COMPONENTS -----------------
def step_1_configuration():
    # Main container with card styling
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Header with step indicator
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; width: 32px; height: 32px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; flex-shrink: 0;">1</div>
            <h2 style="margin: 0;">Configuration</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome message and description
        st.markdown("""
        <div style="margin-bottom: 2.5rem;">
            <h1 style="margin-bottom: 0.5rem; font-size: 1.8rem;">Welcome to AI Job Assistant</h1>
            <p style="color: #94a3b8; margin: 0; line-height: 1.6;">
                Let's get started by configuring your API keys and email settings. 
                This will enable you to generate and send professional job applications.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content columns
        col1, col2 = st.columns([1, 1], gap="large")  # 'large' is a valid gap value
        
        with col1:
            # API Key Section
            with st.container():
                st.markdown("### 🔐 Google AI API Key")
                st.markdown("""
                <p style='color: #94a3b8; font-size: 0.9rem; margin-top: -0.75rem; margin-bottom: 1rem;'>
                    Required for AI-powered email generation
                </p>
                """, unsafe_allow_html=True)
                
                # API Key Input with Icon
                api_key = st.text_input(
                    "API Key", 
                    type="password", 
                    value=st.session_state.api_key,
                    placeholder="Enter your Google AI API key",
                    key="api_input",
                    label_visibility="collapsed"
                )
                if api_key != st.session_state.api_key:
                    st.session_state.api_key = api_key
                
                # API Key Help Card
                st.markdown("""
                <div style="background: #1e293b; padding: 1rem; border-radius: 12px; margin-top: 1rem;
                            border-left: 4px solid #6366f1;">
                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                        <div style="color: #6366f1; font-size: 1.25rem;">ℹ️</div>
                        <div>
                            <p style="font-weight: 600; margin: 0 0 0.5rem 0;">Need an API key?</p>
                            <p style="font-size: 0.9rem; margin: 0; color: #94a3b8; line-height: 1.5;">
                                1. Go to <a href="https://ai.google.dev/" target="_blank" style="color: #6366f1;">Google AI Studio</a><br>
                                2. Create a new API key<br>
                                3. Copy and paste it above
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Gmail Configuration Section
            with st.container():
                st.markdown("### ✉️ Gmail Configuration")
                st.markdown("""
                <p style='color: #94a3b8; font-size: 0.9rem; margin-top: -0.75rem; margin-bottom: 1rem;'>
                    For sending application emails
                </p>
                """, unsafe_allow_html=True)
                
                # Email Input
                gmail_email = st.text_input(
                    "Gmail Address",
                    value=st.session_state.gmail_email,
                    placeholder="your.email@gmail.com",
                    key="gmail_email_input",
                    label_visibility="collapsed"
                )
                if gmail_email != st.session_state.gmail_email:
                    st.session_state.gmail_email = gmail_email
                
                # Password Input
                gmail_password = st.text_input(
                    "App Password",
                    type="password",
                    value=st.session_state.gmail_password,
                    placeholder="Enter your Gmail app password",
                    help="Create an app password in your Google Account settings if you have 2FA enabled.",
                    key="gmail_password_input",
                    label_visibility="collapsed"
                )
                if gmail_password != st.session_state.gmail_password:
                    st.session_state.gmail_password = gmail_password
                
                # Gmail Help Card
                st.markdown("""
                <div style="background: #1e293b; padding: 1rem; border-radius: 12px; margin-top: 1rem;
                            border-left: 4px solid #6366f1;">
                    <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                        <div style="color: #6366f1; font-size: 1.25rem;">🔒</div>
                        <div>
                            <p style="font-weight: 600; margin: 0 0 0.5rem 0;">Security First</p>
                            <p style="font-size: 0.9rem; margin: 0; color: #94a3b8; line-height: 1.5;">
                                • Use an <a href="https://myaccount.google.com/apppasswords" target="_blank" style="color: #6366f1;">App Password</a> for better security<br>
                                • Never share your credentials<br>
                                • Your password is never stored permanently
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Bottom section with navigation
        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
        
        # Navigation Buttons
        col1, col2 = st.columns([1, 1], gap="medium")  # Changed from "1rem" to "medium"
        
        with col1:
            if st.button("⏮️ Back", 
                       disabled=True, 
                       help="This is the first step", 
                       use_container_width=True,
                       type="secondary"):
                pass
                
        with col2:
            if st.button("Next: Upload CV ➡️", 
                        type="primary", 
                        use_container_width=True,
                        help="Save your settings and continue"):
                if not st.session_state.api_key:
                    st.error("❌ Please enter your Google AI API key")
                elif not (st.session_state.gmail_email and st.session_state.gmail_password):
                    st.error("❌ Please enter both Gmail address and app password")
                else:
                    st.session_state.workflow_step = 2
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close card div

def step_2_upload_cv():
    st.markdown("<h1>📄 Upload Your CV</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Header with step indicator
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; width: 32px; height: 32px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; flex-shrink: 0;">2</div>
            <h2 style="margin: 0;">Upload Your CV</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        st.markdown("""
        <p style="color: #94a3b8; margin-bottom: 2rem;">
            Upload your resume in PDF format. We'll analyze it to help craft a personalized cover letter.
        </p>
        """, unsafe_allow_html=True)
        
        # Upload area
        with st.container():
            col1, col2 = st.columns([1, 1], gap="large")  # 'large' is a valid gap value
            
            with col1:
                # Drag and drop upload
                uploaded_file = st.file_uploader(
                    "Drag and drop your CV here",
                    type=['pdf'],
                    help="Supported formats: PDF",
                    label_visibility="collapsed"
                )
                
                if uploaded_file is not None:
                    # Save the uploaded file to a temporary location
                    with st.spinner("Processing your CV..."):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                st.session_state.temp_cv_path = tmp_file.name
                            
                            # Initialize CV processing workflow
                            cv_workflow = create_cv_subgraph(st.session_state.api_key)
                            
                            # Process the CV
                            result = cv_workflow.invoke({"filepath": st.session_state.temp_cv_path})
                            
                            # Convert the result to a dictionary format for the UI
                            if result and 'parsed_data' in result and result['parsed_data']:
                                parsed_data = result['parsed_data']
                                
                                # Handle both dict and model types
                                if hasattr(parsed_data, 'model_dump'):
                                    parsed_data = parsed_data.model_dump()
                                elif hasattr(parsed_data, '__dict__'):
                                    parsed_data = vars(parsed_data)
                                
                                st.session_state.parsed_cv = {
                                    'name': parsed_data.get('name', 'Not specified'),
                                    'location': parsed_data.get('location', 'Not specified'),
                                    'skills': parsed_data.get('skills', []),
                                    'experience': parsed_data.get('experience', []),
                                    'projects': parsed_data.get('projects', []),
                                    'certificates': parsed_data.get('certificates', [])
                                }
                                
                                st.session_state.cv_uploaded = True
                                st.session_state.cv_parsed = True
                                st.success("✅ CV processed successfully!")
                            else:
                                st.error("❌ Could not extract data from CV. Please try a different file.")
                                st.session_state.cv_parsed = False
                                
                        except Exception as e:
                            st.error(f"❌ Error processing CV: {str(e)}")
                            st.session_state.cv_parsed = False
                            if 'parsed_cv' in st.session_state:
                                del st.session_state.parsed_cv
            
            with col2:
                # Preview or instructions
                if st.session_state.cv_parsed and st.session_state.parsed_cv:
                    with st.expander("📋 Preview Parsed CV Data", expanded=True):
                        st.markdown(f"""
                        <div style="background: #1e293b; border-radius: 8px; padding: 1rem;">
                            <h4 style="margin-top: 0;">{st.session_state.parsed_cv.get('name', 'No name found')}</h4>
                            <p style="color: #94a3b8; margin-bottom: 0.5rem;">📍 {st.session_state.parsed_cv.get('location', 'No location found')}</p>
                            
                            <div style="margin: 1rem 0;">
                                <h5 style="margin: 0 0 0.5rem 0;">Skills</h5>
                                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        """, unsafe_allow_html=True)
                        
                        # Display skills as tags
                        skills = st.session_state.parsed_cv.get('skills', [])
                        if skills:
                            for skill in skills[:10]:
                                st.markdown(f"""
                                <span style="background: rgba(99, 102, 241, 0.1); color: #6366f1; 
                                           padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;">
                                    {skill}
                                </span>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("<span style='color: #94a3b8;'>No skills found</span>", unsafe_allow_html=True)
                        
                        st.markdown("""
                                </div>
                            </div>
                            
                            <div style="margin-top: 1rem;">
                                <h5 style="margin: 0 0 0.5rem 0;">Experience</h5>
                                <ul style="margin: 0; padding-left: 1.2rem; color: #94a3b8;">
                        """, unsafe_allow_html=True)
                        
                        # Display experience
                        experience = st.session_state.parsed_cv.get('experience', [])
                        if experience:
                            for exp in experience[:3]:
                                st.markdown(f"<li style='margin-bottom: 0.25rem;'>{exp}</li>", unsafe_allow_html=True)
                        else:
                            st.markdown("<li style='color: #94a3b8;'>No experience found</li>", unsafe_allow_html=True)
                        
                        st.markdown("""
                                </ul>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Upload instructions
                    st.markdown("""
                    <div style="background: #1e293b; border: 2px dashed #475569; 
                                border-radius: 12px; padding: 2rem; text-align: center; margin-top: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 1rem;">📄</div>
                        <h4 style="margin: 0 0 0.5rem 0;">Upload Your CV</h4>
                        <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">
                            Drag and drop your resume here or click to browse
                        </p>
                        <p style="color: #94a3b8; font-size: 0.8rem; margin: 1rem 0 0 0;">
                            Supported format: PDF
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Navigation buttons
        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
        
        # Single column for next button only
        if st.button("Next: Job Details ➡️", 
                    type="primary", 
                    use_container_width=True,
                    disabled=not st.session_state.cv_parsed):
            st.session_state.workflow_step = 3
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def step_3_job_input():
    st.markdown("<h1>💼 Job Details</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Header with step indicator
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; width: 32px; height: 32px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; flex-shrink: 0;">3</div>
            <h2 style="margin: 0;">Job Details</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Description
        st.markdown("""
        <p style="color: #94a3b8; margin-bottom: 2rem;">
            Paste the job description below. Include the company name, position, and any specific requirements 
            to help us craft a tailored application.
        </p>
        """, unsafe_allow_html=True)
        
        # CV Preview
        if st.session_state.parsed_cv:
            with st.expander("👤 Your CV Preview", expanded=False):
                st.markdown(f"""
                <div style="background: #1e293b; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0;">{st.session_state.parsed_cv.get('name', 'No name found')}</h4>
                        <span style="font-size: 0.8rem; color: #94a3b8;">📍 {st.session_state.parsed_cv.get('location', 'No location found')}</span>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        <h5 style="margin: 0 0 0.5rem 0; font-size: 0.9rem;">Skills</h5>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                """, unsafe_allow_html=True)
                
                # Display skills as tags
                skills = st.session_state.parsed_cv.get('skills', [])
                if skills:
                    for skill in skills[:8]:
                        st.markdown(f"""
                        <span style="background: rgba(99, 102, 241, 0.1); color: #6366f1; 
                                   padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem;">
                            {skill}
                        </span>
                        """, unsafe_allow_html=True)
                
                st.markdown("""
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Job Description Input
        st.markdown("### 📝 Job Description")
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -0.75rem; margin-bottom: 0.5rem;'>Paste the complete job posting including company details</p>", unsafe_allow_html=True)
        
        job_text = st.text_area(
            "Job Description",
            value=st.session_state.job_text,
            height=300,
            placeholder="Paste the job description here...\n\nInclude details like:\n- Company name and position\n- Job requirements\n- Key responsibilities\n- Application instructions",
            key="job_input",
            label_visibility="collapsed"
        )
        
        if job_text != st.session_state.job_text:
            st.session_state.job_text = job_text
        
        # Tips for better results
        with st.expander("💡 Tips for better results"):
            st.markdown("""
            <div style="color: #94a3b8;">
                <p style="margin: 0 0 0.75rem 0;">
                    <strong>Include these for best results:</strong>
                </p>
                <ul style="margin: 0 0 0 1rem; padding-left: 0.5rem;">
                    <li>Company name and position title</li>
                    <li>Job requirements and qualifications</li>
                    <li>Key responsibilities</li>
                    <li>Any specific instructions or preferences</li>
                </ul>
                <p style="margin: 0.75rem 0 0 0;">
                    The more details you provide, more tailored your application will be.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation buttons
        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
        
        # Single column for next button only
        if st.button("Next: Review & Send ➡️", 
                    type="primary", 
                    use_container_width=True,
                    disabled=not st.session_state.job_text.strip()):
            st.session_state.workflow_step = 4
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def step_4_review_and_send():
    st.markdown("<h1>✉️ Review & Send</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Header with step indicator
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; width: 32px; height: 32px; 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                        font-weight: bold; flex-shrink: 0;">4</div>
            <h2 style="margin: 0;">Review & Send Application</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate email draft if not exists
        if not st.session_state.email_draft and st.session_state.job_text and st.session_state.parsed_cv:
            with st.spinner("Generating your application email..."):
                try:
                    # Create workflow
                    wf = create_workflow(
                        st.session_state.api_key,
                        st.session_state.gmail_email,
                        st.session_state.gmail_password
                    )
                    
                    initial_state = {
                        "filepath": st.session_state.temp_cv_path,
                        "text": st.session_state.job_text,
                        "parsed_data": st.session_state.parsed_cv
                    }
                    
                    # Generate email draft
                    result = wf.invoke(initial_state, st.session_state.config)
                    
                    if result and 'email_schema' in result:
                        email_schema = result['email_schema']
                        
                        # Handle both dict and model types
                        if hasattr(email_schema, 'model_dump'):
                            email_draft = email_schema.model_dump()
                        elif hasattr(email_schema, '__dict__'):
                            email_draft = vars(email_schema)
                        else:
                            email_draft = email_schema
                        
                        st.session_state.email_draft = email_draft
                        st.session_state.wf = wf
                        st.success("✅ Email draft generated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Could not generate email draft. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating email: {str(e)}")
                    st.write("Debug info:", str(e))
        
        if st.session_state.email_draft:
            # Email Preview with editing capabilities
            st.markdown("""
            <div style="margin-bottom: 2rem;">
                <p style="color: #94a3b8;">
                    Review and customize your application email before sending. You can edit the content below.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                # Email Header
                st.markdown(f"""
                <div style="background: #1e293b; padding: 1.5rem; border-radius: 12px 12px 0 0; 
                            border: 1px solid #475569;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <h3 style="margin: 0;">Application Email</h3>
                        <span style="font-size: 0.85rem; color: #94a3b8;">
                            To: {st.session_state.email_draft.get('to', 'Recipient')}
                        </span>
                    </div>
                    <div style="background: #334155; padding: 0.75rem; border-radius: 8px;">
                        <p style="margin: 0; font-weight: 500;">
                            Subject: {st.session_state.email_draft.get('subject', 'No subject')}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Email Body Editor
                email_body = st.text_area(
                    "Email Body",
                    value=st.session_state.email_draft.get('body', ''),
                    height=400,
                    key="email_body_editor",
                    label_visibility="collapsed"
                )
                
                # Update email body if changed
                if email_body != st.session_state.email_draft.get('body', ''):
                    st.session_state.email_draft['body'] = email_body
                
                # Email Footer
                st.markdown("""
                <div style="background: #1e293b; padding: 1rem; border-radius: 0 0 12px 12px; 
                            border: 1px solid #475569; border-top: none;">
                    <p style="margin: 0; color: #94a3b8; font-size: 0.85rem; text-align: right;">
                        Sent via AI Job Application Assistant
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Action Buttons
            st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("⬅️ Back to Job Details", use_container_width=True):
                    st.session_state.workflow_step = 3
                    st.rerun()
                    
            with col2:
                if st.button("🔄 Regenerate Email", 
                           help="Generate a new version of the email",
                           use_container_width=True):
                    try:
                        # Clear existing draft to trigger regeneration
                        st.session_state.email_draft = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error regenerating email: {str(e)}")
            
            with col3:
                if st.button("✉️ Send Application", 
                           type="primary", 
                           use_container_width=True,
                           help="Send this application email"):
                    try:
                        # Convert dict to EmailSchema if needed
                        email_obj = EmailSchema(**st.session_state.email_draft) if isinstance(st.session_state.email_draft, dict) else st.session_state.email_draft
                        
                        # Send the email
                        result = send_email_directly(
                            email_obj,
                            st.session_state.gmail_email,
                            st.session_state.gmail_password,
                            st.session_state.temp_cv_path
                        )
                        
                        st.success(f"✅ {result}")
                        st.balloons()
                        
                        # Show success message with option to start new application
                        if st.button("🆕 Start New Application", key="new_app_button"):
                            # Reset for new application but keep credentials
                            keys_to_keep = ['api_key', 'gmail_email', 'gmail_password']
                            keys_to_reset = [key for key in st.session_state.keys() if key not in keys_to_keep]
                            for key in keys_to_reset:
                                del st.session_state[key]
                            initialize_session_state()
                            st.session_state.workflow_step = 1
                            st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error sending email: {str(e)}")
                        
        else:
            st.warning("No email draft found. Please go back and complete the previous steps.")
            if st.button("⬅️ Back to Job Details"):
                st.session_state.workflow_step = 3
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close card div

# Progress indicator
def show_progress():
    with st.sidebar:
        st.markdown("""
        <style>
            .progress-container {
                background: #1e293b;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1.5rem;
                border: 1px solid #475569;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .progress-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                opacity: 0.8;
            }
            
            .progress-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: #6366f1;
                margin: 0 0 1.25rem 0;
                padding-bottom: 0.75rem;
                text-align: center;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            
            .progress-title::before {
                content: '🚀';
                font-size: 1.2em;
            }
            
            .progress-steps {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                position: relative;
                padding: 0.25rem 0;
            }
            
            .progress-steps::before {
                content: '';
                position: absolute;
                left: 1.25rem;
                top: 0;
                bottom: 0;
                width: 2px;
                background: #475569;
                z-index: 1;
            }
            
            .step {
                display: flex;
                align-items: center;
                padding: 0.75rem 0;
                position: relative;
                cursor: pointer;
                transition: all 0.2s ease;
                border-radius: 8px;
                padding: 0.5rem 0.75rem;
                margin: 0 -0.5rem;
            }
            .step:hover {
                background: rgba(255, 255, 255, 0.05);
            }
            .step:not(:last-child)::after {
                content: '';
                position: absolute;
                left: 27px;
                top: 48px;
                height: calc(100% - 8px);
                width: 2px;
                background: #475569;
                z-index: 1;
            }
            .step-number {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: #334155;
                color: #94a3b8;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 1rem;
                font-weight: 600;
                position: relative;
                z-index: 2;
                border: 2px solid #475569;
                transition: all 0.3s ease;
                flex-shrink: 0;
            }
            .step.active .step-number {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                border-color: #6366f1;
                box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
                transform: scale(1.05);
            }
            .step.completed .step-number {
                background: #10b981;
                color: white;
                border-color: #10b981;
            }
            .step.completed .step-number::after {
                content: '✓';
                font-size: 1rem;
            }
            .step-label {
                font-weight: 500;
                color: #94a3b8;
                transition: all 0.3s ease;
                font-size: 0.95rem;
            }
            .step.active .step-label {
                color: #f8fafc;
                font-weight: 600;
            }
            .step.completed .step-label {
                color: #e2e8f0;
            }
            .step-icon {
                margin-right: 0.5rem;
                opacity: 0.7;
                transition: all 0.3s ease;
            }
            .step.active .step-icon {
                opacity: 1;
                transform: scale(1.1);
            }
            .step.completed .step-icon {
                opacity: 1;
            }
        </style>
        """, unsafe_allow_html=True)
        
        steps = [
            {"number": 1, "label": "Configuration", "icon": "⚙️", "step": 1},
            {"number": 2, "label": "Upload CV", "icon": "📄", "step": 2},
            {"number": 3, "label": "Job Details", "icon": "💼", "step": 3},
            {"number": 4, "label": "Review & Send", "icon": "✉️", "step": 4}
        ]
        
        current_step = st.session_state.workflow_step
        
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.markdown('<div class="progress-title">Application Progress</div>', unsafe_allow_html=True)
        
        for step in steps:
            step_class = []
            if step["step"] == current_step:
                step_class.append("active")
            elif step["step"] < current_step:
                step_class.append("completed")
            
            st.markdown(f'''
                <div class="step {' '.join(step_class)}" 
                     style="margin-bottom: 0.25rem;">
                    <div class="step-number">{step["number"]}</div>
                    <div class="step-label">
                        <span class="step-icon">{step["icon"]}</span>
                        {step["label"]}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)