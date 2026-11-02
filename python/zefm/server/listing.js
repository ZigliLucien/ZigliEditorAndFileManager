/* v48: ZEFM's original XSLT listing visual language, rebuilt with JSON + DOM.
   Use textContent only for filenames, notes, and directory data. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  // GoFM.java used page 0 for the top listing and HEADER1..N for file pages.
  // In this single-page UI, page 1 starts at index 0; Top scrolls to the
  // directory overview and Bottom selects the final file page.
  const state = {data: null, sort: "filename", filter: "", page: 0, pageSize: 25,
                 directory: ".", requestSerial: 0};
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

  function listingUrl(path, page = 1) {
    const args = {path, page: String(page)};
    if (state.sort !== "filename") args.sort = state.sort;
    if (state.filter) args.filter = state.filter;
    return "/listing?" + new URLSearchParams(args);
  }

  function navigate(path, recordHistory = true) {
    if (filterTimer !== null) {
      clearTimeout(filterTimer);
      filterTimer = null;
    }
    // A directory change starts at page 1 without silently inheriting
    // the prior directory's filename filter or changing its sort order.
    state.filter = "";
    $("filter").value = "";
    if (recordHistory) history.pushState({path, page: 1}, "", listingUrl(path));
    refresh(path, 1);
  }

  function navigateParent() {
    if (!state.data || !state.data.parent) return;
    navigate(state.data.parent);
  }

  function selectPage(index, recordHistory = true, scrollToFiles = true) {
    if (!state.data) return;
    const count = state.data.page_count;
    const page = Math.max(1, Math.min(index + 1, count));
    if (recordHistory) {
      history.pushState({path: state.directory, page}, "",
                        listingUrl(state.directory, page));
    }
    refresh(state.directory, page, scrollToFiles);
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
    $("folder-up").disabled = data.parent === null;
    $("folder-home").disabled = data.relative === ".";
    $("basic-listing").href = pathUrl("/browse", data.relative);
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

  function operationUrl(route, path, extra = {}) {
    return pathUrl(route, path, { ...extra,
      back: listingUrl(state.directory, state.page + 1) });
  }

  function activateFile(row, mode = "view") {
    const path = row.path;
    switch (mode) {
      case "copy": location.href = operationUrl("/copy", path); return;
      case "rename": location.href = operationUrl("/rename", path); return;
      case "move": location.href = operationUrl("/move", path); return;
      case "notes": location.href = operationUrl("/notes", path); return;
      case "quick": location.href = operationUrl("/edit", path); return;
      case "build":
        window.open(operationUrl("/build", path), "_blank", "noopener");
        return;
      case "edit":
        if (hasEditor) {
          $("open-desktop-path").value = path;
          $("open-desktop-back").value = listingUrl(state.directory, state.page + 1);
          $("open-desktop-form").submit();
        } else {
          location.href = operationUrl("/edit", path);
        }
        return;
      case "view":
        if (["pdf", "ps", "eps", "html", "htm", "md", "markdown", "epub", "djvu", "djv", "jpg", "jpeg", "png", "gif", "webp", "bmp", "avif", "zip", "jar", "war", "ear", "tar", "tgz", "tbz", "tbz2", "txz"].includes(row.type)) {
          const route = row.type === "pdf" ? "/pdf" : "/view";
          window.open(operationUrl(route, path), "_blank", "noopener");
        } else {
          location.href = operationUrl("/view", path);
        }
        return;
    }
  }

  // Right click reintroduces the original ZEFM operation workflow;
  // left click always opens the file's normal browser representation.
  const contextMenu = make("div", "zefm-context-menu");
  contextMenu.id = "zefm-context-menu";
  contextMenu.setAttribute("role", "menu");
  contextMenu.hidden = true;
  document.body.append(contextMenu);
  let menuReturnFocus = null;

  function dismissMenu(restoreFocus = false) {
    if (contextMenu.hidden) return;
    contextMenu.hidden = true;
    contextMenu.replaceChildren();
    if (restoreFocus && menuReturnFocus) menuReturnFocus.focus();
    menuReturnFocus = null;
  }

  function showFileMenu(event, row, source) {
    event.preventDefault();
    dismissMenu();
    menuReturnFocus = source;
    const options = [
      ["View", "view"], ["Copy", "copy"], ["Rename", "rename"], ["Move", "move"],
      ["Edit", "edit"], ["Quick Edit", "quick"], ["Notes", "notes"]
    ];
    if (["md", "markdown", "tex"].includes(row.type)) {
      options.push(["Compile PDF", "build"]);
    }
    for (const [name, mode] of options) {
      const item = make("button", "zefm-context-action", name);
      item.type = "button";
      item.setAttribute("role", "menuitem");
      item.addEventListener("click", () => {
        dismissMenu();
        activateFile(row, mode);
      });
      contextMenu.append(item);
    }
    contextMenu.hidden = false;
    const x = event.clientX || source.getBoundingClientRect().left;
    const y = event.clientY || source.getBoundingClientRect().bottom;
    contextMenu.style.left = Math.max(0, Math.min(x, window.innerWidth - 190)) + "px";
    contextMenu.style.top = Math.max(0, Math.min(y, window.innerHeight - 260)) + "px";
    contextMenu.querySelector("button").focus();
  }
  document.addEventListener("click", (event) => {
    if (!contextMenu.hidden && !contextMenu.contains(event.target)) dismissMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") dismissMenu(true);
  });
  window.addEventListener("blur", () => dismissMenu());

  function renderFiles() {
    if (!state.data) return;
    const body = $("file-list").querySelector("tbody");
    body.replaceChildren();
    const rows = state.data.files;
    const count = state.data.page_count;
    state.page = state.data.page - 1;
    const start = state.data.page_start - 1;
    const current = rows;

    for (let i = 0; i < current.length; i++) {
      const item = current[i];
      const tr = make("tr", ((start + i) % 2 === 0 ? "a" : "b"));
      const first = make("td");
      const button = make("button", "filename-button", item.name);
      button.type = "button";
      button.title = "Left click to view; right click for file operations: " + item.name;
      button.addEventListener("click", () => activateFile(item, "view"));
      button.addEventListener("contextmenu", (event) => showFileMenu(event, item, button));
      button.addEventListener("keydown", (event) => {
        if (event.key === "F10" && event.shiftKey) showFileMenu(event, item, button);
      });
      first.append(button);

      const metadata = make("td", "filemeta");
      metadata.append(make("span", "size", Number(item.size).toLocaleString()));
      metadata.append(make("span", "date", item.date));
      metadata.append(make("span", "clock", item.time));

      const notes = make("td", "note");
      if (item.note_count) {
        const a = make("a", "", item.note || "Notes");
        a.href = operationUrl("/notes", item.path);
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

    renderGoFMPages(state.data.references, count);
    $("listing-info").textContent =
      state.data.total_files + " files · " + state.data.folders.length + " directories" +
      (rows.length > 0 ? " · showing " + state.data.page_start + "–" +
        state.data.page_end : "") +
      (state.filter ? " · filtered" : "");
    $("sort-summary").textContent = state.sort +
      (state.sort === "timekey" || state.sort === "size" ? " (descending)" : "");
  }

  function renderGoFMPages(references, count) {
    // Xlster.reffout() progressively exposed GoFM page references through
    // current+1 and arranged references in rows of about ten.
    const pages = $("pages");
    pages.replaceChildren();
    const nav = make("div", "gofm-navigation");
    function navButton(label, page, disabled = false, scroll = true) {
      const b = make("button", "gofm-nav", label);
      b.type = "button";
      b.disabled = disabled;
      b.addEventListener("click", () => {
        if (label === "Top") {
          window.scrollTo({top: 0, behavior: "smooth"});
          if (state.page === 0) return;
        }
        selectPage(page, true, scroll);
      });
      nav.append(b);
      return b;
    }
    navButton("Top", 0, false, false);
    navButton("Previous", state.page - 1, state.page === 0);
    nav.append(make("span", "gofm-current",
      "Listing " + (state.page + 1) + " of " + count));
    navButton("Next", state.page + 1, state.page >= count - 1);
    navButton("Bottom", count - 1, count === 1 || state.page === count - 1);
    pages.append(nav);
    if (count <= 1) return;

    const refs = make("div", "gofm-references");
    // As in GoFM, reveal page references through the next page; never render
    // a sprawling list of all 120 possible refs for a huge directory at once.
    const shown = Math.min(count, state.page + 2);
    for (let i = 0; i < shown; i++) {
      const descriptor = references[i].label;
      const b = make("button", "gofm-reference", descriptor);
      b.type = "button";
      b.title = "Listing " + (i + 1);
      b.setAttribute("aria-label", "Listing " + (i + 1) + ": " + descriptor);
      if (i === state.page) b.setAttribute("aria-current", "page");
      b.addEventListener("click", () => selectPage(i));
      refs.append(b);
    }
    pages.append(refs);
  }

  function updateClock() {
    const now = new Date();
    const date = now.toLocaleDateString(undefined,
      {month: "long", day: "numeric"});
    const time = now.toLocaleTimeString(undefined, {hour12: false});
    $("time").textContent = date + " · " + time;
  }

  async function refresh(path, requestedPage = 1, scrollToFiles = false) {
    const serial = ++state.requestSerial;
    $("listing-info").textContent = "Loading directory…";
    try {
      const result = await fetch(pathUrl("/api/listing-page", path, {
        page: String(requestedPage), sort: state.sort, filter: state.filter
      }), {cache: "no-store", credentials: "same-origin"});
      if (!result.ok) {
        throw new Error("Could not load directory (HTTP " + result.status + ")");
      }
      const data = await result.json();
      if (serial !== state.requestSerial) return;
      state.data = data;
      state.directory = data.relative;
      $("listing-info").classList.remove("error");
      state.page = data.page - 1;
      // Page counts can shrink after deletion/moves or filter changes.
      // Keep the URL consistent with the page the server actually returned.
      const actual = listingUrl(data.relative, data.page);
      if (location.pathname === "/listing" &&
          new URLSearchParams(location.search).get("page") !== String(data.page)) {
        history.replaceState({path: data.relative, page: data.page}, "", actual);
      }
      renderBreadcrumbs(state.data);
      renderDirectories(state.data);
      renderFiles();
      if (scrollToFiles) $("file-list").scrollIntoView({block: "start"});
    } catch (error) {
      if (serial !== state.requestSerial) return;
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
    const modes = {v: "view", c: "copy", e: "edit", q: "quick", n: "notes", m: "move"};
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
    selectPage(0);
  });
  let filterTimer = null;
  $("filter").addEventListener("input", (event) => {
    state.filter = event.target.value.slice(0, 200);
    if (filterTimer !== null) clearTimeout(filterTimer);
    filterTimer = setTimeout(() => {
      filterTimer = null;
      if (!state.data) return;
      // Typing a search should not create dozens of Back history entries.
      history.replaceState({path: state.directory, page: 1}, "",
                           listingUrl(state.directory, 1));
      refresh(state.directory, 1);
    }, 160);
  });
  $("find-file").addEventListener("click", () => $("filter").focus());
  $("folder-up").addEventListener("click", navigateParent);
  $("folder-home").addEventListener("click", () => navigate("."));
  $("refresh").addEventListener("click", () =>
    refresh(state.data ? state.data.relative : ".", state.page + 1));
  function pageFromUrl(query) {
    const raw = query.get("page") || "1";
    if (!/^[1-9][0-9]*$/.test(raw)) return 1;
    const number = Number(raw);
    return Number.isSafeInteger(number) ? number : 1;
  }
  window.addEventListener("popstate", () => {
    const query = new URLSearchParams(location.search);
    state.sort = ["filename", "filetype", "timekey", "size", "notes"].includes(query.get("sort"))
      ? query.get("sort") : "filename";
    state.filter = (query.get("filter") || "").slice(0, 200);
    $("sort-key").value = state.sort;
    $("filter").value = state.filter;
    refresh(query.get("path") || ".", pageFromUrl(query));
  });

  setupKeyboard();
  updateClock();
  setInterval(updateClock, 1000);
  const query = new URLSearchParams(location.search);
  state.sort = ["filename", "filetype", "timekey", "size", "notes"].includes(query.get("sort"))
    ? query.get("sort") : "filename";
  state.filter = (query.get("filter") || "").slice(0, 200);
  $("sort-key").value = state.sort;
  $("filter").value = state.filter;
  refresh(query.get("path") || ".", pageFromUrl(query));
})();
