import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "deepseek/deepseek-v4-flash-0731"
)