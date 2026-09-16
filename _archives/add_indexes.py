"""
Ajoute des index sur les colonnes les plus utilisées.
Compatible SQLite et PostgreSQL.
"""
from app import app, db
from sqlalchemy import text

# Liste des index à créer
INDEXES = [
    ("idx_serie_titre", "CREATE INDEX IF NOT EXISTS idx_serie_titre ON serie(titre)"),
    ("idx_serie_note", "CREATE INDEX IF NOT EXISTS idx_serie_note ON serie(note)"),
    ("idx_serie_annee", "CREATE INDEX IF NOT EXISTS idx_serie_annee ON serie(annee_debut)"),
    ("idx_serie_genre", "CREATE INDEX IF NOT EXISTS idx_serie_genre ON serie(genre_id)"),
    ("idx_saison_serie", "CREATE INDEX IF NOT EXISTS idx_saison_serie ON saison(serie_id)"),
    ("idx_role_serie", "CREATE INDEX IF NOT EXISTS idx_role_serie ON role(serie_id)"),
    ("idx_role_acteur", "CREATE INDEX IF NOT EXISTS idx_role_acteur ON role(acteur_id)"),
]


def main():
    with app.app_context():
        print("Création des index...\n")
        for name, sql in INDEXES:
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f"  ✅ {name}")
            except Exception as e:
                db.session.rollback()
                print(f"  ⚠️  {name} : {e}")

        # Vérifier les index existants
        print("\n=== Index existants sur la table 'serie' ===")
        try:
            result = db.session.execute(text(
                "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='serie'"
            ))
            for row in result:
                print(f"  📌 {row[0]}")
        except Exception:
            # SQLite
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='serie'"
            ))
            for row in result:
                print(f"  📌 {row[0]}")

        print("\n✅ Terminé.")


if __name__ == '__main__':
    main()