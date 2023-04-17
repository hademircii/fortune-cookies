import hashlib
import math
import re
from typing import List, Tuple
from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    Depends,
    APIRouter,
    Body,
    Query,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings, validator
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, asc
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    api_key: str = "not_a_real_key"


settings = Settings()


engine = create_engine(settings.database_url)

Session = sessionmaker(bind=engine)

Base = declarative_base()


class AuthorModel(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    quotes = relationship("QuoteModel", back_populates="author")


class HashMixIn:
    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()


class QuoteModel(HashMixIn, Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"), index=True)
    text = Column(String)
    hashed_text = Column(String, unique=True)
    reference = Column(String)

    author = relationship(
        "AuthorModel", back_populates="quotes", lazy="joined"
    )

    @classmethod
    def create(cls, text: str, author_id: int, reference: str):
        return cls(
            text=text,
            author_id=author_id,
            reference=reference,
            hashed_text=cls.hash_text(text),
        )


class PhoneNumberModel(HashMixIn, Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True)
    # TODO: don't store phone numbers in plaintext.
    phone_number = Column(String, unique=True, index=True)
    hashed_phone_number = Column(String, unique=True, index=True)

    @classmethod
    def create(cls, phone_number: str):
        return cls(
            phone_number=phone_number,
            hashed_phone_number=cls.hash_text(phone_number),
        )


Base.metadata.create_all(bind=engine)


class Author(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class BaseQuote(BaseModel):
    text: str
    reference: str


class CreateQuote(BaseQuote):
    author: str


class Quote(BaseQuote):
    id: int
    author: Author

    class Config:
        orm_mode = True


class CreatePhoneNumber(BaseModel):
    phone_number: str

    @validator("phone_number")
    def validate_phone_number(cls, phone_number):
        pattern = re.compile("^[0-9]{10,15}$")
        if not pattern.match(phone_number):
            raise ValueError("Invalid phone number format")
        return phone_number


class PhoneNumber(BaseModel):
    id: int
    phone_number: str

    class Config:
        orm_mode = True


class PhoneNumbersPagination(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    results: List[PhoneNumber]

    class Config:
        orm_mode = True


async def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


async def verify_api_key(api_key: str = Header(...)) -> bool:
    if api_key == settings.api_key:
        return True
    raise HTTPException(status_code=401, detail="Invalid API key")


def get_random_quote(db: Session) -> QuoteModel:
    return db.query(QuoteModel).order_by(func.random()).first()


router = APIRouter(
    prefix="/quotes",
    tags=["quotes"],
    dependencies=[Depends(verify_api_key)],
)

quote_example = {
    "text": "Emergencies have always been the pretext on which the safeguards of individual liberty have been eroded",
    "author": "Friedrich Hayek",
    "reference": "The Road to Serfdom (1944)",
}


@router.post("/create", status_code=200, response_model=Quote)
async def create_quote(
    quote: CreateQuote = Body(..., example=quote_example),
    db: Session = Depends(get_db),
):
    author = db.query(AuthorModel).filter_by(name=quote.author).first()
    if not author:
        author = AuthorModel(name=quote.author)
        db.add(author)
        db.commit()

    hashed_text = QuoteModel.hash_text(quote.text)
    existing_quote = (
        db.query(QuoteModel).filter_by(hashed_text=hashed_text).first()
    )
    if existing_quote:
        raise HTTPException(status_code=409, detail="Quote already exists")

    new_quote = QuoteModel(
        text=quote.text,
        author_id=author.id,
        reference=quote.reference,
        hashed_text=hashed_text,
    )
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote


@router.get("/random", status_code=200, response_model=Quote)
async def random_quote(db: Session = Depends(get_db)):
    quote = get_random_quote(db)
    if not quote:
        raise HTTPException(status_code=404, detail="No quotes found")
    return quote


app.include_router(router)

router = APIRouter(
    prefix="/listeners",
    tags=["listeners"],
    dependencies=[Depends(verify_api_key)],
)

phone_number_example = {"phone_number": "18319111234"}


@router.post("/create", status_code=200, response_model=PhoneNumber)
async def register_phone_number(
    phone_number: CreatePhoneNumber = Body(..., example=phone_number_example),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    hashed_phone_number = PhoneNumberModel.create(phone_number.phone_number)

    existing_phone_number = (
        db.query(PhoneNumberModel)
        .filter_by(hashed_phone_number=hashed_phone_number.hashed_phone_number)
        .first()
    )

    if existing_phone_number:
        raise HTTPException(
            status_code=409, detail="Phone number already exists"
        )

    db.add(hashed_phone_number)
    db.commit()
    db.refresh(hashed_phone_number)
    return hashed_phone_number


async def get_pagination_params(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
) -> Tuple[int, int]:
    offset = (page - 1) * page_size
    limit = page_size
    return offset, limit


@router.get("/", response_model=PhoneNumbersPagination)
async def read_phone_numbers(
    db: Session = Depends(get_db),
    pagination: Tuple[int, int] = Depends(get_pagination_params),
) -> List[PhoneNumberModel]:
    offset, limit = pagination
    query = (
        db.query(PhoneNumberModel)
        .order_by(asc(PhoneNumberModel.id))
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_records = db.query(func.count(PhoneNumberModel.id)).scalar()
    total_pages = math.ceil(total_records / limit)

    return {
        "page": (offset // limit) + 1,
        "page_size": limit,
        "total_pages": total_pages,
        "total_records": total_records,
        "results": query,
    }


app.include_router(router)
