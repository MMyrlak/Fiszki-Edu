from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Flashcard
from app.auth.security import hash_password
from datetime import datetime

def init_db():
    print("Tworzenie tabel w bazie danych...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        test_user = db.query(User).filter(User.email == "test@test.com").first()
        
        if not test_user:
            print("Tworzenie użytkownika testowego...")
            test_user = User(
                username="tester",
                email="test@test.com",
                hashed_password=hash_password("123") # Hasło: 123
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        else:
            print("Użytkownik testowy już istnieje.")

        if db.query(Flashcard).count() == 0:
            print("Dodawanie przykładowych fiszek...")
            seed_data = [

                {"q": "Co to jest ATP?", "a": "Adenozynotrifosforan - główny nośnik energii w komórkach.", "t": "Biologia"},
                {"q": "Gdzie zachodzi fotosynteza?", "a": "W chloroplastach.", "t": "Biologia"},

                {"q": "Co to jest FastAPI?", "a": "Nowoczesny, szybki framework webowy dla Pythona.", "t": "Informatyka"},
                {"q": "Czym jest klucz główny (PK)?", "a": "Unikalny identyfikator rekordu w tabeli bazy danych.", "t": "Informatyka"},

                {"q": "W którym roku był chrzest Polski?", "a": "966 rok.", "t": "Historia"}
            ]

            for item in seed_data:
                flashcard = Flashcard(
                    question=item["q"],
                    answer=item["a"],
                    topic=item["t"],
                    user_id=test_user.id
                )
                db.add(flashcard)
            
            db.commit()
            print(f"Dodano {len(seed_data)} fiszek do 3 różnych tematów.")
        else:
            print("Fiszki już istnieją w bazie.")

        print("\nInicjalizacja zakończona sukcesem!")
        print(f"Możesz się zalogować: test@test.com / 123")

    except Exception as e:
        print(f"Wystąpił błąd podczas inicjalizacji: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()