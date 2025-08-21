import os
import smtplib
import time
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import Literal, Dict, Any, List
from langchain_community.document_loaders import PyPDFLoader
from typing import TypedDict
import json

# ----------------- SCHEMA -----------------
class EmailSchema(BaseModel):
    from_sender: str = Field(description="Sender email from CV json", default="")
    to: str = Field(description="Recipient email from job post text", default="hr@company.com")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Draft body of the email")
    similarity: float = Field(description="Similarity score between CV and job text", default=0.0)

class DataExtractSchema(BaseModel):
    name: str = Field(description="The candidate's full name", default="")
    skills: List[str] = Field(description="Technical and soft skills", default=[])
    experience: List[str] = Field(description="Work experiences", default=[])
    relevant_job_titles: List[str] = Field(description="Relevant job titles", default=[])
    certificates: List[str] = Field(description="Certifications", default=[])
    location: str = Field(description="Primary location", default="")
    projects: List[str] = Field(description="Significant projects", default=[])

class UserFeedbackSchema(BaseModel):
    suggestion: str = Field(description="User feedback")
    llm_decision: Literal["approved", "needs_improvement"] = Field(description="Decision")

# ----------------- CV Processing -----------------
class CvStateGraph(TypedDict):
    filepath: str
    text: str 
    parsed_data: Dict[str, Any]

def create_cv_subgraph(api_key: str):
    """Create CV processing subgraph"""
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0, 
            google_api_key=api_key
        )
        structured_model = model.with_structured_output(DataExtractSchema)
    except Exception as e:
        raise Exception(f"Failed to initialize Google AI model: {str(e)}")

    def load_data(state: CvStateGraph) -> Dict[str, Any]:
        """Load PDF content"""
        try:
            if not os.path.exists(state['filepath']):
                raise FileNotFoundError(f"CV file not found: {state['filepath']}")
            
            loader = PyPDFLoader(state['filepath'])
            docs = loader.load()
            
            if not docs:
                raise ValueError("No content found in PDF")
            
            all_text = "\n".join([doc.page_content for doc in docs])
            
            if not all_text.strip():
                raise ValueError("PDF appears to be empty or contains only images")
            
            return {'text': all_text}
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")

    def parse_data(state: CvStateGraph) -> Dict[str, Any]:
        """Parse CV data using AI"""
        try:
            if not state.get('text'):
                raise ValueError("No text content to parse")
            
            prompt = f"""
            Extract the following information from this CV/Resume text:
            
            {state['text']}
            
            Please extract:
            - Full name of the candidate
            - All technical and soft skills mentioned
            - Work experience descriptions
            - Relevant job titles held
            - Certifications or qualifications
            - Location/address information
            - Notable projects or achievements
            
            If any information is not found, leave those fields empty.
            """
            
            response = structured_model.invoke(prompt)
            return {'parsed_data': response}
            
        except Exception as e:
            raise Exception(f"Error parsing CV data: {str(e)}")

    # Build the graph
    graph = StateGraph(CvStateGraph)
    graph.add_node('load_data', load_data)
    graph.add_node('parse_data', parse_data)
    graph.add_edge(START, "load_data")
    graph.add_edge('load_data', 'parse_data')
    graph.add_edge('parse_data', END)
    
    return graph.compile()

# ----------------- Main Agent -----------------
class AgentState(TypedDict):
    filepath: str
    parsed_data: Dict[str, Any]
    text: str
    email_schema: Dict[str, Any]
    status: str
    llm_decision: str
    suggestions: str
    user_input: str

def create_workflow(api_key: str, gmail_email: str, gmail_password: str):
    """Create main workflow for email generation"""
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3, 
            google_api_key=api_key
        )
        structured_model = model.with_structured_output(EmailSchema)
        feedback_model = model.with_structured_output(UserFeedbackSchema)
    except Exception as e:
        raise Exception(f"Failed to initialize Google AI model: {str(e)}")
    
    def draft_email_node(state: AgentState) -> Dict[str, Any]:
        """Generate email draft"""
        try:
            # Get parsed CV data
            cv_data = state.get('parsed_data', {})
            job_text = state.get('text', '')
            
            if not job_text:
                raise ValueError("No job description provided")
            
            # Extract candidate info
            candidate_name = cv_data.get('name', 'Candidate')
            candidate_skills = cv_data.get('skills', [])
            candidate_experience = cv_data.get('experience', [])
            
            # Create comprehensive prompt
            prompt = f"""
            Create a professional job application email based on the following information:

            CANDIDATE INFORMATION:
            Name: {candidate_name}
            Skills: {', '.join(candidate_skills[:10]) if candidate_skills else 'Various skills'}
            Experience: {'. '.join(candidate_experience[:3]) if candidate_experience else 'Professional experience available'}

            JOB DESCRIPTION:
            {job_text}

            Instructions:
            1. Extract recipient email from job posting (look for contact email, HR email, or application email)
            2. Create a compelling subject line that mentions the position
            3. Write a professional email body that:
               - Addresses the hiring manager professionally
               - Mentions the specific position being applied for
               - Highlights 2-3 most relevant skills/experiences that match the job
               - Shows enthusiasm for the role and company
               - Mentions that the resume is attached
               - Includes a professional closing
            4. Calculate similarity score between candidate profile and job requirements (0.0 to 1.0)
            5. Use the sender email from CV if available, otherwise use the provided Gmail address

            Keep the email concise but compelling, around 150-200 words.
            """
            
            email_schema = structured_model.invoke(prompt)
            
            # Ensure we have a sender email
            if not email_schema.from_sender or email_schema.from_sender.strip() == "":
                email_schema.from_sender = gmail_email
                
            return {"email_schema": email_schema}
            
        except Exception as e:
            raise Exception(f"Error generating email draft: {str(e)}")

    def human_in_loop(state: AgentState) -> Dict[str, Any]:
        """Handle human feedback"""
        user_input = state.get("user_input", "")
        if not user_input:
            # This would be handled by the UI
            return {"user_input": "", "llm_decision": "approved"}
        
        try:
            feedback_prompt = f"""
            Analyze this user input about an email draft: "{user_input}"
            
            If the user is approving the email (words like: approve, send, ok, yes, good, looks good, send it), 
            set llm_decision to "approved".
            
            Otherwise, if they want changes or improvements, set llm_decision to "needs_improvement" 
            and extract their specific suggestions.
            """
            
            feedback_analysis = feedback_model.invoke(feedback_prompt)
            return {
                "llm_decision": feedback_analysis.llm_decision, 
                "suggestions": feedback_analysis.suggestion, 
                "user_input": ""
            }
        except Exception as e:
            return {"llm_decision": "approved", "suggestions": "", "user_input": ""}

    def edit_message_node(state: AgentState) -> Dict[str, Any]:
        """Edit email based on feedback"""
        try:
            current_email = state.get("email_schema", {})
            suggestions = state.get('suggestions', '')
            cv_data = state.get('parsed_data', {})
            job_text = state.get('text', '')
            
            edit_prompt = f"""
            Revise this email based on the user feedback:

            CURRENT EMAIL:
            Subject: {current_email.get('subject', '')}
            Body: {current_email.get('body', '')}

            USER FEEDBACK: {suggestions}

            CANDIDATE INFO: {cv_data}
            JOB DESCRIPTION: {job_text}

            Please revise the email to address the feedback while maintaining professionalism.
            Keep all other fields (to, from_sender, similarity) the same unless specifically requested to change.
            """
            
            updated_email = structured_model.invoke(edit_prompt)
            
            # Preserve original fields if not changed
            if not updated_email.from_sender:
                updated_email.from_sender = current_email.get('from_sender', gmail_email)
            if not updated_email.to:
                updated_email.to = current_email.get('to', 'hr@company.com')
                
            return {"email_schema": updated_email, "user_input": ""}
            
        except Exception as e:
            # Return original email if editing fails
            return {"email_schema": state.get("email_schema", {}), "user_input": ""}

    def route_evaluation(state: AgentState) -> str:
        """Route based on user decision"""
        decision = state.get('llm_decision', 'approved')
        return 'send_email' if decision == 'approved' else 'edit_message_node'

    def send_email_node(state: AgentState) -> Dict[str, Any]:
        """Send the email"""
        try:
            email_schema = state.get("email_schema", {})
            
            if not email_schema:
                raise ValueError("No email schema found")
            
            # Convert to EmailSchema object if it's a dict
            if isinstance(email_schema, dict):
                email_obj = EmailSchema(**email_schema)
            else:
                email_obj = email_schema
            
            result = send_email_directly(
                email_obj, 
                gmail_email, 
                gmail_password, 
                state.get('filepath', '')
            )
            
            return {"status": result}
            
        except Exception as e:
            return {"status": f"❌ Failed to send email: {str(e)}"}

    # Build workflow graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("draft_email", draft_email_node)
    graph.add_node("human_in_loop", human_in_loop)
    graph.add_node("edit_message_node", edit_message_node)
    graph.add_node("send_email", send_email_node)

    # Add edges
    graph.add_edge(START, "draft_email")
    graph.add_edge("draft_email", "human_in_loop")
    graph.add_conditional_edges(
        "human_in_loop", 
        route_evaluation, 
        {
            'send_email': 'send_email', 
            'edit_message_node': 'edit_message_node'
        }
    )
    graph.add_edge("edit_message_node", "human_in_loop")
    graph.add_edge("send_email", END)

    return graph.compile(checkpointer=InMemorySaver())

# ----------------- EMAIL UTILITIES -----------------
def send_email_directly(email_draft, gmail_email: str, gmail_password: str, cv_path: str = "") -> str:
    """Send email with current draft"""
    try:
        # Handle both EmailSchema objects and dictionaries
        if hasattr(email_draft, 'model_dump'):
            email_data = email_draft.model_dump()
        elif isinstance(email_draft, dict):
            email_data = email_draft
        else:
            email_data = {
                'to': getattr(email_draft, 'to', 'hr@company.com'),
                'subject': getattr(email_draft, 'subject', 'Job Application'),
                'body': getattr(email_draft, 'body', 'Please find my application attached.'),
                'from_sender': getattr(email_draft, 'from_sender', gmail_email)
            }
        
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = gmail_email
        msg["To"] = email_data.get('to', 'hr@company.com')
        msg["Subject"] = email_data.get('subject', 'Job Application')
        
        # Add email body
        body = email_data.get('body', 'Please find my application attached.')
        msg.attach(MIMEText(body, "plain"))
        
        # Attach CV if path exists and file is valid
        if cv_path and os.path.exists(cv_path):
            try:
                with open(cv_path, "rb") as f:
                    pdf_data = f.read()
                cv_attachment = MIMEApplication(pdf_data, _subtype="pdf")
                cv_attachment.add_header("Content-Disposition", "attachment", filename="Resume.pdf")
                msg.attach(cv_attachment)
            except Exception as attach_error:
                print(f"Warning: Could not attach CV: {attach_error}")
        
        # Send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.send_message(msg)
        
        return f"Email sent successfully to {email_data.get('to', 'recipient')}"
        
    except smtplib.SMTPAuthenticationError:
        raise Exception("Gmail authentication failed. Please check your email and app password.")
    except smtplib.SMTPException as e:
        raise Exception(f"SMTP error occurred: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")