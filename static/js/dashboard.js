document.addEventListener('DOMContentLoaded', function() {
    // Цвета для статусов
    const statusColors = {
        'Новая': '#3498db',
        'Подтвержденная': '#2ecc71',
        'В обработке': '#f39c12',
        'Отменена': '#e74c3c',
        'Платеж выполнен': '#27ae60',
        'Платеж удален': '#95a5a6',
        'Возврат': '#9b59b6'
    };

    // Получаем данные для графиков из атрибутов data-*
    const dashboardData = JSON.parse(document.getElementById('dashboard-data').textContent);
    
    // График поступлений и списаний
    const incomeOutcomeCtx = document.getElementById('incomeOutcomeChart').getContext('2d');
    new Chart(incomeOutcomeCtx, {
        type: 'bar',
        data: {
            labels: ['Поступления', 'Списания'],
            datasets: [{
                label: 'Количество операций',
                data: [dashboardData.income_count, dashboardData.outcome_count],
                backgroundColor: ['rgba(46, 204, 113, 0.7)', 'rgba(231, 76, 60, 0.7)'],
                borderColor: ['rgba(46, 204, 113, 1)', 'rgba(231, 76, 60, 1)'],
                borderWidth: 1
            }, {
                label: 'Сумма',
                data: [dashboardData.income_amount, dashboardData.outcome_amount],
                backgroundColor: ['rgba(46, 204, 113, 0.3)', 'rgba(231, 76, 60, 0.3)'],
                borderColor: ['rgba(46, 204, 113, 1)', 'rgba(231, 76, 60, 1)'],
                borderWidth: 1,
                type: 'line',
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество операций'
                    }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Сумма'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });

    // График статусов операций
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    const statusLabels = Object.keys(dashboardData.status_stats).filter(k => dashboardData.status_stats[k] > 0);
    const statusData = statusLabels.map(label => dashboardData.status_stats[label]);
    const statusBackgrounds = statusLabels.map(label => statusColors[label]);

    new Chart(statusCtx, {
        type: 'doughnut',
        data: {
            labels: statusLabels,
            datasets: [{
                data: statusData,
                backgroundColor: statusBackgrounds,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // График банков отправителей
    const senderBanksCtx = document.getElementById('senderBanksChart').getContext('2d');
    const senderBanksLabels = Object.keys(dashboardData.sender_banks)
        .sort((a, b) => dashboardData.sender_banks[b] - dashboardData.sender_banks[a])
        .slice(0, 5);
    const senderBanksData = senderBanksLabels.map(label => dashboardData.sender_banks[label]);

    new Chart(senderBanksCtx, {
        type: 'bar',
        data: {
            labels: senderBanksLabels,
            datasets: [{
                label: 'Количество операций',
                data: senderBanksData,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // График категорий
    const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
    const categoriesLabels = Object.keys(dashboardData.categories)
        .sort((a, b) => dashboardData.categories[b] - dashboardData.categories[a])
        .slice(0, 5);
    const categoriesData = categoriesLabels.map(label => dashboardData.categories[label]);

    new Chart(categoriesCtx, {
        type: 'pie',
        data: {
            labels: categoriesLabels,
            datasets: [{
                data: categoriesData,
                backgroundColor: [
                    'rgba(155, 89, 182, 0.7)',
                    'rgba(52, 152, 219, 0.7)',
                    'rgba(46, 204, 113, 0.7)',
                    'rgba(241, 196, 15, 0.7)',
                    'rgba(230, 126, 34, 0.7)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
    });

    // Анимация загрузки
    document.querySelectorAll('.chart-container').forEach(container => {
        container.style.opacity = 0;
        setTimeout(() => {
            container.style.transition = 'opacity 0.5s ease';
            container.style.opacity = 1;
        }, 100);
    });
});