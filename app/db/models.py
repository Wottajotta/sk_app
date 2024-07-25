from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from datetime import datetime
from typing import List


class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(40), nullable=True)
    number: Mapped[str] = mapped_column(String(20), nullable=True)
    

class Region(Base):
    __tablename__ = 'regions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=True)
    

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    
#Дополнить    
class Series(Base):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    
# Дополнить
class Additionally(Base):
    __tablename__ = "additionally"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
 
    
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id"), nullable=True)
    
    
class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column(String(128), nullable=True)
    category: Mapped[str] = mapped_column(String(25), nullable=True)
    series: Mapped[str] = mapped_column(String(25), nullable=True)
    product = Mapped[str] = mapped_column(String(256), nullable=True)
    add = mapped_column(BigInteger)
        
    


    