import csv
import io
import time
from flask import Flask, render_template, request, redirect, url_for, Response, flash
from config import Config
from models import db, Genre, Serie, Saison, Acteur, Role

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


# ---------- PAGE D'ACCUEIL ----------
@app.route('/')
def index():
    series = Serie.query.order_by(Serie.titre).all()
    return render_template('index.html', series=series)


# ---------- AJOUT ----------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        titre = request.form['titre']
        annee_debut = request.form.get('annee_debut') or None
        annee_fin = request.form.get('annee_fin') or None
        note = request.form.get('note') or None
        genre_id = request.form.get('genre_id') or None
        serie = Serie(
            titre=titre,
            annee_debut=annee_debut,
            annee_fin=annee_fin,
            note=note,
            genre_id=genre_id
        )
        db.session.add(serie)
        db.session.commit()
        flash('Série ajoutée avec succès !', 'success')
        return redirect(url_for('index'))
    genres = Genre.query.all()
    return render_template('form.html', serie=None, genres=genres)


# ---------- MODIFICATION ----------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    serie = Serie.query.get_or_404(id)
    if request.method == 'POST':
        serie.titre = request.form['titre']
        serie.annee_debut = request.form.get('annee_debut') or None
        serie.annee_fin = request.form.get('annee_fin') or None
        serie.note = request.form.get('note') or None
        serie.genre_id = request.form.get('genre_id') or None
        db.session.commit()
        flash('Série modifiée !', 'success')
        return redirect(url_for('index'))
    genres = Genre.query.all()
    return render_template('form.html', serie=serie, genres=genres)


# ---------- SUPPRESSION ----------
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    serie = Serie.query.get_or_404(id)
    db.session.delete(serie)
    db.session.commit()
    flash('Série supprimée !', 'success')
    return redirect(url_for('index'))


# ---------- EXPORT CSV ----------
@app.route('/export')
def export_csv():
    series = Serie.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'titre', 'annee_debut', 'annee_fin', 'note', 'genre_id'])
    for s in series:
        writer.writerow([s.id, s.titre, s.annee_debut, s.annee_fin, s.note, s.genre_id])
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=series.csv'}
    )


# ---------- IMPORT CSV ----------
@app.route('/import', methods=['POST'])
def import_csv():
    file = request.files.get('file')
    if not file:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('index'))
    stream = io.StringIO(file.stream.read().decode('UTF-8'))
    reader = csv.DictReader(stream)
    for row in reader:
        serie = Serie(
            titre=row['titre'],
            annee_debut=row.get('annee_debut') or None,
            annee_fin=row.get('annee_fin') or None,
            note=row.get('note') or None,
            genre_id=row.get('genre_id') or None
        )
        db.session.add(serie)
    db.session.commit()
    flash('Import CSV réussi !', 'success')
    return redirect(url_for('index'))


# ---------- REQUÊTES PRÉ-CODÉES ----------
@app.route('/stats')
def stats():
    start = time.time()

    # Requête 1 : Top 5 séries les mieux notées
    top_series = db.session.query(Serie.titre, Serie.note) \
        .order_by(Serie.note.desc()).limit(5).all()

    # Requête 2 : Nombre de séries par genre
    par_genre = db.session.query(Genre.nom, db.func.count(Serie.id)) \
        .join(Serie, Serie.genre_id == Genre.id) \
        .group_by(Genre.nom).all()

    # Requête 3 : Séries avec plus de 3 saisons
    longues = db.session.query(Serie.titre, db.func.count(Saison.id)) \
        .join(Saison).group_by(Serie.titre) \
        .having(db.func.count(Saison.id) > 3).all()

    # Requête 4 : Acteurs et leurs personnages
    roles = db.session.query(Acteur.nom, Acteur.prenom, Role.nom_personnage, Serie.titre) \
        .join(Role, Role.acteur_id == Acteur.id) \
        .join(Serie, Role.serie_id == Serie.id).limit(10).all()

    duree = round((time.time() - start) * 1000, 2)  # en ms

    return render_template(
        'stats.html',
        top_series=top_series,
        par_genre=par_genre,
        longues=longues,
        roles=roles,
        duree=duree
    )


# ---------- COMMANDE CLI : INITIALISATION ----------
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Base initialisée.")

# ---------- ROUTE TEMPORAIRE D'INITIALISATION ----------
@app.route('/init')
def init_route():
    try:
        db.create_all()

        if not Genre.query.first():
            db.session.add_all([
                Genre(nom='Drame'),
                Genre(nom='Fantastique'),
                Genre(nom='Comedie')
            ])
            db.session.commit()

        if not Serie.query.first():
            db.session.add_all([
                Serie(titre='Breaking Bad', annee_debut=2008, annee_fin=2013, note=9.5, genre_id=1),
                Serie(titre='Game of Thrones', annee_debut=2011, annee_fin=2019, note=9.3, genre_id=2)
            ])
            db.session.commit()

        return "Base initialisee OK"
    except Exception as e:
        return f"Erreur : {str(e)}"
# ---------- LANCEMENT ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)