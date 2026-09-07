/**
 * ECHO OS — Electron IPC Handlers
 * Native OS integrations for the main process.
 */

import { ipcMain, BrowserWindow, app, shell } from 'electron';
import { exec } from 'child_process';
import os from 'os';
import path from 'path';

export function setupIpcHandlers(mainWindow: BrowserWindow) {
  // ── Window Controls ──

  ipcMain.on('window:minimize', () => {
    mainWindow.minimize();
  });

  ipcMain.on('window:maximize', () => {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  });

  ipcMain.on('window:close', () => {
    mainWindow.hide(); // Minimize to tray
  });

  ipcMain.on('window:toggle-always-on-top', () => {
    const current = mainWindow.isAlwaysOnTop();
    mainWindow.setAlwaysOnTop(!current);
    mainWindow.webContents.send('always-on-top-changed', !current);
  });

  // ── System: Open App ──

  ipcMain.handle('system:open-app', async (_event, appName: string) => {
    return new Promise((resolve) => {
      const platform = process.platform;
      let command: string;

      if (platform === 'win32') {
        command = `start "" "${appName}"`;
      } else if (platform === 'darwin') {
        command = `open -a "${appName}"`;
      } else {
        command = `${appName} &`;
      }

      exec(command, (error) => {
        if (error) {
          resolve({ success: false, error: error.message });
        } else {
          resolve({ success: true });
        }
      });
    });
  });

  // ── System: Search Files ──

  ipcMain.handle('system:search-files', async (_event, query: string, searchPath?: string) => {
    const targetPath = searchPath || os.homedir();
    return new Promise((resolve) => {
      const platform = process.platform;
      let command: string;

      if (platform === 'win32') {
        command = `where /r "${targetPath}" *${query}*`;
      } else {
        command = `find "${targetPath}" -maxdepth 5 -iname "*${query}*" 2>/dev/null | head -20`;
      }

      exec(command, { timeout: 10000 }, (error, stdout) => {
        if (error) {
          resolve({ results: [] });
        } else {
          const files = stdout.trim().split('\n').filter(Boolean).slice(0, 20);
          resolve({
            results: files.map((f) => ({
              path: f.trim(),
              name: path.basename(f.trim()),
            })),
          });
        }
      });
    });
  });

  // ── System: Get Info ──

  ipcMain.handle('system:get-info', async () => {
    const cpus = os.cpus();
    const totalMem = os.totalmem();
    const freeMem = os.freemem();

    return {
      platform: os.platform(),
      arch: os.arch(),
      hostname: os.hostname(),
      cpuModel: cpus[0]?.model || 'Unknown',
      cpuCores: cpus.length,
      totalMemoryGB: (totalMem / (1024 ** 3)).toFixed(1),
      freeMemoryGB: (freeMem / (1024 ** 3)).toFixed(1),
      memoryUsagePercent: Math.round(((totalMem - freeMem) / totalMem) * 100),
      uptime: Math.round(os.uptime()),
    };
  });
}
