
__all__ = ['base_convert']

#BASE2 = "01"
#BASE10 = "0123456789"
#BASE16 = "0123456789abcdef"
#BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base_convert(number,frombase = 10, tobase = 36):
	""" converts a "number" between two bases of arbitrary digits

	The input number is assumed to be a string of digits from the
	fromdigits string (which is in order of smallest to largest
	digit). The return value is a string of elements from todigits
	(ordered in the same way). The input and output bases are
	determined from the lengths of the digit strings. Negative 
	signs are passed through.


	"""
	
	if not 2 <= frombase <= 62 or not 2 <= tobase <= 62:
		raise ValueError, 'The base number must be between 2 and 36.'

	if str(number)[0]=='-':
		number = str(number)[1:]
		neg=1
	else:
		neg=0

	fromdigits = BASE62[:frombase]
	todigits = BASE62[:tobase]
	
	#print(fromdigits, todigits)
	#print(len(fromdigits), len(todigits))
	
	# make an integer out of the number
	x=long(0)
	for digit in str(number):
		#print '%d %s %d' % (x, digit, fromdigits.index(digit))
		x = x*frombase + fromdigits.index(digit)
	
	#print 'last x: %s' % x
	## create the result in base 'len(todigits)'
	res=""
	while x>0:
		digit = x % tobase
		#print 'x %s d %s' % (x, digit)
		res = todigits[digit] + res
		x /= tobase
	if neg:
		res = "-"+res

	return res

if __name__ == '__main__':
	a = 45
	print '{0}: {1}'.format(a, base_convert(a, 10, 36))
	a = 'abcd'
	print '{0}: {1}'.format(a, base_convert(a, 16, 36))
	a = '5cc163b92ab9b482b4486999d354f91e'
	print '{0}: {1}'.format(a, base_convert(a, 16, 36))
