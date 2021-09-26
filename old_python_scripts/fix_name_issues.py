import unreal
from unreal import Vector

lst_actors = unreal.EditorLevelLibrary.get_all_level_actors()
lst_nameIssueActors = []

for act in lst_actors:     
    if (act.get_actor_label() != act.get_name()):
        lst_nameIssueActors.append(act)

print(str(len(lst_nameIssueActors)) + ' Name Issues Found!')



for act in lst_nameIssueActors:  
    cachedName = act.get_actor_label()     
    act.set_actor_label('tmpName')
    act.set_actor_label(cachedName)
    print('Fixed ' + cachedName)
    
print('Fixed ' + str(len(lst_nameIssueActors)) + ' Issues')