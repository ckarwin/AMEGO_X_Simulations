##########################################################
#
# Written by Chris Karwin; November 2020; Clemson University
# 
# Purpose: 
#   1) Make input model file for Cosima.
#   2) Calculate effective area resulting from MEGAlib simulation.
#   3) Convert Mimrec output to SED data points; caluclate corresponding error and statistical significance.
#
# Index of functions:
#
#   MEGAlib(superclass)
#       -Make_Cosima_input(input_model)
#       -Effective_Area(input_model,observed_data,bin_width_file,savefile)
#       -Make_SED(observed_data,bin_width_file,background_file,savefile)
#
##########################################################

##########################################################
#imports:
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy import integrate
import numpy as np
import math
from astropy.stats import poisson_conf_interval as pci
##########################################################

#superclass:
class MEGAlib:

    def __init__(self):

        self.time = 10368000.0 #observation time in seconds
        self.area =  70685.83470577 #area of surrounding sphere, units= cm^2

    def Make_Cosima_input(self,input_model):

        ####################
        #
        # input definitions:
        #
        # input_model: model spectrum used for Cosima
        #
        ####################
       
        #make print statement:
        print
        print "********** MEGAlib Module ************"
        print "Running Make_Cosima_input..."
        print
        
        #load original model:
        erg_to_keV = 6.242e8
        df = pd.read_csv(input_model,delim_whitespace=True)
        energy = df["energy[eV]"]*(1e-3) #keV
        energy_erg = energy*(1/erg_to_keV)
        flux = df["flux[erg/cm^2/s]"]
         
        #convert E^2*dN/dE to dN/dE:
        ph_flux = flux/(energy_erg**2) #ph/cm^2/s/erg

        #convert erg to keV:
        ph_flux = ph_flux * (1/erg_to_keV) #ph/cm^2/s/keV

        #interpolate photon flux:
        ph_flux_func = interp1d(energy, ph_flux, kind="linear")
        
        #integrate flux:
        int_flux = integrate.quad(ph_flux_func,1e2,1e6)
        print
        print "integral flux between 100 keV - 1 GeV [ph/cm^2/s]:"
        print int_flux
        print

        #Define plot range between 100 keV and 1e6 keV:
        plot_range = np.logspace(2,6,35,endpoint=True)
        
        #write results
        data = {"energy":plot_range,"diff_flux":ph_flux_func(plot_range),"rows":["DP"]*len(plot_range)}
        new_df = pd.DataFrame(data=data)
        new_df.to_csv("Cosima_input_spectrum.dat",sep="\t",index=False,columns=["rows","energy","diff_flux"])

        #plot differential flux:
        fig = plt.figure(figsize=(9,6))
        ax = plt.subplot()
        
        plt.loglog(plot_range,ph_flux_func(plot_range),color="black",lw=3,label="SED")
        plt.fill_between(plot_range,ph_flux_func(plot_range),0,hatch="//",alpha=0.5,color="gray")

        plt.xlabel("Energy [keV]", fontsize=16)
        plt.ylabel(r"Flux [$\mathrm{ph \ cm^{-2} \ s^{-1} \ \mathrm{keV^{-1}}}$]",fontsize=16)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax.tick_params(axis='both',which='major',length=8)
        ax.tick_params(axis='both',which='minor',length=5)

        #plt.grid(color="grey",alpha=0.4,ls=":")
        plt.xlim(10,1e7)
        plt.legend(loc=1)
        plt.savefig("diff_flux.png")
        plt.show()
        plt.close()

    def Effective_Area(self,input_model,observed_data,savefile):

        ####################
        #
        # input definitions:
        #
        # input_model: model spectrum used for Cosima
        #
        # observed_data: extracted spectrum from Mimrec, i.e. simulated data
        # 
        # savefile: file name for saving effective area plot
        #
        ####################

        #make print statement:
        print
        print "********** MEGAlib Module ************"
        print "Running Effective_Area..."
        print

        #input model:
        df_model = pd.read_csv(input_model, delim_whitespace=True, skiprows=[0,1,2,3,4], names=["row","energy","flux"])
        energy_model = df_model["energy"]
        flux_model = df_model["flux"]

        #convert to number of generated events:
        flux_model = flux_model * self.time * self.area #ph/keV

        #interpolate model to match with the data energy binning:
        flux_model_interp = interp1d(energy_model, flux_model, kind='linear')
        
        #observed (simulated) data:
        df_data = pd.read_csv(observed_data, delim_whitespace=True)
        flux_data = df_data["src_ct/keV"] #ph/keV
        bin_width = df_data["BW[keV]"] #keV
        bin_low_edge = df_data["EL[keV]"]
        bin_up_edge = df_data["EH[keV]"]
        energy_data = np.sqrt(bin_low_edge*bin_up_edge) #geometric mean of energy bin in keV
    
        #calculate effective area as a function of energy:
        A_eff = (flux_data/flux_model_interp(energy_data)) * self.area

        #calculate total effective area, integrated over all energies:
        A_eff_full = ((np.sum(flux_data*bin_width))/np.sum(flux_model_interp(energy_data)*bin_width)) * self.area

        print
        print "total # of detected events:"
        print np.sum(flux_data*bin_width)
        print
        print "total effictive area [cm^2]:"
        print A_eff_full
        print 

        #save effective_area:
        d = {"energy [keV]":energy_data,"A_eff [cm^2]":A_eff}
        df = pd.DataFrame(data = d,columns=["energy [keV]","A_eff [cm^2]"])
        df.to_csv("TXS_0506_A_eff.dat",sep="\t",index=False)

        #plot figure:
        fig = plt.figure(figsize=(9,6))
        plt.rc('axes',linewidth=1.5)
        ax = plt.subplot()

        #plot my results:
        plt.loglog(energy_data,A_eff, color="black",marker="",ls="-",lw=3,label="Effective Area (TXS 0506+056 all events)")

        #Plot True (Carolyn's) results for comparison:
        untracked_compton_silicon = {"file":"AMEGO_effective_area_untracked_compton_silicon.txt","label":"Untracked Compton in silicon","color":"navy","ls":"--"}
        untracked_compton = {"file":"AMEGO_effective_area_untracked_compton.txt","label":"Untracked Compton","color":"cornflowerblue","ls":"--"}
        tracked_compton = {"file":"Amego_effective_area_tracked_compton.txt","label":"Tracked Compton","color":"green","ls":"-."}
        pair = {"file":"Amego_effective_area_pair.txt","label":"Pair Production","color":"red","ls":":"}

        plot_list = [untracked_compton,untracked_compton_silicon,tracked_compton,pair]

        for each in plot_list:

            this_file = "AMEGO_Performance/" + each["file"] 
            this_label = each["label"]
            this_color = each["color"]
            this_ls = each["ls"]
    
            this_df  = pd.read_csv(this_file, delim_whitespace=True, skiprows=[0],names=["energy","effective_area"])
            energy = this_df["energy"] * 1e3 #convert MeV to keV
            area = this_df["effective_area"]

            plt.loglog(energy,area, color=this_color,marker="",ls=this_ls,lw=3,label=this_label)

        plt.title("AMEGO",fontsize=16,y=1.04)
        plt.xlabel("Energy [keV]", fontsize=16)
        plt.ylabel(r"Effective Area [$\mathrm{cm^{2}}$]",fontsize=16)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax.tick_params(axis='both',which='major',length=8)
        ax.tick_params(axis='both',which='minor',length=5)

        plt.legend(loc=2,ncol=1,frameon=False)
        plt.ylim(1,1e5)
        #plt.xlim(10,1e8)
        plt.grid(color="grey",alpha=0.4,ls=":")
        plt.savefig(savefile)

        plt.show()

        return

    def Make_SED(self,observed_data,savefile):

        ####################
        #
        # input definitions:
        #
        # observed_data: extracted spectrum from Mimrec, i.e. simulated data. This also includes background counts.
        #
        # savefile: file name for saving effective area plot
        #
        ####################

        #make print statement:
        print
        print "********** MEGAlib Module ************"
        print "Running Make_SED..."
        print

        #define energy conversion, ergs to keV:
        erg_keV = 1.60218e-9 

        #load AMEGO sensitivity:
        df_amego = pd.read_csv("AMEGO_Performance/AMEGO_sensitivity.txt",skiprows=[0],delim_whitespace=True,names=["energy","flux"])
        energy_amego = df_amego["energy"]*(1e3) #convert MeV energy to keV
        
        #convert flux to erg, scale by observing time, and convert for pointed observation:
        calc_time = 9.4608e7 #sensitivity is calculated for three years
        mev_to_erg = 1.60218e-6
        scan_mode = 0.2 #exposure time is 20% in scanning mode
        flux_amego = df_amego["flux"] * mev_to_erg * math.sqrt((calc_time*scan_mode)/self.time)

        #load original model:
        df = pd.read_csv("Keivani_leptonic_model.txt",skiprows=[0],delim_whitespace=True,names=["energy","flux"])
        energy = df["energy"]*(1e-3) #convert energy to keV
        flux = df["flux"]

        #plot figure:
        fig = plt.figure(figsize=(9,6))
        plt.rc('axes',linewidth=1.5)
        ax = plt.subplot()

        #plot original model:
        plt.loglog(energy,flux,color="black",alpha=0.8,lw=3,label="Keivani+18, leptonic model")

        #plot AMEGO sensitivity:
        plt.loglog(energy_amego,flux_amego,color="purple",ls="--",lw=3,label="AMEGO 3$\sigma$ Continuum Sensitivity")

        ###################
        #plot AMEGO data:

        #load simulated data:
        amego_df = pd.read_csv(observed_data,delim_whitespace=True)
        amego_dNdE = amego_df["src_ct/keV"]
        bin_width = amego_df["BW[keV]"]
        bin_low_edge = amego_df["EL[keV]"]
        bin_up_edge = amego_df["EH[keV]"]
        amego_data_energy = np.sqrt(bin_low_edge*bin_up_edge).tolist() #geometric mean of energy bin in keV
        bg_dNdE = amego_df["bg_ct/keV"] * (self.time/(7200)) #2 hrs were simulated. Need to scale by the observation time. 
    
        bg_counts = bg_dNdE*bin_width

        print
        print "Total background counts:"
        print np.sum(bg_counts)
        print
        print "Background counts list:"
        print bg_counts
        print
        print "time scaling factor [s]: " + str(self.time/(7200))
        print 

        #load effective area:
        area_df = pd.read_csv("TXS_0506_A_eff.dat",skiprows=[0],delim_whitespace=True,names=["energy","area"])
        area_energy = area_df["energy"]
        area = area_df["area"]
    
        #interpolate effective area to agree with counts spectrum
        func = interp1d(area_energy, area, kind='linear',bounds_error=False,fill_value="extrapolate")
        A_eff = func(amego_data_energy)
    
        #get total counts per bin and error:
        amego_counts = amego_dNdE*bin_width
        amego_error = np.sqrt(amego_counts)

        total_counts = np.sum(amego_counts)
        
        print 
        print "Total simulated counts:"
        print total_counts
        print
        print "Counts list:"
        print amego_counts.tolist()
        print 
        print "Counts Error list (standard):"
        print amego_error.tolist()
        print

        #calculate 1 sigma statistical error and significance:
        amego_error = np.sqrt(amego_counts + bg_counts)
        sigma = amego_counts / np.sqrt(amego_counts + bg_counts)
        
        #setting statistical significane for plotting data points; otherwise plot upper limits:
        good_index = sigma >= 3 
        ul_index = sigma < 3

        print
        print "significance (sigma) of SED bins:"
        print sigma.tolist()
        print

        #convert to flux:
        amego_data_energy = np.array(amego_data_energy)
        amego_data_flux = (amego_dNdE/(A_eff*self.time))*(amego_data_energy**2)*erg_keV
        amego_error = ( (amego_error/bin_width) / (A_eff*self.time) ) * (amego_data_energy**2)*erg_keV
        xerr_low = amego_data_energy - bin_low_edge
        xerr_high = bin_up_edge - amego_data_energy
        xerr_good = [xerr_low[good_index],xerr_high[good_index]]
        xerr_ul = [xerr_low[ul_index],xerr_high[ul_index]]

        print
        print "source counts:"
        print amego_counts.tolist()
        print
        print "background counts:"
        print bg_counts.tolist()
        print
    
        #plot 
        plt.loglog(amego_data_energy[good_index],amego_data_flux[good_index],zorder=10,color="red",ms=6,marker="o",ls="",lw=6,label="_nolabel_")
        plt.errorbar(amego_data_energy[good_index],amego_data_flux[good_index],zorder=10,xerr=xerr_good,yerr=amego_error[good_index],ms=6,color="red",marker="o",ls="",lw=2,uplims=False,label="AMEGO-X data (MEGAlib)")
        plt.errorbar(amego_data_energy[ul_index],amego_data_flux[ul_index]+amego_error[ul_index],zorder=10,xerr=xerr_ul,yerr=amego_error[ul_index]/2.0,ms=6,color="red",marker="",ls="",lw=2,uplims=True,label="_nolable_")
        plt.title("TXS 0506+056 (IceCube-170922A flaring state)",fontsize=16,y=1.04)
        plt.xlabel("Energy [keV]", fontsize=16)
        plt.ylabel(r"$\mathrm{E^2}$ dN/dE [$\mathrm{erg \ cm^{-2} \ s^{-1}}$]",fontsize=16)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax.tick_params(axis='both',which='major',length=8)
        ax.tick_params(axis='both',which='minor',length=5)

        plt.legend(loc=2,ncol=1,fontsize=11,frameon=False)
        plt.ylim(1e-13,1e-9)
        plt.xlim(1e1,1e7)
        plt.grid(color="grey",alpha=0.2,ls="-")
        plt.savefig(savefile)
        plt.show()
        plt.close()

        return
