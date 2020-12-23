#imports:
import os, sys
import pandas as pd
from Run_MEGAlib_module import Run_MEGAlib
from Process_MEGAlib_module import Process_MEGAlib

def main(cmd_line):

    #Code can be ran with and without passing the yaml file.
    #Passing the yaml file is necessary for submitting multiple jobs simulataneously.

    if len(cmd_line) == 2:
        this_yaml = cmd_line[1]

    #specify name of default yaml if none is passed:
    if len(cmd_line) == 1:
        this_yaml = "inputs.yaml"

    #upload any data that needs to be passed to module:
    df = pd.read_csv("Inputs/Keivani_leptonic_model.txt",delim_whitespace=True)
    energy = df["energy[eV]"]/1000.0
    flux = df["flux[erg/cm^2/s]"]
    model_dict = {"energy":energy,"flux":flux}

    #define instances:
    instanceA = Run_MEGAlib(this_yaml)
    instanceB = Process_MEGAlib(this_yaml)

    #run help to see function inputs:
    #help(instanceA)
    #help(instanceB)

    ####################################################
    # 
    # Uncomment below for running desired functions:
    #
    
    #functions for running MEGAlib:
    #instanceA.run_cosima(432020)
    #instanceA.run_revan("Inputs/revan_R5_firstinteractionD1_MIPS_clustering.cfg")
    #instanceA.run_mimrec("SixBins_2deg",6,2)
    instanceA.energy_dependent_mimrec("100Bins_Energy_Dependent",100)

    #functions for processing the MEGAlib output:
    #instanceB.Make_Cosima_input("Inputs/Keivani_leptonic_model.txt")
    #instanceB.Effective_Area("Mimrec/SixBins_Energy_Dependent/")
    #instanceB.Make_SED("Mimrec/SixBins_Energy_Dependent/",model_dict)
    #instanceB.Make_LC("Mimrec/SixBins_10deg/",1)

########################
if __name__=="__main__":
        main(sys.argv)
