import os

class JGTML240615Config:
    def __init__(self):
        self.jgtpy_data_full_var_name = "JGTPY_DATA_FULL"
        self.result_drop_base_override = None
        self.source_dataset_archival_path_override = None
        self.data_dir_override = None
        self.archive_used_dataset = True
        self.use_ttf_default = True
        # Additional static configurations can be added here

class JGTML240615Request:
    def __init__(self, instrument=None, timeframe=None, buysell='S', regenerate_cds=True, use_fresh=True, quiet=False):
        self.instrument = instrument
        self.timeframe = timeframe
        self.buysell = buysell
        self.regenerate_cds = regenerate_cds
        self.use_fresh = use_fresh
        self.quiet = quiet
        # Initialize from environment variables if not explicitly set
        self.buysell = os.getenv("bs", buysell)

    @staticmethod
    def from_args(args):
        """
        Create a JGTML240615Request instance from an argparse.Namespace.
        This allows for easy integration with command-line arguments.
        """
        return JGTML240615Request(
            instrument=args.instrument,
            timeframe=args.timeframe,
            buysell=args.buysell,
            regenerate_cds=not args.dont_regenerate_cds,
            use_fresh=not args.use_old,
            quiet=args.quiet
        )