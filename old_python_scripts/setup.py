import sys as sys

# By default, the command should be "python setup.py [sceneId]" with sceneid being a 5-to-6 digit integer
# To tell the script to add collision, use "python setup.py [sceneId] add-collision"
#                    to remove collision, use "python setup.py [sceneId] remove-collision"


def validateDAMSceneId():
    # Users can make error when calling for the script
    # So we need to make sure the DAM SceneId is correct
    sceneId = None
    if len(sys.argv) < 2:
        print('ERROR: No scene id was received.')
        print('>> Please add the scene id using the folowing command: M:\...\setup.py [sceneId]')
        return
    try:
        sceneId = int(sys.argv[1])
    except ValueError:
        print('Invalid scene ID. Must be a 5-digit interger number')
        return

    # If user passes a third argument, that arg is supposed to be for add/remove collision
    if len(sys.argv) == 3:
        validateCollisionArgument()
    else:
        print('No collision option provided. Proceeding to fix the names')

    print('input sceneID is: ', sceneId)
    fixNameAndAddMobility(sceneId)


def fixNameAndAddMobility(sceneId):
    # The the sceneID is valid => import the fetch plugin to check if the sceneid exist in DAM's database
    # If the SCENE_META_URL returns the correct result (responseStatus === 1) => sceneId is valid. 
    # Then we can import the rest of the plugins
    import urllib.request as fetch
    import json as json
    SCENE_META_URL = 'http://api.aareas.com/api/Scene/GetSceneMeta/' + str(sceneId)
    response = fetch.urlopen(SCENE_META_URL)
    API_RESPONSE = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))

    if (API_RESPONSE['responseStatus'] != 1):
        print('No such scene id was found in DAM\'s database. Please double check')
        return

    print('Scene ID found in database. Processing...')
    SCENE_META_DATA = API_RESPONSE['responseObject']['surfaceList']
    if (len(SCENE_META_DATA) < 0): 
        print('API Return empty data. Cannot proceed forward')
        return
    else:
        print('Found ' + str(len(SCENE_META_DATA)) + ' surfaces from API.')

    def searchForMeshName(meshName):
        for item in SCENE_META_DATA:
            if item['meshName'].lower() == meshName.lower():
                return item
            else: 
                return None

    # Start scanning and fixing scene actors - fix_name_issues.py
    # This script MUST ALWAYS run before the "movable script", otherwise the name mismatching will cause undesired result
    import unreal as unreal

    nameIssueCount = 0
    nameFixCount = 0
    mismatchedNames = []

    # Gets all the actors in the editor level
    lst_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    #Filtered array of StaticMeshActors 
    list_static_mesh_actors = unreal.EditorFilterLibrary.by_class(lst_actors,unreal.StaticMeshActor)

    for act in list_static_mesh_actors:
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
                print('')

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
            MOVEABLE_ARRAY = ['CDU', 'DOH', 'FCT', 'SNK', 'SHP', 'PPG', 'TOL', 'SHH', 'DOR', 'CDL', 'CDI']
            RECORD = next((x for x in SCENE_META_DATA if x['meshName'].lower() == MESH_NAME.lower()), None)
            if RECORD:
                print('----------Record found for ' + MESH_NAME)
                # Note: The line below assumes that all surfacetag come in the format [roomkey]_[surfacekey]
                # Should the API change, we're fucked
                SURFACE_TAG = RECORD['surfacetag'].split('_')[1]
                if (SURFACE_TAG in MOVEABLE_ARRAY): 
                    # Set actor movable
                    act.set_mobility(unreal.ComponentMobility.MOVABLE)  
                    print(MESH_NAME, ' has been set to MOVEABLE')
                else:
                    print(MESH_NAME, ' has been set to IMMOVEABLE')
            else:
                print('cannot find record for ' + MESH_NAME)
        
    print('\n')
    print('-------------------SCRIPT EXECUTED---------------------')
    if (nameIssueCount > 0):
        print('Total mismatched name found: ', nameIssueCount)
        print('Total name fixed: ', nameFixCount)
        print('Unable to fix: ', len(mismatchedNames), ' name(s)')
        print('Remained mismatched name(s): ')
        print('\n'.join(mismatchedNames))
    else:
        print('No mismatched name was found. Data is good.')


# Used to call either 1 of these 2 script: addcollision.py and removecollision.py  
def validateCollisionArgument():
    # Note to Qais: We can call the file "addcollision.py" and "removecollision" directly from here
    # Just need to make sure the relative PATH is correct.
    # For now I will assume that ALL THE SCRIPTS ARE IN THE SAME FOLDER, so we can call their names directly 

    collisionOption = sys.argv[2]
    if (collisionOption == 'add-collision'):
        try: 
            import addcollision     
        except ImportError:
            print('Could not find "addcollision.py"')

    elif (collisionOption == 'remove-collision'):
        try: 
            import removecollision     
        except ImportError:
            print('Could not find "removecollision.py"')


if __name__ == "__main__":
    validateDAMSceneId()