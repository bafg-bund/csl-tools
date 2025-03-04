from export_functions.format_workflow import FormatWorkflow
from export_functions.format_workflow_utils.envi_utils import *
from export_functions.format_workflow_utils.envi_config import *
from export_functions.format_workflow_utils.format_utils import get_experiment_ids
from utils.sql_utils import create_session
from utils.file_utils import get_csl_version


class EnviWorkflow(FormatWorkflow):
    def export(self):
        """
        Workflow to export CSL data as a target list usable for enviMass.

        This function loads the default configuration, conducts a CSL query to collect relevant data, processes the CSL
        data, formats it according to the enviMass target list, and then exports the formatted data to a text file.

        Todo: Filtering by other data sources beside 'bfg' (e.g. lfuby, lubw) currently does not work, as it filtering
             is done always for the bfg method (dx.doi.org/10.1016/j.chroma.2015.11.014) which is imported from
             the default settings (envi_config). Therefore, using the data source 'lfuby' will return an empty file.
             Options: a) Filtering only by methods; b) Filtering by data sources for all methods;
                    What is needed?

        Todo: Unit and integration tests
        """


        import os.path
        from datetime import datetime
        from tqdm import tqdm
        import pandas as pd
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for enviMass documents')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Get experiment IDs
        experiment_ids = get_experiment_ids(session, self.subset)
        logger.info(f"Found {len(experiment_ids)} experiment ID's for subset: {self.subset}")

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Generate the output file name based on the CSL version and the current date
        data_source = self.subset
        csl_version = get_csl_version(self.path_csl)
        date_code = datetime.now().strftime("%y%m%d")

        envi_filter_def = default_sql_query_filter_envi()
        fragment_cutoff_percent = envi_filter_def['fragment_cutoff_percent_def']
        fname = f"ENVI-{data_source}-CSLv{csl_version}-cutoff{str(fragment_cutoff_percent)}perc-{date_code}.txt"
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
        df =  pd.DataFrame(export_list, columns=column_names[1:])
        df = df.sort_values(by="Name").reset_index(drop=True)
        df.rename_axis(column_names[0], inplace=True)

        # Export the DataFrame as text file
        df.to_csv(fpath_out, sep='\t', index=True, quoting=3)

        # Close the session after processing all experiments
        session.close()

        logger.info('End of envim export workflow')
