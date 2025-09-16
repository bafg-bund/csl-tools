from csl.rtscan_functions.operation_rtscan import OperationRtscan


class RecalcRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for recalculating and replacing all non-experimental RTs in the CSL."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Executing recalc rtscan workflow')

        logger.info('End of recalc rtscan workflow')
