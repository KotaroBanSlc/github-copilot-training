const form = document.querySelector('#todo-form');
const titleInput = document.querySelector('#title');
const formMessage = document.querySelector('#form-message');
const statusMessage = document.querySelector('#status-message');
const todoList = document.querySelector('#todo-list');
const todoCount = document.querySelector('#todo-count');

let todos = [];
let busy = false;

function setMessage(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle('is-error', isError);
}

function setBusy(value) {
  busy = value;
  form.querySelector('button').disabled = value;
  titleInput.disabled = value;
  todoList.querySelectorAll('button, input').forEach((control) => {
    control.disabled = value;
  });
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.message || `HTTP ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function renderTodos() {
  todoList.replaceChildren();
  todoCount.textContent = `${todos.length}\u4ef6`;

  if (todos.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.className = 'empty-state';
    emptyItem.textContent = 'Todo\u306f\u3042\u308a\u307e\u305b\u3093\u3002';
    todoList.append(emptyItem);
    return;
  }

  todos.forEach((todo) => {
    const item = document.createElement('li');
    item.className = `todo-item${todo.completed === 1 ? ' is-completed' : ''}`;
    item.dataset.todoId = todo.id;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = todo.completed === 1;
    checkbox.setAttribute('aria-label', `${todo.title}\u306e\u5b8c\u4e86\u72b6\u614b`);
    checkbox.addEventListener('change', () => updateTodo(todo, checkbox.checked ? 1 : 0));

    const title = document.createElement('span');
    title.className = 'todo-title';
    title.textContent = todo.title;

    const actions = document.createElement('div');
    actions.className = 'todo-actions';

    const editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.textContent = '\u7de8\u96c6';
    editButton.addEventListener('click', () => editTodo(todo));

    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.textContent = '\u524a\u9664';
    deleteButton.addEventListener('click', () => deleteTodo(todo));

    actions.append(editButton, deleteButton);
    item.append(checkbox, title, actions);
    todoList.append(item);
  });
}

async function loadTodos() {
  setMessage(statusMessage, '\u8aad\u307f\u8fbc\u307f\u4e2d...');
  try {
    todos = await requestJson('/api/todos');
    renderTodos();
    setMessage(statusMessage, '\u4e00\u89a7\u3092\u8aad\u307f\u8fbc\u307f\u307e\u3057\u305f\u3002');
  } catch (error) {
    setMessage(statusMessage, `\u4e00\u89a7\u3092\u8aad\u307f\u8fbc\u3081\u307e\u305b\u3093: ${error.message}`, true);
  }
}

async function updateTodo(todo, completed, title = todo.title) {
  if (busy) return;
  setBusy(true);
  try {
    await requestJson(`/api/todos/${todo.id}`, {
      method: 'PUT',
      body: JSON.stringify({ title, completed }),
    });
    await loadTodos();
  } catch (error) {
    setMessage(statusMessage, `Todo\u3092\u66f4\u65b0\u3067\u304d\u307e\u305b\u3093: ${error.message}`, true);
    renderTodos();
  } finally {
    setBusy(false);
  }
}

async function editTodo(todo) {
  if (busy) return;
  const item = todoList.querySelector(`[data-todo-id="${todo.id}"]`);
  const titleElement = item.querySelector('.todo-title');
  const actions = item.querySelector('.todo-actions');
  const input = document.createElement('input');
  input.type = 'text';
  input.maxLength = 15;
  input.value = todo.title;
  input.setAttribute('aria-label', '\u30bf\u30a4\u30c8\u30eb\u3092\u7de8\u96c6');

  const saveButton = document.createElement('button');
  saveButton.type = 'button';
  saveButton.textContent = '\u4fdd\u5b58';
  saveButton.addEventListener('click', () => updateTodo(todo, todo.completed, input.value));

  const cancelButton = document.createElement('button');
  cancelButton.type = 'button';
  cancelButton.textContent = '\u30ad\u30e3\u30f3\u30bb\u30eb';
  cancelButton.addEventListener('click', renderTodos);

  titleElement.replaceWith(input);
  actions.replaceChildren(saveButton, cancelButton);
  input.focus();
}

async function deleteTodo(todo) {
  if (busy || !window.confirm(`\u300c${todo.title}\u300d\u3092\u524a\u9664\u3057\u307e\u3059\u304b\uff1f`)) return;
  setBusy(true);
  try {
    await requestJson(`/api/todos/${todo.id}`, { method: 'DELETE' });
    await loadTodos();
  } catch (error) {
    setMessage(statusMessage, `Todo\u3092\u524a\u9664\u3067\u304d\u307e\u305b\u3093: ${error.message}`, true);
  } finally {
    setBusy(false);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) {
    setMessage(formMessage, 'title is required', true);
    titleInput.focus();
    return;
  }
  if (busy) return;

  setBusy(true);
  setMessage(formMessage, '');
  try {
    await requestJson('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ title, completed: 0 }),
    });
    titleInput.value = '';
    await loadTodos();
  } catch (error) {
    setMessage(formMessage, error.message, true);
  } finally {
    setBusy(false);
  }
});

loadTodos();
