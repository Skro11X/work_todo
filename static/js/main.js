import { setupEventListeners } from './handlers.js';

document.addEventListener('DOMContentLoaded', () => {
    // Инициализируем все обработчики событий
    setupEventListeners();

    // По умолчанию открываем вкладку "Новая"
    document.getElementById('newTab').click();
});