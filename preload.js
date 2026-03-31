'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  loadData: () => ipcRenderer.invoke('data:load'),
  saveData: (data) => ipcRenderer.invoke('data:save', data),
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  openFiles: () => ipcRenderer.invoke('dialog:openFiles'),
  readDirectory: (dirPath) => ipcRenderer.invoke('fs:readDirectory', dirPath),
  fileToDataUrl: (filePath) => ipcRenderer.invoke('fs:fileToDataUrl', filePath),
  copyFile: (srcPath, destDir) => ipcRenderer.invoke('fs:copyFile', srcPath, destDir),
  getUserDataPath: () => ipcRenderer.invoke('app:getUserDataPath'),
});
