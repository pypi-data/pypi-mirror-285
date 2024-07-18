from dotenv import load_dotenv
load_dotenv()
from typing import Type, Union
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_embeddings_and_vectorstore(vectorstore_folder:str='./vectorstore/', embedding_model:Type[Union[HuggingFaceEmbeddings, OpenAIEmbeddings]] = HuggingFaceEmbeddings, specific_model:str='intfloat/multilingual-e5-large') -> FAISS:
    """  
    Description:
    Loads a local FAISS vectorstore

    Remember to have a .env file in the working directory with API keys for HuggingFace and OpenAI.

    Args: 
        vectorstore_folder: folder where the 'index.faiss' file is located. Defaults to './vectorstore/'.
        embedding_model: Must be HuggingFaceEmbeddings or OpenAIEmbeddings. Defaults to HuggingFaceEmbeddings.
        specific_model: For example 'sentence-transformers/all-MiniLM-L6-v2' or 'gpt-3.5-turbo'. Defaults to'sentence-transformers/all-MiniLM-L6-v2'.

    Returns:
        A FAISS vectorstore object.
    """
   
    # Validate that the embedding_model is either HuggingFaceEmbeddings or OpenAIEmbeddings
    if not issubclass(embedding_model, (HuggingFaceEmbeddings, OpenAIEmbeddings)):
        raise ValueError("embedding_model must be either HuggingFaceEmbeddings or OpenAIEmbeddings")
    
    try:
        embeddings = embedding_model(model_name = specific_model, show_progress=True)
        print("Embeddings created successfully.")
    except Exception as e:
        print("Error creating embeddings:", e)
        return # Stop execution if embeddings cannot be created

    try: 
        vectorstore = FAISS.load_local(vectorstore_folder, embeddings, allow_dangerous_deserialization=True)
        print("Vectorstore loaded successfully.")
        return vectorstore
    except Exception as e:
        print("Error loading vectorstore index: ", e)
        return

### RAG-pipeline med memory ###
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage

vectorstore = load_embeddings_and_vectorstore()

chat_history = [
        AIMessage(content="Hej. Jeg er en AI-bot. Hvordan kan jeg hjælpe dig?"),
    ]

def get_context_retriever_chain(vector_store=vectorstore):
    llm = ChatOpenAI(temperature=0.1)
    
    retriever = vector_store.as_retriever(search_type="similarity_score_threshold", 
                          search_kwargs={"k":10, "score_threshold":0.7})
    
    prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "På baggrund af ovenstående samtale, generer en søgeforespørgsel til at slå op i, for at få oplysninger der er relevante for samtalen")
    ])
    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    return retriever_chain
    
def get_conversational_rag_chain(retriever_chain): 
    
    llm = ChatOpenAI(temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
    ("""
     "system", "Du er en chatbot, der svarer på vejledninger til ØS. Besvar brugerens spørgsmål baseret på nedenstående kontekst. 
     
    Du oplyser altid, alle de steder i konteksten, du har fundet svaret med "Kilde: ", indsætter den på en linje nedenfor.  

    {context}

    Du giver altid det svar i konteksten, der bedst kan besvare spørgsmålet, men er du ikke sikker på svaret, siger du altid, at du ikke er sikker.
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ])
    
    stuff_documents_chain = create_stuff_documents_chain(llm,prompt)
    
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input, vector_store=vectorstore):
    if vector_store is None:
        print("Vector store not loaded correctly.")
        return "Error: Unable to process the request."

    try:
        retriever_chain = get_context_retriever_chain(vector_store)
        conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
        response = conversation_rag_chain.invoke({
            "chat_history": chat_history,
            "input": user_input
        })
        return response['answer']
    
    except Exception as e:
        print("An error occurred during response generation:", e)
        return "An error occurred, and we couldn't process your request."