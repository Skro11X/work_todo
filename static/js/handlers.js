import { api, TaskStatus } from './api.js';
import { toast } from './toast.js';
import { get_form } from './auth.js';

const newTabButton = document.getElementById('newTab');
const openTabButton = document.getElementById('openTab');
const closedTabButton = document.getElementById('closedTab');

const newContent = document.getElementById('newContent');
const openContent = document.getElementById('openContent');
const closedContent = document.getElementById('closedContent');

const fileDropArea = document.getElementById('fileDropArea');
const fileInput = document.getElementById('files');
const fileListContainer = document.getElementById('fileListContainer');
const newTaskForm = document.querySelector('.new-task-form');

const searchInput = document.getElementById('searchInput');
const searchInputClosed = document.getElementById('searchInputClosed');

const registerBtn = document.getElementById("registerBtn")
const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
// --- Внутреннее состояние ---
let openTasksCache = [];
let closedTasksCache = [];
let selectedFiles = []; // Хранит выбранные для загрузки файлы
let searchTimeout = null;

/**
 * Переключает активную вкладку.
 * @param {'new' | 'open' | 'closed'} activeTab - Идентификатор вкладки.
 */
function switchTab(activeTab) {
    [newTabButton, openTabButton, closedTabButton].forEach(btn => btn.classList.remove('active'));
    [newContent, openContent, closedContent].forEach(content => content.classList.add('hidden'));

    if (activeTab === 'new') {
        newTabButton.classList.add('active');
        newContent.classList.remove('hidden');
    } else if (activeTab === 'open') {
        openTabButton.classList.add('active');
        openContent.classList.remove('hidden');
        loadTasks(openContent, (search) => api.getOpenTasks(search), openTasksCache, 'open');
    } else if (activeTab === 'closed') {
        closedTabButton.classList.add('active');
        closedContent.classList.remove('hidden');
        loadTasks(closedContent, (search) => api.getClosedTasks(search), closedTasksCache, 'closed');
    }
}

/**
 * Динамически загружает и отображает задачи.
 * @param {HTMLElement} contentElement - Элемент контента вкладки (`openContent` или `closedContent`).
 * @param {(search: string) => Promise<import('./api.js').TaskModel[]>} fetchApiCall - Функция API для получения задач.
 * @param {import('./api.js').TaskModel[]} cacheArray - Массив для кэширования задач.
 * @param {string} tabType - Тип вкладки ('open' или 'closed').
 */
async function loadTasks(contentElement, fetchApiCall, cacheArray, tabType) {
    const listItemsContainer = contentElement.querySelector('.tasks-list');
    const rightPanelContainer = contentElement.querySelector('.right-panel');
    const searchInput = contentElement.querySelector('.search-input');
    const searchQuery = searchInput ? searchInput.value : '';

    try {
        const tasks = await fetchApiCall(searchQuery);
        cacheArray.splice(0, cacheArray.length, ...tasks); // Очищаем и заполняем кэш

        listItemsContainer.innerHTML = '';
        if (tasks.length === 0) {
            const emptyMessage = searchQuery 
                ? 'По вашему запросу ничего не найдено.' 
                : 'Задач нет.';
            listItemsContainer.innerHTML = `<div style="padding: var(--padding-base); text-align: center; color: var(--light-text-color);">${emptyMessage}</div>`;
            clearRightPanel(rightPanelContainer);
            return;
        }

        tasks.forEach(task => {
            const listItem = document.createElement('div');
            listItem.className = 'list-item';
            listItem.dataset.itemId = task.id;
            
            // Добавляем бейдж статуса для открытых задач
            const statusBadge = tabType === 'open' ? getStatusBadge(task.status) : '';
            
            listItem.innerHTML = `
                <div class="item-id">${task.project}-${task.id}${statusBadge}</div>
                <div class="item-desc">${task.title}</div>`;
            listItem.addEventListener('click', () => handleListItemClick(task.id, contentElement));
            listItemsContainer.appendChild(listItem);
        });

        // Автоматически выбираем первый элемент
        if (listItemsContainer.firstElementChild && !listItemsContainer.firstElementChild.textContent.includes('По вашему запросу')) {
            listItemsContainer.firstElementChild.click();
        } else {
            clearRightPanel(rightPanelContainer);
        }

    } catch (error) {
        console.error('Не удалось загрузить задачи:', error);
        toast.error(`Ошибка загрузки задач: ${error.message}`);
        listItemsContainer.innerHTML = '<div style="padding: var(--padding-base); text-align: center; color: var(--highlight-color);">Ошибка загрузки задач.</div>';
        clearRightPanel(rightPanelContainer);
    }
}

/**
 * Возвращает HTML для бейджа статуса задачи.
 * @param {string} status - Статус задачи.
 * @returns {string} HTML строка с бейджем.
 */
function getStatusBadge(status) {
    const statusLabels = {
        [TaskStatus.NEW]: 'Новая',
        [TaskStatus.IN_PROGRESS]: 'В процессе',
        [TaskStatus.DONE]: 'Выполнена'
    };
    
    const statusClass = status.replace('_', '-');
    const label = statusLabels[status] || status;
    
    return `<span class="task-status-badge ${statusClass}">${label}</span>`;
}

/**
 * Очищает правую панель с деталями задачи.
 * @param {HTMLElement} rightPanelContainer - Элемент правой панели.
 */
function clearRightPanel(rightPanelContainer) {
    rightPanelContainer.querySelector('.right-panel-title').textContent = 'Выберите задачу';
    rightPanelContainer.querySelector('.right-panel .details').innerHTML = '';
    rightPanelContainer.querySelector('.right-panel-description').textContent = '';
    
    // Очищаем файлы
    const filesGrid = rightPanelContainer.querySelector('.files-grid');
    if (filesGrid) {
        filesGrid.innerHTML = '';
    }
}

/**
 * Отображает детали выбранной задачи.
 * @param {import('./api.js').TaskModel} task - Объект задачи.
 * @param {HTMLElement} rightPanelContainer - Элемент правой панели.
 */
function displayTaskDetails(task, rightPanelContainer) {
    rightPanelContainer.querySelector('.right-panel-title').textContent = task.title;
    rightPanelContainer.querySelector('.details').innerHTML = `
        <p>Дата: ${task.created_at.toLocaleDateString()} - ${task.updated_at.toLocaleDateString()}</p>
        <p>Проект: ${task.project}</p>
        <p>ЛПУ: ${task.organisation}</p>`;
    rightPanelContainer.querySelector('.right-panel-description').textContent = task.description;

    // Отображаем все файлы
    displayTaskFiles(task.files, rightPanelContainer);
}

/**
 * Отображает файлы задачи в сетке.
 * @param {import('./api.js').FileModel[]} files - Массив файлов.
 * @param {HTMLElement} rightPanelContainer - Элемент правой панели.
 */
function displayTaskFiles(files, rightPanelContainer) {
    const filesGrid = rightPanelContainer.querySelector('.files-grid');
    
    if (!filesGrid) {
        console.error('Элемент .files-grid не найден в DOM');
        return;
    }
    
    if (!files || files.length === 0) {
        filesGrid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; color: var(--light-text-color); padding: 20px;">Файлы не прикреплены</div>';
        return;
    }

    filesGrid.innerHTML = '';
    
    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.dataset.fileId = file.id;
        
        const thumbnail = createFileThumbnail(file);
        const fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = file.filename;
        
        const fileSize = document.createElement('div');
        fileSize.className = 'file-size';
        fileSize.textContent = formatFileSize(file.size || 0);
        
        fileItem.appendChild(thumbnail);
        fileItem.appendChild(fileName);
        fileItem.appendChild(fileSize);
        
        // Добавляем обработчик клика
        fileItem.addEventListener('click', () => handleFileClick(file));
        
        filesGrid.appendChild(fileItem);
    });
}

/**
 * Создает миниатюру файла.
 * @param {import('./api.js').FileModel} file - Объект файла.
 * @returns {HTMLElement} Элемент миниатюры.
 */
function createFileThumbnail(file) {
    const thumbnail = document.createElement('div');
    thumbnail.className = 'file-thumbnail';
    
    if (file.mimetype && file.mimetype.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = file.url;
        img.alt = file.filename;
        img.onerror = () => {
            // Если изображение не загрузилось, показываем иконку
            thumbnail.innerHTML = '<div class="file-icon image"></div>';
        };
        thumbnail.appendChild(img);
    } else {
        const icon = document.createElement('div');
        icon.className = `file-icon ${getFileTypeClass(file.mimetype)}`;
        thumbnail.appendChild(icon);
    }
    
    return thumbnail;
}

/**
 * Определяет класс CSS для типа файла.
 * @param {string} mimetype - MIME тип файла.
 * @returns {string} Класс CSS.
 */
function getFileTypeClass(mimetype) {
    if (!mimetype) return 'unknown';
    
    if (mimetype.startsWith('image/')) return 'image';
    if (mimetype.startsWith('video/')) return 'video';
    if (mimetype.startsWith('audio/')) return 'audio';
    if (mimetype.includes('pdf')) return 'pdf';
    if (mimetype.includes('text/') || mimetype.includes('json') || mimetype.includes('xml')) return 'text';
    if (mimetype.includes('zip') || mimetype.includes('rar') || mimetype.includes('7z')) return 'archive';
    if (mimetype.includes('javascript') || mimetype.includes('python') || mimetype.includes('java')) return 'code';
    if (mimetype.includes('document') || mimetype.includes('word') || mimetype.includes('excel')) return 'document';
    
    return 'unknown';
}

/**
 * Форматирует размер файла в читаемый вид.
 * @param {number} bytes - Размер в байтах.
 * @returns {string} Форматированный размер.
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Обрабатывает клик по файлу.
 * @param {import('./api.js').FileModel} file - Объект файла.
 */
function handleFileClick(file) {
    if (file.mimetype && file.mimetype.startsWith('image/')) {
        // Для изображений открываем модальное окно
        openImageModal(file);
    } else {
        // Для других файлов просто скачиваем
        downloadFile(file);
    }
}

/**
 * Открывает модальное окно с изображением.
 * @param {import('./api.js').FileModel} file - Объект файла изображения.
 */
function openImageModal(file) {
    const modal = document.getElementById('imageModal');
    if (!modal) {
        console.error('Модальное окно imageModal не найдено');
        return;
    }
    
    const modalImage = document.getElementById('modalImage');
    const modalFilename = modal.querySelector('.modal-filename');
    const modalDownload = document.getElementById('modalDownload');
    
    if (!modalImage || !modalFilename || !modalDownload) {
        console.error('Элементы модального окна не найдены');
        return;
    }
    
    modalImage.src = file.url;
    modalImage.alt = file.filename;
    modalFilename.textContent = file.filename;
    modalDownload.href = file.url;
    modalDownload.download = file.filename;
    
    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.add('show'), 10);
}

/**
 * Закрывает модальное окно с изображением.
 */
function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (!modal) {
        console.error('Модальное окно imageModal не найдено');
        return;
    }
    
    modal.classList.remove('show');
    setTimeout(() => modal.classList.add('hidden'), 300);
}

/**
 * Скачивает файл.
 * @param {import('./api.js').FileModel} file - Объект файла.
 */
function downloadFile(file) {
    const link = document.createElement('a');
    link.href = file.url;
    link.download = file.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Обрабатывает клик по элементу списка задач.
 * @param {number} taskId - ID задачи.
 * @param {HTMLElement} currentContentElement - Текущий элемент контента вкладки.
 */
async function handleListItemClick(taskId, currentContentElement) {
    const rightPanelContainer = currentContentElement.querySelector('.right-panel');
    const cache = (currentContentElement === openContent) ? openTasksCache : closedTasksCache;

    // Снимаем выделение со старого элемента и выделяем новый
    const currentActive = currentContentElement.querySelector('.list-item.active');
    if (currentActive) currentActive.classList.remove('active');
    currentContentElement.querySelector(`.list-item[data-item-id="${taskId}"]`).classList.add('active');

    try {
        let task = cache.find(t => t.id === taskId);
        if (!task) task = await api.getTaskById(taskId); // Если в кэше нет, загружаем
        displayTaskDetails(task, rightPanelContainer);
    } catch (error) {
        console.error(`Ошибка при получении деталей задачи ${taskId}:`, error);
        toast.error(`Не удалось загрузить детали задачи: ${error.message}`);
        clearRightPanel(rightPanelContainer);
    }
}

/**
 * Отображает список выбранных файлов в форме.
 */
function renderFileList() {
    fileListContainer.innerHTML = ''; // Очищаем контейнер
    if (selectedFiles.length === 0) {
        fileDropArea.querySelector('span').style.display = 'block';
        fileDropArea.childNodes[0].nodeValue = 'Кликните для выбора файлов или просто перетащите их сюда';
    } else {
         fileDropArea.querySelector('span').style.display = 'none';
        fileDropArea.childNodes[0].nodeValue = `Выбрано файлов: ${selectedFiles.length}. Перетащите еще или кликните.`;
    }

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-list-item';
        fileItem.textContent = file.name;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'file-remove-btn';
        removeBtn.textContent = '×';
        removeBtn.type = 'button'; // Важно, чтобы не сабмитить форму
        removeBtn.onclick = () => {
            selectedFiles.splice(index, 1); // Удаляем файл из массива
            renderFileList(); // Перерисовываем список
        };

        fileItem.appendChild(removeBtn);
        fileListContainer.appendChild(fileItem);
    });
}

/**
 * Обрабатывает добавление файлов (через drag-n-drop или выбор).
 * @param {FileList} newFiles - Список добавленных файлов.
 */
function handleFiles(newFiles) {
    // Преобразуем FileList в массив и добавляем только уникальные файлы
    Array.from(newFiles).forEach(file => {
        if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    });
    renderFileList(); // Обновляем UI
}

/**
 * Обрабатывает поиск задач с дебаунсом.
 * @param {HTMLElement} contentElement - Элемент контента вкладки.
 * @param {(search: string) => Promise<import('./api.js').TaskModel[]>} fetchApiCall - Функция API для получения задач.
 * @param {import('./api.js').TaskModel[]} cacheArray - Массив для кэширования задач.
 * @param {string} tabType - Тип вкладки ('open' или 'closed').
 */
function handleSearch(contentElement, fetchApiCall, cacheArray, tabType) {
    // Очищаем предыдущий таймаут
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // Устанавливаем новый таймаут для дебаунса
    searchTimeout = setTimeout(() => {
        loadTasks(contentElement, fetchApiCall, cacheArray, tabType);
    }, 300); // 300мс задержка
}

/** Инициализация обработчиков событий */
export function setupEventListeners() {
    // Переключение вкладок
    newTabButton.addEventListener('click', () => switchTab('new'));
    openTabButton.addEventListener('click', () => switchTab('open'));
    closedTabButton.addEventListener('click', () => switchTab('closed'));

    // Поиск задач
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            handleSearch(openContent, (search) => api.getOpenTasks(search), openTasksCache, 'open');
        });
    }
    
    if (searchInputClosed) {
        searchInputClosed.addEventListener('input', () => {
            handleSearch(closedContent, (search) => api.getClosedTasks(search), closedTasksCache, 'closed');
        });
    }

    // --- Логика для загрузки файлов ---
    fileDropArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => handleFiles(fileInput.files));

    // Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.add('highlight'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.remove('highlight'), false);
    });
    fileDropArea.addEventListener('drop', e => handleFiles(e.dataTransfer.files), false);

    // --- Логика для формы создания задачи ---
    newTaskForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const lpuInput = document.getElementById('lpu');

        const taskData = {
            title: document.getElementById('subject').value,
            description: document.getElementById('text').value,
            project: document.getElementById('taskType').value,
            organisation: lpuInput.value, // Используем полное название, а не код
        };

        try {
            // 1. Создаем задачу
            const newTask = await api.createTask(taskData);
            toast.success(`Задача "${newTask.title}" (ID: ${newTask.id}) успешно создана!`);

            // 2. Загружаем файлы, если они есть
            if (selectedFiles.length > 0) {
                await api.uploadFilesForTask(newTask.id, selectedFiles);
                toast.success(`Файлы (${selectedFiles.length} шт.) успешно загружены для задачи ${newTask.id}.`);
            }

            // 3. Сбрасываем форму и очищаем список файлов
            newTaskForm.reset();
            selectedFiles = [];
            renderFileList();
            switchTab('open'); // Переключаемся на вкладку с открытыми задачами
        } catch (error) {
            console.error('Ошибка при создании задачи или загрузке файлов:', error);
            toast.error(`Ошибка: ${error.message || 'Не удалось создать задачу.'}`);
        }
    });

    // --- Обработчики для модального окна ---
    const imageModal = document.getElementById('imageModal');
    
    if (imageModal) {
        const modalClose = imageModal.querySelector('.modal-close');
        
        if (modalClose) {
            modalClose.addEventListener('click', closeImageModal);
        }
        
        // Закрытие модального окна по клику на фон
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) {
                closeImageModal();
            }
        });
    }
    
    // Закрытие модального окна по нажатию Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const imageModal = document.getElementById('imageModal');
            if (imageModal && !imageModal.classList.contains('hidden')) {
                closeImageModal();
            }
        }
    });
//     Открытие модального окна формы и регистрации
    registerBtn.addEventListener("click", () => {
            const wrapper = document.getElementById('authModal');

            wrapper.classList.remove('hidden');
            wrapper.classList.add('show');
    })
    signUpButton.addEventListener('click', () => {
        const wrapper = document.getElementById('authModal');
        const container = wrapper.querySelector('#container');
        container.classList.add('right-panel-active');
    })


    signInButton.addEventListener('click', () => {
        const wrapper = document.getElementById('authModal');
        const container = wrapper.querySelector('#container');
        container.classList.remove('right-panel-active');
    })
}