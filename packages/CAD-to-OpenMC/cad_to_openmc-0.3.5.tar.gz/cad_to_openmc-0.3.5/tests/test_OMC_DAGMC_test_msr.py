import pathlib
import os
import openmc
import math

import CAD_to_OpenMC.assembly as ab

from tests.OMC_DAGMC_run import DAGMC_template
from tests.harnessRun import HarnessRun

class msr_DAGMC(DAGMC_template):
    def bld_mats(self):
        uf4 = openmc.Material(name='uf4')
        uf4.set_density('g/cm3', 4.5)
        uf4.add_nuclide('U231', 1.)
        uf4.add_element('F', 4.)

        helium = openmc.Material(name='he')
        helium.set_density('g/cm3', 0.001598)
        helium.add_nuclide('He4', 2.4044e-4)

        zircaloy = openmc.Material(name='zr4')
        zircaloy.set_density('g/cm3', 6.55)
        zircaloy.add_nuclide('Sn114', 0.014, 'wo')
        zircaloy.add_element('Fe', 0.00165, 'wo')
        zircaloy.add_element('Cr', 0.001, 'wo')
        zircaloy.add_element('Zr', 0.98335, 'wo')

        water = openmc.Material(name='h2o')
        water.set_density('g/cm3', 1)
        water.add_nuclide('H2', 2)
        water.add_element('O', 1)
        water.add_s_alpha_beta('c_D_in_D2O')

        # Define overall material
        self.materials = openmc.Materials([uf4, helium, zircaloy, water])

class OMC_DAGMC_harness(HarnessRun):
  def __init__(self, step):
    self.path = pathlib.Path(step)
    self.h5m = self.path.with_suffix('.h5m')
    self.nuclear_lib = pathlib.Path('tests/nuclear_data_testlib/cross_sections.xml').absolute()
    self.aa = ab.Assembly([str(self.path)], verbose = 2)
    self.tt = msr_DAGMC(self.h5m)

  def run(self):
    self.aa.run(backend='stl2', merge = True, h5m_filename = self.h5m)
    assert self.h5m.exists()
    self.tt.run()
    assert pathlib.Path('statepoint.5.h5').exists()
    self.tt.cleanup()
    self.cleanup()

def test_h5m_neutronics_test_reactor1():
  o = OMC_DAGMC_harness('examples/step_files/test_reactor1.step')
  openmc.config['cross_sections']=str(o.nuclear_lib)
  o.tt.results={'keff':(0.,0.47448),}
  o.run()

if __name__=='__main__':
  test_h5m_neutronics_test_reactor1()
