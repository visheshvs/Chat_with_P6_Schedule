from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone
import pinecone
import psycopg2

# Initialize OpenAI
llm = OpenAI(api_key='YOUR_OPENAI_API_KEY')

# Initialize Pinecone
pinecone.init(api_key='YOUR_PINECONE_API_KEY', environment='us-west1-gcp')
index = pinecone.Index("xer-data-embeddings")
vector_store = Pinecone(index, embed_function=None, metadata_filter=None)

# Establish SQL connection
conn = psycopg2.connect(
    dbname="your_db",
    user="your_user",
    password="your_password",
    host="localhost",
    port="5432"
)

def fetch_from_sql(query):
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

# Define your conversational chain
chain = ConversationalRetrievalChain.from_llm(
    llm,
    vector_store.as_retriever(),
    return_source_documents=True
)

# Example interaction
user_input = "Show me all tasks related to resource allocation."
response = chain.run(user_input)
print(response)
