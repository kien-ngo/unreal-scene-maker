import sys as sys
import unreal


def validateScenePath():
    # Users can make error when calling for the script
    # So we need to make sure the datasmith scene path is correct
    path = None
    if len(sys.argv) < 2:
        print('ERROR: No datasmith scene path was received.')
        print('>> Please add the datasmith scene path using the folowing command: M:\...\datasmith_importer.py [path]')
        return
    try:
        path = str(sys.argv[1])
    except ValueError:
        print('Invalid path. Must be a valid datasmith scene')
        return

    print('input path is: ', path)
    loadScene(path)
    
def loadScene(path):
   scene = unreal.DatasmithSceneElement.construct_datasmith_scene_from_file(path)
   result = scene.import_scene('/Game/Structure')
   
   
validateScenePath()

   