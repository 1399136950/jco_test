import numpy as np
import matplotlib.pyplot as plt

xx = np.linspace(0, 12, 100)
# Y=3.0389490329777X + 9.540521796842

yy = np.linspace(0, 12, 100)
plt.figure(figsize=(8,4))
plt.plot(xx,yy,color="red",linewidth=2)



plt.legend()
plt.show()
