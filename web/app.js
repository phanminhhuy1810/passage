"use strict";

const METHODS = {
  semantic: {name:"Semantic", scoreLabel:"cosine"},
  tfidf: {name:"TF-IDF", scoreLabel:"cosine"},
  overlap: {name:"Token overlap", scoreLabel:"shared tokens"},
};
const $ = id => document.getElementById(id);
let serviceReady = false;
let searching = false;
let activeMethod = "semantic";
let compare = false;
let lastResult = null;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function showError(message) {
  $("error-banner").textContent = message;
  $("error-banner").hidden = false;
}
function clearError() { $("error-banner").hidden = true; }
function setLoading(active) {
  searching = active;
  $("search-button").disabled = active || !serviceReady;
  $("search-button").textContent = active ? "Searching…" : "Search";
  $("query").disabled = active;
  $("top-k").disabled = active;
  $("results-section").setAttribute("aria-busy", String(active));
  $("results-panel").classList.toggle("loading", active);
  document.querySelectorAll(".example-button,.method-tab,#compare-button").forEach(button => { button.disabled = active; });
}
async function readJSON(response) {
  let payload;
  try { payload = await response.json(); }
  catch { throw new Error("The server returned an unreadable response."); }
  if (!response.ok || payload.error) {
    // Keep input guidance in the same language as the interface.
    if (response.status === 422) throw new Error("Enter 1–500 characters with at least one letter or number.");
    throw new Error(payload.error || `Request failed (HTTP ${response.status}).`);
  }
  return payload;
}
function highlightedText(parent, text, query, enabled) {
  if (!enabled) { parent.textContent = text; return; }
  const normalized = text.normalize("NFC");
  const terms = new Set(query.normalize("NFC").toLocaleLowerCase("vi").match(/[\p{L}\p{N}]+/gu) || []);
  let cursor = 0;
  for (const match of normalized.matchAll(/[\p{L}\p{N}]+/gu)) {
    parent.append(document.createTextNode(normalized.slice(cursor, match.index)));
    parent.append(terms.has(match[0].toLocaleLowerCase("vi")) ? element("mark", "", match[0]) : document.createTextNode(match[0]));
    cursor = match.index + match[0].length;
  }
  parent.append(document.createTextNode(normalized.slice(cursor)));
}
function resultItem(hit, index, method, query) {
  const item = element("li", "result");
  item.append(element("span", "rank", String(index + 1)));
  const body = element("div", "result-body");
  const heading = element("div", "result-heading");
  const doc = hit.document;
  heading.append(element("h3", "", (doc.title || "Untitled passage").replaceAll("_", " ")));
  const score = Number.isFinite(hit.score) ? (method === "overlap" ? hit.score.toFixed(0) : hit.score.toFixed(3)) : "—";
  heading.append(element("span", "score", `${score} ${METHODS[method].scoreLabel}`));
  body.append(heading);
  const id = String(doc.id);
  const source = element("div", "source", `XQuAD / Vietnamese / ${id.slice(0, 10)}`);
  source.title = `Passage ID: ${id}`;
  body.append(source);
  const preview = element("p", "passage-preview");
  highlightedText(preview, doc.text, query, method !== "semantic");
  body.append(preview);
  const details = element("details");
  details.append(element("summary", "", "Read passage"));
  const text = element("p", "passage-full");
  highlightedText(text, doc.text, query, method !== "semantic");
  details.append(text);
  body.append(details);
  item.append(body);
  return item;
}
function resultList(data, method, query) {
  if (!data?.hits.length) return element("p", "no-results", "No matching passages. Try another query from this collection.");
  const list = element("ol", "result-list");
  data.hits.forEach((hit, index) => list.append(resultItem(hit, index, method, query)));
  return list;
}
function renderView() {
  document.querySelectorAll(".method-tab").forEach(button => {
    const selected = !compare && button.dataset.method === activeMethod;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  $("compare-button").setAttribute("aria-pressed", String(compare));
  const panel = $("results-panel");
  panel.replaceChildren();
  if (!lastResult) {
    $("result-context").hidden = true;
    $("result-note").hidden = true;
    const empty = element("div", "initial-state");
    empty.append(element("p", "", compare ? "Search to compare the three ranked lists." : "Enter a question to find its source passage."));
    empty.append(element("span", "", "Or choose one of the examples above."));
    panel.append(empty);
    return;
  }
  $("result-context").hidden = false;
  $("result-note").hidden = false;
  $("results-title").textContent = `Results for “${lastResult.query}”`;
  const selected = lastResult.results.find(result => result.method === activeMethod);
  if (compare) {
    $("results-meta").textContent = "3 methods · same collection";
    const grid = element("div", "comparison");
    for (const method of Object.keys(METHODS)) {
      const data = lastResult.results.find(result => result.method === method);
      const column = element("div", "comparison-column");
      const header = element("div", "comparison-header");
      header.append(element("h3", "", METHODS[method].name));
      if (Number.isFinite(data?.elapsed_ms)) header.append(element("span", "", `${data.elapsed_ms.toFixed(1)} ms`));
      column.append(header, resultList(data, method, lastResult.query));
      grid.append(column);
    }
    panel.append(grid);
  } else {
    const count = selected?.hits.length || 0;
    const timing = Number.isFinite(selected?.elapsed_ms) ? ` · ${selected.elapsed_ms.toFixed(1)} ms` : "";
    $("results-meta").textContent = `${count} ${count === 1 ? "passage" : "passages"}${timing}`;
    panel.append(resultList(selected, activeMethod, lastResult.query));
  }
}
function renderBenchmark(benchmark) {
  if (!benchmark?.results?.length) return;
  const body = $("benchmark-body");
  body.replaceChildren();
  for (const result of benchmark.results) {
    if (!METHODS[result.method]) continue;
    const row = element("tr");
    const name = element("th", "", METHODS[result.method].name);
    name.scope = "row";
    row.append(name);
    for (const key of ["hit_at_1", "hit_at_5", "mrr_at_5"]) {
      const value = result[key];
      row.append(element("td", "", Number.isFinite(value) ? (key === "mrr_at_5" ? value.toFixed(3) : `${(value * 100).toFixed(1)}%`) : "—"));
    }
    body.append(row);
  }
  const split = benchmark.split === "test" ? "test" : "development";
  $("benchmark-meta").textContent = `${benchmark.query_count} ${split} questions`;
  $("benchmark-description").textContent = `Closed-corpus passage retrieval on ${benchmark.query_count} ${split} questions. All methods search the same known XQuAD Vietnamese collection.`;
  $("benchmark-section").hidden = false;
}
async function loadStatus() {
  try {
    const status = await readJSON(await fetch("/api/status", {headers:{Accept:"application/json"}}));
    serviceReady = status.ready === true;
    $("connection-status").classList.toggle("ready", serviceReady);
    $("connection-text").textContent = serviceReady ? "Local · Ready" : "Not ready";
    if (Number.isFinite(status.document_count)) $("document-count").textContent = status.document_count;
    if (status.model?.name) $("model-note").textContent = `Model: ${status.model.name} · ${status.model.device || "local"}. No fine-tuning.`;
    renderBenchmark(status.benchmark);
    const examples = $("example-buttons");
    if (status.examples?.length) {
      for (const example of status.examples.slice(0, 4)) {
        const button = element("button", "example-button", (example.title || example.text).replaceAll("_", " "));
        button.type = "button";
        button.title = example.text;
        button.addEventListener("click", () => {
          if (searching) return;
          $("query").value = example.text;
          $("search-form").requestSubmit();
        });
        examples.append(button);
      }
      $("examples").hidden = false;
    }
    $("search-button").disabled = !serviceReady;
    if (!serviceReady) showError("The model is not ready. Check the app window and reload this page.");
  } catch (error) {
    $("connection-status").classList.add("failed");
    $("connection-text").textContent = "Disconnected";
    showError(`Cannot connect to the local app. ${error.message}`);
  }
}
function showLaunchGuide() {
  document.title = "Open Passage";
  const guide = element("main", "launch-guide");
  guide.append(element("h1", "", "Open the local demo"));
  const instruction = element("p");
  instruction.append("Start Passage by opening ", element("code", "", "Open Retrieval Lab.command"),
    " in the project folder. Keep its Terminal window open, then follow the link below.");
  const link = element("a", "launch-link", "Open Passage");
  link.href = "http://127.0.0.1:8765/";
  guide.append(instruction, link);
  document.querySelector(".workspace").replaceWith(guide);
  document.querySelector(".skip-link").remove();
  $("connection-status").hidden = true;
}

function startApp() {
  if (window.location.protocol === "file:") {
    showLaunchGuide();
    return;
  }
  document.querySelectorAll(".method-tab").forEach(button => button.addEventListener("click", () => {
    activeMethod = button.dataset.method;
    compare = false;
    renderView();
  }));
  $("compare-button").addEventListener("click", () => { compare = !compare; renderView(); });
  $("search-form").addEventListener("submit", async event => {
    event.preventDefault();
    if (searching || !serviceReady) return;
    const query = $("query").value.trim();
    if (!query) { $("query").focus(); return; }
    clearError();
    setLoading(true);
    $("result-announcement").textContent = "Searching the passage collection.";
    try {
      const payload = await readJSON(await fetch("/api/search", {
        method:"POST", headers:{"Content-Type":"application/json",Accept:"application/json"},
        body:JSON.stringify({query,top_k:Number($("top-k").value)}),
      }));
      if (!Array.isArray(payload.results) || Object.keys(METHODS).some(method => !payload.results.some(result => result.method === method && Array.isArray(result.hits)))) {
        throw new Error("The search response is incomplete.");
      }
      lastResult = payload;
      renderView();
      $("result-announcement").textContent = `Results ready for ${payload.query}.`;
    } catch (error) {
      lastResult = null;
      renderView();
      showError(error.message);
      $("result-announcement").textContent = "Search failed.";
    } finally { setLoading(false); }
  });
  loadStatus();
}
startApp();
