from SFRcalculator import sfr_calculator as sfc
import numpy as np
import pandas as pd

def test_compute():
    """
    Function to test the compute() method of sfr_calculator.
    """
    test_phot = np.random.rand(10,3) * 5 - 21 # random floats from -21 to -16 (abs mags)
    tphot = pd.DataFrame(test_phot,columns=['u','b','z'])
    usersfrs = sfc.compute(bands = ['u','b','z'], user_data = tphot)

    assert len(usersfrs) == len(test_phot)
    assert np.all(np.isfinite(usersfrs))