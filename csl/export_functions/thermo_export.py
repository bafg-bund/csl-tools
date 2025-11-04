from csl.config import DEFAULT_PAIRS_DSOURCE_CHROM
from csl.export_functions.format_export import FormatExport
from csl.export_functions.utils import *
from csl.utils.sql_utils import create_session
from csl.utils.file_utils import get_csl_version
from csl.config import CSLTOOLS_VERSION

class ThermoExport(FormatExport):
    def export(self):
        """Workflow to export CSL data to a text file."""
        import os.path
        from collections import defaultdict
        from datetime import datetime
        from tqdm import tqdm
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for MSP/NIST documents (thermo workflow)')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        if 'all' in self.subset:
            data_sources = DEFAULT_PAIRS_DSOURCE_CHROM.keys()
        else:
            data_sources = self.subset

        # Get all experiment IDs and bulk load everything
        exp_ids = get_experiment_ids_by_data_src(session, 'all')
        logger.info(f"Bulk loading {len(exp_ids)} experiments")
        sql_data_dict = sql_bulk_queries_by_exp_ids(session, exp_ids)

        # Process experiment IDs by chromatographic method
        for data_source in data_sources:
            chrom_method = DEFAULT_PAIRS_DSOURCE_CHROM[data_source]
            logger.info(f"Exporting file for {chrom_method}")

            # Generate the output file name based on the CSL version and the current date
            csl_version = get_csl_version(self.path_csl)
            date_code = datetime.now().strftime("%Y%m%d")
            fname = f"thermo-{chrom_method}-CSLv{csl_version}-{date_code}.msp"
            fpath_out = os.path.join(self.path_out, fname)

            # Initialize a list to accumulate data for batch writing
            export_data_list = []

            # Extract text chunks from the CSL data and append them to the export file
            with open(fpath_out, 'a', encoding='utf-8') as f:

                # Process each experiment ID
                for i, exp_id in tqdm(enumerate(exp_ids), total=len(exp_ids), ncols=77):
                    try:
                        export_data = extract_experiment_chunk_thermo(
                            exp_id, chrom_method, csl_version, CSLTOOLS_VERSION, sql_data_dict
                        )
                        if not export_data:
                            logger.info(f'Skipping {exp_id}')
                            continue
                        export_data_list.append(export_data + "\n\n")

                        if (i + 1) % 100 == 0 or (i + 1) == len(exp_ids):
                            f.writelines(export_data_list)
                            export_data_list.clear()  # Clear the list after writing

                    except Exception as e:
                        logger.error(f"There was an error processing experiment ID {exp_id}: {str(e)}")

                # Write any remaining data to the file
                if export_data_list:
                    f.writelines(export_data_list)

        # Close the session after processing all experiments
        session.close()

        logger.info('End of thermo export workflow')
