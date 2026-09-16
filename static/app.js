/* ============================================
   malifa_big_data — Interactions JS
   ============================================ */

// ---------- MENU MOBILE ----------
function toggleNav() {
    document.getElementById('navLinks').classList.toggle('open');
}

// ---------- RECHERCHE EN DIRECT ----------
function filterTable() {
    const input = document.getElementById('searchInput');
    if (!input) return;

    const filter = input.value.toLowerCase();
    const table = document.getElementById('seriesTable');
    if (!table) return;

    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    let visibleCount = 0;

    for (let row of rows) {
        const text = row.textContent.toLowerCase();
        if (text.includes(filter)) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    }

    const noResults = document.getElementById('noResults');
    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

// ---------- TRI DE TABLEAU ----------
let sortDirection = {};

function sortTable(columnIndex) {
    const table = document.getElementById('seriesTable');
    if (!table) return;

    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = Array.from(tbody.getElementsByTagName('tr'));

    sortDirection[columnIndex] = !sortDirection[columnIndex];
    const dir = sortDirection[columnIndex] ? 1 : -1;

    rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].textContent.trim();
        let bVal = b.cells[columnIndex].textContent.trim();

        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return (aNum - bNum) * dir;
        }
        return aVal.localeCompare(bVal, 'fr') * dir;
    });

    rows.forEach(row => tbody.appendChild(row));
}

// ---------- NOM DU FICHIER CSV ----------
function updateFileName(input) {
    const label = document.getElementById('fileLabel');
    if (!label) return;

    if (input.files && input.files[0]) {
        label.textContent = '📄 ' + input.files[0].name;
        label.style.borderColor = 'var(--success)';
        label.style.color = 'var(--success)';
    }
}

// ---------- ANIMATION DES CHIFFRES KPI ----------
function animateCounters() {
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(counter => {
        const target = parseFloat(counter.dataset.count);
        const isDecimal = counter.dataset.decimal === 'true';
        const duration = 1000;
        const start = performance.now();

        function update(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = target * eased;

            counter.textContent = isDecimal ? value.toFixed(2) : Math.floor(value);

            if (progress < 1) requestAnimationFrame(update);
            else counter.textContent = isDecimal ? target.toFixed(2) : target;
        }
        requestAnimationFrame(update);
    });
}

// ---------- AUTO-DISMISS DES ALERTES ----------
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

// ---------- INITIALISATION ----------
document.addEventListener('DOMContentLoaded', () => {
    animateCounters();
    autoDismissAlerts();
});