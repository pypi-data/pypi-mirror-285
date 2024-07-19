import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation
import matplotlib.animation as an
import numpy as np


#defining function that makes an ellipse 
def ellipse(phi,a,e):
    b = np.sqrt(1-e**2) * a 
    return np.array([a*np.cos(phi), b*np.sin(phi)])

#defining a function that takes the temperature of a star and returns a color based on that 
def suncolor(teff):
    """ Sun color selector 

    Selects a color for plotting the star based on its temperature 

    Args: 
        teff (float): stellar temperature (K)

    Returns: 
        color (string): color in which to plot star 
        
    """

    if teff < 3500:
        return 'red'

    if (teff >= 3500) and (teff < 5000):
        return 'orange'
    
    if (teff >= 5000) and (teff < 8000):
        return 'yellow'
    
    if (teff >= 8000) and (teff < 15000):
        return 'white'
    
    if teff >= 15000:
        return 'blue'

#defining function to make a circle 
def circle(phi,r):
    return np.array([r*np.cos(phi), r*np.sin(phi)])

#defining the function which creates an animation based on planetary parameters
def animator(a_s,pers,rs,rstar,norbs,es,tstar,system,dir):
    """ Animation function 

    Generates an animation based on the exoplanetary system input 

    Args: 
        a_s (array): semimajor axes (AU) 
        pers (array): periods of planets 
        rs (array): planetary radii (R_jup)
        rstar (float): stellar radius (R_sun)
        norbs (int): number of orbits desired in animation 
        es (array): eccentricities of planets 
        tstar (float): temperature of star (K)
        system (string): system to make the animation of 
        dir (string): directory in which to save animation (default current directory)

        Note: units are not important, as all quantities will be scaled relative to each other. 
        As long as all values use the same units, any unit system works. 

    Returns: 
        Saved animation file (.gif)
        
    """

    #finding the number of planets based on the length of input 
    nplanets = len(a_s)

    #defining the size of the plot as 2 times the maximum semimajor axis
    a_plot = 1.5*np.max(a_s)

    #setting normalizing factors such that the innermost planet has an a of 1 and period of 1
    norma = np.min(a_s)
    normper = np.min(pers)

    #normalizing planet radii such that an earth radius planet has a size of 1 
    rearth = 6.37e8
    rjupiter = 7.05e9
    normr = rearth/rjupiter

    #creating the figure and setting bounds 
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    scale = 3*a_plot
    ax.set_xlabel("{:.1f}".format(scale) + " AU",loc='right')
    ax.set_facecolor('xkcd:black')
    ax.set_title(system,loc='left')
     
    ax.axis([-a_plot/norma,a_plot/norma,-a_plot/norma,a_plot/norma])

    #plotting the star as a point in the center, increasing star size
    sun = ax.plot(0,0, marker="o",markersize = 10*rstar,color=suncolor(tstar)) 


    #setting individual cases for each possible number of planets in the system
    if nplanets == 1: 
        
        #normalizing parameters of system 
        a1 = a_s[0]/norma
        per1 = pers[0]/normper
        r1 = rs[0]/normr

        #creating the plabet object and setting size and radius based on normalized parameters
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')

        #defining the function which updates the location of the planet throughout its elliptical orbit
        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            p1.set_data([x1],[y1])
            return p1,

        #creating the animation and making it loop over 360 degrees of phi 
        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        #saving the animation 
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())
 
    if nplanets == 2: 

        a1 = a_s[0]/norma
        per1 = pers[0]/normper
        r1 = rs[0]/normr
        a2 = a_s[1]/norma
        per2 = pers[1]/normper
        r2 = rs[1]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            return p1,p2,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())

    if nplanets == 3: 

        a1 = a_s[0]/norma
        a2 = a_s[1]/norma
        a3 = a_s[2]/norma
        per1 = pers[0]/normper
        per2 = pers[1]/normper
        per3 = pers[2]/normper
        r1 = rs[0]/normr
        r2 = rs[1]/normr
        r3 = rs[2]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')
        p3, = ax.plot(0,a3, marker="o",markersize = r3,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            x3,y3 = ellipse(phi/per3,a3,es[2])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            p3.set_data([x3],[y3])
            return p1,p2,p3,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())


    if nplanets == 4: 

        a1 = a_s[0]/norma
        a2 = a_s[1]/norma
        a3 = a_s[2]/norma
        a4 = a_s[3]/norma
        per1 = pers[0]/normper
        per2 = pers[1]/normper
        per3 = pers[2]/normper
        per4 = pers[3]/normper
        r1 = rs[0]/normr
        r2 = rs[1]/normr
        r3 = rs[2]/normr
        r4 = rs[3]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')
        p3, = ax.plot(0,a3, marker="o",markersize = r3,color='xkcd:eggshell')
        p4, = ax.plot(0,a4, marker="o",markersize = r4,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            x3,y3 = ellipse(phi/per3,a3,es[2])
            x4,y4 = ellipse(phi/per4,a4,es[3])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            p3.set_data([x3],[y3])
            p4.set_data([x4],[y4])
            return p1,p2,p3,p4,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())

    if nplanets == 5: 

        a1 = a_s[0]/norma
        a2 = a_s[1]/norma
        a3 = a_s[2]/norma
        a4 = a_s[3]/norma
        a5 = a_s[4]/norma
        per1 = pers[0]/normper
        per2 = pers[1]/normper
        per3 = pers[2]/normper
        per4 = pers[3]/normper
        per5 = pers[4]/normper
        r1 = rs[0]/normr
        r2 = rs[1]/normr
        r3 = rs[2]/normr
        r4 = rs[3]/normr
        r5 = rs[4]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')
        p3, = ax.plot(0,a3, marker="o",markersize = r3,color='xkcd:eggshell')
        p4, = ax.plot(0,a4, marker="o",markersize = r4,color='xkcd:eggshell')
        p5, = ax.plot(0,a5, marker="o",markersize = r5,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            x3,y3 = ellipse(phi/per3,a3,es[2])
            x4,y4 = ellipse(phi/per4,a4,es[3])
            x5,y5 = ellipse(phi/per5,a5,es[4])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            p3.set_data([x3],[y3])
            p4.set_data([x4],[y4])
            p5.set_data([x5],[y5])
            return p1,p2,p3,p4,p5,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())

    if nplanets == 6: 

        a1 = a_s[0]/norma
        a2 = a_s[1]/norma
        a3 = a_s[2]/norma
        a4 = a_s[3]/norma
        a5 = a_s[4]/norma
        a6 = a_s[5]/norma
        per1 = pers[0]/normper
        per2 = pers[1]/normper
        per3 = pers[2]/normper
        per4 = pers[3]/normper
        per5 = pers[4]/normper
        per6 = pers[5]/normper
        r1 = rs[0]/normr
        r2 = rs[1]/normr
        r3 = rs[2]/normr
        r4 = rs[3]/normr
        r5 = rs[4]/normr
        r6 = rs[5]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')
        p3, = ax.plot(0,a3, marker="o",markersize = r3,color='xkcd:eggshell')
        p4, = ax.plot(0,a4, marker="o",markersize = r4,color='xkcd:eggshell')
        p5, = ax.plot(0,a5, marker="o",markersize = r5,color='xkcd:eggshell')
        p6, = ax.plot(0,a6, marker="o",markersize = r6,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            x3,y3 = ellipse(phi/per3,a3,es[2])
            x4,y4 = ellipse(phi/per4,a4,es[3])
            x5,y5 = ellipse(phi/per5,a5,es[4])
            x6,y6 = ellipse(phi/per6,a6,es[5])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            p3.set_data([x3],[y3])
            p4.set_data([x4],[y4])
            p5.set_data([x5],[y5])
            p6.set_data([x6],[y6])
            return p1,p2,p3,p4,p5,p6,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())

    if nplanets == 7: 

        a1 = a_s[0]/norma
        a2 = a_s[1]/norma
        a3 = a_s[2]/norma
        a4 = a_s[3]/norma
        a5 = a_s[4]/norma
        a6 = a_s[5]/norma
        a7 = a_s[6]/norma
        per1 = pers[0]/normper
        per2 = pers[1]/normper
        per3 = pers[2]/normper
        per4 = pers[3]/normper
        per5 = pers[4]/normper
        per6 = pers[5]/normper
        per7 = pers[6]/normper
        r1 = rs[0]/normr
        r2 = rs[1]/normr
        r3 = rs[2]/normr
        r4 = rs[3]/normr
        r5 = rs[4]/normr
        r6 = rs[5]/normr
        r7 = rs[6]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')
        p3, = ax.plot(0,a3, marker="o",markersize = r3,color='xkcd:eggshell')
        p4, = ax.plot(0,a4, marker="o",markersize = r4,color='xkcd:eggshell')
        p5, = ax.plot(0,a5, marker="o",markersize = r5,color='xkcd:eggshell')
        p6, = ax.plot(0,a6, marker="o",markersize = r6,color='xkcd:eggshell')
        p7, = ax.plot(0,a7, marker="o",markersize = r7,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            x3,y3 = ellipse(phi/per3,a3,es[2])
            x4,y4 = ellipse(phi/per4,a4,es[3])
            x5,y5 = ellipse(phi/per5,a5,es[4])
            x6,y6 = ellipse(phi/per6,a6,es[5])
            x7,y7 = ellipse(phi/per7,a7,es[6])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            p3.set_data([x3],[y3])
            p4.set_data([x4],[y4])
            p5.set_data([x5],[y5])
            p6.set_data([x6],[y6])
            p7.set_data([x7],[y7])
            return p1,p2,p3,p4,p5,p6,p7,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(str(system)+'.gif')

        from IPython.display import HTML
        HTML(dir+ani.to_jshtml())

    if nplanets == 8: 

        a1 = a_s[0]/norma
        a2 = a_s[1]/norma
        a3 = a_s[2]/norma
        a4 = a_s[3]/norma
        a5 = a_s[4]/norma
        a6 = a_s[5]/norma
        a7 = a_s[6]/norma
        a8 = a_s[7]/norma
        per1 = pers[0]/normper
        per2 = pers[1]/normper
        per3 = pers[2]/normper
        per4 = pers[3]/normper
        per5 = pers[4]/normper
        per6 = pers[5]/normper
        per7 = pers[6]/normper
        per8 = pers[7]/normper
        r1 = rs[0]/normr
        r2 = rs[1]/normr
        r3 = rs[2]/normr
        r4 = rs[3]/normr
        r5 = rs[4]/normr
        r6 = rs[5]/normr
        r7 = rs[6]/normr
        r8 = rs[7]/normr
        
        p1, = ax.plot(0,a1, marker="o",markersize = r1,color='xkcd:eggshell')
        p2, = ax.plot(0,a2, marker="o",markersize = r2,color='xkcd:eggshell')
        p3, = ax.plot(0,a3, marker="o",markersize = r3,color='xkcd:eggshell')
        p4, = ax.plot(0,a4, marker="o",markersize = r4,color='xkcd:eggshell')
        p5, = ax.plot(0,a5, marker="o",markersize = r5,color='xkcd:eggshell')
        p6, = ax.plot(0,a6, marker="o",markersize = r6,color='xkcd:eggshell')
        p7, = ax.plot(0,a7, marker="o",markersize = r7,color='xkcd:eggshell')
        p8, = ax.plot(0,a7, marker="o",markersize = r8,color='xkcd:eggshell')

        def update(phi):
            x1,y1 = ellipse(phi/per1,a1,es[0])
            x2,y2 = ellipse(phi/per2,a2,es[1])
            x3,y3 = ellipse(phi/per3,a3,es[2])
            x4,y4 = ellipse(phi/per4,a4,es[3])
            x5,y5 = ellipse(phi/per5,a5,es[4])
            x6,y6 = ellipse(phi/per6,a6,es[5])
            x7,y7 = ellipse(phi/per7,a7,es[6])
            x8,y8 = ellipse(phi/per7,a7,es[6])
            p1.set_data([x1],[y1])
            p2.set_data([x2],[y2])
            p3.set_data([x3],[y3])
            p4.set_data([x4],[y4])
            p5.set_data([x5],[y5])
            p6.set_data([x7],[y7])
            p7.set_data([x8],[y8])
            return p1,p2,p3,p4,p5,p6,p7,p8,

        ani = an.FuncAnimation(fig, update, interval=10, blit=True, repeat=True,
                        frames=np.linspace(0,norbs*2*np.pi,360, endpoint=False))
        ani.save(dir+str(system)+'.gif')

        from IPython.display import HTML
        HTML(ani.to_jshtml())