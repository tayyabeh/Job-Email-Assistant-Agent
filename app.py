import streamlit as st
from ui import initialize_session_state, show_progress, step_1_configuration, step_2_upload_cv, step_3_job_input, step_4_review_and_send

# Page configuration
st.set_page_config(
    page_title="AI Job Application Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/tayyabeh/job-email-assistant',
        'Report a bug': 'https://github.com/tayyabeh/job-email-assistant/issues',
        'About': "# AI Job Application Assistant\n\nCraft professional job applications with AI assistance.\n\nVersion: 1.0.0"
    }
)

# Custom CSS for enhanced dark theme
st.markdown("""
<style>
    /* Base CSS Variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: rgba(99, 102, 241, 0.1);
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --bg-card: #1e293b;
        
        --text-primary: #f8fafc;
        --text-secondary: #e2e8f0;
        --text-muted: #94a3b8;
        
        --border-color: #475569;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base Styling */
    * {
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main App Background */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] > div {
        background-color: var(--bg-primary) !important;
        border-right: 1px solid var(--border-color);
        padding: 1.5rem 1rem;
    }
    
    .stSidebar .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Main Content Area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        background-color: var(--bg-primary);
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    h1 {
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.25rem;
        font-weight: 700;
    }
    
    p, div, span {
        color: var(--text-primary);
    }
    
    /* Card Styling */
    .card {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    /* Button Styling */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
        filter: brightness(1.05) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Secondary Buttons */
    .stButton > button[kind="secondary"] {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-tertiary) !important;
        border-color: var(--primary) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Labels */
    .stTextInput label,
    .stTextArea label,
    .stFileUploader label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    /* File Uploader */
    .stFileUploader > section {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        background: var(--bg-secondary) !important;
        transition: all 0.2s ease !important;
        padding: 2rem !important;
    }
    
    .stFileUploader > section:hover {
        border-color: var(--primary) !important;
        background: var(--bg-tertiary) !important;
    }
    
    .stFileUploader section button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: var(--primary-gradient) !important;
    }
    
    .stProgress > div > div {
        background: var(--bg-secondary) !important;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        padding: 1rem 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .stAlert[data-baseweb="notification"] {
        background-color: var(--bg-secondary) !important;
    }
    
    /* Success Alert */
    .stAlert .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* Expander */
    .stExpander {
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        background: var(--bg-secondary) !important;
    }
    
    .stExpander > div:first-child {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--primary) !important;
    }
    
    /* Columns */
    .stColumns {
        gap: 2rem;
    }
    
    /* Balloons Animation */
    .stBalloons {
        z-index: 999;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        
        .card {
            padding: 1.5rem;
        }
        
        h1 {
            font-size: 1.75rem;
        }
        
        .stColumns {
            gap: 1rem;
        }
    }
    
    /* Loading States */
    .stSpinner {
        color: var(--primary) !important;
    }
    
    /* Tooltips */
    [data-baseweb="tooltip"] {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Disabled States */
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        background: var(--bg-secondary) !important;
        color: var(--text-muted) !important;
    }
    
    /* Error Messages */
    .stException {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid var(--error) !important;
        border-radius: 8px !important;
        color: var(--error) !important;
    }
    
    /* Custom Classes */
    .step-container {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border-left: 4px solid var(--primary);
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
    }
    
    .email-preview {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 1.5rem 0;
        box-shadow: var(--shadow);
    }
    
    .config-section {
        background: var(--bg-tertiary);
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1.25rem;
        border: 1px solid var(--border-color);
    }
    
    /* Markdown Content */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    .stMarkdown a {
        color: var(--primary);
        text-decoration: none;
    }
    
    .stMarkdown a:hover {
        text-decoration: underline;
    }
    
    /* Custom Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .card {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Focus indicators for accessibility */
    *:focus-visible {
        outline: 2px solid var(--primary);
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Additional CSS for enhanced styling
        st.markdown("""
        <style>
            /* Enhanced button interactions */
            .stButton > button {
                position: relative;
                overflow: hidden;
            }
            
            .stButton > button:before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg, 
                    transparent, 
                    rgba(255, 255, 255, 0.2), 
                    transparent
                );
                transition: left 0.5s;
            }
            
            .stButton > button:hover:before {
                left: 100%;
            }
            
            /* Enhanced error handling */
            .error-container {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid var(--error);
                border-radius: 12px;
                padding: 1rem;
                margin: 1rem 0;
            }
            
            .success-container {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid var(--success);
                border-radius: 12px;
                padding: 1rem;
                margin: 1rem 0;
            }
            
            /* Loading animation improvements */
            .loading-pulse {
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: .5; }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Display progress in sidebar
        show_progress()
        
        # Main content area
        with st.container():
            # Route to appropriate step
            try:
                if st.session_state.workflow_step == 1:
                    step_1_configuration()
                elif st.session_state.workflow_step == 2:
                    step_2_upload_cv()
                elif st.session_state.workflow_step == 3:
                    step_3_job_input()
                elif st.session_state.workflow_step == 4:
                    step_4_review_and_send()
                else:
                    st.error("❌ Invalid workflow step. Please refresh the page.")
                    if st.button("🔄 Reset Application", type="primary"):
                        # Reset to step 1
                        st.session_state.workflow_step = 1
                        st.rerun()
                        
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                
                # Debug information in expander
                with st.expander("🔍 Debug Information"):
                    st.code(f"""
                    Error: {str(e)}
                    Current Step: {st.session_state.workflow_step}
                    Session State Keys: {list(st.session_state.keys())}
                    """)
                
                # Recovery options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Refresh Page", type="primary"):
                        st.rerun()
                with col2:
                    if st.button("🏠 Go to Start", type="secondary"):
                        # Reset to beginning
                        for key in list(st.session_state.keys()):
                            if key not in ['api_key', 'gmail_email', 'gmail_password']:
                                del st.session_state[key]
                        initialize_session_state()
                        st.rerun()
        
        # Footer
        st.markdown("""
        <div style="text-align: center; margin-top: 4rem; padding: 2rem; color: var(--text-muted); border-top: 1px solid var(--border-color);">
            <div style="margin-bottom: 1rem;">
                <h3 style="margin: 0; color: var(--text-secondary); font-size: 1.2rem;">AI Job Application Assistant</h3>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">Streamline your job search with AI-powered applications</p>
            </div>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;">
                <a href="https://github.com/yourusername/job-email-assistant" target="_blank" 
                   style="color: var(--primary); text-decoration: none; font-size: 0.9rem;">
                    📚 Documentation
                </a>
                <a href="https://github.com/yourusername/job-email-assistant/issues" target="_blank" 
                   style="color: var(--primary); text-decoration: none; font-size: 0.9rem;">
                    🐛 Report Issue
                </a>
                <a href="mailto:support@jobassistant.ai" 
                   style="color: var(--primary); text-decoration: none; font-size: 0.9rem;">
                    💬 Support
                </a>
            </div>
            <p style="font-size: 0.8rem; opacity: 0.8;">
                Version 1.0.0 | Made with ❤️ and AI | © 2024 Job Assistant Team
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        # Global error handler
        st.error("❌ A critical error occurred while loading the application.")
        st.code(f"Error Details: {str(e)}")
        
        if st.button("🔄 Restart Application", type="primary"):
            # Clear all session state and restart
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()