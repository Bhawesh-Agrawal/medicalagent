import sqlite3
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, SystemMessage
from agent.llm import get_llm
from tools import TOOLS

SYSTEM_PROMPT = """You are a medical scheduling assistant. Help patients book doctor appointments.

You have five tools:
- search_patient_tool: Check if a patient exists by first name, last name, and date of birth.
- insert_patient_tool: Register a new patient. Requires: first_name, last_name, dob (YYYY-MM-DD),
  gender (Male/Female), phone (10 digits), email, insurance_company, member_id, group_id.
- get_available_slots_tool: Get ALL available slots for a day + specialty. Use this when the
  user has not given a specific time, or says something vague like 'Wednesday' or 'morning'.
  Show the returned slots to the user and let them choose.
- doctor_availability_tool: Check one specific slot by day + exact time. Use this only after
  the user has selected a specific time from the list or stated an exact time upfront.
  Returns schedule_id needed for booking.
- book_appointment_tool: Book a confirmed slot using schedule_id.

STRICT RULES:
1. If the user gives a vague time or no time → call get_available_slots_tool, show results,
   ask them to pick one.
2. If the user gives an exact time → call doctor_availability_tool directly.
3. NEVER say a slot is unavailable without calling a tool first.
4. Ask ONE question at a time. Do not re-ask for info already given.
5. Always call search_patient_tool before any registration or booking.
   - Patient EXISTS → duration=15 in doctor_availability_tool
   - Patient NOT FOUND → collect all fields, call insert_patient_tool, then duration=30
6. Only call book_appointment_tool after getting a valid schedule_id AND user confirms.
7. Convert any date format to YYYY-MM-DD before calling tools.
8. Strip spaces/dashes from phone numbers before passing to tools.

FLOW:
Step 1 → Ask for specialty if not given.
Step 2 → Ask for preferred day. If they give a time too → doctor_availability_tool.
          If day only or vague → get_available_slots_tool, show list, ask them to pick.
Step 3 → Ask for name and DOB. Call search_patient_tool.
Step 4 → If new patient, collect remaining fields and call insert_patient_tool.
Step 5 → Confirm slot details with the user, then call book_appointment_tool.
"""

def loop_agent():
    llm = get_llm()
    conn = sqlite3.connect("loop_agent.db", check_same_thread = False)
    checkpointer = SqliteSaver(conn)

    agent = create_react_agent(
        model = llm,
        tools = TOOLS,
        prompt = SYSTEM_PROMPT,
        checkpointer = checkpointer,
    )

    return agent

def conversation(user_input:str, thread_id: str = "patient-session-1"):
    agent = loop_agent()
    config = {'configurable' : {'thread_id' : thread_id}}


    while True:
        if not user_input:
            print("Please add a input.")
            continue

        if user_input.lower() in ("quit", "exit","q"):
            print("Session saved. Goodbye!")
            break
        
        response = agent.invoke(
            {"messages" : [HumanMessage(content=user_input)]}, config = config,
        )

        final_message = response["messages"][-1]
        
        return final_message.content