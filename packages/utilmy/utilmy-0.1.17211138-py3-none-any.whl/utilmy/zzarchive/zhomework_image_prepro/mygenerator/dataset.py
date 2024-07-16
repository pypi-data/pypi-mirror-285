# -*- coding: utf-8 -*-
import io
import os
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import pandas as pd
from phone_gen import PhoneNumber

import mygenerator.util_image as util_image

#### Dataset element consists of: features, label and metadata
Meta = Dict[str, Any]
DatasetElement = Tuple[Any, Any, Meta]


##############################################################################################
class NlpDataset:
    """
    Elements of this dataset are related to text. It can be words,
    sentences or word embeddings (vectors).
    """

    def __init__(self, meta: pd.DataFrame):
        self.meta = meta

    def __len__(self) -> int:
        """Return number of elements in this dataset."""
        return len(self.meta)

    def get_sample(self, idx: int):
        meta = self.meta.iloc[idx]
        return self.get_text_only(idx), meta

    def get_text_only(self, idx: int) -> str:
        meta = self.meta.iloc[idx]
        text = meta["label"]
        return text


class PhoneNlpDataset(NlpDataset):
    """
    Elements of this dataset are related to text. It can be words,
    sentences or word embeddings (vectors).
    """

    def __init__(self, size: int = 1):
        meta_rows = []

        #### Randomly generate the dataset  ######################
        self.phone_gen = PhoneNumber("JP")
        for idx in range(size):
            s = self.get_phone_number(idx)
            meta_rows.append({"uri": "{}.txt".format(idx), "label": s})
        super().__init__(pd.DataFrame(meta_rows))

    def __len__(self) -> int:
        """Return number of elements in this dataset."""
        return len(self.meta)

    def get_phone_number(self, idx):
        s = self.phone_gen.get_number()
        # s = s.replace("+81", "0")  ### TODO : Move from Internationnal phone to local phone
        return s


class ImageDataset:
    """
    Elements of this dataset are related to images. Features of this
    elements are either image, or list of images. Images are represented
    as numpy arrays.
    Note: This dataset doesn't guarantee that images have the same size
    or same type (RGBA, Grayscale, etc).
    """

    def __init__(
        self,
        path: Optional[Union[str, pathlib.Path]] = None,
        get_image_fn=None,
        meta=None,
        image_suffix="*.png",
        **kwargs,
    ):
        """
        Args:
        * path - directory of the dataset or meta-data
        * get_image_fn - function for getting i-th image of the dataset
          directly from metadata part

        """
        if path is not None:
            if isinstance(path, str):
                path = pathlib.Path(path)

            assert path.is_dir(), path
            meta_rows = []
            for label_dir in path.iterdir():
                if not label_dir.is_dir():
                    continue

                for img_path in label_dir.glob(f"{image_suffix}"):
                    meta_rows.append(
                        {
                            "uri": str(img_path),
                            "label": label_dir.name,
                        }
                    )
            meta = pd.DataFrame(meta_rows)
            assert len(meta) > 0
        assert meta is not None
        self.meta = meta
        self.get_image_fn = get_image_fn

    def __len__(self) -> int:
        """Return number of elements in this dataset."""
        return len(self.meta)

    def get_image_only(self, idx: int) -> Union[np.ndarray, List[np.ndarray]]:
        """Return image of the single element of the dataset"""
        if self.get_image_fn is None:
            img_path = self.meta.iloc[idx]["uri"]
            return self.read_image(str(img_path))
        else:
            return self.get_image_fn(idx)

    def get_sample(self, idx: int) -> Tuple[Union[np.ndarray, List[np.ndarray]], Meta]:
        img = self.get_image_only(idx)
        meta = self.meta.iloc[idx]
        return (img, meta)

    def get_label_list(self, label: Any) -> np.ndarray:
        """Return indices of the elements which have certain label."""
        labels = self.meta["label"]
        if not isinstance(labels, np.ndarray):
            labels = np.asarray(labels)
        return np.flatnonzero(labels == label)

    def read_image(self, filepath_or_buffer: Union[str, io.BytesIO]):
        """
        Read a file into an image object
        Args:
            filepath_or_buffer: The path to the file, a URL, or any object
                with a `read` method (such as `io.BytesIO`)
        """
        return util_image.image_read(filepath_or_buffer)

    def save(self, path: str, prefix: str = "img", suffix: str = "png", nrows: int = -1):
        """Serialize on Disk the dataset elements
        Args:
            path:
        Returns: None

        """
        #### Serialize on disk
        os.makedirs(path, exist_ok=True)
        nmax = len(self) if nrows == -1 else min(len(self), nrows)
        for idx in range(nmax):
            img, meta = self.get_sample(idx)
            if img is not None:
                if img.shape[0] > 1 and img.shape[1] > 1:
                    cv2.imwrite(os.path.join(path, f"{prefix}_{idx}.{suffix}"), img)

        self.meta.to_csv(os.path.join(path, "meta.csv"), index=False)


def dataset_build_meta_mnist(
    path: Optional[Union[str, pathlib.Path]] = None,
    get_image_fn=None,
    meta=None,
    image_suffix="*.png",
    **kwargs,
):
    """
    Args:
    * path - directory of the dataset or meta-data
    * get_image_fn - function for getting i-th image of the dataset
    directly metadat part

    """
    if path is not None:
        if isinstance(path, str):
            path = pathlib.Path(path)

        assert path.exists(), path
        assert path.is_dir(), path
        meta_rows = []
        for label_dir in path.iterdir():
            if not label_dir.is_dir():
                continue

            for img_path in label_dir.glob(f"{image_suffix}"):
                meta_rows.append(
                    {
                        "uri": str(img_path),
                        "label": label_dir.name,
                    }
                )
        meta = pd.DataFrame(meta_rows)
        assert len(meta) > 0
    assert meta is not None
    meta.to_csv(path + "/metadata.csv")
