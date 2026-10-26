// TODO アプリ フロントエンド
// バグ修正・機能追加はこのファイルとサーバ側 (server.py) の両方に手を入れることになります。

const API = "/api/todos";

const els = {
  list: document.getElementById("todoList"),
  count: document.getElementById("count"),
  searchInput: document.getElementById("searchInput"),
  searchBtn: document.getElementById("searchBtn"),
  resetBtn: document.getElementById("resetBtn"),
  addForm: document.getElementById("addForm"),
  newTitle: document.getElementById("newTitle"),
  newDescription: document.getElementById("newDescription"),
  editDialog: document.getElementById("editDialog"),
  editId: document.getElementById("editId"),
  editTitle: document.getElementById("editTitle"),
  editDescription: document.getElementById("editDescription"),
  editCompleted: document.getElementById("editCompleted"),
  editSave: document.getElementById("editSave"),
  editCancel: document.getElementById("editCancel"),
};

async function fetchTodos(query = "") {
  const url = query ? `${API}?q=${encodeURIComponent(query)}` : API;
  const res = await fetch(url);
  if (!res.ok) throw new Error("一覧取得に失敗しました");
  return res.json();
}

async function createTodo(title, description) {
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "作成に失敗しました");
  }
  return res.json();
}

async function updateTodo(id, patch) {
  const res = await fetch(`${API}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "更新に失敗しました");
  }
  return res.json();
}

async function deleteTodo(id) {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "削除に失敗しました");
  }
  return res.json();
}

function render(todos) {
  els.count.textContent = todos.length;
  els.list.innerHTML = "";

  if (todos.length === 0) {
    const li = document.createElement("li");
    li.className = "empty-state";
    li.textContent = "TODO はまだありません";
    els.list.appendChild(li);
    return;
  }

  for (const todo of todos) {
    const li = document.createElement("li");
    li.className = "todo-item" + (todo.completed ? " completed" : "");
    li.dataset.id = todo.id;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = !!todo.completed;
    checkbox.addEventListener("change", async () => {
      try {
        await updateTodo(todo.id, { completed: checkbox.checked });
        await refresh();
      } catch (e) {
        alert(e.message);
      }
    });

    const content = document.createElement("div");
    content.className = "todo-content";
    const title = document.createElement("div");
    title.className = "todo-title";
    title.textContent = todo.title;
    const desc = document.createElement("div");
    desc.className = "todo-desc";
    desc.textContent = todo.description || "";
    const meta = document.createElement("div");
    meta.className = "todo-meta";
    meta.textContent = `更新: ${todo.updated_at}`;
    content.append(title, desc, meta);

    const actions = document.createElement("div");
    actions.className = "todo-actions";
    const editBtn = document.createElement("button");
    editBtn.textContent = "編集";
    editBtn.className = "secondary";
    editBtn.addEventListener("click", () => openEditDialog(todo));
    const delBtn = document.createElement("button");
    delBtn.textContent = "削除";
    delBtn.className = "danger";
    delBtn.addEventListener("click", async () => {
      if (!confirm(`"${todo.title}" を削除しますか?`)) return;
      try {
        await deleteTodo(todo.id);
        await refresh();
      } catch (e) {
        alert(e.message);
      }
    });
    actions.append(editBtn, delBtn);

    li.append(checkbox, content, actions);
    els.list.appendChild(li);
  }
}

async function refresh() {
  const q = els.searchInput.value.trim();
  try {
    const todos = await fetchTodos(q);
    render(todos);
  } catch (e) {
    alert(e.message);
  }
}

function openEditDialog(todo) {
  els.editId.value = todo.id;
  els.editTitle.value = todo.title;
  els.editDescription.value = todo.description || "";
  els.editCompleted.checked = !!todo.completed;
  els.editDialog.showModal();
}

els.searchBtn.addEventListener("click", refresh);
els.searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") refresh();
});
els.resetBtn.addEventListener("click", () => {
  els.searchInput.value = "";
  refresh();
});

els.addForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = els.newTitle.value.trim();
  const description = els.newDescription.value.trim();
  if (!title) return;
  try {
    await createTodo(title, description);
    els.newTitle.value = "";
    els.newDescription.value = "";
    await refresh();
  } catch (err) {
    alert(err.message);
  }
});

els.editSave.addEventListener("click", async () => {
  const id = Number(els.editId.value);
  try {
    await updateTodo(id, {
      title: els.editTitle.value,
      description: els.editDescription.value,
      completed: els.editCompleted.checked,
    });
    els.editDialog.close();
    await refresh();
  } catch (e) {
    alert(e.message);
  }
});

els.editCancel.addEventListener("click", () => {
  els.editDialog.close();
});

refresh();
