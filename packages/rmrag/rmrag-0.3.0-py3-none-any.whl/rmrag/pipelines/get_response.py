from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage

chat_history = [
    AIMessage(content="Hej. Jeg er en AI-bot. Hvordan kan jeg hjælpe dig?"),
]

def get_context_retriever_chain(vectorstore):
    try:
        llm = ChatOpenAI(temperature=0.1)
        
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold", 
            search_kwargs={"k": 10, "score_threshold": 0.7}
        )
        
        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "På baggrund af ovenstående samtale, generer en søgeforespørgsel til at slå op i, for at få oplysninger der er relevante for samtalen")
        ])
        
        retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
        
        return retriever_chain
    
    except Exception as e:
        print("An error occurred while creating the context retriever chain:", e)
        return None

def get_conversational_rag_chain(retriever_chain): 
    llm = ChatOpenAI(temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        """
        "system", "Du er en chatbot, der svarer på vejledninger til ØS. Besvar brugerens spørgsmål baseret på nedenstående kontekst. 
        
        Du oplyser altid, alle de steder i konteksten, du har fundet svaret med "Kilde: ", indsætter den på en linje nedenfor.  

        {context}

        Du giver altid det svar i konteksten, der bedst kan besvare spørgsmålet, men er du ikke sikker på svaret, siger du altid, at du ikke er sikker.
        """,
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input, vectorstore):
    if vectorstore is None:
        print("Vector store not loaded correctly.")
        return "Error: Unable to process the request."

    try:
        retriever_chain = get_context_retriever_chain(vectorstore)
        conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
        response = conversation_rag_chain.invoke({
            "chat_history": chat_history,
            "input": user_input
        })
        return response['answer']
    
    except Exception as e:
        print("An error occurred during response generation:", e)
        return "An error occurred, and we couldn't process your request."
