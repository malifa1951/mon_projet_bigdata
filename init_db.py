from app import app, db
from models import Genre, Serie, Saison, Acteur, Role

with app.app_context():
    db.create_all()

    if not Genre.query.first():
        genres = [Genre(nom='Drame'), Genre(nom='Fantastique'), Genre(nom='Comedie')]
        db.session.add_all(genres)
        db.session.commit()
        print("Genres ajoutes.")

    if not Serie.query.first():
        s1 = Serie(titre='Breaking Bad', annee_debut=2008, annee_fin=2013, note=9.5, genre_id=1)
        s2 = Serie(titre='Game of Thrones', annee_debut=2011, annee_fin=2019, note=9.3, genre_id=2)
        db.session.add_all([s1, s2])
        db.session.commit()

        a1 = Acteur(nom='Cranston', prenom='Bryan')
        db.session.add(a1)
        db.session.commit()

        db.session.add(Role(nom_personnage='Walter White', serie_id=s1.id, acteur_id=a1.id))
        db.session.commit()
        print("Donnees d'exemple ajoutees.")

    print("BD initialisee OK")