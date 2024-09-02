from sqlalchemy import DateTime, ForeignKey, String, BigInteger, func, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


from typing import List


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(40), nullable=True)
    number: Mapped[str] = mapped_column(String(20), nullable=True)
    

class Region(Base):
    __tablename__ = 'regions'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    
#Дополнить    
class Series(Base):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    category: Mapped[str] = mapped_column(String(25), nullable=True)
     
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=True)
    category: Mapped[str] = mapped_column(String(25), nullable=True)
    series: Mapped[str] = mapped_column(String(25), nullable=True)

    
class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(25), nullable=True)
    tg_id = mapped_column(BigInteger)
    region: Mapped[str] = mapped_column(String(128), nullable=True)
    category: Mapped[str] = mapped_column(String(25), nullable=True)
    series: Mapped[str] = mapped_column(String(25), nullable=True)
    product: Mapped[str] = mapped_column(String(120), nullable=True)
    additionally: Mapped[str] = mapped_column(String(512), nullable=True)
    images: Mapped[str] = mapped_column(Text, nullable=True)
    documents: Mapped[str] = mapped_column(Text, nullable=True)
    finish_documents: Mapped[str] = mapped_column(Text, nullable=True)
    