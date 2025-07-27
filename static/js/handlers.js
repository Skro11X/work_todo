import { api, TaskStatus } from './api.js';

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

// --- Внутреннее состояние ---
let openTasksCache = [];
let closedTasksCache = [];
let selectedFiles = []; // Хранит выбранные для загрузки файлы

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
        loadTasks(openContent, api.getOpenTasks, openTasksCache);
    } else if (activeTab === 'closed') {
        closedTabButton.classList.add('active');
        closedContent.classList.remove('hidden');
        loadTasks(closedContent, api.getClosedTasks, closedTasksCache);
    }
}

/**
 * Динамически загружает и отображает задачи.
 * @param {HTMLElement} contentElement - Элемент контента вкладки (`openContent` или `closedContent`).
 * @param {() => Promise<import('./api.js').TaskModel[]>} fetchApiCall - Функция API для получения задач.
 * @param {import('./api.js').TaskModel[]} cacheArray - Массив для кэширования задач.
 */
async function loadTasks(contentElement, fetchApiCall, cacheArray) {
    const listItemsContainer = contentElement.querySelector('.left-panel');
    const rightPanelContainer = contentElement.querySelector('.right-panel');

    try {
        const tasks = await fetchApiCall();
        cacheArray.splice(0, cacheArray.length, ...tasks); // Очищаем и заполняем кэш

        listItemsContainer.innerHTML = '';
        if (tasks.length === 0) {
            listItemsContainer.innerHTML = '<div style="padding: var(--padding-base); text-align: center; color: var(--light-text-color);">Задач нет.</div>';
            clearRightPanel(rightPanelContainer);
            return;
        }

        tasks.forEach(task => {
            const listItem = document.createElement('div');
            listItem.className = 'list-item';
            listItem.dataset.itemId = task.id;
            listItem.innerHTML = `
                <div class="item-id">${task.project}-${task.id}</div>
                <div class="item-desc">${task.title}</div>`;
            listItem.addEventListener('click', () => handleListItemClick(task.id, contentElement));
            listItemsContainer.appendChild(listItem);
        });

        // Автоматически выбираем первый элемент
        if (listItemsContainer.firstElementChild) {
            listItemsContainer.firstElementChild.click();
        } else {
            clearRightPanel(rightPanelContainer);
        }

    } catch (error) {
        console.error('Не удалось загрузить задачи:', error);
        listItemsContainer.innerHTML = '<div style="padding: var(--padding-base); text-align: center; color: var(--highlight-color);">Ошибка загрузки задач.</div>';
        clearRightPanel(rightPanelContainer);
    }
}

/**
 * Очищает правую панель с деталями задачи.
 * @param {HTMLElement} rightPanelContainer - Элемент правой панели.
 */
function clearRightPanel(rightPanelContainer) {
    rightPanelContainer.querySelector('.right-panel-title').textContent = 'Выберите задачу';
    rightPanelContainer.querySelector('.right-panel .details').innerHTML = '';
    rightPanelContainer.querySelector('.right-panel-description').textContent = '';
    rightPanelContainer.querySelector('.screenshot-placeholder img').src = "https://via.placeholder.com/600x400/333/666?text=Нет+данных";
    rightPanelContainer.querySelector('.screenshot-placeholder img').alt = "Нет данных";
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

    const screenshotImg = rightPanelContainer.querySelector('.screenshot-placeholder img');
    const firstImageFile = task.files.find(f => f.mimetype.startsWith('image/'));
    if (firstImageFile) {
        screenshotImg.src = firstImageFile.url; // Используем URL из API
        screenshotImg.alt = firstImageFile.filename;
    } else {
        screenshotImg.src = "https://via.placeholder.com/600x400/333/666?text=Нет+изображений";
        screenshotImg.alt = "Нет изображений";
    }
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
        alert('Не удалось загрузить детали задачи.');
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

/** Инициализация обработчиков событий */
export function setupEventListeners() {
    // Переключение вкладок
    newTabButton.addEventListener('click', () => switchTab('new'));
    openTabButton.addEventListener('click', () => switchTab('open'));
    closedTabButton.addEventListener('click', () => switchTab('closed'));

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
            organisation: lpuInput.dataset.orgCode,
        };

        try {
            // 1. Создаем задачу
            const newTask = await api.createTask(taskData);
            alert(`Задача "${newTask.title}" (ID: ${newTask.id}) успешно создана!`);

            // 2. Загружаем файлы, если они есть
            if (selectedFiles.length > 0) {
                await api.uploadFilesForTask(newTask.id, selectedFiles);
                alert(`Файлы (${selectedFiles.length} шт.) успешно загружены для задачи ${newTask.id}.`);
            }

            // 3. Сбрасываем форму и очищаем список файлов
            newTaskForm.reset();
            selectedFiles = [];
            renderFileList();
            switchTab('open'); // Переключаемся на вкладку с открытыми задачами
        } catch (error) {
            console.error('Ошибка при создании задачи или загрузке файлов:', error);
            alert(`Ошибка: ${error.message || 'Не удалось создать задачу.'}`);
        }
    });
}