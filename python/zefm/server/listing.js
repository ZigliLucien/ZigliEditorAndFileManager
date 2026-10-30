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
    if (recordHistory) history.pushState({path, page: 1}, "", listingUrl(path));
    refresh(path, 1);
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
        location.href = pathUrl(row.type === "pdf" ? "/pdf" : "/view", path);
        return;
      default:
        return; // Move and delete are intentionally not ported.
    }
  }

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
      b.addEventListener("click", () => selectPage(page, true, scroll));
      nav.append(b);
      return b;
    }
    navButton("Top", 0, false, false).addEventListener("click", () => {
      window.scrollTo({top: 0, behavior: "smooth"});
    });
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
    selectPage(0);
  });
  $("filter").addEventListener("input", (event) => {
    state.filter = event.target.value;
    selectPage(0);
  });
  $("find-file").addEventListener("click", () => $("filter").focus());
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
