const API_BASE_URL = '/api/v1';

const TaskStatus = {
    NEW: 'new',
    IN_PROGRESS: 'in_progress',
    DONE: 'done',
};

class FileModel {
    constructor({ id, filename, mimetype, url }) {
        this.id = id;
        this.filename = filename;
        this.mimetype = mimetype;
        this.url = url;
    }
}

class TaskModel {
    constructor({ id, title, description, project, organisation, status, created_at, updated_at, files = [] }) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.project = project;
        this.organisation = organisation; // Здесь будет полное имя, например "ГП 17"
        this.status = status;
        this.created_at = new Date(created_at);
        this.updated_at = new Date(updated_at);
        this.files = files.map(file => new FileModel(file));
    }
}

// Функции для взаимодействия с API
const api = {
    /**
     * Создает новую задачу.
     * @param {object} taskData - Объект с деталями задачи.
     * @returns {Promise<TaskModel>} - Промис, который разрешается новым экземпляром TaskModel.
     */
    async createTask(taskData) {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData),
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
    },

    /**
     * Загружает файлы для указанной задачи.
     * @param {number} taskId - ID задачи.
     * @param {File[]} files - Массив объектов File.
     * @returns {Promise<FileModel[]>} - Промис, который разрешается массивом экземпляров FileModel.
     */
    async uploadFilesForTask(taskId, files) {
        if (files.length === 0) return [];

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file, file.name);
        });

        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/files/`, {
                method: 'POST',
                body: formData, // Отправляем все файлы одним запросом
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Не удалось загрузить файлы');
            }
            const data = await response.json();
            return data.map(file => new FileModel(file));
        } catch (error) {
            console.error(`Ошибка при загрузке файлов для задачи ${taskId}:`, error);
            throw error;
        }
    },

    /**
     * Получает одну задачу по ее ID.
     * @param {number} taskId
     * @returns {Promise<TaskModel>}
     */
    async getTaskById(taskId) {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Не удалось получить задачу ${taskId}`);
            }
            const data = await response.json();
            return new TaskModel(data);
        } catch (error) {
            console.error(`Ошибка при получении задачи ${taskId}:`, error);
            throw error;
        }
    },

    /**
     * Получает список открытых задач.
     * @returns {Promise<TaskModel[]>}
     */
    async getOpenTasks() {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/?status=${TaskStatus.IN_PROGRESS}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Не удалось получить открытые задачи');
            }
            const data = await response.json();
            return data.map(task => new TaskModel(task));
        } catch (error) {
            console.error('Ошибка при получении открытых задач:', error);
            throw error;
        }
    },

    /**
     * Получает список закрытых задач.
     * @returns {Promise<TaskModel[]>}
     */
    async getClosedTasks() {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/?status=${TaskStatus.DONE}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Не удалось получить закрытые задачи');
            }
            const data = await response.json();
            return data.map(task => new TaskModel(task));
        } catch (error) {
            console.error('Ошибка при получении закрытых задач:', error);
            throw error;
        }
    },
};

export { api, TaskModel, FileModel, TaskStatus };