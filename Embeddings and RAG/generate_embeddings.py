import os
import pandas as pd
import openai
import pinecone

# Initialize OpenAI and Pinecone
openai.api_key = 'YOUR_OPENAI_API_KEY'
pinecone.init(api_key='YOUR_PINECONE_API_KEY', environment='us-west1-gcp')

# Create Pinecone index
index_name = "xer-data-embeddings"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=1536)  # Dimension based on embedding model
index = pinecone.Index(index_name)

# Load data
df = pd.read_csv('CSV Exports/tasks.csv')  # Example table

# Generate and upload embeddings
for _, row in df.iterrows():
    text = row['description']  # Replace with your text field
    embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")['data'][0]['embedding']
    index.upsert([(str(row['id']), embedding, {"name": row['name']})])  # Use appropriate ID and metadata

# Close connection
index.close()
