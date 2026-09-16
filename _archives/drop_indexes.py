"""Supprime tous les index pour repartir de zéro."""
from app import app, db
from sqlalchemy import text

INDEXES = [
    "DROP INDEX IF EXISTS idx_serie_titre",
    "DROP INDEX IF EXISTS idx_serie_note",
    "DROP INDEX IF EXISTS idx_serie_annee",
    "DROP INDEX IF EXISTS idx_serie_genre",
    "DROP INDEX IF EXISTS idx_saison_serie",
    "DROP INDEX IF EXISTS idx_role_serie",
    "DROP INDEX IF EXISTS idx_role_acteur",
]

with app.app_context():
    print("Suppression des index...\n")
    for sql in INDEXES:
        try:
            db.session.execute(text(sql))
            db.session.commit()
            print(f"  ✅ {sql.split()[-1]}")
        except Exception as e:
            db.session.rollback()
            print(f"  ⚠️  {sql.split()[-1]} : {e}")
    print("\n✅ Terminé.")