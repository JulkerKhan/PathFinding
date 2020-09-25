import subprocess
from time import time

from greedijk import greedijk

FILENAME = '200.in'

times = list()

# for _ in range(100):
while True:
    # generate new random input
    subprocess.check_call('python genin.py'.split())
    start = time()
    greedijk(FILENAME)
    # times.append(time() - start)
    if time() - start > 0.42:
        break
