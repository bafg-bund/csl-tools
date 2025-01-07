from export_functions.format_workflow import FormatWorkflow
from utils.sql_utils import inst_code_csl_mapping, create_session, Experiment, ExperimentGroup, expGroupExp
from export_functions.format_workflow_utils import *
from utils.file_utils import get_csl_version
from config import pycsl_version

class MbankWorkflow(FormatWorkflow):
    def export(self):
        """Workflow to export CSL data for MassBank."""

        from sqlalchemy import select
        import os.path
        import re
        from tqdm import tqdm
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for MassBank documents')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Query to get experiment IDs with specific ExperimentGroup name
        inst_notation_pairs = inst_code_csl_mapping()
        stmt = (
            select(Experiment.experiment_id)
            .join(expGroupExp, Experiment.experiment_id == expGroupExp.c.experiment_id)
            .join(ExperimentGroup, expGroupExp.c.experimentGroup_id == ExperimentGroup.experimentGroup_id)
            .where(ExperimentGroup.name == inst_notation_pairs[self.inst])
        )

        # Execute the query
        experiment_ids = session.execute(stmt).scalars().all()
        logger.info(f"Found {len(experiment_ids)} experiment ID's for {inst_notation_pairs[self.inst]}")

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Temporary settings
        chrom_method = "dx.doi.org/10.1016/j.chroma.2015.11.014"  # Todo: needs to be a command

        # Get CSL version number
        csl_version = get_csl_version(self.path_csl)

        # Process experiment IDs and generate txt files
        for i, exp_id in tqdm(enumerate(experiment_ids), total=len(experiment_ids), ncols=77):
            try:
                # Extracts data for a specific experiment id and formats data to meet MassBank requirements.
                export_data = extract_experiment_chunk(session, exp_id, chrom_method, csl_version, pycsl_version)

                # Skip experiment ID if compound is an internal standard (export_data is None)
                if not export_data:
                    logger.info(f'Skipping {exp_id} (internal standard)')
                    continue

                # Write txt file
                file_name = re.search(r"ACCESSION: (.+?)\n", export_data).group(1)
                fname_out = os.path.join(self.path_out, f'{file_name}.txt')
                with open(fname_out, 'a') as f:
                    f.writelines(export_data)

            except Exception as e:
                logger.error(f"There was an error processing experiment ID {exp_id}: {str(e)}")

        # Close the session after processing all experiments
        session.close()

        logger.info('End of MassBank export workflow')
