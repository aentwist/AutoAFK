import json
import os

import pyscreeze
import pytest
from PIL import Image

from autoafk.tools import open_image
from test import TEST_DIR


def get_params() -> list[tuple[str, str]]:
    params: list[tuple[str, str]] = []

    with open(os.path.join(TEST_DIR, "ss-imgs-map.json")) as f:
        SS_IMGS_DICT = json.load(f)
        for ss, images in SS_IMGS_DICT.items():
            for image in images:
                params.append((image, ss))

    return params


def open_test_image(image: str) -> Image.Image:
    return Image.open(os.path.join(TEST_DIR, "ss", f"{image}.png"))


@pytest.mark.parametrize("image,ss", get_params())
def test_locate_img_in_ss(image: str, ss: str):
    assert bool(
        pyscreeze.locate(open_image(image), open_test_image(ss), confidence=0.9)
    )
