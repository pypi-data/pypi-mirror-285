import functools
import io
import json
import os
import pathlib
from typing import Any, Dict, Union

from fathom.sdk.exceptions import GeoJSONError


@functools.singledispatch
def load_geojson(
    geojson: Union[
        os.PathLike, str, bytes, bytearray, io.BufferedIOBase, io.TextIOBase, Dict
    ],
) -> Dict:
    raise NotImplementedError(f"Cannot load geojson from {type(geojson)}")


@load_geojson.register(os.PathLike)
def load_geojson_path(
    geojson: os.PathLike,
) -> Dict:
    return json.loads(pathlib.Path(geojson).read_text())


@load_geojson.register(str)
@load_geojson.register(bytes)
@load_geojson.register(bytearray)
def load_geojson_string(
    geojson: Union[str, bytes, bytearray],
) -> Dict:
    if isinstance(geojson, str) and os.path.exists(geojson):
        raise GeoJSONError(
            "When passing a filepath to a GeoJSON file, the argument should be wrapped using `pathlib.Path`"
        )

    return json.loads(geojson)


@load_geojson.register(io.BufferedIOBase)
@load_geojson.register(io.TextIOBase)
def load_geojson_buffer(
    geojson: Union[io.BufferedIOBase, io.TextIOBase],
) -> Dict:
    return json.load(geojson)


@load_geojson.register(dict)
def load_geojson_dict(
    geojson: Dict,
) -> Dict:
    return geojson


def polygon_from_geojson(geojson: Any) -> Dict:
    """Loads the geojson from the given object - polygon verification is done server-side"""
    return load_geojson(geojson)
