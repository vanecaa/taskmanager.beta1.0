document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed");
    
    // ==================== ОБРАБОТЧИКИ МОДАЛЬНЫХ ОКОН ====================
    // Открытие модальных окон
    document.querySelectorAll('.open-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            document.getElementById(target).style.display = 'block';
        });
    });

    // Закрытие модальных окон
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            document.getElementById(target).style.display = 'none';
        });
    });

    // Закрытие при клике вне модального окна
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });

    // ==================== ОКНО ПРОСМОТРА ЗАДАЧИ ====================
    const taskItems = document.querySelectorAll(".task-item");
    const taskModal = document.getElementById("task-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const modalResponsible = document.getElementById("modal-responsible");
    const modalRegion = document.getElementById("modal-region");
    const modalPriority = document.getElementById("modal-priority");
    const modalDate = document.getElementById("modal-date");
    const modalClose = taskModal.querySelector(".close");

    let currentTaskId = null;

    // Открытие окна задачи
    taskItems.forEach(item => {
        item.addEventListener("click", function () {
            currentTaskId = item.getAttribute("data-id");
            modalTitle.textContent = item.getAttribute("data-title") || "";
            modalDescription.textContent = item.getAttribute("data-description") || "";
            modalResponsible.textContent = item.getAttribute("data-responsible") || "";
            modalRegion.textContent = item.getAttribute("data-region") || "";
            modalPriority.textContent = item.getAttribute("data-priority") || "";
            modalDate.textContent = item.getAttribute("data-date") || "Без даты";
            taskModal.style.display = "block";
        });
    });

    // Закрытие окна задачи
    modalClose.addEventListener("click", () => {
        taskModal.style.display = "none";
    });

    // ==================== ОБРАБОТЧИКИ ДЕЙСТВИЙ С ЗАДАЧАМИ ====================
    // Завершение задачи
    document.getElementById("complete-task")?.addEventListener("click", () => {
        if (!currentTaskId) return;
        fetch(`/complete_task/${currentTaskId}`, {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert("Ошибка при завершении задачи: " + (data.error || ""));
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Произошла ошибка при завершении задачи");
        });
    });

    // Удаление задачи
    document.getElementById("delete-task")?.addEventListener("click", () => {
        if (!currentTaskId) return;
        if (!confirm("Вы уверены, что хотите удалить эту задачу?")) return;
        
        fetch(`/delete_task/${currentTaskId}`, {
            method: "DELETE"
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert("Ошибка при удалении задачи: " + (data.error || ""));
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Произошла ошибка при удалении задачи");
        });
    });

    // ==================== ОБРАБОТЧИК ФОРМЫ НАПОМИНАНИЯ ====================
    document.getElementById("reminderForm")?.addEventListener("submit", function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        fetch('/set_reminder', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Напоминание установлено');
                document.getElementById('reminderModal').style.display = 'none';
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при установке напоминания');
        });
    });

    // ==================== ОБРАБОТЧИК ФОРМЫ РЕДАКТИРОВАНИЯ ====================
    document.getElementById("editTaskForm")?.addEventListener("submit", function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const taskId = document.getElementById("editTaskId").value;
        
        fetch(`/edit/${taskId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Ошибка при сохранении изменений');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при сохранении изменений');
        });
    });

    // ==================== ПРОВЕРКА НАПОМИНАНИЙ ====================
    function checkReminders() {
        fetch('/check_reminders')
        .then(response => response.json())
        .then(reminders => {
            if (reminders.length > 0) {
                reminders.forEach(reminder => {
                    showReminderNotification(reminder);
                    markReminderAsShown(reminder.id);
                });
            }
        });
    }

    function showReminderNotification(reminder) {
        const notification = document.createElement('div');
        notification.className = 'reminder-notification';
        notification.innerHTML = `
            <h3>Напоминание: ${reminder.title}</h3>
            <p>${reminder.description || ''}</p>
            <p>Время: ${new Date(reminder.date).toLocaleString()}</p>
            <button class="close-notification">Закрыть</button>
        `;
        
        document.body.appendChild(notification);
        
        notification.querySelector('.close-notification').addEventListener('click', () => {
            notification.remove();
        });
    }

    function markReminderAsShown(reminderId) {
        fetch('/mark_reminder_shown/' + reminderId, {
            method: 'POST'
        });
    }

    // Проверяем напоминания каждые 30 секунд
    setInterval(checkReminders, 30000);
    checkReminders(); // Первоначальная проверка
});

function openTaskModal(id, title, description, responsible, region, priority, date, completed) {
    const modal = document.getElementById('taskModal');
    document.getElementById('taskModalTitle').textContent = title || "";
    document.getElementById('taskModalDescription').textContent = description || "";
    document.getElementById('taskModalResponsible').textContent = responsible || "";
    document.getElementById('taskModalRegion').textContent = region || "";
    document.getElementById('taskModalPriority').textContent = priority || "";
    document.getElementById('taskModalDate').textContent = date || "Без даты";
    document.getElementById('taskModalStatus').textContent = completed === "True" ? "Завершена" : "Активна";
    modal.style.display = "block";
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Обработчики для кнопок в модальном окне задачи
document.addEventListener('DOMContentLoaded', function() {
    // Назначение обработчиков для кнопок в модальном окне задачи
    const taskModal = document.getElementById('taskModal');
    
    // Кнопка "Завершить"
    const completeBtn = document.createElement('button');
    completeBtn.textContent = '✔️ Завершить';
    completeBtn.className = 'action-btn complete';
    completeBtn.addEventListener('click', completeCurrentTask);
    
    // Кнопка "Удалить"
    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '❌ Удалить';
    deleteBtn.className = 'action-btn delete';
    deleteBtn.addEventListener('click', deleteCurrentTask);
    
    // Кнопка "Редактировать"
    const editBtn = document.createElement('button');
    editBtn.textContent = '✏️ Редактировать';
    editBtn.className = 'action-btn edit';
    editBtn.addEventListener('click', () => {
        if (!currentTaskId) return;
        // Заполняем форму редактирования значениями из модалки
        document.getElementById("editTaskId").value = currentTaskId;
        document.getElementById("editTaskTitle").value = modalTitle.textContent;
        document.getElementById("editTaskDescription").value = modalDescription.textContent;
        document.getElementById("editTaskResponsible").value = modalResponsible.textContent;
        document.getElementById("editTaskRegion").value = modalRegion.textContent;
        document.getElementById("editTaskPriority").value = modalPriority.textContent;
        document.getElementById("editTaskDate").value = modalDate.textContent;

        // Устанавливаем action формы
        document.getElementById("editTaskForm").action = "/edit/" + currentTaskId;

        // Закрываем текущее модальное окно задачи
        taskModal.style.display = "none";
        // Открываем модальное окно редактирования
        document.getElementById("editTaskModal").style.display = "block";
    });

    // Контейнер для кнопок
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'modal-buttons';
    buttonsContainer.appendChild(completeBtn);
    buttonsContainer.appendChild(deleteBtn);
    // Добавляем кнопку в контейнер
    buttonsContainer.appendChild(editBtn);
    
    // Добавляем кнопки в модальное окно
    taskModal.querySelector('.modal-content').appendChild(buttonsContainer);
    
    let currentTaskId = null;
    
    function setCurrentTaskId(id) {
        currentTaskId = id;
    }
    
    function completeCurrentTask() {
        if (!currentTaskId) return;
        fetch(`/complete_task/${currentTaskId}`, {
            method: "POST"
        })
        .then(handleResponse)
        .catch(handleError);
    }
    
    function deleteCurrentTask() {
        if (!currentTaskId || !confirm("Вы уверены, что хотите удалить эту задачу?")) return;
        fetch(`/delete_task/${currentTaskId}`, {
            method: "DELETE"
        })
        .then(handleResponse)
        .catch(handleError);
    }
    
    function handleResponse(response) {
        if (response.ok) {
            location.reload();
        } else {
            alert("Ошибка при выполнении операции");
        }
    }
    
    function handleError(error) {
        console.error("Error:", error);
        alert("Произошла ошибка при выполнении операции");
    }
    
    // Обновляем функцию handleTaskClick
    window.handleTaskClick = function(el) {
        setCurrentTaskId(el.dataset.id);
        openTaskModal(
            el.dataset.id,
            el.dataset.title,
            el.dataset.description,
            el.dataset.responsible,
            el.dataset.region,
            el.dataset.priority,
            el.dataset.date,
            el.dataset.completed
        );
    };
    
    // Закрытие модального окна при клике вне его
    window.addEventListener('click', function(event) {
        if (event.target === taskModal) {
            taskModal.style.display = 'none';
        }
    });
});