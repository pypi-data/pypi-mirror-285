import unittest
import sys
sys.path.append('/Users/max/Documents/Flyio/cyborgai_server')
from evo.evo_framework.core.evo_core_system.utility.IuSystem import IuSystem

class TestPip(unittest.TestCase):
    def test_do_install_requirements(self):
        IuSystem.do_install_requirements('/Users/max/Documents/Flyio/cyborgai_server/evo/evo_packages/evo_package_youtube/requirements.txt')


if __name__ == '__main__':
    unittest.main()