// Modules to control application life and create native browser window
const { app, BrowserWindow } = require('electron')
const path = require('path')

function createWindow() {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    resizable: true
  })
  mainWindow.removeMenu();
  mainWindow.webContents.openDevTools();
  // and load the index.html of the app.
  mainWindow.loadFile('index.html')
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
const { ipcMain } = require('electron');
const { dialog } = require('electron')

// Attach listener in the main process with the given ID
ipcMain.on('request-mainprocess-action', (event, arg) => {
  console.log('Message from render: ', arg);
  if (arg.message === 'open-console-debugger') {
    // mainWindow.webContents.openDevTools()
  }
  else if (arg.message === 'open-scene-datasmith-dialog') {
    dialog.showOpenDialog({
      defaultPath: arg.defaultPath || '',
      // Restricting the user to only Text Files. 
      filters: [
        {
          name: 'Custom File Type',
          extensions: ['udatasmith']
        },],
      properties: ['openFile']
    }).then(file => {
      if (!file.canceled) {
        event.sender.send('save-scene-datasmith-path', file.filePaths[0].toString());
      }
    }).catch(err => {
      console.log(err)
    });
  }
  else if (arg.message === 'open-furniture-datasmith-dialog') {
    dialog.showOpenDialog({
      defaultPath: arg.defaultPath || '',
      filters: [
        {
          name: 'Custom File Type',
          extensions: ['udatasmith']
        },],
      properties: ['openFile']
    }).then(file => {
      if (!file.canceled) {
        event.sender.send('save-furniture-datasmith-path', file.filePaths[0].toString());
      }
    }).catch(err => {
      console.log(err)
    });
  }
  else if (arg.message === 'open-output-folder-dialog') {
    dialog.showOpenDialog({
      defaultPath: arg.defaultPath || '',
      properties: ['openDirectory']
    }).then(result => {
      if (!result.canceled) {
        event.sender.send('save-output-folder-path', result.filePaths[0]);
      }
    }).catch(err => {
      console.log(err)
    });
  }
  else if (arg.message === 'open-template-folder-dialog') {
    dialog.showOpenDialog({
      defaultPath: arg.defaultPath || '',
      properties: ['openDirectory']
    }).then(result => {
      if (!result.canceled) {
        event.sender.send('save-template-folder-path', result.filePaths[0]);
      }
    }).catch(err => {
      console.log(err)
    });
  }
});