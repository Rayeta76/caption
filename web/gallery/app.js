const state = {
  page: 1,
  limit: 36,
  pages: 1,
  query: "",
  format: "",
  item: null,
};

const els = {
  form: document.querySelector("#searchForm"),
  search: document.querySelector("#searchInput"),
  format: document.querySelector("#formatFilter"),
  state: document.querySelector("#stateFilter"),
  grid: document.querySelector("#grid"),
  empty: document.querySelector("#emptyState"),
  resultTitle: document.querySelector("#resultTitle"),
  pageInfo: document.querySelector("#pageInfo"),
  prev: document.querySelector("#prevPage"),
  next: document.querySelector("#nextPage"),
  summary: document.querySelector("#summary"),
  metricTotal: document.querySelector("#metricTotal"),
  metricProcessed: document.querySelector("#metricProcessed"),
  metricThumbs: document.querySelector("#metricThumbs"),
  detail: document.querySelector("#detail"),
  detailImage: document.querySelector("#detailImage"),
  detailName: document.querySelector("#detailName"),
  detailCaption: document.querySelector("#detailCaption"),
  detailMeta: document.querySelector("#detailMeta"),
  keywords: document.querySelector("#keywords"),
  closeDetail: document.querySelector("#closeDetail"),
  copyCaption: document.querySelector("#copyCaption"),
  copyKeywords: document.querySelector("#copyKeywords"),
  openOriginal: document.querySelector("#openOriginal"),
};

function fmtNumber(value) {
  return new Intl.NumberFormat("es-ES").format(value || 0);
}

function fmtBytes(value) {
  if (!value) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = Number(value);
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index ? 1 : 0)} ${units[index]}`;
}

function text(value) {
  return value === null || value === undefined || value === "" ? "—" : String(value);
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function loadStats() {
  const stats = await fetchJson("/api/stats");
  els.metricTotal.textContent = fmtNumber(stats.total);
  els.metricProcessed.textContent = fmtNumber(stats.processed);
  els.metricThumbs.textContent = fmtNumber(stats.withThumbnails);
  els.summary.textContent = `${fmtNumber(stats.total)} imagenes indexadas`;

  stats.formats.forEach((item) => {
    if (!item.format || item.format === "sin formato") return;
    const option = document.createElement("option");
    option.value = item.format;
    option.textContent = `${item.format.toUpperCase()} (${item.count})`;
    els.format.appendChild(option);
  });
}

function cardTemplate(item) {
  const figure = document.createElement("article");
  figure.className = "card";
  figure.tabIndex = 0;
  figure.dataset.id = item.id;
  if (item.width && item.height) {
    figure.style.setProperty("--image-ratio", `${item.width} / ${item.height}`);
  }

  const img = document.createElement("img");
  img.className = "thumb";
  img.loading = "lazy";
  img.alt = item.name;
  img.src = item.hasThumbnail ? `/thumb/${item.id}` : `/media/${item.id}`;
  img.onerror = () => {
    img.removeAttribute("src");
    img.alt = "Imagen no disponible";
    img.classList.add("missing");
  };

  const body = document.createElement("div");
  body.className = "card-body";

  const title = document.createElement("h3");
  title.className = "card-title";
  title.textContent = item.name;

  const caption = document.createElement("p");
  caption.className = "card-caption";
  caption.textContent = item.caption || "Sin caption";

  const chips = document.createElement("div");
  chips.className = "chips";
  (item.keywords || []).slice(0, 3).forEach((keyword) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = keyword;
    chips.appendChild(chip);
  });

  body.append(title, caption, chips);
  figure.append(img, body);
  figure.addEventListener("click", () => openDetail(item.id));
  figure.addEventListener("keydown", (event) => {
    if (event.key === "Enter") openDetail(item.id);
  });
  return figure;
}

async function loadImages() {
  const params = new URLSearchParams({
    page: state.page,
    limit: state.limit,
  });
  if (state.query) params.set("q", state.query);
  if (state.format) params.set("format", state.format);
  if (els.state.value) params.set("state", els.state.value);

  els.grid.innerHTML = "";
  const data = await fetchJson(`/api/images?${params.toString()}`);
  state.pages = data.pages;
  els.empty.hidden = data.items.length !== 0;
  els.resultTitle.textContent = state.query ? `Resultados para "${state.query}"` : "Galeria IA";
  els.pageInfo.textContent = `${data.page} / ${data.pages}`;
  els.prev.disabled = data.page <= 1;
  els.next.disabled = data.page >= data.pages;

  const fragment = document.createDocumentFragment();
  data.items.forEach((item) => fragment.appendChild(cardTemplate(item)));
  els.grid.appendChild(fragment);
}

function renderMeta(item) {
  const origin = item.aiOrigin || {};
  const originLabel = origin.is_ai_generated
    ? `${origin.generator || "Desconocido"}`
    : "No detectado";
  const rows = [
    ["Original", item.originalName],
    ["Origen IA", originLabel],
    ["Formato", item.format],
    ["Tamaño", `${item.width || "?"} x ${item.height || "?"}`],
    ["Peso", fmtBytes(item.sizeBytes)],
    ["Estado", item.state],
    ["Analisis IA", item.model],
    ["Procesado", item.processedAt],
    ["Ruta original", item.originalPath],
    ["Salida", item.outputPath],
  ];
  els.detailMeta.innerHTML = "";
  rows.forEach(([label, value]) => {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = text(value);
    els.detailMeta.append(dt, dd);
  });
}

function renderKeywords(item) {
  els.keywords.innerHTML = "";
  (item.keywords || []).forEach((keyword) => {
    const span = document.createElement("span");
    span.textContent = keyword;
    els.keywords.appendChild(span);
  });
}

async function openDetail(id) {
  const data = await fetchJson(`/api/images/${id}`);
  const item = data.item;
  state.item = item;
  els.detailImage.src = `/media/${id}`;
  els.detailImage.alt = item.name;
  els.detailName.textContent = item.name;
  els.detailCaption.textContent = item.caption || item.description || "Sin caption";
  els.openOriginal.href = `/media/${id}`;
  renderMeta(item);
  renderKeywords(item);
  els.detail.classList.add("open");
  els.detail.setAttribute("aria-hidden", "false");
}

function closeDetail() {
  els.detail.classList.remove("open");
  els.detail.setAttribute("aria-hidden", "true");
  els.detailImage.removeAttribute("src");
  state.item = null;
}

async function copyText(value) {
  if (!value) return;
  await navigator.clipboard.writeText(value);
}

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  state.page = 1;
  state.query = els.search.value.trim();
  state.format = els.format.value;
  loadImages().catch(console.error);
});

els.format.addEventListener("change", () => {
  state.page = 1;
  state.format = els.format.value;
  loadImages().catch(console.error);
});

els.state.addEventListener("change", () => {
  state.page = 1;
  loadImages().catch(console.error);
});

els.prev.addEventListener("click", () => {
  if (state.page <= 1) return;
  state.page -= 1;
  loadImages().catch(console.error);
});

els.next.addEventListener("click", () => {
  if (state.page >= state.pages) return;
  state.page += 1;
  loadImages().catch(console.error);
});

els.closeDetail.addEventListener("click", closeDetail);
els.detail.addEventListener("click", (event) => {
  if (event.target === els.detail) closeDetail();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeDetail();
});
els.copyCaption.addEventListener("click", () => copyText(state.item?.caption || state.item?.description));
els.copyKeywords.addEventListener("click", () => copyText((state.item?.keywords || []).join(", ")));

loadStats()
  .then(loadImages)
  .catch((error) => {
    els.empty.hidden = false;
    els.empty.textContent = error.message;
    console.error(error);
  });
