def dimension_multi2one(data, old_list=[]):
    
    '''
    把一个多维度list变为单维度list
    '''
    
    if not isinstance(data, list) :
        return data
        
    for key in data :
        if not isinstance(key, list) :
            old_list.append(key)
        elif isinstance(key, list):
            sub_list = dimension_multi2one(key, old_list=old_list)
            old_list = old_list + sub_list
            
    old_list = set(old_list)
    old_list = list(old_list)
    return old_list
