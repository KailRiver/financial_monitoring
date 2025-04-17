document.addEventListener('DOMContentLoaded', function() {
    // Функция для получения текущих фильтров
    function getCurrentFilters() {
        const form = document.getElementById('reportForm');
        const formData = new FormData(form);
        const filters = {};

        for (const [key, value] of formData.entries()) {
            if (value) filters[key] = value;
        }

        return filters;
    }

    // Функция для создания URL экспорта
    function buildExportUrl(baseUrl, filters) {
        const params = new URLSearchParams();

        for (const key in filters) {
            if (filters[key]) {
                params.append(key, filters[key]);
            }
        }

        return `${baseUrl}?${params.toString()}`;
    }

    // Обработка экспорта в CSV
    document.getElementById('exportCsv').addEventListener('click', function() {
        const filters = getCurrentFilters();
        const exportUrl = buildExportUrl('/reports/export/csv', filters);
        window.location.href = exportUrl;
    });

    // Обработка экспорта в Excel
    document.getElementById('exportExcel').addEventListener('click', function() {
        const filters = getCurrentFilters();
        const exportUrl = buildExportUrl('/reports/export/excel', filters);
        window.location.href = exportUrl;
    });

    // Валидация дат
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');

    if (startDate && endDate) {
        startDate.addEventListener('change', function() {
            if (endDate.value && startDate.value > endDate.value) {
                alert('Дата "от" не может быть больше даты "до"');
                startDate.value = '';
            }
        });

        endDate.addEventListener('change', function() {
            if (startDate.value && startDate.value > endDate.value) {
                alert('Дата "до" не может быть меньше даты "от"');
                endDate.value = '';
            }
        });
    }

    // Валидация сумм
    const minAmount = document.getElementById('min_amount');
    const maxAmount = document.getElementById('max_amount');

    if (minAmount && maxAmount) {
        minAmount.addEventListener('change', function() {
            if (maxAmount.value && parseFloat(minAmount.value) > parseFloat(maxAmount.value)) {
                alert('Минимальная сумма не может быть больше максимальной');
                minAmount.value = '';
            }
        });

        maxAmount.addEventListener('change', function() {
            if (minAmount.value && parseFloat(minAmount.value) > parseFloat(maxAmount.value)) {
                alert('Максимальная сумма не может быть меньше минимальной');
                maxAmount.value = '';
            }
        });
    }
});