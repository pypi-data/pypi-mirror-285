import shutil

import e2clab.optimizer as e2copt
from e2clab.tests.unit import TestE2cLab


class MyOptimize(e2copt.Optimizer):

    def run(self):
        pass


class TestOptimizer(TestE2cLab):

    def test_optimizer(self):

        opt = MyOptimize(
            scenario_dir=self.test_folder,
            artifacts_dir=self.test_folder,
        )

        opt.prepare()
        opt.run()

        shutil.rmtree(opt.optimization_dir)
