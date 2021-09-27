import unreal as unreal
import json as json

# Method to import .udatasmith content inside level [Maps/Main]
def import_datasmith_scene(plugin_name, datasmithPath, includeMaterials):
    log_msg ("applySelectionMaterials")
    # Prepare the datasmith content in memory
    datasmith_scene = unreal.DatasmithSceneElement.construct_datasmith_scene_from_file(datasmithPath)

    if datasmith_scene is None :
        log_msg ("Scene loading failed for " + datasmithPath)
        return

    for mesh_actor in datasmith_scene.get_all_mesh_actors():
        actor_label = mesh_actor.get_label()
        if actor_label.contains("REFRIGERATOR") or actor_label.contains("DISHWASHER"):
            log_msg("removing actor named: " + actor_label)
            # add this actor's mesh asset to the list of meshes to skip
            mesh = mesh_actor.get_mesh_element()
            datasmith_scene.remove_mesh_actor(mesh_actor)
            mesh_name = mesh.get_element_name()
            log_msg("removing mesh named " + mesh_name)
            datasmith_scene.remove_mesh(mesh)
        
        
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
    static_mesh_options = import_options.base_options.static_mesh_options

    #generate_lightmap_u_vs (bool): [Read-Write] Generate Lightmap UVs
    static_mesh_options.generate_lightmap_u_vs = True

    #max_lightmap_resolution (DatasmithImportLightmapMax): [Read-Write] Maximum resolution for auto-generated lightmap UVs
    static_mesh_options.max_lightmap_resolution = unreal.DatasmithImportLightmapMax.LIGHTMAP_1024
    
    #min_lightmap_resolution (DatasmithImportLightmapMin): [Read-Write] Minimum resolution for auto-generated lightmap UVs
    static_mesh_options.min_lightmap_resolution = unreal.DatasmithImportLightmapMin.LIGHTMAP_512
    
    #remove_degenerates (bool): [Read-Write] Remove Degenerates
    static_mesh_options.remove_degenerates = True
    
    #---------------------------------------------------------------------------------------------------------------------------
    
    # Import all content inside a 'Datasmith' within the Plugin content directory
    result = datasmith_scene.import_scene("/DLC_" + plugin_name + "/Datasmith")

    if not result.import_succeed:
        log_msg ("Importing datasmith scene failed for " + datasmithPath)
        return

    # After import, remove scene in memory
    datasmith_scene.destroy_scene()

# Method to load level [Maps/Main] and import datasmith scenes
def load_level():
    log_msg ("Loading Maps/Main level...") 
    setup_json = open('C:\\_SceneCreator\\SETUP.json',)
    setup = json.load(setup_json)
    setup_json.close()
  
    levelName = "/DLC_" + setup["name"] + "/Maps/Main"
    log_msg ("Loading " + levelName + "...")
    loadSuccess = unreal.EditorLevelLibrary().load_level(levelName)   
    if not loadSuccess:
        log_msg ("Loading " + levelName + " failed!")

    log_msg ("Loading " + levelName + " successful!")
    
    # Import all .udatasmith content from setup.json  
    for scene in setup["scenes"]:
        import_datasmith_scene(setup["name"], scene, False)

    log_msg ("Importing datasmith scenes successful!")
    
    # Make changes in the new level
    update_level(setup["sceneID"], setup["selectionID"], setup["name"], setup["movableTags"])

    # Save all content
    log_msg ("Saving all dirty packages!")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Method to make changes level [Maps/Main]
def update_level(sceneID, selectionID, name, movableTags):
    log_msg ("update_level")
    # Users can make error when calling for the script
    # So we need to make sure the DAM sceneID is correct
    if not sceneID:
        log_msg('ERROR: No scene id was received. Please add a scene id to the SETUP.json file.')
        return
        
    if not len(sceneID) <= 5:
        log_msg('ERROR: Invalid scene ID. Must be a 5-digit interger number.')
        return
 
    log_msg ("SceneID: " + sceneID)
    # The the sceneID is valid => import the fetch plugin to check if the sceneID exist in DAM's database
    # If the SCENE_META_URL returns the correct result (responseStatus === 1) => sceneID is valid. 
    # Then we can import the rest of the plugins
    import urllib.request as fetch
    import json as json
    SCENE_META_URL = 'http://api.aareas.com/api/Scene/GetSceneMeta/' + str(sceneID)
    response = fetch.urlopen(SCENE_META_URL)
    API_RESPONSE = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))

    if (API_RESPONSE['responseStatus'] != 1):
        log_msg('No such scene id was found in DAM\'s database. Please double check')
        return

    log_msg('Scene ID found in database. Processing...')
    SCENE_META_DATA = API_RESPONSE['responseObject']['surfaceList']
    if (len(SCENE_META_DATA) < 0): 
        log_msg('API Return empty data. Cannot proceed forward')
        return
    else:
        log_msg('Found ' + str(len(SCENE_META_DATA)) + ' surfaces from API.')

    def searchForMeshName(meshName):
        for item in SCENE_META_DATA:
            if item['meshName'].lower() == meshName.lower():
                return item
            else: 
                return None

    # Start scanning and fixing scene actors - fix_name_issues.py
    # This script MUST ALWAYS run before the "movable script", otherwise the name mismatching will cause undesired result

    nameIssueCount = 0
    nameFixCount = 0
    mismatchedNames = []

    # Gets all the StaticMeshActors in the editor level
    list_static_mesh_actors = unreal.EditorFilterLibrary.by_class(unreal.EditorLevelLibrary.get_all_level_actors(),unreal.StaticMeshActor)

    clayMaterial = unreal.load_asset("/DLC_"+ name +"/Materials/White.White")
    
    for act in list_static_mesh_actors:
        # Add collision to all static mesh actors
        mesh_component = act.get_component_by_class(unreal.StaticMeshComponent)
        static_mesh = mesh_component.static_mesh
        unreal.EditorStaticMeshLibrary.remove_collisions(static_mesh)
        unreal.EditorStaticMeshLibrary.add_simple_collisions(static_mesh, unreal.ScriptingCollisionShapeType.BOX)      
        bodysetup = static_mesh.get_editor_property('body_setup')
        bodysetup.set_editor_property("double_sided_geometry", True)
        bodysetup.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        log_msg("Added simple box collision to " + act.get_name()) 
          
        # Set clay material on each static mesh component   
        if ("Plane" not in act.get_name()) :
            log_msg ("Not importing materials...Applying clay mat on all surfaces...")
            num_materials = unreal.EditorStaticMeshLibrary.get_number_materials(static_mesh)
            log_msg (act.get_name() + " | Painting " + str(num_materials) + " Slots...")
        
            for slot in range(num_materials):         
                mesh_component.set_material(slot, clayMaterial)
                
        if (act.get_actor_label() != act.get_name()):
            nameIssueCount += 1

            # Try to fix the name by this cache-clearing hack
            cachedName = act.get_actor_label()

            # Unsafe code: Sometimes Unreal renames the strings that have special character
            # Those code below is hard-coded for those situation
            if (cachedName.startswith('Object_empty')):
                cachedName.replace('Object_empty', '[empty]')

            if ('OPTIONAL' in cachedName):
                # Do nothing for now, to be investigated
                log_msg('')

            act.set_actor_label('tmpName')
            act.set_actor_label(cachedName)

        # Check the name again, if it's still mismatched that means user is using the wrong Max file
        # After the loop => Print out mismatchedNames
        MESH_NAME = act.get_actor_label()
        if (MESH_NAME != act.get_name()):
            mismatchedNames.append(act.get_actor_label())
        else:
            nameFixCount += 1
            # When the name fix is done, start assigning the "moveability" for each actor
            # For testing purpose, we will hard code some popular proxy tags MOVEABLE_ARRAY = ['CDU', 'DOH', ...]
            # If an actor's tag is belong to one of the MOVEABLE_ARRAY's children, then it's moveable. otherwise immovable
            # To get an actor's tag, we just need to look up the actor's name inside SCENE_META_DATA
            # Cab Loop MOVEABLE_ARRAY OR movableTags from json file
            #MOVEABLE_ARRAY = ['CDU', 'DOH', 'FCT', 'SNK', 'SHP', 'PPG', 'TOL', 'SHH', 'DOR', 'CDL', 'CDI']
            RECORD = next((x for x in SCENE_META_DATA if x['meshName'].lower() == MESH_NAME.lower()), None)
            if RECORD:
                log_msg('----------Record found for ' + MESH_NAME)
                # Note: The line below assumes that all surfacetag come in the format [roomkey]_[surfacekey]
                # Should the API change, we're fucked
                SURFACE_TAG = RECORD['surfacetag'].split('_')[1]
                if (SURFACE_TAG in movableTags): 
                    # Set actor movable
                    act.set_mobility(unreal.ComponentMobility.MOVABLE)  
                    log_msg(MESH_NAME + ' has been set to MOVEABLE')
                else:
                    log_msg(MESH_NAME + ' has been set to IMMOVEABLE')
            else:
                log_msg('cannot find record for ' + MESH_NAME)
        
    log_msg('\n')
    log_msg('-------------------SCRIPT EXECUTED---------------------')
    if (nameIssueCount > 0):
        log_msg('Total mismatched name found: ', nameIssueCount)
        log_msg('Total name fixed: ', nameFixCount)
        log_msg('Unable to fix: ', len(mismatchedNames), ' name(s)')
        log_msg('Remained mismatched name(s): ')
        log_msg('\n'.join(mismatchedNames))
    else:
        log_msg('No mismatched name was found. Data is good.')
           
# Method to apply selection id materials to all surfaces in level [Maps/Main]
def apply_api_materials(selectionID, importMaterials, static_mesh_actors):
    if (importMaterials != "False") :     
        log_msg ("Importing Materials | Applying Materials from API")
        # Users can make error when calling for the script
        # So we need to make sure the DAM selectionID is correct
        if not selectionID:
            log_msg('ERROR: No selection id was received. Please add a selection id to the SETUP.json file.')
            return
            
        if not len(selectionID) <= 6:
            log_msg('ERROR: Invalid selection ID. Must be a 6-digit interger number.')
            return

        log_msg ("SelectionID: " + selectionID)
      
        # The the selectionID is valid => import the fetch plugin to check if the selectionID exist in DAM's database
        # If the SCENE_META_URL returns the correct result (responseStatus === 1) => sceneID is valid. 
        # Then we can import the rest of the plugins
        import urllib.request as fetch
        
        SURFACE_LIST_URL = 'http://api.aareas.com/api/SceneSaved/GetSurfaceList/' + str(selectionID)
        response = fetch.urlopen(SURFACE_LIST_URL)
        SL_API_RESPONSE = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))

        if (SL_API_RESPONSE['responseObject']['responseStatus'] != 1):
            log_msg('No such selection id was found in DAM\'s database. Please double check')
            return

        log_msg('Selection ID found in database. Processing...')
        SURFACE_LIST_DATA = SL_API_RESPONSE['responseObject']['surfaceList']
        if (len(SURFACE_LIST_DATA) < 0): 
            log_msg('API Return empty data. Cannot proceed forward')
            return
        else:
            log_msg('Found ' + str(len(SCENE_META_DATA)) + ' surfaces from API.')

        def searchForMeshName(meshName):
            for item in SURFACE_LIST_DATA:
                if item['meshName'].lower() == meshName.lower():
                    return item
                else: 
                    return None
                      
# Method to log to external LOG.txt file
def log_msg(msg):
    f = open("C:\_SceneCreator\LOG.txt", "a")
    f.write(msg + "\n")
    f.close()


logfile = open("C:\_SceneCreator\LOG.txt", "w").close()  
load_level()
