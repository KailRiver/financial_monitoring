document.addEventListener('DOMContentLoaded', function() {
    // Добавление транзакции
    document.getElementById('addTransactionForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => data[key] = value);

        fetch('/add_transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Транзакция успешно добавлена');
                window.location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при добавлении транзакции');
        });
    });

    // Редактирование транзакции
    const editButtons = document.querySelectorAll('.edit-btn');
    const editModal = document.getElementById('editModal');
    const closeModal = document.querySelector('.close');
    const editForm = document.getElementById('editTransactionForm');

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const transactionId = this.getAttribute('data-id');

            fetch(`/transaction/${transactionId}`)
                .then(response => response.json())
                .then(transaction => {
                    document.getElementById('editId').value = transaction.id;
                    document.getElementById('editEntityType').value = transaction.entity_type;
                    document.getElementById('editOperationDate').value = transaction.operation_date;
                    document.getElementById('editComment').value = transaction.comment || '';
                    document.getElementById('editAmount').value = transaction.amount;
                    document.getElementById('editStatus').value = transaction.status;
                    document.getElementById('editSenderBank').value = transaction.sender_bank || '';
                    document.getElementById('editRecipientBank').value = transaction.recipient_bank || '';
                    document.getElementById('editRecipientInn').value = transaction.recipient_inn || '';
                    document.getElementById('editCategory').value = transaction.category || '';
                    document.getElementById('editRecipientPhone').value = transaction.recipient_phone || '';

                    editModal.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при загрузке данных транзакции');
                });
        });
    });

    closeModal.addEventListener('click', function() {
        editModal.style.display = 'none';
    });

    editForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => data[key] = value);

        fetch(`/edit_transaction/${data.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Транзакция успешно обновлена');
                window.location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при обновлении транзакции');
        });
    });

    // Удаление транзакции
    const deleteButtons = document.querySelectorAll('.delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (confirm('Вы уверены, что хотите удалить эту транзакцию?')) {
                const transactionId = this.getAttribute('data-id');

                fetch(`/delete_transaction/${transactionId}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Транзакция успешно удалена');
                        window.location.reload();
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при удалении транзакции');
                });
            }
        });
    });
});