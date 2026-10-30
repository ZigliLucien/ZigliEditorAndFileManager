/* v48: ZEFM's original XSLT listing visual language, rebuilt with JSON + DOM.
   Use textContent only for filenames, notes, and directory data. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const state = {data: null, sort: "filename", filter: "", page: 0, pageSize: 25};
  const collator = new Intl.Collator(undefined, {numeric: true, sensitivity: "base"});
  const hasEditor = document.body.dataset.editor === "true";

  function make(tag, className, value) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined) element.textContent = String(value);
    return element;
  }

  function pathUrl(route, path, more = {}) {
    const query = new URLSearchParams({path, ...more});
    return route + "?" + query.toString();
  }

  function navigate(path, recordHistory = true) {
    const nextUrl = pathUrl("/listing", path);
    if (recordHistory) history.pushState({path}, "", nextUrl);
    refresh(path);
  }

  function renderBreadcrumbs(data) {
    const area = $("breadcrumbs");
    area.replaceChildren();
    const crumbs = data.breadcrumbs || [];
    for (let i = 0; i < crumbs.length; i++) {
      if (i) area.append(make("span", "separator", "/"));
      const item = crumbs[i];
      const a = make("a", "", item.name);
      a.href = pathUrl("/listing", item.path);
      a.addEventListener("click", (event) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        navigate(item.path);
      });
      area.append(a);
    }
    $("directory-title").textContent = data.directory;
    document.title = data.directory + " · ZEFM Listing";
  }

  function renderDirectories(data) {
    const body = $("directory-grid").querySelector("tbody");
    body.replaceChildren();
    const folders = [...data.folders].sort((a, b) => collator.compare(a.name, b.name));
    if (!folders.length) {
      const row = make("tr");
      const cell = make("td", "empty-folder", "No subdirectories");
      cell.colSpan = 4;
      row.append(cell);
      body.append(row);
    } else {
      for (let i = 0; i < folders.length; i += 4) {
        const row = make("tr");
        for (let j = 0; j < 4; j++) {
          const k = i + j;
          const cell = make("td", (k % 2 === 0 ? "x" : "y"));
          if (k < folders.length) {
            const folder = folders[k];
            const a = make("a", "", folder.name);
            a.href = pathUrl("/listing", folder.path);
            a.addEventListener("click", (event) => {
              if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
              event.preventDefault();
              navigate(folder.path);
            });
            cell.append(a);
          } else {
            cell.append(make("span", "empty-cell", " "));
          }
          row.append(cell);
        }
        body.append(row);
      }
    }
    $("folder-parent").value = data.relative;
  }

  function chosenMode() {
    const selected = document.querySelector('input[name="fileops"]:checked');
    return selected ? selected.value : "view";
  }

  function activateFile(row) {
    const path = row.path;
    switch (chosenMode()) {
      case "copy":
        location.href = pathUrl("/copy", path);
        return;
      case "notes":
        location.href = pathUrl("/notes", path);
        return;
      case "quick":
        location.href = pathUrl("/edit", path);
        return;
      case "edit":
        if (hasEditor) {
          $("open-desktop-path").value = path;
          $("open-desktop-form").submit();
        } else {
          location.href = pathUrl("/edit", path);
        }
        return;
      case "view":
        location.href = pathUrl("/view", path);
        return;
      default:
        return; // Move and delete are intentionally not ported.
    }
  }

  function orderedFiles() {
    if (!state.data) return [];
    const search = state.filter.toLocaleLowerCase();
    const rows = state.data.files.filter((row) =>
      row.name.toLocaleLowerCase().includes(search));
    rows.sort((a, b) => {
      switch (state.sort) {
        case "filetype":
          return collator.compare(a.type, b.type) || collator.compare(a.name, b.name);
        case "size":
          return b.size - a.size || collator.compare(a.name, b.name);
        case "timekey":
          return b.modified - a.modified || collator.compare(a.name, b.name);
        case "notes":
          return collator.compare(a.note, b.note) || collator.compare(a.name, b.name);
        default:
          return collator.compare(a.name, b.name);
      }
    });
    return rows;
  }

  function renderFiles() {
    const body = $("file-list").querySelector("tbody");
    body.replaceChildren();
    const rows = orderedFiles();
    const count = Math.max(1, Math.ceil(rows.length / state.pageSize));
    state.page = Math.max(0, Math.min(state.page, count - 1));
    const start = state.page * state.pageSize;
    const current = rows.slice(start, start + state.pageSize);

    for (let i = 0; i < current.length; i++) {
      const item = current[i];
      const tr = make("tr", ((start + i) % 2 === 0 ? "a" : "b"));
      const first = make("td");
      const button = make("button", "filename-button", item.name);
      button.type = "button";
      button.title = "Apply selected file operation to " + item.name;
      button.addEventListener("click", () => activateFile(item));
      first.append(button);

      const metadata = make("td", "filemeta");
      metadata.append(make("span", "size", Number(item.size).toLocaleString()));
      metadata.append(make("span", "date", item.date));
      metadata.append(make("span", "clock", item.time));

      const notes = make("td", "note");
      if (item.note_count) {
        const a = make("a", "", item.note || "Notes");
        a.href = pathUrl("/notes", item.path);
        a.title = item.note_count + " annotation(s)";
        notes.append(a);
      } else {
        notes.append(make("span", "none", "—"));
      }
      tr.append(first, metadata, notes);
      body.append(tr);
    }
    if (!current.length) {
      const tr = make("tr");
      const cell = make("td", "empty-folder", "No matching files");
      cell.colSpan = 3;
      tr.append(cell);
      body.append(tr);
    }

    const pages = $("pages");
    pages.replaceChildren();
    if (count > 1) {
      for (let index = 0; index < count; index++) {
        const b = make("button", "", String(index + 1));
        b.type = "button";
        if (index === state.page) b.setAttribute("aria-current", "page");
        b.addEventListener("click", () => {
          state.page = index;
          renderFiles();
          $("file-list").scrollIntoView({block: "start"});
        });
        pages.append(b);
      }
    }
    $("listing-info").textContent =
      rows.length + " files · " + state.data.folders.length + " directories" +
      (rows.length > 0 ? " · showing " + (start + 1) + "–" +
        (start + current.length) : "") +
      (state.filter ? " · filtered" : "");
    $("sort-summary").textContent = state.sort +
      (state.sort === "timekey" || state.sort === "size" ? " (descending)" : "");
  }

  function updateClock() {
    const now = new Date();
    const date = now.toLocaleDateString(undefined,
      {month: "long", day: "numeric"});
    const time = now.toLocaleTimeString(undefined, {hour12: false});
    $("time").textContent = date + " · " + time;
  }

  async function refresh(path) {
    $("listing-info").textContent = "Loading directory…";
    try {
      const result = await fetch(pathUrl("/api/files", path),
        {cache: "no-store", credentials: "same-origin"});
      if (!result.ok) {
        throw new Error("Could not load directory (HTTP " + result.status + ")");
      }
      state.data = await result.json();
      state.page = 0;
      renderBreadcrumbs(state.data);
      renderDirectories(state.data);
      renderFiles();
    } catch (error) {
      $("listing-info").textContent = String(error.message || error);
      $("listing-info").classList.add("error");
    }
  }

  function focusFilename(delta) {
    const nodes = [...document.querySelectorAll(".filename-button")];
    if (!nodes.length) return;
    const activeIndex = nodes.indexOf(document.activeElement);
    const next = activeIndex === -1 ? (delta > 0 ? 0 : nodes.length - 1)
                                   : (activeIndex + delta + nodes.length) % nodes.length;
    nodes[next].focus();
  }

  function setupKeyboard() {
    const modes = {v: "view", c: "copy", e: "edit", q: "quick", n: "notes"};
    document.addEventListener("keydown", (event) => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      const focused = document.activeElement;
      if (focused && (focused.tagName === "INPUT" ||
          focused.tagName === "TEXTAREA" || focused.tagName === "SELECT")) return;
      if (event.key === "ArrowDown") {
        event.preventDefault(); focusFilename(1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault(); focusFilename(-1);
      } else if (event.key.toLowerCase() === "u" && state.data && state.data.parent) {
        event.preventDefault(); navigate(state.data.parent);
      } else if (event.key.toLowerCase() === "f" || event.key === "/") {
        event.preventDefault(); $("filter").focus();
      } else if (event.key.toLowerCase() === "r" && state.data) {
        event.preventDefault(); refresh(state.data.relative);
      } else if (modes[event.key.toLowerCase()]) {
        event.preventDefault();
        const op = document.querySelector(
          'input[name="fileops"][value="' + modes[event.key.toLowerCase()] + '"]');
        if (op) op.checked = true;
      }
    });
  }

  $("sort-key").addEventListener("change", (event) => {
    state.sort = event.target.value;
    state.page = 0;
    renderFiles();
  });
  $("filter").addEventListener("input", (event) => {
    state.filter = event.target.value;
    state.page = 0;
    renderFiles();
  });
  $("find-file").addEventListener("click", () => $("filter").focus());
  $("refresh").addEventListener("click", () =>
    refresh(state.data ? state.data.relative : "."));
  window.addEventListener("popstate", () => {
    const query = new URLSearchParams(location.search);
    refresh(query.get("path") || ".");
  });

  setupKeyboard();
  updateClock();
  setInterval(updateClock, 1000);
  const query = new URLSearchParams(location.search);
  refresh(query.get("path") || ".");
})();
