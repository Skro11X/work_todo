/**
 * Toast notification system
 */

const TOAST_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    INFO: 'info'
};

const TOAST_DURATION = {
    SHORT: 3000,
    MEDIUM: 5000,
    LONG: 8000
};

class ToastManager {
    constructor() {
        this.container = document.getElementById('toastContainer');
        if (!this.container) {
            console.error('Toast container not found! Make sure there is an element with id="toastContainer"');
        }
    }

    /**
     * Показывает toast уведомление
     * @param {string} message - Текст сообщения
     * @param {string} type - Тип уведомления (success, error, info)
     * @param {number} duration - Длительность показа в миллисекундах
     */
    show(message, type = TOAST_TYPES.INFO, duration = TOAST_DURATION.MEDIUM) {
        if (!this.container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const closeButton = document.createElement('button');
        closeButton.className = 'toast-close';
        closeButton.innerHTML = '×';
        closeButton.addEventListener('click', () => this.remove(toast));

        toast.innerHTML = `
            <div>${message}</div>
        `;
        toast.appendChild(closeButton);

        this.container.appendChild(toast);

        // Анимация появления
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Автоматическое удаление
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        return toast;
    }

    /**
     * Удаляет toast уведомление
     * @param {HTMLElement} toast - Элемент toast
     */
    remove(toast) {
        if (!toast || !toast.parentNode) return;

        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Показывает уведомление об успехе
     * @param {string} message - Текст сообщения
     * @param {number} duration - Длительность показа
     */
    success(message, duration = TOAST_DURATION.MEDIUM) {
        return this.show(message, TOAST_TYPES.SUCCESS, duration);
    }

    /**
     * Показывает уведомление об ошибке
     * @param {string} message - Текст сообщения
     * @param {number} duration - Длительность показа
     */
    error(message, duration = TOAST_DURATION.LONG) {
        return this.show(message, TOAST_TYPES.ERROR, duration);
    }

    /**
     * Показывает информационное уведомление
     * @param {string} message - Текст сообщения
     * @param {number} duration - Длительность показа
     */
    info(message, duration = TOAST_DURATION.MEDIUM) {
        return this.show(message, TOAST_TYPES.INFO, duration);
    }

    /**
     * Очищает все toast уведомления
     */
    clear() {
        if (!this.container) return;
        
        const toasts = this.container.querySelectorAll('.toast');
        toasts.forEach(toast => this.remove(toast));
    }
}

// Создаем глобальный экземпляр
const toast = new ToastManager();

export { toast, TOAST_TYPES, TOAST_DURATION };
