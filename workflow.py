# from typing import TypedDict, Annotated, List
# import operator
# import os
# import json

# from langgraph.graph import StateGraph, START, END
# from langgraph.checkpoint.memory import MemorySaver

# from agents.agent_a import extract_requirements
# from agents.agent_b import generate_playwright_code, fix_code
# from agents.agent_c import validate_code
# from utils.playwright_runner import run_tests


# # Shared State

# class AgentState(TypedDict):
#     pdf_path: str
#     requirements: str
#     code: str
#     issues: List[dict]
#     attempt: int
#     test_results: dict
#     messages: Annotated[list, operator.add]


# # Agent A - Extract Requirements

# def agent_a_node(state: AgentState):
#     print(" [Agent A] Extracting requirements...")

#     req = extract_requirements(state["pdf_path"])

#     os.makedirs("output", exist_ok=True)

#     with open("output/requirements.json", "w", encoding="utf-8") as f:
#         json.dump(req, f, indent=4)

#     print(" Requirements saved to output/requirements.json")

#     return {
#         "requirements": req,
#         "messages": ["[Agent A] Requirements extracted and saved"]
#     }

# # Agent B - Generate / Fix Code

# def agent_b_node(state: AgentState):
#     if not state.get("code"):
#         print(" [Agent B] Generating new code...")
#         code = generate_playwright_code(state["requirements"])
#         msg = "[Agent B] Generated initial code"
#     else:
#         print(f" [Agent B] Fixing issues (Attempt {state['attempt']})...")
#         code = fix_code(
#             state["requirements"],
#             state["code"],
#             state["issues"]
#         )
#         msg = "[Agent B] Performed incremental fix only"

#     return {
#     "code": code,
#     "attempt": state.get("attempt", 0) + 1,
#     "messages": [msg]
# }
#     if not code:
#         print("  ERROR: Code generation failed!")
#         code = "# fallback code\nprint('Code generation failed')"

#     return {
#         "code": code,
#         "messages": ["[Agent B] Code processed"]
#     }

# # Agent C - Validate Code

# def agent_c_node(state: AgentState):
#     print(" [Agent C] Validating code...")
#     feedback = validate_code(state["code"], state["requirements"])

#     return {
#         "issues": feedback.get("issues", []),
#         "messages": [f"[Agent C] Found {len(feedback.get('issues', []))} issues"]
#     }

# # Execute Tests

# def execute_tests_node(state: AgentState):
#     print(" Executing final tests...")

#     test_file = "output/tests/test_generated.py"
#     os.makedirs("output/tests", exist_ok=True)

#     with open(test_file, "w", encoding="utf-8") as f:
#         f.write(state["code"])

#     results = run_tests(test_file, "output")

#     return {
#         "test_results": results,
#         "messages": ["[Executor] Tests completed"]
#     }

# # Control Logic

# def should_continue(state: AgentState):
#     if len(state.get("issues", [])) == 0 or state.get("attempt", 0) >= 3:
#         return "execute_tests"
#     return "agent_b"


# # Build Workflow

# def build_workflow():
#     workflow = StateGraph(AgentState)

#     workflow.add_node("agent_a", agent_a_node)
#     workflow.add_node("agent_b", agent_b_node)
#     workflow.add_node("agent_c", agent_c_node)
#     workflow.add_node("execute_tests", execute_tests_node)

#     workflow.add_edge(START, "agent_a")
#     workflow.add_edge("agent_a", "agent_b")
#     workflow.add_edge("agent_b", "agent_c")

#     workflow.add_conditional_edges(
#         "agent_c",
#         should_continue,
#         {
#             "agent_b": "agent_b",
#             "execute_tests": "execute_tests"
#         }
#     )

#     workflow.add_edge("execute_tests", END)

#     return workflow.compile(checkpointer=MemorySaver())


# # Main Execution

# if __name__ == "__main__":
#     app = build_workflow()

#     initial_state = {
#         "pdf_path": "SRS_Document.pdf",
#         "requirements": "",
#         "code": "",
#         "issues": [],
#         "attempt": 0,
#         "test_results": {},
#         "messages": []
#     }

#     print(" Starting Virtusa Capstone - LangGraph Multi-Agent System\n")

#     final = app.invoke(initial_state)

#     report = {
#         "total_attempts": final.get("attempt", 0) + 1,
#         "final_issues": final.get("issues", []),
#         "execution_status": final["test_results"].get("status"),
#         "communication_log": final["messages"]
#     }

#     os.makedirs("output", exist_ok=True)

#     with open("output/report.json", "w", encoding="utf-8") as f:
#         json.dump(report, f, indent=4)

#     print(f"\n Done! Total attempts: {final.get('attempt', 0) + 1}")
#     print(f"Final status: {final['test_results'].get('status')}")
#     print(" Report: output/report.json")
#     print(" Test file: output/tests/test_generated.py")

from typing import TypedDict, Annotated, List
import operator
import os
import json

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Agents
from agents.agent_a import extract_requirements
from agents.agent_k import extract_locators   
from agents.agent_b import generate_playwright_code, fix_code
from agents.agent_c import validate_code

from utils.playwright_runner import run_tests


# -------------------------------
# Shared State
# -------------------------------

class AgentState(TypedDict):
    pdf_path: str
    requirements: dict
    locators: dict           
    code: str
    issues: List[dict]
    attempt: int
    test_results: dict
    messages: Annotated[list, operator.add]



# Agent A - Extract Requirements

def agent_a_node(state: AgentState):
    print(" [Agent A] Extracting requirements...")

    req = extract_requirements(state["pdf_path"])

    os.makedirs("output", exist_ok=True)

    with open("output/requirements.json", "w", encoding="utf-8") as f:
        json.dump(req, f, indent=4)

    print(" Requirements saved to output/requirements.json")

    return {
        "requirements": req,
        "messages": ["[Agent A] Requirements extracted and saved"]
    }


# Agent K - Extract Locators


def agent_k_node(state: AgentState):
    print(" [Agent K] Extracting locators via web scraping...")

    requirements = state.get("requirements", {})
    base_url = requirements.get("url", "")
    scenarios = requirements.get("scenarios", [])

    locators = extract_locators(base_url, scenarios)

    os.makedirs("output", exist_ok=True)

    with open("output/locators.json", "w", encoding="utf-8") as f:
        json.dump(locators, f, indent=4)

    print(" Locators saved to output/locators.json")

    return {
        "locators": locators,
        "messages": ["[Agent K] Locators extracted and saved"]
    }


# Agent B - Generate / Fix Code


def agent_b_node(state: AgentState):
    if not state.get("code"):
        print(" [Agent B] Generating new code...")

        code = generate_playwright_code(
            state["requirements"],
            state.get("locators", {})  
        )

        msg = "[Agent B] Generated initial code"

    else:
        print(f" [Agent B] Fixing issues (Attempt {state['attempt']})...")

        code = fix_code(
            state["requirements"],
            state.get("locators", {}),  
            state["code"],
            state["issues"]
        )

        msg = "[Agent B] Fixed code based on issues"

    if not code:
        print(" ERROR: Code generation failed!")
        code = "# fallback code\nprint('Code generation failed')"

    return {
        "code": code,
        "attempt": state.get("attempt", 0) + 1,
        "messages": [msg]
    }

# Agent C - Validate Code


def agent_c_node(state: AgentState):
    print(" [Agent C] Validating code...")

    feedback = validate_code(state["code"], state["requirements"])

    issues = feedback.get("issues", [])

    return {
        "issues": issues,
        "messages": [f"[Agent C] Found {len(issues)} issues"]
    }


# Execute Tests


def execute_tests_node(state: AgentState):
    print(" Executing final tests...")

    test_file = "output/tests/test_generated.py"
    os.makedirs("output/tests", exist_ok=True)

    with open(test_file, "w", encoding="utf-8") as f:
        f.write(state["code"])

    results = run_tests(test_file, "output")

    return {
        "test_results": results,
        "messages": ["[Executor] Tests completed"]
    }

# Control Logic

def should_continue(state: AgentState):
    if len(state.get("issues", [])) == 0 or state.get("attempt", 0) >= 2:
        return "execute_tests"
    return "agent_b"


# Build Workflow


def build_workflow():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("agent_a", agent_a_node)
    workflow.add_node("agent_k", agent_k_node)  
    workflow.add_node("agent_b", agent_b_node)
    workflow.add_node("agent_c", agent_c_node)
    workflow.add_node("execute_tests", execute_tests_node)

    # Flow
    workflow.add_edge(START, "agent_a")
    workflow.add_edge("agent_a", "agent_k")      
    workflow.add_edge("agent_k", "agent_b")     
    workflow.add_edge("agent_b", "agent_c")

    workflow.add_conditional_edges(
        "agent_c",
        should_continue,
        {
            "agent_b": "agent_b",
            "execute_tests": "execute_tests"
        }
    )

    workflow.add_edge("execute_tests", END)

    return workflow.compile(checkpointer=MemorySaver())


# Main Execution

if __name__ == "__main__":
    app = build_workflow()

    initial_state = {
        "pdf_path": "SRS_Document.pdf",
        "requirements": {},
        "locators": {},  
        "code": "",
        "issues": [],
        "attempt": 0,
        "test_results": {},
        "messages": []
    }

    print(" Starting Multi-Agent Playwright Automation System\n")

    final = app.invoke(initial_state)

    report = {
        "total_attempts": final.get("attempt", 0),
        "final_issues": final.get("issues", []),
        "execution_status": final.get("test_results", {}).get("status"),
        "communication_log": final.get("messages", [])
    }

    os.makedirs("output", exist_ok=True)

    with open("output/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    print(f"\n Done! Total attempts: {final.get('attempt', 0)}")
    print(f"Final status: {final.get('test_results', {}).get('status')}")
    print(" Report: output/report.json")
    print(" Test file: output/tests/test_generated.py")