from csl.config import DEFAULT_PAIRS_INST_CHROM, CSLTOOLS_VERSION
from csl.export_functions.format_export import FormatExport
from csl.export_functions.utils import *
from csl.utils.sql_utils import create_session
from csl.utils.file_utils import get_csl_version

class MbankExport(FormatExport):
    def export(self):
        """Workflow to export CSL data for MassBank."""
        from collections import defaultdict
        from tqdm import tqdm
        import re
        import os.path
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for MassBank documents')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Get CSL version number
        csl_version = get_csl_version(self.path_csl)

        # Create a mapping of experiment_id to chromatographic method
        exp_method_pairs = defaultdict(list)

        if 'all' in self.subset:
            data_sources = DEFAULT_PAIRS_INST_CHROM.keys()
        else:
            data_sources = self.subset

        for data_source in data_sources:
            # Get all experiment IDs based on data source in experiment group
            experiment_ids = get_experiment_ids_by_exp_group(session, data_source)
            logger.info(f"Found {len(experiment_ids)} experiment IDs for data source: {data_source}")
            # Apply mapping
            chrom_method = DEFAULT_PAIRS_INST_CHROM.get(data_source)
            for exp_id in experiment_ids:
                exp_method_pairs[chrom_method].append(exp_id)

        # Get list of current MassBank experiment IDs
        logger.info(f"Checking for existing MassBank files at {self.path_out}")
        dict_mbank_exp_id_fn = get_exp_ids_mbank(self.path_out)

        # Process experiment IDs by chromatographic method
        for chrom_method, exp_ids in exp_method_pairs.items():
            logger.info(f"Bulk loading {len(exp_ids)} experiments for chrom_method={chrom_method}")

            # Bulk load sql data for all experiment IDs by method
            sql_data_dict = sql_bulk_queries_by_exp_ids_chrom_method(session, exp_ids, chrom_method)

            # Process each experiment ID and generate txt files
            for i, exp_id in tqdm(enumerate(exp_ids), total=len(exp_ids), ncols=77):
                try:
                    # Extracts data for a specific experiment id and formats data to meet MassBank requirements.
                    export_data = extract_experiment_chunk_mbank(
                        exp_id, chrom_method, csl_version, CSLTOOLS_VERSION, sql_data_dict, dict_mbank_exp_id_fn
                    )

                    # Skip experiment ID if compound is an internal standard (export_data is None)
                    if not export_data:
                        logger.info(f'Skipping {exp_id} (internal standard)')
                        continue

                    # Write txt file
                    file_name = re.search(r"ACCESSION: (.+?)\n", export_data).group(1)
                    fname_out = os.path.join(self.path_out, f'{file_name}.txt')
                    with open(fname_out, 'w', encoding='utf-8') as f:
                        f.writelines(export_data)

                except Exception as e:
                    logger.error(f"There was an error processing experiment ID {exp_id}: {str(e)}")

        # Close the session after processing all experiments
        session.close()

        # Check for deprecated files
        exp_ids = [em_pair[0] for em_pair in exp_method_pairs]
        keys_not_in_exp_ids = set(dict_mbank_exp_id_fn.keys()) - set(exp_ids)
        if keys_not_in_exp_ids:
            entries_not_in_exp_ids = [dict_mbank_exp_id_fn[key] for key in keys_not_in_exp_ids]
            logger.info(f"{len(entries_not_in_exp_ids)} files not found in current experiment IDs and may need to be marked as deprecated:\n"
                        f"{entries_not_in_exp_ids}")

        logger.info('End of MassBank export workflow')
