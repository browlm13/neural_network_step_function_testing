#python 3

"""
	m = number of categories
	n = number of ranges
	d = interval size, d = R[n]
	R = [R[0],...,R[n]]; where R[0] = 0, R[n] = d
	C = [C[0],..., C[m]]; where C[0] = 'c0',...,C[m-1] = 'cm-1'
	key = [[C[0] ranges],...,[C[m] ranges]] # [r0,...,rn] represnted as integers [0,...,n]
	#A range, rx , is defined as [ R[x] , R[x+1] ) # R[x+1] not inclusive

	#range sizes generated with beta distribution, exluding final range size
	a = alpha in beta distribution
	b = beta in beta distribution
"""

import numpy as np

m = 15
n = 100
d = 1000		#d must be >= n #actually bigger than interval size by 1?
a = 3		#center
b = 20 		#increase to narrow presision

max_range_size = d/2
min_range_size = 1

#
#	generate randomly sized n ranges filling the interval [0,d] exactly
#

"""
	use beta distribution to choose size of each range 
	with exception of the final range size (S[n])

	S = array of range sizes.
	R[0] = 0 additional element (len(S) = len(R) -1)
	R[x] = sum(S[:x+1]) #S[x] included in sum

	genrate n-1 ranges sizes, S, where sum(S) < d
	#S[0] = 0
	S[n] = d - sum(S)	#final range
"""

def generate_range_sizes(n,a,b,max_range_size, min_range_size):
	S = np.random.beta(a, b, size=(n-1))
	S = S*max_range_size + min_range_size 			#scale and make smallest size equal to min_range_size
	return np.rint(S)

S = generate_range_sizes(n,a,b,max_range_size,min_range_size)
while np.sum(S) > (d - min_range_size):
	S = generate_range_sizes(n,a,b,max_range_size,min_range_size)
	b += 1	#increase beta to narrow precision

#S.fill(2)

#add S[n] = d - np.sum(S) to S
S = np.append(S, d - np.sum(S))

#add S[0] = 0 to S
#S = np.insert(S, 0, 0)

"""
	Convert range sizes S, to range start points, R.

	S = array of range sizes.
	R[0] = 0 #additional element (len(S) = len(R) -1)
	R[x] = sum(S[:x+1]) #S[x] included in sum
"""


R = np.zeros(n+1)

for i in range(0,n):
	R[i+1] = np.sum(S[0:i+1])


"""
	See if ranges can be obtained from R

	A range, rx , is defined as [ R[x] , R[x+1] )
	there are n-1 ranges
"""

def get_range(R,x):
	# 0 <= x < n
	#A range, rx , is defined as [ R[x] , R[x+1] ) # R[x+1] not inclusive
	return [R[x], R[x+1]]


"""
	generate m categories and '[c_0,...,c_m-1]'

	give each category 1, then randomly pick for other range grabs

	C = [C[0],..., C[m]]; where C[0] = 'c0',...,C[m-1] = 'cm-1'
	key = [[C[0] ranges],...,[C[m-1] ranges]] # [r0,...,rn] represnted as integers [0,...,n]
"""


C = []
for i in range(m):
	C.append('c' + str(i))

"""
	n+1 ranges
	select m ranges randomly
"""

cpy_R = np.linspace(0,n-1, num=n, dtype=int) #np.copy(R)

key = []
for i in range(m):
	index = np.random.choice(cpy_R.shape[0])  
	key.append([cpy_R[index]])
	cpy_R = np.delete(cpy_R,index)


"""
	randomly assaign the remaining ranges to categories
"""

for i in cpy_R:
	key_index = np.random.choice(len(key))
	key[key_index].append(i)


"""
	write to file in csv format

	term1, term2, catergory_name
"""
"""
Z = np.linspace(0,n-1, num=n, dtype=int)
for i in np.nditer(Z):
	element = int(i)
	print (get_range(R,element))
"""

with open('category_ranges.csv', 'w') as f:
	for i in range(len(key)):
		for j in range(len(key[i])):
			range_terminals = get_range(R,key[i][j])
			s = '%d,%d,%s\n' % (int(range_terminals[0]), int(range_terminals[1]), C[i])
			f.write(s)


"""

given any number, [0,(d-1)], must be able to find the category its in

need to be able to generate test set and training set
values, and there assosiate category values
"""

