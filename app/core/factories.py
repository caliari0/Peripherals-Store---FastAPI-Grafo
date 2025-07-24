from app.core.services.order_service import OrderService
from app.core.services.setup_service import SetupService
from app.core.services.stock_service import StockService
from app.core.services.tag_service import TagService
from app.database import get_db
from app.core.use_cases.sales_use import SalesUseCase
from app.core.use_cases.stock_use import StockUseCase
from app.core.use_cases.tag_use import TagUseCase
from fastapi import Depends
from sqlmodel import Session
from app.adapters.jinja2_adapter import Jinja2Adapter
from app.adapters.instructor_adapter import InstructorAdapter
from app.adapters.type_adapter import TypeAdapter


def get_formatter_adapter():
    return Jinja2Adapter()


def get_llm_adapter():
    return InstructorAdapter()


def get_type_adapter():
    return TypeAdapter()


def get_sales_use_case(db: Session = Depends(get_db)):
    return SalesUseCase(
        session=db,
        order_service=OrderService(session=db),
        setup_service=SetupService(session=db),
        stock_service=StockService(session=db),
        type_adapter=TypeAdapter(),
    )


def get_stock_use_case(db: Session = Depends(get_db)):
    return StockUseCase(
        session=db,
        stock_service=StockService(session=db),
        tag_service=TagService(session=db),
        type_adapter=TypeAdapter(),
    )


def get_tag_use_case(db: Session = Depends(get_db)):
    return TagUseCase(session=db, tag_service=TagService(session=db))
