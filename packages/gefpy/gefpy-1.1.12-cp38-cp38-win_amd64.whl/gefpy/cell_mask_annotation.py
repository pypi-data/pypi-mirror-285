# -*- coding: utf-8 -*-

import logging
import os

os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
import sys
import gc
from optparse import OptionParser

import cv2
import geojson
import h5py
import numpy as np
import pandas as pd
import tifffile as tifi
from gefpy.cgef_adjust_cy import CgefAdjust
from gefpy.gef_to_gem_cy import gefToGem

logging.basicConfig(format="%(asctime)s - %(name)s - %(message)s", level=logging.DEBUG)


def generate_cell_mask_from_cellbin_file(
    cellbin_file: str, output_image_file, fill_value: int = 255
) -> bool:
    if fill_value < 0:
        fill_value = 0
    if fill_value > 255:
        fill_value = 255
    if not os.path.exists(cellbin_file):
        print("the given cell bin file is not exist!")
        return False
    output_image_dir = os.path.dirname(output_image_file)
    if output_image_dir and not os.path.exists(output_image_dir):
        # create the image dir to save the file!
        os.makedirs(output_image_dir)

    legacy_pad_value = 0
    pad_value = 32767
    with h5py.File(cellbin_file, mode="r", locking=False) as file_handler:
        try:
            cell_border_dataset = file_handler["cellBin/cellBorder"]
            cell_dataset = file_handler["cellBin/cell"]
        except Exception as ex:
            print(
                "fail to get cell border/cell dataset,the reason is {}".format(str(ex))
            )
            return False

        # then read the range of dataset!
        try:
            xmin = file_handler.attrs["offsetX"][0]
            ymin = file_handler.attrs["offsetY"][0]
            xmax = file_handler.attrs["maxX"][0]
            ymax = file_handler.attrs["maxY"][0]
        except Exception as ex:
            print("fail to read the attrs!")
            return False
        cell_border_mat = cell_border_dataset[:]
        cell_center_xs = cell_dataset["x"]
        cell_center_ys = cell_dataset["y"]

    if xmin > xmax or ymin > ymax:
        print(
            "the range from cell bin file is invalid,see xmin:{} ymin:{} xmax:{} ymax:{}".format(
                xmin, ymin, xmax, ymax
            )
        )
        return False

    height: int = ymax - ymin + 1
    width: int = xmax - xmin + 1
    cell_poygons = []
    cell_num, point_size, coor_size = cell_border_mat.shape
    print("the padding point size per cell is {}".format(point_size))
    if len(cell_center_xs) != cell_num:
        print(
            "the cell dataset size not equal to the cell border dataset size,we can not match one by one!"
        )
        return False
    if coor_size != 2:
        print(
            "the cell border should be an 2d cooridnates,but we get {}".format(
                coor_size
            )
        )
        return False

    # x,y can not be the pad value!
    cell_index_mask = cell_border_mat != pad_value
    cell_index_mask = np.all(cell_index_mask, axis=2)

    for i in range(cell_num):
        polygon = cell_border_mat[i][cell_index_mask[i]].astype(np.int32)
        polygon[:, 0] += cell_center_xs[i]
        polygon[:, 1] += cell_center_ys[i]
        cell_poygons.append(polygon)
    # now we can filling by the polygon!
    cell_image_mask = np.zeros(shape=(height, width), dtype=np.uint8)
    cv2.fillPoly(cell_image_mask, cell_poygons, fill_value)
    tifi.imwrite(
        output_image_file,
        cell_image_mask,
        compression="zlib",
        compressionargs={"level": 8},
    )
    return True


class MaskSegmentation:
    def __init__(
        self, sampleid, infile, geneFile, outpath, binsize, omics="Transcriptomics"
    ):
        self.sampleid = sampleid
        self.bin_size = binsize
        self.outpath = outpath
        self.infile = infile
        self.geneFile = geneFile
        self.omics_type = omics

    def convertMask(self, label):
        """
        将二值mask, 转为按细胞编号的32bit/64bit的label
        """
        tifi.imwrite(
            os.path.join(self.gem_path, f"{self.sampleid}.lasso.{label}.mask.tif"),
            self.maskFile,
        )
        labels = self.maskFile
        return labels

    def generate_mask(self, bin_size, label, uID, gef_file):
        if gef_file.endswith(".gef"):
            with h5py.File(gef_file, "r") as gef_f:
                self.x1 = gef_f["geneExp"][f"bin{bin_size}"]["expression"].attrs[
                    "minX"
                ][0]
                self.y1 = gef_f["geneExp"][f"bin{bin_size}"]["expression"].attrs[
                    "minY"
                ][0]
                self.y2 = gef_f["geneExp"][f"bin{bin_size}"]["expression"].attrs[
                    "maxY"
                ][0]
                self.x2 = gef_f["geneExp"][f"bin{bin_size}"]["expression"].attrs[
                    "maxX"
                ][0]
                self.ori_shape = (self.y2 - self.y1 + 1, self.x2 - self.x1 + 1)
                for i in self.raw_areas:
                    i[:, 0] = i[:, 0] - self.x1
                    i[:, 1] = i[:, 1] - self.y1

                self.maskFile = np.zeros(self.ori_shape, np.uint8)
                cv2.fillPoly(self.maskFile, self.raw_areas, 1)
                self.convertMask(label)

    def saptialbin_lasso_process(self):
        with open(self.infile, encoding="UTF-8-sig") as geofile:
            gj = geojson.load(geofile)

        for i in gj["geometries"]:
            areas = []
            self.raw_areas = []
            for idx in range(len(i["coordinates"])):
                area = np.array(i["coordinates"][idx]).flatten()
                raw_area = np.array(i["coordinates"][idx])
                areas.append(area.astype(np.uint32))
                self.raw_areas.append(raw_area)

            uID = i["properties"]["uID"] + 1
            if "label" in i["properties"]:
                label = i["properties"]["label"]
            else:
                label = f"{uID}"

            os.makedirs(os.path.join(self.outpath, label), exist_ok=True)
            tmp_outpath = os.path.join(self.outpath, f"{label}")
            os.makedirs(os.path.join(tmp_outpath, "segmentation"), exist_ok=True)
            self.gem_path = os.path.join(tmp_outpath, f"segmentation")
            gef_outpath = ""
            if self.omics_type == "Transcriptomics":
                gef_outpath = os.path.join(
                    tmp_outpath, f"{self.sampleid}.{label}.label.gef"
                )
            else:
                gef_outpath = os.path.join(
                    tmp_outpath, f"{self.sampleid}.protein.{label}.label.gef"
                )

            # 1. generate bgef
            cg = CgefAdjust()
            lasso_binsize = str(self.bin_size).split(",")
            cg.set_lasso_binsize(lasso_binsize)
            cg.create_Region_Bgef(self.geneFile, gef_outpath, areas)

            if os.path.exists(gef_outpath):
                # 2. generate mask
                self.generate_mask(1, label, uID, gef_outpath)
                # 3. generate bgem
                for i in str(self.bin_size).split(","):
                    strout = os.path.join(
                        self.gem_path, f"{self.sampleid}.lasso.bin{i}.{label}.gem"
                    )
                    obj = gefToGem(strout, self.sampleid)
                    obj.bgef2gem(gef_outpath, int(i))
                    os.system("gzip -f %s" % (strout))
            else:
                logging.error("generate gene file failed. ")
                return

    def run_cellMask(self):
        if self.geneFile.endswith(".gef"):
            gef_f = h5py.File(self.geneFile, "r")
            if "omics" in gef_f.attrs:
                if (
                    bytes(self.omics_type, encoding="utf8")
                    not in gef_f.attrs["omics"].tolist()
                ):
                    logging.error(
                        f"-O information does not match the omics recorded in {self.geneFile}, please check input parameter or files."
                    )
                    return
            else:
                if self.omics_type != "Transcriptomics":
                    logging.error(
                        f"-O information does not match the omics recorded in {self.geneFile}, please check input parameter or files."
                    )
                    return

            if "cellBin" in gef_f:
                # cell bin
                # read the max area..
                gef_f.close()
                with open(self.infile, encoding="UTF-8-sig") as geofile:
                    gj = geojson.load(geofile)
                cg = CgefAdjust()
                polygons = []
                for i in gj["geometries"]:
                    areas = []
                    for idx in range(len(i["coordinates"])):
                        polygon = np.array(i["coordinates"][idx]).astype(np.int32)
                        polygons.append(polygon)
                        flat_polygon = polygon.flatten()
                        areas.append(flat_polygon)
                    label = i["properties"]["label"]
                    label_dir: str = os.path.join(self.outpath, label)
                    if not os.path.exists(label_dir):
                        os.makedirs(label_dir)
                    # os.makedirs(os.path.join(self.outpath, label), exist_ok=True)
                    tmp_outpath = ""
                    if self.omics_type == "Transcriptomics":
                        tmp_outpath = os.path.join(
                            os.path.join(self.outpath, label),
                            f"{self.sampleid}.{label}.label.cellbin.gef",
                        )
                    else:
                        tmp_outpath = os.path.join(
                            os.path.join(self.outpath, label),
                            f"{self.sampleid}.protein.{label}.label.cellbin.gef",
                        )

                    ret = cg.create_Region_Cgef(self.geneFile, tmp_outpath, areas)
                    if ret:
                        # fill the mask and output to the tiff format!
                        output_image_file = os.path.join(
                            label_dir,
                            "{}.lasso.cellbin.{}.mask.tiff".format(
                                self.sampleid, label
                            ),
                        )
                        print(tmp_outpath)
                        generate_cell_mask_from_cellbin_file(
                            cellbin_file=tmp_outpath,
                            output_image_file=output_image_file,
                            fill_value=255,
                        )
                    else:
                        print(
                            "we will not generate any mask file for invallid polygon..."
                        )
            else:
                # spatial bin
                gef_f.close()
                self.saptialbin_lasso_process()
        else:
            logging.warning("Genefile is not gef file...")


def getGefPath(file_dir):
    if os.path.exists(file_dir) and os.path.isdir(file_dir):
        for root, dirs, files in os.walk(file_dir, topdown=False):
            for i in files:
                path = os.path.join(root, i)
                if (
                    not path.endswith(".tissue.gef")
                    and not path.endswith(".cellbin.gef")
                    and not path.endswith(".raw.gef")
                    and not path.endswith(".tissue.protein.gef")
                    and not path.endswith(".cellbin.protein.gef")
                    and not path.endswith(".raw.protein.gef")
                    and path.endswith(".gef")
                ):
                    gef_file = path
                    print(gef_file)
                    return gef_file
    return ""


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
        "-i", dest="geneFilePath", help="Path contains gene expression matrix. "
    )
    parser.add_option("-o", dest="outpath", help="Output directory. ")
    parser.add_option("-m", dest="infile", help="Segmentation mask or geojson. ")
    parser.add_option(
        "-s", dest="bin_size", type=int, default=1, help="Bin size for annotation. "
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
    opts, args = parser.parse_args()

    if not opts.geneFilePath or not opts.outpath or not opts.infile:
        logging.error("Inputs are not correct")
        sys.exit(not parser.print_usage())

    gef_file = getGefPath(opts.geneFilePath)
    if gef_file and os.path.exists(gef_file):
        geneFile = gef_file
    elif os.path.exists(os.path.join(opts.geneFilePath, "stereomics.h5")):
        geneFile = os.path.join(opts.geneFilePath, "stereomics.h5")
    elif os.path.exists(
        os.path.join(
            opts.geneFilePath, "gene_merge", f"merge_gene_bin{opts.bin_size}.pickle"
        )
    ):
        geneFile = os.path.join(
            opts.geneFilePath, "gene_merge", f"merge_gene_bin{opts.bin_size}.pickle"
        )
    elif os.path.exists(os.path.join(opts.geneFilePath, "merge_GetExp_gene.txt")):
        geneFile = os.path.join(opts.geneFilePath, "merge_GetExp_gene.txt")
    else:
        geneFile = ""

    if not geneFile:
        logging.error("Input gene file does not exist")
        sys.exit(1)

    infile = opts.infile
    binsize = opts.bin_size
    outpath = opts.outpath
    sampleid = opts.sampleid
    omics = opts.omics

    seg = MaskSegmentation(sampleid, infile, geneFile, outpath, binsize, omics)
    seg.run_cellMask()


if __name__ == "__main__":
    main()
