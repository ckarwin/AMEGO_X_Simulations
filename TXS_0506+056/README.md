# Analysis Outline <br />
One of the primary software tools used for designing future MeV Telescopes is MEGAlib, available [here](http://megalibtoolkit.com/home.html). MEGAlib simulates the emission from any gamma-ray source, simulates the instrument response, and generates the simulated data that would be detected for a given detector design, observation time, background emission, etc. See the above link for more details regarding the MEGAlib package. 

## Purpose <br />
The primary code is **MEGAlib_module.py**, which is called with **client_code.py**. The purpose of of the module is to generate the inputs for MEGAlib, and process the simulated data. The main output is shown below. The black curve is the model spectrum that was simulated. The red data points are the observed data, with the corresponding error. For reference, the dashed purple line shows the 3-sigma sensitivity of AMEGO. The code also calculates the significane of each SED bin. 

![Alt text](SED_7bins.png)
