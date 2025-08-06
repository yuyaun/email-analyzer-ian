import json
import os

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.core.database import AsyncSessionLocal
from app.models.magic_task_result import MagicTaskResult


def get_title_optimize_chain():
    prompt = ChatPromptTemplate.from_template(
        "你是一個郵件行銷助手，請根據內容優化標題並判斷情感與是否為垃圾訊息。"
        "以 JSON 格式回傳，包含 title, sentiment, is_spam。內容: {content}"
    )
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return prompt | llm


chain_map = {
    "title_optimize": get_title_optimize_chain(),
}


async def handle_llm_task(message: str) -> None:
    data = json.loads(message)
    chain = chain_map.get(data.get("magicType"))
    if chain is None:
        return
    raw = (await chain.ainvoke({"content": data.get("content", "") })).content
    result = json.loads(raw)
    if AsyncSessionLocal is None:
        return
    async with AsyncSessionLocal() as db:
        record = MagicTaskResult(
            campaign_sn=data.get("campaignSn"),
            magic_type=data.get("magicType"),
            result=result,
        )
        db.add(record)
        await db.commit()
