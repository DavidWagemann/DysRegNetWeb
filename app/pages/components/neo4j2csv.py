def get_csv(graph_map_list):

    tuple_set = set()
    for graph_map in graph_map_list:
        for target in graph_map["targets"]:
            tuple_set.add(get_tuple(target["regulation"]))
        for source in graph_map["sources"]:
            tuple_set.add(get_tuple(source["regulation"]))

    rows = ["source,target,type,fraction"]
    for row in tuple_set:
        rows.append(",".join(row))

    return "\n".join(rows)+"\n"

def get_tuple(regulation):
    source, target = regulation["regulation_id"].split(":")
    fraction = regulation['fraction']
    regulation_type = 'repression' if regulation['direction'] == '-' else 'activation'
    return source, target, regulation_type, str(fraction)
