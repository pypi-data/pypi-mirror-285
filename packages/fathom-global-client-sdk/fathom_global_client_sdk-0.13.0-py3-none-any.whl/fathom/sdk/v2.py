import dataclasses
import io
import logging
import os
import warnings
from typing import Dict, List, Optional, Union

import grpc
import requests
from google.protobuf.struct_pb2 import Struct
from protoc_gen_validate.validator import validate_all

from fathom.api.v2 import (
    common_pb2,
    fathom_pb2,
    fathom_pb2_grpc,
    portfolio_pb2,
    portfolio_pb2_grpc,
)
from fathom.sdk._internal import polygon_from_vector_file
from fathom.sdk._internal.geojson import load_geojson

from .client import FATHOM_GRPC_CHANNEL_MSG_SIZE, BaseClient
from .common import (
    PathOrString,
    write_tiff_data_to_file,
)
from .exceptions import PortfolioCSVError, TaskNotCompleteException

log = logging.getLogger(__name__)


class Client(BaseClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_address: str = "api.fathom.global",
        msg_channel_size: int = FATHOM_GRPC_CHANNEL_MSG_SIZE,
        *,
        grpc_interceptors: Optional[List[grpc.UnaryUnaryClientInterceptor]] = None,
    ):
        """Constructs a new Client, connected to a remote server.

        Args:
            client_id: Client ID to identify a registered client on the
                    authorization server.
            client_secret: Client Secret used with client_id to get an
                    access token.
            api_address: Address of the Fathom API server.
            msg_channel_size: gRPC message channel size, it is 10MB by
                default but if you will be dealing with data size larger than
                the default, you can configure the size.

        Attributes:
            geo (GeoClient): Client to talk to the geospatial data API
            geojson (GeoJSONClient): Client to talk to the geospatial data API using GeoJSON
            vector_file_name (VectorFileClient): Client to talk to the geospatial data API using vector file formats
            portfolio (PortfolioClient): Client to talk to the large portfolio API
        """

        super().__init__(
            client_id,
            client_secret,
            api_address,
            msg_channel_size,
            grpc_interceptors=grpc_interceptors,
        )

        self.geo: "GeoClient" = GeoClient(self)
        self.geojson: "GeoJSONClient" = GeoJSONClient(self)
        self.portfolio: "PortfolioClient" = PortfolioClient(self)
        self.vector_file_name: "VectorFileClient" = VectorFileClient(self)


@dataclasses.dataclass
class VectorFileClient:
    """Sub-client for fetching data using polygons encoded in vector files.

    Supported vector types:

    - KML and KMZ files
    - GeoJSON
    - Shapefiles
    - GeoPackage

    Each file must contain exactly one polygon 'feature' which follows the rules
    for other [polygon queries](../usage.md#polygon-queries).

    Additionally, GeoJSON files must follow the same rules as defined in
    the [GeoJSON query documentation](../usage.md#geojson-queries).

    Example: Vector file queries
        ```python
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        polygon_resp = client.vector_file_name.get_polygon_stats("/path/to/file.kml", layer_ids)
        # On Windows, use the 'r' prefix to the path:
        # polygon_resp = client.vector_file_name.get_polygon_stats(r"C:\\Users\\MyUser\\file.kml", layer_ids)
        ```
    """

    client: "Client"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        return self.client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    @staticmethod
    def _check_polygon_order(
        geojson: Dict,
        correct_polygon_points_order: bool,
    ):
        """Checks if the polygon contained in the geojson is in the right order.

        If correct_polygon_points_order is True, reverse the points. If not, just log a warning.
        """
        geom_type = geojson.get("type", None)
        if not geom_type or geom_type != "Polygon":
            # Wrong or no type - will be rejected by the API, with a useful error message
            return

        coordinates = geojson.get("coordinates", None)
        if (
            not coordinates
            or not isinstance(coordinates, list)
            or len(coordinates) != 1
            or not isinstance(coordinates[0], list)
        ):
            # Wrong number or no coordinates - will be rejected by the API, with a useful error message
            return

        angle = 0.0
        ring = coordinates[0]
        for i, _ in enumerate(ring):
            j = (i + len(ring) - 1) % len(ring)
            res = (ring[i][0] - ring[j][0]) * (ring[i][1] + ring[j][1])
            angle += res

        if angle > 0:
            if correct_polygon_points_order:
                geojson["coordinates"][0] = coordinates[0][::-1]
            else:
                logging.warning(
                    "Polygon ring must be in counter-clockwise order - this will be rejected by the API"
                )

    def get_polygon(
        self,
        vector_file_name: Union[str, os.PathLike],
        layer_ids: List[str],
        project_id: Optional[str] = None,
        *,
        correct_polygon_points_order: bool = False,
    ) -> fathom_pb2.GetPolygonDataResponse:
        """Returns data pertaining to a polygon contained in the given vector file.

        Args:
            vector_file_name: path to a vector file in one of the supported formats
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.
            correct_polygon_points_order:
                If set to True, attempt to correct the order of polygon points. If the polygon contained in the given vector
                file has points in the incorrect order (counter-clockwise) this will be rejected by the API, Enabling this
                option reverses the points before sending it to the API.
        """

        geojson = polygon_from_vector_file(vector_file_name)
        self._check_polygon_order(geojson, correct_polygon_points_order)

        return self.client.geojson.get_polygon(
            geojson,
            layer_ids=layer_ids,
            project_id=project_id,
        )

    def get_polygon_stats(
        self,
        vector_file_name: Union[str, os.PathLike],
        layer_ids: List[str],
        project_id: Optional[str] = None,
        *,
        correct_polygon_points_order: bool = False,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Returns stats pertaining to a polygon contained in the given vector file.

        Args:
            vector_file_name: path to a vector file in one of the supported formats
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.
            correct_polygon_points_order:
                If set to True, attempt to correct the order of polygon points. If the polygon contained in the given vector
                file has points in the incorrect order (counter-clockwise) this will be rejected by the API, Enabling this
                option reverses the points before sending it to the API.
        """

        geojson = polygon_from_vector_file(vector_file_name)
        self._check_polygon_order(geojson, correct_polygon_points_order)

        return self.client.geojson.get_polygon_stats(
            geojson,
            layer_ids=layer_ids,
            project_id=project_id,
        )


@dataclasses.dataclass
class PortfolioClient:
    """Sub-client for interacting with portfolios

    Example: Triggering large portfolio requests
        ```python
        import time

        from fathom.api.v2 import portfolio_pb2
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        create_resp = client.portfolio.create_task(layer_ids)

        client.portfolio.upload_portfolio_csv(create_resp.upload_url, "/path/to/input.csv")

        for i in range(100):
            time.sleep(10)

            status = client.portfolio.task_status(create_resp.task_id)
            if status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
                break
            elif status.task_status == portfolio_pb2.TASK_STATUS_ERROR:
                raise Exception(f"task failed: {status}")
        else:
            raise Exception("task was not ready in time")

        num_bytes_read = client.portfolio.attempt_task_result_download(
            create_resp.task_id, "/path/to/output.csv"
        )
        ```
    """

    base_client: "BaseClient"

    def _service_stub(self) -> portfolio_pb2_grpc.PortfolioServiceStub:
        return self.base_client._get_stub(portfolio_pb2_grpc.PortfolioServiceStub)

    def create_task(
        self, layer_ids: List[str], project_id: Optional[str] = None
    ) -> portfolio_pb2.CreatePortfolioTaskResponse:
        """Create a new portfolio task

        Args:
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.
        """

        metadata = _metadata_from_project_id(project_id)
        request = portfolio_pb2.CreatePortfolioTaskRequest(
            layer_ids=layer_ids, metadata=metadata
        )

        validate_all(request)

        log.debug("Creating new portfolio task")

        return self._service_stub().CreatePortfolioTask(request)

    def task_status(self, task_id: str) -> portfolio_pb2.GetPortfolioTaskStatusResponse:
        """Gets the status of an existing portfolio task

        Args:
            task_id: ID of previously created portfolio task
        """

        request = portfolio_pb2.GetPortfolioTaskStatusRequest(
            task_id=task_id,
        )

        validate_all(request)

        log.debug(f"Getting status of task '{task_id}")

        return self._service_stub().GetPortfolioTaskStatus(request)

    def attempt_task_result_download(
        self, task_id: str, output_path: PathOrString, chunk_size: int = 1000
    ) -> int:
        """Attempts to download the result of a given task. Should only be called after a call to
        `task_status` has indicated that the task completed without errors, otherwise an
        exception will be raised.

        Args:
            task_id: ID of previously created portfolio task
            output_path: Name of file to download output in to. It will be OVERWRITTEN if it already exists.
            chunk_size: Override chunk size when downloading CSV

        Returns:
            Number of bytes downloaded

        Raises:
            TaskNotCompleteException: Task was not ready or there were errors during processing
        """

        task_status = self.task_status(task_id)
        if not task_status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
            raise TaskNotCompleteException(
                f"Expected task {task_id} to be COMPLETE, but was {task_status.task_status}"
            )

        log.debug(f"Downloading results of portfolio task to {output_path}")

        bytes_read = 0

        # stream response to avoid having to download hundreds of MB into memory first
        with open(output_path, "wb") as output_file:
            streaming_resp = requests.api.get(task_status.download_url, stream=True)

            for chunk in streaming_resp.iter_content(chunk_size):
                output_file.write(chunk)
                bytes_read += len(chunk)

        return bytes_read

    @staticmethod
    def upload_portfolio_csv(
        upload_url: str, input_path: PathOrString, *, timeout: int = 10
    ):
        """Uploads the given portfolio CSV file for the portfolio task

        Args:
            upload_url: upload url from a previous CreatePortfolioTaskResponse
            input_path: path to CSV file to upload
            timeout: timeout on uploading CSV
        """

        log.debug(f"Uploading portfolio input from {input_path}")

        with open(input_path, "rb") as csv_file:
            size = os.path.getsize(input_path)
            extra_headers = {
                "content-length": str(size),
                "content-type": "text/csv",
                "x-goog-content-length-range": "0,524288000",
            }
            resp = requests.api.put(
                url=upload_url,
                data=csv_file,
                headers=extra_headers,
                timeout=timeout,
            )

        if resp.status_code != 200:
            raise PortfolioCSVError(f"Error uploading CSV: {resp}")


@dataclasses.dataclass
class GeoClient:
    """A sub-client for synchronously fetching data for points or polygons."""

    base_client: "BaseClient"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        return self.base_client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    def get_points(
        self,
        points: List[fathom_pb2.Point],
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPointsDataResponse:
        """Returns data pertaining to a list of lat-lng coordinates.

        Args:
            points: A list of coordinates.
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.
        """

        request = fathom_pb2.GetPointsDataRequest(
            points=points,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetPointsData(request)

    def get_polygon(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPolygonDataResponse:
        """Returns data pertaining to a polygon coordinates.

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: Idenitifier to differentiate projects using the API.
        """
        request = fathom_pb2.GetPolygonDataRequest(
            polygon=polygon,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetPolygonData(request)

    def get_polygon_stats(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Returns statistics about polygons using the given layer_ids

        This is similar to the get_polygons method, but will only return statistics about the polygon,
        not the polygon itself. To see what statistics are returned, see [the gRPC documentation](
        ../compile_proto_docs.md#polygonstats_1)

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: Idenitifier to differentiate projects using the API.
        """

        request = fathom_pb2.GetPolygonStatsRequest(
            polygon=polygon,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetPolygonStats(request)


@dataclasses.dataclass
class GeoJSONClient:
    """A client to fetch data from the fathom SDK using [GeoJSON](https://geojson.org/).

    The `geojson` input to the method parameters should be one of:

    - An opened file object
    - A string or bytes containing raw GeoJSON
    - A [PathLike](https://docs.python.org/3/library/os.html#os.PathLike) object with the filepath to a geojson file
    - A Python dictionary containing the GeoJSON

    Example: GeoJSON queries
        ```python
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        # With an opened file
        with open("/path/to/geo.json") as geojson_file:
            polygon_resp = client.geojson.get_polygon_stats(geojson_file, layer_ids)

        # With a geojson string
        geojson_string = '{"type": ...}'
        polygon_resp = client.geojson.get_polygon(geojson_string, layer_ids)

        # With a Python dictionary
        polygon_geojson = {
            ...
        }
        polygon_resp = client.geojson.get_polygon(polygon_geojson, layer_ids)
        ```
    """

    base_client: "BaseClient"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        return self.base_client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    def get_polygon(
        self,
        geojson: Union[
            os.PathLike, str, bytes, bytearray, io.BufferedIOBase, io.TextIOBase, Dict
        ],
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPolygonDataResponse:
        """Returns data pertaining to a polygon coordinates encoded in GeoJSON."""

        loaded_geojson = load_geojson(geojson)

        buffer = Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetGeoJSONPolygonDataRequest(
            polygon_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetGeoJSONPolygonData(request)

    def get_polygon_stats(
        self,
        geojson: Union[
            os.PathLike, str, bytes, bytearray, io.BufferedIOBase, io.TextIOBase, Dict
        ],
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Returns statistics about polygons using the given layer_ids"""

        loaded_geojson = load_geojson(geojson)

        buffer = Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetGeoJSONPolygonStatsRequest(
            polygon_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetGeoJSONPolygonStats(request)

    def get_points(
        self,
        geojson: Union[
            os.PathLike, str, bytes, bytearray, io.BufferedIOBase, io.TextIOBase, Dict
        ],
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPointsDataResponse:
        """Returns data pertaining to points encoded in GeoJSON."""

        loaded_geojson = load_geojson(geojson)

        buffer = Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetGeoJSONPointsDataRequest(
            points_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetGeoJSONPointsData(request)


def _metadata_from_project_id(
    project_id: Optional[str],
) -> Optional[Dict[str, str]]:
    return common_pb2.Metadata(project_id=project_id) if project_id else None


def point(lat: float, lng: float) -> fathom_pb2.Point:
    """Returns a Point object for use with Client.get_point()."""
    return fathom_pb2.Point(
        latitude=lat,
        longitude=lng,
    )


def polygon(points: List[fathom_pb2.Point]) -> fathom_pb2.Polygon:
    """Returns a Polygon object for use with Client.get_polygon()."""
    return fathom_pb2.Polygon(points=points)


def write_tiffs(
    response: fathom_pb2.GetPolygonDataResponse,
    output_dir: PathOrString,
    *,
    pattern: str = "{layer_id}.tif",
):
    """Given a polygon data response, write polygon tiff data in the response to the output directory.

    If any polygon result in the response was fully 'no data' (see [key values documentation](../usage.md#key-values)),
    the output tiff will not be written.

    Args:
        response: A response from a `get_polygon` request
        output_dir: the directory to write the tiff data to
        pattern: The pattern to save the file as. Formatted using normal Python string formatting,
            with the only available key being :
                - 'layer_id': the layer id
                - 'sep': The os-specific directory separator
    """

    polygon: fathom_pb2.PolygonResult
    for layer_id, polygon in response.results.items():
        if polygon.code == fathom_pb2.POLYGON_RESULT_CODE_OUT_OF_BOUNDS:
            warnings.warn(
                f"polygon result for layer {layer_id} was all 'no data' - no output file will be written for this "
                "result. In future, this will raise an exception.",
                FutureWarning,
                stacklevel=2,
            )
            continue

        write_tiff_data_to_file(polygon.geo_tiff, layer_id, output_dir, pattern, 0)
