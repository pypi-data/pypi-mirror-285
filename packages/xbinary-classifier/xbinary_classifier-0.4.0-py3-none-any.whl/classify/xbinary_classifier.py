import joblib
import os
import pandas as pd
import pickle
import warnings
from astropy.io import fits
from astropy.table import Table, vstack
# Define our classifying function.
def xbinary_classifier_function(source):
    ''' 
    Classifies an X-ray binary source as either High Mass X-ray Binary (HMXB) or Low Mass X-ray Binary (LMXB).
    
    Parameters:
    source (list): A list containing the following features of the target in order:
        - RA (float): Right Ascension
        - DEC (float): Declination
        - VMAG (float): Visual Magnitude (optical counterpart)
        - BV_COLOR (float): B-V Color Index (optical counterpart)
        - PORB (float): Orbital Period
        - FLUX (float): X-ray Flux
        - FLUX_MAX (float): Maximum X-ray Flux
        - LII (float): Galactic Longitude
        - BII (float): Galactic Latitude
        - VMAG_MIN (float): Minimum Visual Magnitude (optical counterpart)
        - UB_COLOR (float): U-B Color Index (optical counterpart)
        - PULSE_PERIOD (float): Pulse Period
    
    Returns:
    None: Prints the classification of the source as either HMXB or LMXB.
    '''
    # Get the directory where the script is located
    script_dir = os.path.dirname(__file__)
    # Define the path to the model file within the same directory
    model_path = os.path.join(script_dir, 'model.pkl')
    # Check if the model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    # Upload our trained model
    model = joblib.load(model_path)
    warnings.filterwarnings('ignore', message='X does not have valid feature names, but KNeighborsClassifier was fitted with feature names')
    # Get the source data
    source = [source]
    # Make prediction
    prediction = model.predict(source)
    if prediction[0] == 0:
        print('The X-ray Binary source has been classified as low mass')
    else:
        print('The X-ray Binary source has been classified as high mass')
