import frills.debugging as fd
import numpy as np


def get_factors(n):
	factors = []
	for i in range(1, n):
		if n % i == 0:
			factors.append(i)
	return factors



def normalise_to_range(x, min_orig, max_orig, min_new, max_new):
	if isinstance(x, list): x = np.array(x)
	return np.round((x - min_orig) * (max_new - min_new) / (max_orig - min_orig) + min_new, 3)



def euclidean_distance(vector_a, vector_b):
    if type(vector_a) != type(vector_b): fd.printx("\nError in euclidean_distance()\nvector_a and vector_b are inconsistent types\n")
    elif isinstance(vector_a, list): vector_a, vector_b = np.array(vector_a), np.array(vector_b)
    elif isinstance(vector_a, np.ndarray): pass
    else: fd.printx("\nError in euclidean_distance()\nvector_a and vector_b are not the appropriate types\n")
    return np.sqrt(np.sum((vector_a - vector_b)**2))



def cumulative_mean(new_value, current_mean, n):
    return (current_mean * n + new_value) / (n + 1)

