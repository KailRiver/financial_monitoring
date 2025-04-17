function initDashboardCharts(data) {
    // График поступлений vs списаний
    const incomeOutcomeCtx = document.getElementById('incomeOutcomeChart').getContext('2d');
    new Chart(incomeOutcomeCtx, {
        type: 'bar',
        data: {
            labels: ['Поступления', 'Списания'],
            datasets: [{
                label: 'Количество',
                data: [data.income_count, data.outcome_count],
                backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 99, 132, 0.6)']
            }, {
                label: 'Сумма',
                data: [data.income_amount, data.outcome_amount],
                backgroundColor: ['rgba(75, 192, 192, 0.8)', 'rgba(255, 99, 132, 0.8)'],
                type: 'line',
                yAxisID: 'y1'
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Количество'
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

    // График статусов транзакций
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    new Chart(statusCtx, {
        type: 'pie',
        data: {
            labels: Object.keys(data.status_stats),
            datasets: [{
                data: Object.values(data.status_stats),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)'
                ]
            }]
        }
    });

    // График топ банков отправителей
    const senderBanksCtx = document.getElementById('senderBanksChart').getContext('2d');
    const senderBanksLabels = Object.keys(data.sender_banks).slice(0, 5);
    const senderBanksData = senderBanksLabels.map(label => data.sender_banks[label]);

    new Chart(senderBanksCtx, {
        type: 'bar',
        data: {
            labels: senderBanksLabels,
            datasets: [{
                label: 'Количество транзакций',
                data: senderBanksData,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // График топ банков получателей
    const recipientBanksCtx = document.getElementById('recipientBanksChart').getContext('2d');
    const recipientBanksLabels = Object.keys(data.recipient_banks).slice(0, 5);
    const recipientBanksData = recipientBanksLabels.map(label => data.recipient_banks[label]);

    new Chart(recipientBanksCtx, {
        type: 'bar',
        data: {
            labels: recipientBanksLabels,
            datasets: [{
                label: 'Количество транзакций',
                data: recipientBanksData,
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // График категорий
    const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
    const categoriesLabels = Object.keys(data.categories).slice(0, 5);
    const categoriesData = categoriesLabels.map(label => data.categories[label]);

    new Chart(categoriesCtx, {
        type: 'doughnut',
        data: {
            labels: categoriesLabels,
            datasets: [{
                data: categoriesData,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)'
                ]
            }]
        }
    });
}