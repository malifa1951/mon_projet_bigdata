from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    series = db.relationship('Serie', backref='genre', lazy=True)

class Serie(db.Model):
    __tablename__ = 'serie'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False, index=True)
    annee_debut = db.Column(db.Integer, index=True)
    annee_fin = db.Column(db.Integer)
    note = db.Column(db.Float, index=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), index=True)
    saisons = db.relationship('Saison', backref='serie', lazy=True, cascade="all, delete-orphan")
    roles = db.relationship('Role', backref='serie', lazy=True, cascade="all, delete-orphan")

class Saison(db.Model):
    __tablename__ = 'saison'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    nb_episodes = db.Column(db.Integer)
    serie_id = db.Column(db.Integer, db.ForeignKey('serie.id'))

class Acteur(db.Model):
    __tablename__ = 'acteur'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80))
    roles = db.relationship('Role', backref='acteur', lazy=True, cascade="all, delete-orphan")

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    nom_personnage = db.Column(db.String(100))
    serie_id = db.Column(db.Integer, db.ForeignKey('serie.id'))
    acteur_id = db.Column(db.Integer, db.ForeignKey('acteur.id'))