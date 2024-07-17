import numpy as np
import os
from rail.core.stage import RailStage
from rail.utils.testing_utils import one_algo
from rail.utils.path_utils import RAILDIR
from rail.estimation.algos.gpz import GPzInformer, GPzEstimator
import scipy.special
sci_ver_str = scipy.__version__.split(".")


traindata = os.path.join(RAILDIR, "rail/examples_data/testdata/training_100gal.hdf5")
validdata = os.path.join(RAILDIR, "rail/examples_data/testdata/validation_10gal.hdf5")
DS = RailStage.data_store
DS.__class__.allow_overwrite = True


def test_gpz_v1():
    train_config_dict = {"hdf5_groupname": "photometry", "max_iter": 30, "max_attempt": 25,
                         "model": "gpz_default.pkl"}
    estim_config_dict = {"hdf5_groupname": "photometry", "model": "gpz_default.pkl"}
    train_algo = GPzInformer
    pz_algo = GPzEstimator
    zb_expected = np.array([0.12, 0.13, 0.12, 0.14, 0.07, 0.13, 0.14, 0.13,
                            0.06, 0.12])
    results, rerun_results, _ = one_algo("GPz_v1", train_algo, pz_algo,
                                         train_config_dict, estim_config_dict)
    flatres = results.ancil["zmode"].flatten()
    assert np.isclose(flatres, zb_expected, atol=2.e-02).all()
    assert np.isclose(results.ancil["zmode"], rerun_results.ancil["zmode"]).all()
