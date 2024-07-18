#!/usr/bin/env python

# opPtimizer: optimization framework for AI  
# Copyright (c) 2019 Artur Bak. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .pcons import *



MEDBASE_VER = 1

_PRINT_LOG_ENABLED = True

def medbaseversion():
    return 'b' + str(MEDBASE_VER)

#Get relative path (from execution directory) to file realted to test
# @testName  name of test
#
#
def getDecorFileName(fileName, prefix= None, postfix = None):
 
    decoratedFileName = ''

    if prefix:
        decoratedFileName += prefix
    
    decoratedFileName += fileName
     
    if postfix:
        decoratedFileName += postfix
        
    return decoratedFileName


def getFileLines(file):
    f = open(file,'r')
    lines = f.readlines()
    lines = [l.split('\n')[0] for l in lines]
    return lines
    
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

# prints the object on standard output
def oppdbg(object_to_write):
    if _PRINT_LOG_ENABLED:
        print(object_to_write)

def set_move_chunk(chunk_ind_start, chunk_size, first, second):
    
    moved_count = 0
    while moved_count < chunk_size and len(first) > chunk_ind_start:
        el = first.pop(chunk_ind_start)
        second.append(el)
        moved_count += 1


    return

def set_get_index_pairs(index_list):

    index_pairs_str = ''
    ind_first = 0
    ind_second = ind_first
    list_len = len(index_list)

    while ind_first < list_len:

        add_pair_condiftion = False
        
        if ind_second >= list_len - 1:
            add_pair_condiftion = True # we reach end of list
        else:
            #print(' i_s ' + str(index_list[ind_second]) + ' is+1:' + str(index_list[ind_second + 1]) + ' cond ' + str(index_list[ind_second + 1] > index_list[ind_second]))
            if index_list[ind_second + 1] - index_list[ind_second] > 1 or index_list[ind_second + 1] < index_list[ind_second]:
                add_pair_condiftion = True
            

        #add_pair_condiftion = index_list[ind_second] - index_list[ind_first] > 1 if ind_second < list_len else add_pair_condiftion

        if add_pair_condiftion:
            # ADD pair
            if len(index_pairs_str) > 0:
                index_pairs_str += ','
            index_pairs_str += str(index_list[ind_first]) + ',' + str(index_list[ind_second])
            ind_first = ind_second + 1
            ind_second = ind_first
        else:
            ind_second += 1

    return index_pairs_str

def set_getSplitPairs(setToSplit, ratio, first_index, chunk_size, step):


    curr_first = setToSplit
    curr_second = []

    print('getSplitPairs::LEN: ' + str(len(curr_first)) + ' -------->')

    curr_ratio = 1.0

    curr_ind = first_index
    while curr_ratio > ratio:
        set_move_chunk(curr_ind, chunk_size, curr_first, curr_second)
        curr_first_size = len(curr_first)
        curr_second_size = len(curr_second)
        curr_ratio =  curr_first_size / (curr_second_size + curr_first_size)
        curr_ind += step
        print(str(curr_ind) + '('  + str(curr_ratio) + '):' + str(curr_first) + ' ' + str(curr_second))
        if curr_ind >= len(curr_first):
            curr_ind = 0

    print('LEN_sum: ' + str(len(curr_first) + len(curr_second)))
    return set_get_index_pairs(curr_first), set_get_index_pairs(curr_second)

# Returns given text many times in string separated by comma 
def set_getFilesInString(text, ntimes = 1):
    str = ''
    for i in range(ntimes):
        if i>0:
            str +=','
        str += text
    return str

def set_getPairsAndFiles(pairs, file_name):
    
    pairs_count = len(pairs.split(','))
    files = set_getFilesInString(file_name, int(pairs_count/2))

    print(' == PAIRS: ' + str(pairs) + ' ' + str(files))
    
    return pairs, files

