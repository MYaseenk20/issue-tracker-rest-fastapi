from dotenv import load_dotenv

from app.agent.tools.create_issue_tool import create_issue_tool
from app.agent.tools.update_issue_tool import update_issue_tool

load_dotenv()
from langchain.agents import create_agent
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import create_retriever_tool
from langchain_ollama import ChatOllama  # Changed import

class AgentService:
    def __init__(self):
        self.agent = self._build_agent()

    def _build_agent(self):
        llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
        )

        tools = [create_issue_tool,update_issue_tool]

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="""You are an issue agent that can CREATE or UPDATE issues by calling tools.

            Intent routing:
            - If the user describes a new bug/issue => call create_issue_tool
            - If the user says update/modify/change and includes an id (issue#12, issue 12, ticket-12) => call update_issue_tool

            Allowed enums:
            - priority: low | medium | high
            - status: open | in_progress | closed

            UPDATE rules:
            - MUST extract issue_id (int). Never guess it.
            - Put only changed fields into the "updates" dict.
            - If user says "medium to high" / "from medium to high" => {"priority": "high"}
            - If user says "open to in_progress" => {"status": "in_progress"}
            - If user says "close it" / "mark as closed" => {"status": "closed"}
            - If user says "add tag X" => {"tags": [...]} ONLY if they mean replace; otherwise you can ask
              Prefer: if user says "add tag", use {"tags": existing+new} is not possible without DB,
              so store as {"tags": ["x"]} only if user explicitly says "set tags to ...".
            - Return ONLY the tool result.

            CREATE rules:
            - Use fields: title, description, priority, status, tags, root_cause_hint, estimated_minutes
            - make description from user query
            - If urgency/blocking implied => priority="high"
            - **tags MUST be a list of strings, e.g., ["bug", "urgent"]. Use empty list [] if no tags.**
            - root_cause_hint: you should give a hint according to user prompt
            - Return ONLY the tool result.
            """
        )
        return agent

    def process_chat(self,user_input,chat_history):
        """Process a chat message and return the response"""

        # Only keep last 2-4 messages for context
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        message = recent_history + [HumanMessage(content=user_input)]

        response = self.agent.invoke({
            "messages": message,
        })

        # Extract tool results
        tool_result = None
        tools_used = []

        # Extract tools used
        for msg in response["messages"]:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tools_used.append(tool_call['name'])

            # Check for tool messages (results from tool execution)
            if hasattr(msg, 'type') and msg.type == 'tool':
                tool_result = msg.content

        if tools_used:
            print(f"\n🔧 Tools Used: {', '.join(set(tools_used))}\n")

        return {
            "content": response["messages"][-1].content,
            "tool_result": tool_result,
            "tools_used": tools_used
        }

if __name__ == "__main__":
    agent = AgentService()
    response = agent.process_chat(
        user_input="Internet is working but website is giving 402 error",
        chat_history=[]
    )

    print(response)
