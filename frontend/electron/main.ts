/**
 * ECHO OS — Electron Main Process
 * Frameless, transparent, always-on-top desktop shell with system tray and global hotkey.
 */

import { app, BrowserWindow, Tray, Menu, globalShortcut, ipcMain, nativeImage, screen } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import { setupIpcHandlers } from './ipc-handlers';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let isQuitting = false;

const isDev = process.env.NODE_ENV !== 'production' || !app.isPackaged;

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: Math.min(1280, screenWidth * 0.85),
    height: Math.min(800, screenHeight * 0.85),
    minWidth: 800,
    minHeight: 600,
    frame: false,
    transparent: true,
    resizable: true,
    movable: true,
    alwaysOnTop: false,
    skipTaskbar: false,
    backgroundColor: '#00000000',
    icon: path.join(__dirname, '../public/favicon.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
    titleBarStyle: 'hidden',
    titleBarOverlay: false,
    show: false, // Show after ready-to-show
  });

  // Load app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
    mainWindow?.focus();
  });

  // Minimize to tray instead of closing
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTray() {
  // Create a simple tray icon
  const icon = nativeImage.createFromDataURL(
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAGJJREFUWEft17ENgDAQRNF/KGigoqOho6KgoUP4LDlSZGe1vsLy6G5tkyT94vTH+ycA0wlMJ2A8Ad5+JLkludpPwHcCxhOQPB95Lfe7A0wn0J+A8QR4eyWZ5G+S3O8OMJ3AHRR0ICFHKqH3AAAAAElFTkSuQmCC'
  );

  tray = new Tray(icon);
  tray.setToolTip('ECHO OS');

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '◈ Show ECHO OS',
      click: () => {
        mainWindow?.show();
        mainWindow?.focus();
      },
    },
    { type: 'separator' },
    {
      label: '📌 Always on Top',
      type: 'checkbox',
      checked: false,
      click: (menuItem) => {
        mainWindow?.setAlwaysOnTop(menuItem.checked);
        mainWindow?.webContents.send('always-on-top-changed', menuItem.checked);
      },
    },
    { type: 'separator' },
    {
      label: '⚙️ Developer Tools',
      click: () => mainWindow?.webContents.openDevTools({ mode: 'detach' }),
      visible: isDev,
    },
    { type: 'separator' },
    {
      label: '❌ Quit ECHO OS',
      click: () => {
        isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    mainWindow?.show();
    mainWindow?.focus();
  });
}

function registerGlobalHotkey() {
  // Ctrl+Shift+E to toggle ECHO OS visibility
  globalShortcut.register('CommandOrControl+Shift+E', () => {
    if (mainWindow?.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow?.show();
      mainWindow?.focus();
    }
  });

  // Ctrl+Shift+V for push-to-talk
  globalShortcut.register('CommandOrControl+Shift+V', () => {
    mainWindow?.webContents.send('push-to-talk');
  });
}

// ── App Lifecycle ──

app.whenReady().then(() => {
  createWindow();
  createTray();
  registerGlobalHotkey();
  setupIpcHandlers(mainWindow!);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    mainWindow?.show();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

// Prevent multiple instances
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}
