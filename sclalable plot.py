import matplotlib.pyplot as plt
import numpy as np

rank = np.array([2, 4, 8, 16, 32, 64, 128, 256])
time = np.array([1276.335, 641.806, 481.968, 247.320, 144.761, 61.528, 33.830, 40.692])
speed_up = time[0] / time
expected_speed_up = np.array([1, 2, 4, 8, 16, 32, 64, 64])
plt.figure()
plt.plot(rank, speed_up, label = "Actual speed up")
plt.plot(rank, expected_speed_up, label = "Expected speed up")
plt.xscale("log", base=2)
plt.yscale("log", base=2)
plt.xlabel("Rank number")
plt.ylabel("Speed up")

plt.legend()
plt.show()