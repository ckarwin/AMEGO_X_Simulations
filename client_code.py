#imports:
from MEGAlib_module import MEGAlib

#define instance:
instance = MEGAlib()

model_file = "TXS_0506_056_30_day_spectrum.dat"
simulated_data_file = "Extracted_Mimrec_Spectra/" +  "extracted_spectrum_7bins_10deg.dat"

#run functions:
#instance.Make_Cosima_input("Keivani_leptonic_model.txt")
instance.Effective_Area(model_file,simulated_data_file,"Image_Files/effective_area_7bins.pdf")
instance.Make_SED(simulated_data_file,"Image_Files/SED_7bins.pdf")
