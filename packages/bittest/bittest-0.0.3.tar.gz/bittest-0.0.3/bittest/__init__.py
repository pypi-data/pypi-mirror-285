import pickle
import os
import sys
import subprocess
import re
import glob
import unittest


class ChallengeSolution:
    def __init__(self, name, subdir=None, **kwargs):
        self.name = name
        self.subdir = subdir
        for key, value in kwargs.items():
            setattr(self, key, value)

    def check_tests_folder(self):
        """Simple function that returns path of the tests folder"""
        current_directory = os.getcwd()

        tests_folder_path = os.path.join(current_directory, 'tests')

        # Check if the 'tests' folder exists
        if not os.path.isdir(tests_folder_path):
            raise NameError("The 'tests' folder does not exist in the current directory.")

        return tests_folder_path

    def check_answer(self):
        """Write down values from initialize to result.pickle"""
        tests_path = self.check_tests_folder()

        result_file = os.path.join(tests_path, f"{self.name}.pickle")
        with open(result_file, 'wb') as file:
            pickle.dump(self, file)


        file_path = f"test_{self.name}.py"
        command = [sys.executable, "-m", "pytest", "-v", "--color=yes", file_path]
        sub_process = subprocess.Popen(command,
                             cwd=tests_path, # set current working directory
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, error = sub_process.communicate(b"")  # binary input passed as parameter
        result = output.decode("utf-8")

        return result


class ChallengeSolutionTestCase(unittest.TestCase):
    """Read pickle file to provide access to its results in the python test file
    """
    def setUp(self):
        """Load the pickle file"""
        current_directory = os.getcwd()

         # Get the name of the current class (test case class)
        klass = self.__class__.__name__

        # Convert class name to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', klass).lower()[len('test_'):]

        # Use glob to find the pickle file matching the class name in the current directory
        pickle_path = glob.glob(
        os.path.abspath(os.path.join(current_directory, f'{name}.pickle')), recursive=True)[0]

        # Store the found pickle file path
        result_file = pickle_path

        with open(result_file, 'rb') as file:
            self.result = pickle.load(file)
