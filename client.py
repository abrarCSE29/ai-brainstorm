# client.py

import streamlit as st
import os
from dotenv import load_dotenv
import time
from app import AIDiscussionPanel

# Load environment variables
load_dotenv()

# Predefined color options for termcolor compatibility
COLOR_OPTIONS = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]

def main():
    st.set_page_config(page_title="AI Discussion Panel", layout="wide")
    
    # Sidebar for configuration and previous discussions
    st.sidebar.title("Configuration")
    
    # Session state initialization
    if 'custom_personas' not in st.session_state:
        st.session_state.custom_personas = {
            "Developer": {
                "description": "An experienced software engineer with expertise in architecture, algorithms, and technical implementation.",
                "focus": "Technical feasibility, implementation details, code architecture, and potential technical challenges.",
                "color": "blue",
            },
            "Reasoning_Model": {
                "description": "A logical and analytical thinker with expertise in critical reasoning and problem-solving.",
                "focus": "Logical analysis, causal relationships, gap identification, and rational evaluation of ideas.",
                "color": "green",
            },
            "Project_Manager": {
                "description": "An experienced project manager skilled in planning, coordination, and resource allocation.",
                "focus": "Timeline estimation, resource requirements, risk assessment, and project coordination.",
                "color": "red",
            },
            "Business_Analyst": {
                "description": "A business-oriented analyst focused on market trends, user needs, and value proposition.",
                "focus": "Market analysis, user requirements, business value, and competitive landscape.",
                "color": "magenta",
            },
            "Creative_Designer": {
                "description": "A creative professional with expertise in user experience, design thinking, and innovation.",
                "focus": "User experience, creative solutions, design principles, and aesthetic considerations.",
                "color": "yellow",
            },
        }
    if 'discussion_history' not in st.session_state:
        st.session_state.discussion_history = []
    
    # Display previous discussions in sidebar
    st.sidebar.title("Previous Discussions")
    if st.session_state.discussion_history:
        for i, discussion in enumerate(st.session_state.discussion_history):
            with st.sidebar.expander(f"{i+1}. {discussion['topic'][:30]}{'...' if len(discussion['topic']) > 30 else ''}"):
                st.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(discussion['timestamp']))}")
                st.write(f"Iterations: {discussion['iterations']}")
                if st.button("View Full", key=f"view_{i}"):
                    st.session_state.selected_discussion = i
    else:
        st.sidebar.write("No previous discussions yet.")
    
    # Main title
    st.title("AI Discussion Panel")
    
    # Tabs for different functionalities
    tab1, tab2 = st.tabs(["Discussion", "Persona Management"])
    
    with tab1:
        st.header("Start a Discussion")
        
        # Show selected previous discussion if any
        if 'selected_discussion' in st.session_state:
            selected_idx = st.session_state.selected_discussion
            selected_discussion = st.session_state.discussion_history[selected_idx]
            st.subheader(f"Viewing Previous Discussion: {selected_discussion['topic']}")
            st.text_area("Previous Discussion Output", selected_discussion['content'], height=400)
            if st.button("Clear Selection"):
                del st.session_state.selected_discussion
        
        else:
            # Discussion parameters
            topic = st.text_input("Discussion Topic", "Enter your topic here...")
            iterations = st.slider("Number of Iterations", 1, 10, 5)
            model_name = st.selectbox("Model Selection", ["gemini-2.0-flash"], disabled=True)
            
            if st.button("Start Discussion"):
                if topic.strip():
                    with st.spinner("Running discussion..."):
                        panel = AIDiscussionPanel(
                            topic=topic,
                            num_iterations=iterations,
                            model_name=model_name
                        )
                        panel.PERSONAS = st.session_state.custom_personas
                        
                        discussion_history = panel.run_discussion()
                        
                        discussion_data = {
                            'topic': topic,
                            'content': discussion_history,
                            'iterations': iterations,
                            'timestamp': time.time(),
                            'panel': panel
                        }
                        st.session_state.discussion_history.append(discussion_data)
                        
                        st.subheader("Discussion Results")
                        result_area = st.text_area("Discussion Output", discussion_history, height=400)
                        
                        if st.button("Save Discussion"):
                            filename = panel.save_discussion()
                            st.success(f"Discussion saved to {filename}")
                else:
                    st.error("Please enter a discussion topic!")
    
    with tab2:
        st.header("Manage Personas")
        
        # Add new persona
        st.subheader("Add New Persona")
        with st.form("add_persona_form"):
            new_persona_name = st.text_input("Persona Name")
            new_description = st.text_area("Description")
            new_focus = st.text_area("Focus Areas")
            new_color = st.selectbox("Display Color", COLOR_OPTIONS, index=0)
            
            if st.form_submit_button("Add Persona"):
                if new_persona_name and new_description and new_focus:
                    if new_persona_name not in st.session_state.custom_personas:
                        st.session_state.custom_personas[new_persona_name] = {
                            "description": new_description,
                            "focus": new_focus,
                            "color": new_color
                        }
                        st.success(f"Added persona: {new_persona_name}")
                    else:
                        st.error("Persona name already exists!")
                else:
                    st.error("Please fill in all fields!")
        
        # Display and manage existing personas
        st.subheader("Current Personas")
        for persona_name, details in st.session_state.custom_personas.items():
            with st.expander(f"{persona_name}", expanded=False):
                st.write(f"Description: {details['description']}")
                st.write(f"Focus: {details['focus']}")
                st.write(f"Color: {details['color']}")
                
                if st.button(f"Delete {persona_name}", key=f"del_{persona_name}"):
                    del st.session_state.custom_personas[persona_name]
                    st.success(f"Deleted persona: {persona_name}")
                    st.experimental_rerun()

if __name__ == "__main__":
    main()