import time

import numpy as np
import ray

ray.init()

dataset = ray.data.range_tensor(20000, shape=(2, 2))

dataset.filter(np.ones((dataset.count(), )))
print(dataset)
print(dataset.materialize())