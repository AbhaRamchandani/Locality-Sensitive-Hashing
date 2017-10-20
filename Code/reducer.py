#!/local/anaconda/bin/python
# IMPORTANT: leave the above line as is.

import numpy as np
import sys
import random

last_key = None
key_count = 0

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
        self.a = np.random.randint(100000, size=NUM_ROWS)
        self.b = np.random.randint(100000)
        self.m = 3367900313 
        
    def get(self, array): 
        return (np.sum(np.multiply(self.a, array)) + self.b) % self.m
        
   
class Video: 
    def __init__(self, ID, features): 
        self.ID = ID
        self.features = set(features)
    
    def __eq__(self, other): 
        return (isinstance(other, self.__class__)
            and self.features == other.features)
                
    def JaqcuardSim(self, other): 
        n = self.features.intersection(other.features)
        u = self.features.union(other.features)
        return float(len(n)) / float(len(u))
        
    def getHash(self, permutations, hashFunctions): 
        # Compute the signature
        signature = np.zeros(NUM_BANDS * NUM_ROWS)
        for numP, p in enumerate(permutations): 
            for i in range(MAX_FEATURE + 1): 
                if p.get(i) in self.features: 
                    signature[numP] = i 
                    break
                    
        # Compute the hash values of the bands 
        hashes = np.zeros(NUM_BANDS, dtype=np.int32)
        for b in range(NUM_BANDS): 
            beginRow = b * NUM_ROWS
            endRow = beginRow + NUM_ROWS
            hashes[b] = hashFunctions[b].get(signature[beginRow:endRow])
        
        return hashes



def printDuplicates(videos):
    # Print pairs that have an actual Jacquard similarity that is at least 
    # 0.9  
    for i1 in range(len(videos)): 
        v1 = videos[i1]
        for i2 in range(i1+1, len(videos)): 
            v2 = videos[i2]
            if v1.JaqcuardSim(v2) >= 0.9: 
                # The two videos are similar enough. 
                # Ensure that it is printed only once by only printing
                # if B = minimum index in hash array where the two values
                # are equal
                h1 = v1.getHash(permutations, hashFunctions)
                h2 = v2.getHash(permutations, hashFunctions)
                for b in range(len(h1)): 
                    if h1[b] == h2[b]: break
                if b != B: continue
                print "%d\t%d" % (min(v1.ID, v2.ID), 
                                  max(v1.ID, v2.ID)) 



if __name__ == "__main__":
    videos = []

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
        # Parse the key-value pair
        line = line.strip()
        key, value = line.split("\t")
        
        # Parse the value
        value = value.strip()
        ID = int(value[6:15])
        features = np.fromstring(value[16:], sep=" ", dtype=np.uint32)

        if last_key is None:
            last_key = key
            B, HASH = key.split(":")
            B = int(B)
            HASH = int(HASH)

        if key == last_key:
            videos.append(Video(ID, features))
            B, HASH = key.split(":")
            B = int(B)
            HASH = int(HASH)
        else:
            # Key changed (previous line was k=x, this line is k=y)
            printDuplicates(videos)
             
            B, HASH = key.split(":")
            B = int(B)
            HASH = int(HASH)
            
            videos = [ Video(ID, features) ]
            last_key = key

    if len(videos) > 0:
        printDuplicates(videos)
