from csl.export_functions.format_export import FormatExport
from csl.export_functions.utils import *
from csl.utils.sql_utils import *

class SqliteExport(FormatExport):
    def export(self):
        """Workflow to export a subset of the CSL data to a new sqlite file."""

        import logging
        from pathlib import Path
        import os.path
        import shutil
        from sqlalchemy.orm import joinedload
        from sqlalchemy import text

        logger = logging.getLogger(__name__)
        logger.info('Executing export workflow for creating a CSL subset (sqlite workflow)')

        # Generate the output file name based on the CSL file and the subset information
        fname = f"{Path(self.path_csl).stem}-{'-'.join(self.subset)}.db"
        fpath_out = os.path.join(self.path_out, fname)

        # Connect to the CSL database
        session_source = create_session(self.path_csl)

        # Get experiment IDs
        experiment_ids = get_experiment_ids_by_exp_group(session=session_source, data_source=self.subset)
        logger.info(f"Found {len(experiment_ids)} experiment ID's for subset: {self.subset}")

        # Copy the sqlite file
        shutil.copyfile(self.path_csl, fpath_out)

        # Open SQLAlchemy session for the new file
        session = create_session(fpath_out)

        # Load the experiments to keep
        exp_to_keep = session.query(Experiment) \
            .options(joinedload(Experiment.compound), joinedload(Experiment.parameter)) \
            .filter(Experiment.experiment_id.in_(experiment_ids)) \
            .all()

        # Delete all other experiments and related information
        if exp_to_keep:
            # Delete all other experiments
            session.query(Experiment).filter(~Experiment.experiment_id.in_(experiment_ids)).delete(
                synchronize_session=False)

            # Delete parameters
            session.query(Parameter).filter(~Parameter.parameter_id.in_(
                session.query(Experiment.parameter_id)
            )).delete(synchronize_session=False)

            # Delete compounds
            session.query(Compound).filter(~Compound.compound_id.in_(
                session.query(Experiment.compound_id)
            )).delete(synchronize_session=False)

            # Delete fragments
            session.query(Experiment.fragments.property.mapper.class_).filter(
                ~Experiment.fragments.property.mapper.class_.experiment_id.in_(
                    session.query(Experiment.experiment_id)
                )
            ).delete(synchronize_session=False)

            # Delete retention times
            session.query(RetentionTime).filter(~RetentionTime.compound_id.in_(
                session.query(Experiment.compound_id)
            )).delete(synchronize_session=False)

            # Delete experiment group information
            session.query(expGroupExp).filter(
                ~expGroupExp.c.experiment_id.in_(
                    session.query(Experiment.experiment_id)
                )
            ).delete(synchronize_session=False)

            # Delete compound group information
            session.query(compGroupComp).filter(
                ~compGroupComp.c.compound_id.in_(
                    session.query(Compound.compound_id)
                )
            ).delete(synchronize_session=False)

            # Commit changes to session
            session.commit()

            # VACUUM to reduce file size
            session.execute(text("VACUUM"))
        else:
            logger.warning(f"Experiment ID(s) {experiment_ids} not found in the database!")

        # Close the session
        session.close()

        logger.info('End of sqlite export workflow')
