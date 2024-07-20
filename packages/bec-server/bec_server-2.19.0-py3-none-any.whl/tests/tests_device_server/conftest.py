import pytest

from bec_lib.logger import bec_logger

### THE NEXT FIXTURE HAS TO BE RE-ACTIVATED ONCE
### OPHYD "STATUS CALLBACKS" THREADS ARE CLEANED
### (NEXT OPHYD RELEASE)
# overwrite threads_check fixture from bec_lib,
# to have it in autouse

# @pytest.fixture(autouse=True)
# def threads_check(threads_check):
#    yield
#    bec_logger.logger.remove()
###
### MEANWHILE, THIS FIXTURE WILL JUST CLEAN LOGGER
### THREADS, AND THERE WILL BE NO CHECK FOR DANGLING
### THREADS FOR DEVICE SERVER TESTS (LIKE BEFORE...)


@pytest.fixture(autouse=True)
def threads_check():
    yield
    bec_logger.logger.remove()
