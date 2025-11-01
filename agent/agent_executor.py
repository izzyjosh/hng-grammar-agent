# Python import 
import json

# Library import
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from a2a.utils.errors import ServerError
from a2a.types import InternalError, UnsupportedOperationError, InvalidParamsError

# Module import
from agent.agent import GrammarAgent


class GrammarAgentExecutor(AgentExecutor):
    
    def __init__(self):
        self.agent = GrammarAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        try:
            phrase = context.get_user_input()
            if not phrase and not context.message:
                raise ServerError(error=InvalidParamsError())

            response = await self.agent.run(phrase)
            await event_queue.enqueue_event(new_agent_text_message(json.dumps(response)))
        except Exception as e:
            raise ServerError(error=InternalError())

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise ServerError(error=UnsupportedOperationError())
