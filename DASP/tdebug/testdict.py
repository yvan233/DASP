# D = {'a':11,'b':22, 'c':33}
# print(D.get('d',0))

# print(list(D.keys()))


import json
keylist = [1,5,99,13,1401]
valuelist = ['a','b','c','d','e']
D = dict(zip(keylist,valuelist))
print (sorted(D.keys()))
json_list = json.dumps(D, indent=2);
print(json_list)

# if 2 not in D :
#     print (1)
# if D.setdefault(2) or D.setdefault(2).p:
#     pass

# for ele in D:
#     print(D[ele])