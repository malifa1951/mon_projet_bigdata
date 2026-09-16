"""
Test de performance par paliers : 1k, 5k, 10k, 50k, 100k
Génère les données progressivement et mesure à chaque palier.
"""
import time
import csv
import random
from app import app, db
from models import Genre, Serie, Saison
from sqlalchemy import func

PALIERS = [1000, 5000, 10000, 25000, 50000, 100000]


def clear_series():
    with app.app_context():
        Saison.query.delete()
        Serie.query.delete()
        db.session.commit()


def generate(n):
    """Génère n séries en batch."""
    from generate_data import random_title, GENRES
    with app.app_context():
        if not Genre.query.first():
            for g in GENRES:
                db.session.add(Genre(nom=g))
            db.session.commit()

        genre_ids = [g.id for g in Genre.query.all()]
        batch = []

        for i in range(n):
            batch.append(Serie(
                titre=f"{random_title()} {i}",
                annee_debut=random.randint(1950, 2025),
                annee_fin=random.choice([None] + list(range(1960, 2026))),
                note=round(random.uniform(1, 10), 1),
                genre_id=random.choice(genre_ids)
            ))
            if len(batch) >= 1000:
                db.session.add_all(batch)
                db.session.commit()
                batch = []
        if batch:
            db.session.add_all(batch)
            db.session.commit()


def time_query(func, iterations=5):
    times = []
    with app.app_context():
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            times.append(time.perf_counter() - start)
    return sum(times) / len(times) * 1000


def run():
    print("=== BENCHMARK PAR PALIERS ===\n")
    results = []

    for palier in PALIERS:
        print(f"\n--- Palier : {palier} séries ---")
        clear_series()

        # Génération
        start = time.time()
        generate(palier)
        gen_time = round(time.time() - start, 2)
        print(f"  Génération : {gen_time} s")

        # Mesures
        t_select = time_query(lambda: Serie.query.all())
        t_order = time_query(lambda: Serie.query.order_by(Serie.titre).all())
        t_count = time_query(lambda: db.session.query(func.count(Serie.id)).scalar())
        t_group = time_query(lambda: db.session.query(Genre.nom, func.count(Serie.id))
                             .join(Serie).group_by(Genre.nom).all())
        t_top = time_query(lambda: Serie.query.order_by(Serie.note.desc()).limit(10).all())

        print(f"  SELECT *         : {t_select:.2f} ms")
        print(f"  ORDER BY titre   : {t_order:.2f} ms")
        print(f"  COUNT(*)         : {t_count:.2f} ms")
        print(f"  GROUP BY genre   : {t_group:.2f} ms")
        print(f"  TOP 10 note      : {t_top:.2f} ms")

        results.append({
            'n': palier,
            'select_all': round(t_select, 2),
            'order_by': round(t_order, 2),
            'count': round(t_count, 2),
            'group_by': round(t_group, 2),
            'top10': round(t_top, 2),
        })

    # Export CSV
    with open('benchmark_paliers.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Résultats dans benchmark_paliers.csv")


if __name__ == '__main__':
    run()