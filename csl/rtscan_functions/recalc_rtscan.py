from .operation_rtscan import OperationRtscan


class RecalcRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for recalculating all retention time data in the CSL."""

        import os.path
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing recalc rtscan workflow')

        logger.info('Not implemented yet')

        logger.info('End of recalc rtscan workflow')
