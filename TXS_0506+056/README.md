## Software <br />
One of the primary software tools used for designing future MeV Telescopes is MEGAlib, available [here](http://megalibtoolkit.com/home.html). MEGAlib simulates the emission from any gamma-ray source, simulates the instrument response, and generates the simulated data that would be detected for a given detector design, observation time, background emission, etc. See the above link for more details regarding the MEGAlib package. Examples for running MEGAlib can be found in the folders "Simulation_Challenge" and "GRB170817A".  

## Purpose <br />
The primary code in this folder is **MEGAlib_module.py**, which is called with **client_code.py**. The purpose of the module is to generate the inputs for MEGAlib, and process the simulated data. The main output is shown below for the specific case of TXS 0506+056. The black curve is the model spectrum that was simulated. The red data points are the observed (simulated) data. The error bars in the x-direction give the bin size, and the error bars in the y-direction give the 1-sigma statistical error. The module calculates the error, as well as the statistical significance of each bin. For reference, the dashed purple line shows the 3-sigma sensitivity of AMEGO.  

![Alt text](SED_7bins.png)
