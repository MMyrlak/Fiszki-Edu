import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List

from app.database import get_db
from app.models import Flashcard, User
from app.schemas import (
    FlashcardCreateRequest, 
    FlashcardResponse, 
    FlashcardListResponse, 
    FlashcardUpdate
)
from app.auth.deps import get_current_user

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])

genai.configure(api_key="AIzaSyBbX3VHb4-g3mNaric-BBXHm4yzIyxISrA")
ai_model = genai.GenerativeModel('gemini-2.5-flash')


@router.post("/generate", response_model=List[FlashcardResponse], status_code=status.HTTP_201_CREATED)
def generate_flashcards(
    req: FlashcardCreateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tworzy zestaw fiszek na podstawie tekstu. 
    Użytkownik może określić liczbę fiszek (domyślnie 10)[cite: 5, 93].
    """
    prompt = f"""
    Zanalizuj tekst i stwórz dokładnie {req.count} fiszek (pytanie-odpowiedź).
    Nadaj całemu zestawowi jeden konkretny temat.
    Wynik zwróć wyłącznie jako JSON:
    {{
      "topic": "Nazwa Tematu",
      "flashcards": [ {{"question": "...", "answer": "..."}} ]
    }}
    Tekst: {req.text}
    """

    try:
        response = ai_model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        topic_name = data.get("topic", "Nowy Temat")
        
        new_cards = []
        for item in data.get("flashcards", []):
            card = Flashcard(
                question=item['question'],
                answer=item['answer'],
                topic=topic_name,
                user_id=current_user.id
            )
            db.add(card)
            new_cards.append(card)
        
        db.commit()
        for c in new_cards: db.refresh(c)
        return new_cards
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Błąd generowania AI")


@router.get("/", response_model=FlashcardListResponse)
def list_flashcards(
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pobiera wszystkie fiszki użytkownika z pagynacją."""
    limit = 10
    skip = (page - 1) * limit
    
    query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)
    total_count = query.count()
    results = query.offset(skip).limit(limit).all()
    
    return {
        "count": total_count,
        "pages": (total_count + limit - 1) // limit,
        "currentPage": page,
        "results": results
    }

@router.get("/topics", response_model=List[str])
def list_unique_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Zwraca unikalne tematy (kolekcje) użytkownika[cite: 166]."""
    topics = db.query(Flashcard.topic).filter(
        Flashcard.user_id == current_user.id
    ).distinct().all()
    return [t[0] for t in topics if t[0]]

@router.get("/topic/{topic_name}", response_model=List[FlashcardResponse])
def get_by_topic(
    topic_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pobiera fiszki z konkretnej kolekcji[cite: 200]."""
    return db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id,
        Flashcard.topic == topic_name
    ).all()

# --- ENDPOINTY ADMINISTRACYJNE (CRUD) ---

@router.patch("/{id}", response_model=FlashcardResponse)
def update_flashcard(
    id: int, 
    data: FlashcardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Edytuje pojedynczą fiszkę[cite: 32, 157]."""
    card = db.query(Flashcard).filter(Flashcard.id == id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Nie znaleziono fiszki")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(card, key, value)
    
    db.commit()
    db.refresh(card)
    return card

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Usuwa pojedynczą fiszkę."""
    card = db.query(Flashcard).filter(Flashcard.id == id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Nie znaleziono fiszki")
    db.delete(card)
    db.commit()
    return None

@router.delete("/topic/{topic_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic_collection(
    topic_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Usuwa całą kolekcję (temat) użytkownika."""
    db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id, 
        Flashcard.topic == topic_name
    ).delete(synchronize_session=False)
    db.commit()
    return None