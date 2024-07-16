class JGTML240615Config:
    """
    Configuration class for the JGTML240615 prototype.
    """

    def __init__(self,
                 instrument: str = "GBP/USD",
                 timeframe: str = "H4",
                 buysell: str = "S",
                 regenerate_cds: bool = False,
                 result_drop_base_override: str = None,
                 source_dataset_archival_path_override: str = None,
                 quiet: bool = False,
                 print_abstract: bool = False,
                 use_ttf_rather_than_cds: bool = False,
                 result_file_basename: str = "jgtml_obsds_240515_SIGNALS.result",
                 data_dir_override: str = None,
                 use_fresh: bool = True,
                 mfi_flag: bool = True,
                 balligator_flag: bool = True,
                 talligator_flag: bool = True,
                 ):
        """
        Initialize the JGTML240615Config object.

        Args:
            instrument: The financial instrument to analyze.
            timeframe: The timeframe of the data to analyze.
            buysell: The direction of the signals to analyze ("S" for sell, "B" for buy).
            regenerate_cds: Whether to regenerate the CDS data.
            result_drop_base_override: The path to the directory where the results will be saved.
            source_dataset_archival_path_override: The path to the directory where the source dataset is archived.
            quiet: Whether to suppress output.
            print_abstract: Whether to print the abstract.
            use_ttf_rather_than_cds: Whether to use TTF data as the source of data.
            result_file_basename: The base name of the result files.
            data_dir_override: The path to the directory containing the data.
            use_fresh: Whether to use fresh data.
            mfi_flag: Whether to include MFI data.
            balligator_flag: Whether to include Big Alligator data.
            talligator_flag: Whether to include Tide Alligator data.
        """

        self.instrument = instrument
        self.timeframe = timeframe
        self.buysell = buysell
        self.regenerate_cds = regenerate_cds
        self.result_drop_base_override = result_drop_base_override
        self.source_dataset_archival_path_override = source_dataset_archival_path_override
        self.quiet = quiet
        self.print_abstract = print_abstract
        self.use_ttf_rather_than_cds = use_ttf_rather_than_cds
        self.result_file_basename = result_file_basename
        self.data_dir_override = data_dir_override
        self.use_fresh = use_fresh
        self.mfi_flag = mfi_flag
        self.balligator_flag = balligator_flag
        self.talligator_flag = talligator_flag