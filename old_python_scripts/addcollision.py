import unreal
from unreal import StaticMesh
from unreal import StaticMeshComponent
from unreal import BodySetup
from unreal import CollisionTraceFlag
from unreal import EditorStaticMeshLibrary
from unreal import EditorLevelLibrary
from unreal import ScriptingCollisionShapeType
from unreal import GameplayStatics

#Gets all the static mesh actors in the scene
lst_actors = unreal.GameplayStatics.get_all_actors_of_class(unreal.EditorLevelLibrary.get_editor_world(), unreal.StaticMeshActor)

#These are the names being excluded
lst_excludedNames = []

#Both arrays are cached
lst_excludedActors = []
lst_actorsToAddCollisionsTo = []

def SortActorsInScene():
    #Iterates all the actors in the scene 
    #If the name contains any string from excluded names list it will add it to excluded actors list
    for actor in lst_actors:  
        for excludedName in lst_excludedNames:
            #Compares both string upper to ensure the case doesnt cause a mismatch
            if excludedName.upper() in actor.get_name().upper():
                lst_excludedActors.append(actor)
                print(actor.get_name() + " | Excluded:  True")
                
    print(str(len(lst_excludedActors)) + ' actors excluded from search!--------------------------------------------->')

    #Iterates all the actors in the scene and if its not in the excluded actors list add it to the list
    for actor in lst_actors:  
            if actor not in lst_excludedActors:
                lst_actorsToAddCollisionsTo.append(actor)

def AddCollisions():
     print(str(len(lst_actorsToAddCollisionsTo)) + ' actors to add collisions to!--------------------------------------------->')  
     for actor in lst_actorsToAddCollisionsTo:     
         mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
         static_mesh = mesh_component.static_mesh
         unreal.EditorStaticMeshLibrary.remove_collisions(static_mesh)
         unreal.EditorStaticMeshLibrary.add_simple_collisions(static_mesh, unreal.ScriptingCollisionShapeType.BOX)      
         bodysetup = static_mesh.get_editor_property('body_setup')
         bodysetup.set_editor_property("double_sided_geometry", True)
         bodysetup.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
         print("Added simple box collision to " + actor.get_name())   
    
SortActorsInScene();    
AddCollisions();
  



    



