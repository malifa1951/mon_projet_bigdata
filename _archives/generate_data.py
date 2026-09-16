"""
Génère un jeu de données volumineux pour tester les performances.
Usage : python generate_data.py [nombre_de_lignes]
"""
import sys
import random
import time
from app import app, db
from models import Genre, Serie, Saison, Acteur, Role

GENRES = ['Drame', 'Comédie', 'Science-Fiction', 'Fantastique', 'Thriller',
          'Horreur', 'Romance', 'Documentaire', 'Animation', 'Policier',
          'Aventure', 'Historique', 'Biographie', 'Musical', 'Western']

MOTS_TITRES = ['The', 'Dark', 'Light', 'Shadow', 'Fire', 'Ice', 'Blood',
               'Crown', 'Empire', 'Kingdom', 'City', 'Night', 'Day', 'Star',
               'Moon', 'Sun', 'Time', 'Space', 'World', 'Life', 'Death',
               'Lost', 'Found', 'Rise', 'Fall', 'Secret', 'Hidden', 'Broken',
               'Silent', 'Eternal', 'Last', 'First', 'Young', 'Old', 'Great']

NOMS_ACTEURS = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez',
                'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor',
                'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis',
                'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright']

PRENOMS_ACTEURS = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer',
                   'Michael', 'Linda', 'David', 'Elizabeth', 'William',
                   'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                   'Thomas', 'Sarah', 'Charles', 'Karen', 'Chris', 'Nancy',
                   'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Margaret',
                   'Mark', 'Sandra', 'Donald', 'Ashley', 'Steven', 'Kimberly']


def random_title():
    """Génère un titre de série aléatoire."""
    n = random.randint(1, 4)
    return ' '.join(random.choices(MOTS_TITRES, k=n))


def main():
    n_series = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    print(f"Génération de {n_series} séries...")

    with app.app_context():
        # Créer les genres s'ils n'existent pas
        if not Genre.query.first():
            for g in GENRES:
                db.session.add(Genre(nom=g))
            db.session.commit()
            print(f"✅ {len(GENRES)} genres créés.")
        genres = Genre.query.all()
        genre_ids = [g.id for g in genres]

        # Créer les acteurs
        if not Acteur.query.first():
            print("Création de 1000 acteurs...")
            for _ in range(1000):
                db.session.add(Acteur(
                    nom=random.choice(NOMS_ACTEURS),
                    prenom=random.choice(PRENOMS_ACTEURS)
                ))
            db.session.commit()
        acteur_ids = [a.id for a in Acteur.query.all()]

        # Créer les séries
        start = time.time()
        batch = []
        BATCH_SIZE = 1000

        for i in range(n_series):
            s = Serie(
                titre=f"{random_title()} {i}",
                annee_debut=random.randint(1950, 2025),
                annee_fin=random.choice([None] + list(range(1960, 2026))),
                note=round(random.uniform(1, 10), 1),
                genre_id=random.choice(genre_ids)
            )
            batch.append(s)

            if len(batch) >= BATCH_SIZE:
                db.session.add_all(batch)
                db.session.commit()
                batch = []
                print(f"  ... {i+1}/{n_series} séries insérées", end='\r')

        if batch:
            db.session.add_all(batch)
            db.session.commit()

        duree = round(time.time() - start, 2)
        print(f"\n✅ {n_series} séries créées en {duree} secondes.")
        print(f"   Vitesse : {round(n_series/duree, 0)} séries/seconde")

        # Ajouter quelques saisons à certaines séries
        print("\nAjout de saisons aléatoires...")
        series_sample = Serie.query.limit(min(2000, n_series)).all()
        for s in series_sample:
            nb_saisons = random.randint(1, 8)
            for num in range(1, nb_saisons + 1):
                db.session.add(Saison(
                    numero=num,
                    nb_episodes=random.randint(6, 24),
                    serie_id=s.id
                ))
        db.session.commit()
        print(f"✅ Saisons ajoutées à {len(series_sample)} séries.")

        # Ajouter des rôles
        print("\nAjout de rôles...")
        for s in series_sample[:500]:
            nb_roles = random.randint(1, 5)
            for _ in range(nb_roles):
                db.session.add(Role(
                    nom_personnage=f"Personnage_{random.randint(1, 999)}",
                    serie_id=s.id,
                    acteur_id=random.choice(acteur_ids)
                ))
        db.session.commit()
        print("✅ Rôles ajoutés.")

        # Statistiques finales
        print("\n=== BASE FINALE ===")
        print(f"Séries   : {Serie.query.count()}")
        print(f"Genres   : {Genre.query.count()}")
        print(f"Saisons  : {Saison.query.count()}")
        print(f"Acteurs  : {Acteur.query.count()}")
        print(f"Rôles    : {Role.query.count()}")


if __name__ == '__main__':
    main()