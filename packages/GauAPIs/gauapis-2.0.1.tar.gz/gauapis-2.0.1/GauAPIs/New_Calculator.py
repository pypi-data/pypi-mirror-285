import os
import time
from GauAPIs.Molecule import Molecule
import numpy as np


'''
Calculators are:
    xTB: GFN1-xTB, GFN2-xTB
    ANI: ANI-1x, ANI-2x, ANI-1ccx
    MLatom: AIQM1, AIQM1@DFT
    Orca: 
'''
global eleslist
eleslist = ['H','He',
        'Li','Be','B','C','N','O','F','Ne',
        'Na','Mg','Al','Si','P','S','Cl','Ar',
        'K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr']

global b2a
b2a = 0.52917724

#XTB default input is in Bohr
def calculate_mol_xTB(mol,xtbpara):
    #first solve the environment
    try:
        from xtb.libxtb import VERBOSITY_FULL, VERBOSITY_MINIMAL
        from xtb.interface import Environment, Calculator, Param
    except ImportError:
        print('no xTB module found.')
    
    env = Environment()
    env.set_output("env_error.log")
    env.set_verbosity(VERBOSITY_FULL)
    if env.check != 0:
        env.show("Error message")
    env.release_output()
    xtbpara = Param(xtbpara)
    #define structure data for molecule
    eles_nums = mol.elements
    coors = np.divide(mol.coordinates,b2a)
    #define calculator based on input xtbpara and mol
    calc = Calculator(xtbpara,eles_nums,coors)
    calc.set_verbosity(VERBOSITY_MINIMAL)
    #Calculation
    res = calc.singlepoint()
    Ene = res.get_energy()
    Grad = res.get_gradient()
    return Ene, Grad

#ani input in cartesian(Angstrom)
def calculate_mol_ani(mol,methodani):
    
    #ANI
    try:
        import torch
        import torchani
        device = torch.device('cpu')

    except ImportError:
        print('no ANI module found')

    #define model based on input methodani

    if methodani.lower() == 'ani-2x':
        model = torchani.models.ANI2x(periodic_table_index=True).to(device).double()
    elif methodani.lower() == 'ani-1ccx':
        model = torchani.models.ANI1ccx(periodic_table_index=True).to(device).double()
    elif methodani.lower() == 'ani-1x':
        model = torchani.models.ANI1x(periodic_table_index=True).to(device).double()
    else:
        print('Error: Method not recognised, Using ANI2x instead')
        model = torchani.models.ANI2x(periodic_table_index=True).to(device).double()

    #have to convert from np to tensor first
    coordinates = torch.from_numpy(mol.coordinates).requires_grad_(True).unsqueeze(0)
    species = torch.from_numpy(mol.elements).unsqueeze(0)
    ene = model((species, coordinates)).energies
    derivative = torch.autograd.grad(ene.sum(), coordinates)[0]
    force = -derivative
    #convert tensor to numpy and return
    return ene.item(),derivative.numpy()


def calculate_mol_mlatom(xyzfile,charge,spin,methodmlatm):
    try:
        import mlatom as ml
    except ImportError:
        print('no MLatom module found')
    #read molecule in 
    mol = ml.data.molecule.from_xyz_file(xyzfile)
    mol.charge = charge
    mol.multiplicity = spin
    #define model
    model = ml.models.methods(method=methodmlatm)
    
    #calculate energy and force
    model.predict(molecule=mol)

    ene = mol.energy
    grad = mol.get_energy_gradients()
    return ene,grad

#OCRA: orca takes some file in&out without python API.
#So I just write a function to call orca and get the result.
def mol2xyz(mol):
    nums = mol.get_num_atoms()
    fw = open(f'{mol.name}.xyz','w')
    fw.write('%d\n\n'%(nums))
    try:
        for i in range(nums):
            fw.write('%s %f %f %f\n'%(eleslist[mol.elements[i]-1],mol.coordinates[i][0],mol.coordinates[i][1],mol.coordinates[i][2]))
    except IndexError:
            print('IndexError: Maybe no such element in eleslist')
    fw.write('\n')
    fw.close()        

def write_orca_input(mol,charge,spin,methodorca,par_core):
    fw = open(f'{mol.name}.inp','w')
    fw.write(f'! {methodorca} DEF2-TZVPP ENGRAD\n')
    fw.write(f'%PAL NPROCS {par_core} END\n')
    #Use xyz file to define molecule, it is covenient
    fw.write(f'* xyzfile {charge} {spin} {mol.name}.xyz \n')
    fw.write('\n')


def Get_Orca_SP(outname):
    fr = open(outname,"r") 
    lines = fr.readlines()
    fr.close()
    index_of_energy = []
    index_of_ext_energy = []
    i = 0
    errlines = []
    for line in lines:
        if "FINAL SINGLE POINT ENERGY" in line:
            index_of_energy.append(i)
        
        i= i+1
    try:
        loc = int(index_of_energy[-1])
        energy = lines[loc].split()[-1]
        return float(energy)           
    except IndexError:
        print('Energy not found in %s file!'%outname)              #help check the bug   
        print(errlines)
        print('')

def Get_orca_grad(outname,mol,der):
    fg = open(outname,"r")
    lines = fg.readlines()
    fg.close()
    nums = mol.get_num_atoms()
    grad_arr = np.zeros((nums,3),dtype=float)
    if der == 1:
        for line in lines:
            if "CARTESIAN GRADIENT" in line:
                index_of_grad = lines.index(line)
                break
            counts = 0
        for grads in lines[index_of_grad+3:index_of_grad+2+nums]:
            grad_arr[counts] = np.array([float(grads.split()[3]),float(grads.split()[4]),float(grads.split()[5])])
            counts += 1
        
    return grad_arr


def calculate_mol_orca(mol,charge,spin,methodorca,par_core,der):
    write_orca_input(mol,charge,spin,methodorca,par_core)
    orca_inp = f'{mol.name}.inp'
    os.system('orca '+orca_inp+'> '+mol.name+'.log')
    ene_sp = Get_Orca_SP(mol.name+'.log')
    grad_sp = Get_orca_grad(mol.name+'.log',mol,der)
    return ene_sp, grad_sp

