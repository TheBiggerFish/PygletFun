import torch
from pyperlin import FractalPerlin2D
import matplotlib.pyplot as plt

shape = (1,1024,1024) #for batch size = 1 and noises' shape = (1024,1024)
factors = [.5**i for i in range(8)] #for persistence = 0.5
# g_cuda = torch.Generator(device='cuda') #for GPU acceleration
g_cuda = torch.Generator(device='cpu')

clouds_resolutions = [(2**i,2**i) for i in range(1,7)] #for lacunarity = 2.0
clouds_factors = [.5**i for i in range(6)] #for persistence = 0.5
clouds = FractalPerlin2D(shape, clouds_resolutions, clouds_factors, generator=g_cuda)().cpu().numpy()[0]

fire_resolutions = [(2**i,4**i) for i in range(1,4)] #for lacunarity = 2.0 and 4.0
fire_factors = [.5**i for i in range(3)] #for persistence = 0.5
fire = FractalPerlin2D(shape, fire_resolutions, fire_factors, generator=g_cuda)().cpu().numpy()[0]

fig = plt.figure(figsize=(10,5))

ax1 = fig.add_subplot(121)
ax1.set_axis_off()
ax1.set_title('Clouds')
ax1.imshow(clouds, vmax=1.2, cmap=plt.get_cmap('Blues'))

ax2 = fig.add_subplot(122)
ax2.set_axis_off()
ax2.set_title('Fire')
ax2.imshow(fire, vmax=.3, cmap=plt.get_cmap('YlOrBr'))

fig.show()
input()