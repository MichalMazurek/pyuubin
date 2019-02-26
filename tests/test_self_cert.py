from yuubin.certs import create_self_signed_certificate
from click.testing import CliRunner
from pathlib import Path
from subprocess import run


def test_creation():

    runner = CliRunner()

    with runner.isolated_filesystem():

        create_self_signed_certificate("./cert", "./private_key")

        assert Path("./cert").exists()
        assert Path("./private_key").exists()

        assert Path("./private_key").read_text() != ""

        result = run(["openssl", "verify", "-CAfile", "./cert", "./cert"], stderr=True, stdout=True)
        assert result.returncode == 0, result.stdout()

