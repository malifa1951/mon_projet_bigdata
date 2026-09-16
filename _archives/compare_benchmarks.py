"""
Compare les résultats avant/après index et génère un tableau + graphique.
"""
import csv
import matplotlib.pyplot as plt

# Charger les deux CSV
with open('benchmark_avant.csv') as f:
    avant = next(csv.DictReader(f))
with open('benchmark_apres.csv') as f:
    apres = next(csv.DictReader(f))

# Extraire les requêtes (hors 'n_series')
queries = [k for k in avant.keys() if k != 'n_series']

# Afficher le tableau
print(f"\n=== COMPARAISON AVANT / APRÈS INDEX ===")
print(f"Taille de la BD : {avant['n_series']} séries\n")
print(f"{'Requête':<25} {'Avant (ms)':>12} {'Après (ms)':>12} {'Gain':>10}")
print("-" * 65)

gains = []
for q in queries:
    a = float(avant[q])
    b = float(apres[q])
    gain = round((a - b) / a * 100, 1) if a > 0 else 0
    gains.append(gain)
    print(f"{q:<25} {a:>12.2f} {b:>12.2f} {gain:>9.1f}%")

# Graphique comparatif
labels = [q.replace('_', ' ').title() for q in queries]
avant_vals = [float(avant[q]) for q in queries]
apres_vals = [float(apres[q]) for q in queries]

x = range(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar([i - width/2 for i in x], avant_vals, width, label='Avant index', color='#ef4444', alpha=0.85)
bars2 = ax.bar([i + width/2 for i in x], apres_vals, width, label='Après index', color='#10b981', alpha=0.85)

ax.set_xlabel('Type de requête')
ax.set_ylabel('Temps de réponse (ms)')
ax.set_title('Impact des index sur les performances', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=15, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

for bar in bars1:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}',
            ha='center', va='bottom', fontsize=8)
for bar in bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}',
            ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('courbe_index_comparaison.png', dpi=150)
print(f"\n✅ courbe_index_comparaison.png généré")

# Graphique du gain en %
fig2, ax2 = plt.subplots(figsize=(12, 5))
colors = ['#10b981' if g > 0 else '#ef4444' for g in gains]
bars = ax2.barh(labels, gains, color=colors, alpha=0.85)
ax2.set_xlabel('Gain de performance (%)')
ax2.set_title("Gain apporté par l'ajout des index", fontsize=14, fontweight='bold')
ax2.axvline(0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='x')

for bar, g in zip(bars, gains):
    ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
             f'{g:.1f}%', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('courbe_index_gain.png', dpi=150)
print(f"✅ courbe_index_gain.png généré")