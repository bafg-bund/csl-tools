from csl.utils.sql_utils import (Experiment, Fragment, Parameter, Compound, RetentionTime, CompoundGroup,
                                 ExperimentGroup)

def check_duplicate(session, entry):
    """
    Checks if the experimental information are already present in the CSL. Constructs and executes a query using the
    experimental information from the data entry.

    The query is constructed with join and filter conditions:
    1. Construct query that will return relevant tables/columns
    2. Join SQL tables by linking them using a foreign key relationship
       (e.g. tables "Experiment" and "Parameter" linked by the foreign key "parameter_id")
    3. Filter SQL entries by experimental information and either the InChIKey or the CAS registry number (CAS RN)

    Args:
        session (obj)         : SQLAlchemy session object (sqlalchemy.orm.session.Session)
        entry (pandas.series) : Data of one entry (pandas.core.series.Series)

    Returns:
        res_count (int) : Number of matches returned by executing the query.
                          Returns -1 if matching was not attempted due to missing CAS RN and InChIKey.
    """
    from sqlalchemy import func

    # Prepare query
    qry = session.query(
        Compound.CAS, Experiment.isotope, Parameter.instrument, Parameter.ionisation,
        Parameter.CE, Parameter.CES, Parameter.col_type, Parameter.ce_unit,
        Parameter.polarity, Experiment.adduct
    ). \
        join(Experiment, Compound.compound_id == Experiment.compound_id). \
        join(Parameter, Experiment.parameter_id == Parameter.parameter_id)

    qry = qry.filter(Experiment.adduct == entry['adduct_i'],
                     Experiment.isotope == entry['var_isotope'],
                     Parameter.instrument == entry['instrument_i'],
                     Parameter.ionisation == entry['ionization_i'],
                     Parameter.polarity == entry['pol_i'],
                     Parameter.CE == entry['ce_i'],
                     Parameter.CES == entry['ces_i'],
                     Parameter.col_type == entry['col_type_i'],
                     Parameter.ce_unit == entry['var_ce_unit'])

    inchikey_main_i = entry['inchikey_main_i']
    cas_i = entry['cas_i']
    exp_id = entry['experiment_id_i']

    if inchikey_main_i and not cas_i:
        # Add query filter using the main layer of the InChIkey
        qry = qry.filter(func.substr(Compound.inchikey, 1, func.length(inchikey_main_i)) == inchikey_main_i)
        res_count = qry.count()
    elif not inchikey_main_i and cas_i:
        # Add query filter using the CAS RN
        qry = qry.filter(Compound.CAS == cas_i)
        res_count = qry.count()
    elif inchikey_main_i and cas_i:
        # Do the query once using the main layer of the InChIkey and the CAS RN
        qry1 = qry.filter(func.substr(Compound.inchikey, 1, func.length(inchikey_main_i)) == inchikey_main_i)
        qry2 = qry.filter(Compound.CAS == cas_i)
        # Combine results
        combined_results = qry1.all() + qry2.all()
        unique_results = list(set(combined_results))
        # Count results
        res_count = len(unique_results)
    else:  # If there is no InChIkey (Main Layer) AND no CAS RN
        res_count = -1

    # Additional check by experiment ID if any previous query returned no results
    if res_count == 0 and exp_id:
        exp_qry = session.query(Experiment).filter(Experiment.experiment_id == exp_id)
        res_count = exp_qry.count()

    return res_count


def add_exp_to_session(session, entry, inst_def):
    """
    Adds the new experimental information to the following tables in the CSL:
    # Experiment group
    - Checks if the experiment group exists in the CSL and adds it if necessary.
    # Compound group(s)
    - Matches compound groups with existing ones in the CSL. Collects the matches.
    - If no matches are found, uses the default compound group.
    # Compound
    - Checks if the compound, and a link to the matched compound group(s), exists in the CSL.
    - Missing compounds and links to compound group(s) are added.
    # Retention time
    - Checks for an existing retention time (RT) and uses the RT from the file if it doesn't exist.
    Otherwise, prefers existing RT. Also checks for RT inconsistency (warning at a difference of >10 s).
    # Experimental parameters
    - Searches for experimental parameters and add them from the file if they do not exist.
    # Experiment
    - Creates a new experiment entry in the CSL at the current time.
    # Fragments
    - Adds all fragment information from the file.

    Args:
        session (obj)         : SQLAlchemy session object (sqlalchemy.orm.session.Session)
        entry (pandas.series) : Data of one entry (pandas.core.series.Series)
        inst_def (dict)       : Data-source-specific defaults used for keeping format, and csl-matching/commits.

    Returns:
        (No return variables, but the session object is updated)
    """
    from datetime import datetime
    from sqlalchemy import func
    import logging

    logger = logging.getLogger(__name__)

    # Prepare all variables
    expg_def = entry['var_expg_csl']
    compg_def = entry['var_compg_csl']
    comp_i = entry['comp_i']
    formula_i = entry['formula_i']
    smiles_i = entry['smiles_i']
    inchikey_i = entry['inchikey_i']
    inchi_i = entry['inchi_i']
    chrom_method = entry['var_chrom_method']
    rt_i = entry['rt_i']
    instrument = entry['var_instrument']
    pol_i = entry['pol_i']
    ce_i = entry['ce_i']
    ces_i = entry['ces_i']
    ce_unit = entry['var_ce_unit']
    col_type_i = entry['col_type_i']
    ionization_i = entry['ionization_i']
    mz_i = entry['mz_i']
    adduct_i = entry['adduct_i']
    isotope = entry['var_isotope']
    spec_i = entry['spec_i']
    inchikey_main_i = entry['inchikey_main_i']
    cas_i = entry['cas_i']
    compgroup_i = entry['compgroup_i']
    file_path = entry['file_path']

    # Log compound name, adduct and file path for reference
    logger.info(f"Compound: {comp_i}; CE: {ce_i}; File path: {file_path}")

    # Check if the experiment group exists (e.g., 'UBA', 'BfG') in the CSL and add it if necessary.
    exp_group = session.query(ExperimentGroup).filter_by(name=expg_def).one_or_none()
    if not exp_group:
        logger.info(f'Adding missing default experiment group: "{expg_def}"')
        exp_group = ExperimentGroup(name=expg_def)
        session.add(exp_group)

    # Match compound groups with existing ones in the CSL. Collect the matches. If no matches are found, use the default.
    comp_group = []
    if compgroup_i:
        for cg in compgroup_i:
            cg_db = session.query(CompoundGroup).filter(func.lower(CompoundGroup.name) == cg.lower()).one_or_none()
            if cg_db:
                comp_group.append(cg_db)

    if not comp_group:
        existing_cg = session.query(CompoundGroup).filter_by(name=compg_def).one_or_none()
        # Create the default compound group if necessary.
        if not existing_cg:
            logger.info(f'Adding missing default compound group: "{compg_def}"')
            new_cg = CompoundGroup(name=compg_def)
            session.add(new_cg)
        comp_group = session.query(CompoundGroup).filter_by(name=compg_def).one_or_none()
        if not isinstance(comp_group, list):
            comp_group = [comp_group]

    # Check if the compound, and a link to the matched compound group(s), exists in the CSL. Missing entries are added.
    def get_single_compound_entry(base_query, refine_query):
        """
        Runs base_query, unwraps if exactly one result. If multiple, runs refine_query.
        Returns either a single compound entry or None.
        """
        comp_list = base_query.all()

        if len(comp_list) == 1:  # If there is one match, return query result.
            return comp_list[0]
        elif len(comp_list) > 1:  # If there are multiple matches, give warning and refine query.
            logger.warning(f"Multiple entries for the same InChIkey (main layer) or CAS in the CSL: {comp_list}")
            return refine_query.one_or_none()
        else:
            return None

    if inchikey_main_i:  # InChIKey is preferred
        # Prepare base query (main layer of the InChIKey) and refine query (compound name)
        base_query = session.query(Compound).filter(
            func.substr(Compound.inchikey, 1, func.length(inchikey_main_i)) == inchikey_main_i
        )
        refine_query = base_query.filter(Compound.name == comp_i)
        # Run query
        comp_res = get_single_compound_entry(base_query, refine_query)
    elif cas_i:
        # Prepare base query (CAS RN) and refine query (compound name)
        base_query = session.query(Compound).filter(Compound.CAS == cas_i)
        refine_query = base_query.filter(Compound.name == comp_i)
        # Run query
        comp_res = get_single_compound_entry(base_query, refine_query)
    else:
        comp_res = None

    if comp_res:  # If the compound exists in the CSL
        # Add compound groups that do not exist yet for this compound
        for cg in comp_group:
            if cg.name not in [group.name for group in comp_res.groups]:
                logger.info(f'Adding compound group "{cg.name}" to the compound "{comp_i}"')
                comp_res.groups.append(cg)
    else:  # If the compound was not found in the CSL
        logger.info(f'Compound "{comp_i}" not found in CSL. Adding entry.')
        comp_res = Compound(formula=formula_i, CAS=cas_i, SMILES=smiles_i, name=comp_i,
                            groups=comp_group, inchikey=inchikey_i, inchi=inchi_i)
        # Add compound entry to session
        session.add(comp_res)

    # Check for existing retention time (filter by compound_id and chrom. method). Use RT from file if no RT exists,
    # otherwise prefer existing RT. Also check for RT inconsistency (warning at difference >10 s).
    rt_res = session.query(RetentionTime).filter_by(compound_id=comp_res.compound_id, chrom_method=chrom_method
                                                     ).one_or_none()
    if not rt_res:
        logger.info(f'Retention time for compound ID "{comp_res.compound_id}" and chromatographic method '
                    f'"{chrom_method}" not found in CSL. Adding retention time from data entry.')
        rt_res = RetentionTime(chrom_method=chrom_method, rt=rt_i, compound=comp_res, predicted='FALSE')
        session.add(rt_res)
    else:
        if abs(rt_res.rt-rt_i)*60 > 10:
            logger.warning(f'Retention times from file ({rt_i}) and CSL ({rt_res.rt}) differ by more than 10 s.')

    # Search experimental parameters and add them from the file if they don't exist
    para_res = session.query(Parameter).filter_by(instrument=instrument, polarity=pol_i, CE=ce_i, CES=ces_i,
                                                  ce_unit=ce_unit, col_type=col_type_i, ionisation=ionization_i
                                                  ).one_or_none()
    if not para_res:
        logger.info('Experimental parameters not found in CSL. Adding parameters from data entry.')
        para_res = Parameter(instrument=instrument, polarity=pol_i, CE=ce_i, CES=ces_i, ce_unit=ce_unit,
                             col_type=col_type_i, ionisation=ionization_i)
        session.add(para_res)

    # Create a new experiment entry in the CSL at the current time
    exp = Experiment(mz=mz_i, compound=comp_res, parameter=para_res, adduct=adduct_i, groups=[exp_group],
                     time_added=datetime.today(), isotope=isotope)
    session.add(exp)

    # Add the spectrum to the experiment
    for frag in spec_i.itertuples():
        frag_i = Fragment(mz=frag.mz, int=frag.int, experiment=exp)
        session.add(frag_i)
