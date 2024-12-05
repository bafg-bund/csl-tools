from .format_workflow import FormatWorkflow


class MbankWorkflow(FormatWorkflow):
    def export(self):
        """Workflow to export CSL data for massbank."""

        import os.path
        import logging
        logger = logging.getLogger(__name__)
        logger.info('Executing massbank export workflow')

        logger.info('End of massbank export workflow')
