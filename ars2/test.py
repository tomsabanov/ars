import matplotlib.pyplot as plt
import numpy as np

# 100 linearly spaced numbers
x = np.linspace(0,np.pi,100)


A = 100
alpha = 0.5
tau = 0.2

Y = []
for v in x:
    val = A + (A*alpha - A) * (1-np.exp(-v/tau))
    Y.append(val)



# setting the axes at the centre
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('center')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

# plot the functions
plt.plot(x,Y, 'b', label='y=sin(x)')

plt.legend(loc='upper left')

# show the plot
plt.show()

