from langchain_core.messages import HumanMessage, ToolMessage
from agent.llm import get_llm
from tools import TOOLS

def agent(user_input : str):
    llm = get_llm()
    llm_with_tools = llm.bind_tools(TOOLS)
    tool_map = {t.name: t for t in TOOLS}

    messages = [HumanMessage(content=user_input)]

    print("User Input : ")
    print(messages)

    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    print("RAW LLM Message : ")
    print(ai_msg.content)
    print(ai_msg.tool_calls)

    if not ai_msg.tool_calls:
        print(ai_msg.content)
        return

    for call in ai_msg.tool_calls:
        name = call["name"]
        args = call["args"]
        call_id = call["id"]

        print(name, args)

        if name not in tool_map:
            result = {"status" : False, "message" : f"Unknown tool : {name}"}
        
        else:
            try:
                result = tool_map[name].invoke(args)
            except Exception as e:
                result = {'status' : False, 'message' : f"Tool execution error {e}"}

        print(result)

        messages.append(
            ToolMessage(
                content = str(result),
                tool_call_id = call_id
            )
        )

    final_msg = llm_with_tools.invoke(messages)

    return final_msg.content
