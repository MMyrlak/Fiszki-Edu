from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

# --- SCHEMATY UŻYTKOWNIKA (AUTH) ---

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Schemat wykorzystywany przy rejestracji użytkownika."""
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Schemat wykorzystywany przy logowaniu (SignIn)."""
    email: EmailStr
    password: str

class UserOut(UserBase):
    """Schemat zwracany przez API z profilem użytkownika."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- SCHEMATY TOKENÓW ---

class Token(BaseModel):
    """
    Para tokenów autentykacji i odświeżania.
    Wzorowane na schemacie TokensPair z Food Driver API.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Dane zaszyte wewnątrz tokena JWT."""
    email: Optional[str] = None

# --- SCHEMATY FISZEK ---

class FlashcardBase(BaseModel):
    question: str
    answer: str
    topic: str

class FlashcardCreateRequest(BaseModel):
    """
    Żądanie generowania fiszek przez AI.
    Pozwala zdefiniować tekst źródłowy oraz żądaną liczbę fiszek.
    """
    text: str = Field(..., 
                      min_length=10, 
                      max_length=50000,
                      description="Tekst, z którego AI ma przygotować fiszki"
                      )
    count: int = Field(default=10, ge=1, le=30, description="Liczba fiszek do wygenerowania")

class FlashcardUpdate(BaseModel):
    """Schemat do edycji pojedynczej fiszki (PATCH/PUT)."""
    question: Optional[str] = None
    answer: Optional[str] = None
    topic: Optional[str] = None

class FlashcardResponse(FlashcardBase):
    """Pełny schemat pojedynczej fiszki zwracany z bazy danych."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FlashcardListResponse(BaseModel):
    """
    Struktura odpowiedzi dla listy fiszek z pagynacją.
    Zastosowano nazewnictwo i logikę identyczną jak w Food Driver API.
    """
    count: int = Field(..., description="Całkowita liczba rekordów użytkownika")
    pages: int = Field(..., description="Całkowita liczba stron")
    currentPage: int = Field(..., description="Numer aktualnej strony")
    results: List[FlashcardResponse] = Field(..., description="Lista fiszek na danej stronie") 

    class Config:
        from_attributes = True