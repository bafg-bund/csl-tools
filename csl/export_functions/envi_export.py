from csl.export_functions.format_export import FormatExport
from csl.export_functions.utils import *
from csl.utils.sql_utils import create_session
from csl.utils.file_utils import get_csl_version


class EnviExport(FormatExport):
    def export(self):
        """Workflow to export CSL data as a target list usable for enviMass."""
        import os.path
        from datetime import datetime
        from tqdm import tqdm
        import pandas as pd
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for enviMass documents')

        # Get chrom. methods
        chrom_methods = get_chrom_methods(self.subset)

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Start CSL data extraction
        logger.info("Starting CSL data export, creating one file per chrom. method.")

        for chrom_method in chrom_methods:
            # Generate the output file name based on the CSL version and the current date
            csl_version = get_csl_version(self.path_csl)
            date_code = datetime.now().strftime("%Y%m%d")
            envi_filter_def = default_sql_query_filter_envi()
            fragment_cutoff_percent = envi_filter_def['fragment_cutoff_percent_def']
            fname = f"envi-{chrom_method}-CSLv{csl_version}-cutoff{str(fragment_cutoff_percent)}perc-{date_code}.txt"
            fpath_out = os.path.join(self.path_out, fname)

            # Get csl data based on query filters
            csl_query_data = sql_query_with_filters_envi(session, chrom_method)
            logger.info(f"Found {len(csl_query_data)} experiments for chrom. method: {chrom_method}")

            # Process csl data entries to match required format
            export_list = []
            for csl_data in tqdm(csl_query_data, total=len(export_list), ncols=77):
                try:
                    processed_entry = process_data_entry_envi(csl_data, chrom_method)
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

            # Group by the key columns and merge Fragments
            merged_df = df.groupby(['Name', 'main_adduct', 'ion_mode'], as_index=False).agg(
                lambda x: [t for sublist in x for t in sublist] if x.name == 'Fragments' else x.iloc[0]
            )
            merged_df['Fragments'] = merged_df['Fragments'].apply(deduplicate_fragments_envi)

            # Reorder columns and insert "ID" column
            merged_df = merged_df[column_names[1:]]
            merged_df.insert(0, "ID", range(len(merged_df)))

            # Export the DataFrame as text file
            merged_df.to_csv(fpath_out, sep='\t', index=False, quoting=3)

        # Close the session after processing all experiments
        session.close()

        logger.info('End of enviMass export workflow')
