# import pytest
# from unittest.mock import patch
import genebe as gb


# @pytest.fixture
# def mock_requests_post():
#     with patch("your_module.genetic_annotation.requests.post") as mock_post:
#         yield mock_post


def test_annotate_variants_list():
    # Test case
    variants = ["6-160585140-T-G"]
    annotations = gb.annotate_variants_list(
        variants,
        use_ensembl=True,
        use_refseq=False,
        genome="hg38",
        batch_size=500,
        use_netrc=False,
        endpoint_url="https://api.genebe.net/cloud/api-public/v1/variants",
    )

    # Assertions
    assert len(annotations) == len(variants)

    anns = annotations[0]
    print(anns)

    assert anns["chr"] == "6"
    assert anns["pos"] == 160585140
