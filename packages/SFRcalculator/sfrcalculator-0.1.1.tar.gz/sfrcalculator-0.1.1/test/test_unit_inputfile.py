import sys
sys.path.append("../SFRcalculator/")

import numpy as np
import pandas as pd
#import sfr_calculator
#frpom SFRs-calculator import SFRscalculator.sfr_calculator
from SFRcalculator import sfr_calculator
import matplotlib.pyplot as plt

data = pd.read_csv("SFRcalculator/A2670Finalcat.csv")


def test_inputfile():
    print("Now we are testing the input file")
    # Load the data
    data = pd.read_csv("SFRcalculator/A2670Finalcat.csv")
    mag_data = data[['mag_u', 'mag_g','mag_r','mag_z']]
    mag_data.columns = ['u','g','r','z']
    
    bands = ['u', 'b', 'v', 'k', 'g', 'r', 'i', 'z']

    assert np.isin(mag_data.columns,bands).all()
    assert np.isnan(mag_data.values).all()==False


    
