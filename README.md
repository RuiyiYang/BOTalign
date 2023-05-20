# BOTalign
This is an algorithm for aligning three-dimensional objects represented as three dimensional arrays $V_1,V_2\in \mathbb{R}^{L\times L\times L}$.
# Dependencies
The algorithm requires the following packages:
- [ASPIRE](https://github.com/ComputationalCryoEM/ASPIRE-Python)
- numpy
- scipy
- mrcfile
- pymanopt
# Usage
The user can simply download the files utils_BO.py and wemd.py. The main alignment algorithm can be found in utils_BO.py as align_BO, which takes in the two volumes to be aligned and four parameters:
- Loss type: 'wemd' or 'eu' 
- Downsampling level: an integer 
- Number of iterations: an integer 
- Whether to perform refinement: True or False 

The data folder contains one test volume (more can be found on [EMDB](https://www.ebi.ac.uk/emdb/)). The test_BOTalign.py conducts a comparison on four combinations of the parameters that we illustrated in the manuscript.  

# Comparisons
To reproduce the comparison results in the manuscript, install the [EMalign](https://github.com/ShkolniskyLab/emalign) and the [alignOT](https://github.com/artajmir3/alignOT) packages, and run test_comparison.py. For alignOT, one needs to download all the files in their alignOT folder and put them in the same directory as test_comparison.py. 
