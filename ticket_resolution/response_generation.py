import requests
import pandas as pd
from transformers import pipeline

from ticket_resolution.config import API_URL, TOKEN
from ticket_resolution.embedding_utils import query_tickets


def get_direct_response_old_ticket(chroma_client, ticket_data):
    category = ticket_data['Category'].replace(' ', '_')
    collection = chroma_client.get_collection(name=category)
    combined_text = ticket_data['Issue'] + " " + ticket_data['Description']
    print("Querying new ticket...")
    result = query_tickets(collection, combined_text)
    return result


def get_direct_responses_old_ticket(chroma_client, new_tickets_path):
    new_tickets_df = pd.read_csv(new_tickets_path)
    new_tickets_df['combined_text'] = new_tickets_df['Issue'] + " " + new_tickets_df['Description']
    results = []
    for i in range(len(new_tickets_df)):
        category = new_tickets_df['Category'].iloc[i]
        collection_name = category.replace(' ', '_')
        collection = chroma_client.get_collection(name=collection_name)
        print("Querying new ticket...")
        result = query_tickets(collection, new_tickets_df['combined_text'].iloc[i])
        results.append(result)
    return results


def query_meta_llama(query):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    payload = {
        "inputs": query,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.01,
            "top_k": 50,
            "top_p": 0.95,
            "return_full_text": False
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()[0]['generated_text'].strip() if response.status_code == 200 else "Error in generation"


def generate_llm_responses(chroma_client, new_tickets_path):
    new_tickets_df = pd.read_csv(new_tickets_path)
    new_tickets_df['combined_text'] = new_tickets_df['Issue'] + " " + new_tickets_df['Description']

    results = []
    for i in range(len(new_tickets_df)):
        category = new_tickets_df['Category'].iloc[i]
        collection_name = category.replace(' ', '_')
        collection = chroma_client.get_collection(name=collection_name)
        result = query_tickets(collection, new_tickets_df['combined_text'].iloc[i])
        # Assuming that documents are returned in the query
        combined_documents = " ".join(result['documents'][0])
        prompt= f""" You are a IT engineer and you provide solution for IT related issues. Give the issue {[new_tickets_df['combined_text'].iloc[i]]}
                    make use of the following previously handled similar issues {combined_documents} to provide a proper response"""
        # Make two part answer, First part answer comes from the old ticket documents db(display ticketId) while the seconds
        #  from outside source also share URL(sources ) of the searches.
        response = query_meta_llama(prompt)
        results.append(response)
    return results


def generate_llm_response(chroma_client, ticket_data):

    ticket_data['combined_text'] = ticket_data['Issue'] + " " + ticket_data['Description']
    category = ticket_data['Category'].replace(' ', '_')
    collection = chroma_client.get_collection(name=category)
    combined_text = ticket_data['Issue'] + " " + ticket_data['Description']
    result = query_tickets(collection, combined_text)
    # Assuming that documents are returned in the query
    combined_documents = " ".join(result['documents'][0])
    prompt= f""" You are a IT engineer and you provide solution for IT related issues. Give the issue {[ticket_data['combined_text']]}
                    make use of the following previously handled similar issues {combined_documents} to provide a proper response"""
    response = query_meta_llama(prompt)
    return response


def get_parsed_results(data):
    parsed_results = []
    for i, distances in enumerate(data['distances']):
        for j, distance in enumerate(distances):
            if distance < 1:
                metadata = data['metadatas'][i][j]
                document = data['documents'][i][j]
                ticket_id = data['ids'][i][j]
                parsed_results.append({
                    "Ticket ID": ticket_id,
                    "Issue": document,
                    "Agent Name": metadata['Agent Name'],
                    "Resolution": metadata.get('Resolution', 'No resolution provided'),
                    "Resolved": metadata['Resolved'],
                })
    return parsed_results


def generate_rag_llm_response(chroma_client, ticket_data):
    # Extract information from ticket data
    combined_text = f"{ticket_data['Issue']} {ticket_data['Description']}"
    collection_name = ticket_data['Category'].replace(' ', '_')
    # Get the corresponding collection from ChromaDB
    collection = chroma_client.get_collection(name=collection_name)
    # Query the collection for similar past issues
    result = query_tickets(collection, combined_text)
    parsed_result = get_parsed_results(result) 
    combined_documents = ','.join([p['Resolution'] for p in parsed_result]) 


    if combined_documents:
        prompt= f""" As an IT engineer responsible for maintaining and troubleshooting technology 
        infrastructure, I am currently facing a critical issue related to the category of 
        "{ticket_data['Category']}". Here are the details:

        - Category: {ticket_data['Category']}
        - Issue Description: {combined_text}
        - Common Issues: {','.join([p['Resolution'] for p in parsed_result])}
        - Initial Troubleshooting Steps Taken: {combined_documents} 

        The order of response is solutions ranked by olds similar tickets results followed by generative response.

        First: Write deatiled information of the previous tickets from set of most{parsed_result}. 
            Mention ticket id, resolved, issue, resolution(use markdowwn)                          

        Second: Given this context, I am seeking comprehensive solutions that address the root causes 
        and provide step-by-step remediation strategies. Additionally, it would be beneficial to 
        include any relevant documentation, best practices, or case studies from credible sources 
        that pertain to similar issues within this category. This will aid in not only resolving t
        he current problem but also in enhancing our preventive maintenance protocols.

        Please provide detailed solutions along with references to the (real) materials 
        where I can find further information or detailed guides that are specifically relevant
        to the category of "{ticket_data['Category']}".
        """

    else:
        prompt= f""" You are a IT engineer and you provide solution for IT related issues. The issue is {combined_text}.                
                As an IT engineer responsible for maintaining and troubleshooting technology infrastructure, 
                I am currently facing a critical issue related to the category of "{ticket_data['Category']}". 
                Here are the details:
                Category: {ticket_data['Category']},
                Issue Description: {combined_text},
                Given this context, I am seeking comprehensive solutions that address the root causes 
                and provide step-by-step remediation strategies. Additionally, it would be beneficial 
                to include any relevant documentation, best practices, or case studies from credible 
                sources that pertain to similar issues within this category. This will aid in not only
                resolving the current problem but also in enhancing our preventive maintenance protocols.            

                Please provide detailed solutions along with references to the source materials where
                I can find further information or detailed guides that are specifically relevant to 
                the category of "{ticket_data['Category']}". Add show/display the previous relevant
                tickets from parsed_result{parsed_result} to your response.
                """
    # Query a language model to generate a response based on the prompt      
    response = query_meta_llama(prompt)
    try:
        if ','.join(set([p['Agent Name'] for p in parsed_result]))!='':                  
            response = response +'. \n \nPlease reach out to '+','.join(set([p['Agent Name'] for p in parsed_result]))+' for further support.' 
        else:
            response = query_meta_llama(prompt) 
    except:
        response = combined_documents +'. \n \nPlease reach out to '+','.join(set([p['Agent Name'] for p in parsed_result]))+' for further support'
    
    return response