def try_to_reach(source, target, skip_path, paths, visited_already):
    for path in paths:
        if path != skip_path:
            if path[0] == source and path[1] == target:
                return True
            elif path[0] == source and path[1] not in visited_already:
                visited_already.append(path[1])
                if try_to_reach(path[1], target, skip_path, paths, visited_already):
                    return True

    return False

def check_soundness(activity, skip_path, remaining_paths, start_activities, end_activities):
    reached_source = False
    for start_activity in start_activities:
        if start_activity == activity or try_to_reach(start_activity, activity, skip_path, remaining_paths, []):
            reached_source = True

    if not reached_source:
        return False

    reached_target = False
    for end_activity in end_activities:
        if end_activity == activity or try_to_reach(activity, end_activity, skip_path, remaining_paths, []):
            reached_target = True

    return reached_target

def filter_dfg_activity(activities, paths, start_activities, end_activities):
    for activity in activities.copy():
        if activity not in start_activities and activity not in end_activities:
            sources = []
            targets = []

            for path in paths:
                if path[0] == activity:
                    targets.append(path[1])
                if path[1] == activity:
                    sources.append(path[0])

            can_filter = True
            for source in sources:
                target_count = 0
                for path in paths:
                    if source == path[0]:
                        target_count += 1
                if target_count <= 1:
                    can_filter = False
                    break
            for target in targets:
                source_count = 0
                for path in paths:
                    if target == path[1]:
                        source_count += 1
                if source_count <= 1:
                    can_filter = False
                    break

            if can_filter:
                remaining_activities = activities.copy()
                del remaining_activities[activity]

                remaining_paths = {}
                for path in paths:
                    if activity != path[0] and activity != path[1]:
                        remaining_paths[path] = paths[path]

                for remaining_activity in remaining_activities:
                    if not check_soundness(remaining_activity, (activity, activity), remaining_paths, start_activities, end_activities):
                        can_filter = False
                        break

                if can_filter:
                    return remaining_activities, remaining_paths, False

    return activities, paths, True

def filter_dfg_activities(percentage, dfg, start_activities, end_activities, sort_by = "frequency", ascending = True):
    remaining_activities = dict(sorted(dfg["activities"].items(), key = lambda activity: activity[1][sort_by], reverse = not ascending))
    remaining_paths = dfg["connections"]

    activities_to_filter = int(len(remaining_activities) - round(len(remaining_activities) * percentage / 100, 0))

    end_reached = False
    for i in range(activities_to_filter):
        remaining_activities, remaining_paths, end_reached = filter_dfg_activity(remaining_activities, remaining_paths, start_activities, end_activities)

        if end_reached:
            break

    dfg["activities"] = remaining_activities
    dfg["connections"] = remaining_paths

    return dfg

def filter_dfg_cycles(dfg):
    filtered_paths = {}
    remaining_paths = {}

    for path in dfg["connections"]:
        if path[0] == path[1]:
            filtered_paths[path] = dfg["connections"][path]
        else:
            remaining_paths[path] = dfg["connections"][path]

    return filtered_paths, remaining_paths

def filter_dfg_path(filtered_paths, remaining_paths, start_activities, end_activities):
    for path in remaining_paths.copy():
        source_count = 0
        target_count = 0

        for other_path in remaining_paths:
            if path[0] == other_path[0]:
                source_count += 1
            if path[1] == other_path[1]:
                target_count += 1

        if source_count > 1 and target_count > 1:
            if check_soundness(path[0], path, remaining_paths, start_activities, end_activities) and check_soundness(path[1], path, remaining_paths, start_activities, end_activities):

                filtered_paths[path] = remaining_paths[path]
                del remaining_paths[path]

                return filtered_paths, remaining_paths, False

    return filtered_paths, remaining_paths, True

def filter_dfg_paths(percentage, dfg, start_activities, end_activities, sort_by = "frequency", ascending = True):
    filtered_paths, remaining_paths = filter_dfg_cycles(dfg)

    remaining_paths = dict(sorted(remaining_paths.items(), key = lambda path: path[1][sort_by], reverse = not ascending))

    end_reached = False
    while not end_reached:
        filtered_paths, remaining_paths, end_reached = filter_dfg_path(filtered_paths, remaining_paths, start_activities, end_activities)

    filtered_paths = dict(sorted(filtered_paths.items(), key = lambda path: path[1][sort_by], reverse = ascending))
    paths_to_include = round(len(filtered_paths) * percentage / 100, 0)

    if paths_to_include > 0:
        i = 0
        for path, values in filtered_paths.items():
            remaining_paths[path] = values

            i += 1
            if i >= paths_to_include:
                break

    dfg["connections"] = remaining_paths

    return dfg