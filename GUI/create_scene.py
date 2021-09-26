import unreal
import json
from pathlib import Path

PYTHON_BASE_PATH = str(Path(__file__).parent.absolute())

# Method to create a new unreal level inside Maps/Main and load it then begin importing scenes
def create():
    setup_json = open(PYTHON_BASE_PATH + '/config.json',)
    setup = json.load(setup_json)
    setup_json.close()

    levelName = "/DLC_" + setup["name"] + "/Maps/Main"
    loadSuccess = unreal.EditorLevelLibrary().load_level(levelName)   
    if not loadSuccess:
        print ("Loading Map failed!")

    # Import all .udatasmith content from setup.json  
    for scene in setup["scenes"]:
        #scene != setup["scenes"][0]
        import_datasmith_scene(setup["name"], scene, True)
            
    # Save all content
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Method to import .udatasmith content inside Maps/Main
def import_datasmith_scene(plugin_name, datasmithPath, includeMaterials):
    # Prepare the datasmith content in memory
    datasmith_scene = unreal.DatasmithSceneElement.construct_datasmith_scene_from_file(datasmithPath)

    if datasmith_scene is None :
        print ("Scene loading failed for " + datasmithPath)
        return

    #OPTIONS FOR DATASMITH IMPORT-------------------------------------------------------------------------------------------------
    # Prepare any settings - set the scene handling to only import assets and to not create a map
    import_options = datasmith_scene.get_options(unreal.DatasmithImportOptions)

    #include_animation (bool): [Read-Write] Specifies whether or not to import animations
    import_options.base_options.include_animation = False
    
    #include_camera (bool): [Read-Write] Specifies whether or not to import cameras
    import_options.base_options.include_camera = False
    
    #include_geometry (bool): [Read-Write] Specifies whether or not to import geometry
    import_options.base_options.include_geometry = True
    
    #include_light (bool): [Read-Write] Specifies whether or not to import lights
    import_options.base_options.include_light = False
    
    #include_material (bool): [Read-Write] Specifies whether or not to import materials and textures
    import_options.base_options.include_material = includeMaterials
    
    #scene_handling (DatasmithImportScene): [Read-Write] Specifies where to put the content 
    import_options.base_options.scene_handling = unreal.DatasmithImportScene.CURRENT_LEVEL
    
    #STATIC MESH OPTIONS FOR DATASMITH IMPORT-----------------------------------------------------------------------------------

    #static_mesh_options (DatasmithStaticMeshImportOptions): [Read-Write] Static Mesh Options
    #static_mesh_options = import_options.base_options.static_mesh_options

    #generate_lightmap_u_vs (bool): [Read-Write] Generate Lightmap UVs
    #static_mesh_options.generate_lightmap_u_vs = True

    #max_lightmap_resolution (DatasmithImportLightmapMax): [Read-Write] Maximum resolution for auto-generated lightmap UVs
    #static_mesh_options.max_lightmap_resolution = unreal.DatasmithImportLightmapMax.LIGHTMAP_1024
    
    #min_lightmap_resolution (DatasmithImportLightmapMin): [Read-Write] Minimum resolution for auto-generated lightmap UVs
    #static_mesh_options.min_lightmap_resolution = unreal.DatasmithImportLightmapMin.LIGHTMAP_16
    
    #remove_degenerates (bool): [Read-Write] Remove Degenerates
    #static_mesh_options.remove_degenerates = False
    
    #---------------------------------------------------------------------------------------------------------------------------
    
    # Import all content inside a 'Datasmith' within the Plugin content directory
    result = datasmith_scene.import_scene("/DLC_" + plugin_name + "/Datasmith")

    if not result.import_succeed:
        print ("Importing datasmith scene failed for " + datasmithPath)
        return

    # After import, remove scene in memory
    datasmith_scene.destroy_scene()

create()
