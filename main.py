# Python import
from asyncio import timeout
from datetime import time
import os
from typing import Any

# Library import
from fastapi import FastAPI, HTTPException, Request
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import A2A, AgentCard, SendMessageRequest, MessageSendParams
from fastapi.responses import JSONResponse
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
import uvicorn
from dotenv import load_dotenv
import httpx
from uuid import uuid4

# Module import
from schemas import PhraseSchema
from a2a_setup import a2a_app


load_dotenv()

PORT = int(os.getenv("PORT", 5000))


app = FastAPI(
        title="Grammar AI Agent", 
        description="Integrating an AI agent with telex.im that helps user to check for sentence errors",
        version="1.0.0"
        )

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

#--------------------------------------
# a2a sub app mounting with fastapi app
#--------------------------------------
app.mount("/a2a", a2a_app.build())

@app.post("/grammar-check")
async def grammar_check(request: Request, phrase: PhraseSchema):
    """ Main endpoint that handles ai agent operations"""

    base_url = str(request.base_url).replace("http://", "https://")
    a2a_url = f"{base_url}a2a/"


    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as httpx_client:
        resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=a2a_url
                )
        final_agent_card_to_use: AgentCard | None = None
        try:
            _public_card = await resolver.get_agent_card()
            final_agent_card_to_use = _public_card
        except Exception as e:
            raise HTTPException(status_code=404, detail="Failed to fetch the public agent card")
        grammar_agent_client = A2AClient(
                httpx_client=httpx_client, agent_card=final_agent_card_to_use
                )
        print("Client Initialized")


        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': f'{phrase.sentence}'}
                ],
                'messageId': uuid4().hex,
            },
        }
        a2a_request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await grammar_agent_client.send_message(a2a_request)
        data = response.model_dump(mode='json', exclude_none=True)

        return JSONResponse(status_code=200, content=data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
