import sys
import os
import secrets
from sqlalchemy.orm import Session
from sqlalchemy import select

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.engine import SessionLocal
from database.crud import create_user, get_user_by_login_id
from database.models import Category, User


def test_user_creation_with_subscriptions():
    db: Session = SessionLocal()
    try:
        # 1. Setup Data
        # We purposely DO NOT create the category to test if create_user does it.
        cat_name = "NewAutoCat_" + secrets.token_hex(4)

        # Unique user info
        login_id = "testuser_" + secrets.token_hex(4)

        # 2. Call create_user with subscriptions
        print(f"[Action] Creating user {login_id} with subs...")
        user = create_user(
            db,
            login_id=login_id,
            password_hash="dummyhash",
            user_real_name="Test User",
            subscribed_categories=[cat_name],
            subscribed_keywords=["testkey1", "testkey2"],
        )

        # 3. Verify
        # Reload user to be sure
        db.refresh(user)

        print(f"[Verify] User subs entries: {len(user.subscribed_categories)}")
        print(f"[Verify] User kw entries: {len(user.keyword_subscriptions)}")

        created_cats = [c.name for c in user.subscribed_categories]
        created_kws = [k.keyword for k in user.keyword_subscriptions]

        print(f"Categories found: {created_cats}")
        print(f"Keywords found: {created_kws}")

        if cat_name in created_cats and "testkey1" in created_kws:
            print("SUCCESS: Subscriptions saved correctly.")
        else:
            print("FAILURE: Subscriptions NOT saved.")

        # Cleanup
        db.delete(user)
        # Note: we don't delete the category as it might be used, but here it's unique so we could.
        db.execute(select(Category).where(Category.name == cat_name)).scalar_one().delete()
        db.commit()

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_user_creation_with_subscriptions()
