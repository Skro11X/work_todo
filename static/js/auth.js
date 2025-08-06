import {api, TaskModel, TaskStatus} from './api.js';
import {toast} from './toast.js';

class CreateUserModel {
    constructor({ username, password, password_confirm }) {
        this.username = id;
        this.password = filename;
        this.password_confirm = mimetype;
    }
}

const auth = {
    async createNewUser(CreateUserModel) {
        try {
            const response = await fetch(`${API_BASE_URL}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(CreateUserModel),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Не удалось создать задачу');
            }
            const data = await response.json();
            return new TaskModel(data);
        } catch (error) {
            console.error('Ошибка при создании задачи:', error);
            throw error;
        }
    }
}