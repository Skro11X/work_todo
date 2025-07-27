const API_BASE_URL = '/api/v1';

const TaskStatus = {
    NEW: 'new',
    IN_PROGRESS: 'in_progress',
    DONE: 'done',
};

class FileModel {
    constructor({ id, filename, mimetype, size }) {
        this.id = id;
        this.filename = filename;
        this.mimetype = mimetype;
        this.size = size || 0;
        this.url = `${API_BASE_URL}/tasks/files/${id}`; // Генерируем URL на клиенте
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

        // Загружаем файлы по одному, так как API принимает один файл за раз
        const uploadedFiles = [];
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file, file.name); // Изменили с 'files' на 'file'

            try {
                const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/files/`, {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Не удалось загрузить файл');
                }
                const data = await response.json();
                uploadedFiles.push(new FileModel(data));
            } catch (error) {
                console.error(`Ошибка при загрузке файла ${file.name} для задачи ${taskId}:`, error);
                throw error;
            }
        }
        
        return uploadedFiles;
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
     * Получает список открытых задач (статусы: NEW и IN_PROGRESS).
     * @param {string} searchQuery - Поисковый запрос (опционально).
     * @returns {Promise<TaskModel[]>}
     */
    async getOpenTasks(searchQuery = '') {
        try {
            // Делаем два отдельных запроса для разных статусов
            const [newTasks, inProgressTasks] = await Promise.all([
                this.getTasksByStatus(TaskStatus.NEW, searchQuery),
                this.getTasksByStatus(TaskStatus.IN_PROGRESS, searchQuery)
            ]);
            
            // Объединяем результаты и сортируем по дате обновления (новые сверху)
            const allTasks = [...newTasks, ...inProgressTasks];
            return allTasks.sort((a, b) => b.updated_at - a.updated_at);
        } catch (error) {
            console.error('Ошибка при получении открытых задач:', error);
            throw error;
        }
    },

    /**
     * Получает список закрытых задач.
     * @param {string} searchQuery - Поисковый запрос (опционально).
     * @returns {Promise<TaskModel[]>}
     */
    async getClosedTasks(searchQuery = '') {
        try {
            return await this.getTasksByStatus(TaskStatus.DONE, searchQuery);
        } catch (error) {
            console.error('Ошибка при получении закрытых задач:', error);
            throw error;
        }
    },

    /**
     * Получает задачи по статусу с опциональным поиском.
     * @param {string} status - Статус задач.
     * @param {string} searchQuery - Поисковый запрос (опционально).
     * @returns {Promise<TaskModel[]>}
     */
    async getTasksByStatus(status, searchQuery = '') {
        try {
            let url = `${API_BASE_URL}/tasks/?status=${status}`;
            if (searchQuery.trim()) {
                // Ищем по заголовку (title)
                url += `&title=${encodeURIComponent(searchQuery.trim())}`;
            }
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Не удалось получить задачи со статусом ${status}`);
            }
            const data = await response.json();
            return data.map(task => new TaskModel(task));
        } catch (error) {
            console.error(`Ошибка при получении задач со статусом ${status}:`, error);
            throw error;
        }
    },
};

export { api, TaskModel, FileModel, TaskStatus };