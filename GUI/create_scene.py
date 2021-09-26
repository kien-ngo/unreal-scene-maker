import unreal
import json

f = open('C:\\_SceneCreator\\SETUP.json',)
json = json.load(f)

name = json["name"] + '_' + str(json["version"])
structure = json["structure"]
furniture = json["furniture"]
output = json["output"]

f.close()

structure_ds = unreal.DatasmithSceneElement.construct_datasmith_scene_from_file(structure)

if structure_ds is None:
    print(".udatasmith file is invalid.")
    quit()

# Get import options.
structure_ds_import_options = structure_ds.get_options(unreal.DatasmithImportOptions)
    
# Set import options.
structure_ds_import_options.base_options.scene_handling = unreal.DatasmithImportScene.NEW_LEVEL

# Your destination folder must start with /Game/
structure_scene = structure_ds.import_scene("/Game/")

if not structure_scene.import_succeed:
    print("Importing structure datasmith scene failed.")
    quit()

# Clean up the Datasmith Scene.
structure_ds.destroy_scene()
print("Importing structure datasmith complete!")


