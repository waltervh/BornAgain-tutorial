"""
Fitting example: 4 parameters fit with simple output. Example explains:
* How to define fit parameters (start values, limits, steps)
* How to invoke drawing of fit progress
* How to change another minimizer, and set its properties

"""
import bornagain as ba
from bornagain import deg, angstrom, nm, AttLimits
from matplotlib import pyplot as plt


def get_sample():
    """
    Returns a sample with uncorrelated cylinders and prisms on a substrate.
    """
    # defining materials
    m_air = ba.HomogeneousMaterial("Air", 0.0, 0.0)
    m_substrate = ba.HomogeneousMaterial("Substrate", 6e-6, 2e-8)
    m_particle = ba.HomogeneousMaterial("Particle", 6e-4, 2e-8)

    # collection of particles
    cylinder_ff = ba.FormFactorCylinder(1.0*nm, 1.0*nm)
    cylinder = ba.Particle(m_particle, cylinder_ff)
    prism_ff = ba.FormFactorPrism3(1.0*nm, 1.0*nm)
    prism = ba.Particle(m_particle, prism_ff)
    particle_layout = ba.ParticleLayout()
    particle_layout.addParticle(cylinder, 0.5)
    particle_layout.addParticle(prism, 0.5)
    interference = ba.InterferenceFunctionNone()
    particle_layout.addInterferenceFunction(interference)

    # air layer with particles and substrate form multi layer
    air_layer = ba.Layer(m_air)
    air_layer.addLayout(particle_layout)
    substrate_layer = ba.Layer(m_substrate, 0)
    multi_layer = ba.MultiLayer()
    multi_layer.addLayer(air_layer)
    multi_layer.addLayer(substrate_layer)
    return multi_layer


def get_simulation():
    """
    Returns a GISAXS simulation with beam and detector defined
    """
    simulation = ba.GISASSimulation()
    simulation.setDetectorParameters(100, -1.0*deg, 1.0*deg,
                                     100, 0.0*deg, 2.0*deg)
    simulation.setBeamParameters(1.0*angstrom, 0.2*deg, 0.0*deg)
    return simulation


def run_fitting():
    """
    run fitting
    """
    sample = get_sample()
    simulation = get_simulation()
    simulation.setSample(sample)

    real_data = ba.IntensityDataIOFactory.readIntensityData(
        'refdata_fitcylinderprisms.int.gz')

    fit_suite = ba.FitSuite()
    fit_suite.addSimulationAndRealData(simulation, real_data)
    fit_suite.initPrint(10)

    # setting fitting parameters with starting values and limits
    fit_suite.addFitParameter("*Cylinder/Height", 4.*nm).setLowerLimited(0.01).setStep(0.02)
    fit_suite.addFitParameter("*Cylinder/Radius", 6.*nm).setLimited(3.0, 8.0)
    fit_suite.addFitParameter("*Prism3/Height", 4.*nm).setUpperLimited(10.0)
    fit_suite.addFitParameter("*Prism3/BaseEdge", 5.*nm).setFixed()

    # > Changing minimization algorithm
    # catalogue = ba.MinimizerCatalogue()
    # print(catalogue.toString())
    # fit_suite.setMinimizer("Minuit2", "Migrad")  # ba.Default
    # fit_suite.setMinimizer("Minuit2", "Fumili")
    # fit_suite.setMinimizer("Minuit2", "Fumili", "MaxFunctionCalls=20")
    # fit_suite.setMinimizer("GSLLMA")

    # > Drawing fit progress evey 10'th iteration
    # draw_observer = ba.DefaultFitObserver(draw_every_nth=10)
    # fit_suite.attachObserver(draw_observer)

    # running fit
    fit_suite.runFit()

    print("Fitting completed.")
    print("chi2:", fit_suite.getChi2())
    for par in fit_suite.fitParameters():
        print(par.name(), par.value(), par.error())

if __name__ == '__main__':
    run_fitting()
    plt.show()
