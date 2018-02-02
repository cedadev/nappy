import na_to_nc
import nc_to_na
import os

in_dir = "../../data_files"
out_dir = "../../test_outputs"

for ffi in (1001, 1010, 1020, 2010, 3010, 4010):

    infile = os.path.join(in_dir, "%s.na" % ffi)
    outfile = os.path.join(out_dir, "%s.nc" % ffi)

    print "Reading:", infile
    x = na_to_nc.NAToNC(infile)

    print "Writing:", outfile
    x.writeNCFile(outfile)
