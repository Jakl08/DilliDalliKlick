'use strict';

const { app, BrowserWindow, ipcMain, dialog, Menu, protocol, net } = require('electron');
const path = require('path');
const fs = require('fs');
const url = require('url');

// Register protocol privilege before app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'local-resource', privileges: { secure: true, supportFetchAPI: true, bypassCSP: false, corsEnabled: false, stream: true } },
]);

let mainWindow;
const userDataPath = app.getPath('userData');
const dataFilePath = path.join(userDataPath, 'data.json');

function loadData() {
  if (!fs.existsSync(dataFilePath)) {
    return { photobooks: {} };
  }
  try {
    return JSON.parse(fs.readFileSync(dataFilePath, 'utf8'));
  } catch (e) {
    return { photobooks: {} };
  }
}

function saveData(data) {
  fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2), 'utf8');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    title: 'DilliDalliKlick',
    backgroundColor: '#1a1a2e',
    show: false,
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  Menu.setApplicationMenu(null);
}

app.whenReady().then(() => {
  // Register custom protocol to serve local image files
  protocol.handle('local-resource', (request) => {
    const filePath = decodeURIComponent(request.url.slice('local-resource://'.length));
    return net.fetch(url.pathToFileURL(filePath).toString());
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers

ipcMain.handle('data:load', () => {
  return loadData();
});

ipcMain.handle('data:save', (_event, data) => {
  saveData(data);
  return true;
});

ipcMain.handle('dialog:openDirectory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  });
  if (result.canceled || result.filePaths.length === 0) return null;
  return result.filePaths[0];
});

ipcMain.handle('dialog:openFiles', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'] },
    ],
  });
  if (result.canceled || result.filePaths.length === 0) return [];
  return result.filePaths;
});

ipcMain.handle('fs:readDirectory', (_event, dirPath) => {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'];
  try {
    const files = fs.readdirSync(dirPath);
    return files
      .filter(f => imageExtensions.includes(path.extname(f).toLowerCase()))
      .map(f => path.join(dirPath, f));
  } catch (e) {
    return [];
  }
});

ipcMain.handle('fs:fileToDataUrl', (_event, filePath) => {
  try {
    const data = fs.readFileSync(filePath);
    const ext = path.extname(filePath).toLowerCase().replace('.', '');
    const mimeType = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg'
      : ext === 'png' ? 'image/png'
      : ext === 'gif' ? 'image/gif'
      : ext === 'bmp' ? 'image/bmp'
      : ext === 'webp' ? 'image/webp'
      : ext === 'svg' ? 'image/svg+xml'
      : 'image/jpeg';
    return `data:${mimeType};base64,${data.toString('base64')}`;
  } catch (e) {
    return null;
  }
});

ipcMain.handle('fs:copyFile', (_event, srcPath, destDir) => {
  try {
    if (!fs.existsSync(destDir)) {
      fs.mkdirSync(destDir, { recursive: true });
    }
    const fileName = path.basename(srcPath);
    const destPath = path.join(destDir, fileName);
    fs.copyFileSync(srcPath, destPath);
    return destPath;
  } catch (e) {
    return null;
  }
});

ipcMain.handle('app:getUserDataPath', () => {
  return userDataPath;
});
