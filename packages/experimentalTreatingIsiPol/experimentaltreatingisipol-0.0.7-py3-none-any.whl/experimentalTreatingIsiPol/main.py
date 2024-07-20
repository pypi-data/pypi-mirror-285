# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as st
from scipy.optimize import curve_fit
from experimentalTreatingIsiPol.machines._68FM100 import _68FM100


blue_tonalities_options = [
    '#1f0794', 
    '#000080', 
    '#6476d1', 
    '#00008B', 
    '#003366', 
    '#191970', 
    '#0000CD', 
    '#27414a', 
    '#4B0082', 
    '#2f6b6b', 
    '#00688B', 
    '#483D8B', 
    '#4682B4', 
    '#708090', 
    '#4169E1', 
    '#778899', 
    '#7B68EE', 
    '#6495ED'
]


linestyles_options = [
    "-",    # solid
    "--",   # dashed
    "-.",   # dashdot
    ":",    # dotted
    " ",    # no line (blank space)
    "-",    # solid (thicker)
    (0, (1, 10)), # loosely dotted
    (0, (5, 10)), # loosely dashed
    (0, (3, 5, 1, 5)), # dashdotted
    (0, (3, 1, 1, 1)), # densely dashdotted
    (0, (5, 5)),  # dashed with same dash and space lengths
    (5, (10, 3)), # long dashes with offset
    (0, (3, 10, 1, 15)), # complex custom dash pattern
    (0, (1, 1)), # densely dotted
    (0, (1, 5)), # moderately dotted
    (0, (3, 1)), # densely dashed
    (0, (3, 5, 1, 5, 1, 5)), # dashdotdot
    (0, (3, 10, 1, 10, 1, 10)), # dashdashdash
]

marker_options = [
    ".",      # point
    ",",      # pixel
    "o",      # circle
    "v",      # triangle down
    "^",      # triangle up
    "<",      # triangle left
    ">",      # triangle right
    "1",      # tripod down
    "2",      # tripod up
    "3",      # tripod left
    "4",      # tripod right
    "s",      # square
    "p",      # pentagon
    "*",      # star
    "h",      # hexagon1
    "H",      # hexagon2
    "+",      # plus
    "x",      # x
    "D",      # diamond
    "d",      # thin diamond
]

def plot_helper(ax,x,y,label,xlabel,ylabel,color='blue', linestyle='-.', marker='<', markersize=1, linewidth=1,**kwargs):

    ax.plot(x,y, label = label, color = color, marker = marker, 
            markersize = markersize, 
            linestyle = linestyle,
            linewidth = linewidth,**kwargs)
    ax.grid()
    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return ax

def scatter_helper(ax,x,y,label, xlabel, ylabel,color='blue', marker='+', markersize=10, **kwargs):

    ax.scatter(x,y, label = label, color = color, marker = marker,
             s = markersize,
             **kwargs)
    ax.grid()
    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return ax

def several_plots_helper(ax,xs,ys,labels,xlabel,ylabel,colors: list | None = None, 
                         linestyles: list | None =None, markers : list | None = None, 
                         markersize=1, linewidth=1, 
                         **kwargs
                         ):
    '''
    Função para plotar diversos gráficos.
    '''
    if len(xs)!=len(ys):
        raise Exception('As dimensões das variáveis xs e ys devem ser iguais.')
    
    if len(labels)!=len(ys):
        raise Exception('A quantidade de labels deve ser igual à quantidade de pares.')
    

    if not (colors and markers and linestyles): 

        for each_x, each_y, each_label in zip(xs,ys,labels): 
            if len(each_x)>100:
                slice = int(len(each_x)/20)
                each_x=each_x[::slice]
                each_y=each_y[::slice]

            color = blue_tonalities_options[np.random.random_integers(0,17)]
            marker = marker_options[np.random.random_integers(0,17)]
            linestyle = linestyles_options[np.random.random_integers(0,17)]

            ax.plot(each_x,each_y, label = each_label, color = color, marker = marker, 
                    markersize = markersize, 
                    linestyle = linestyle,
                    linewidth = linewidth,**kwargs)

    else:
        for each_x, each_y, each_label,each_color, each_marker, each_linestyle in zip(xs,ys,labels,colors,markers,linestyles): 
            if len(each_x)>100:
                slice = int(len(each_x)/20)
                each_x=each_x[::slice]
                each_y=each_y[::slice]

            ax.plot(each_x,each_y, label = each_label, color = each_color, marker = each_marker, 
                    markersize = markersize, 
                    linestyle = each_linestyle,
                    linewidth = linewidth,**kwargs)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid()
    fig_obj = ax.get_figure()
    fig_height = fig_obj.get_figheight()
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -fig_height/20),
        ncol=3,
        framealpha=1,
        )
    
    return ax

def several_scatter_helper(ax,xs,ys,labels,xlabel,ylabel,colors: list | None = None, linestyles: list | None =None, markers : list | None = None, markersize=1, linewidth=1, **kwargs):
    '''
    Função para plotar diversos gráficos.

    PAREI AQUI
    '''
    if len(xs)!=len(ys):
        raise Exception('As dimensões das variáveis xs e ys devem ser iguais.')
    
    if len(labels)!=len(ys):
        raise Exception('A quantidade de labels deve ser igual à quantidade de pares.')
    
    ax.grid()

    if not (colors and markers and linestyles): 

        for each_x, each_y, each_label in zip(xs,ys,labels): 

            if len(each_x)>100:
                slice = int(len(each_x)/20)
                each_x=each_x[::slice]
                each_y=each_y[::slice]

            color = blue_tonalities_options[np.random.random_integers(0,17)]
            marker = marker_options[np.random.random_integers(0,17)]

            ax.scatter(each_x,each_y, label = each_label, color = color, marker = marker, 
                    s = markersize, 
                    **kwargs)

    else:
        for each_x, each_y, each_label,each_color, each_marker in zip(xs,ys,labels,colors,markers): 
           
            if len(each_x)>100:
                slice = int(len(each_x)/20)
                each_x=each_x[::slice]
                each_y=each_y[::slice]

            ax.scatter(each_x,each_y, label = each_label, color = each_color, marker = each_marker, 
                    s = markersize, 
                    **kwargs)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig_obj = ax.get_figure()
    fig_height = fig_obj.get_figheight()
    ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -fig_height/15),
        ncol=3,
        framealpha=1,
        )
    
    return ax


class MechanicalTestFittingLinear():
    '''
    Classe para determinar propriedades mecânicas em regimes lineares. Ela servirão para Moduli de Young e Cisalhamento. 
    '''
    def __init__(self, machineName: str, archive_name : str, linearRegionSearchMethod='Deterministic') -> None:
        self.rawdata = self.dataExtract(machineName=machineName, archive_name= archive_name, linearRegionSearchMethod=linearRegionSearchMethod)
        pass

    def _68FM100_Data_Aquisition(self, archive_name : str, linearRegionSearchMethod):
        '''
        Método para a leitura e aquisição de dados de ensaio efetuados na 68FM100
        '''
        machine  = _68FM100()
        raw_data = pd.read_csv(archive_name, sep=machine.column_delimitador, encoding_errors='backslashreplace', on_bad_lines='skip', skiprows=10, decimal=machine.decimal)
        raw_data.columns = [machine.colunas[0],machine.colunas[1],machine.colunas[2],machine.colunas[3]]
        i = self.__filterInitGraph(y=raw_data[machine.colunas[2]],linearRegionSearchMethod=linearRegionSearchMethod)
        x = raw_data[machine.colunas[3]]
        y = raw_data[machine.colunas[2]]
        x_linear = self.__selectGraphRange(x,i)
        y_linear = self.__selectGraphRange(y,i)

        a,b,root = self.__equationFit(x_linear, y_linear)
        self.plotData(x,y,x_linear,y_linear)
        self.plotComparisonExcludedData(x,y,x_linear,y_linear)

        print('a--->', a)
        print('b--->', b)
        print('root--->', root)

        new_x, new_y = self.__cut_garbage_data(x,y,x_linear,a,b,root)
        self.plotCleanedData(new_x, new_y)

        self.new_x = new_x # Salvando internamente os dados limpos (x)
        self.new_y = new_y # Salvando internamente os dados limpos (y)
        return raw_data
    
    def __equationFit(self, x_linear, y_linear):
        '''
        Retorna os coeficientes a, b, e a raiz (-b/a) de uma equaçãoo linear f(x)=ax+b
        '''
        def linear(x,a,b):
            return a*x+b

        popt,_ = curve_fit(linear, x_linear, y_linear)
        return tuple([popt[0],popt[1],-popt[1]/popt[0]])
    
    def __cut_garbage_data(self,x,y,x_linear,a,b,root):
        '''
        Método para cortar os dados iniciais do ensaio
        x -> Dados Originais (x)
        y -> Dados Originais (y)
        x_linear -> Conjunto do eixo x, dos dados originais, em que a informação é válida
        a,b -> Coef. das retas ajustadas na região linear
        root -> Raiz da eq. ajustada na parte linear
        '''

        x_cleaned = x[len(x_linear):len(x)] # Exclui os primeiros dados
        y_cleaned = y[len(x_linear):len(x)] # Exclui os primeiros dados
        x_init = np.linspace(root,x[len(x_linear)],20) # Array da raiz do gráfico até o início dos dados originais
        y_init = [a*x+b for x in x_init] # Y ajustado na parte linear
        
        new_x = list(x_init) + list(x_cleaned) 
        new_x = np.subtract(new_x,root) # descontando a raiz
        new_y = list(y_init) + list(y_cleaned)
        return new_x, new_y
    
    def __selectGraphRange(self, var, i):
        '''
        Método para retornar um range de dados, dado seu tamanho, e posição. 
        '''
        offset = int(len(var)/50)
        return var[offset*(i-1):offset+offset*(i-1)]

    def __filterInitGraph(self, y : pd.Series, linearRegionSearchMethod: str)->int:
        '''
        Recebe os dados de ensaios experimentais, e encontra a primeira região linear pela diminuição do desvio padrão da segunda derivada
        '''
        i=1
        y_current = self.__selectGraphRange(y,i)
        derivative = np.gradient(y_current)
        second_order_derivative = np.gradient(derivative)
        init_cov = np.std(second_order_derivative)
        cov = init_cov
        convergence_criteria = init_cov/5

        while(cov > convergence_criteria):
            i+=1
            y_current = self.__selectGraphRange(y,i)
            derivative = np.gradient(y_current)
            second_order_derivative = np.gradient(derivative)
            cov = np.std(second_order_derivative)
            if i>100:
                raise Exception('loop inf')

        return i         

    def __typeCheck(self, var, type_correct):
        '''
        Fun��o de apoio para checar se o tipo passo estão correto
        '''
        if type(var) != type_correct:
            raise Exception(f'O argumento machineName deve ser uma {type_correct}. Recebeu um {type(var)}')

    def dataExtract(self, machineName : str, archive_name : str, linearRegionSearchMethod : str)->pd.DataFrame:
        '''
        Funçãoo para obter, a parte de um tipo de máquina, identificado pelo nome, os dados brutos do ensaio.
        '''
        # Verificação dos argumentos
        self.__typeCheck(machineName, str)
        self.__typeCheck(archive_name, str)

        if machineName == '68FM100':
            return self._68FM100_Data_Aquisition(archive_name, linearRegionSearchMethod)
        
        raise Exception('Tipo de Máquina não encontrado')
    
    def MeasureYoungModulus(self,length : float,thickess : float,width : float):
        '''
        Método para medir o módulo de Young
        '''
        strain = np.divide(self.new_x, length)
        area = thickess*width
        stress =  np.divide(self.new_y, area)
        linear_region_strain =  strain[0:10] # Está hardcoded, talvez poderiámos pensar em alguma lógica para calcular o ponto final do cálculo
        linear_region_stress = stress[0:10]
        E,b,root=self.__equationFit(x_linear=linear_region_strain, y_linear=linear_region_stress)
        self.plotStressStrain(strain,stress,E)


    def plotComparisonExcludedData(self, x,y, x_linear,y_linear):
        '''
        Método comparar dados excluídos da análise
        '''
        fig, ax = plt.subplots(figsize=(6,3))
        ax = plot_helper(ax=ax, x = x[0:len(x_linear)], y=y[0:len(y_linear)], label='Dados Originais', ylabel='F', xlabel='mm')
        ax = plot_helper(ax=ax, x = x_linear, y=y_linear, label='Curva linear', ylabel='F', xlabel='mm', color='red')
        lim_sup_x = x[len(x_linear)] 
        lim_inf_x = x[0] 
        y_max= y[len(y_linear)]
        y_min= y[0]
        
        ax.arrow(x=lim_sup_x,y=y_min,dx=0,dy=(y_max-y_min)*1.2, color='orange')
        ax.arrow(x=lim_inf_x,y=y_min,dx=0,dy=(y_max-y_min)*1.2, color='orange')
        text_x_position = (lim_inf_x)*1.01
        text_y_position = y_max*1.3
        ax.text(text_x_position, text_y_position, r'Região excluída', fontsize=7, bbox={'facecolor': 'orange', 'alpha': 0.1, 'pad': 2})
        ax.legend(loc ='lower right')
        plt.show()

    def plotCleanedData(self, x,y):
        '''
        Método para plotar os dados limpos
        '''
        fig, ax = plt.subplots(figsize=(6,3))
        ax = plot_helper(ax=ax, x = x, y=y, label='Dados Ajustados', ylabel='F', xlabel='mm')    
        plt.show()

    def plotData(self,x,y, x_linear,y_linear):
        '''
        Método para graficar os dados originais e a parte linear
        '''
        fig, ax = plt.subplots(figsize=(6,3))
        ax = plot_helper(ax=ax, x = x, y=y, label='Dados Originais', ylabel='F', xlabel='mm')
        ax = plot_helper(ax=ax, x = x_linear, y=y_linear, label='Curva linear', ylabel='F', xlabel='mm', color='red')
        plt.show()

    def plotStressStrain(self,x,y,E):
        '''
        Método para graficar a curva de tensão e deformação

        TODO - generalizar para a função receber um eixo, assim ela pode receber diversos corpos de prova
        '''
        fig, ax = plt.subplots(figsize=(6,3))
        x_linear = np.linspace(0,0.02)
        y_linear = [E*x for x in x_linear]
        ax = plot_helper(ax=ax, x = x, y=y, label='Curva de tensão', ylabel=r'$\sigma_{x}$', xlabel=r'$\varepsilon \ \frac{mm}{mm}$')
        ax = plot_helper(ax=ax, x = x_linear, y=y_linear, label='Módulo ajustado', ylabel=r'$\sigma_{x} \ [MPa]$', xlabel=r'$\varepsilon \ \frac{mm}{mm}$', color=blue_tonalities_options[5])
        ax.text(x_linear[-1]*0.8,y_linear[-1]*0.3,fr'E={E:.2f} [MPa]',bbox={'facecolor': 'white', 'alpha': 1, 'pad': 3})
        plt.show()

class MonteCarloErrorPropagation():
    '''
    Classe para calcular a propagação de erros mediante uma simulação de Monte Carlo

    Ex.:

    def density(m,r,t):
        return m/(np.pi*r**2*t)

    measured_r = [10.01,10.02,10.00,10.05]
    measured_t = [1.01,1.02,1.00,1.05]
    measured_m = [10.50,10.35,10.44,10.42]

    MonteCarloErrorPropagation(density, measured_r,measured_t,measured_m)

    '''

    def __init__(self, f : any, *measured_vars):
        self.__computeError(f, *measured_vars)
        self.__plotDistribution()

        pass

    def __computeError(self,f, *params):
        '''
        
        '''
        array_distributions = []

        for each_param in params:
            var = np.array(each_param)
            var_MC = var.mean()+var.std()*np.random.normal(size=10000)
            array_distributions.append(var_MC)

        self.f_MC : np.array = f(*array_distributions)
        self.f_mean = self.f_MC.mean()
        self.f_max = self.f_MC.mean() + 2*self.f_MC.std()
        self.f_min = self.f_MC.mean() - 2*self.f_MC.std()

    def __plotDistribution(self):
        
        graph_limit_min = min(self.f_MC)
        graph_limit_max = max(self.f_MC)
        confidence_inf = self.f_MC.mean()-2*self.f_MC.std()
        confidence_sup = self.f_MC.mean()+2*self.f_MC.std()

        y_confidence_lenght = len(self.f_MC[self.f_MC>confidence_sup])
        fig,ax = plt.subplots(figsize=(4,3))
        ax.hist(self.f_MC, bins=np.linspace(graph_limit_min,graph_limit_max))
        ax.plot([confidence_inf,confidence_inf],[0, y_confidence_lenght], color='orange')
        ax.plot([confidence_sup,confidence_sup],[0,y_confidence_lenght],color='orange')

        self.ax = ax

if __name__ == '__main__':
    classInit =  MechanicalTestFittingLinear('68FM100', archive_name=r'D:\Jonas\PostProcessingData\DataArquives\Specimen_RawData_1.csv')
    classInit.MeasureYoungModulus(50,1,12)    


# %%
# %%

