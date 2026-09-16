"""
Benchmark AVANT index — mesure le temps SQL réel (pas le transfert Python).
Sauvegarde dans benchmark_avant.csv
"""
import time
import csv
from app import app, db
from models import Serie, Genre
from sqlalchemy import func, text


def measure_sql(sql, label, iterations=10):
    """Exécute un SQL brut et mesure uniquement le temps SQL."""
    times = []
    with app.app_context():
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        try:
            for _ in range(iterations):
                start = time.perf_counter()
                cursor.execute(sql)
                cursor.fetchall()
                times.append(time.perf_counter() - start)
        finally:
            cursor.close()
            conn.close()
    avg = sum(times) / len(times) * 1000
    print(f"  {label:45s} : {avg:8.2f} ms")
    return round(avg, 2)


def run():
    with app.app_context():
        n = Serie.query.count()

    print(f"\n=== BENCHMARK APRÈS INDEX ===")
    print(f"Taille de la BD : {n} séries\n")

    results = {
        'n_series': n,
        'order_by_titre': measure_sql(
            "SELECT titre FROM serie ORDER BY titre LIMIT 50",
            "SELECT titre ORDER BY titre LIMIT 50"
        ),
        'where_note': measure_sql(
            "SELECT id, titre FROM serie WHERE note > 9.9 LIMIT 100",
            "WHERE note > 9.9 LIMIT 100"
        ),
        'where_annee': measure_sql(
            "SELECT id FROM serie WHERE annee_debut = 2005",
            "WHERE annee_debut = 2005"
        ),
        'where_genre': measure_sql(
            "SELECT id FROM serie WHERE genre_id = 1 LIMIT 100",
            "WHERE genre_id = 1 LIMIT 100"
        ),
        'count_note': measure_sql(
            "SELECT COUNT(*) FROM serie WHERE note > 9",
            "COUNT(*) WHERE note > 9"
        ),
    }

    with open('benchmark_apres.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results.keys())
        writer.writeheader()
        writer.writerow(results)

    print(f"\n✅ Résultats dans benchmark_apres.csv")
    return results


if __name__ == '__main__':
    run()