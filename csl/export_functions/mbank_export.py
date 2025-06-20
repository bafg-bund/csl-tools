from csl.export_functions.format_export import FormatExport
from csl.export_functions.utils import *
from csl.utils.sql_utils import create_session
from csl.utils.file_utils import get_csl_version
from csl.config import CSLTOOLS_VERSION

class MbankExport(FormatExport):
    def export(self):
        """Workflow to export CSL data for MassBank."""

        import os.path
        import re
        from tqdm import tqdm
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for MassBank documents')

        # Connect to the CSL database
        session = create_session(self.path_csl)

        # Get experiment IDs
        experiment_ids = get_experiment_ids_by_exp_group(session, self.subset)
        logger.info(f"Found {len(experiment_ids)} experiment ID's for subset: {self.subset}")

        # Start CSL data extraction
        logger.info("Starting CSL data export")

        # Temporary settings
        chrom_method = "dx.doi.org/10.1016/j.chroma.2015.11.014"  # Todo: needs to be a command

        # Get CSL version number
        csl_version = get_csl_version(self.path_csl)

        # Get list of current MassBank experiment IDs
        logger.info(f"Checking for existing MassBank files at {self.path_out}")
        dict_mbank_exp_id_fn = get_exp_ids_mbank(self.path_out)

        # Process experiment IDs and generate txt files
        for i, exp_id in tqdm(enumerate(experiment_ids), total=len(experiment_ids), ncols=77):
            try:
                # Extracts data for a specific experiment id and formats data to meet MassBank requirements.
                export_data = extract_experiment_chunk_mbank(session, exp_id, chrom_method, csl_version, CSLTOOLS_VERSION,
                                                       dict_mbank_exp_id_fn)

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
        keys_not_in_exp_ids = set(dict_mbank_exp_id_fn.keys()) - set(experiment_ids)
        if keys_not_in_exp_ids:
            entries_not_in_exp_ids = [dict_mbank_exp_id_fn[key] for key in keys_not_in_exp_ids]
            logger.info(f"{len(entries_not_in_exp_ids)} files not found in current experiment IDs and may need to be marked as deprecated:\n"
                        f"{entries_not_in_exp_ids}")

        logger.info('End of MassBank export workflow')
