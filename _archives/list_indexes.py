"""Liste les index existants sur les tables principales."""
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("\n=== Index sur la table 'serie' ===")
    result = db.session.execute(text(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='serie'"
    ))
    indexes = [row[0] for row in result]
    if indexes:
        for name in indexes:
            print(f"  📌 {name}")
    else:
        print("  (aucun index)")
    print(f"\nTotal : {len(indexes)} index")