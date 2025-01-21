from datetime import datetime
import ast
import json

import pandas as pd
import streamlit as st

from ticket_resolution.main import chroma_client
from ticket_resolution.main import initialize_database
from ticket_resolution.response_generation import get_direct_responses_old_ticket, generate_llm_responses
from ticket_resolution.response_generation import  get_direct_response_old_ticket, generate_llm_response
from ticket_resolution.response_generation import generate_rag_llm_response

from ticket_resolution.config import NEW_TICKETS_PATH, OLD_TICKETS_DIR, QUERY_TICKET_SAVE_PATH


# def generate_ticket_id(NEW_TICKETS_PATH):
#     # Assuming new_tickets.csv is in the same directory as your Streamlit script
#     try:
#         df = pd.read_csv(NEW_TICKETS_PATH)
#         last_ticket_id = df['Ticket ID'].dropna().iloc[-1]
#         prefix, num = last_ticket_id.split('-')
#         new_id = int(num) + 1
#         new_ticket_id = f"{prefix}-{new_id:04d}"
#     except Exception as e:
#         st.error(f"Failed to generate ticket ID: {e}")
#         return None
#     return new_ticket_id

def generate_ticket_id(NEW_TICKETS_PATH, QUERY_TICKET_SAVE_PATH):
    try:
        # Load the new tickets DataFrame
        new_df = pd.read_csv(NEW_TICKETS_PATH)
        if not new_df.empty:
            last_ticket_id = new_df['Ticket ID'].dropna().iloc[-1]
            prefix, num = last_ticket_id.split('-')
            new_id = int(num) + 1
        else:
            prefix = "TICKET"
            new_id = 1  # Start from 1 if no tickets exist yet
        new_ticket_id = f"{prefix}-{new_id:04d}"

        # Check if the new ticket ID exists in the query ticket save DataFrame
        query_df = pd.read_csv(QUERY_TICKET_SAVE_PATH)
        if new_ticket_id in query_df['Ticket ID'].values:
            last_query_ticket_id = query_df['Ticket ID'].dropna().iloc[-1]
            _, query_num = last_query_ticket_id.split('-')
            new_query_id = int(query_num) + 1
            new_ticket_id = f"{prefix}-{new_query_id:04d}"

    except Exception as e:
        st.error(f"Failed to generate ticket ID: {e}")
        return None
    return new_ticket_id


def save_new_ticket(ticket_data, QUERY_TICKET_SAVE_PATH):
    try:
        new_df = pd.DataFrame([ticket_data])
        df = pd.read_csv(QUERY_TICKET_SAVE_PATH)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(QUERY_TICKET_SAVE_PATH, index=False) 

        # After saving, clear the related session state to reset the form
        for key in ['Ticket ID', 'Date', 'Issue', 'Description', 'Agent Name', 'Category', 'Resolved', 'Resolution']:
            if key in st.session_state['ticket_data']:
                del st.session_state['ticket_data'][key]
        st.success("Ticket saved successfully!")
        st.rerun()  # Rerun the app to reset the form        
    except Exception as e:
        print(f"Failed to save ticket: {e}")


def display_llm_results(result):
    # Assuming 'result' is a string containing the response from the LLM
    # Use Streamlit's markdown to display the formatted text
    st.markdown("""
    **Issue Response from LLM:**
    """)
    st.markdown(result, unsafe_allow_html=True)


def display_results(results):
    # Assuming 'results' is a dictionary containing all the required data
    if results and 'metadatas' in results:
        # Sorting results based on the distance scores
        sorted_results = sorted(zip(results['metadatas'][0], results['distances'][0], results['documents'][0], results['ids'][0]), 
                                key=lambda x: x[1])  # x[1] is the distance
        
        for metadata, distance, document, ticket_id in sorted_results:
            # Display each ticket and its details
            status_color = "green" if metadata['Resolved'] == 'True' else "red"
            status = "Resolved" if metadata['Resolved'] == 'True' else "Unresolved"
            resolution = metadata.get('Resolution', 'No resolution provided')
            
            # Display ticket information
            st.markdown(f"""
            **Ticket ID:** {ticket_id} - **Distance Score:** {distance:.2f}
            - **Status:** <span style='color: {status_color};'>{status}</span>
            - **Agent Name:** {metadata['Agent Name']}
            - **Category:** {metadata['Category']}
            - **Date:** {metadata['Date']}
            - **Query Description:** {document}
            - **Resolution:** {resolution}
            """, unsafe_allow_html=True)


def app():
    initialize_database(OLD_TICKETS_DIR)
    st.title("Ticket Resolution Assistance")

    with st.form("ticket_form"):
        new_ticket = st.selectbox("New Ticket?", ["Yes", "No"])
        category = st.selectbox("Category", ["Network", "Software", "Hardware", "Account Management"])
        issue = st.text_input("Issue", max_chars=200)
        description = st.text_area("Description", max_chars=800)
        date = st.text( datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        agent_name = st.text_input("Agent Name")
        choice = st.radio("Select Mode of Operation:", ["Direct Query", "Generative Response"])
        submit = st.form_submit_button("Submit Query")

        if submit and all([agent_name, issue, description]):
            ticket_id = generate_ticket_id(NEW_TICKETS_PATH, QUERY_TICKET_SAVE_PATH)
            ticket_data = {
                "Ticket ID": ticket_id,
                "Category": category,
                "Issue": issue,
                "Description": description,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Agent Name": agent_name
            }
            st.session_state['ticket_data'] = ticket_data

            if choice == "Direct Query":
                result = get_direct_response_old_ticket(chroma_client, ticket_data)
                st.write("Response:")
                display_results(result)
            else:
                result = generate_rag_llm_response(chroma_client, ticket_data)
                # result = generate_llm_response(chroma_client, ticket_data) 
                display_llm_results(result)
    
        elif submit:
            st.error("Please fill in all required fields.")  
        
    # Second form for resolution, checking if 'ticket_data' exists in session state
    if 'ticket_data' in st.session_state:
        with st.form("resolution_form",  clear_on_submit=True):
            resolved = st.radio("Is the issue resolved?", ["Yes", "No"], index=1)  # Default to "No"
            resolution = st.text_area("Resolution Details", max_chars=800)
            save_resolution = st.form_submit_button("Save Resolution")

            if save_resolution:
                if resolved and resolution:
                    ticket_data = st.session_state['ticket_data']
                    ticket_data['Resolved'] = resolved
                    ticket_data['Resolution'] = resolution
                    save_new_ticket(ticket_data, QUERY_TICKET_SAVE_PATH)                                      
                else:
                    st.error("Please provide resolution details and confirm if the issue is resolved.")


if __name__ == "__main__":
    app()
