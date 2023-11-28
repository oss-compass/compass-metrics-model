def split_list(input_list, chunk_size=500):
    """ Split a large list into multiple smaller lists """
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]