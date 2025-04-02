from .operation_rtscan import OperationRtscan


class CheckRtscan(OperationRtscan):
    def rtscan(self):
        """Workflow for checking the status of the retention time data in the CSL, without making any changes."""

        import os.path
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing check rtscan workflow')

        logger.info('End of check rtscan workflow')
