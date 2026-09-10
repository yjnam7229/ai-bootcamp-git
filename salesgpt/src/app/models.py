# models.py
# SQLAlchemy ORM 모델
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.config import Base

# corp_code	고유번호
# stock_code 종목코드
# corp_name	 종목명(법인명)
class Company(Base):
    __tablename__ = "companies"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True, index=True)
    corp_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stock_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    modify_date: Mapped[str | None] = mapped_column(String(8), nullable=True)

    financial_reports: Mapped[list["FinancialReport"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    corp_code: Mapped[str] = mapped_column(ForeignKey("companies.corp_code"), nullable=False)
    bsns_year: Mapped[str] = mapped_column(String(4), nullable=False)
    reprt_code: Mapped[str] = mapped_column(String(5), nullable=False)
    account_nm: Mapped[str] = mapped_column(String(100), nullable=False)
    thstrm_amount: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="financial_reports")