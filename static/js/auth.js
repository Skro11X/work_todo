// /static/js/auth.js

import { API_BASE_URL } from './api.js'; // Предполагаем, что API_BASE_URL экспортируется из api.js
import { toast } from './toast.js';

/**
 * Регистрирует нового пользователя.
 * @param {string} username - Имя пользователя.
 * @param {string} password - Пароль.
 * @returns {Promise<object>} - Промис, который разрешается объектом с данными пользователя.
 */
async function registerUser(username, password) {
    try {
        // Замените '/auth/register' на ваш реальный эндпоинт регистрации
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            // Выводим более конкретную ошибку от сервера
            throw new Error(errorData.detail || 'Не удалось зарегистрироваться');
        }

        const data = await response.json();
        toast.success(`Пользователь ${data.username} успешно зарегистрирован!`);
        return data;

    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        toast.error(`Ошибка регистрации: ${error.message}`);
        throw error; // Пробрасываем ошибку дальше для обработки в UI
    }
}

export { registerUser };