import numpy as np

def get_data(useDummyData=False):
    all_states=[]
    f = None
    if useDummyData:
        f=open("test_box.txt", "r")
    else:
        f=open("states10_3box.txt", "r")

    array_s=[]
    array_a=[]
    duplicate = []
    index = []

    i=0
    for line in f:
        array_s.append([int(x) for x in line.split()])
        #print(i)
        if array_s[i] not in duplicate:
            arr=np.asarray(array_s[i])
            temp=np.reshape(arr, (10,10))
            all_states.append(temp)
            duplicate.append(array_s[i])
            index.append(i)
        i+=1
        if i > 10:
            break
        # break

    return all_states
    f.close()
