import na_to_nc
import nc_to_na
import os

in_dir = "../../data_files"
out_dir = "../../test_outputs"
in_dir = out_dir

for ffi in (1001, 2010, 3010, 4010):

    infile = os.path.join(in_dir, "%s.nc" % ffi)
    outfile = os.path.join(out_dir, "%s_from_nc.na" % ffi)

    print("Reading:", infile)
    x = nc_to_na.NCToNA(infile)

    print("Writing:", outfile)
    x.writeNAFiles(outfile)
