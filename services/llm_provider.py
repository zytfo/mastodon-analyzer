# stdlib
import json
import re
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator, Dict, Tuple

# thirdparty
import anthropic
import google.generativeai as genai
from openai import AsyncOpenAI

from settings import get_settings

settings = get_settings()


class LLMModel(str, Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LLAMA = "llama"


class LLMProvider:
    def __init__(self):
        # OpenAI
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Anthropic Claude
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Google Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')

        # Together AI for Llama
        self.llama_client = AsyncOpenAI(
            api_key=settings.TOGETHER_API_KEY,
            base_url="https://api.together.xyz/v1"
        )

    def build_prompt(self, status: dict) -> str:
        current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        return f"""
You are an expert in social media content analysis with specialized knowledge in detecting AI-generated or suspicious
posts.
Your task is to analyze the following Mastodon post and evaluate whether it is likely suspicious or AI-generated.

**Current Date and Time:** {current_date}

**Post Analysis Details:**

1. **Post Text:**
   "{status['content']}"

2. **Author Details:**
   - Number of followers: {status['author_followers_count']}
   - Number of followings: {status['author_following_count']}
   - Total posts written by the author: {status['author_statuses_count']}
   - Date of registration: {status['author_created_at']}

3. **Post Metadata:**
   - Hashtags used in the post: check hashtags in the post text

**Guidelines for Evaluation:**
- Consider whether the post text contains patterns commonly found in AI-generated content
- Assess the author's activity profile (registration date, posting frequency, follower ratio)
- Examine the hashtags: Are they relevant or spammy?
- Combine all factors to determine the likelihood of being suspicious

**Response Format (JSON ONLY):**
{{
    "is_suspicious": true/false,
    "confidence": 0.0-1.0,
    "likelihood": "Low/Medium/High",
    "reasoning": "detailed explanation based on the parameters",
    "red_flags": ["flag1", "flag2", ...]
}}

Confidence scale:
- 0.9-1.0: Very certain
- 0.7-0.89: Confident
- 0.5-0.69: Moderately confident
- 0.3-0.49: Uncertain
- 0.0-0.29: Very uncertain
"""

    async def analyze_openai(self, status: dict) -> AsyncGenerator[str, None]:
        prompt = self.build_prompt(status)

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant skilled in analyzing social media posts. Always respond "
                               "with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True,
            temperature=0.3
        )

        accumulated = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                accumulated += content
                yield accumulated

    async def analyze_claude(self, status: dict) -> AsyncGenerator[str, None]:
        prompt = self.build_prompt(status)

        accumulated = ""
        async with self.anthropic_client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
        ) as stream:
            async for text in stream.text_stream:
                accumulated += text
                yield accumulated

    async def analyze_gemini(self, status: dict) -> AsyncGenerator[str, None]:
        prompt = self.build_prompt(status)

        generation_config = genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=2000,
        )

        response = await self.gemini_model.generate_content_async(
            prompt,
            generation_config=generation_config,
            stream=True
        )

        accumulated = ""
        async for chunk in response:
            if chunk.text:
                accumulated += chunk.text
                yield accumulated

    async def analyze_llama(self, status: dict) -> AsyncGenerator[str, None]:
        prompt = self.build_prompt(status)

        response = await self.llama_client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant skilled in analyzing social media posts. Always respond "
                               "with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True,
            temperature=0.3,
            max_tokens=2000
        )

        accumulated = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                accumulated += content
                yield accumulated

    async def analyze(self, status: dict, model: LLMModel) -> AsyncGenerator[str, None]:
        if model == LLMModel.OPENAI:
            async for result in self.analyze_openai(status):
                yield result
        elif model == LLMModel.CLAUDE:
            async for result in self.analyze_claude(status):
                yield result
        elif model == LLMModel.GEMINI:
            async for result in self.analyze_gemini(status):
                yield result
        elif model == LLMModel.LLAMA:
            async for result in self.analyze_llama(status):
                yield result
        else:
            raise ValueError(f"Unknown model: {model}")


def extract_json_and_confidence(text: str) -> Tuple[Dict, float, bool]:
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            confidence = float(data.get('confidence', 0.5))
            is_suspicious = bool(data.get('is_suspicious', False))
            return data, confidence, is_suspicious
    except (json.JSONDecodeError, ValueError):
        pass

    text_lower = text.lower()

    is_suspicious = any(word in text_lower for word in [
        'suspicious', 'fake', 'bot', 'artificial', 'generated',
    ])

    if any(word in text_lower for word in ['definitely', 'clearly', 'certain', 'obvious']):
        confidence = 0.9
    elif any(word in text_lower for word in ['likely', 'probably', 'appears']):
        confidence = 0.7
    elif any(word in text_lower for word in ['possibly', 'might', 'could']):
        confidence = 0.5
    else:
        confidence = 0.6

    return {}, confidence, is_suspicious
