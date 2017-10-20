#!/local/anaconda/bin/python
# IMPORTANT: leave the above line as is.

import numpy as np
import sys
import random

# Features are in [0, NUM_FEATURES]
MAX_FEATURE = 20000

# Number of bands 
NUM_BANDS = 8
# Number of rows per band
NUM_ROWS = 2
# Number of hash functions
NUM_HASHFUNS = NUM_BANDS * NUM_ROWS
assert (NUM_HASHFUNS <= 1024)


class PseudoPermutation: 
    def __init__(self): 
        self.a = random.randint(0, 1000000)
        self.b = random.randint(0, 1000000)
        
    def get(self, n): 
        return (self.a * n + self.b) % (MAX_FEATURE + 1)
        
class RowHashFunction: 
    """ The hash function for the rows """
    def __init__(self): 
        self.a = np.random.randint(10000, size=NUM_ROWS)
        self.b = np.random.randint(10000)
        self.m = 3367900313 
        
    def get(self, array): 
        return (np.sum(np.multiply(self.a, array)) + self.b) % self.m
        
        
class Video: 
    def __init__(self, ID, features): 
        self.ID = ID
        self.features = set(features)
    
    def getHash(self, permutations, hashFunctions): 
        # Compute the signature
        signature = np.zeros(NUM_BANDS * NUM_ROWS)
        for numP, p in enumerate(permutations): 
            for i in range(MAX_FEATURE + 1): 
                if p.get(i) in self.features: 
                    signature[numP] = i 
                    break
                    
        # Compute the hash values of the bands 
        hashes = np.zeros(NUM_BANDS)
        for b in range(NUM_BANDS): 
            beginRow = b * NUM_ROWS
            endRow = beginRow + NUM_ROWS
            hashes[b] = hashFunctions[b].get(signature[beginRow:endRow])
        
        return hashes
                

if __name__ == "__main__":
    # VERY IMPORTANT:
    # Make sure that each machine is using the
    # same seed when generating random numbers for the hash functions.
    np.random.seed(seed=42)
    random.seed(42)

    # Generate one random permutation for every hash function
    permutations = [PseudoPermutation() for _ in range(NUM_HASHFUNS)]
    
    # Generate one hash function for each band
    hashFunctions = [RowHashFunction() for _ in range(NUM_BANDS)]
    
    for line in sys.stdin:
        # Parse line
        line = line.strip()
        ID = int(line[6:15])
        features = np.fromstring(line[16:], sep=" ", dtype=np.uint32)
        video = Video(ID, features)
        
        # Output one tuple for each band with key=<band:hashValue> and 
        # value=>same as input>
        for band, hval in enumerate(video.getHash(permutations, hashFunctions)): 
            print "%d:%d\t%s" % (band, hval, line)
        
        
        
        
