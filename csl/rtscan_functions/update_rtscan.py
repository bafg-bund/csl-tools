from csl.rtscan_functions.operation_rtscan import OperationRtscan


class UpdateRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for recalculating all retention time entries in the CSL."""

        import os.path
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing update rtscan workflow')

        logger.info('Not implemented yet')

        logger.info('End of update rtscan workflow')
