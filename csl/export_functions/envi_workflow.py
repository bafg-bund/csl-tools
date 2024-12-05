from .format_workflow import FormatWorkflow
from utils.sql_utils import create_session, Experiment, Fragment, Parameter, Compound, RetentionTime
from .format_workflow_utils import *


class EnviWorkflow(FormatWorkflow):
    def export(self):
        """
        Workflow to export CSL data as a target list usable for envimass.

        This function loads the default configuration, conducts a CSL query to collect relevant data, processes the CSL
        data, formats it according to the EnviMass target list, and then exports the formatted data to a text file.
        """

        import os
        from datetime import datetime
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing envimass export workflow')

        # Load default configuration
        envi_def = default_config_envi()
        fragment_cutoff_percent = envi_def['fragment_cutoff_percent_def']  # todo: default 20; argument input needed?
        ce_filter = envi_def['ce_def']
        ces_filter = envi_def['ces_def']
        instrument_filter = envi_def['instrument_def']
        chrom_method_filter = envi_def['chrom_method_def']  # todo: default bfg; input chrom method?

        # Generate the output file name based on the CSL version and the current date
        export_method = f"envi_target_cutoff{fragment_cutoff_percent}perc"
        csl_version = os.path.splitext(os.path.basename(self.path_csl))[0]
        date_code = datetime.now().strftime("%y%m%d")
        fname_out = os.path.join(self.path_out, f'{date_code}_{csl_version}_{export_method}.txt')

        # Read files
        logger.info('Querying CSL data')
        df, fragment_data = self.csl_query_envi(ce_filter, ces_filter, instrument_filter, chrom_method_filter)

        # Process and format the DataFrame based on standard configuration
        logger.info('Processing and formatting data')
        df = self.process_data_envi(df, fragment_data, fragment_cutoff_percent)

        # Export the DataFrame as text file
        logger.info('Writing data to file')
        df.to_csv(fname_out, sep='\t', index=False, quoting=3)

        logger.info('End of envimass export workflow')

    def csl_query_envi(self, ce_filter, ces_filter, instrument_filter, chrom_method_filter):
        """
        Queries CSL data based on the specified filters and returns the results.

        Args:
            ce_filter (list of int)         : Collision energy filter range.
            ces_filter (int)                : Collision energy spread lower threshold.
            instrument_filter (list of str) : List of instrument types to filter by.
            chrom_method_filter (str)       : Chromatographic method filter.

        Returns:
            df (DataFrame)       : Pandas DataFrame containing the queried data.
            fragment_data (list) : List of fragments data for all experiments.
        """
        from sqlalchemy import and_
        import pandas as pd

        # Connect to the database
        session = create_session(self.path_csl)

        # SQLAlchemy query to fetch the required data
        query = session.query(
            Compound.name,
            Compound.formula,
            RetentionTime.rt,
            Experiment.adduct,
            Parameter.polarity,
            Experiment.experiment_id,
            Compound.CAS,
            Compound.inchi,
            Compound.SMILES
        ).join(
            Experiment, Experiment.compound_id == Compound.compound_id
        ).join(
            Parameter, Experiment.parameter_id == Parameter.parameter_id
        ).join(
            RetentionTime, RetentionTime.compound_id == Compound.compound_id
        ).filter(
            and_(
                Parameter.CE.between(ce_filter[0], ce_filter[1]),
                Parameter.CES > ces_filter,
                Parameter.instrument.in_(
                    instrument_filter
                ),
                RetentionTime.chrom_method == chrom_method_filter
            )
        ).order_by(
            Compound.name
        )

        # Convert query result to a DataFrame
        df = pd.read_sql(query.statement, session.bind)

        # Fragment extraction for all experiments
        fragment_data = session.query(
            Fragment.experiment_id, Fragment.mz, Fragment.int
        ).filter(Fragment.experiment_id.in_(df['experiment_id'])).all()

        # Close the session
        session.close()

        return df, fragment_data

    # noinspection PyMethodMayBeStatic
    def process_data_envi(self, df, fragment_data, fragment_cutoff_percent):
        """
        Processes the queried CSL data and formats it according to the EnviMass target list format.

        Args:
            df (DataFrame)                  : Queried CSL data in a pandas DataFrame.
            fragment_data (list)            : List of fragment data for each experiment.
            fragment_cutoff_percent (float) : The cutoff percentage for fragment intensity.

        Returns:
            df (DataFrame) : Pandas DataFrame formatted for the EnviMass target list.
        """

        # Organize fragment data into a dictionary by experiment_id
        fragments_by_experiment = {}
        for fragment in fragment_data:
            expid = fragment.experiment_id
            if expid not in fragments_by_experiment:
                fragments_by_experiment[expid] = []
            fragments_by_experiment[expid].append((fragment.mz, fragment.int))

        # Apply the get_fragments_int_cut_batch function in a loop
        df['Fragments'] = df['experiment_id'].apply(
            lambda exp_id: self.get_mz_fragments_int_cutoff(fragments_by_experiment.get(expid, []), fragment_cutoff_percent)
        )

        # Processing and formatting based on standard configuration (envi_config.py)
        df['adduct'] = df['adduct'].replace(adduct_name_pairs_envi())
        df['polarity'] = df['polarity'].replace(polarity_pairs_envi())
        df.rename(columns=column_name_pairs_envi(), inplace=True)

        # Add additional columns
        for key, value in additional_columns_with_def_values_envi().items():
            if key == 'ID':
                df[key] = range(1, len(df) + 1)
            else:
                df[key] = value

        # Set 'restrict_adduct' to TRUE if main_adduct is 'M+'
        df.loc[df['main_adduct'] == 'M+', 'restrict_adduct'] = 'TRUE'

        # Check if 'CAS' column contains 'NA', an empty string, or is NaN and replace with 'FALSE'
        id_na = (df['CAS'] == 'NA') | (df['CAS'] == '') | (df['CAS'].isna())
        df.loc[id_na, 'CAS'] = 'FALSE'

        # Remove specific rows
        df = df[~df['Name'].isin(remove_name_rows_envi())]

        # Replace occurrences of single quote with "prime" in the 'Name' column
        df.loc[:, 'Name'] = df['Name'].str.replace("'", "prime")

        # Remove SMILES codes with '#'
        df.loc[df['SMILES'].str.contains('#'), 'SMILES'] = 'FALSE'

        # Reorder the DataFrame columns based on defined order
        df = df.reindex(columns=column_order_envi())

        return df

    @staticmethod
    def get_mz_fragments_int_cutoff(fragments, cutoff_percent):
        """
        Filters and returns fragment mass-to-charge (m/z) ratios that have an intensity above a specified cutoff
        percentage of the maximum intensity.

        Args:
            fragments (list of tuple) : List of tuples where each tuple contains two elements:
                                        - mz (float): The mass-to-charge ratio of the fragment.
                                        - intensity (float): The intensity of the fragment.
            cutoff_percent (float)    : The intensity cutoff as a percentage of the maximum intensity.
                                        Only fragments with an intensity above this percentage of the maximum
                                        intensity will be included in the result.

        Returns:
            str: Comma-separated string of m/z ratios that meet or exceed the intensity cutoff.
                 Returns an empty string if no fragments meet the criteria or if the input fragments list is empty.
        """
        if not fragments:
            return ""
        max_int = max(intensity for _, intensity in fragments)
        selected_fragments = [mz for mz, intensity in fragments if intensity / max_int >= cutoff_percent / 100]
        return ", ".join(map(str, selected_fragments))
