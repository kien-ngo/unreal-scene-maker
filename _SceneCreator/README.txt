Scene Creator

-------------------
SETUP.json : Used to provide inputs to the script
-------------------

1: Set the name and version of the unreal project
2: Provide the paths to the structure/furniture .udatasmith scene/s you want to import.
3: If you need to modify the engine/template/pythonscripttolaunch/output paths you can use the other fields 

"name": "4387G_30024",
"version": 4.5,
"structure": "(path to structure .udatasmith scene)"
"furniture": "(path to furniture .udatasmith scene)"   
"engine": "(path to unreal engine version)"
"template": "(path to unreal project template to use : Make sure template has a plugin folder inside called DLC_Scene)"
"script": "(path to python script to run on new unreal project)"
"output": "(Where to export the new unreal project)"

-------------------
CREATE.bat
-------------------
Click this to create your new unreal project.

-Clones the template project into the output folder
-Renames project to name from setup.txt
-Renames plugin into name from setup.txt and sets friendlyname inside .uplugin
-Imports the datasmith scenes 
-Runs name fixer, adds collisions, and sets movablity



