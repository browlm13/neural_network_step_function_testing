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
import csv

#
#	generate randomly sized n ranges filling the interval [0,d] exactly
#

def generate_range_sizes(n,a,b,max_range_size, min_range_size):
	S = np.random.beta(a, b, size=(n-1))
	S = S*max_range_size + min_range_size 			#scale and make smallest size equal to min_range_size
	return np.rint(S)

#generate R
def generate_R(n,a,b,max_range_size,min_range_size):

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
	S = generate_range_sizes(n,a,b,max_range_size,min_range_size)
	while np.sum(S) > (d - min_range_size):
		S = generate_range_sizes(n,a,b,max_range_size,min_range_size)
		b += 1	#increase beta to narrow precision

	#add S[n] = d - np.sum(S) to S
	S = np.append(S, d - np.sum(S))

	"""
		Convert range sizes S, to range start points, R.

		S = array of range sizes.
		R[0] = 0 #additional element (len(S) = len(R) -1)
		R[x] = sum(S[:x+1]) #S[x] included in sum
	"""
	R = np.zeros(n+1)

	for i in range(0,n):
		R[i+1] = np.sum(S[0:i+1])

	return R


def get_range(R,x):

	"""
	obtained range from R

	A range, rx , is defined as [ R[x] , R[x+1] )
	there are n-1 ranges
	"""
	# 0 <= x < n
	#A range, rx , is defined as [ R[x] , R[x+1] ) # R[x+1] not inclusive
	return [R[x], R[x+1]]


def generate_C(m):
	#generate m categories and '[c_0,...,c_m-1]'
	C = []
	for i in range(m):
		C.append('c' + str(i))
	return C

def generate_key(n,m):
	"""
		give each category 1, then randomly pick for other range grabs

		C = [C[0],..., C[m]]; where C[0] = 'c0',...,C[m-1] = 'cm-1'
		key = [[C[0] ranges],...,[C[m-1] ranges]] # [r0,...,rn] represnted as integers [0,...,n]
	"""


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

	return key


def write_to_csv(fname, R, C, key):
	#write to file in csv format: term1, term2, catergory_name
	with open(fname, 'w') as f:
		for i in range(len(key)):
			for j in range(len(key[i])):
				range_terminals = get_range(R,key[i][j])
				s = '%d,%d,%s\n' % (int(range_terminals[0]), int(range_terminals[1]), C[i])
				f.write(s)

"""

	test csv range generation

"""
m = 6
n = 30
d = 100		#d must be >= n #actually bigger than interval size by 1?
a = 3		#center
b = 20 		#increase to narrow presision

max_range_size = d/2
min_range_size = 1

CSV_FNAME = 'category_ranges.csv'

R = generate_R(n,a,b,max_range_size,min_range_size)
C = generate_C(m)
key = generate_key(n,m)

write_to_csv(CSV_FNAME, R, C, key)


"""

given any number, [0,(d-1)], must be able to find the category its in

need to be able to generate test set and training set
values, and there assosiate category values
"""


#return greatest common denominator of two numbers
def gcd (a,b):
    if (b == 0):
        return a
    else:
         return gcd (b, a % b)

#return greatest common denominator of a list of numbers
def gcd_list(list):
	res = list[0]
	for c in list[1::]:
	    res = gcd(res , c)
	return res

#extract all range blocks  from csv{term_1:, term_2:, category_name:}
def read_range_blocks(CSV_FNAME):
	all_blocks = []
	with open(CSV_FNAME, mode='r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			block = {}
			block['term_1'] = int(row[0])
			block['term_2'] = int(row[1])
			block['category_name'] = row[2]
			all_blocks.append(block)
	return all_blocks

#set global GCD and global lookup table
def create_global_lookup_table():
	global GCD
	global lookup_table
	global CSV_FNAME

	all_blocks = iana_country_blocks(CSV_FNAME)
	terminals_1 = [b['term_1'] for b in all_blocks]
	terminals_2 = [b['term_2'] for b in all_blocks]

	GCD = gcd_list(terminals_1)

	#build, constant time, memory hog, lookup table
	lookup_table = [DEFAULT_VALUE] * ( int(terminals_2[-1]/GCD) + 1 )
	for block in all_blocks:
		lookup_table[int(block['term_1']/GCD)] = block['category_name']

		low = int(block['term_1']//GCD)
		high = int( -(-block['term_2'])//GCD) + 1

		#fill slots between terminals
		n = high - low
		for i in range(n):
			lookup_table[low+(i)] = block['category_name']

def val_to_category(val):
	global lookup_table
	global GCD

	return lookup_table[val//GCD]


#global for constant time speed up
lookup_table = []
GCD = -1

def main(args=None):

	if (len(sys.argv) != 3):	sys.exit()
	infile = sys.argv[1]
	outfile = sys.argv[2]

	#load lookup table into ram
	create_global_lookup_table()

	#load ip list
	ips = read_ip_list(infile)

	#look up start
	countries = [ip_to_country(ip) for ip in ips]

	#write ip list
	with open(outfile, mode='w+') as f:
		for i in range(0, len(ips)):
			f.write("%s,%s\n" % (countries[i], ips[i]))


#
#	run program
#

#if __name__ == "__main__":
#	main()
