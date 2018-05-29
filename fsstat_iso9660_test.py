import unittest

import fsstat_iso9660
import tsk_helper



class TestFsstatISO(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.fractional_score = {}

    def testMC(self):
        with open('MC.iso.out') as f:
            expected = tsk_helper.strip_all(tsk_helper.get_fsstat_output(f))
        with open('MC.iso', 'rb') as f:
            actual = tsk_helper.strip_all(fsstat_iso9660.fsstat_iso9660(f))
        if len(expected) != len(actual):
            self.fail()
        self.assertEqual(expected, actual)

    def testwindows(self):
        with open('windows.iso.out') as f:
            expected = tsk_helper.strip_all(tsk_helper.get_fsstat_output(f))
        with open('windows.iso', 'rb') as f:
            actual = tsk_helper.strip_all(fsstat_iso9660.fsstat_iso9660(f))
        if len(expected) != len(actual):
            self.fail()
        self.assertEqual(expected, actual)

    def testdosj(self):
        with open('d-osj.iso.out') as f:
            expected = tsk_helper.strip_all(tsk_helper.get_fsstat_output(f))
        with open('d-osj.iso', 'rb') as f:
            actual = tsk_helper.strip_all(fsstat_iso9660.fsstat_iso9660(f))
        if len(expected) != len(actual):
            self.fail()
        self.assertEqual(expected, actual)

    def testMM(self):
        with open('MM.iso.out') as f:
            expected = tsk_helper.strip_all(tsk_helper.get_fsstat_output(f))
        with open('MM.iso', 'rb') as f:
            actual = tsk_helper.strip_all(fsstat_iso9660.fsstat_iso9660(f))
        if len(expected) != len(actual):
            self.fail()
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()