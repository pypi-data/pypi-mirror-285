def unique(l: list) -> list:
    new_list = []
    for i in l:
        if i not in new_list:
            new_list.append(i)
    return new_list

def get(l :list, index, default = ''):
    if 0 <= index < len(l):
        return l[index]
    else:
        return default
    
def fill(l: list, len, default = ''):
    newL = []
    for i in range(len):
        newL.append(get(l, i, default))

    return newL