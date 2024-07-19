import os
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

import e2clab.cli as e2cli
from e2clab.constants import PATH_SERVICES_PLUGINS, WORKFLOW_CONF_FILE
from e2clab.tests.unit import TestE2cLab


class TestCLI(TestE2cLab):

    def setUp(self):

        self.test_service = self.test_folder / "service" / "Default2.py"
        self.test_notaservice = self.test_folder / "service" / "Default3.py"

        self.runner = CliRunner()
        self.invalid_test_folder = self.test_folder / "tmp"
        os.mkdir(self.invalid_test_folder)
        for file in self.test_folder.glob("invalid_*"):
            dest_name = file.name.replace("invalid_", "")
            dest_path = self.invalid_test_folder / dest_name
            shutil.copy(file, dest_path)

    def tearDown(self):
        shutil.rmtree(self.invalid_test_folder)
        pass

    @pytest.mark.skip("No automated providers id for runner")
    def test_check_testbeds(self):
        result = self.runner.invoke(e2cli.check_testbeds, [])
        self.assertEqual(result.exit_code, 0)

    def test_check_argument(self):
        folder = str(self.test_folder)
        invalid_folder = str(self.invalid_test_folder)
        result = self.runner.invoke(e2cli.check_configuration, [folder])
        self.assertEqual(result.exit_code, 0)
        result = self.runner.invoke(e2cli.check_configuration, [folder, "-c", "deploy"])
        self.assertEqual(result.exit_code, 0)
        result = self.runner.invoke(
            e2cli.check_configuration, [folder, "-c", "notacommand"]
        )
        self.assertEqual(result.exit_code, 2)
        result = self.runner.invoke(e2cli.check_configuration, [invalid_folder])
        self.assertEqual(result.exit_code, 1)
        result = self.runner.invoke(e2cli.check_configuration, ["Notafolder"])
        self.assertEqual(result.exit_code, 2)

    def test_services_list(self):
        result = self.runner.invoke(e2cli.list, [])
        self.assertEqual(result.exit_code, 0)

    def test_services_add(self):
        result = self.runner.invoke(e2cli.add, ["dontexist"])
        self.assertEqual(result.exit_code, 2)

        is_a_folder = self.test_folder
        folder_path = self.get_filepath_str(is_a_folder)
        result = self.runner.invoke(e2cli.add, [folder_path])
        self.assertEqual(result.exit_code, 1)

        not_python_file = self.test_folder / WORKFLOW_CONF_FILE
        file_path = self.get_filepath_str(not_python_file)
        result = self.runner.invoke(e2cli.add, [file_path])
        self.assertEqual(result.exit_code, 1)

        dummy_service = self.test_service
        dummy_file_path = self.get_filepath_str(dummy_service)

        # Try adding a service using a copy
        result = self.runner.invoke(e2cli.add, [dummy_file_path, "--copy"])
        self.assertEqual(result.exit_code, 0)

        # Try adding an already present service
        result = self.runner.invoke(e2cli.add, [dummy_file_path])
        self.assertEqual(result.exit_code, 1)

        file_to_clean = PATH_SERVICES_PLUGINS / dummy_service.name
        file_to_clean.unlink()

        # Try adding a serice using a symlink
        result = self.runner.invoke(e2cli.add, [dummy_file_path, "--link"])
        self.assertEqual(result.exit_code, 0)

        file_to_clean = PATH_SERVICES_PLUGINS / dummy_service.name
        file_to_clean.unlink()

        # Try importing an invalid service
        inv_service = self.get_filepath_str(self.test_notaservice)
        result = self.runner.invoke(e2cli.add, [inv_service])
        self.assertEqual(result.exit_code, 1)

    def test_services_remove(self):
        result = self.runner.invoke(e2cli.remove, ["Default"])
        self.assertEqual(result.exit_code, 1)

        result = self.runner.invoke(e2cli.remove, ["Notaservice"])
        self.assertEqual(result.exit_code, 1)

        # Copying a valid dummy service to be removed
        shutil.copy(self.test_service, PATH_SERVICES_PLUGINS)

        result = self.runner.invoke(e2cli.remove, [self.test_service.stem])
        self.assertEqual(result.exit_code, 0)

    def get_filepath_str(self, not_python_file: Path) -> str:
        file_path = str(not_python_file.resolve())
        return file_path
