class FilterGeneData(object):
    def __init__(self, gene_str: str, min_mid_count: int, max_mid_count: int) -> None:
        """
        Args:
            gene_str,the gene string you want to filter,for legacy data,it should be gene name
                for current data,it should be gene id
            min_mid_count:int, the min value of filter mid count,should be positive int value
            max_mid_count:int, the max value of filter mid count,should be positive int value
        """
        self.gene_str = gene_str
        self.min_mid_count = min_mid_count
        self.max_mid_count = max_mid_count
        # check the data type
        if len(gene_str) == 0:
            raise ValueError("the gene str can not be empty!")

        for mid_count in (min_mid_count, max_mid_count):
            if not isinstance(mid_count, int):
                raise TypeError(
                    "the mid count should have type int,get get type {}".format(
                        type(mid_count)
                    )
                )

            if mid_count < 0:
                raise ValueError(
                    "the mid count can not be negative,but get {}".format(
                        mid_count)
                )

        # the max mid count should greater than min_mid_count
        if max_mid_count < min_mid_count:
            raise ValueError(
                "the max_mid_count {} mismatch with min_mid_count:{}".format(
                    max_mid_count, min_mid_count
                )
            )

    def __str__(self) -> str:
        return "Yuyalong {} with gene_str:{} range[{},{}]".format(
            self.gene_str, self.min_mid_count, self.max_mid_count
        )


# the filter return status!,should keep same with c++ code!
class FilterMidCountStatus(object):
    kSuccess: int = 0
    kPreparingData: int = 1
    kFilteringData: int = 2
    kUnknownException: int = -1
    kDiskSpaceError: int = -2
    kInvalidMidRange: int = -3
