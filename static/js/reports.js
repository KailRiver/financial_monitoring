document.addEventListener('DOMContentLoaded', function() {
    // Экспорт в CSV
    document.getElementById('exportCsv').addEventListener('click', function() {
        const filters = {
            sender_bank: document.querySelector('input[name="sender_bank"]').value,
            recipient_bank: document.querySelector('input[name="recipient_bank"]').value,
            start_date: document.querySelector('input[name="start_date"]').value,
            end_date: document.querySelector('input[name="end_date"]').value,
            status: document.querySelector('select[name="status"]').value,
            inn: document.querySelector('input[name="inn"]').value,
            min_amount: document.querySelector('input[name="min_amount"]').value,
            max_amount: document.querySelector('input[name="max_amount"]').value,
            transaction_type: document.querySelector('select[name="transaction_type"]').value,
            category: document.querySelector('input[name="category"]').value
        };

        let url = '/reports/export/csv?';
        for (const key in filters) {
            if (filters[key]) {
                url += `${key}=${encodeURIComponent(filters[key])}&`;
            }
        }

        window.location.href = url;
    });

    // Экспорт в Excel
    document.getElementById('exportExcel').addEventListener('click', function() {
        const filters = {
            sender_bank: document.querySelector('input[name="sender_bank"]').value,
            recipient_bank: document.querySelector('input[name="recipient_bank"]').value,
            start_date: document.querySelector('input[name="start_date"]').value,
            end_date: document.querySelector('input[name="end_date"]').value,
            status: document.querySelector('select[name="status"]').value,
            inn: document.querySelector('input[name="inn"]').value,
            min_amount: document.querySelector('input[name="min_amount"]').value,
            max_amount: document.querySelector('input[name="max_amount"]').value,
            transaction_type: document.querySelector('select[name="transaction_type"]').value,
            category: document.querySelector('input[name="category"]').value
        };

        let url = '/reports/export/excel?';
        for (const key in filters) {
            if (filters[key]) {
                url += `${key}=${encodeURIComponent(filters[key])}&`;
            }
        }

        window.location.href = url;
    });
});