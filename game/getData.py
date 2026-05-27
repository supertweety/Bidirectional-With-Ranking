import os
import numpy as np

# Repo-root /data directory, resolved relative to this file so data loads
# regardless of the current working directory.
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def get_data(useDummyData=False):
    """
    Load game states from a text file.

    Args:
        useDummyData (bool): Whether to use the small test dataset.

    Returns:
        list: List of 10x10 numpy arrays representing game states.
    """
    all_states=[]
    f = None
    if useDummyData:
        f=open(os.path.join(_DATA_DIR, "test_box.txt"), "r")
    else:
        f=open(os.path.join(_DATA_DIR, "states10_3box.txt"), "r")

    array_s=[]
    array_a=[]
    duplicate = []
    index = []

    i=0
    k=0
    for line in f:
        if k < 10:
            k+=1
            continue
        array_s.append([int(x) for x in line.split()])
        #print(i)
        if array_s[i] not in duplicate:
            arr=np.asarray(array_s[i])
            temp=np.reshape(arr, (10,10))
            all_states.append(temp)
            duplicate.append(array_s[i])
            index.append(i)
        i+=1
        # if i > 10:
        #     break
        # break

    return all_states
    f.close()


def get_paths():
    """
    Load paths from a text file.
    
    Returns:
        list: List of paths, where each path is a list of game states.
    """
    all_paths=[]
    f=open(os.path.join(_DATA_DIR, "paths10_3box.txt"), "r")
    array_s=[]
    for line in f:
        array_s.append([int(x) for x in line.split()])
        arr=np.asarray(array_s[:-1])
        all_paths.append(arr)
        array_s=[]
    return all_paths