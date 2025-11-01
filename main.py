# Python import
from asyncio import timeout
from datetime import time
import os
from typing import Any

# Library import
from fastapi import FastAPI, HTTPException
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import A2A, AgentCard, SendMessageRequest, MessageSendParams
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import httpx
from uuid import uuid4

# Module import
from schemas import PhraseSchema
from a2a_setup import a2a_app


load_dotenv()

PORT = int(os.getenv("PORT", 5001))
HOST = os.getenv("HOST", "127.0.0.1")


app = FastAPI(
        title="Grammar AI Agent", 
        description="Integrating an AI agent with telex.im that helps user to check for sentence errors",
        version="1.0.0"
        )

#--------------------------------------
# a2a sub app mounting with fastapi app
#--------------------------------------
app.mount("/a2a", a2a_app.build())

@app.post("/grammar-check")
async def grammar_check(phrase: PhraseSchema):
    """ Main endpoint that handles ai agent operations"""
    
    base_url = f"http://{HOST}:{PORT}/a2a/"

    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as httpx_client:
        resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=base_url
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
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await grammar_agent_client.send_message(request)
        data = response.model_dump(mode='json', exclude_none=True)

        return JSONResponse(status_code=200, content=data)

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
