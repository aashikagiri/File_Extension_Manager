import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
from your_module import get_file_extension_with_fleep, create_database, log_rename, rename_file, undo_rename, read_log, entry_path, result_text

class TestFileManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_database()

    def setUp(self):
        # Create a temporary file for testing
        self.test_file = 'test_file.jpg'
        with open(self.test_file, 'wb') as f:
            f.write(b'\xFF\xD8\xFF\xE0')  # JPEG file signature

    def tearDown(self):
        # Remove the temporary file after tests
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_get_file_extension_with_fleep(self):
        extension = get_file_extension_with_fleep(self.test_file)
        self.assertEqual(extension, 'jpg')

    @patch('your_module.ask_for_new_name', return_value='new_name.jpg')
    @patch('os.rename')
    def test_rename_file(self, mock_rename, mock_ask_for_new_name):
        # Mock the entry path to simulate the file renaming
        with patch('your_module.entry_path.get', return_value=self.test_file):
            rename_file()
            mock_rename.assert_called_once_with(self.test_file, os.path.join(os.path.dirname(self.test_file), 'new_name.jpg'))
            self.assertTrue(os.path.exists(os.path.join(os.path.dirname(self.test_file), 'new_name.jpg')))

    @patch('your_module.entry_path.get', return_value=os.path.join(os.path.dirname(self.test_file), 'new_name.jpg'))
    @patch('os.rename')
    def test_undo_rename(self, mock_rename, mock_entry_path_get):
        # Set up initial rename log entry
        log_rename('test_file.jpg', 'new_name.jpg')
        # Mock renaming to undo
        with patch('your_module.entry_path.get', return_value=os.path.join(os.path.dirname(self.test_file), 'new_name.jpg')):
            undo_rename()
            mock_rename.assert_called_once_with(os.path.join(os.path.dirname(self.test_file), 'new_name.jpg'), self.test_file)
            self.assertTrue(os.path.exists(self.test_file))

    @patch('your_module.result_text.insert')
    @patch('your_module.result_text.config')
    def test_read_log(self, mock_config, mock_insert):
        log_rename('test_file.jpg', 'new_name.jpg')
        read_log()
        mock_insert.assert_called()

if __name__ == "__main__":
    unittest.main()
