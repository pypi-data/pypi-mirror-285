from astropy import units as u
from ExoViz.parameterquery import query_parameters
import ExoViz.anim_function
from ExoViz.anim_function import animator

#example to use query to get planet_radius, orbital_period, semi_major_axis, planet_mass, eccentricity,
# stellar_radius, stellar_temp
def exoanim(system, norbs, dir=''):
    """ Calls query and animation function 

    Queries exoplanet database to generate an animation based on the exoplanetary system input 

    Args: 
        system (string): system to make the animation of 
        norbs (int): number of orbits desired in animation 
        dir (string): directory in which to save animation (default current directory)

    Returns: 
        Saved animation file (.gif)
        
    """

    if type(system) != str: 
        return ValueError("System name not entered as string")
    
    if type(norbs) != int: 
        return ValueError("Orbit number not entered as integer")
    
    if type(dir) != str: 
        return ValueError("Saving directory not entered as string")


    planets = query_parameters(system)
    
    rs = planets[0]
    pers = planets[1]
    a_s = planets[2]
    m_s = planets[3]
    es = planets[4]
    rstar = planets[5]
    tstar = planets[6]
    
    animator(a_s,pers,rs,rstar,norbs,es,tstar,system,dir)
    
