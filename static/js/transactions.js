document.addEventListener('DOMContentLoaded', function() {
    // Обработка кнопок редактирования
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const transactionId = this.dataset.id;
            const transactionStatus = this.dataset.status;
            const nonEditableStatuses = JSON.parse(this.dataset.nonEditableStatuses);

            if (nonEditableStatuses.includes(transactionStatus)) {
                e.preventDefault();
                alert(`Редактирование запрещено для статуса "${transactionStatus}"`);
                return false;
            }
        });
    });

    // Обработка кнопок удаления
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const transactionId = this.dataset.id;
            const transactionStatus = this.dataset.status;
            const nonDeletableStatuses = JSON.parse(this.dataset.nonDeletableStatuses);

            if (nonDeletableStatuses.includes(transactionStatus)) {
                e.preventDefault();
                alert(`Удаление запрещено для статуса "${transactionStatus}"`);
                return false;
            }

            if (!confirm('Вы уверены, что хотите пометить транзакцию как "Платеж удален"?')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Валидация форм
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const amountInput = form.querySelector('input[name="amount"]');
            if (amountInput && parseFloat(amountInput.value) <= 0) {
                e.preventDefault();
                alert('Сумма должна быть положительным числом');
                amountInput.focus();
                return false;
            }

            const statusSelect = form.querySelector('select[name="status"]');
            if (statusSelect) {
                const nonEditableStatuses = JSON.parse(form.dataset.nonEditableStatuses || '[]');
                const originalStatus = form.dataset.originalStatus;

                if (originalStatus && nonEditableStatuses.includes(originalStatus)) {
                    e.preventDefault();
                    alert('Нельзя изменять транзакции с данным статусом');
                    return false;
                }
            }

            return true;
        });
    });
});