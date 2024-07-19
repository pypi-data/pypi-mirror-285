# # %%
# '''
# Only to performs tests
# '''
# import os
# import sys
# import numpy as np
# sys.path.insert(0, os.path.join(os.getcwd(),r'..\src\experimentalTreatingIsiPol'))
# import matplotlib.pyplot as plt
# from main import MechanicalTestFittingLinear, MonteCarloErrorPropagation
# from main import plot_helper
# def createFakeExperimentalData(data, n):
#     y_data = data['Carga']

#     fig, ax = plt.subplots(figsize=(4,3))

#     for i in range(n):
#         r = np.random.rand()
#         mean = 0.01*(r-1)+0.01*(r)

#         Y_with_noise = y_data -y_data*(np.random.normal(mean,0.1,1))
#         plot_helper(ax, x=data['Extensometro'], y=Y_with_noise, label=f'Data {i}', xlabel=r'mm/mm', ylabel='Força', color='green', linewidth=1)
#     plot_helper(ax, x=data['Extensometro'], y=y_data, label=f'Data Original', xlabel=r'mm/mm', ylabel='Força', color='blue', linewidth=2)



# ClassInit = MechanicalTestFittingLinear('68FM100', archive_name=r'D:\Jonas\PostProcessingData\DataArquives\Specimen_RawData_1.csv')

# createFakeExperimentalData(ClassInit.rawdata,10)


# %%
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(),r'..\src\experimentalTreatingIsiPol'))

from main import MonteCarloErrorPropagation
import numpy as np


def density(m,r,t):
    return m/(np.pi*r**2*t)

measured_r = [10.01,10.02,10.00,10.00]
measured_t = [1.01,1.02,1.00,1.05]
measured_m = [15.50,5.35,1.44,15.42,1.44]

ClassInit = MonteCarloErrorPropagation(density, measured_m, measured_r, measured_t)


ClassInit.ax.set_title('Densidade calculada: ' + f'{ClassInit.f_mean:.2f}+/- {2*ClassInit.f_MC.std():.2f}')
# %%
