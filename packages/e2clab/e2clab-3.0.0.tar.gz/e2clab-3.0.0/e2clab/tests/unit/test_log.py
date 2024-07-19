import logging

import e2clab.log as e2clog
from e2clab.constants import LOG_ERR_FILENAME, LOG_INFO_FILENAME
from e2clab.tests.unit import TestE2cLab


class TestLog(TestE2cLab):

    def setUp(self) -> None:
        e2clog.init_logging(
            level=logging.INFO,
            file_handler=True,
            mute_ansible=True,
            file_path=self.test_folder,
        )
        # Path to logging files
        self.info_log = self.test_folder / LOG_INFO_FILENAME
        self.err_log = self.test_folder / LOG_ERR_FILENAME

    def test_getLogger(self):
        log = e2clog.getLogger(__name__, None)
        with self.assertLogs(__name__, level="INFO") as cm:
            log.info("test")
            log.debug("debug")
            log.warning("warn")
        self.assertEqual(len(cm.output), 2)
        self.assertIn("[E2C] test", cm.output[0])
        self.assertIn("[E2C] warn", cm.output[1])

        # Check logging files existence
        self.assertTrue(self.info_log.exists())
        self.assertTrue(self.err_log.exists())

    def tearDown(self):
        e2clog.init_logging(file_handler=False)
        # Remove logging files
        self.info_log.unlink()
        self.err_log.unlink()
