import unreal
from unreal import StaticMeshActor
from unreal import ComponentMobility
 
lst_actors = unreal.EditorLevelLibrary.get_all_level_actors()
list_static_mesh_actors = unreal.EditorFilterLibrary.by_class(lst_actors,unreal.StaticMeshActor)

for act in list_static_mesh_actors:  
    act.set_mobility(unreal.ComponentMobility.MOVABLE)     
    print('Set ' + act.get_name() + ' Movable')

