# app/models.py
# SQLAlchemy ORM 모델 (2.0 Mapped 스타일)
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config import Base


class Company(Base):
    __tablename__ = "companies"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True, index=True)
    corp_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stock_code: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    modify_date: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    financial_reports: Mapped[List["FinancialReport"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    corp_code: Mapped[str] = mapped_column(ForeignKey("companies.corp_code"), nullable=False, index=True)
    bsns_year: Mapped[str] = mapped_column(String(4), nullable=False, index=True)
    reprt_code: Mapped[str] = mapped_column(String(5), nullable=False)
    sj_div: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Mapped 스타일로 통일
    account_nm: Mapped[str] = mapped_column(String(100), nullable=False)
    thstrm_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="financial_reports")