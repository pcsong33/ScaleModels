import unittest
from main import *
import os
import csv

DIR = 'test_logs'

class ScaleModelTest(unittest.TestCase):
    # Helper function to remove all files in a directory
    def empty_directory(self, dir):
        for file_name in os.listdir(dir):
            file = f'{dir}/{file_name}'
            if os.path.isfile(file):
                os.remove(file)

    def test_init_log(self):
        # create temporary test_logs directory, or empty an existing one
        if os.path.isdir(DIR):
            self.empty_directory(DIR)
        else:
            os.mkdir(DIR)

        process = ModelMachine(1, ['port1', 'port2', 0], DIR)

        # create file
        process.init_log()

        # check that file exists
        self.assertTrue(os.path.exists(process.filename))

        # update file
        process.update_log(['test', 'test', 'test', 'test'])

        # create another log with same name
        process.init_log()

        # check that there is only one file in the directory
        self.assertEqual(len(os.listdir(DIR)), 1)

        # check that old file has been overwritten
        rows = []
        with open(process.filename, 'r',  newline='') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                rows.append(row)
        self.assertEqual(rows, [['logical clock', 'global time', 'event type', 'queue length']])

        # check that multiple logs can be created
        for i in range(1, 10):
            ModelMachine(1, ['port1', 'port2', i], DIR).init_log()
        self.assertEqual(len(os.listdir(DIR)), 10)

        # delete directory after testing
        self.empty_directory(DIR)
        os.rmdir(DIR)

    def test_update_log(self):
        # If no operations have been logged, length is 1

        # System time should be incremented by 1
        pass


if __name__ == '__main__':
    unittest.main()




