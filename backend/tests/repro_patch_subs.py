import sys
import os
import secrets
from sqlalchemy.orm import Session
from sqlalchemy import select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.engine import SessionLocal
from database.crud import create_user, update_user_subscriptions, get_user_by_login_id
from database.models import Category, User
from main import app  # Not used directly but ensures imports work


def test_user_update_subscriptions():
    db: Session = SessionLocal()
    try:
        # 1. Setup User with Initial Subs
        cat_name_1 = "InitialCat_" + secrets.token_hex(4)
        cat_name_2 = "UpdateCat_" + secrets.token_hex(4)

        login_id = "testpatch_" + secrets.token_hex(4)

        print(f"[Setup] Creating user {login_id} with initial subs (Cat={cat_name_1})...")
        user = create_user(
            db,
            login_id=login_id,
            password_hash="pw",
            subscribed_categories=[cat_name_1],
            subscribed_keywords=["initKey"],
        )

        # Verify initial
        print(f"[Verify] Initial Cats: {[c.name for c in user.subscribed_categories]}")

        # 2. Simulate PATCH logic (Calling update_user_subscriptions directly to test logic)
        # Note: We are testing the CRUD logic here. Integration test would require requests.
        # But if logic works, main.py connection is simple.
        print("[Action] Updating subscriptions to new set...")
        update_user_subscriptions(
            db, user, new_categories=[cat_name_2, "NewAutoCatIsHere"], new_keywords=["NewKey1", "NewKey2"]
        )
        db.commit()
        db.refresh(user)

        # 3. Verify
        cats = [c.name for c in user.subscribed_categories]
        kws = [k.keyword for k in user.keyword_subscriptions]

        print(f"[Verify] Updated Cats: {cats}")
        print(f"[Verify] Updated Keywords: {kws}")

        if cat_name_2 in cats and "NewAutoCatIsHere" in cats and cat_name_1 not in cats:
            if "NewKey1" in kws and "initKey" not in kws:
                print("SUCCESS: Subscriptions replaced correctly.")
            else:
                print("FAILURE: Keywords not updated correctly.")
        else:
            print("FAILURE: Categories not updated correctly.")

        # Cleanup
        db.delete(user)
        db.commit()

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_user_update_subscriptions()
