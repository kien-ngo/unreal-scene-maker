import unreal
from unreal import Vector

lst_actors = unreal.EditorLevelLibrary.get_all_level_actors()
lst_nameIssueActors = []

for act in lst_actors:     
    if (act.get_actor_label() != act.get_name()):
        lst_nameIssueActors.append(act)
        print(act.get_actor_label())

print(str(len(lst_nameIssueActors)) + ' Name Issues Found!')

