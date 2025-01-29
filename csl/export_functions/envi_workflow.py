from export_functions.format_workflow import FormatWorkflow
from export_functions.format_workflow_utils.envi_utils import *
from export_functions.format_workflow_utils.envi_config import *
from utils.sql_utils import inst_code_csl_mapping, create_session, Experiment, ExperimentGroup, expGroupExp
from utils.file_utils import get_csl_version


class EnviWorkflow(FormatWorkflow):
    def export(self):
        """
        Workflow to export CSL data as a target list usable for enviMass.

        This function loads the default configuration, conducts a CSL query to collect relevant data, processes the CSL
        data, formats it according to the enviMass target list, and then exports the formatted data to a text file.
        Todo: Make function to get experiment ids in all 3 workflows
        Todo: Write tests (unit and integration)
        Todo: clean up __init__ and imports
        """

        from sqlalchemy import select
        import os.path
        from datetime import datetime
        from tqdm import tqdm
        import pandas as pd
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for enviMass documents')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Get experiment IDs  Todo: make function in all 3 workflows in format_utils or sql utils?-> get_exp_ids(self.subset)
        if self.subset == 'all':
            # Get all experiment IDs
            experiment_ids = session.query(Experiment.experiment_id).all()
            experiment_ids = [exp_id[0] for exp_id in experiment_ids]  # Convert to a flat list
        else:
            # Get experiment IDs based on subset (query at specific ExperimentGroup name)
            inst_notation_pairs = inst_code_csl_mapping()
            stmt = (
                select(Experiment.experiment_id)
                .join(expGroupExp, Experiment.experiment_id == expGroupExp.c.experiment_id)
                .join(ExperimentGroup, expGroupExp.c.experimentGroup_id == ExperimentGroup.experimentGroup_id)
                .where(ExperimentGroup.name == inst_notation_pairs[self.subset])
            )
            # Execute the query
            experiment_ids = session.execute(stmt).scalars().all()

        logger.info(f"Found {len(experiment_ids)} experiment ID's for subset: {self.subset}")

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Generate the output file name based on the CSL version and the current date
        data_source = self.subset
        csl_version = get_csl_version(self.path_csl)
        date_code = datetime.now().strftime("%y%m%d")
        fname = f"ENVI-{data_source}-CSLv{csl_version}-{date_code}.txt"
        fpath_out = os.path.join(self.path_out, fname)

        # Get csl data based on query filters
        csl_query_data = sql_query_with_filters_envi(session)

        # Filter result by list of allowed experiment ids
        csl_data_filtered = [data_entry for data_entry in csl_query_data if data_entry.experiment_id in experiment_ids]

        # Process csl data entries to match required format
        export_list = []
        for csl_data in tqdm(csl_data_filtered, total=len(export_list), ncols=77):
            try:
                processed_entry = process_data_entry_envi(csl_data)
                if not processed_entry:
                    logger.info(f"Skipping compound {csl_data.compound.name} with experiment ID: {csl_data.experiment_id}")
                    continue
                export_list.append(processed_entry)

            except Exception as e:
                logger.error(f"There was an error processing experiment ID {csl_data.experiment_id}: {str(e)}")

        # Create DataFrame
        column_names = column_names_order_envi()  # Column structure target list
        df = pd.DataFrame(export_list, columns=column_names[1:], index=range(1,len(export_list)+1))
        df.rename_axis(column_names[0], inplace=True)

        # Export the DataFrame as text file
        df.to_csv(fpath_out, sep='\t', index=True, quoting=3)

        # Close the session after processing all experiments
        session.close()

        logger.info('End of envim export workflow')
