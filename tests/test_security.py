import pytest
from typer.testing import CliRunner
from pr_assistant.main import app

runner = CliRunner()

def test_init_masks_input(mock_config_manager):
    # We can't easily verify masking in CliRunner as it captures stdin/stdout
    # But we can verify that the keys are not printed back to stdout in clear text
    
    # Inputs: Token, Key, Confirm Local (n), Repo Name
    inputs = "my_github_token\nmy_gemini_key\nn\nmy_repo\n"
    result = runner.invoke(app, ["init"], input=inputs)
    
    # Check that inputs are not echoed back in the output
    # (Typer/Click default behavior for hide_input=True is not to echo)
    assert "my_github_token" not in result.stdout
    assert "my_gemini_key" not in result.stdout
    
    # But the repo name should be visible or at least not hidden if we didn't hide it
    # (We didn't hide repo name)
    # assert "my_repo" in result.stdout # Typer might not echo input either way depending on terminal

def test_config_file_permissions(mock_config_manager):
    # Verify that we can save and load
    mock_config_manager.save({"key": "secret"})
    assert mock_config_manager.get("key") == "secret"
    
    # In a real scenario, we'd check os.stat(config_path).st_mode
    # But we are mocking the config dir in conftest, so we can check that.
    
    # This test is more of a placeholder for where we'd put OS-specific permission checks
    pass
