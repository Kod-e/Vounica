"""Story service wrapper."""
from typing import List, Dict, Any
from app.services.common.common_base import BaseService
from app.infra.models.story import Story
from app.infra.repo.story_repository import StoryRepository
from langchain_core.messages import SystemMessage, HumanMessage
from app.infra.context import uow_ctx
from app.llm.client import chat_completion, LLMModel

class StoryService(BaseService[Story]):
    """Service for Story entity."""

    def __init__(self):
        self._uow = uow_ctx.get()
        self._repo : StoryRepository = StoryRepository(db=self._uow.db)
        super().__init__(self._repo)
        
    async def create(self, data: Dict[str, Any]) -> Story:
        """Create a new story."""
        # 查看data的summary是否为空, 并且content存在而且不为空
        if data.get("summary") == "" or data.get("summary") is None and data.get("content") and data.get("content") != "":
            # 调用LLM生成summary和content
            response = await chat_completion(
                model_type=LLMModel.HIGH,
                input=[
                    SystemMessage(content="You are a user's story summary generator, you need to summarize the user's input to a String(256), and keep the user's intention as much as possible, if the story is short, return the whole story, only ensure the final length is less than 256 characters"),
                    HumanMessage(content=data.get("content"))
                ]
            )
            data["summary"] = response.content
        # 调用LLM生成summary和content
        return await super().create(data)
        
    async def get_user_stories(self, offset: int = 0, limit: int = 100, only_target_language: bool = False) -> List[Story]:
        """Get the user's stories."""
        return await self._repo.get_user_stories(
            user_id=self._uow.current_user.id,
            offset=offset,
            limit=limit,
            language=self._uow.target_language if only_target_language else None
        )
        
    # 获得用户所有故事的category
    async def get_user_story_categories(self) -> List[str]:
        """Get the user's all story categories."""
        return await self._repo.get_user_story_categories(
            user_id=self._uow.current_user.id
        )
    
    # 从Category中获取故事list
    async def get_story_by_category(self, category: str, limit: int = 50, offset: int = 0) -> List[Story]:
        """Get the user's stories by category."""
        return await self._repo.get_story_by_category(
            user_id=self._uow.current_user.id,
            category=category,
            limit=limit,
            offset=offset
        )
        
    # 获取数据库里关于User Story数量的统计
    async def get_user_story_count_prompt_for_agent(self) -> str:
        """Get the user's story count prompt for agent."""
        result_str = "#User's Story Count\n"
        count_dict = await self._repo.get_category_counts(
            user_id=self._uow.current_user.id
        )
        if len(count_dict) == 0:
            result_str += "No Any story\n"
        else:
            for category, count in count_dict.items():
                result_str += f"{category}: {count}\n"
        return result_str

    # 获取用户最重要的N条story的summar, 并且分类
    async def get_user_story_summary_prompt_for_agent(self, limit: int = 150) -> str:
        """Get the user's most important stories summary."""
        result_dict = {}
        # 利用StoryRepository获取用户最重要的几条story
        stories = await self._repo.get_story_by_language(
            user_id=self._uow.current_user.id,
            language=self._uow.target_language,
            limit=limit
        )
        result_str = "#User's Story Summary\n"
        result_str += f"ID|Time|Summary|Language ISO 639-1(if is not from target language, it will be show, if is from target language, it will be hidden)\n"
        if len(stories) == 0:
            result_str += "No Any story\n"
            return result_str
        for story in stories:
            # 检测result_dict里是否存在story.category, 如果不存在, 则添加
            if story.category not in result_dict:
                result_dict[story.category] = []
            # 添加story.summary到result_dict[story.category]
            # 如果不是当前语言, 后方添加来自其他语言
            if story.language != self._uow.target_language:
                result_dict[story.category].append(
                    f"{story.id}|{story.updated_at.strftime('%Y-%m-%d')}|{story.summary}|{story.priority}|THIS STORY IS FROM {story.language}"
                )
            else:
                result_dict[story.category].append(
                    f"{story.id}|{story.updated_at.strftime('%Y-%m-%d')}|{story.summary}|{story.priority}"
            )
        # 遍历result_dict的key
        for category, stories in result_dict.items():
            result_str += f"##{category}\n"
            for story in stories:
                result_str += f"{story}\n"
        return result_str
__all__ = ["StoryService"] 