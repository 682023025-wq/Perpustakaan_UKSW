// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
});

function loadDashboardStats() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatsDisplay(data.stats);
            }
        })
        .catch(error => console.error('Error loading stats:', error));
}

function updateStatsDisplay(stats) {
    const statCards = document.querySelectorAll('.stat-card h3');
    if (statCards.length >= 4) {
        statCards[0].textContent = stats.total_users || 0;
        statCards[1].textContent = stats.total_buku || 0;
        statCards[2].textContent = stats.sedang_dipinjam || 0;
        statCards[3].textContent = stats.denda_belum_lunas || 0;
    }
}