#!/usr/bin/env python
# coding: utf-8

# In[93]:


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
from astropy import constants as const
from collections import Counter


# In[130]:


def query_parameters(system_name):

    """ Query function 

    Queries NASA Exoplanet archive and obtains system parameters for desired system 

    Args: 
        system_name (string): system to query parameters for 

    Returns: 
        planet_radius (array): radii of planets in system 
        orbital_period (array): orbital periods of planets in system 
        semi_major_axis (array): semimajor axes of planets in system 
        planet_mass (array): masses of planets in system
        eccentricity (array): eccentricities of planets in system 
        stellar_radius (float): radius of star in system 
        stellar_temp (float): temperature of star in system
        number_of_planets (int): number of planets in system 
        
    """
    
    # NASA Exoplanet Archive Downloader
    # inspired by https://github.com/ethankruse/exoplots


    NEW_API = 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query='
    # The "exoplanets" table includes all confirmed planets and hosts in the
    # archive with parameters derived from a single, published reference


    # New confirmed planets
    print("Downloading all confirmed planets from NExSci's new table...")

    columns='pl_name,hostname,default_flag,sy_snum,sy_pnum,discoverymethod,disc_year,disc_facility,tran_flag,soltype,pl_controv_flag,pl_refname,pl_orbper,pl_orbpererr1,pl_orbpererr2,pl_orbperlim,pl_orbsmax,pl_orbsmaxerr1,pl_orbsmaxerr2,pl_orbsmaxlim,pl_rade,pl_radeerr1,pl_radeerr2,pl_radelim,pl_radj,pl_radjerr1,pl_radjerr2,pl_radjlim,pl_bmasse,pl_bmasseerr1,pl_bmasseerr2,pl_bmasselim,pl_bmassj,pl_bmassjerr1,pl_bmassjerr2,pl_bmassjlim,pl_bmassprov,pl_orbeccen,pl_orbeccenerr1,pl_orbeccenerr2,pl_orbeccenlim,pl_insol,pl_insolerr1,pl_insolerr2,pl_insollim,pl_eqt,pl_eqterr1,pl_eqterr2,pl_eqtlim,pl_orbincl,pl_orbinclerr1,pl_orbinclerr2,pl_orbincllim,ttv_flag,pl_trandur,pl_trandurerr1,pl_trandurerr2,pl_trandurlim,pl_ratdor,pl_ratdorerr1,pl_ratdorerr2,pl_ratdorlim,pl_ratror,pl_ratrorerr1,pl_ratrorerr2,pl_ratrorlim,pl_occdep,pl_occdeperr1,pl_occdeperr2,pl_occdeplim,st_refname,st_spectype,st_teff,st_tefferr1,st_tefferr2,st_tefflim,st_rad,st_raderr1,st_raderr2,st_radlim,st_mass,st_masserr1,st_masserr2,st_masslim,st_met,st_meterr1,st_meterr2,st_metlim,st_metratio,st_logg,st_loggerr1,st_loggerr2,st_logglim,sy_refname,rastr,ra,decstr,dec,sy_dist,sy_disterr1,sy_disterr2,sy_vmag,sy_vmagerr1,sy_vmagerr2,sy_jmag,sy_jmagerr1,sy_jmagerr2,sy_hmag,sy_hmagerr1,sy_hmagerr2,sy_kmag,sy_kmagerr1,sy_kmagerr2,sy_gaiamag,sy_gaiamagerr1,sy_gaiamagerr2,rowupdate,pl_pubdate,releasedate'


    print("Downloading default_flag=1")
    where1 = 'where+default_flag=1'
    full1 = NEW_API + 'select+' + columns + '+from+ps+' + where1 + '&format=csv'
    df = pd.read_csv(full1)
    df.to_csv('default_params1.csv')

    with open('last_update_time.txt', 'w') as ff:
        ff.write(str(datetime.now()))
    
    # read in default flag = 1 csv
    
    df1_filename = "default_params1.csv"
    
    # assign to pandas dataframe
    
    df1 = pd.read_csv(
        df1_filename,
        header=0
    ).iloc[:, 1:]
    
    # find planetary system
    
    system_parameters = df1.loc[df1['hostname'] == system_name]
    
    # return number of planets
    
    number_of_planets = system_parameters['sy_pnum'].values
    
    # get planetary radii
    
    planet_radius = system_parameters['pl_radj'].values
    
    planet_radius_array_without_nan = [x for x in planet_radius if str(x) != 'nan']
    
    if len(planet_radius_array_without_nan) == 0:
        return ValueError('No planetary radii available for this system.')
    
    # get orbital periods
    
    orbital_period = system_parameters['pl_orbper'].values
    
    orbital_period_without_nan = [x for x in orbital_period if str(x) != 'nan']
    
    if len(orbital_period_without_nan) == 0:
        return ValueError('No periods available for this system.')
    
    # get semi_major axis
    
    semi_major_axis = system_parameters['pl_orbsmax'].values
    
    semi_major_axis_without_nan = [x for x in semi_major_axis if str(x) != 'nan']
    
    if len(semi_major_axis_without_nan) == 0:
        return ValueError('No semi-major axis available for this system.')
    
    # get planetary masses
    
    planet_mass = system_parameters['pl_bmassj'].values
    
    planet_mass_without_nan = [x for x in planet_mass if str(x) != 'nan']
    
    if len(planet_mass_without_nan) == 0:
        return ValueError('No masses available for this system.')
    
    # get eccentricities
    
    eccentricity = system_parameters['pl_orbeccen'].values
    
    eccentricity_without_nan = [x for x in  eccentricity if str(x) != 'nan']
    
    if len(eccentricity_without_nan) == 0:
        return ValueError('No eccentricities available for this system.')
    
    # find most frequent stellar radius and report it
    
    stellar_radius_array = system_parameters['st_rad'].values
    
    stellar_radius_array_without_nan = [x for x in stellar_radius_array if str(x) != 'nan']
    
    if len(stellar_radius_array_without_nan) == 0:
        return ValueError('No stellar radius measurement available.')
    
    stellar_radius_max = [num for num, count in Counter(stellar_radius_array_without_nan).most_common(1)]
    
    stellar_radius = stellar_radius_max[0]
    
    # find most frequent stellar temp and report it
    
    stellar_temp_array = system_parameters['st_teff'].values # stellar temp array
    
    stellar_temp_array_without_nan = [x for x in stellar_temp_array if str(x) != 'nan']
    
    if len(stellar_temp_array_without_nan) == 0:
        return ValueError('No stellar temperature measurement available.')
    
    stellar_temp = [num for num, count in Counter(stellar_temp_array_without_nan).most_common(1)]
    
    return planet_radius, orbital_period, semi_major_axis, planet_mass, eccentricity, stellar_radius, stellar_temp, number_of_planets

