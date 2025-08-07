import json
import os

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel, Field

from app.services.magic_task_result_service import create_magic_task_result
from app.core.logger import log_event


class TitleOptimizeResult(BaseModel):
    title: str = Field(description="優化後的郵件標題")
    sentiment: str = Field(description="郵件的情感")
    is_spam: bool = Field(description="是否為垃圾郵件")


def get_title_optimize_chain():
    output_parser = PydanticOutputParser(pydantic_object=TitleOptimizeResult)

    system_template = """
你是一個郵件行銷助手，請根據內容優化標題並判斷情感與是否為垃圾訊息。
只輸出 JSON，不要包含額外的說明。
"""

    human_template = """
{format_instructions}

內容：
{content}
"""

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(template=system_template, input_variables=[])
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=human_template,
                input_variables=["content", "format_instructions"],
            )
        ),
    ])

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    return (
        chat_prompt.partial(
            format_instructions=output_parser.get_format_instructions()
        )
        | llm
        | output_parser
    )


chain_map = {
    "title_optimize": get_title_optimize_chain(),
}


async def handle_llm_task(message: str) -> None:
    log_event("llm_handler", "handle_task", {"message": message})
    data = json.loads(message)
    chain = chain_map.get(data.get("magicType"))
    log_event("llm_handler", "chain_selected", {"magicType": data.get("magicType")})
    if chain is None:
        return

    result = await chain.ainvoke({"content": data.get("content", "")})

    log_event("llm_handler", "raw_response", {"raw": result.dict()})
    await create_magic_task_result(
        campaign_sn=data.get("campaignSn"),
        magic_type=data.get("magicType"),
        result=result.dict(),
    )

