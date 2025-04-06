from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi import APIRouter
from routes.auth import validate_token  # Import token validation function
from langchain_community.utilities import SQLDatabase
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
router = APIRouter()


db = SQLDatabase.from_uri(
    database_uri="mysql+pymysql://root:Khi%402025@127.0.0.1:3306/oraaqdb"
)

from typing_extensions import TypedDict

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

import getpass
import os

# if not os.environ.get("OPENAI_API_KEY"):
#   os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")


if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key =openai_api_key)

from langchain import hub

query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
assert len(query_prompt_template.messages) == 1

query_prompt_template = query_prompt_template + "Instructions: -For greeting inputs, reply with greetings"

query_prompt_template.messages[0].pretty_print()

from typing_extensions import Annotated

class QueryOutput(TypedDict):
    """Generated SQL query."""

    query: Annotated[str, ..., "Syntactically valid SQL query."]

def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}

write_query({"question": "How many Users are there?"})

from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

def execute_query(state: State):
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

execute_query({"query": "SELECT COUNT(*) AS App_users FROM Appuser;"})

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)
graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

def function1(user_input):
    for step in graph.stream(
        {"question": user_input}, stream_mode="updates"
    ):
        print(step)
    return step  


# def function1(user_input):
#     """
#     Process user input to generate SQL queries, execute them, and return an answer.
#     If the result still contains SQL-like patterns, it loops until a final response is generated.
#     Returns all intermediate steps as well.
#     """
#     state = {"question": user_input}
#     steps = []  # Store all steps for debugging and tracing

#     while True:
#         step = None
#         for step in graph.stream(state, stream_mode="updates"):
#             print("Step Output:", step)
#             steps.append(step)  # Store each step
        
#         if not step:
#             return {"error": "No response generated", "steps": steps}
        
#         # Extract the response content
#         response = step.get("answer", "")

#         # Check if the response suggests additional SQL generation
#         if "sql'''" in response:
#             print("Detected SQL response, looping again...")
#             state["question"] = response  # Feed it back into the loop
#         else:
#             return {"response": response, "steps": steps}  # Return all steps with final answer


# @fastapi.get("/")
# def home():
#     return f"This is Home!"

class input_validate(BaseModel):
    user_input: str

@router.post("/sql")
def sql_function(request: Request, user_input1 : input_validate):
                # Validate token
    # if not validate_token(request):
    #     return JSONResponse(
    #         status_code=401,
    #         content={"status": "error", "message": "Invalid Access Token"}
    #     )
    
    try: 
        inp = user_input1.user_input
        responsee = function1(inp)
        print(responsee)
        return {"response":responsee}
    except Exception as e:
        print ("Exception:", {str(e)})