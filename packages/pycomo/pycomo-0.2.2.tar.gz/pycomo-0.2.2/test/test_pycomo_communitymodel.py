from src import pycomo as pycomo
import pytest

community_output = "test/data/koch_com_model.xml"
flux_output = "test/data/gut_flux.csv"
toy_folder = "data/toy/gut"


def test_run_fva_mu_c():
    # Test if mu_c is set correctly for fva
    target_mu_c = 0.01
    toy_model = pycomo.CommunityModel.load(community_output)
    toy_model.convert_to_fixed_growth_rate(0.02)
    original_mu_c = toy_model.mu_c
    solution = toy_model.run_fva(fva_mu_c=target_mu_c)
    biomass_flux = solution.loc["community_biomass", :]

    # Check results of mu_c with model in fixed growth mode
    assert biomass_flux["min_flux"] == target_mu_c
    assert biomass_flux["max_flux"] == target_mu_c

    # Check that mu_c of the CommunityModel remains unchanged
    assert toy_model.mu_c == original_mu_c

    # Check results of mu_c with model in fixed abundance mode
    toy_model = pycomo.CommunityModel.load(community_output)
    toy_model.convert_to_fixed_abundance()
    solution = toy_model.run_fva(fva_mu_c=target_mu_c)
    biomass_flux = solution.loc["community_biomass", :]
    assert biomass_flux["min_flux"] == target_mu_c
    assert biomass_flux["max_flux"] == target_mu_c




