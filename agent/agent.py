# Python import
import os

# Library import 
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException

# Module import
from schemas import GrammarResponse

load_dotenv()


GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
print(GOOGLE_API_KEY)
class GrammarAgent:
    SYSTEM_INSTRUCTIONS = (
            "You are a specialized assistant that helps users correct grammar, spelling, "
            "and phrasing mistakes in text"
            "Your goal is to return correct sentence and explanation"
            "If users provides unrelated questions, politely state that you can only help with grammar or writing task"
            )

    def __init__(self):
    
        provider = GoogleProvider(api_key=GOOGLE_API_KEY)
        if not provider:
            raise HTTPException(status_code=404, detail="no api key")
        model = GoogleModel("gemini-2.0-flash", provider=provider)

        self.agent = Agent(
                model=model,
                output_type=GrammarResponse,
                system_prompt=self.SYSTEM_INSTRUCTIONS
                )

    async def run(self, phrase: str):
        try:
            response = await self.agent.run(user_prompt=phrase)

            return response.output.model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Something went wrong")
