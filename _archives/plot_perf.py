"""
Génère les courbes de performance à partir de benchmark_paliers.csv
"""
import csv
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# Lire les données
rows = []
with open('benchmark_paliers.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append({k: float(v) for k, v in row.items()})

n = [int(r['n']) for r in rows]
select_all = [r['select_all'] for r in rows]
order_by = [r['order_by'] for r in rows]
count = [r['count'] for r in rows]
group_by = [r['group_by'] for r in rows]
top10 = [r['top10'] for r in rows]

# Graphique 1 : toutes les requêtes
plt.figure(figsize=(11, 6))
plt.plot(n, select_all, marker='o', label='SELECT *', linewidth=2)
plt.plot(n, order_by, marker='s', label='ORDER BY titre', linewidth=2)
plt.plot(n, group_by, marker='^', label='GROUP BY genre', linewidth=2)
plt.plot(n, top10, marker='d', label='TOP 10 note', linewidth=2)
plt.plot(n, count, marker='v', label='COUNT(*)', linewidth=2)

plt.xlabel("Nombre de séries en base")
plt.ylabel("Temps de réponse (ms)")
plt.title("Performance des requêtes selon la taille de la base")
plt.legend()
plt.grid(True, alpha=0.3)
plt.xscale('log')
plt.yscale('log')
plt.tight_layout()
plt.savefig('courbe_performance.png', dpi=150)
print("✅ courbe_performance.png généré")

# Graphique 2 : évolution par requête
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

axes[0].plot(n, select_all, marker='o', color='#6366f1')
axes[0].set_title('SELECT *')
axes[0].set_xlabel('N séries')
axes[0].set_ylabel('ms')
axes[0].grid(True, alpha=0.3)

axes[1].plot(n, order_by, marker='s', color='#ec4899')
axes[1].set_title('ORDER BY titre')
axes[1].set_xlabel('N séries')
axes[1].set_ylabel('ms')
axes[1].grid(True, alpha=0.3)

axes[2].plot(n, group_by, marker='^', color='#06b6d4')
axes[2].set_title('GROUP BY genre')
axes[2].set_xlabel('N séries')
axes[2].set_ylabel('ms')
axes[2].grid(True, alpha=0.3)

axes[3].plot(n, top10, marker='d', color='#10b981')
axes[3].set_title('TOP 10 note')
axes[3].set_xlabel('N séries')
axes[3].set_ylabel('ms')
axes[3].grid(True, alpha=0.3)

axes[4].plot(n, count, marker='v', color='#f59e0b')
axes[4].set_title('COUNT(*)')
axes[4].set_xlabel('N séries')
axes[4].set_ylabel('ms')
axes[4].grid(True, alpha=0.3)

axes[5].axis('off')

plt.suptitle('Détail des performances par requête', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('courbes_detail.png', dpi=150)
print("✅ courbes_detail.png généré")