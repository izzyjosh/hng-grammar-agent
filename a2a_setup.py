# Python import 

# Library import 
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication

# Module import
from schemas import GrammarResponse
from agent.agent_executor import GrammarAgentExecutor


skill = AgentSkill(
        id="grammar_corrector",
        name="Grammatical Correction",
        description="Takes a sentense and check for grammatical error, if any it gives the correction",
        tags=["Grammar", "Correction", "Word"],
        examples=["what is me name?", "response: what is my name ?"]
        )


public_agent_card = AgentCard(
        name="Grammar Corrector Agent",
        description="An agent that corrects grammatical errors in inputed sentences",
        url="http://localhost:5001/a2a/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill]
        )


request_handler = DefaultRequestHandler(
        agent_executor=GrammarAgentExecutor(),
        task_store=InMemoryTaskStore()
        )


a2a_app = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
        )
