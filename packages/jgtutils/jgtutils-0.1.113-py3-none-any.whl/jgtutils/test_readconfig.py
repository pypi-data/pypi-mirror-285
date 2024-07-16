import pytest
import os
import json
from jgtcommon import readconfig

def test_readconfig():
    # Mock data
    mock_config = {"key": "value"}
    mock_config_str = json.dumps(mock_config)
    mock_config_file = 'mock_config.json'
    with open(mock_config_file, 'w') as f:
        json.dump(mock_config, f)

    # Test reading from file
    result = readconfig(config_file=mock_config_file)
    assert result == mock_config

    # Test reading from environment variable
    os.environ['JGT_CONFIG'] = mock_config_str
    result = readconfig(config_file='non_existent_file.json')
    assert result == mock_config

    # Cleanup
    os.remove(mock_config_file)
    del os.environ['JGT_CONFIG']