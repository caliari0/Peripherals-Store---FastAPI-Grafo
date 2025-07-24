from grafo.trees import AsyncTreeExecutor, Node
from app.core.ports.llm_port import LLMPort
from typing import Type, TypeVar, Callable
from pydantic import BaseModel
from app.core.ports.formatter_port import FormatterPort
from pathlib import Path
from app.core.workflows.intention_models import UserIntention, InfoIntention, ComboIntention
from app.core.services.tag_service import TagService
from app.database import get_db
from sqlmodel import select
from app.models import Product

T = TypeVar("T", bound=BaseModel)


class IntentionWorkflow():   
    def __init__(self, llm_adapter: LLMPort, formatter_adapter: FormatterPort):
        self.llm = llm_adapter
        self.formatter = formatter_adapter

    def __str__(self):
        return f"IntentionWorkflow(llm={self.llm}, formatter={self.formatter})"

    def _get_available_tags(self) -> list[str]:
        """Get all available tags from the database"""
        session = next(get_db())
        tag_service = TagService(session)
        return tag_service.get_all_existing_tags()

    def _get_available_products(self) -> list[str]:
        """Get all available product names from the database"""
        session = next(get_db())
        products = session.exec(select(Product)).all()
        return [product.name for product in products]

    async def _task(self,
        file_name: str, 
        response_model: Type[T],
        **kwargs: dict
    ) -> T:
        """
        This task is responsible for rendering the developer and user messages,
        and sending them to the LLM.
        """
        # 1. build messages
        path = f"{str(Path(__file__).parent)}/{file_name}"
        developer, user = self.formatter.render(
            path=path,
            input={
                "developer": {**kwargs},
                "user": {**kwargs},
            },
        )
        messages: list = [
            {"role": "system", "content": developer},
            {"role": "user", "content": user},
        ]

        return await self.llm.asend(
            messages=messages,
            response_model=response_model,
        )

    async def _redirect_workflow(self, source_node: Node[UserIntention], info_node: Node, combo_node: Node[list]):
        if source_node.output is None:
            raise ValueError("Source node output is None")
            
        if isinstance(source_node.output.intention, InfoIntention):
            # Keep info node, disconnect combo node
            await source_node.disconnect(combo_node)
        elif isinstance(source_node.output.intention, ComboIntention):
            # Keep combo node, disconnect info node
            await source_node.disconnect(info_node)



    async def run(self, message: str, get_product_callback: Callable[[str], any], get_combo_callback) -> list[Node]: 
        # Get available tags and products for the LLM
        available_tags = self._get_available_tags()
        available_products = self._get_available_products()
        
        # 1. build tree
        intention_node = Node[UserIntention](
            uuid="intention node",
            coroutine=self._task,
            kwargs=dict(
                file_name="intention.yaml",
                response_model=UserIntention,
                message=message,
                available_tags=available_tags,
                available_products=available_products,
            )
        ) 
        
        # 2. build nodes
        info_node = Node(
            uuid="info node",
            coroutine=get_product_callback,
            kwargs=dict(
                product_name=lambda: intention_node.output.intention.completed_product_name or intention_node.output.intention.product_name,
            )
        )
        
        combo_node = Node[list](
            uuid="combo node",
            coroutine=get_combo_callback,
            kwargs=dict(
                tag=lambda: intention_node.output.intention.tag,
            )
        )

        intention_node.on_after_run = (
            self._redirect_workflow, 
            dict(
                source_node=intention_node,
                info_node=info_node,
                combo_node=combo_node,
            )
        )
        # 3. connect nodes
        await intention_node.connect(info_node)
        await intention_node.connect(combo_node)

        # 4. build tree executor
        tree_executor = AsyncTreeExecutor(
            roots=[intention_node],
        )

        # 5. run tree executor
        return await tree_executor.run()
        









# create a new node that consults the taglist
# inject literals into taglist
# create a new node that injects the literals into the taglist
