import numpy as np
from zacrostools.read_functions import parse_general_output, get_data_specnum, get_species_sites_dict
from zacrostools.custom_exceptions import *


class KMCOutput:
    """A class that represents a KMC output

    Parameters
    ----------
    path: str
        Path of the directory containing the output files.
    ignore: float (optional)
        Ignore first % of simulated time, i.e., equilibration (in %). Default value: 0.0.
    weights: str (optional)
        Weights for the averages. Possible values: 'time', 'events', None. If None, all weights are set to 1.
        Default value: None.


    Attributes
    ----------
    n_gas_species: int
        Number of gas species.
    gas_species_names: list of str
        Gas species names.
    n_surf_species: int
        Number of surface species.
    surf_species_names: list of str
        Surface species names.
    n_sites: int
        Total number of lattice sites.
    area: float
        Lattice surface area (in Å^2)
    site_types: dict
        Site type names and total number of sites of that type
    time: np.Array
        Simulated time (in s).
    final_time: float
        Final simulated time (in s).
    energy: np.Array
        Lattice energy (in eV·Å^-2).
    av_energy: float
        Average lattice energies (in eV·Å^-2).
    final_energy: float
        Final lattice energy (in eV·Å^-2).
    production: dict
        Gas species produced. Example: KMCOutput.production['CO']
    total_production: dict
        Total number of gas species produced. Example: KMCOutput.total_production['CO']
    tof: dict
        TOF of gas species (in molec·s^-1·Å^-2). Example: KMCOutput.tof['CO2']
    coverage: dict
        Coverage of surface species (in %). Example: KMCOutput.coverage['CO']
    av_coverage: dict
        Average coverage of surface species (in %). Example: KMCOutput.av_coverage['CO']
    total_coverage: np.Array
        Total coverage of surface species (in %).
    av_total_coverage: float
        Average total coverage of surface species (in %).
    dominant_ads: str
        Most dominant surface species, to plot the kinetic phase diagrams.
    coverage_per_site_type: dict
        Coverage of surface species per site type (in %).
    av_coverage_per_site_type: dict
        Average coverage of surface species per site type (in %).
    total_coverage_per_site_type: dict
        Total coverage of surface species per site type (in %). Example: KMCOutput.total_coverage_per_site_type['top']
    av_total_coverage_per_site_type: dict
        Average total coverage of surface species per site type (in %).
    dominant_ads_per_site_type: dict
        Most dominant surface species per site type, to plot the kinetic phase diagrams.
    """

    @enforce_types
    def __init__(self, path: str, ignore: Union[float, int] = 0.0, weights: Union[str, None] = None):

        self.path = path

        # Get data from general_output.txt file
        data_general = parse_general_output(path)
        self.n_gas_species = data_general['n_gas_species']
        self.gas_species_names = data_general['gas_species_names']
        self.n_surf_species = data_general['n_surf_species']
        self.surf_species_names = data_general['surf_species_names']
        self.n_sites = data_general['n_sites']
        self.area = data_general['area']
        self.site_types = data_general['site_types']

        # Get data from specnum_output.txt file
        ignore = float(ignore)
        data_specnum, header = get_data_specnum(path, ignore)
        self.nevents = data_specnum[:, 1]
        self.time = data_specnum[:, 2]
        self.final_time = data_specnum[-1, 2]
        self.energy = data_specnum[:, 4] / self.area  # in eV/Å2
        self.final_energy = data_specnum[-1, 4] / self.area
        self.av_energy = self.get_average(array=self.energy, weights=weights)

        # Compute production and TOF
        self.production = {}  # in molec
        self.total_production = {}  # useful when calculating selectivity (i.e., set min_total_production)
        self.tof = {}  # in molec·s^-1·Å^-2
        for i in range(5 + self.n_surf_species, len(header)):
            gas_spec = header[i]
            self.production[gas_spec] = data_specnum[:, i]
            self.total_production[gas_spec] = data_specnum[-1, i] - data_specnum[0, i]
            if data_specnum[-1, i] != 0:
                self.tof[header[i]] = np.polyfit(data_specnum[:, 2], data_specnum[:, i], 1)[0] / self.area
            else:
                self.tof[header[i]] = 0.00

        # Compute coverages (per total number of sites)
        self.coverage = {}
        self.av_coverage = {}
        for i in range(5, 5 + self.n_surf_species):
            surf_spec = header[i].replace('*', '')
            self.coverage[surf_spec] = data_specnum[:, i] / self.n_sites * 100
            self.av_coverage[surf_spec] = self.get_average(array=self.coverage[surf_spec], weights=weights)
        self.total_coverage = sum(self.coverage.values())
        self.av_total_coverage = min(sum(self.av_coverage.values()), 100)  # to prevent 100.00000000001 (num. error)
        self.dominant_ads = max(self.av_coverage, key=self.av_coverage.get)

        # Compute partial coverages (per total number of sites of a given type)
        ads_sites = get_species_sites_dict(self.path)
        self.coverage_per_site_type = {}
        self.av_coverage_per_site_type = {}
        for site_type in self.site_types:
            self.coverage_per_site_type[site_type] = {}
            self.av_coverage_per_site_type[site_type] = {}
        for i in range(5, 5 + self.n_surf_species):
            surf_spec = header[i].replace('*', '')
            site_type = ads_sites[surf_spec]
            self.coverage_per_site_type[site_type][surf_spec] = data_specnum[:, i] / self.site_types[
                ads_sites[surf_spec]] * 100
            self.av_coverage_per_site_type[site_type][surf_spec] = self.get_average(
                array=self.coverage_per_site_type[site_type][surf_spec], weights=weights)
        self.total_coverage_per_site_type = {}
        self.av_total_coverage_per_site_type = {}
        self.dominant_ads_per_site_type = {}
        for site_type in self.site_types:
            self.total_coverage_per_site_type[site_type] = sum(self.coverage_per_site_type[site_type].values())
            self.av_total_coverage_per_site_type[site_type] = min(sum(
                self.av_coverage_per_site_type[site_type].values()), 100)  # to prevent 100.00000000001 (num. error)
            self.dominant_ads_per_site_type[site_type] = max(self.av_coverage_per_site_type[site_type],
                                                             key=self.av_coverage_per_site_type[site_type].get)

    def get_average(self, array, weights):

        if weights not in [None, 'time', 'events']:
            raise KMCOutputError(f"'weights' must be one of the following: 'none' (default), 'time', or 'events'.")

        if weights is None:
            return np.average(array)
        elif weights == 'time':
            return np.average(array[1:], weights=np.diff(self.time))
        elif weights == 'events':
            return np.average(array[1:], weights=np.diff(self.nevents))

    @enforce_types
    def get_selectivity(self, main_product: str, side_products: list):
        """
        Get the selectivity.

        Parameters
        ----------
        main_product: str
            Name of the main product
        side_products: list of str
            Names of the side products

        """
        selectivity = float('NaN')
        tof_side_products = 0.0
        for side_product in side_products:
            tof_side_products += self.tof[side_product]
        if self.tof[main_product] + tof_side_products != 0:
            selectivity = self.tof[main_product] / (self.tof[main_product] + tof_side_products) * 100
        return selectivity
