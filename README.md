# Aleph Alpha AI Solutions Engineer Case Study Solution

![alt text](rag_lanchain.png)
## Overview
This repository contains a tool designed to assist IT helpdesk agents by leveraging historical data of previously resolved tickets to suggest resolutions for new tickets. The system is built using Streamlit for the UI and integrates advanced AI models for response generation.

## Problem Statement
IT helpdesk agents often encounter repetitive issues that have been resolved previously. However, they lack an efficient way to reference these solutions, leading to inefficiencies and increased resolution times for customer tickets.

## Approach
The solution involves creating an intelligent ticket resolution assistant that:
1. **Indexes Existing Tickets**: Uses embeddings to transform previous tickets into a searchable format stored in a Chroma database.
2. **Queries for Solutions**: When a new ticket arrives, the system queries this database to find similar past tickets and suggests possible solutions.
3. **Leverages Advanced AI Models**: Integrates Meta-Llama, a generative model, to suggest solutions when direct matches are not found in the database.

### Key Components
- **Data Processing**: Consolidates and preprocesses ticket data from various formats into a unified DataFrame.
- **Embedding Utilities**: Employs sentence transformer models to generate embeddings for each ticket, which are then indexed using the Chroma database for quick retrieval.
- **Response Generation**: Implements two modes of operation:
  - Direct response from the database using vector similarity to find and suggest solutions from past tickets.
  - Generative response using the Meta-Llama model to generate insights and solutions based on the context of the query.

## Features
- **Dual Mode Response System**:
  - **Mode 1**: Directly fetches solutions from past resolved tickets.
  - **Mode 2**: Utilizes AI to generate responses for complex issues not directly resolved in past tickets.
- **Interactive UI**: Built with Streamlit, the UI allows agents to input new tickets and receive instant solution suggestions.

## Setup
### Prerequisites
- Python 3.11+
- Dependencies include pandas, requests, transformers, chromadb, langchain_community

### Installation
Clone the repository and install the required packages:
```bash
git clone https://github.com/yourusername/aa-case-study-ai-solutions-engineer-main.git
cd aa-case-study-ai-solutions-engineer-main
sh setup.sh
```

### Configuration
Set up necessary configurations in `config.py`, replacing `Your_huggingface_token` with your actual API token.

## Usage
Run the application:
```bash
streamlit run app.py
``` 
Follow the on-screen instructions to process new tickets in either direct query mode or generative response mode.

### Modules
- **Data Processing**: Handles the ingestion and preprocessing of ticket data
- **Embedding Utilities**: Manages the embedding and querying operations using sentence transformers and - Chroma (*see embedding_utils.py*).
- **Response Generation**: Interfaces with the Meta-Llama model to generate responses based on past - ticket data
- **Main**: Orchestrates the overall workflow from data loading to response generation (*see app.py*).

### Resources

- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- https://python.langchain.com/docs/integrations/llms/textgen/
- https://python.langchain.com/docs/integrations/providers/huggingface/
- https://github.com/langchain-ai/rag-from-scratch/blob/main/rag_from_scratch_1_to_4.ipynb

### Acknowledgments
- Thanks to Aleph Alpha for providing the opportunity to engage in this case study.
- Special thanks to the open-source community for the tools and libraries utilized in this project.

