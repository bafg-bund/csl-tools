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

        # Get experiment IDs
        experiment_ids = get_experiment_ids_by_exp_group(session, self.subset)
        logger.info(f"Found {len(experiment_ids)} experiment ID's for subset: {self.subset}")

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Temporary settings
        chrom_method = "dx.doi.org/10.1016/j.chroma.2015.11.014"  # Todo: needs to be a command

        # Generate the output file name based on the CSL version and the current date
        data_source = self.subset
        csl_version = get_csl_version(self.path_csl)
        date_code = datetime.now().strftime("%y%m%d")
        fname = f"THERMO-{data_source}-CSLv{csl_version}-{date_code}.msp"
        fpath_out = os.path.join(self.path_out, fname)

        # Initialize a list to accumulate data for batch writing
        export_data_list = []

        # Extract text chunks from the CSL data and append them to the export file
        with open(fpath_out, 'a', encoding='utf-8') as f:
            # Process each experiment IDs
            for i, exp_id in tqdm(enumerate(experiment_ids), total=len(experiment_ids), ncols=77):
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
