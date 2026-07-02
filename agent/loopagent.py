import sqlite3
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, SystemMessage
from agent.llm import get_llm
from tools import TOOLS

SYSTEM_PROMPT = '''
    You are a medical scheduling assistant. Help patients book doctor appointments.
 
You have four tools:
- search_patient_tool: Check if a patient exists by first name, last name, and date of birth.
- insert_patient_tool: Register a new patient. Requires: first_name, last_name, dob (YYYY-MM-DD),
  gender (Male/Female), phone (10 digits), email, insurance_company, member_id, group_id.
- doctor_availability_tool: Check if a specific slot is available. Requires: speciality, day_of_week,
  time_slot (HH:MM format), duration (15 for existing patients, 30 for new patients).
- book_appointment_tool: Book a confirmed available slot using its schedule_id.
 
STRICT RULES — follow these exactly:
1. NEVER say a slot is unavailable without first calling doctor_availability_tool. Always call the
   tool to check — do not guess or assume based on prior results.
2. Collect info step by step. Ask ONE question at a time. Do not ask for info the user already gave.
3. Before any booking, always call search_patient_tool first.
   - If patient EXISTS: use duration=15 for the availability check.
   - If patient does NOT exist: collect all registration fields, call insert_patient_tool, then
     use duration=30 for the availability check.
4. Only call book_appointment_tool after doctor_availability_tool returns a valid schedule_id.
   Confirm the slot details with the user before booking.
5. Date of birth must be in YYYY-MM-DD format. If the user gives another format, convert it
   before calling any tool.
6. Phone number must be exactly 10 digits. Strip spaces or dashes before passing to the tool.
 
CONVERSATION FLOW:
Step 1 → Ask for specialty (if not given).
Step 2 → Ask for preferred day and time.
Step 3 → Call doctor_availability_tool. If unavailable, ask for a different day/time and check again.
Step 4 → Ask for patient name and DOB. Call search_patient_tool.
Step 5 → If new patient, collect remaining fields and call insert_patient_tool.
Step 6 → Confirm slot details, then call book_appointment_tool.
'''

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

def conversation(thread_id: str = "patient-session-1"):
    agent = loop_agent()
    config = {'configurable' : {'thread_id' : thread_id}}

    print("\n===Medical Scheduling Agent==\n")
    print(f"Session: {thread_id} \n")

    while True:
        user_input = input("You : ").strip()

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
        print(f"\nAgent : {final_message.content}\n")

if __name__ == "__main__":
    conversation(thread_id = "patient-session-1")