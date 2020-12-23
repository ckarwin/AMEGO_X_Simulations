############################################################
# 
# Written by Chris karwin; December 2020; Clemson University
#
# Purpose: Simulate a source SED and light curve.
# 
# Index of functions:
#
#   Run_MEGAlib(superclass)
#       -run_cosima(seed="none")
#       -run_revan(config_file="none")
#       -run_mimrec(save_dir, numbins, rad, config_file="none")
#       -energy_dependent_mimrec(save_dir, numbins, config_file="none")
#
###########################################################

######################
#imports:
import os,sys,shutil 
import yaml
import pandas as pd
from scipy.interpolate import interp1d
######################

#superclass:
class Run_MEGAlib:
    
    """Main inputs are specified in inputs.yaml file"""

    def __init__(self,input_yaml):

        #get home directory:
        self.home = os.getcwd()
        
        #load main inputs from yaml file:
        with open(input_yaml,"r") as file:
            inputs = yaml.load(file,Loader=yaml.FullLoader)

        self.name = inputs["name"]
        self.geo_file = inputs["geometry_file"]
        self.spectrum_file = self.home + "/" + inputs["spectrum_file"]
        self.lc_file = self.home + "/" + inputs["lightcurve_file"]
        self.source_file = self.home + "/" + inputs["source_file"]
        self.bg_tra_file = self.home + "/" + inputs["background_tra_file"]
        self.mission = inputs["mission"]

    def run_cosima(self,seed="none"):

        """

         input definitions:
        
         seed: Optional input. Specify seed to be used in simulations for reproducing results.
        
        """

        #make print statement:
        print()
        print("********** Run_MEGAlib_Module ************")
        print("Running run_cosima...")
        print()

        #make Cosima directory:
        if os.path.isdir("Cosima") == True:
            shutil.rmtree("Cosima")
        os.system("mkdir Cosima")
        os.chdir("Cosima")
    
        #run Cosima:
        if seed != "none":
            print("running with a seed...")
            os.system("cosima -s %s %s | tee terminal_output_cosima.txt" %(seed,self.source_file))
        if seed == "none":
            print("running with no seed...")
            os.system("cosima %s | tee terminal_output_cosima.txt" %(self.source_file))

        #return home:
        os.chdir(self.home)

        return

    def run_revan(self,config_file="none"):

        """
        
         input definitions:
        
         config_file: Optional input. Configuration file specifying selections for event reconstruction.
        
        """

        #make print statement:
        print()
        print("********** Run_MEGAlib_Module ************")
        print("Running run_revan...")
        print()

        #make revan directory:
        if os.path.isdir("Revan") == True:
            shutil.rmtree("Revan")
        os.system("mkdir Revan")
        os.chdir("Revan")

        #copy output sim file from cosima to revan directory:
        cos_path = self.home + "/Cosima/"
        sim_file = self.name + ".inc1.id1.sim"
        shutil.copy2(cos_path+sim_file,sim_file)

        #run revan:
        if config_file != "none":
            print("running with a configuration file...")
            os.system("revan -g %s -c %s -f %s -n -a | tee revan_terminal_output.txt" %(self.geo_file, config_file, sim_file))

        if config_file == "none":
            print("running without a configuration file...")
            os.system("revan -g %s -f %s -n -a | tee revan_terminal_output.txt" %(self.geo_file, sim_file))

        #go home:
        os.chdir(self.home)

        return

    def run_mimrec(self, save_dir, numbins, rad, config_file="none"):

        """
        
         input definitions:
        
         save_dir: name of directory to save the output of run (this will be a subdirectory in Mimrec directory)
         
         numbins: number of log bins to use for extracting spectrum

         rad: radius of extraction region in degrees
        
         config_file: Optional input. Configuration file specifying selections for image reconstruction.
            
            - Note: the configuration file overwrites numbins and rad when passed.

        """

        #make print statement:
        print()
        print("********** Run_MEGAlib_Module ************")
        print("Running run_mimrec...")
        print()

        #make mimrec directory:
        if os.path.isdir("Mimrec") == False:
            os.system("mkdir Mimrec")
        os.chdir("Mimrec")

        #make save directory:
        if os.path.isdir(save_dir) == True:
            shutil.rmtree(save_dir)
        os.system("mkdir %s" %save_dir)
    
        #copy output tra file from revan to mimrec directory:
        rev_path = self.home + "/Revan/"
        tra_file = self.name + ".inc1.id1.tra"
        shutil.copy2(rev_path+tra_file,tra_file)
        
        #define outputs:
        src_output = save_dir + "/source_counts_spectrum.root"
        lc_output = save_dir + "/source_LC.root"
        bg_output = save_dir + "/background_counts_spectrum.root"

        #run mimrec for both source and background:
        if config_file != "none":
            
            config_file = self.home + "/" + config_file
            
            print("running with a configuration file...")
            
            #source spectrum:
            os.system("mimrec -g %s -c %s -f %s -s -o %s -n \
                    | tee %s/source_mimrec_terminal_output.txt" %(self.geo_file, config_file, tra_file, src_output, save_dir))
             
            #background spectrum:
            os.system("mimrec -g %s -c %s -f %s -s -n -o %s \
                    | tee %s/background_mimrec_terminal_output.txt" %(self.geo_file, config_file, self.bg_tra_file, bg_output, save_dir))
            
            #source ligh curve:
            os.system("mimrec -g %s -c %s -f %s -l -o %s -n \
                    | tee %s/lightcurve_mimrec_terminal_output.txt" %(self.geo_file, config_file, tra_file, lc_output, save_dir))
            

        if config_file == "none":
            
            print("running without a configuration file...")
            
            #source spectrum:
            os.system("mimrec -g %s -f %s -s -o %s -n \
                    -C HistogramBins.Spectrum=%s \
                    -C EventSelections.Source.UsePointSource=true \
                    -C EventSelections.Source.ARM.Max=%s \
                     | tee %s/source_mimrec_terminal_output.txt" %(self.geo_file, tra_file, src_output, str(numbins+1), str(rad), save_dir))

            #background spectrum:
            os.system("mimrec -g %s -f %s -s -o %s -n \
                    -C HistogramBins.Spectrum=%s \
                    -C EventSelections.Source.UsePointSource=true \
                    -C EventSelections.Source.ARM.Max=%s \
                     | tee %s/background_mimrec_terminal_output.txt" %(self.geo_file, self.bg_tra_file, bg_output, str(numbins+1), str(rad), save_dir))

            #source light curve:
            os.system("mimrec -g %s -f %s -l -o %s -n \
                    -C EventSelections.Source.UsePointSource=true \
                    -C EventSelections.Source.ARM.Max=%s \
                     | tee %s/lightcurve_mimrec_terminal_output.txt" %(self.geo_file, tra_file, lc_output, str(rad), save_dir))
                
        #change to save directory:
        os.chdir(save_dir)

        #extract spectrum histogram:
        os.system("root -q -b %s/ExtractSpectrum.cxx" %self.home)
        
        #extract light curve  histogram:
        os.system("root -q -b %s/ExtractLightCurve.cxx" %self.home)

        #go home:
        os.chdir(self.home)

        return

    def energy_dependent_mimrec(self, save_dir, numbins, config_file="none"):

        """
        
         purpose: calculate SED using energy-dependent extraction radius. 
            - radius is set by angular resolution of telescope.

         input definitions:
        
         save_dir: name of directory to save the output of run (this will be a subdirectory in Mimrec directory)
         
         numbins: number of log energy bins to use for extracting spectrum
        
         config_file: Optional input. Configuration file specifying selections for image reconstruction.
            
            - Note: the configuration file overwrites numbins and rad when passed.

        """

        #make print statement:
        print()
        print("********** Run_MEGAlib_Module ************")
        print("Running energy_dependent_mimrec...")
        print()

        #make mimrec directory:
        if os.path.isdir("Mimrec") == False:
            os.system("mkdir Mimrec")
        os.chdir("Mimrec")

        #make save directory:
        if os.path.isdir(save_dir) == True:
            shutil.rmtree(save_dir)
        os.system("mkdir %s" %save_dir)
    
        #copy output tra file from revan to mimrec directory:
        rev_path = self.home + "/Revan/"
        tra_file = self.name + ".inc1.id1.tra"
        shutil.copy2(rev_path+tra_file,tra_file)
        
        #define outputs:
        src_output = save_dir + "/source_counts_spectrum.root"
        bg_output = save_dir + "/background_counts_spectrum.root"

        #define angular resolution files for energy-dependent extraction region:
        performance_dir = self.home + "/" + self.mission + "_Performance/"
        tracked_compton = performance_dir + self.mission + "_compton_angular_resolution.txt"
        untracked_compton = performance_dir + self.mission + "_untracked_compton_angular_resolution.txt"
        pair = performance_dir + self.mission + "_pair_angular_resolution.txt"

        #extract angular resolution data
        tc_df = pd.read_csv(tracked_compton,delim_whitespace=True)
        tc_energy = tc_df["Energy[MeV]"]*1000 #convert to keV
        tc_res = tc_df["Resolution[deg]"]
        tc_func = interp1d(tc_energy,tc_res,kind="linear",bounds_error=False,fill_value="extrapolate")

        utc_df = pd.read_csv(untracked_compton,delim_whitespace=True)
        utc_energy = utc_df["Energy[MeV]"]*1000 #convert to keV
        utc_res = utc_df["Resolution[deg]"]
        utc_func = interp1d(utc_energy,utc_res,kind="linear",bounds_error=False,fill_value="extrapolate")

        pair_df = pd.read_csv(pair,delim_whitespace=True)
        pair_energy = pair_df["Energy[MeV]"]*1000 #convert to keV
        pair_res = pair_df["Resolution[deg]"]
        pair_func = interp1d(pair_energy,pair_res,kind="linear",bounds_error=False,fill_value="extrapolate")

        arm_list = [10] #initial value is used for determining energy-dependent list
        src_list = []
        bg_list = []
        for i in range(0,numbins+1):
            
            print("Working on energy bin %s..." %i)

            this_cut = arm_list[i]

            #source spectrum:
            os.system("mimrec -g %s -f %s -s -o %s -n \
                    -C HistogramBins.Spectrum=%s \
                    -C EventSelections.Source.UsePointSource=true \
                    -C EventSelections.Source.ARM.Max=%s" %(self.geo_file, tra_file, src_output, str(numbins+1), str(this_cut)))
            
            #background spectrum:
            os.system("mimrec -g %s -f %s -s -o %s -n \
                    -C HistogramBins.Spectrum=%s \
                    -C EventSelections.Source.UsePointSource=true \
                    -C EventSelections.Source.ARM.Max=%s" %(self.geo_file, self.bg_tra_file, bg_output, str(numbins+1), str(this_cut)))

            #change to save directory:
            os.chdir(save_dir)

            #extract spectrum histogram:
            os.system("root -q -b %s/ExtractSpectrum.cxx" %self.home)
            
            if i == 0:
                df = pd.read_csv("extracted_spectrum.dat", delim_whitespace=True)
                energy_bin = df["EC[keV]"]

                #make energy-dependent arm_list:
                real_arm_list = []
                for each in energy_bin:
            
                    if each < max(utc_energy):
                        this_res = utc_func(each)
                        real_arm_list.append(float(this_res))
            
                    if max(utc_energy) < each <= max(tc_energy):
                        this_res = tc_func(each) 
                        real_arm_list.append(float(this_res))
            
                    if each > max(tc_energy):
                        this_res = pair_func(each)
                        real_arm_list.append(float(this_res))
    
                #define updated arm list
                arm_list += real_arm_list

                #print and write the updated arm list:
                print("Energy-dependent arm list:")
                print(arm_list[1:])
                f = open("extraction_list.txt","w")
                f.write(str(arm_list[1:]))
                f.close()

                #remove file:
                os.system("rm extracted_spectrum.dat")
    
                #go back to working directory:
                os.chdir(self.home+"/Mimrec")

            if i > 0:
            
                #get counts for current energy bin:
                df = pd.read_csv("extracted_spectrum.dat", delim_whitespace=True)
                src_cts = df["src_ct/keV"]
                bg_cts = df["bg_ct/keV"]
            
                this_src = src_cts[i-1]
                this_bg = bg_cts[i-1]
            
                src_list.append(this_src)
                bg_list.append(this_bg)
            
                #rename file:
                os.system("mv extracted_spectrum.dat extracted_spectrum_energy_bin_%s.dat" %i)
    
                #go back to working directory:
                os.chdir(self.home+"/Mimrec")

        #change to save directory:
        os.chdir(save_dir)
        
        #write_final_file:
        df = pd.read_csv("extracted_spectrum_energy_bin_1.dat", delim_whitespace=True)
        EC = df["EC[keV]"]
        EL = df["EL[keV]"]
        EH = df["EH[keV]"]
        BW = df["BW[keV]"]
        
        d = {"EC[keV]":EC, "EL[keV]":EL, "EH[keV]":EH, "BW[keV]":BW, "src_ct/keV":src_list, "bg_ct/keV":bg_list}
        new_df = pd.DataFrame(data=d)
        new_df.to_csv("extracted_spectrum.dat", index=False, sep="\t", columns=["EC[keV]", "EL[keV]", "EH[keV]", "BW[keV]", "src_ct/keV", "bg_ct/keV"])

        #go home:
        os.chdir(self.home)

        return
