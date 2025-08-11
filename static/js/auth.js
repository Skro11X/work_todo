// js/auth.js (заменить всё содержимое)

import {toast} from './toast.js';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// ИСПРАВЛЕНО: Модель для создания пользователя
class CreateUserModel {
    constructor({username, password, password_confirm}) {
        this.username = username;
        this.password = password;
        this.password_confirm = password_confirm;
    }
}

// Создаем объект для работы с API аутентификации
export const authApi = {
    /**
     * Регистрирует нового пользователя.
     * @param {object} userData - Данные пользователя { username, password, password_confirm }.
     * @returns {Promise<object>} - Данные созданного пользователя.
     */
    async createNewUser(userData) {
        // Создаем экземпляр модели для возможной валидации в будущем
        const userToCreate = new CreateUserModel(userData);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register/`, { // Используем правильный URL
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(userToCreate),
            });

            // Если ответ не успешный, получаем текст ошибки от сервера
            if (!response.ok) {
                const errorData = await response.json();
                let messages = [];

                // Если есть detail — добавляем в начало
                if (errorData.detail) {
                    messages.push(errorData.detail);
                }

                // Если есть errors — собираем все msg
                if (Array.isArray(errorData.errors)) {
                    messages.push(...errorData.errors.map(err => ":\n" + err.loc[1] + ":\n" + err.msg));
                }

                const errorMessage = "\n\n" + messages.join('\n');
                throw new Error(errorMessage || 'Не удалось зарегистрироваться');
            }

            // ИСПРАВЛЕНО: Возвращаем данные пользователя, а не TaskModel
            return await response.json();

        } catch (error) {
            console.error('Ошибка при регистрации пользователя:', error);
            // Пробрасываем ошибку дальше, чтобы ее поймал обработчик в handlers.js
            throw error;
        }
    },

    /**
     * Авторизует пользователя.
     * @param {object} credentials - Данные для входа { username, password }.
     * @returns {Promise<object>} - Токены доступа.
     */
    async loginUser(credentials) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(credentials),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка авторизации');
            }

            const data = await response.json();
            // localStorage.setItem('accessToken', data.access);
            // localStorage.setItem('refreshToken', data.refresh);
            return data;
        } catch (error) {
            console.error('Ошибка при авторизации:', error);
            throw error;
        }
    },
    /**
     * Выход пользователя из системы.
     * Отправляет запрос на бэкенд для инвалидации сессии/токена.
     * @returns {Promise<void>}
     */
    async logoutUser() {
        try {
            // Обычно для выхода используется POST-запрос, чтобы бэкенд мог очистить сессию/куки.
            const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Не удалось выйти' }));
                throw new Error(errorData.detail || 'Ошибка выхода');
            }
            // Успешный выход обычно не возвращает тело ответа.
        } catch (error) {
            console.error('Ошибка при выходе из системы:', error);
            throw error;
        }
    },
    // Эта функция должна делать GET-запрос на эндпоинт, возвращающий данные пользователя
    // Например, /api/v1/users/me/
    async getCurrentUser() {
        const response = await fetch(`${API_BASE_URL}/auth/users/me/`, { // Стандартный эндпоинт для "текущего пользователя"
            method: 'GET',
        });
        if (!response.ok) {
            throw new Error('Нет доступа к пользователям');
        }
        return response.json(); // Ожидаем { "username": "имя_пользователя" }
    }
};