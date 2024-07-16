from src import pycomo as pycomo
import cobra

community_output = "test/data/gut_community.xml"
toy_folder = "data/toy/gut"


def test_doall():
    community_model = pycomo.doall(toy_folder).model
    # Compare the output with the reference
    ref_model = cobra.io.read_sbml_model(community_output)
    assert len(community_model.metabolites) == len(ref_model.metabolites)
    assert len(community_model.reactions) == len(ref_model.reactions)
    assert len(community_model.groups) == len(ref_model.groups)
