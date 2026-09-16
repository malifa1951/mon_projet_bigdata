import csv
import io
import time
from flask import Flask, render_template, request, redirect, url_for, Response, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import Config
from models import db, Genre, Serie, Saison, Acteur, Role

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ---------- AUTHENTIFICATION ----------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "warning"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# ---------- CONTEXTE GLOBAL (pour les templates) ----------
@app.context_processor
def inject_globals():
    return {
        'app_name': 'malifa_big_data',
        'app_version': '1.0',
        'current_year': time.strftime('%Y')
    }


# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            login_user(User(username))
            flash(f'Bienvenue {username} 👋', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Identifiants incorrects. Essayez à nouveau.', 'danger')

    return render_template('login.html')


# ---------- LOGOUT ----------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('login'))


# ---------- PAGE D'ACCUEIL ----------
@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 25  # 25 séries par page

    pagination = Serie.query.order_by(Serie.titre).paginate(
        page=page, per_page=per_page, error_out=False
    )
    series = pagination.items
    genres = Genre.query.all()
    stats = {
        'total_series': Serie.query.count(),
        'total_genres': Genre.query.count(),
        'avg_note': round(db.session.query(db.func.avg(Serie.note)).scalar() or 0, 2)
    }
    return render_template(
        'index.html',
        series=series,
        genres=genres,
        stats=stats,
        pagination=pagination
    )


# ---------- AJOUT ----------
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            serie = Serie(
                titre=request.form['titre'],
                annee_debut=request.form.get('annee_debut') or None,
                annee_fin=request.form.get('annee_fin') or None,
                note=request.form.get('note') or None,
                genre_id=request.form.get('genre_id') or None
            )
            db.session.add(serie)
            db.session.commit()
            flash(f'Série « {serie.titre} » ajoutée avec succès !', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')

    genres = Genre.query.all()
    return render_template('form.html', serie=None, genres=genres)


# ---------- MODIFICATION ----------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    serie = Serie.query.get_or_404(id)
    if request.method == 'POST':
        try:
            serie.titre = request.form['titre']
            serie.annee_debut = request.form.get('annee_debut') or None
            serie.annee_fin = request.form.get('annee_fin') or None
            serie.note = request.form.get('note') or None
            serie.genre_id = request.form.get('genre_id') or None
            db.session.commit()
            flash(f'Série « {serie.titre} » modifiée !', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur : {str(e)}', 'danger')

    genres = Genre.query.all()
    return render_template('form.html', serie=serie, genres=genres)


# ---------- SUPPRESSION ----------
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    serie = Serie.query.get_or_404(id)
    titre = serie.titre
    db.session.delete(serie)
    db.session.commit()
    flash(f'Série « {titre} » supprimée.', 'success')
    return redirect(url_for('index'))


# ---------- EXPORT CSV ----------
@app.route('/export')
@login_required
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
        headers={'Content-Disposition': 'attachment; filename=malifa_big_data_series.csv'}
    )


# ---------- IMPORT CSV ----------
@app.route('/import', methods=['POST'])
@login_required
def import_csv():
    file = request.files.get('file')
    if not file:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('index'))
    try:
        stream = io.StringIO(file.stream.read().decode('UTF-8'))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            db.session.add(Serie(
                titre=row['titre'],
                annee_debut=row.get('annee_debut') or None,
                annee_fin=row.get('annee_fin') or None,
                note=row.get('note') or None,
                genre_id=row.get('genre_id') or None
            ))
            count += 1
        db.session.commit()
        flash(f'{count} série(s) importée(s) avec succès !', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur d\'import : {str(e)}', 'danger')
    return redirect(url_for('index'))


# ---------- STATISTIQUES ----------
@app.route('/stats')
@login_required
def stats():
    start = time.time()

    top_series = db.session.query(Serie.titre, Serie.note) \
        .filter(Serie.note.isnot(None)) \
        .order_by(Serie.note.desc()).limit(5).all()

    par_genre = db.session.query(Genre.nom, db.func.count(Serie.id)) \
        .join(Serie, Serie.genre_id == Genre.id) \
        .group_by(Genre.nom).all()

    longues = db.session.query(Serie.titre, db.func.count(Saison.id)) \
        .join(Saison).group_by(Serie.titre) \
        .having(db.func.count(Saison.id) > 3).all()

    roles = db.session.query(Acteur.nom, Acteur.prenom, Role.nom_personnage, Serie.titre) \
        .join(Role, Role.acteur_id == Acteur.id) \
        .join(Serie, Role.serie_id == Serie.id).limit(10).all()

    duree = round((time.time() - start) * 1000, 2)

    return render_template(
        'stats.html',
        top_series=top_series,
        par_genre=par_genre,
        longues=longues,
        roles=roles,
        duree=duree
    )


# ---------- COMMANDE CLI ----------
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print("Base initialisée.")


# ---------- LANCEMENT ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)