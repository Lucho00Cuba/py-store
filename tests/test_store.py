import unittest
import json
import os
from unittest.mock import MagicMock, patch, mock_open
from store import Store
from collections import OrderedDict


class TestStore(unittest.TestCase):

    def setUp(self):
        """Set up a temporary file for testing"""
        self.test_file = 'test_store.json'
        self.store = Store(self.test_file)
        self.store._data = {}  # Initialize with empty data

    def tearDown(self):
        """Clean up the temporary file after tests"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_init_invalid_path(self):
        """Test invalid path initialization"""
        with self.assertRaises(TypeError):
            Store(123)

    def test_load_create_file(self):
        """Test that the JSON file is created if it does not exist and loaded correctly."""
        # Create an instance of Store
        store = Store(self.test_file)

        # Verify that the file was created with the expected initial content
        with open(self.test_file, 'r') as f:
            content = f.read()
            self.assertTrue(content.startswith(
                '{'), "File should start with '{'")
            self.assertTrue(content.endswith('}'), "File should end with '}'")
            # Optionally, parse the JSON to verify its structure
            data = json.loads(content)
            self.assertEqual(
                data, {"_data": {}}, "The JSON file should have the expected initial structure.")

        # Verify that the Store's _data is initialized correctly
        self.assertEqual(store._data, OrderedDict({'_data': OrderedDict()}))

        # Add data, save it, and reopen to verify persistence
        store['key'] = 'value'
        store._save()
        store = Store(self.test_file)  # Reopen the store

        # Verify that data is correctly loaded after reopening
        self.assertEqual(store['key'], 'value')

    def test_load_existing_file(self):
        """Test loading data from an existing file"""
        with open(self.test_file, 'w') as f:
            f.write('{}')
        self.store._load()
        self.assertEqual(self.store._data, {})

    def test_save_creates_temp_file(self):
        """Test that the temporary file is created and saved correctly."""
        self.store._data = {"key": "value"}
        with patch('builtins.open', mock_open()) as mocked_file:
            with patch('os.replace') as mocked_replace:
                # Mock os.path.exists to return True to simulate the existence of the file
                with patch('os.path.exists', return_value=True):
                    self.store._save()
                    # Verify the temp file is opened for writing in binary mode
                    mocked_file.assert_called_once_with(
                        self.store._path + "~", 'wb')
                    handle = mocked_file()
                    handle.write.assert_called_once_with(json.dumps(
                        self.store._data, indent=self.store._indent).encode('utf-8'))
                    mocked_replace.assert_called_once_with(
                        self.store._path + "~", self.store._path)

    # def test_save_raises_error_if_temp_file_does_not_exist(self):
    #     """Test that an error is raised if the temporary file does not exist."""
    #     self.store._data = {"key": "value"}
    #     with patch('builtins.open', mock_open()) as mocked_file:
    #         with patch('os.replace') as mocked_replace:
    #             # Mock os.path.exists to return False to simulate the non-existence of the file
    #             with patch('os.path.exists', return_value=False):
    #                 # The _save method should raise an OSError due to the non-existent temp file
    #                 with self.assertRaises(OSError):
    #                     self.store._save()

    def test_context_manager(self):
        """Test using the context manager"""
        with self.store as store:
            store._data['key'] = 'value'
        self.assertEqual(self.store._data['key'], 'value')

    def test_get_set_delete_attr(self):
        """Test accessing, setting, and deleting attributes"""
        # Test getting attribute
        self.store._data['attribute'] = 'value'
        self.assertEqual(self.store.attribute, 'value')

        # Test setting attribute
        self.store.attribute = 'new_value'
        self.assertEqual(self.store._data['attribute'], 'new_value')

        # Test deleting attribute
        del self.store.attribute
        self.assertNotIn('attribute', self.store._data)

    def test_get_set_delete_item(self):
        """Test setting, getting, and deleting items"""
        # Test setting and getting item
        self.store['key'] = 'value'
        self.assertEqual(self.store['key'], 'value')

        # Test deleting item
        del self.store['key']
        with self.assertRaises(KeyError):
            self.store['key']

    def test_contains(self):
        """Test checking containment with __contains__"""
        self.store['key'] = 'value'
        self.assertIn('key', self.store)
        self.assertNotIn('nonexistent_key', self.store)

    def test_context_manager_commit(self):
        """Test committing changes with the context manager"""
        # Test committing changes
        with self.store:
            self.store['user.age'] = 30
        self.assertEqual(self.store['user.age'], 30)

    def test_context_manager_rollback(self):
        """Test rolling back changes with the context manager"""
        # Test rolling back changes
        with self.assertRaises(ValueError):
            with self.store:
                self.store['user.age'] = 30
                raise ValueError("Rolling back changes")

        # Ensure rollback has occurred
        self.assertNotIn('user.age', self.store)

    def test_auto_commit(self):
        """Test that changes are automatically committed"""
        self.store['user.email'] = 'jane@example.com'
        new_store = Store(self.test_file)
        self.assertEqual(new_store['user.email'], 'jane@example.com')

    def test_missing_intermediate_keys(self):
        """Test setting a value with missing intermediate keys"""
        self.store['user.profile.email'] = 'jane@example.com'
        self.assertEqual(self.store['user.profile.email'], 'jane@example.com')

    def test_invalid_key_and_value_types(self):
        """Test handling of invalid key and value types"""
        # Invalid key type
        with self.assertRaises(TypeError):
            self.store[123] = 'invalid'

        # Invalid value type
        with self.assertRaises(TypeError):
            self.store['user.name'] = set([1, 2, 3])


if __name__ == '__main__':
    unittest.main()
