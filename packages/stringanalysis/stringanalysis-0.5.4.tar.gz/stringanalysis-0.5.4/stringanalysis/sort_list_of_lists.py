from stringanalysis.stringanalysis import sort_list_of_lists as raw  # type: ignore

def sort_list_of_lists(l, keep_scores: bool = False, **kwargs):
    if keep_scores:
        return raw([[((i[0], i[1]), i[1]) for i in j] for j in l])
    else:
        return raw(l)