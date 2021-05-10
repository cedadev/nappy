import os

here = os.path.dirname(__file__)
data_files = os.path.join(here, 'testdata')
test_outputs = os.path.join(here, './test_outputs')


if not os.path.isdir(test_outputs):
    os.makedirs(test_outputs)

