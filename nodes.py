# nodes.py
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Initialize models
llm_researcher = ChatOllama(model="qwen3:1.7b", temperature=0) 
llm_writer = ChatOllama(model="qwen3:1.7b", temperature=0)

def supervisor_node(state):
    """Strict Routing Logic"""
    # Check if messages exist to avoid index error on start
    if not state.get("messages"):
        return {"next_step": "Researcher"}

    last_message = state["messages"][-1]
    
    if last_message.name == "Researcher" and state.get("research_data"):
        return {"next_step": "Writer"}
    
    if last_message.name == "Writer" and state.get("draft_report"):
        return {"next_step": "FINISH"}
    
    return {"next_step": "Researcher"}

def researcher_node(state):
    """Performs research and gathers data"""
    # Get initial user request
    user_request = state['messages'][0].content
    prompt = f"Research the topic: {user_request}"
    
    print(f"--- Researcher working on: {user_request} ---")
    response = llm_researcher.invoke([SystemMessage(content=prompt)])
    
    research_data = response.content 

    return {
        "messages": [HumanMessage(content=response.content, name="Researcher")],
        "research_data": research_data,
    }

def writer_node(state):
    """Writes a report based on the gathered research"""
    prompt = f"Write a report based on the following research data: {state['research_data']}"
    
    print("--- Writer working on report ---")
    response = llm_writer.invoke([SystemMessage(content=prompt)])

    draft_report = response.content 

    return {
        "messages": [HumanMessage(content=response.content, name="Writer")],
        "draft_report": draft_report,
    }