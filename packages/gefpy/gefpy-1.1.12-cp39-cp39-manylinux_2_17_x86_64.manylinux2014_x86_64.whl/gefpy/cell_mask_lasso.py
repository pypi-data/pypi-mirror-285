import logging
import os
import sys
import time
from optparse import OptionParser
import h5py
from gefpy import cell_mask_annotation


def print_err(case, code):
    """
    print error code
    """
    err_code = {
        "SAW-A00031": "{} is missing.",
        "SAW-A00032": "cannot access {}: No such file or directory.",
        "SAW-A00033": "file type error:{}.",
        "SAW-A00034": "information loss: {}.",
        "SAW-A00035": "{}.",
    }
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open("errcode.log", "a") as err_info:
        err_info.write(
            "[{}] {}: {}\n".format(nowtime, code, err_code[code].format(case))
        )
    sys.stderr.write("[{}] {}: {}\n".format(nowtime, code, err_code[code].format(case)))
    sys.exit(1)


def convert_str_2_bool(s: str) -> bool:
    if isinstance(s, bool):
        return s
    if isinstance(s, str):
        s = s.lower()
        return s == "true"
    return False


def main():
    Usage = """
    %prog
    -i <Gene expression matrix>
    -m <Mask/Geojson File>
    -o <output Path>
    -s <bin size>

    return gene expression matrix under cells with labels
    """
    parser = OptionParser(Usage)
    parser.add_option("-n", dest="sampleid", help="SampleID for input data. ")
    parser.add_option(
        "-i", dest="geneFile", help="Path contains gene expression matrix. "
    )
    parser.add_option("-o", dest="outpath", help="Output directory. ")
    parser.add_option("-m", dest="infile", help="Segmentation mask or geojson. ")
    parser.add_option(
        "-s", dest="bin_size", default=1, help="Bin size for annotation. "
    )
    parser.add_option(
        "-f",
        dest="flip_code",
        type=int,
        default=0,
        help="Image flip code. 0 for flip vertically, 1 for flip horizontally, -1 for both.",
    )
    parser.add_option(
        "-O", dest="omics", type=str, default="Transcriptomics", help="Omics type ."
    )
    parser.add_option(
        "-t",
        dest="transform_coor",
        type=str,
        default="false",
        help="whether transform coor by sbustract with minx/miny",
    )
    opts, args = parser.parse_args()

    if opts.sampleid == None:
        print_err("-n", "SAW-A00031")
    elif opts.geneFile == None:
        print_err("-i", "SAW-A00031")
    elif opts.outpath == None:
        print_err("-o", "SAW-A00031")
    elif opts.infile == None:
        print_err("-m", "SAW-A00031")
    elif not os.path.exists(opts.geneFile):
        print_err(os.path.abspath(opts.geneFile), "SAW-A00032")
    elif not os.path.exists(opts.infile):
        print_err(os.path.abspath(opts.infile), "SAW-A00032")

    gef_file = opts.geneFile
    if gef_file.endswith(".gef"):
        if not h5py.is_hdf5(gef_file):
            print_err(f"{gef_file} is not h5file", "SAW-A00033")
    else:
        print_err(f"{gef_file} is not h5file", "SAW-A00033")

    # file of coordinate...
    infile = opts.infile
    binsize = opts.bin_size
    # the output directory
    outpath = opts.outpath
    sampleid = opts.sampleid
    omics = opts.omics
    # whether translation point to original point!
    substract_left_top = convert_str_2_bool(opts.transform_coor)
    if substract_left_top:
        print("we will substract the minx miny ....")
    else:
        print("we will not substract....")
    try:
        seg = cell_mask_annotation.MaskSegmentation(
            sampleid, infile, gef_file, outpath, binsize, omics, substract_left_top
        )
    except Exception as ex:
        print("running with legacy mode,cased by reason {}....".format(str(ex)))
        seg = cell_mask_annotation.MaskSegmentation(
            sampleid, infile, gef_file, outpath, binsize, omics
        )
    seg.run_cellMask()


if __name__ == "__main__":
    main()


"""

cellbin =>   -n B01809A1 -i cellbin.gef -m .lasso.geojson -o ./lasso

squarebin =>   -n B01809A1 -i sn.gef -m .lasso.geojson -o ./lasso -s 1,50,200

"""
