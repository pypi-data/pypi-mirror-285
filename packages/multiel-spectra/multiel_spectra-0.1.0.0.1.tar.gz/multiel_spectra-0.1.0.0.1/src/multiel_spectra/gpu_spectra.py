import spekpy as sp 
import larch 
from larch.xray import * 
# import torch study how an optional torch import will import torch
import skbeam
from skbeam.core.constants import XrfElement
from skbeam.core.fitting import gaussian
import scipy 
from scipy.interpolate import interp1d
import scipy 
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import torch 
from multiel_spectra import Primary_gen
from multiel_spectra.src.multiel_spectra.XRF_utils import *
import time
import gc
#peaks_dic example {'Na_ll': 0.0304,...}

air_density = material_get("air")[1]

####################################################################################################
#####################################################################################################
# OPTIZIMIZED PARALLEL SPECTRA CREATION USING TORCH
#########################################################################################################
#################################################################################################################
#-----------------------------------------------------------------------------------------------------


# AIR mass coeficient as tensor: 

# air_mu = torch.tensor(material_mu("air",  np.arange(0,30,0.1)*1000 , air_density, kind = "photo")).cuda()

# Indexing reduced elements list and inverse:

#numbers (idxs) as keys, elements as values 
num_to_el = dict(zip(np.arange(len(reduced_list)), reduced_list))

#elements as keys, numbers (idxs) as values
el_to_number = dict(zip(reduced_list, np.arange(len(reduced_list))))

#-----------------------------------------------------------------------------------------------
#  Changes In the peaks dic: 

#we get the elements 
peaks_dic_el =  [key.split('_')[0] for key in peaks_dic.keys()]

# we transform the elements into their indices
peaks_dic_n = [el_to_number[el] for el in peaks_dic_el]

#we make it a torch tensor 
peaks_dic_ncpu = torch.tensor(peaks_dic_n)

#send the tensor to the GPU 
peaks_dic_n = torch.tensor(peaks_dic_n).cuda() #+ 1

#Nested dictionary with all elements, each having a list of the names of the lines and a tensor of the energies of those lines

lin_e_dic = {} 
for elem in reduced_list: 
    lin = list(filter(lambda x: x[1] != 0, XrfElement(elem).emission_line.all)) #convertir lista en torch type.
    lines, ens , pos  = [], [], []
    j = 0 
    for i in lin:
        lines.append(i[0])
        ens.append(i[1])
        pos.append(j)
        j +=1 

    el_d = {"lines": lines, "energies" :torch.tensor(ens), "pos" : dict(zip(lines, pos))   }
    # print(el_d)
    lin_e_dic[elem] = el_d

# Example of this dictionary
# {'O': {'lines': ['ka1', 'ka2', 'ka3'],
#   'energies': tensor([0.5249, 0.5249, 0.5035]),
#   'pos': {'ka1': 0, 'ka2': 1, 'ka3': 2}},
#  'F': {'lines': ['ka1', 'ka2', 'ka3'],
#   'energies': tensor([0.6768, 0.6768, 0.6514]),
#   'pos': {'ka1': 0, 'ka2': 1, 'ka3': 2}},
#......}

# Standard Primary Spectra

Prim, brems = Primary_gen(30, 46, 0.1, "casim", "nist", 1, 9, "Mo", [('Be',0.127),('Air',10)])

# tensor containing all the cross sections (of the 25 IUPAC lines) for all elements for each energy value of the Primary spectrum
css_tens  = torch.zeros((len(reduced_list), len(Prim[0]),25))

# tensor containing all the energies for all elements for all the 25 IUPAC Lines that give the cross sections in css_tens
#energies will be repeated for the second dimension in this tensor 
cens_tens = torch.zeros((len(reduced_list),len(Prim[0]),25))

#we loop on the selected elements
for i in range(len(reduced_list)):
    #we obtian the energies and line name 
    a, lin = zip(* XrfElement(reduced_list[i]).emission_line.all)
    
    #we loop on the primary spectrum 
    for en,j in zip(Prim[0],range(len(Prim[0]))):
        #all the cross sections for an element in the energy range
        rs =  XrfElement(reduced_list[i]).cs(en).all    
        r_names, cs = zip(*rs)
        
        # we add the cross section in the corresponding position 
        css_tens[i,j,:] = torch.tensor(cs)

        # we add the energy in the corrisponding position
        cens_tens[i,j,:] = torch.tensor(lin)

# css_tens.size() = torch.Size([41, 580, 25])
# cens_tens.size() = torch.Size([41, 580, 25])
# The 580 entries in  cens_tens are the same, but the tensor is build like this for 
# dimension compatibility in future comptutations

# Dim 0 [41]: each of the selected elements 
# Dim 1 [580]: Primary Spectrum divisions on energy 
# Dim 2 [25]: 25 IUPAC LINES ('ka1','ka2','ka3','kb1','kb2','kb3','kb4','kb5','la1','la2','lb1','lb2','lb3','lb4','lb5','lg1','lg2','lg3','lg4','ll','ln','ma1','ma2','mb','mg')


##################################################################################################
# TENSORIAL FUNCTIONS USING TORCH 
###################################################################################################
# All the process is created and fixed for an energy bin of 300 in the 0-30 KeV range 
# x = torch.arange(0,30,0.1)

#----------------------------------------------------------
#Constants 

#(2 pi)^0.5 constant
s2pi = torch.sqrt(torch.tensor(2*torch.pi))

#----------------------------------------------------------

def Narea_t(array):
    """ Normalizes the values of an array to sum to 1, if the tensor has more than 1 dimension 
    then normalization is over the last dimension. If all the elements are 0 the normalization 
    may give an error.
    
    It is the same as Narea in the normal module but adapted to work with tensors.

    Args:
        array (torch.Tensor): A torch array to be normalized.

    Returns:
        torch.Tensor: The same normalized array.
    """

    tam = array.size()
    if len(tam) > 1 : 
        norm_a = array/torch.max(array, dim = -1 ).values.unsqueeze(-1) #mirar que pasa en 3 dim 
        norm_a = norm_a/torch.sum(norm_a, dim = -1 ).unsqueeze(-1)
    else: 
        norm_a = array/torch.max(array) 
        norm_a = norm_a/torch.sum(norm_a)
    return norm_a

def s_gauss(x, area, center, sigma):
    """1 dimensional gaussian
    Parameters
    ----------
    x : array
        independent variable
    area : float
        Area of the normally distributed peak
    center : float
        center position
    sigma : float
        standard deviation
    """
    return ((1/area) *torch.exp(-1 * (1.0 * x - center.item()) ** 2 / (2 * sigma ** 2)))

def escape_peaks_t(spectra,gauss): # he quitado c porque no lo he usado, podria usarlo para seleccionar solo algun pico de algun elemento.
    
    """
    This function simulates the escape peaks of a Silicon detector, specifically the Ka1 line at 1.73998 KeV.

    A preselection of the peaks is applied, and then one of these selected peaks is randomly chosen
    to apply the escape function on it. 

    This function is similar to the one in the main module but adapted to work with tensors in batches, hence
    having one more dimension.

    Args:
        spectra (torch.Tensor): The input spectra tensor to be processed.
        gauss (torch.Tensor): A tensor of Gaussian standard deviations for each batch.

    Returns:
        torch.Tensor: The spectra tensor with the escape peaks simulated.
    """
    import scipy 
    peaks, prominences, proms, x, area, N, proms_t, peaks_it, a, perc = None, None,  None, None,  None, None,  None, None,  None, None    
    x = torch.arange(0,30,0.1)
    area = 0.05 * torch.sqrt(torch.tensor(2 * torch.pi)).cuda().detach()
    for i in range(spectra.size(0)) :
        std = gauss[i].item()
        area = std* torch.sqrt(torch.tensor(2 * torch.pi)).cuda().detach()
        peaks = scipy.signal.find_peaks(spectra[i].cpu().detach().numpy(), prominence = torch.max(spectra[i]).cpu().detach().numpy()/15)
        prominences = sorted((zip(peaks[1]["prominences"], peaks[0])))
        if len(prominences) > 0: 
            
            proms = list(zip(*prominences))[0] #peak prominence
            peaks_i = list(zip(*prominences))[1] #peak index, estan ordenadas de menor a mayor
            N = round(0.6*len(proms)/2) #numero de elementos que se cogen
            proms_t = torch.flip(torch.tensor(proms), dims = [0]) #ahora si ordenadas por importancia
            peaks_it = torch.flip(torch.tensor(peaks_i), dims = [0])
            a = torch.randperm(round(len(proms_t)/2))[:N]
            proms_t = proms_t[a]
            peaks_it = peaks_it[a]
            peaks_it = peaks_it[x[peaks_it] > 1.75]
            if peaks_it.numel()!=0: 
                for peak in peaks_it: 
                    # print("Escape peak a " ,x[peak])
                    perc =  torch.randint(low = 1,high = 15, size =  (1,))/100
                    spectra[i] -= s_gauss(x.cuda().detach(), area, x[peak].cuda().detach(), std).cuda().detach()*perc.cuda().detach() * spectra[i][peak]
                    spectra[i] += s_gauss(x.cuda().detach(), area*2, (x[peak]-1.73998).cuda().detach(), std*2).cuda().detach()*perc.cuda().detach() * spectra[i][peak]
    
    del peaks, prominences, proms, x, area, N, proms_t, peaks_it, a, perc
    
    return spectra.cuda().detach()

def sum_peaks_t(spectra,gauss):
    """
    This function sums two peaks (simulatinng their simultaneous arrival at the detector),
    taking two lines from two elements and summing them to create another peak.

    Args:
        spectra (torch.Tensor): The input spectra tensor to be processed.
        gauss (torch.Tensor): A tensor of Gaussian standard deviations for each batch.

    Returns:
        torch.Tensor: The spectra tensor with the peaks summed.
    """
    import scipy 
    peaks, prominences, proms, x, area, N, proms_t, peaks_it, a, perc = None, None,  None, None,  None, None,  None, None,  None, None    
    x = torch.arange(0,30,0.1)
    area = 0.05 * torch.sqrt(torch.tensor(2 * torch.pi)).cuda().detach()

    for i in range(spectra.size(0)) :
        std = gauss[i].item()
        area = std * torch.sqrt(torch.tensor(2 * torch.pi)).cuda().detach()
        peaks = scipy.signal.find_peaks(spectra[i].cpu().detach().numpy(), prominence = torch.max(spectra[i]).cpu().detach().numpy()/15)
        prominences = sorted((zip(peaks[1]["prominences"], peaks[0])))
        if len(prominences) > 0: 
            proms = list(zip(*prominences))[0] #peak prominence
            peaks_i = list(zip(*prominences))[1] #peak index, estan ordenadas de menor a mayor
            N = round(0.6*len(proms)/2) #numero de elementos que se cogen
            proms_t = torch.flip(torch.tensor(proms), dims = [0]) #ahora si ordenadas por importancia
            peaks_it = torch.flip(torch.tensor(peaks_i), dims = [0])
            a = torch.randperm(round(len(proms_t)/2))[:N]
            proms_t = proms_t[a]
            peaks_it = peaks_it[a]
            if len(peaks_it)>1: 
            # print("mas de dos picos")
                for i in range(len(peaks_it)-1):
                    pos1 = peaks_it[i]
                    pos2 = peaks_it[i+1]
                    # print(" Picos sumados" ,x[pos1], x[pos2])
                    y_alt = spectra[i][pos1]
                    perc =  torch.randint(low = 1,high = 15, size =  (1,))/100
                    spectra[i] -= s_gauss(x.cuda().detach(), area, x[pos1].cuda().detach(), std).cuda().detach()*perc.cuda().detach() * y_alt *perc.cuda().detach()/2
                    spectra[i] -= s_gauss(x.cuda().detach(), area, x[pos2].cuda().detach(), std).cuda().detach()*perc.cuda().detach() * y_alt *perc.cuda().detach()/2

                    spectra[i] += s_gauss(x.cuda().detach(), area*2, x[pos1].cuda().detach() + x[pos2].cuda().detach(), std*2).cuda().detach()*perc.cuda().detach() * y_alt

    del peaks, prominences, proms, x, area, N, proms_t, peaks_it, a, perc
    return spectra.cuda().detach()

def decalibration_t(spectra):
    """
    This function applies a decalibration to the input spectra. The decalibration is simulated by
    introducing random shifts and distortions to the energy axis (up to quadratic).

    Args:
        spectra (torch.Tensor): The input spectra tensor to be decalibrated.

    Returns:
        torch.Tensor: The decalibrated spectra tensor.
    """
    x = torch.arange(0, 30, 0.1)
    a = torch.tensor(np.random.uniform(-0.03, 0.03))
    b = torch.tensor(np.random.uniform(-0.03, 0.03))
    c = torch.tensor(np.random.uniform(-0.05, 0.05) * 10**(-3))
    x_tr = a + (1 + b) * x + c * x**2
    decal = interp1d(x_tr, spectra.cpu(), bounds_error=False, fill_value=0)
    return torch.tensor(decal(torch.tensor(x))).cuda().detach()

copia_inter = interp1d(x_c, y_c, bounds_error = False, fill_value = 0 )
eff_inter = torch.tensor(copia_inter(torch.arange(0,30,0.1)))

def sigmoid_t(x, a, b):
    """
    This function computes a modified sigmoid function.

    Args:
        x (torch.Tensor): The input tensor.
        a (torch.Tensor or float): The scaling factor for the input.
        b (torch.Tensor or float): The scaling factor for the exponent term.

    Returns:
        torch.Tensor: The result of applying the sigmoid function to the input tensor.
    """
    return 1/(1 + b*torch.exp(-x*a)) 

def detector_eff_t(spectra):
    """
    This function simulates the efficiency window of a XRF detector.

    Args:
        spectra (torch.Tensor): The input spectra tensor to be modified by the detector efficiency.

    Returns:
        torch.Tensor: The spectra tensor after applying the detector efficiency.
    """

    alpha = torch.tensor(np.random.uniform(low = 0.01 , high = 40 ))# de vez en cuando podria dar un uno y un 0, que es como no tener eficiencia. 
    beta = torch.tensor(np.random.uniform(low = 0.01 , high = 40))
    n =  torch.randint(low = 1,high = 50, size =  (1,))
    new_eff = torch.zeros((300))
    if n!=0: 
        new_eff[n:] = eff_inter[:-n]
    else: 
        new_eff = eff_inter
   
    eff = torch.tensor(sigmoid_t(new_eff, alpha,beta)).cuda().detach()

    return eff * spectra


def q_creat(element,prop): 
    """
    This function creates a list of mass attenuation coefficients for given elements and their properties.

    Args:
        element (list or tensor): A list or tensor of element indices. (is it a list ?? or just 1 )
        prop (list or tensor): A list or tensor of properties corresponding to the elements.

    Returns:
        torch.Tensor: A tensor of mass attenuation coefficients for the elements.

    """

    # give the index and get the element name
    elem =  num_to_el[element]
    z = zip(elem, prop)
    mus = [material_mu(elem, np.arange(0,30,0.1)*1000, XrfElement(elem).density,  kind = "photo")* XrfElement(elem).density*0.5*p*10**(-4) for element,p in z]
    return torch.tensor(mus)

def density(el):
    """
    This function retrieves the density of a given element.

    Args:
        el (int or list): The index or list of indices of the element(s).

    Returns:
        float or list: The density of the element(s).
    """

    # give the index and get the element name
    elem =  num_to_el[el]
    return  XrfElement(elem).density 

def mus(el,dens): 

    """
    This function calculates the mass attenuation coefficients for a given element and density.

    Args:
        el (int or list): The index or list of indices of the element(s).
        dens (float): The density of the element.

    Returns:
        numpy.ndarray: The mass attenuation coefficients for the element over a range of energies.
    """

    elem = num_to_el[el]
    return material_mu(elem, np.arange(0,30,0.1)*1000, dens,  kind = "photo")

# """
#     Interesa solo la absorción por lo que no uso el componente fotoelectrico.
#     Se devuelve solo aquello transmitido no lo que excita

#     la lista de las proporciones de los elementos tiene que ser con todos los elementos, es decir, la mayoria 0 excepto algunos, 
#     hacer en manera random el orden de los estratos. Porque de momento están ordenados por Z. 

#     """

def multigen_opt(els, Prim_s, cens_tens, css_tens):
    """
    Generates synthetic spectra by simulating the absorption effects of multiple elements in various proportions.

    This function calculates the transmitted spectra through different layers of materials, each composed of single elements
    in specified proportions. The simulation includes the effects of material density and absorption coefficients.
    The resulting spectra account for attenuation through air and are adjusted for random noise in element distributions and Gaussian
    broadening.

    Args:
        els (torch.Tensor): Tensor of element indices.
        Prim_s (list or tensor): Primary spectrum information.
        cens_tens (torch.Tensor): Tensor containing center values.
        css_tens (torch.Tensor): Tensor containing cross-section values.

    Returns:
        tuple: Containing the following tensors:
            - air_spectra (torch.Tensor): The spectra after applying air attenuation.
            - peaks_pos (torch.Tensor): Tensor indicating the positions of peaks.
            - c (torch.Tensor): The tensor of element proportions.
            - std (torch.Tensor): The standard deviations used in the Gaussian distribution.
    """
    
    mask, mask_non0,n,peaks_pos, column, mask_col,d1,d2,low,high,sig,sums,factors = None, None, None, None, None,None, None, None,None, None, None,None, None 
    air_z, air_f, q_air, summed_f, summed_qs,qs, vec_el, props, dens, muss, fact, q, f1,f2 = None, None, None, None, None, None,None, None, None,None, None, None,None, None 
    std,area, cs, centers, new_x, posi, x,Prim_y  = None, None, None, None, None, None , None, None
    
    air_mu = torch.tensor(material_mu("air",  np.arange(0,30,0.1)*1000 , air_density, kind = "photo")).cuda().detach()

    mask = torch.full((els.size(0),41), True)
    mask = mask.scatter_(1, els, False).cuda().detach()
    c = torch.rand((els.size(0), len(reduced_list))).cuda().detach()
    c = c/torch.sum(c, dim = 0 )
    c[mask] = 0
    mask_non0 = ~ mask
    c = Narea_t(c)
    n = torch.masked_select(c, mask_non0).view(c.size(0), -1).cuda().detach()
    peaks_pos = torch.zeros((els.size(0) ,len(peaks_dic)))
    for col in range(els.size(0)):
        column = els[col,:].cuda().detach()
        mask_col = torch.isin(peaks_dic_n, column).cuda().detach()
        peaks_pos[col,: ][mask_col ] = 1  

    d1, d2 = els.size() 
    posi = torch.arange(d2).repeat(d1, 1).cuda().detach()
    low = 0.02
    high = 0.2

    sums = torch.empty((d1,d2, 300)).cuda().detach()
    factors = torch.empty((d1,d2)).cuda().detach()
    qs = torch.empty((d1,d2, 300)).cuda().detach() #hay uno para cada energia. 
    x = torch.arange(0,30,0.1).cuda().detach()
    
    std = (torch.rand(d1) * (high - low) + low).cuda().detach()
    s2pi = torch.sqrt(torch.tensor(2*torch.pi)).cuda().detach()

    Prim_y = torch.tensor(Prim_s[1]).unsqueeze(0).unsqueeze(-1).cuda().detach()

    for i in range(d1):# si invierto el orden de esto puedo hacer que se sumen al anterior 

        vec_el = els[i].clone()
        props = n[i].clone().cuda().detach()
        dens = list(map(lambda x: density(x.item()), vec_el))
        muss = torch.tensor(list(map( lambda x,y: mus(x.item(),y), vec_el, dens))).cuda().detach()
        fact = torch.tensor( torch.tensor(dens).cuda().detach()*props*10**(-4)).cuda().detach()  #should be a vector of dim = d2
        q = muss*fact[:,None]*10**(-4)

        sig = std[i]
        area = sig * s2pi
        cs = css_tens[vec_el].unsqueeze(-1)
        new_x = x.repeat(cs.size())
        centers = cens_tens[vec_el].unsqueeze(-1)
        #centers + noise ??? con un noise de 0.001 keV approx más o menos 
        sums[i,:,:] = torch.sum(torch.sum((1/area)*torch.exp(-1 * ( ( new_x.cuda().detach() - centers.cuda().detach())** 2)/ (2 *sig** 2))*cs.cuda().detach(), dim = 2)*Prim_y, dim = 1)

        qs[i,:,:] = q
        factors[i,:] = fact  

    final_spectra = torch.zeros((d1,d2,300))

    if d2 > 1: 

        f1, f2 = factors.size()
        summed_f = torch.zeros((f1,f2)).cuda()
        summed_qs = torch.zeros((f1,f2,300)).cuda()    
        for i in range(f2): #no pogo el -1 porque a pesar de que la ultima fila no esta sumada tiene que trasferirse a summ
            summed_f[:,i] = torch.sum(factors[:,i:], dim = 1)
            summed_qs[:,i,:] = torch.sum(qs[:,i:,:], dim = 1)
            
        # if torch.isnan(summed_f).any(): 
        #     print("There is a nan in summed_f", summed_f)
        # if torch.isnan(summed_qs).any(): 
        #     print("There is a nan in summed_qs", summed_qs)


        last_row = Narea_t(sums[:,-1,:]) *n[:,-1].unsqueeze(-1) #ultimo elemento 
        final_spectra =  Narea_t( sums*summed_f.unsqueeze(-1)*((1-torch.exp(-summed_qs))/summed_qs))*n.unsqueeze(-1)
        final_spectra[:,-1,:] = last_row
        final_spectra = torch.sum(final_spectra, dim = 1)
#         if torch.isnan(final_spectra).any(): 
#             print("There is a nan in final_spectra")
#             for w in range(d1):
#                 if (torch.isnan(final_spectra[w])).any():
#                     torch.set_printoptions(threshold=torch.inf)
#                     print("Nan is at row", w)
#                     print(sums[w])
#                     print(els[w])
#                     indx_0 = [(sums[w][j]==0).all().cpu() for j in range(sums[w].size(0))]
#                     print(indx_0)
#                     pos = np.where(indx_0)[0]
#                     print(els[w][pos])
#                     pdb.set_trace()
   
#                     torch.set_printoptions(edgeitems=3, threshold=1000, linewidth=75, sci_mode=False)
            
    else:
        
        final_spectra = Narea_t(sums)*n.unsqueeze(-1)
        final_spectra = final_spectra.squeeze(dim = 1)

    air_z = torch.rand(1).cuda().detach()
    q_air = air_mu*air_z*air_density
    air_spectra = Narea_t( final_spectra*air_z*air_density*((1-torch.exp(-q_air))/q_air).unsqueeze(0) )
    if torch.isnan(air_spectra).any(): 
            print("There is a nan in air_spectra")
            
    
    del mask, mask_non0,n, column, mask_col,d1,d2,low,high,sums,factors
    del air_z, air_f, q_air, summed_f, summed_qs,qs, vec_el, props, dens, muss, fact, q, f1,f2
    del final_spectra, x, area,sig, cs, centers, new_x, posi, Prim_y
    
    return air_spectra, peaks_pos, c, std


def process_spectra(train_size, batch_size, path, n_min = 3, n_max = 13, new_p_rate = 100,decal_rate = 3):
    """
    Generates and processes spectra, saving the results to specified files.

    Parameters:
    - train_size (int): Total number of spectra batches to generate. The total number of spectra is train_size * batch_size.
    - batch_size (int): Number of samples in each batch.
    - path (str): Directory path to save the generated spectra and metadata.

    - n_min (int, optional): Minimum number of elements for random selection. Default is 3.
    - n_max (int, optional): Maximum number of elements for random selection. Default is 13.
    - new_p_rate (int, optional): Rate at which a new primary spectrum is generated. Default is 100.
    - decal_rate (int, optional): Rate at which decalibration is applied. Default is 3.

    Returns:
    None
    """
    a, spec, peaks, c, noise, brems_choice, char_choice, brem, char = None, None,  None, None, None, None, None, None, None
    final_d_choice, h_final_d, final_d,prop, new_spec, Primary = None, None,  None, None, None, None

    decal = True
    x = torch.arange(0, 30, 0.1).cuda().detach()
    start2 = time.perf_counter()

    for j in range(0, train_size):
        gc.collect()
        print(f"\r{j} of {train_size}")
        start = time.perf_counter()
        
        if (j % new_p_rate == 0) and (j != 0):
            bn, o = 0.1, 1
            k = 30
            th = np.random.randint(low=30, high=60)
            be_width = np.random.uniform(low=0, high=0.4)
            air_width = np.random.uniform(low=0, high=15)
            target_i = np.random.randint(low=0, high=3)
            mu_i = np.random.choice(range(2), replace=False)
            phys_i = np.random.randint(low=0, high=2) if target_i > 0 else np.random.randint(low=0, high=len(physics))
            mas = np.random.randint(low=1, high=20)
            f = np.random.randint(0, 3)
            b = np.random.choice(range(3), f, replace=False)
            extra_f = ["Al", "Cu", "Ti", "Ag"]
            filters = [('Be', be_width), ('Air', air_width)]
            if len(b) > 0:
                for p in b:
                    filters.append((extra_f[p], np.random.uniform(low=0, high=0.3)))

            Prim, brems = Primary_gen(k, th, bn, physics[phys_i], mu_source[mu_i], o, mas, Targets[target_i], filters)
            print("Primary Spectrum has been created\n")
            Primary = Prim
        else:
            print("Primary Spectrum selected from Prim\n")

        N = np.random.randint(n_min, n_max)
        weights = torch.ones(41).expand(batch_size, -1)
        a = torch.multinomial(weights, num_samples=N, replacement=False)
        spec, peaks, c, gau = multigen_opt(a, Primary, cens_tens, css_tens)
        spec = escape_peaks_t(spec, gau)
        spec = sum_peaks_t(spec, gau)
        inds = x.unsqueeze(0).repeat(spec.size(0), 1).cuda().detach()

        if j % decal_rate == 0:
            decal = True
        else:
            decal = False

        if decal:
            spec = decalibration_t(spec)

        final_d = detector_eff_t(spec)

        if (final_d < 0).any():
            final_d[final_d < 0] = 0

        final_d = Narea_t(final_d)

        if not torch.isnan(final_d).any():
            noise = torch.rand(final_d.size()) / 1000
            brems_choice = torch.tensor(np.random.choice(brems[0], size=30000, p=Narea_t(torch.tensor(brems[1]))))
            char_choice = torch.tensor(np.random.choice(Primary[0], size=30000, p=Narea_t(torch.tensor(Primary[1]))))
            brem = Narea_t(torch.histc(brems_choice, bins=300, min=0.0, max=30)).cuda().detach()
            char = Narea_t(torch.histc(char_choice, bins=300, min=0.0, max=30)).cuda().detach()

            final_d_choice = torch.multinomial(final_d.cpu(), num_samples=30000, replacement=True)
            h_final_d = inds.gather(1, final_d_choice.cuda().detach())
            h_final_d = [torch.histc(row.float(), bins=300, min=0, max=30) for row in h_final_d]
            final_d = Narea_t(torch.stack(h_final_d))

            prop = torch.rand(1).unsqueeze(0).cuda().detach()
            new_spec = ((brem / 5) * prop) + final_d + noise.cuda().detach() + ((char / 15) * prop)

            torch.save(new_spec, path + str(j) + "_spectra.pt")
            torch.save(peaks, path + str(j) + "_peaks.pt")
            torch.save(c, path + str(j) + "_elements.pt")
            torch.save(gau, path + str(j) + "_gauss.pt")

            end = time.perf_counter()
            coef = -(end - start2) / (j * batch_size) if j != 0 else -(end - start) / batch_size
            print(f"Time taken for {batch_size} samples: {start - end:.6f} seconds\n")
            print(f"{coef} seconds per file\n")
        else:
            print("There is a nan element\n")

        del a, spec, peaks, c, noise, brems_choice, char_choice, brem, char
        del final_d_choice, h_final_d, final_d, prop, new_spec, Primary