import os

def test_simul_gpu_results_directory():
    fname = "/d:/ProgrammationGitLab/HECEPython/wolfhece/Results2DGPU.py"
    expected_directory = os.path.join(os.path.dirname(fname), "simul_gpu_results")

    assert os.path.isdir(expected_directory), "Directory 'simul_gpu_results' does not exist"