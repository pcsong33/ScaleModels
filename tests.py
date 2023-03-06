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

    # Helper function to create test directory
    def create_dir(self, dir):
        if os.path.isdir(dir):
            self.empty_directory(dir)
        else:
            os.mkdir(dir)

    def csv_to_list(self, filename):
        rows = []
        with open(filename, 'r', newline='') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                rows.append(row)
        return rows


    def test_init_log(self):
        self.create_dir(DIR)

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
        rows = self.csv_to_list(process.filename)
        self.assertEqual(rows, [['logical clock', 'global time', 'event type', 'queue length']])

        # check that multiple logs can be created
        for i in range(1, 10):
            ModelMachine(1, ['port1', 'port2', i], DIR).init_log()
        self.assertEqual(len(os.listdir(DIR)), 10)

        self.empty_directory(DIR)
        os.rmdir(DIR)

    def test_update_log(self):
        self.create_dir(DIR)
        process = ModelMachine(1, ['port1', 'port2', 0], DIR)
        process.init_log()
        for i in range(100):
            process.update_log([i, i, i, i])

        data = self.csv_to_list(process.filename)[1:]
        expected = [[str(i)]*4 for i in range(100)]

        self.assertEqual(data, expected)

        self.empty_directory(DIR)
        os.rmdir(DIR)


if __name__ == '__main__':
    unittest.main()




