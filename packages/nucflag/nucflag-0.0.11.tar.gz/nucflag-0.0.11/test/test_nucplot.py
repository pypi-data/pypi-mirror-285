import pytest
import subprocess


@pytest.mark.parametrize(
    ["bam", "bed", "expected", "config"],
    [
        # Standard case
        (
            "test/standard/HG00096_hifi.bam",
            "test/standard/region.bed",
            "test/standard/expected.bed",
            tuple(["-c", "test/config.toml"]),
        ),
        # Ignore regions
        (
            "test/ignored/HG00731_hifi.bam",
            "test/ignored/region.bed",
            "test/ignored/expected.bed",
            tuple(
                [
                    "-c",
                    "test/config.toml",
                    "--ignore_regions",
                    "test/ignored/ignore.bed",
                ]
            ),
        ),
        # Static misjoin threshold
        (
            "test/misjoin/HG00171_hifi.bam",
            "test/misjoin/region.bed",
            "test/misjoin/expected_static.bed",
            tuple(["-c", "test/misjoin/config_static.toml"]),
        ),
        # Percent misjoin threshold
        (
            "test/misjoin/HG00171_hifi.bam",
            "test/misjoin/region.bed",
            "test/misjoin/expected_perc.bed",
            tuple(["-c", "test/misjoin/config_perc.toml"]),
        ),
    ],
)
def test_identify_misassemblies(bam: str, bed: str, expected: str, config: tuple[str]):
    process = subprocess.run(
        ["python", "-m", "nucflag.main", "-i", bam, "-b", bed, *config],
        capture_output=True,
        check=True,
    )
    res = [line.split("\t") for line in process.stdout.decode().split("\n") if line]
    with open(expected, "rt") as exp_res_fh:
        exp_res = [line.strip().split("\t") for line in exp_res_fh.readlines() if line]
        assert res == exp_res
