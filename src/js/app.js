'use strict';

// =====================
// Global App State
// =====================
const App = {
  data: { photobooks: {} },
  currentView: null,

  async init() {
    this.data = await window.electronAPI.loadData();
    if (!this.data.photobooks) this.data.photobooks = {};
    this.showMenu();
    this.createToastContainer();
  },

  async saveData() {
    await window.electronAPI.saveData(this.data);
  },

  createToastContainer() {
    const el = document.createElement('div');
    el.className = 'toast-container';
    el.id = 'toast-container';
    document.body.appendChild(el);
  },

  toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  },

  showMenu() {
    this.renderView(renderMenuView());
    initMenuView();
  },

  showPhotobooks() {
    this.renderView(renderPhotobookView());
    initPhotobookView();
  },

  showSettings() {
    this.renderView(renderSettingsView());
    initSettingsView();
  },

  showGame(config) {
    this.renderView(renderGameView());
    initGameView(config);
  },

  renderView(html) {
    document.getElementById('app').innerHTML = html;
  },
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});

// =====================
// Menu View
// =====================
function renderMenuView() {
  return `
    <div class="view menu-view">
      <div class="menu-center">
        <div class="menu-logo">DilliDalliKlick</div>
        <div class="menu-subtitle">Das Foto-Enthüllungsspiel</div>
        <div class="menu-buttons">
          <button class="btn btn-primary btn-large" id="btn-start">▶ Spiel starten</button>
          <button class="btn btn-info btn-large" id="btn-photobooks">📚 Fotobücher verwalten</button>
        </div>
      </div>
    </div>
  `;
}

function initMenuView() {
  document.getElementById('btn-start').addEventListener('click', () => App.showSettings());
  document.getElementById('btn-photobooks').addEventListener('click', () => App.showPhotobooks());
}

// =====================
// Photobook View
// =====================
function renderPhotobookView() {
  return `
    <div class="view photobook-view">
      <div class="navbar">
        <div class="navbar-brand">📚 Fotobücher</div>
        <div class="navbar-actions">
          <button class="btn btn-secondary" id="btn-back-menu">← Menü</button>
        </div>
      </div>
      <div class="content" id="photobook-content">
        <!-- Rendered by JS -->
      </div>
    </div>
  `;
}

function initPhotobookView() {
  document.getElementById('btn-back-menu').addEventListener('click', () => App.showMenu());
  renderPhotobookList();
}

function renderPhotobookList() {
  const content = document.getElementById('photobook-content');
  const books = App.data.photobooks;
  const bookIds = Object.keys(books);

  let listHtml = '';
  for (const id of bookIds) {
    const book = books[id];
    const photoCount = (book.photos || []).length;
    listHtml += `
      <div class="photobook-card" id="pbc-${id}">
        <div class="photobook-card-title">${escapeHtml(book.name)}</div>
        <div class="photobook-card-meta">${photoCount} Foto(s)${book.directory ? ` · 📁 ${escapeHtml(book.directory)}` : ''}</div>
        <div class="photobook-card-actions">
          <button class="btn btn-info btn-sm" data-action="open" data-id="${id}">Öffnen</button>
          <button class="btn btn-danger btn-sm" data-action="delete" data-id="${id}">Löschen</button>
        </div>
      </div>
    `;
  }

  content.innerHTML = `
    <div class="photobooks-header">
      <h2>Meine Fotobücher</h2>
    </div>
    <div class="photobook-list">
      ${listHtml}
      <div class="photobook-card add-photobook-card" id="btn-add-photobook">
        <div class="icon">➕</div>
        <div>Neues Fotobuch erstellen</div>
      </div>
    </div>
    <div id="photo-manager-area"></div>
  `;

  document.getElementById('btn-add-photobook').addEventListener('click', () => showCreatePhotobookModal());

  document.querySelectorAll('[data-action="open"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      openPhotobookManager(btn.dataset.id);
    });
  });

  document.querySelectorAll('[data-action="delete"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      deletePhotobook(btn.dataset.id);
    });
  });
}

function showCreatePhotobookModal() {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal">
      <h3>Neues Fotobuch</h3>
      <div class="form-group">
        <label>Name des Fotobuchs</label>
        <input type="text" class="form-control" id="new-book-name" placeholder="z.B. Urlaub 2024" />
      </div>
      <div class="modal-actions">
        <button class="btn btn-secondary" id="modal-cancel">Abbrechen</button>
        <button class="btn btn-success" id="modal-create">Erstellen</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const input = document.getElementById('new-book-name');
  input.focus();

  document.getElementById('modal-cancel').addEventListener('click', () => overlay.remove());
  document.getElementById('modal-create').addEventListener('click', () => {
    const name = input.value.trim();
    if (!name) { App.toast('Bitte einen Namen eingeben.', 'error'); return; }
    createPhotobook(name);
    overlay.remove();
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('modal-create').click();
    if (e.key === 'Escape') overlay.remove();
  });
}

function createPhotobook(name) {
  const id = 'book_' + Date.now();
  App.data.photobooks[id] = { id, name, photos: [], directory: null };
  App.saveData();
  App.toast(`Fotobuch "${name}" erstellt.`, 'success');
  renderPhotobookList();
  openPhotobookManager(id);
}

function deletePhotobook(id) {
  const book = App.data.photobooks[id];
  if (!book) return;
  if (!confirm(`Fotobuch "${book.name}" wirklich löschen?`)) return;
  delete App.data.photobooks[id];
  App.saveData();
  App.toast('Fotobuch gelöscht.', 'success');
  renderPhotobookList();
}

async function openPhotobookManager(bookId) {
  const book = App.data.photobooks[bookId];
  if (!book) return;

  const area = document.getElementById('photo-manager-area');
  area.innerHTML = `
    <div class="card photo-manager" id="photo-manager-${bookId}">
      <div class="photo-manager-header">
        <h3>📷 ${escapeHtml(book.name)}</h3>
        <div class="photo-manager-actions">
          <button class="btn btn-secondary btn-sm" id="btn-choose-dir">📁 Verzeichnis wählen</button>
          <button class="btn btn-info btn-sm" id="btn-import-photos">➕ Fotos importieren</button>
          ${book.directory ? `<button class="btn btn-warning btn-sm" id="btn-refresh-dir">🔄 Verzeichnis aktualisieren</button>` : ''}
        </div>
      </div>
      ${book.directory ? `<div class="directory-path">📁 ${escapeHtml(book.directory)}</div>` : ''}
      <div id="photo-grid-${bookId}"></div>
    </div>
  `;

  renderPhotoGrid(bookId);

  document.getElementById('btn-choose-dir').addEventListener('click', async () => {
    const dir = await window.electronAPI.openDirectory();
    if (!dir) return;
    book.directory = dir;
    const files = await window.electronAPI.readDirectory(dir);
    book.photos = [...new Set([...(book.photos || []), ...files])];
    App.saveData();
    renderPhotobookList();
    openPhotobookManager(bookId);
  });

  document.getElementById('btn-import-photos').addEventListener('click', async () => {
    const files = await window.electronAPI.openFiles();
    if (!files.length) return;
    book.photos = [...new Set([...(book.photos || []), ...files])];
    App.saveData();
    App.toast(`${files.length} Foto(s) hinzugefügt.`, 'success');
    renderPhotoGrid(bookId);
  });

  const refreshBtn = document.getElementById('btn-refresh-dir');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', async () => {
      const files = await window.electronAPI.readDirectory(book.directory);
      const existing = new Set(book.photos);
      const added = files.filter(f => !existing.has(f));
      book.photos = [...new Set([...(book.photos || []), ...files])];
      App.saveData();
      App.toast(`${added.length} neue Foto(s) gefunden.`, 'success');
      renderPhotoGrid(bookId);
    });
  }
}

function renderPhotoGrid(bookId) {
  const book = App.data.photobooks[bookId];
  const grid = document.getElementById(`photo-grid-${bookId}`);
  if (!grid) return;

  const photos = book.photos || [];
  if (photos.length === 0) {
    grid.innerHTML = `<div class="empty-photos">Noch keine Fotos. Wähle ein Verzeichnis oder importiere Fotos.</div>`;
    return;
  }

  const thumbsHtml = photos.map((p, i) => `
    <div class="photo-thumb">
      <img src="local-resource://${p.replace(/\\/g, '/')}" alt="Foto ${i + 1}"
           onerror="this.parentElement.style.background='#333';this.style.display='none'" />
      <button class="remove-photo" data-index="${i}" title="Entfernen">✕</button>
    </div>
  `).join('');

  grid.innerHTML = `<div class="photo-grid">${thumbsHtml}</div>`;

  grid.querySelectorAll('.remove-photo').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.index, 10);
      book.photos.splice(idx, 1);
      App.saveData();
      renderPhotoGrid(bookId);
    });
  });
}

// =====================
// Settings View
// =====================
function renderSettingsView() {
  return `
    <div class="view settings-view">
      <div class="navbar">
        <div class="navbar-brand">⚙️ Einstellungen</div>
        <div class="navbar-actions">
          <button class="btn btn-secondary" id="btn-back-menu-settings">← Menü</button>
        </div>
      </div>
      <div class="content">
        <div class="settings-section">
          <h3>Fotobuch</h3>
          <div class="form-group">
            <label>Fotobuch auswählen</label>
            <select class="form-control" id="setting-photobook">
              <option value="">-- Bitte auswählen --</option>
            </select>
          </div>
          <div class="form-group">
            <label>Anzahl der Fotos</label>
            <div class="number-input-group">
              <button id="photos-minus">−</button>
              <input type="number" id="setting-photo-count" value="5" min="1" max="100" />
              <button id="photos-plus">+</button>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h3>Raster</h3>
          <div class="settings-row">
            <div class="settings-row-label">
              <span>Spalten &amp; Zeilen</span>
              <small>Wie viele Teile das Foto aufgeteilt wird</small>
            </div>
            <div class="settings-row-control">
              <div class="grid-inputs">
                <div class="number-input-group">
                  <button id="cols-minus">−</button>
                  <input type="number" id="setting-cols" value="4" min="1" max="20" />
                  <button id="cols-plus">+</button>
                </div>
                <span>✕</span>
                <div class="number-input-group">
                  <button id="rows-minus">−</button>
                  <input type="number" id="setting-rows" value="3" min="1" max="20" />
                  <button id="rows-plus">+</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h3>Enthüllungsmodus</h3>
          <div class="toggle-group" id="reveal-mode-group">
            <label class="toggle-option selected" id="mode-click-label">
              <input type="radio" name="reveal-mode" value="click" id="mode-click" checked />
              🖱️ Klick-Modus
            </label>
            <label class="toggle-option" id="mode-timer-label">
              <input type="radio" name="reveal-mode" value="timer" id="mode-timer" />
              ⏱️ Timer-Modus
            </label>
          </div>
          <div id="timer-settings" class="hidden" style="margin-top:16px;">
            <div class="settings-row">
              <div class="settings-row-label">
                <span>Intervall (Sekunden)</span>
                <small>Wie oft wird ein Feld automatisch aufgedeckt</small>
              </div>
              <div class="settings-row-control">
                <div class="number-input-group">
                  <button id="interval-minus">−</button>
                  <input type="number" id="setting-interval" value="3" min="1" max="60" />
                  <button id="interval-plus">+</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="settings-start">
          <button class="btn btn-primary btn-large" id="btn-start-game">▶ Spiel starten</button>
        </div>
      </div>
    </div>
  `;
}

function initSettingsView() {
  document.getElementById('btn-back-menu-settings').addEventListener('click', () => App.showMenu());

  // Populate photobook dropdown
  const select = document.getElementById('setting-photobook');
  for (const [id, book] of Object.entries(App.data.photobooks)) {
    const opt = document.createElement('option');
    opt.value = id;
    opt.textContent = `${book.name} (${(book.photos || []).length} Fotos)`;
    select.appendChild(opt);
  }

  // Mode toggle
  const clickLabel = document.getElementById('mode-click-label');
  const timerLabel = document.getElementById('mode-timer-label');
  const timerSettings = document.getElementById('timer-settings');

  document.querySelectorAll('[name="reveal-mode"]').forEach(radio => {
    radio.addEventListener('change', () => {
      clickLabel.classList.toggle('selected', document.getElementById('mode-click').checked);
      timerLabel.classList.toggle('selected', document.getElementById('mode-timer').checked);
      timerSettings.classList.toggle('hidden', !document.getElementById('mode-timer').checked);
    });
  });

  // Number inputs
  setupNumberInput('setting-cols', 'cols-minus', 'cols-plus', 1, 20);
  setupNumberInput('setting-rows', 'rows-minus', 'rows-plus', 1, 20);
  setupNumberInput('setting-photo-count', 'photos-minus', 'photos-plus', 1, 100);
  setupNumberInput('setting-interval', 'interval-minus', 'interval-plus', 1, 60);

  // Start game
  document.getElementById('btn-start-game').addEventListener('click', () => {
    const bookId = document.getElementById('setting-photobook').value;
    if (!bookId) { App.toast('Bitte ein Fotobuch auswählen.', 'error'); return; }
    const book = App.data.photobooks[bookId];
    if (!book || !book.photos || book.photos.length === 0) {
      App.toast('Das gewählte Fotobuch enthält keine Fotos.', 'error');
      return;
    }
    const config = {
      bookId,
      photos: book.photos,
      photoCount: parseInt(document.getElementById('setting-photo-count').value, 10),
      cols: parseInt(document.getElementById('setting-cols').value, 10),
      rows: parseInt(document.getElementById('setting-rows').value, 10),
      mode: document.querySelector('[name="reveal-mode"]:checked').value,
      interval: parseInt(document.getElementById('setting-interval').value, 10),
    };
    App.showGame(config);
  });
}

function setupNumberInput(inputId, minusId, plusId, min, max) {
  const input = document.getElementById(inputId);
  document.getElementById(minusId).addEventListener('click', () => {
    const val = parseInt(input.value, 10);
    if (val > min) input.value = val - 1;
  });
  document.getElementById(plusId).addEventListener('click', () => {
    const val = parseInt(input.value, 10);
    if (val < max) input.value = val + 1;
  });
  input.addEventListener('change', () => {
    const val = parseInt(input.value, 10);
    if (isNaN(val) || val < min) input.value = min;
    if (val > max) input.value = max;
  });
}

// =====================
// Game View
// =====================
function renderGameView() {
  return `
    <div class="view game-view">
      <div class="navbar">
        <div class="navbar-brand">🎮 DilliDalliKlick</div>
        <div class="navbar-actions">
          <button class="btn btn-secondary btn-sm" id="btn-back-settings">⚙️ Einstellungen</button>
          <button class="btn btn-secondary btn-sm" id="btn-back-menu-game">🏠 Menü</button>
        </div>
      </div>
      <div class="game-content">
        <div class="game-area">
          <div class="game-info-bar" id="game-info-bar"></div>
          <div class="progress-bar-wrap" style="width:100%;max-width:800px;">
            <div class="progress-bar" id="game-progress" style="width:0%"></div>
          </div>
          <div class="game-board-container" id="game-board-container"></div>
          <div class="game-controls" id="game-controls"></div>
        </div>
      </div>
    </div>
  `;
}

function initGameView(config) {
  document.getElementById('btn-back-settings').addEventListener('click', () => {
    stopTimer();
    App.showSettings();
  });
  document.getElementById('btn-back-menu-game').addEventListener('click', () => {
    stopTimer();
    App.showMenu();
  });

  // Shuffle and pick photos
  const allPhotos = shuffleArray([...config.photos]);
  const selectedPhotos = allPhotos.slice(0, Math.min(config.photoCount, allPhotos.length));

  let currentPhotoIndex = 0;
  let timerInterval = null;

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  // Make stopTimer accessible for nav buttons
  window._gameStopTimer = stopTimer;

  function loadPhoto(index) {
    stopTimer();
    if (index >= selectedPhotos.length) {
      showGameOver();
      return;
    }

    const photoPath = selectedPhotos[index];
    const cols = config.cols;
    const rows = config.rows;
    const totalTiles = cols * rows;
    let revealedTiles = new Set();
    let unrevealed = Array.from({ length: totalTiles }, (_, i) => i);

    updateInfoBar(index, selectedPhotos.length, 0, totalTiles);
    updateProgress(0, totalTiles);

    const container = document.getElementById('game-board-container');
    container.innerHTML = `<div class="game-board" id="game-board">
      <img class="game-board-image" id="game-img" alt="Spiel-Foto" />
      <div class="game-tiles" id="game-tiles"></div>
    </div>`;

    // Size the board
    const img = document.getElementById('game-img');
    const tilesEl = document.getElementById('game-tiles');

    function sizeBoard() {
      const containerW = container.clientWidth - 32;
      const containerH = container.clientHeight - 32;
      const imgW = img.naturalWidth || 800;
      const imgH = img.naturalHeight || 600;
      const scale = Math.min(containerW / imgW, containerH / imgH, 1);
      const w = Math.round(imgW * scale);
      const h = Math.round(imgH * scale);
      const board = document.getElementById('game-board');
      if (board) {
        board.style.width = w + 'px';
        board.style.height = h + 'px';
      }
      if (tilesEl) {
        tilesEl.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
        tilesEl.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
      }
    }

    img.onload = () => {
      sizeBoard();
      buildTiles();
      startMode();
    };

    window.electronAPI.fileToDataUrl(photoPath).then(dataUrl => {
      if (dataUrl) {
        img.src = dataUrl;
      } else {
        // Fallback: try direct file URL
        img.src = 'local-resource://' + photoPath.replace(/\\/g, '/');
        sizeBoard();
        buildTiles();
        startMode();
      }
    });

    function buildTiles() {
      const tilesContainer = document.getElementById('game-tiles');
      if (!tilesContainer) return;
      tilesContainer.innerHTML = '';
      for (let i = 0; i < totalTiles; i++) {
        const tile = document.createElement('div');
        tile.className = 'tile' + (config.mode === 'click' ? ' clickable' : '');
        tile.dataset.index = i;
        if (config.mode === 'click') {
          tile.addEventListener('click', () => revealTile(i));
        }
        tilesContainer.appendChild(tile);
      }
    }

    function revealTile(index) {
      if (revealedTiles.has(index)) return;
      revealedTiles.add(index);
      unrevealed = unrevealed.filter(i => i !== index);

      const tile = document.querySelector(`.tile[data-index="${index}"]`);
      if (tile) tile.classList.add('revealed');

      updateInfoBar(currentPhotoIndex, selectedPhotos.length, revealedTiles.size, totalTiles);
      updateProgress(revealedTiles.size, totalTiles);

      if (revealedTiles.size === totalTiles) {
        onPhotoComplete();
      }
    }

    function revealRandomTile() {
      if (unrevealed.length === 0) return;
      const randIdx = Math.floor(Math.random() * unrevealed.length);
      revealTile(unrevealed[randIdx]);
    }

    function startMode() {
      const controls = document.getElementById('game-controls');
      controls.innerHTML = '';

      if (config.mode === 'timer') {
        const timerDisplay = document.createElement('div');
        timerDisplay.className = 'timer-display';
        timerDisplay.id = 'timer-display';
        timerDisplay.textContent = config.interval + 's';
        controls.appendChild(timerDisplay);

        let remaining = config.interval;
        timerInterval = setInterval(() => {
          remaining--;
          const display = document.getElementById('timer-display');
          if (display) display.textContent = remaining + 's';
          if (remaining <= 0) {
            remaining = config.interval;
            revealRandomTile();
          }
        }, 1000);
      } else {
        const hint = document.createElement('span');
        hint.className = 'text-secondary';
        hint.textContent = 'Klicke auf die Felder, um sie aufzudecken';
        controls.appendChild(hint);
      }
    }

    function onPhotoComplete() {
      stopTimer();
      const board = document.getElementById('game-board');
      if (!board) return;

      const overlay = document.createElement('div');
      overlay.className = 'complete-overlay';
      overlay.innerHTML = `
        <div class="complete-message">
          <h2>✅ Aufgedeckt!</h2>
          <p>Foto ${currentPhotoIndex + 1} von ${selectedPhotos.length}</p>
          ${currentPhotoIndex + 1 < selectedPhotos.length
            ? `<button class="btn btn-success btn-large" id="btn-next-photo">Nächstes Foto ➜</button>`
            : `<button class="btn btn-primary btn-large" id="btn-finish-game">🏁 Spiel beenden</button>`
          }
        </div>
      `;
      board.appendChild(overlay);

      const nextBtn = document.getElementById('btn-next-photo');
      if (nextBtn) {
        nextBtn.addEventListener('click', () => {
          currentPhotoIndex++;
          loadPhoto(currentPhotoIndex);
        });
      }

      const finishBtn = document.getElementById('btn-finish-game');
      if (finishBtn) {
        finishBtn.addEventListener('click', () => showGameOver());
      }
    }
  }

  function updateInfoBar(photoIdx, total, revealed, totalTiles) {
    const bar = document.getElementById('game-info-bar');
    if (!bar) return;
    bar.innerHTML = `
      Foto <span>${photoIdx + 1} / ${total}</span>
      &nbsp;&nbsp;|&nbsp;&nbsp;
      Aufgedeckt <span>${revealed} / ${totalTiles}</span>
      &nbsp;&nbsp;|&nbsp;&nbsp;
      Modus <span>${config.mode === 'click' ? 'Klick' : 'Timer (' + config.interval + 's)'}</span>
    `;
  }

  function updateProgress(revealed, total) {
    const bar = document.getElementById('game-progress');
    if (bar) bar.style.width = Math.round((revealed / total) * 100) + '%';
  }

  function showGameOver() {
    stopTimer();
    const container = document.getElementById('game-board-container');
    container.innerHTML = `
      <div class="complete-message" style="position:relative;z-index:1;">
        <h2>🎉 Spiel beendet!</h2>
        <p>Du hast alle ${selectedPhotos.length} Foto(s) aufgedeckt.</p>
        <div style="display:flex;gap:12px;justify-content:center;margin-top:16px;">
          <button class="btn btn-info btn-large" id="btn-play-again">🔄 Nochmal spielen</button>
          <button class="btn btn-secondary btn-large" id="btn-back-to-menu">🏠 Menü</button>
        </div>
      </div>
    `;
    document.getElementById('btn-play-again').addEventListener('click', () => App.showGame(config));
    document.getElementById('btn-back-to-menu').addEventListener('click', () => App.showMenu());
    document.getElementById('game-controls').innerHTML = '';
    document.getElementById('game-info-bar').innerHTML = '';
    document.getElementById('game-progress').style.width = '100%';
  }

  // Start the first photo
  loadPhoto(0);
}

// =====================
// Helpers
// =====================
function shuffleArray(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function stopTimer() {
  if (window._gameStopTimer) window._gameStopTimer();
}
