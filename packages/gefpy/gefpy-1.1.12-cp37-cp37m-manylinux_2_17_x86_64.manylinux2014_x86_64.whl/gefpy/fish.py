import logging
import json
import cv2
import h5py
from typing import Dict, Any, List, Sequence, Union

import tifffile as tifi

from gefpy.cgef_adjust_cy import CgefAdjust
import os
import numpy as np
import sys
import gzip
import pandas as pd


# a simple logger to record the program pipeline!
class WrapedLogger(object):
    logger: logging.Logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)
    # set the format
    log_format: logging.Formatter = logging.Formatter(
        "[%(asctime)s %(filename)s %(funcName)s %(lineno)s %(levelname)s]:%(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    # you can add file to it,but it is not need!

    @staticmethod
    def get_logger() -> logging.Logger:
        return WrapedLogger.logger


def write_csv_file(
    file_path: str,
    write_datas: List[Sequence] = None,
    header: List[str] = None,
    sep: str = "\t",
    check_dir: bool = True,
) -> None:
    absoulute_file_path = os.path.abspath(file_path)
    file_dir = os.path.dirname(absoulute_file_path)
    if check_dir and (not os.path.exists(file_dir)):
        os.makedirs(file_dir)
    with open(write_csv_file, "w", encoding="utf-8") as f:
        if header is not None:
            header_str = sep.join(header)
            f.write(header_str)
            f.write("\n")
        for data in write_datas:
            data = [str(x) for x in data]
            data_str = sep.join(data)
            f.write(data_str)
            f.write("\n")


class PolygonMeta(object):
    def __init__(
        self, label: str, uid: int = None, polygons: List[np.ndarray] = None
    ) -> None:
        """
        Args:
            label:str,the label of this polygon
            uid:str,just a id specify
            polygons:a list contains the coordinates...
        """
        self.label = label
        self.uid = uid
        self.polygons = polygons


class Rect(object):
    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.min_x = x1
        self.min_y = y1
        self.max_x = x2
        self.max_y = y2


# define some constant
TRANSCRIPT_OMICS = "Transcriptomics"
PROTEIN_OMICS = "Proteomics"


class MaskSegmentation(object):
    def __init__(
        self,
        sample_id: str,
        polygon_file: str,
        gene_file: str,
        output_dir: str,
        bin_size: int = 1,
        omics: str = TRANSCRIPT_OMICS,
        substract_leftop_coordinate: bool = True,
        fill_mask_value: int = 255,
        write_csv_sep: str = "\t",
        compress_level: int = 6,
        gem_output_add_gz_suffix: bool = True,
        io_encoding: str = "utf-8",
        write_batch_size: int = 6000000,
        **kwargs,
    ) -> None:
        """
        Args:
            sample_id:str,the seq name,just a prefix to create the file...
            polygon_file:a json file,contains the coordinates,and will be used to fill a polygon
            gene_file:str,a hdf5 file,contains the meta datas of gene
            output_dir:str,the dir to save our result
            bin_size:int,should be positive,a block size to split the large matrix!
            omics:str,for biology....
            substract_lefttop:bool,if True,all the coor will do transform x = x - minx,y = y - miny
            compress_level:the output file will use the gzip to compress,the default param on linux is 6,to keep the same feature,we also set default value as 6
        """
        self.logger: logging.Logger = WrapedLogger.get_logger()
        self.gem_output_add_gz_suffix = gem_output_add_gz_suffix
        self.io_encoding: str = io_encoding
        self.logger.info("the csv file encoding is {}".format(self.io_encoding))
        # check the input file is valid!
        self.sample_id = sample_id
        self.logger.info("process sample id {}".format(sample_id))
        self.omics = omics
        self.logger.info("omics:{}".format(omics))
        for file_path in (polygon_file, gene_file):
            if not os.path.exists(file_path):
                error_msg = "the specify file path {} is not exist!".format(
                    os.path.abspath(file_path)
                )
                self.logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        self.polygon_file = polygon_file
        self.logger.info("polygon file:{}".format(self.polygon_file))
        self.gene_file = gene_file
        self.logger.info("gene file:{}".format(self.gene_file))
        self.output_dir = output_dir

        if not isinstance(bin_size, int):
            error_msg = "we expect bin_size has type int,but get type {}".format(
                bin_size
            )
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        # check the bin_size is a positive interger!
        if bin_size <= 0:
            error_msg = "the bin_size should be a positive number,but get {} which is unexpected!".format(
                bin_size
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        self.bin_size = bin_size

        self._create_dir(self.output_dir)
        self.substract_leftop_coordinate = substract_leftop_coordinate
        if not isinstance(fill_mask_value, int):
            error_msg = "tne fill mask value must be int,but get type {}".format(
                type(fill_mask_value)
            )
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        if fill_mask_value < 0:
            self.logger.info(
                "invalid fill mask value {},we will set it to 0".format(fill_mask_value)
            )
            fill_mask_value = 0
        if fill_mask_value > 255:
            self.logger.info(
                "invalid fill mask value {},we will set it to 255".format(
                    fill_mask_value
                )
            )
            fill_mask_value = 255
        self.fill_mask_value = fill_mask_value
        self.write_csv_sep: str = write_csv_sep
        if not isinstance(compress_level, int):
            error_msg = "the compress level need int,but get type {}".format(
                type(compress_level)
            )
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        # however,the supported compress level is 0 ~ 9
        if compress_level < 0:
            self.logger.info(
                "invalid compress level {},we will set to 0!".format(compress_level)
            )
            compress_level = 0
        if compress_level > 9:
            self.logger.info(
                "invalid compress level {},we will set to 9".format(self.compress_level)
            )
            compress_level = 9

        self.compress_level: int = compress_level
        self.logger.info(
            "the compress level for gzip is {}".format(self.compress_level)
        )

        self.write_batch_size: int = write_batch_size

    def _create_dir(self, dir_path: str) -> None:
        if not os.path.exists(dir_path):
            self.logger.info("creating directory '{}'".format(dir_path))
            os.makedirs(dir_path)
        else:
            self.logger.info("'{}' is already exit,noting to do...".format(dir_path))

    @staticmethod
    def _is_transcript_omics(omics_str: str) -> bool:
        return omics == TRANSCRIPT_OMICS

    @staticmethod
    def _is_protein_omics(omics_str: str) -> bool:
        return omics == PROTEIN_OMICS

    def _is_gef_format_file(self, file_path: str) -> bool:
        if file_path.endswith("gef"):
            self.logger.info("{} ends with gef which is expected!".format(file_path))
            return True
        else:
            self.logger.info(
                "file {} is not endswith gef,maybe is a broken file format!".format(
                    file_path
                )
            )
            return False

    def _get_value_from_dict(self, key: str, data_dict: Dict[str, Any]) -> Any:
        """
        if the key not in the data dict,will raise KeyError!
        """
        if key not in data_dict:
            error_msg = "missing key {} in json file {}".format(key, self.polygon_file)
            self.logger.error(error_msg)
            raise KeyError(error_msg)
        return data_dict[key]

    def _fill_polygons_and_write_to_file(
        self,
        height: int,
        width: int,
        polygons: List[np.ndarray] = None,
        return_filled_mask: bool = True,
        file_path: str = None,
    ) -> Union[np.ndarray, None]:
        """
        Args:
            height:int,the value of image height
            width:int,the value of image_width
            polygons:a list contains the coordinates,the coordinates should be a 2-D array
            return_filled_mask:bool,if true,will return filled mask!
            file_path:str,the file path to write the image!
        """
        # check the params!
        for name, value in zip(["height", "width"], [height, width]):
            if not isinstance(value, int):
                error_msg = "{} should be int,but get type {}".format(name, type(value))
                self.logger.error(error_msg)
                raise TypeError(error_msg)
            if value <= 0:
                error_msg = "{} can not be negative,but get {}".format(name, value)
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        for polygon in polygons:
            if not isinstance(polygon, np.ndarray):
                error_msg = "polygon should be list of ndarray,but contains {}".format(
                    type(polygon)
                )
                self.logger.error(error_msg)
                raise TypeError(error_msg)
            shape = polygon.shape
            if len(shape) != 2:
                error_msg = "the polygon should be 2-D array,but get shape {}".format(
                    shape
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)

            if shape[1] != 2:
                error_msg = "the cooridnates should be 2d,but get shape {}".format(
                    shape
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        absolute_file_path = os.path.abspath(file_path)
        parent_directory = os.path.dirname(absolute_file_path)
        self._create_dir(parent_directory)
        self.logger.info("fill the specify polygon...")
        self.logger.info("create mask with height:{} width:{}".format(height, width))
        mask = np.zeros(shape=(height, width), dtype=np.uint8)
        cv2.fillPoly(mask, pts=polygons, color=self.fill_mask_value)
        filled_cnt = np.sum(mask == self.fill_mask_value)
        self.logger.info("filled {} points with specify polygon!".format(filled_cnt))
        self.logger.info("write the image with tif format to {}".format(file_path))
        tifi.imwrite(file_path, data=mask)
        if return_filled_mask:
            self.logger.info("return the filled mask!")
            return mask
        else:
            self.logger.info("return None without filled mask!")

    def _guess_polygon_is_transformed(
        self, polygons: List[np.ndarray] = None, min_x: int = 0, min_y: int = 0
    ) -> bool:
        """
        if find the coor value less than min_x and min_y,the coordinates is already substranct the left top
            so,even the caller set substact the coordinate,we will not do the substract!
        Args:
            polygons:list of polygon
            min_x:int,the x coordinate of left top!
            max_x:int,the y coordinate of the left top
        """
        for polygon in polygons:
            # guess the x
            all_x_coors = polygon[:0]
            x_coor_mask = all_x_coors < min_x
            less_than_x_sum: int = np.sum(x_coor_mask)
            if less_than_x_sum > 0:
                self.logger.info(
                    "find some x coordinates less than min_x,so we guess the polygons is already substacted!"
                )
                return True
            # guess the y
            all_y_coors = polygon[:1]
            y_coor_mask = all_y_coors < min_y
            less_than_y_sum: int = np.sum(y_coor_mask)
            if less_than_y_sum > 0:
                self.logger.info(
                    "find some y coordinates less than min_y,so we guess the polygons is already substracted!"
                )
                return True
        return False

    def _read_polygon_metas_from_json_file(self) -> List[PolygonMeta]:
        polygon_metas: List[PolygonMeta] = []
        with open(self.polygon_file, "r", encoding="utf-8-sig") as f:
            polygon_dict = json.load(f)
            self.logger.info(
                "load the polygon coordinates info from file {}".format(
                    self.polygon_file
                )
            )
            geometries_key: str = "geometries"
            geometries: List[Dict[str, Any]] = self._get_value_from_dict(
                geometries_key, polygon_dict
            )

            for geometry in geometries:
                polygons: List[np.ndarray] = []
                coordinates_key = "coordinates"
                self.logger.info("append the coordinates")
                coordinates = self._get_value_from_dict(coordinates_key, geometry)
                for index in range(len(coordinates)):
                    polygon = np.array(coordinates[index])
                    polygon = polygon.astype(np.int32)
                    polygons.append(polygon)

                property_key = "properties"
                properties: Dict[str, Any] = self._get_value_from_dict(
                    property_key, geometry
                )

                label_key: str = "label"
                label: str = self._get_value_from_dict(label_key, properties)

                uid_key = "uID"
                uid: int = self._get_value_from_dict(uid_key, properties)
                polygon_meta = PolygonMeta(label=label, uid=uid, polygons=polygons)
                polygon_metas.append(polygon_meta)
        return polygon_metas

    def _check_coordinates_contains_negative(self, coordinates: np.ndarray) -> bool:
        """
        if the coor have negative ...
        """
        negative_mask = coordinates < 0
        negative_cnt = np.sum(negative_mask)
        if negative_cnt > 0:
            self.logger.info(
                "find {} negative coordinates,which is unexpected!".format(negative_cnt)
            )
            return True
        return False

    @staticmethod
    def _read_coordinate_ranges_from_file(
        file_path: str,
        min_x_attr_name: str = "minX",
        min_y_attr_name: str = "minY",
        max_x_attr_name: str = "maxX",
        max_y_attr_name: str = "maxY",
        attr_loc_name: str = None,
    ) -> Rect:
        min_x_attr_name: str = "minX"
        min_y_attr_name: str = "minY"
        max_x_attr_name: str = "maxX"
        max_y_attr_name: str = "maxY"
        with h5py.File(file_path, "r") as file_handler:
            # avoid get zero!
            min_x = file_handler[attr_loc_name].attrs[min_x_attr_name][0]
            min_y = file_handler[attr_loc_name].attrs[min_y_attr_name][0]
            max_x = file_handler[attr_loc_name].attrs[max_x_attr_name][0]
            max_y = file_handler[attr_loc_name].attrs[max_y_attr_name][0]
        rect = Rect(x1=int(min_x), y1=int(min_y), x2=int(max_x), y2=int(max_y))
        return rect

    def _append_data_to_csv(
        self,
        file_path: str,
        write_data_frame: pd.DataFrame = None,
        with_header: bool = True,
    ) -> None:
        compress_dict = {
            "method": "gzip",
            "compresslevel": self.compress_level,
            # "mttime":1
        }
        write_data_frame.to_csv(
            file_path,
            sep=self.write_csv_sep,
            compression=compress_dict,
            mode="a",
            header=with_header,
            index=False,
        )

    def _single_bin_process(
        self,
        bin_size: int,
        label: str,
        # not used!
        uid: int,
        gem_directory: str,
        polygons: List[np.ndarray] = None,
    ) -> None:
        # you can modify it!

        if self._is_gef_format_file(self.gene_file):
            expression_path: str = "geneExp/bin{}/expression".format(bin_size)
            rect = self._read_coordinate_ranges_from_file(
                file_path=self.gene_file, attr_loc_name=expression_path
            )
            min_x = rect.min_x
            min_y = rect.min_y
            max_x = rect.max_x
            max_y = rect.max_y
            with h5py.File(self.gene_file, "r") as gene_file_handler:
                expression_path: str = "/geneExp/bin{}/expression".format(bin_size)
                expression_dataset = gene_file_handler[expression_path]
                expression_num = expression_dataset.shape[0]
                self.logger.info(
                    "the valid polygon of gene data is min_x:{} min_y:{} max_x:{} max_y:{}".format(
                        min_x, min_y, max_x, max_y
                    )
                )

                if self._guess_polygon_is_transformed(
                    polygons=polygons, min_x=min_x, min_y=min_y
                ):
                    self.logger.info(
                        "the coordinates contains values less than left top ({},{})".format(
                            min_x, min_y
                        )
                    )
                    self.substract_leftop_coordinate = False

                if self.substract_leftop_coordinate:
                    self.logger.info(
                        "all the coordinates will substract the left top,the substract x ix {},substract y is {}".format(
                            min_x, min_y
                        )
                    )
                    for polygon_array in polygons:
                        polygon_array[:0] -= min_x
                        polygon_array[:1] -= min_y
                else:
                    self.logger.info(
                        "use the original coordinate to construct the polygon!"
                    )

                for polygon in polygons:
                    if self._check_coordinates_contains_negative(coordinates=polygon):
                        error_msg = "invalid negative coordinates"
                        self.logger.error(error_msg)
                        raise RuntimeError(error_msg)

                height = max_y - min_y + 1
                width = max_x - min_x + 1
                write_image_file = os.path.join(
                    gem_directory, "{}.lasso.{}.mask.tif".format(self.sample_id, label)
                )
                mask_array = self._fill_polygons_and_write_to_file(
                    height=height,
                    width=width,
                    polygons=polygons,
                    return_filled_mask=True,
                    file_path=write_image_file,
                )
                if self.gem_output_add_gz_suffix:
                    gem_output_filename = "{}.lasso.bin{}.{}.gem.gz".format(
                        self.sample_id, bin_size, label
                    )
                else:
                    gem_output_filename = "{}.lasso.bin{}.{}.gem".format(
                        self.sample_id, bin_size, label
                    )
                gem_output_file = os.path.join(gem_directory, gem_output_filename)

                gene_ids = []
                gene_path = "geneExp/bin{}/gene".format(bin_size)
                for item in gene_file_handler[gene_path][:]:
                    # repeat
                    # this is very ugly!
                    gene_ids += [item[0].decode("utf-8")] * item[2]

                # with open(gem_output_file, "w", encoding="utf-8") as writer:
                new_line_encoded = "\n".encode(self.io_encoding)
                writer = gzip.open(
                    gem_output_file, mode="w", compresslevel=self.compress_level
                )
                # file_header = f"#FileFormat=GEMv0.1\n#SortedBy=None\n#BinType=Bin\n#BinSize={bin_size}\n#Omics={self.omics_type}\n#Stereo-seqChip={self.sampleid}\n#OffsetX={offset_x}\n#OffsetY={offset_y}\n"
                format_require_header_string = "#FileFormat=GEMv0.1\n#SortedBy=None\n#BinType=Bin\n#BinSize={}\n#Omics={}\n#Stereo-seqChip={}\n#OffsetX={}\n#OffsetY={}".format(
                    bin_size, self.omics, self.sample_id, min_x, min_y
                )
                writer.write(format_require_header_string.encode(self.io_encoding))
                writer.write(new_line_encoded)

                # using the pandas to write the file
                # define the column name
                gene_id_name: str = "geneID"
                coor_x_name: str = "x"
                coor_y_name: str = "y"
                mid_count_name: str = "MIDCount"
                exon_count_name: str = "ExonCount"
                columns: List[str] = [
                    gene_id_name,
                    coor_x_name,
                    coor_y_name,
                    mid_count_name,
                    exon_count_name,
                ]
                self.logger.info("will write the data with header {}".format(columns))
                columns_str = self.write_csv_sep.join(columns)
                writer.write(columns_str.encode(self.io_encoding))
                writer.write(new_line_encoded)
                writer.close()

                # now write the data with frame!
                self.logger.info("write the data to compressed csv file...")
                exon_path = "geneExp/bin{}/exon".format(bin_size)
                has_exon: bool = exon_path in gene_file_handler

                # the idx for each filed!
                expression_x_idx = 0
                expression_y_idx = 1
                expression_midcount_idx = 2

                write_cnt = 0
                # batch_size: int = 1000000
                batches: int = (
                    expression_num + self.write_batch_size - 1
                ) // self.write_batch_size
                self.logger.info("batches {}".format(batches))
                # select_op = (
                #     lambda expresion: mask_array[
                #         expresion[expression_y_idx], expresion[expression_x_idx]
                #     ]
                #     == self.fill_mask_value
                # )
                # vectorized_select_op = np.vectorize(select_op)
                write_data_frames = []
                if has_exon:
                    self.logger.info("exist exon,will append it!")
                    exon_dataset = gene_file_handler[exon_path]
                    for i in range(batches):
                        left_idx: int = i * self.write_batch_size
                        right_idx: int = (i + 1) * self.write_batch_size
                        if right_idx > expression_num:
                            right_idx = expression_num

                        batch_expression = expression_dataset[left_idx:right_idx]
                        # this is slow!
                        # selected_indexes = np.where(vectorized_select_op(batch_expression))[0]
                        all_x_coors = np.array(
                            [
                                expression[expression_x_idx]
                                for expression in batch_expression
                            ]
                        )
                        all_y_coors = np.array(
                            [
                                expression[expression_y_idx]
                                for expression in batch_expression
                            ]
                        )
                        self.logger.info(
                            "select the datas which have mask value == {}".format(
                                self.fill_mask_value
                            )
                        )
                        selected_indexes = np.where(
                            mask_array[all_y_coors, all_x_coors] == self.fill_mask_value
                        )[0]
                        batch_exon = exon_dataset[left_idx:right_idx]
                        # for fast access!
                        batch_expression_dataframe = pd.DataFrame(
                            batch_expression[selected_indexes]
                        )
                        batch_gene_id_dataframe = pd.DataFrame(
                            [gene_ids[index + left_idx] for index in selected_indexes]
                        )
                        batch_exon_datafame = pd.DataFrame(batch_exon[selected_indexes])

                        # keep the order!
                        batch_write_dataframe = pd.concat(
                            [
                                batch_gene_id_dataframe,
                                batch_expression_dataframe,
                                batch_exon_datafame,
                            ],
                            axis=1,
                        )
                        batch_write_dataframe.columns = [
                            gene_id_name,
                            coor_x_name,
                            coor_y_name,
                            mid_count_name,
                            exon_count_name,
                        ]
                        # self._append_data_to_csv(
                        #     file_path=gem_output_file,
                        #     write_data_frame=batch_write_dataframe,
                        #     with_header=False,
                        # )
                        write_data_frames.append(batch_write_dataframe)
                        write_cnt += len(batch_write_dataframe)
                        self.logger.info("already write {} rows".format(write_cnt))
                        self.logger.info("finish batch {}/{}".format(i + 1, batches))
                else:
                    for i in range(batches):
                        left_idx: int = i * self.write_batch_size
                        right_idx: int = (i + 1) * self.write_batch_size
                        if right_idx > expression_num:
                            right_idx = expression_num
                        batch_expression = expression_dataset[left_idx:right_idx]
                        self.logger.info(
                            "select the datas which have mask value == {}".format(
                                self.fill_mask_value
                            )
                        )
                        all_x_coors = np.array(
                            [
                                expression[expression_x_idx]
                                for expression in batch_expression
                            ]
                        )
                        all_y_coors = np.array(
                            [
                                expression[expression_y_idx]
                                for expression in batch_expression
                            ]
                        )

                        selected_indexes = np.where(
                            mask_array[all_y_coors, all_x_coors] == self.fill_mask_value
                        )[0]
                        selected_batch_expression = batch_expression[selected_indexes]
                        self.logger.info(selected_batch_expression)
                        # test_coors = [(14908, 11036), (14912, 11036)]
                        batch_expression_dataframe = pd.DataFrame(
                            selected_batch_expression
                        )
                        batch_gene_id_dataframe = pd.DataFrame(
                            [gene_ids[index + left_idx] for index in selected_indexes]
                        )
                        # keep the order!
                        self.logger.info("concat the data frame...")
                        batch_write_dataframe = pd.concat(
                            [batch_gene_id_dataframe, batch_expression_dataframe],
                            axis=1,
                        )
                        batch_write_dataframe.columns = [
                            gene_id_name,
                            coor_x_name,
                            coor_y_name,
                            mid_count_name,
                        ]
                        self.logger.info(batch_write_dataframe)

                        # for fast access!
                        # self._append_data_to_csv(
                        #     file_path=gem_output_file,
                        #     write_data_frame=batch_write_dataframe,
                        #     with_header=False,
                        # )
                        write_data_frames.append(batch_write_dataframe)
                        write_cnt += len(batch_write_dataframe)
                        self.logger.info("already write {} rows".format(write_cnt))
                        self.logger.info("finish batch {}/{}".format(i + 1, batches))
                filtered_data_frame: pd.DataFrame = pd.concat(write_data_frames, axis=0)
                filtered_data_frame = filtered_data_frame.sort_values(
                    by=["geneID", "x", "y"], ascending=[True, True, True]
                )
                compress_dict = {
                    "method": "gzip",
                    "compresslevel": self.compress_level,
                    # "mttime":1
                }
                filtered_data_frame.to_csv(
                    gem_output_file,
                    sep=self.write_csv_sep,
                    compression=compress_dict,
                    index=False,
                    header=False,
                )
        else:
            self.logger.info(
                "the file {} is not a gef format file,noting to do...".format(
                    self.gene_file
                )
            )

    def saptialbin_lasso_process(self) -> None:
        polygon_metas: List[PolygonMeta] = self._read_polygon_metas_from_json_file()
        for polygon_meta in polygon_metas:
            uid: int = polygon_meta.uid
            label: str = polygon_meta.label
            polygons: List[np.ndarray] = polygon_meta.polygons
            uid += 1

            result_directory = os.path.join(self.output_dir, label)
            self._create_dir(result_directory)
            gem_output_directory: str = os.path.join(result_directory, "segmentation")
            self._create_dir(gem_output_directory)
            if self._is_transcript_omics(self.omics):
                formated_name = "{}.{}.label.gef".format(self.sample_id, label)
            elif self._is_protein_omics(self.omics):
                formated_name = "{}.protein.{}.label.gef".format(self.sample_id, label)
            else:
                error_msg = "unknow omics string {} which is not in [{},{}]".format(
                    self.omics, TRANSCRIPT_OMICS, PROTEIN_OMICS
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            # create the gef
            gef_output_file: str = os.path.join(result_directory, formated_name)
            cgef_adj = CgefAdjust()
            flatten_polygons = [item.flatten() for item in polygons]
            self.logger.info("invoking the cgef adj...")
            cgef_adj.create_Region_Bgef(
                self.gene_file, gef_output_file, flatten_polygons
            )
            self._single_bin_process(
                bin_size=self.bin_size,
                uid=uid,
                gem_directory=gem_output_directory,
                polygons=polygons,
                label=label,
            )

    @staticmethod
    def _is_cellbin_file(
        file_handler: str, expected_group_path: str = "/cellBin"
    ) -> None:
        is_cellbin = False
        if isinstance(file_handler, str):
            with h5py.File(file_handler, "r") as f:
                is_cellbin = expected_group_path in f
        elif isinstance(file_handler, h5py.File):
            is_cellbin = expected_group_path in file_handler
        return is_cellbin

    def run_cell_mask(self) -> None:
        expected_group_path: str = "/cellBin"
        if self._is_gef_format_file(self.gene_file):
            gene_file_handler = h5py.File(self.gene_file, mode="r")
            file_attrs = gene_file_handler.attrs
            omics_attr_name = "omics"
            if omics_attr_name in file_attrs:
                omics_list = gene_file_handler.attrs[omics_attr_name].tolist()
                omics_list = [item.decode("utf-8") for item in omics_list]
                if self.omics not in omics_list:
                    error_msg = "you specify omics type {},but we found {} in hdf5 file,which is mismatch!".format(
                        self.omics, omics_list
                    )
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)
            else:
                # need to talk with it!
                if not self._is_transcript_omics(self.omics):
                    error_msg = (
                        "the omics {} is mimatch with transcript omics {}".format(
                            self.omics, TRANSCRIPT_OMICS
                        )
                    )
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

            # whether the file constains the cell bin group!
            has_cell_bin_group: bool = self._is_cellbin_file(
                file_handler=gene_file_handler
            )
            self.logger.info("{}".format(list(gene_file_handler.keys())))
            gene_file_handler.close()
            if has_cell_bin_group:
                self.logger.info("process for cell bin file!")
                polygon_metas: List[PolygonMeta] = (
                    self._read_polygon_metas_from_json_file()
                )
                for polygon_meta in polygon_metas:
                    label = polygon_meta.label
                    polygons = polygon_meta.polygons
                    result_directory = os.path.join(self.output_dir, label)
                    self._create_dir(result_directory)
                    if self._is_transcript_omics(self.omics):
                        formatted_filename = "{}.{}.label.cellbin.gef".format(
                            self.sample_id, label
                        )
                        output_file = os.path.join(result_directory, formatted_filename)
                    else:
                        formatted_filename = "{}.protein.{}.label.cellbin.gef".format(
                            self.sample_id, label
                        )
                        output_file = os.path.join(result_directory, formatted_filename)
                    coordinate_range_attr_path = "cellBin/cell"
                    rect = self._read_coordinate_ranges_from_file(
                        file_path=self.gene_file,
                        attr_loc_name=coordinate_range_attr_path,
                    )

                    # concat the file path!
                    write_image_file = os.path.join(
                        self.output_dir,
                        "{}.lasso.{}.mask.tif".format(self.sample_id, label),
                    )
                    height = rect.max_y - rect.min_y + 1
                    width = rect.max_x - rect.min_x + 1
                    self._fill_polygons_and_write_to_file(
                        height=height,
                        width=width,
                        polygons=polygons,
                        return_filled_mask=False,
                        file_path=write_image_file,
                    )

                    self.logger.info(
                        "the output region cgef file is {}".format(output_file)
                    )
                    cell_adj = CgefAdjust()
                    cell_adj.create_Region_Bgef(self.gene_file, output_file, polygons)
            else:
                self.logger.info(
                    "the group name {} is not find in file {}".format(
                        expected_group_path, self.gene_file
                    )
                )
                self.saptialbin_lasso_process()

        else:
            error_msg = "specify file {} is not a gef format file,please retry!".format(
                self.gene_file
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def run_cellMask(self) -> None:
        self.logger.info(
            "recommend use function {},do not use {}".format(
                self.run_cell_mask.__name__, self.run_cellMask.__name__
            )
        )
        self.run_cell_mask()


def validate_gef_file_path(file_path: str) -> bool:
    expected_suffixs = [
        ".tissue.gef",
        ".cellbin.gef",
        ".raw.gef",
        ".tissue.protein.gef",
        ".cellbin.protein.gef",
        ".raw.protein.gef",
        ".gef",
    ]
    for suffix in expected_suffixs:
        if file_path.endswith(suffix):
            return True
    return False


def try_to_get_gef_file_from_directory(file_directory) -> str:
    if os.path.exists(file_directory) and os.path.isdir(file_directory):
        file_names = os.listdir(file_directory)
        for file_name in file_names:
            file_path = os.path.join(file_directory, file_name)
            if validate_gef_file_path(file_path):
                return file_path
    else:
        return None


def main():
    Usage = """
    %prog
    -i <Gene expression matrix>
    -m <Mask/Geojson File>
    -o <output Path>
    -s <bin size>

    return gene expression matrix under cells with labels
    """
    logger = WrapedLogger.get_logger()
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

    gene_file_path = opts.geneFilePath
    if not os.path.exists(gene_file_path):
        error_msg = "{} is not exist!".format(gene_file_path)
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    if os.path.isfile(gene_file_path):
        if not validate_gef_file_path(gene_file_path):
            error_msg = "{} is not expected which has wrong suffix!".format(
                gene_file_path
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        else:
            gef_file = gene_file_path
    else:
        logger.info(
            "given a directory {},we try to find gef file in it!".format(gene_file_path)
        )
        gef_file = try_to_get_gef_file_from_directory(gene_file_path)

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

    # set the construct params...
    polygon_file = opts.infile
    bin_size = opts.bin_size
    output_directory = opts.outpath
    sample_id = opts.sampleid
    omics = opts.omics
    compress_level: int = 2
    handle_batch_size = 6000000
    runner = MaskSegmentation(
        sample_id=sample_id,
        polygon_file=polygon_file,
        gene_file=geneFile,
        bin_size=bin_size,
        omics=omics,
        substract_leftop_coordinate=False,
        # 填充mask的值
        fill_mask_value=255,
        compress_level=compress_level,
        output_dir=output_directory,
        gem_output_add_gz_suffix=True,
        handle_batch_size=handle_batch_size,
    )


if __name__ == "__main__":
    main()
    # logger = WrapedLogger.get_logger()
    # logger.info("the brownfox jumps over the lazydog!")

    # # gef 文件
    # gene_file = "FP200000366BL_C4.gef"
    # # gene_file = "data_01/A02677B5.protein.gef"
    # # 储存点坐标的文件
    # polygon_file = "FP200000366BL_C4.20240320165402.lasso.geojson"
    # # polygon_file = "data_01/20240402141228.lasso.geojson"
    # bin_size = 1
    # # 结果保存目录
    # output_directory = "foo"
    # sample_id = "xxxxxx"
    # omics = "Transcriptomics"
    # # omics = "Proteomics"
    # compress_level = 6
    # # json文件中的点不减掉min_x,min_y
    # substract_leftop_coordinate: bool = False

    # seg_obj = MaskSegmentation(
    #     sample_id=sample_id,
    #     polygon_file=polygon_file,
    #     gene_file=gene_file,
    #     bin_size=bin_size,
    #     omics=omics,
    #     substract_leftop_coordinate=False,
    #     # 填充mask的值
    #     fill_mask_value=255,
    #     compress_level=compress_level,
    #     output_dir=output_directory,
    #     gem_output_add_gz_suffix=True,
    #     handle_batch_size=6000000,
    # )
    # seg_obj.run_cell_mask()
