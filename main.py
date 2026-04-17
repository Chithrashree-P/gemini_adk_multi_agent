# from workflow import build_workflow 

# if __name__ == "__main__": app = build_workflow() 

# initial_state = {
#                  #"pdf_path": " Capstonerequirements document (1).pdf",
#                  "pdf_path": "SRS_Document.pdf", 
#                  "requirements": "", 
#                  "code": "",
#                  "issues": [], 
#                  "attempt": 0, 
#                  "test_results": {}, 
#                  "messages": [] }

# final_state = app.invoke( initial_state,
#                           config={"configurable": {"thread_id": "1"}} )

# print("\n Project execution completed!") 

from workflow import build_workflow

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

    final_state = app.invoke(
        initial_state,
        config={"configurable": {"thread_id": "1"}}
    )

    print("\n Project execution completed!")