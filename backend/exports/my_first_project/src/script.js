document.addEventListener('DOMContentLoaded', () => {
    // DOM 元素引用
    const taskInput = document.getElementById('taskInput');
    const addBtn = document.getElementById('addBtn');
    const taskList = document.getElementById('taskList');
    const emptyState = document.getElementById('emptyState');

    // 从 localStorage 加载任务
    let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

    // 初始化渲染
    renderTasks();

    // 事件监听：点击添加按钮
    addBtn.addEventListener('click', handleAddTask);

    // 事件监听：输入框回车键
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleAddTask();
        }
    });

    /**
     * 处理添加任务逻辑
     */
    function handleAddTask() {
        const text = taskInput.value.trim();

        // 校验非空
        if (!text) {
            return;
        }

        // 创建新任务对象
        const newTask = {
            id: generateUUID(),
            text: text,
            isCompleted: false
        };

        // 添加到数组头部
        tasks.unshift(newTask);

        // 更新存储并重新渲染
        saveTasks();
        renderTasks();

        // 清空输入框
        taskInput.value = '';
        taskInput.focus();
    }

    /**
     * 生成唯一 ID
     */
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * 保存任务到 localStorage
     */
    function saveTasks() {
        localStorage.setItem('tasks', JSON.stringify(tasks));
    }

    /**
     * 渲染任务列表
     */
    function renderTasks() {
        // 清空当前列表
        taskList.innerHTML = '';

        // 切换空状态显示
        if (tasks.length === 0) {
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
        }

        // 遍历任务数组生成 DOM
        tasks.forEach(task => {
            const li = document.createElement('li');
            li.className = `task-item ${task.isCompleted ? 'completed' : ''}`;
            li.dataset.id = task.id;

            // 复选框
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'task-checkbox';
            checkbox.checked = task.isCompleted;
            checkbox.addEventListener('change', () => toggleTaskCompletion(task.id));

            // 任务文本
            const span = document.createElement('span');
            span.className = 'task-text';
            span.textContent = task.text;

            // 删除按钮
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerHTML = '&times;'; // X 符号
            deleteBtn.title = '删除任务';
            deleteBtn.addEventListener('click', () => deleteTask(task.id, li));

            // 组装组件
            li.appendChild(checkbox);
            li.appendChild(span);
            li.appendChild(deleteBtn);

            // 插入列表
            taskList.appendChild(li);
        });
    }

    /**
     * 标记任务完成/未完成
     * @param {string} id - 任务 ID
     */
    function toggleTaskCompletion(id) {
        const taskIndex = tasks.findIndex(t => t.id === id);
        if (taskIndex > -1) {
            tasks[taskIndex].isCompleted = !tasks[taskIndex].isCompleted;
            saveTasks();
            // 局部更新 DOM 样式，避免全量重绘导致的焦点丢失等问题
            const taskItem = document.querySelector(`.task-item[data-id="${id}"]`);
            if (taskItem) {
                taskItem.classList.toggle('completed', tasks[taskIndex].isCompleted);
            }
        }
    }

    /**
     * 删除任务
     * @param {string} id - 任务 ID
     * @param {HTMLElement} element - 对应的 DOM 元素
     */
    function deleteTask(id, element) {
        // 弹出确认提示
        const confirmDelete = window.confirm("确定要删除该任务吗？");
        
        if (confirmDelete) {
            // 添加淡出动画类
            element.classList.add('fade-out');

            // 等待动画结束后移除 DOM 和数据
            element.addEventListener('animationend', () => {
                tasks = tasks.filter(t => t.id !== id);
                saveTasks();
                renderTasks();
            }, { once: true });
        }
    }
});