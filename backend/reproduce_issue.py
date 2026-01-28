
from database.engine import SessionLocal
from database.crud import create_user, update_user_subscriptions, get_user_by_login_id
from database.models import Base
from database.engine import engine

def test_subscription_update():
    # Setup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create test user
    test_login_id = "test_user_repro"
    existing = get_user_by_login_id(db, test_login_id)
    if not existing:
        create_user(db, login_id=test_login_id, password_hash="hash", user_real_name="Test")
        existing = get_user_by_login_id(db, test_login_id)
        
    print(f"User ID: {existing.user_id}")
    
    # Initial subscriptions
    initial_keywords = ["A", "B"]
    print(f"Setting initial keywords: {initial_keywords}")
    update_user_subscriptions(db, existing, None, initial_keywords)
    db.commit()
    db.refresh(existing)
    
    current_keywords = [k.keyword for k in existing.keyword_subscriptions]
    print(f"Current keywords: {current_keywords}")
    assert set(current_keywords) == set(initial_keywords)
    
    # Update subscriptions (Remove B, Add C)
    new_keywords = ["A", "C"]
    print(f"Updating keywords to: {new_keywords}")
    update_user_subscriptions(db, existing, None, new_keywords)
    db.commit()
    db.refresh(existing)
    
    final_keywords = [k.keyword for k in existing.keyword_subscriptions]
    print(f"Final keywords: {final_keywords}")
    
    if set(final_keywords) == set(new_keywords):
        print("SUCCESS: Keywords updated correctly")
    else:
        print("FAILURE: Keywords mismatch")

    db.close()

if __name__ == "__main__":
    test_subscription_update()
