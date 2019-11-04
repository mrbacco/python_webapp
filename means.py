# Python program to print 
# mode of elements 
from collections import Counter
lst =[] # will create a list of elements

# list of elements to calculate mode 
n_num = int(input("enter the number of elements: ")) # let the user decide how many elements in the list
for i in range(0, n_num):
    value = int(input())
    lst.append(value)
    
n = len(lst)

data = Counter(lst) 
get_mode = dict(data) 
mode = [k for k, v in get_mode.items() if v == max(list(data.values()))] #actual calculation of the most occurrencies

if len(mode) == n: 
	get_mode = "No mode found"
else: 
	get_mode = "Mode is / are: " + ', '.join(map(str, mode)) 
	
print(get_mode)

