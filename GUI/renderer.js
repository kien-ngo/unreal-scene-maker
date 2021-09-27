// Plugins
const fs = require('fs-extra')
const { shell, ipcRenderer } = require('electron');


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
const DAM_SCENE_ID_INPUT = document.getElementById('dam_scene_id');
const ADD_COLLISION_INPUT = document.getElementById('add_collision_input');
const CREATE_PAK_INPUT = document.getElementById('create_pak_input');


// Global variables
let PROJECT_NAME = '';
let DAM_SCENE_ID = '';
let PROJECT_VERSION = '';
let UNREAL_VERSION = '4.26';
let UNREAL_PATH = '';
let TEMPLATE_FOLDER_PATH = './Template';
let SCENE_DATASMITH_PATH = '';
let FURNITURE_DATASMITH_PATH = '';
let OUTPUT_FOLDER_PATH = '';
let TO_ADD_COLLISION = true;
let TO_CREATE_PAK = false;
let SCENE_META_DATA = [];
const IS_TESTING = true;


function createUnrealScene() {
    if (!validateProjectName()) return;
    if (!validateDamSceneId()) return;
    if (!validateProjectVersion()) return;
    if (!validateUnrealVersion()) return;
    if (!validateSceneDataSmithPath()) return;
    if (!validateOutputFolder()) return;

    fetch(`http://api.aareas.com/api/Scene/GetSceneMeta/${DAM_SCENE_ID}`).then(res => res.json()).then(data => {
        if (data.responseStatus != 1) {
            showErrorMessage('No such scene id was found in DAM\'s database. Please double check');
            return;
        }
        else {
            SCENE_META_DATA = data.responseObject;
            console.log('------------------------------');
            console.log('All requirements checked. Generating scene...');
            const jsonContent = generateJsonContent();
            console.log('json content: ', jsonContent);
            const newProjectPath = `${OUTPUT_FOLDER_PATH}\\${PROJECT_NAME}`;
        
            // create new folder for the new project
            fs.mkdirSync(newProjectPath);
        
            // copy the template files over
            try {
                const files = fs.readdirSync(TEMPLATE_FOLDER_PATH);
                if (files.includes('Plugins')) {
                    const pluginFiles = fs.readdirSync(TEMPLATE_FOLDER_PATH + '/Plugins/');
                    console.log(pluginFiles);
                    if (pluginFiles.length) {
                        const DLC_name = pluginFiles.find(name => name.startsWith('DLC_'));
                        if (DLC_name) {
                            fs.copySync(TEMPLATE_FOLDER_PATH, newProjectPath);
                            const currentDlcPath = newProjectPath + `\\Plugins\\${DLC_name}`;
                            const newDlcPath = newProjectPath + `\\Plugins\\DLC_${PROJECT_NAME}`;
                            fs.renameSync(currentDlcPath, newDlcPath);
                            const unrealProjectFileName = findUnrealProjectFile(newProjectPath);
                            fs.writeFileSync('config.json', JSON.stringify(jsonContent, null, 4));
                            fs.writeFileSync(
                                'run.bat', 
                                `"${UNREAL_PATH}" "${newProjectPath}\\${unrealProjectFileName}" -run=pythonscript -script="${__dirname}/create_scene.py"`
                            );
                            openBatchFile('run.bat');
                        }
                        else {
                            showErrorMessage('Cannot find DLC Folder. Aborted')
                        }
                    }
                    else {
                        showErrorMessage('Plugins folder empty');
                    }
                }
                else {
                    showErrorMessage('Selected template does not have Plugins. Aborted')
                }
            } 
            catch (err) {
                console.error(err)
            }
        }
    })
    .catch(err => {
        showErrorMessage('Cannot get data from this DAM Scene ID: ', DAM_SCENE_ID);
    });
}

ADD_COLLISION_INPUT.addEventListener('change', () => {
    TO_ADD_COLLISION = !TO_ADD_COLLISION;
});

CREATE_PAK_INPUT.addEventListener('change', () => {
    TO_CREATE_PAK = !TO_CREATE_PAK;
});

function findUnrealProjectFile(path) {
    files = fs.readdirSync(path, { withFileTypes: false });
    return files.find(name => name.endsWith('.uproject'));
}

DEBUG_BUTTON.addEventListener('click', () => {
    ipcRenderer.send('request-mainprocess-action', {message: 'open-console-debugger'});
});

TEMPLATE_FOLDER_BUTTON.addEventListener('click', () => {
    const data = {
        message: 'open-template-folder-dialog',
        defaultPath: '.\\Template'
    }
    ipcRenderer.on('save-template-folder-path', (event, arg) => {
        console.log('Output folder path: ', arg);
        files = fs.readdirSync(arg, { withFileTypes: false });
        if (!files.length) {
            showErrorMessage('Folder is empty. Could not find Unreal Project file (*.uproject)');
        }
        else {
            console.log('Files in template folder: ', files);
            const containsUnrealFile = files.some(fileName => fileName.endsWith('.uproject'));
            if (containsUnrealFile) {
                TEMPLATE_FOLDER_PATH = arg;
                TEMPLATE_FOLDER_TEXT.innerHTML = arg;
            }
            else {
                showErrorMessage('Folder does not have Unreal project file (*.uproject)');
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

function validateDamSceneId() {
    try {
        let damSceneId = parseInt(DAM_SCENE_ID_INPUT.value);
        if (!isNaN(damSceneId)) {
            DAM_SCENE_ID = damSceneId;
            return true;
        }
        else {
            showErrorMessage('Invalid DAM Scene id');
            return false;
        }
    }
    catch(err) {
        showErrorMessage(err);
        return false;
    }
}

function validateProjectName() {
    const projectName = PROJECT_NAME_INPUT.value;
    if (!projectName) {
        showErrorMessage('Project Name cannot be empty');
        return false;
    }
    PROJECT_NAME = projectName;
    return true;
}

function validateProjectVersion() {
    const projectVersion = PROJECT_VERSION_INPUT.value;
    if (!projectVersion) {
        showErrorMessage('Project version cannot be empty');
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
        showErrorMessage('Cannot find unreal version ' + unrealVersion + '. Custom installation is not supported');
        return false;
    }
}

function validateSceneDataSmithPath() {
    if (!SCENE_DATASMITH_PATH) {
        showErrorMessage('Please select a datasmith file');
        return false;
    }
    return true;
}

function validateOutputFolder() {
    if (!OUTPUT_FOLDER_PATH) {
        showErrorMessage('Please select an output folder');
        return false;
    }
    const newProjectPath = `${OUTPUT_FOLDER_PATH}\\${PROJECT_NAME}`;
    if (fs.existsSync(newProjectPath)) {
        showErrorMessage(`The path [${newProjectPath}] already exists. Please select another path, or change the project name`);
        return false;
    }
    else {
        return true;
    }
}

function checkIfDatasmithFilesAreDuplicated() {
    if (SCENE_DATASMITH_PATH && FURNITURE_DATASMITH_PATH && SCENE_DATASMITH_PATH === FURNITURE_DATASMITH_PATH)
        showErrorMessage('Warning: You just selected the same datasmith file for both Scene and Furniture!');
}

function generateJsonContent() {
    return {
        name: PROJECT_NAME,
        sceneID: DAM_SCENE_ID,
        sceneMetaData: SCENE_META_DATA,
        version: PROJECT_VERSION,
        scenes: [SCENE_DATASMITH_PATH, FURNITURE_DATASMITH_PATH].filter(item => !!item).map(item => {
            return {
                path: item,
                addMaterial: false
            }
        }),
        structure: SCENE_DATASMITH_PATH,
        furniture: FURNITURE_DATASMITH_PATH,
        engine: UNREAL_PATH,
        template: TEMPLATE_FOLDER_PATH,
        output: OUTPUT_FOLDER_PATH,
        movableTags: ["CDU", "DOH", "FCT", "SNK", "SHP", "PPG", "TOL", "SHH", "DOR", "CDL", "CDI", "BCK", "OVN", "CTP", "FAN", "FRG", "DWH", "STV"],
        addCollision: TO_ADD_COLLISION,
        createPak: TO_CREATE_PAK
    }
}

function openBatchFile(path) {
    shell.openPath(path);
}

function showErrorMessage(msg) {
    const data = {
        message: 'showErrorMessage',
        data: msg
    }
    ipcRenderer.send('request-mainprocess-action', data);
}