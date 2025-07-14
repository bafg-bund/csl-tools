from csl.config import DEFAULT_PAIRS_INST_CHROM
from csl.export_functions.format_export import FormatExport
from csl.export_functions.utils import *
from csl.utils.sql_utils import create_session
from csl.utils.file_utils import get_csl_version
from csl.config import CSLTOOLS_VERSION

class ThermoExport(FormatExport):
    def export(self):
        """Workflow to export CSL data to a text file."""

        import os.path
        from datetime import datetime
        from tqdm import tqdm
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for MSP/NIST documents (thermo workflow)')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Generate the output file name based on the CSL version and the current date
        csl_version = get_csl_version(self.path_csl)
        date_code = datetime.now().strftime("%y%m%d")
        if 'all' in self.subset:
            fname = f"THERMO-CSLv{csl_version}-{date_code}.msp"
        else:
            fname = f"THERMO-{'-'.join(self.subset)}-CSLv{csl_version}-{date_code}.msp"
        fpath_out = os.path.join(self.path_out, fname)

        # Initialize a list to accumulate data for batch writing
        export_data_list = []

        # Extract text chunks from the CSL data and append them to the export file
        with open(fpath_out, 'a', encoding='utf-8') as f:

            # Create a mapping of experiment_id -> method
            exp_method_pairs = []

            if 'all' in self.subset:
                data_sources = DEFAULT_PAIRS_INST_CHROM.keys()
            else:
                data_sources = self.subset

            for data_source in data_sources:
                # Get all experiment IDs based on data source in experiment group
                experiment_ids = get_experiment_ids_by_exp_group(session, data_source)
                logger.info(f"Found {len(experiment_ids)} experiment IDs for data source: {data_source}")
                # Apply mapping
                for exp_id in experiment_ids:
                    exp_method_pairs.append((exp_id, DEFAULT_PAIRS_INST_CHROM.get(data_source)))

            # Process each experiment IDs
            for i, (exp_id, chrom_method) in tqdm(enumerate(exp_method_pairs), total=len(exp_method_pairs), ncols=77):
                try:
                    # Extract the text chunk for the current experiment
                    export_data = extract_experiment_chunk_thermo(session, exp_id, chrom_method, csl_version, CSLTOOLS_VERSION)
                    if not export_data:
                        logger.info(f'Skipping {exp_id}')
                        continue
                    export_data_list.append(export_data + "\n\n")  # Append new line after each chunk

                    # Every 100 iterations, write to the file and clear the list
                    if (i + 1) % 100 == 0 or (i + 1) == len(experiment_ids):
                        f.writelines(export_data_list)
                        export_data_list.clear()  # Clear the list after writing

                except Exception as e:
                    logger.error(f"There was an error processing experiment ID {exp_id}: {str(e)}")

            # Write any remaining data to the file after the loop
            if export_data_list:
                f.writelines(export_data_list)

        # Close the session after processing all experiments
        session.close()

        logger.info('End of thermo export workflow')
