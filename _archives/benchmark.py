"""
Mesure les performances des requêtes selon la taille de la BD.
Usage : python benchmark.py
"""
import time
import csv
from app import app, db
from models import Serie, Genre, Saison, Acteur, Role
from sqlalchemy import func


def measure(query_func, label, iterations=10):
    """Exécute une requête plusieurs fois et retourne le temps moyen."""
    times = []
    with app.app_context():
        for _ in range(iterations):
            start = time.perf_counter()
            query_func()
            times.append(time.perf_counter() - start)
    avg = sum(times) / len(times) * 1000  # ms
    print(f"  {label:40s} : {avg:8.2f} ms")
    return avg


def run_benchmark():
    with app.app_context():
        n_series = Serie.query.count()
        n_genres = Genre.query.count()
        n_saisons = Saison.query.count()

    print(f"\n=== BENCHMARK ===")
    print(f"Taille de la BD : {n_series} séries, {n_genres} genres, {n_saisons} saisons\n")

    results = {}

    # Requête 1 : SELECT simple
    results['select_all'] = measure(
        lambda: Serie.query.all(),
        "SELECT * FROM serie"
    )

    # Requête 2 : ORDER BY
    results['order_by'] = measure(
        lambda: Serie.query.order_by(Serie.titre).all(),
        "SELECT ... ORDER BY titre"
    )

    # Requête 3 : WHERE note > 8
    results['filter_note'] = measure(
        lambda: Serie.query.filter(Serie.note > 8).all(),
        "SELECT ... WHERE note > 8"
    )

    # Requête 4 : COUNT
    results['count'] = measure(
        lambda: db.session.query(func.count(Serie.id)).scalar(),
        "SELECT COUNT(*) FROM serie"
    )

    # Requête 5 : GROUP BY (séries par genre)
    results['group_by'] = measure(
        lambda: db.session.query(Genre.nom, func.count(Serie.id))
            .join(Serie).group_by(Genre.nom).all(),
        "SELECT genre, COUNT(*) ... GROUP BY genre"
    )

    # Requête 6 : JOIN + GROUP BY
    results['join'] = measure(
        lambda: db.session.query(Serie.titre, func.count(Saison.id))
            .join(Saison).group_by(Serie.titre).all(),
        "SELECT serie, COUNT(saison) ... JOIN"
    )

    # Requête 7 : TOP 10
    results['top10'] = measure(
        lambda: Serie.query.order_by(Serie.note.desc()).limit(10).all(),
        "SELECT ... ORDER BY note DESC LIMIT 10"
    )

    # Sauvegarder les résultats
    with open('benchmark_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Requête', 'Temps moyen (ms)', 'Nb séries'])
        for name, t in results.items():
            writer.writerow([name, round(t, 2), n_series])

    print(f"\n✅ Résultats sauvegardés dans benchmark_results.csv")
    return results


if __name__ == '__main__':
    run_benchmark()