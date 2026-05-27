from scipy.stats import truncnorm
import numpy as np

# Define parameters for the UNTRUNCATED normal distribution
MEAN = 0.0
STD_DEV = 1.0
LOWER_BOUND = -1.0
UPPER_BOUND = 1.0

EXPECTED_VALUE = 5

def samp_rand_norm():
    """
    Generate a random value using a Poisson distribution.
    
    Returns:
        int: Randomly sampled value.
    """

    ## integer poisson distribution
    return np.random.poisson(lam=EXPECTED_VALUE)
    
    ## float normal distribtion

    # Calculate the standardized bounds (a and b) required by scipy:
    # a = (lower_bound - mean) / std_dev
    # a = (LOWER_BOUND - MEAN) / STD_DEV
    # # b = (upper_bound - mean) / std_dev
    # b = (UPPER_BOUND - MEAN) / STD_DEV
    # # Create the truncated distribution object
    # dist = truncnorm(a, b, loc=MEAN, scale=STD_DEV)
    # # Draw a single random sample (or an array of samples with size=N)
    # random_number_scipy = dist.rvs(size=1)[0] 
    # return random_number_scipy