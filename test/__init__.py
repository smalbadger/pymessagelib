import os
import sys
TEST_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.join(TEST_PATH, '..')
SOURCE_PATH = os.path.join(PROJECT_PATH, "pymessagelib")
sys.path.insert(0, TEST_PATH)
sys.path.insert(0, SOURCE_PATH)