#!/usr/bin/env python

# opPtimizer: optimization framework for AI   
# Copyright (c) 2019 Artur Bak

OPP_VER = 2

def oppversion():
    return 'o'+ str(OPP_VER)

def opp(*items):
    itemList = [i for i in items]
    oppString =''
    i = 0
    while i < len(itemList) - 1:
        if oppString != '':
            oppString += ';'
        oppString += str(itemList[i]) + '=' +  str(itemList[i+1])
        i += 2
    
    return oppString

def oppsum(*props):
    opp = ''
    for prop in props:
        if opp != '':
            opp += ';'
        opp += prop
    return opp

#returns oppstring consist of keys with empty values
def oppemptyvals(*keys):
    keyList = [i for i in keys]
    params = []
    for k in keyList:
        params.append(k)
        params.append('')
    return opp(*tuple(params))

# extracts value for key if found in params (returns None if key not exists in params)
# @param params the parameter list which will be searched for the key
# @param default value that will be returned if no key value is found in params
def oppval(key, params, default=None):
    result = None
    items = params.split(';')
    for item in items:
        tokens = item.split('=')
        if (tokens[0] == key):
            if len(tokens) > 1:
                result = tokens[1]
            else:
                result = None
            break
    
    if result == None:
        result = default

    return result

#Sets bool value for key
def oppbool(key, val):
    valToSet = '1' if val and (val == True or val==1 or val=='1' or val == 'T' or val == 't') else '0'
    return opp(key, valToSet)

# Returns True if val is '1' or 'True' or 'true' or 'T' or 't's
# False othewise (or if no key found in paramssss)
def oppvalbool(key, params):
    
    result = False
    val = oppval(key, params)
    if val =='1' or val == 'True' or val == 'true' or val == 'T' or val == 't':
        result = True
    
    return result

#returns first key from params
def oppkey(params):
    key = None
    tokens = params.split('=')
    if len(tokens) > 1:
        key = tokens[0]
    return key

def oppkeys(params):
    keys = []
    items = params.split(';')
    for item in items:
        tokens = item.split('=')
        keys.append(tokens[0])
    return keys

def oppvals(params):
    values = []
    items = params.split(';')
    for item in items:
        tokens = item.split('=')
        values.append(tokens[1])
    return values

def oppitems(params):
    items = []
    for item in params.split(';'):
        items.append(item)
    return items

# Makes OPP string from list of parameters
#e.g. opplist('key', 1, 2, 3)
# If a list must be passed as an argument, use: opplist('key', *list)
def opplist(key, *listitems):
    result = key + '='
    vals = ''
    for item in listitems:
        if (vals != ''):
            vals += ','
        vals += item
    return result + vals

#Returns list of item from specific value of oppstring 
def opplistvals(listval):
    result = []
    if listval != None and listval != '':
        vals = listval.split(',')
        for val in vals:
            result.append(val)
    return result

# Returns the list made of values for given key
def opptolist(key, params):
    result = None
    
    val = oppval(key, params)
    if val:
        result = opplistvals(val)

    return result

# Creates dictionary from pairs in the list
# - list should contain event number of parameters like [key1,val1,key2,val2]
# - for list with odd number of parameters or if value is '' the resultant dict item is key->None 
def opplisttodict(params):
    dict = None
    list = opplistvals(params)
    list_len = len(list) if list else 0
    if list_len > 0:
        dict = {}
        key_ind = 0 
        while key_ind < list_len:
            dict[list[key_ind]] = list[key_ind + 1] if key_ind + 1 < list_len else None 
            key_ind += 2
    
    return dict

# Returns the list of two element tuples for all pairs on the list
# - for list with odd number of parameters the last member is paired with None
def opplisttopairs(params):
    result = []
    list = opplistvals(params)
    list_len = len(list) if list else 0
    if list_len > 0:
        first_elem_ind = 0 
        while first_elem_ind < list_len:
            first_elem = list[first_elem_ind]
            second_elem = list[first_elem_ind + 1] if first_elem_ind + 1 < list_len else None
            result.append((first_elem, second_elem))
            first_elem_ind += 2
    
    return result

# Returns the two-elem tuplels made of list of pair values for given key
def opptopairs(key, params):
    val = oppval(key, params)
    result = opplisttopairs(val)
    return result

def oppmodify(params,newValues):
    newParams = ''
    paramItems = params.split(';')
    newValItems = newValues.split(';')
    
    #change existing ones
    for paramItem in paramItems:
        paramTokens = paramItem.split('=')
        if (len(paramTokens)):
            val = oppval(paramTokens[0], newValues)
            if (val!=''):
                if (newParams != ''):
                    newParams = newParams + ';'
                if (val):
                    newParams = newParams + paramTokens[0] + '=' + val
                else:
                    newParams = newParams + paramItem

    #add new ones
    for newValItem in newValItems:
        newValTokens = newValItem.split('=')
        if (len(newValTokens) == 2):
            val = oppval(newValTokens[0], params)
            if (not val and newValTokens[1] != ''):
                if (newParams!=''):
                    newParams = newParams + ';'
                newParams = newParams + newValItem
        
    return newParams

# Makes a range of parameters
# e.g opprange('key', 1, 2)
# If a list must be passed as an argument, use: opprange('key', *list)
def opprange(key, *rangeVals):
    resultList = [key]
    for val in rangeVals:
        resultList.append(val)
    return resultList