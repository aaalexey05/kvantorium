(function(){
  const root = document.documentElement;
  const storageKey = "kv-theme";
  const motionKey = "kv-motion";
  const toggle = document.getElementById('theme-toggle');
  const setTheme = (mode) => {
    root.setAttribute("data-theme", mode);
    localStorage.setItem(storageKey, mode);
  };
  const applyMotion = () => {
    const motion = localStorage.getItem(motionKey);
    root.classList.toggle("animations-off", motion === "off");
  };
  const saved = localStorage.getItem(storageKey);
  if(saved){
    setTheme(saved);
  } else {
    const prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
    root.setAttribute("data-theme", prefersLight ? "light" : "dark");
  }
  applyMotion();
  if(toggle){
    toggle.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      setTheme(current);
    });
  }

  const insertSnippet = (target, before, after) => {
    if (!target) return;
    const start = typeof target.selectionStart === "number" ? target.selectionStart : target.value.length;
    const end = typeof target.selectionEnd === "number" ? target.selectionEnd : start;
    const value = target.value || "";
    target.value = value.slice(0, start) + before + after + value.slice(end);
    const cursor = start + before.length;
    target.focus();
    if (typeof target.setSelectionRange === "function") {
      target.setSelectionRange(cursor, cursor);
    }
    target.dispatchEvent(new Event("input", { bubbles: true }));
  };

  document.addEventListener("click", (event) => {
    const btn = event.target.closest(".js-insert-snippet");
    if (!btn) return;
    const selector = btn.getAttribute("data-target");
    const target = selector ? document.querySelector(selector) : null;
    if (!target) return;
    insertSnippet(target, btn.getAttribute("data-before") || "", btn.getAttribute("data-after") || "");
  });

  const syncRichEditor = (editor) => {
    const form = editor.closest("form");
    if (!form) return;
    const output = form.querySelector(".js-rich-editor-output");
    if (!output) return;
    output.value = editor.innerHTML.trim();
  };

  const insertTableHtml = (rows, cols) => {
    const safeRows = Math.max(1, Math.min(rows || 2, 10));
    const safeCols = Math.max(1, Math.min(cols || 2, 10));
    const body = Array.from({ length: safeRows })
      .map(() => `<tr>${Array.from({ length: safeCols }).map(() => "<td>Ячейка</td>").join("")}</tr>`)
      .join("");
    return `<table class="rt-table"><tbody>${body}</tbody></table><p></p>`;
  };

  const runRichAction = (editor, action) => {
    if (action === "insertTable") {
      const rows = Number(window.prompt("Сколько строк?", "2"));
      const cols = Number(window.prompt("Сколько столбцов?", "2"));
      if (!rows || !cols) return;
      document.execCommand("insertHTML", false, insertTableHtml(rows, cols));
      return;
    }
    if (action === "insertImageUrl") {
      const imageUrl = window.prompt("Введите URL изображения", "https://");
      if (!imageUrl) return;
      const html = `<figure><img src="${imageUrl}" alt="" /><figcaption>Подпись</figcaption></figure><p></p>`;
      document.execCommand("insertHTML", false, html);
      return;
    }
    if (action === "insertHr") {
      document.execCommand("insertHorizontalRule", false, null);
      return;
    }
  };

  const runRichCommand = (editor, cmd, value) => {
    if (!cmd) return;
    if (cmd === "createLink") {
      const linkValue = window.prompt("Введите URL ссылки", "https://");
      if (!linkValue) return;
      document.execCommand(cmd, false, linkValue);
      return;
    }
    document.execCommand(cmd, false, value || null);
  };

  document.addEventListener("input", (event) => {
    const editor = event.target.closest(".js-rich-editor");
    if (!editor) return;
    syncRichEditor(editor);
  });

  document.addEventListener("click", (event) => {
    const button = event.target.closest(".rich-btn");
    if (!button) return;
    const form = button.closest("form");
    if (!form) return;
    const editor = form.querySelector(".js-rich-editor");
    if (!editor) return;

    event.preventDefault();
    editor.focus();

    const action = button.getAttribute("data-action");
    const cmd = button.getAttribute("data-cmd");
    const value = button.getAttribute("data-value") || null;
    if (action) {
      runRichAction(editor, action);
    } else {
      runRichCommand(editor, cmd, value);
    }
    syncRichEditor(editor);
  });

  document.addEventListener("input", (event) => {
    const picker = event.target.closest(".rich-color-picker");
    if (!picker) return;
    const form = picker.closest("form");
    if (!form) return;
    const editor = form.querySelector(".js-rich-editor");
    if (!editor) return;
    editor.focus();
    document.execCommand("foreColor", false, picker.value);
    syncRichEditor(editor);
  });

  document.addEventListener("keydown", (event) => {
    const editor = event.target.closest(".js-rich-editor");
    if (!editor) return;
    const mod = event.ctrlKey || event.metaKey;
    if (!mod) return;

    const key = event.key.toLowerCase();
    if (key === "b") {
      event.preventDefault();
      runRichCommand(editor, "bold");
    } else if (key === "i") {
      event.preventDefault();
      runRichCommand(editor, "italic");
    } else if (key === "u") {
      event.preventDefault();
      runRichCommand(editor, "underline");
    } else if (key === "k") {
      event.preventDefault();
      runRichCommand(editor, "createLink");
    } else if (event.shiftKey && key === "7") {
      event.preventDefault();
      runRichCommand(editor, "insertOrderedList");
    } else if (event.shiftKey && key === "8") {
      event.preventDefault();
      runRichCommand(editor, "insertUnorderedList");
    } else if (event.shiftKey && key === "t") {
      event.preventDefault();
      runRichAction(editor, "insertTable");
    } else if (event.shiftKey && key === "m") {
      event.preventDefault();
      runRichAction(editor, "insertImageUrl");
    } else if (event.shiftKey && key === "l") {
      event.preventDefault();
      runRichCommand(editor, "justifyLeft");
    } else if (event.shiftKey && key === "e") {
      event.preventDefault();
      runRichCommand(editor, "justifyCenter");
    } else if (event.shiftKey && key === "r") {
      event.preventDefault();
      runRichCommand(editor, "justifyRight");
    }
    syncRichEditor(editor);
  });

  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    form.querySelectorAll(".js-rich-editor").forEach((editor) => {
      syncRichEditor(editor);
    });
  });

  const getCsrfToken = () => {
    const el = document.querySelector("input[name='csrfmiddlewaretoken']");
    return el ? el.value : "";
  };

  const initAutosave = () => {
    const form = document.querySelector(".js-course-autosave");
    if (!form) return;
    const url = form.getAttribute("data-autosave-url");
    const statusEl = form.querySelector(".js-autosave-status");
    if (!url) return;

    let lastSnapshot = "";
    let saving = false;

    const snapshot = () => {
      const fd = new FormData(form);
      fd.delete("csrfmiddlewaretoken");
      return Array.from(fd.entries())
        .map(([k, v]) => `${k}:${v}`)
        .join("|");
    };

    const saveDraft = async () => {
      if (saving) return;
      const currentSnapshot = snapshot();
      if (currentSnapshot === lastSnapshot) return;
      saving = true;
      if (statusEl) statusEl.textContent = "Сохранение...";
      try {
        const body = new FormData(form);
        const res = await fetch(url, {
          method: "POST",
          headers: { "X-CSRFToken": getCsrfToken() },
          body,
        });
        if (!res.ok) {
          if (statusEl) statusEl.textContent = "Ошибка автосохранения";
          return;
        }
        const data = await res.json();
        lastSnapshot = currentSnapshot;
        if (statusEl) statusEl.textContent = `Сохранено в ${data.saved_at}`;
      } catch (e) {
        if (statusEl) statusEl.textContent = "Ошибка автосохранения";
      } finally {
        saving = false;
      }
    };

    lastSnapshot = snapshot();
    window.setInterval(saveDraft, 15000);
  };

  const initBlockDnD = () => {
    const lists = document.querySelectorAll(".js-block-list");
    if (!lists.length) return;

    const sendOrder = async (list) => {
      const url = list.getAttribute("data-reorder-url");
      if (!url) return;
      const ids = Array.from(list.querySelectorAll(".js-draggable-block")).map((el) => el.getAttribute("data-block-id"));
      const body = new URLSearchParams();
      body.set("block_ids", ids.join(","));
      try {
        await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCsrfToken(),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
          },
          body: body.toString(),
        });
      } catch (e) {
        // ignore transient network errors in UI
      }
    };

    lists.forEach((list) => {
      let dragged = null;

      list.addEventListener("dragstart", (event) => {
        const item = event.target.closest(".js-draggable-block");
        if (!item) return;
        dragged = item;
        item.classList.add("is-dragging");
      });

      list.addEventListener("dragend", () => {
        if (dragged) dragged.classList.remove("is-dragging");
        dragged = null;
      });

      list.addEventListener("dragover", (event) => {
        event.preventDefault();
        if (!dragged) return;
        const siblings = Array.from(list.querySelectorAll(".js-draggable-block:not(.is-dragging)"));
        const next = siblings.find((sibling) => {
          const box = sibling.getBoundingClientRect();
          return event.clientY <= box.top + box.height / 2;
        });
        if (next) {
          list.insertBefore(dragged, next);
        } else {
          list.appendChild(dragged);
        }
      });

      list.addEventListener("drop", () => {
        if (!dragged) return;
        sendOrder(list);
      });
    });
  };

  initAutosave();
  initBlockDnD();

  document.addEventListener("click", (event) => {
    const previewLink = event.target.closest(".lesson-preview-link");
    if (!previewLink) return;
    event.stopPropagation();
  });
})();
