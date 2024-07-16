from src import pycomo as pycomo
import pytest


def test_single_organism_model_empty():
    with pytest.raises(TypeError):
        test_model = pycomo.SingleOrganismModel()
