############################################################
# 
# Written by Chris karwin; December 2020; Clemson University
#
# Purpose: Simulate a source
# 
# Index of functions:
#
#   Run_MEGAlib(superclass)
#       -run_cosima()
#       -run_revan()
#       -run_mimrec()
#
###########################################################

######################
#imports:
import os,sys,shutil 
import yaml
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
