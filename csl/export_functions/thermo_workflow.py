from .format_workflow import FormatWorkflow
from utils.sql_utils import create_session, Experiment
from .format_workflow_utils import *


class ThermoWorkflow(FormatWorkflow):
    def export(self):
        """Workflow to export CSL data to a text file."""

        from datetime import datetime
        import os.path
        from tqdm import tqdm
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing thermo export workflow')

        # Temporary settings
        chrom_method = "dx.doi.org/10.1016/j.chroma.2015.11.014"  # Todo: needs to be a command later

        # Generate the output file name based on the CSL version and the current date
        export_method = f"thermo"
        csl_version = os.path.splitext(os.path.basename(self.path_csl))[0]
        date_code = datetime.now().strftime("%y%m%d")
        fname_out = os.path.join(self.path_out, f'{date_code}_{csl_version}_{export_method}.txt')

        # Start CSL connection and data extraction
        logger.info("Starting CSL data extraction")

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Retrieve all experiment IDs
        experiment_ids = session.query(Experiment.experiment_id).all()
        experiment_ids = [exp_id[0] for exp_id in experiment_ids]  # Convert to a flat list

        # Initialize a list to accumulate data for batch writing
        export_data_list = []

        # Extract text chunks from the CSL data and append them to the export file
        with open(fname_out, 'a') as f:
            # Process each experiment IDs
            for i, exp_id in tqdm(enumerate(experiment_ids), total=len(experiment_ids), ncols=77):
                try:
                    # Extract the text chunk for the current experiment
                    export_data = extract_experiment_text_chunk(session, exp_id, chrom_method)
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
