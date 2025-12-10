# agent.py
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver # Corrected Import
from state import AgentState
from nodes import supervisor_node, researcher_node, writer_node # Import your nodes

# Initialize Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Writer", writer_node)

# Add Edges
workflow.add_edge("Researcher", "Supervisor")
workflow.add_edge("Writer", "Supervisor")

# Conditional Edge
workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next_step"],
    {
        "Researcher": "Researcher",
        "Writer": "Writer",
        "FINISH": END,
    }
)

workflow.add_edge(START, "Supervisor")

# Compile with Interrupt
# Memory needs a checkpointer to handle interrupts
checkpointer = MemorySaver()
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["Writer"], 
)

# Run Loop
if __name__ == "__main__":
    print("--- Specialist Swarm (Researcher -> Writer -> Researcher Loop) ---")
    user_input = input("Enter a topic for research: ")

    full_prompt = f"{user_input}. Please generate a comprehensive report."
    
    # IMPORTANT: Config is required for memory/interrupts
    config = {"configurable": {"thread_id": "1"}}
    
    current_input = {"messages": [HumanMessage(content=full_prompt, name="User")]}
    
    # We use a loop to handle the stream and the interrupt manually
    while True:
        try:
            # Stream events
            # Passing None as input when resuming allows graph to pick up from state
            events = graph.stream(current_input, config=config, stream_mode="values")
            
            for event in events:
                if "messages" in event and event["messages"]:
                    last_msg = event["messages"][-1]
                    # Print logic to see progress
                    if last_msg.name == "Researcher":
                        # Only print if this is a new update
                        pass 
            
            # Check state after stream finishes (or pauses)
            snapshot = graph.get_state(config)
            
            if snapshot.next:
                print(f"\n---- ⏸️  Paused before node: {snapshot.next} ----")
                print("Research complete. Proceed to writing?")
                approve = input("(yes/no): ")
                
                if approve.lower() == "yes":
                    # To resume, we pass None as input, but keep the config
                    current_input = None 
                else:
                    print("Process terminated by user.")
                    break
            else:
                # If no next step, we are done
                final_report = snapshot.values.get("draft_report")
                if final_report:
                    filename = "report.txt"
                    with open(filename, "w", encoding='utf-8') as f:
                        f.write(final_report)
                    print(f"\n\033[92m[System]: Report saved to '{filename}'\033[0m")
                break
                
        except Exception as e:
            print(f"Error: {e}")
            break
