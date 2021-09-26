// Plugins
const fs = require('fs-extra')
const { shell } = require('electron');
const { ipcRenderer } = require('electron');
const path = require("path");

// const { PythonShell } = require('python-shell');
// HTML Elements
const PROJECT_NAME_INPUT = document.getElementById('project_name');
const PROJECT_VERSION_INPUT = document.getElementById('project_version');
const PROJECT_UNREAL_VERSION_OPTION = document.getElementById('unreal-version');
const CREATE_SCENE_BUTTON = document.getElementById('createSceneButton');

const SCENE_DATASMITH_BTN = document.getElementById('scene_datasmith_btn');
const SCENE_DATASMITH_TEXT = document.getElementById('selected_scene_datasmith_path');

const FURNITURE_DATASMITH_BTN = document.getElementById('furniture_datasmith_btn');
const FURNITURE_DATASMITH_TEXT = document.getElementById('selected_furniture_datasmith_path');

const OUTPUT_FOLDER_BTN = document.getElementById('output_folder_button');
const OUTPUT_FOLDER_TEXT = document.getElementById('output_folder_text')

const TEMPLATE_FOLDER_BUTTON = document.getElementById('template_folder_button');
const TEMPLATE_FOLDER_TEXT = document.getElementById('template_folder_text');

const DEBUG_BUTTON = document.getElementById('debug_button');

// Global variables
let PROJECT_NAME = '';
let PROJECT_VERSION = '';
let UNREAL_VERSION = '4.26';
let UNREAL_PATH = '';
let TEMPLATE_FOLDER_PATH = './Template';
let SCENE_DATASMITH_PATH = '';
let FURNITURE_DATASMITH_PATH = '';
let OUTPUT_FOLDER_PATH = '';
const IS_TESTING = true;


function createUnrealScene() {
    if (!validateProjectName()) return;
    if (!validateProjectVersion()) return;
    if (!validateUnrealVersion()) return;
    if (!validateSceneDataSmithPath()) return;
    if (!validateOutputFolder()) return;
    console.log('------------------------------');
    console.log('All requirements checked. Generating scene...');
    const jsonContent = generateJsonContent();
    console.log('json content: ', jsonContent);
    const newProjectPath = `${OUTPUT_FOLDER_PATH}\\${PROJECT_NAME}`;

    // create new folder for the new project
    fs.mkdirSync(newProjectPath);

    // copy the template files over
    try {
        fs.copySync(TEMPLATE_FOLDER_PATH, newProjectPath);
        console.log('success!');
        const unrealProjectFileName = findUnrealProjectFile(newProjectPath);
        fs.writeFileSync('config.json', JSON.stringify(jsonContent, null, 4));
        fs.writeFileSync(
            'run.bat', 
            `"${UNREAL_PATH}" "${newProjectPath}\\${unrealProjectFileName}" -run=pythonscript -script="${__dirname}/create_scene.py"`
        );
        openBatchFile('run.bat');
    } 
    catch (err) {
        console.error(err)
    }
}

function findUnrealProjectFile(path) {
    files = fs.readdirSync(path, { withFileTypes: false });
    return files.find(name => name.endsWith('.uproject'));
}

// DEBUG_BUTTON.addEventListener('click', () => {
//     ipcRenderer.send('request-mainprocess-action', {message: 'open-console-debugger'});
// });

TEMPLATE_FOLDER_BUTTON.addEventListener('click', () => {
    const data = {
        message: 'open-template-folder-dialog',
        defaultPath: '.\\Template'
    }
    ipcRenderer.on('save-template-folder-path', (event, arg) => {
        console.log('Output folder path: ', arg);
        files = fs.readdirSync(arg, { withFileTypes: false });
        if (!files.length) {
            alert('Folder is empty. Could not find Unreal Project file (*.uproject)');
        }
        else {
            console.log('Files in template folder: ', files);
            const containsUnrealFile = files.some(fileName => fileName.endsWith('.uproject'));
            if (containsUnrealFile) {
                TEMPLATE_FOLDER_PATH = arg;
                TEMPLATE_FOLDER_TEXT.innerHTML = arg;
            }
            else {
                alert('Folder does not have Unreal project file (*.uproject)');
            }
        }
    });
    ipcRenderer.send('request-mainprocess-action', data);
})

OUTPUT_FOLDER_BTN.addEventListener('click', () => {
    const DEFAULT_PATH = (IS_TESTING) ? 'C:\\' : 'M:\\';

    const data = {
        message: 'open-output-folder-dialog',
        defaultPath: DEFAULT_PATH
    }
    ipcRenderer.on('save-output-folder-path', (event, arg) => {
        console.log('Output folder path: ', arg);
        OUTPUT_FOLDER_PATH = arg;
        OUTPUT_FOLDER_TEXT.innerHTML = arg;
    });
    ipcRenderer.send('request-mainprocess-action', data);
});

SCENE_DATASMITH_BTN.addEventListener('click', () => {
    const DEFAULT_PATH = (IS_TESTING) ? 'C:\\' : 'M:\\';

    const data = {
        message: 'open-scene-datasmith-dialog',
        defaultPath: DEFAULT_PATH
    }
    ipcRenderer.on('save-scene-datasmith-path', (event, arg) => {
        console.log('Furniture datasmith: ', arg);
        SCENE_DATASMITH_PATH = arg;
        SCENE_DATASMITH_TEXT.innerHTML = arg;
        checkIfDatasmithFilesAreDuplicated()
    });
    ipcRenderer.send('request-mainprocess-action', data);
});

FURNITURE_DATASMITH_BTN.addEventListener('click', () => {
    const DEFAULT_PATH = (IS_TESTING) ? 'C:\\' : 'M:\\';

    const data = {
        message: 'open-furniture-datasmith-dialog',
        defaultPath: DEFAULT_PATH
    }
    ipcRenderer.on('save-furniture-datasmith-path', (event, arg) => {
        console.log('Furniture datasmith: ', arg);
        FURNITURE_DATASMITH_PATH = arg;
        FURNITURE_DATASMITH_TEXT.innerHTML = arg;
        checkIfDatasmithFilesAreDuplicated()
    });
    ipcRenderer.send('request-mainprocess-action', data);
});

CREATE_SCENE_BUTTON.addEventListener('click', () => {
    createUnrealScene();
});

function validateProjectName() {
    const projectName = PROJECT_NAME_INPUT.value;
    if (!projectName) {
        alert('Project Name cannot be empty');
        return false;
    }
    PROJECT_NAME = projectName;
    return true;
}

function validateProjectVersion() {
    const projectVersion = PROJECT_VERSION_INPUT.value;
    if (!projectVersion) {
        alert('Project version cannot be empty');
        return false;
    }
    PROJECT_VERSION = projectVersion;
    return true;
}

function validateUnrealVersion() {
    const unrealVersion = PROJECT_UNREAL_VERSION_OPTION.value;
    const path = `C:\\Program Files\\Epic Games\\UE_${unrealVersion}\\Engine\\Binaries\\Win64\\UE4Editor.exe`;
    if (fs.existsSync(path)) {
        console.log('Unreal version is valid. ', unrealVersion);
        UNREAL_PATH = path;
        UNREAL_VERSION = unrealVersion;
        return true;
    } 
    else {
        alert('Cannot find unreal version ' + unrealVersion + '. Custom installation is not supported');
        return false;
    }
}

function validateSceneDataSmithPath() {
    if (!SCENE_DATASMITH_PATH) {
        alert('Please select a datasmith file');
        return false;
    }
    return true;
}

function validateOutputFolder() {
    if (!OUTPUT_FOLDER_PATH) {
        alert('Please select an output folder');
        return false;
    }
    const newProjectPath = `${OUTPUT_FOLDER_PATH}\\${PROJECT_NAME}`;
    if (fs.existsSync(newProjectPath)) {
        alert(`The path [${newProjectPath}] already exists. Please select another path, or change the project name`);
        return false;
    }
    else {
        return true;
    }
}

function checkIfDatasmithFilesAreDuplicated() {
    if (SCENE_DATASMITH_PATH && FURNITURE_DATASMITH_PATH && SCENE_DATASMITH_PATH === FURNITURE_DATASMITH_PATH)
        alert('Warning: You just selected the same datasmith file for both Scene and Furniture!');
}

function generateJsonContent() {
    return {
        name: PROJECT_NAME,
        version: PROJECT_VERSION,
        scenes: [SCENE_DATASMITH_PATH, FURNITURE_DATASMITH_PATH].filter(item => !!item),
        structure: SCENE_DATASMITH_PATH,
        furniture: FURNITURE_DATASMITH_PATH,
        engine: UNREAL_PATH,
        template: TEMPLATE_FOLDER_PATH,
        output: OUTPUT_FOLDER_PATH
    }
}

function openBatchFile(path) {
    shell.openPath(path);
}

// function callCreateScenePython(json) {
//     let pyshell = new PythonShell('create_scene.py');
//     pyshell.send(JSON.stringify(json))
//     pyshell.on('message', function(message) {
//         console.log(message);
//     });

//     pyshell.end(function (err) {
//         if (err){
//             throw err;
//         };
//         console.log('create_scene.py finished');
//     });
// }