from __future__ import annotations
from typing import Any, Optional, Union, List, Tuple, TYPE_CHECKING
import re
import warnings
import datetime as pydatetime

from geodesic.account.projects import Project, get_project
from geodesic.account.credentials import get_credential
from geodesic.account.tokens import Token
from geodesic.bases import _APIObject
from dateutil.parser import isoparse

from geodesic.service import ServiceClient
from dateutil.parser import parse

from geodesic.descriptors import (
    _BaseDescr,
    _DictDescr,
    _ListDescr,
    _IntDescr,
    _StringDescr,
    _TimeDeltaDescr,
    _TypeConstrainedDescr,
)
from geodesic.client import get_client, raise_on_error
from geodesic.account import get_active_project
from geodesic.entanglement import Object
from geodesic.boson import (
    AssetBands,
    BosonDescr,
    BosonConfig,
    MiddlewareConfig,
    CacheConfig,
    TileOptions,
    DEFAULT_CREDENTIAL_KEY,
    STORAGE_CREDENTIAL_KEY,
)
from geodesic.config import SearchReturnType
from geodesic.stac import (
    _AssetsDescr,
    STACAPI,
    FeatureCollection,
    _parse_date,
    Extent,
    Collection,
)
from geodesic.cql import CQLFilter
import numpy as np
from geodesic.utils import DeferredImport, datetime_to_utc, deprecated
from shapely.geometry import box, MultiPolygon, shape

if TYPE_CHECKING:
    try:
        from geopandas import GeoDataFrame
    except ImportError:

        class GeoDataFrame:
            pass


SEARCH_RETURN_TYPE = SearchReturnType.GEODATAFRAME
display = DeferredImport("IPython.display")
pyproj = DeferredImport("pyproj")
Image = DeferredImport("PIL", "Image")

datasets_client = ServiceClient("entanglement", 1, "datasets")
stac_client = ServiceClient("spacetime", 1, "stac")
boson_client = ServiceClient("boson", 1, "datasets")
ted_client = ServiceClient("ted", 1, "share")

stac_root_re = re.compile(r"(.*)\/collections\/")

_valid_resampling = [
    "nearest",
    "bilinear",
    "cubic",
    "cubicspline",
    "lanczos",
    "average",
    "mode",
    "max",
    "min",
    "median",
    "q1",
    "q3",
    "sum",
]


def get_dataset(
    name: str,
    project: str = None,
    version_datetime: Union[str, pydatetime.datetime] = None,
) -> "Dataset":
    """gets a Dataset from Entanglement by name

    Args:
        name: the name of a dataset to get
        project: the name of the project to search datasets. Defaults to the active project
        version_datetime: the point in time to search the graph - will return older versions of \
            datasets given a version_datetime.

    Returns:
        a DatasetList of matching Datasets.

    """
    dataset_list = get_datasets(names=[name], project=project, version_datetime=version_datetime)
    if len(dataset_list) == 0:
        raise ValueError(f"dataset '{name}' not found")
    elif len(dataset_list) > 1:
        raise ValueError(
            f"more than one dataset matching '{name}' found, this should not happen, please report this"
        )

    return dataset_list[0]


def get_datasets(
    names: Union[List, str] = [],
    search: str = None,
    project=None,
    version_datetime: Union[str, pydatetime.datetime] = None,
    deleted: bool = False,
) -> "DatasetList":
    """searchs/returns a list of Datasets from Entanglement based on the user's query

    Args:
        names: an optional list of dataset IDs to return
        search: a search string to use to search for datasets who's name/description match
        project: the name of the project to search datasets. Defaults to the active project
        version_datetime: the point in time to search the graph - will return older versions of \
            datasets given a version_datetime.
        deleted: if True, will return datasets that have been soft deleted. This allows you to\
            recover datasets that have been deleted by calling save() on them again.

    Returns:
        a DatasetList of matching Datasets.

    """

    if project is None:
        project = get_active_project()
    else:
        if isinstance(project, str):
            project = get_project(project)
        elif not isinstance(project, Project):
            raise ValueError("project must be a string or Project")

    params = {}
    if names:
        if isinstance(names, str):
            names = names.split(",")
        params["name"] = ",".join(names)

    if search is not None:
        params["search"] = search

    # Find object versions that were valid at a specific datetime
    if version_datetime is not None:
        # check for valid format
        if isinstance(version_datetime, str):
            params["version_datetime"] = datetime_to_utc(isoparse(version_datetime)).isoformat()
        elif isinstance(version_datetime, pydatetime.datetime):
            params["version_datetime"] = datetime_to_utc(version_datetime).isoformat()
        else:
            raise ValueError(
                "version_datetime must either be RCF3339 formatted string, or datetime.datetime"
            )

    params["deleted"] = deleted

    resp = boson_client.get(f"{project.uid}", **params)
    raise_on_error(resp)

    js = resp.json()
    if js["datasets"] is None:
        return DatasetList([])

    ds = [
        Dataset(**graph_info, **dataset)
        for graph_info, dataset in zip(js["graph_infos"], js["datasets"])
    ]
    datasets = DatasetList(ds, names=names)
    return datasets


list_datasets = deprecated("1.0.0", "list_datasets")(get_datasets)


def new_union_dataset(
    name: str,
    datasets: List["Dataset"],
    feature_limit: int = 1000,
    project: Optional[Union[Project, str]] = None,
    ignore_duplicate_fields: bool = False,
    middleware: MiddlewareConfig = {},
    cache: CacheConfig = {},
    tile_options: TileOptions = {},
    domain: str = "*",
    category: str = "*",
    type: str = "*",
    **kwargs: dict,
) -> "Dataset":
    """creates a new ``union`` of ``Datasets`` that provides data from all input Datasets

    Creates a new ``Dataset`` by combining multiple ``Datasets`` with the ``union`` operation. This means
    that a query to this provider will return the combination of results from all input ``Datasets``. This
    can be filtered down by the way of the ``collections`` parameter on ``query`` and the ``asset_bands`` parameter
    in the case of a ``get_pixels`` request. All image datasets must have either all the same assets/bands or all
    different.

    Args:
        name: the name of the new ``Dataset``
        datasets: a list of ``Datasets`` to ``union``
        feature_limit: the max size of a results page from a query/search
        project: the name of the project this will be assigned to
        ignore_duplicate_fields: if True, duplicate fields across providers will be ignored
        middleware: configure any boson middleware to be applied to the new dataset.
        cache: configure caching for this dataset
        tile_options: configure tile options for this dataset

    """
    collection = _stac_collection_from_kwargs(name, **kwargs)
    _remove_keys(collection, "id", "summaries", "stac_version")

    data_api = None
    item_type = None
    for dataset in datasets:
        if data_api is None:
            data_api = dataset.data_api
            item_type = dataset.item_type
        else:
            if dataset.data_api == "stac":
                data_api = "stac"
            if item_type not in ("features", "other"):
                item_type = item_type

    properties = dict(
        providers=[
            dict(
                dataset_name=dataset.name,
                project=dataset.project.uid,
                provider_config=dataset.boson_config,
            )
            for dataset in datasets
        ],
        ignore_duplicate_fields=ignore_duplicate_fields,
    )

    boson_cfg = BosonConfig(
        provider_name="union",
        max_page_size=feature_limit,
        properties=properties,
        middleware=middleware,
        cache=cache,
        tile_options=tile_options,
    )

    return boson_dataset(
        name=name,
        alias=collection.pop("title"),
        data_api=data_api,
        item_type=item_type,
        boson_cfg=boson_cfg,
        domain=domain,
        category=category,
        type=type,
        project=project,
        **collection,
    )


class DatasetInfo(_APIObject):
    """metadata about a boson dataset.

    This is obtained by calling the dataset-info endpoint in Boson. While there is some
    field overlap, this is usually dynamically generated by Boson and is not necessarily
    the same as the metadata set by the user. Especially in cases where a creator of a
    Dataset opted to not provide much metadata, Boson attempts to generate update to date
    information, depending on the provider used.

    This is particularly useful to inspect things like valid raster assets, min/max zoom,
    available fields for querying, and STAC collections.

    """

    name = _StringDescr(doc="name of this Dataset")
    alias = _StringDescr(doc="alias - human readable name of this Dataset")
    description = _StringDescr(doc="description of this Dataset")
    overall_extent = _TypeConstrainedDescr(
        (Extent, dict), doc="spatiotemporal extent of this Dataset"
    )
    min_zoom = _IntDescr(doc="Min Zoom (OSM Zoom Value) for this layer")
    max_zoom = _IntDescr(doc="Max Zoom (OSM Zoom Value) for this layer")
    raster_assets = _DictDescr(doc="dictionary of raster-assets fro this Dataset")
    default_asset_bands = _ListDescr(
        item_type=(AssetBands, dict),
        coerce_items=True,
        doc="default asset bands that will be used for requests that render raster data",
    )
    conforms_to = _ListDescr(doc="list of OGC/other standard conformances this dataset supports")
    queryables = _DictDescr(doc="dictionary of fields that this dataset has")
    links = _ListDescr(doc="list of links for this Dataset")
    collections = _ListDescr(
        item_type=(Collection, dict),
        coerce_items=True,
        doc="list of STAC/Features Collections this Dataset has",
    )
    provider_config = _TypeConstrainedDescr((BosonConfig, dict), doc="Boson provider config")


class Dataset(Object):
    """Allows interaction with SeerAI datasets.

    Dataset provides a way to interact with datasets in the SeerAI.

    Args:
        \\*\\*obj (dict): Dictionary with all properties in the dataset.

    Attributes:
        alias(str): Alternative name for the dataset. This name has fewer restrictions on characters and should be human
        readable.

    """

    hash = _StringDescr(nested="item", doc="hash of this dataset")
    alias = _StringDescr(nested="item", doc="the alias of this object, anything you wish it to be")
    data_api = _StringDescr(nested="item", doc="the api to access the data")
    item_type = _StringDescr(nested="item", doc="the api to access the data")
    item_assets = _AssetsDescr(
        nested="item", doc="information about assets contained in this dataset"
    )
    extent = _TypeConstrainedDescr(
        (Extent, dict), nested="item", doc="spatiotemporal extent of this Dataset"
    )
    services = _ListDescr(
        nested="item",
        item_type=str,
        doc="list of services that expose the data for this dataset",
    )
    providers = _ListDescr(nested="item", doc="list of providers for this dataset")
    stac_extensions = _ListDescr(nested="item", doc="list of STAC extensions this dataset uses")
    links = _ListDescr(nested="item", doc="list of links")
    metadata = _DictDescr(nested="item", doc="arbitrary metadata for this dataset")
    boson_config = BosonDescr(
        nested="item", doc="boson configuration for this dataset", default=BosonConfig()
    )

    def __init__(
        self,
        uid: str = None,
        iri: str = None,
        project: Union[Project, str] = None,
        qualifiers: dict = {},
        **obj,
    ):
        if "item" in obj:
            return super().__init__(
                uid=uid,
                project=project,
                **obj,
            )

        if project is None:
            project = get_active_project()

        # If this came from the Boson dataset API, this needs to be built as an object
        o = {
            "project": project,
        }

        if iri is not None:
            o["xid"] = iri
        if uid is not None:
            o["uid"] = uid

        name = obj.get("name")
        if name is None:
            return super().__init__(**qualifiers, **o)

        if "name" not in qualifiers:
            qualifiers = {
                "name": name,
                "domain": obj.get("domain", "*"),
                "category": obj.get("category", "*"),
                "type": obj.get("type", "*"),
            }
        o["alias"] = obj.get("alias", name)
        o["description"] = obj.get("description", "")
        o["keywords"] = obj.get("keywords", [])
        o["item"] = obj
        o["version_tag"] = obj.get("hash", "")

        # geom from extent
        extent = obj.get("extent", {})
        if extent is not None:
            spatial_extent = extent.get("spatial", None)
            if spatial_extent is not None:
                boxes = []
                for bbox in spatial_extent.get("bbox", []):
                    g = box(*bbox, ccw=False)
                    boxes.append(g)

                if len(boxes) == 1:
                    g = boxes[0]
                else:
                    g = MultiPolygon(boxes)

                self.geometry = g

        super().__init__(**o, **qualifiers)

    @property
    def object_class(self):
        return "Dataset"

    @object_class.setter
    def object_class(self, v):
        if v.lower() != "dataset":
            raise ValueError("shouldn't happen")
        self._set_item("class", "dataset")

    def save(self) -> "Dataset":
        """
        Create or update a Dataset in Boson.

        Returns:
            self

        Raises:
            requests.HTTPError: If this failed to save.

        """
        # Make sure the uid is either None or valid
        try:
            self.uid
        except ValueError as e:
            raise e

        body = {
            "dataset": self.item,
            "qualifiers": {
                "domain": self.domain,
                "category": self.category,
                "type": self.type,
            },
        }

        res = raise_on_error(boson_client.post(f"{self.project.uid}", **body))
        try:
            res_js = res.json()
            graph_info = res_js["graph_info"]
            dataset = res_js["dataset"]
        except KeyError:
            raise KeyError(f"invalid response {res_js}")

        self.__init__(**graph_info, **dataset)
        return self

    create = deprecated("1.0.0", "Dataset.create")(save)

    def _root_url(self, servicer: str) -> str:
        return f"{self.project.uid}/{self.name}/{servicer}"

    def _stac_client(self) -> STACAPI:
        # TODO: use hash when we ensure all datasets have one.
        # dataset_hash = self.get("hash")
        root = f"{boson_client._stub}/{self._root_url('stac')}"
        return STACAPI(root)

    def search(
        self,
        bbox: Optional[List] = None,
        datetime: Union[List, Tuple] = None,
        limit: Optional[Union[bool, int]] = 10,
        page_size: Optional[int] = 500,
        intersects: Optional[object] = None,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        filter: Optional[Union[CQLFilter, dict]] = None,
        fields: Optional[dict] = None,
        sortby: Optional[dict] = None,
        method: str = "POST",
        return_type: SearchReturnType = None,
        extra_params: Optional[dict] = {},
    ) -> Union[FeatureCollection, GeoDataFrame]:
        """Search the dataset for items.

        Search this service's OGC Features or STAC API.

        Args:
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            datetime: The temporal extent for the query formatted as a list: [start, end].
            limit: The maximum number of items to return in the query. If None, will page through all results
            page_size: If retrieving all items, this page size will be used for the subsequent requests
            intersects: a geometry to use in the query
            collections: a list of collections to search
            ids: a list of feature/item IDs to filter to
            filter: a CQL2 filter. This is supported by most datasets but will not work for others.
            fields: a list of fields to include/exclude. Included fields should be prefixed by '+' \
                    and excluded fields by '-'. Alernatively, a dict with a 'include'/'exclude' lists may be provided
            sortby: a list of sortby objects, which are dicts containing "field" and "direction". \
                    Direction may be one of "asc" or "desc". Not supported by all datasets
            method: the HTTP method - POST is default and usually should be left alone unless a server doesn't support
            return_type: the type of object to return. Either a FeatureCollection or a GeoDataFrame
            extra_params: a dict of additional parameters that will be passed along on the request.

        Returns:
            A :class:`geodesic.stac.FeatureCollection` with all items in the dataset matching the query.

        Examples:
            A query on the `sentinel-2-l2a` dataset with a given bounding box and time range. Additionally,
            you can apply filters on the parameters in the items

            >>> bbox = geom.bounds
            >>> date_range = (datetime.datetime(2020, 12,1), datetime.datetime.now())
            >>> ds.search(
            ...          bbox=bbox,
            ...          datetime=date_range,
            ...          filter=CQLFilter.lte("properties.eo:cloud_cover", 10.0)
            ... )

        """
        client = self._stac_client()

        # If limit is None, this will page through all results with the given page size (default 500)
        if limit is not None and limit < page_size:
            page_size = limit

        search_res = client.search(
            bbox=bbox,
            datetime=datetime,
            limit=page_size,
            intersects=intersects,
            collections=collections,
            ids=ids,
            filter=filter,
            fields=fields,
            sortby=sortby,
            method=method,
            extra_params=extra_params,
        )

        # pages through each page of the results if there are more than one page to request
        res = search_res.page_through_results(limit=limit)

        if return_type is None:
            return_type = SEARCH_RETURN_TYPE
        if return_type == SearchReturnType.FEATURE_COLLECTION:
            collection = res.feature_collection()
            collection.dataset = self
            collection._is_stac = True
            return collection
        return res.geodataframe()

    query = deprecated("1.0.0", "Dataset.query")(search)

    def get_pixels(
        self,
        *,
        bbox: list,
        datetime: Union[List, Tuple] = None,
        pixel_size: Optional[list] = None,
        shape: Optional[list] = None,
        pixel_dtype: Union[np.dtype, str] = np.float32,
        bbox_crs: str = "EPSG:4326",
        output_crs: str = "EPSG:3857",
        resampling: str = "nearest",
        no_data: Any = None,
        content_type: str = "raw",
        asset_bands: Union[List[AssetBands], AssetBands] = [],
        filter: dict = {},
        compress: bool = True,
        bbox_srs: str = None,
        output_srs: str = None,
        input_nodata: Any = None,
        output_nodata: Any = None,
    ):
        """get pixel data or an image from this `Dataset`

        `get_pixels` gets requested pixels from a dataset by calling Boson. This method returns either a
        numpy array or the bytes of a image file (jpg, png, gif, or tiff). If the `content_type` is
        "raw", this will return a numpy array, otherwise it will return the requested image format as
        bytes that can be written to a file. Where possible, a COG will be returned for Tiff format,
        but is not guaranteed.

        Args:
            bbox: a bounding box to export as imagery (xmin, ymin, xmax, ymax)
            datetime: a start and end datetime to query against. Imagery will be filtered to between this range and mosaiced.
            pixel_size: a list of the x/y pixel size of the output imagery. This list needs to have length equal to the number of bands. This should be specified in the output spatial reference.
            shape: the shape of the output image (rows, cols). Either this or the `pixel_size` must be specified, but not both.
            pixel_dtype: a numpy datatype or string descriptor in numpy format (e.g. <f4) of the output. Most, but not all basic dtypes are supported.
            bbox_crs: the spatial reference of the bounding bbox, as a string. May be EPSG:<code>, WKT, Proj4, ProjJSON, etc.
            output_crs: the spatial reference of the output pixels.
            resampling: a string to select the resampling method.
            no_data: in the source imagery, what value should be treated as no data?
            content_type: the image format. Default is "raw" which sends raw image bytes that will \
                be converted into a numpy array. If "jpg", "gif", or "tiff", returns the bytes of an image \
                file instead, which can directly be written to disk.
            asset_bands: either a list containing dictionaries with the keys "asset" and "bands" or \
                a single dictionary with the keys "asset" and "bands". Asset should point to an asset in \
                the dataset, and "bands" should list band indices \
                (0-indexed) or band names.
            filter: a CQL2 JSON filter to filter images that will be used for the resulting output.
            compress: compress bytes when transfering. This will usually, but not always improve performance
            input_nodata (deprecated): in the source imagery, what value should be treated as no data?
            output_nodata (deprecated): what value should be set as the nodata value in the resulting dataset. Only meaningful for tiff outputs.
            bbox_srs (deprecated): the spatial reference of the bounding bbox, as a string. May be EPSG:<code>, WKT, Proj4, ProjJSON, etc.
            output_srs (deprecated): the spatial reference of the output pixels.

        Returns:
            a numpy array or bytes of an image file.

        Examples:
            >>> # Get a numpy array of pixels from sentinel-2-l2a
            >>> bbox = [-109.050293,36.993778,-102.030029,41.004775] # roughly the state of Colorado
            >>> range = (datetime(2020,1,1), datetime(2020,2,1))
            >>> # The RGB bands of sentinel-2-l2a are B04, B03, B02
            >>> asset_bands = [AssetBands(asset="B04", bands=[0]), AssetBands(asset="B03", bands=[0]), AssetBands(asset="B02", bands=[0])]
            >>> pixels = ds.get_pixels(
            ...             bbox=bbox, 
            ...             datetime=range, 
            ...             pixel_size=(1000,1000), 
            ...             asset_bands=asset_bands, 
            ...             output_srs="EPSG:3857", 
            ...             bbox_srs="EPSG:4326",
            ...             )
            
            >>> # Get a numpy array of pixels from landsat-8
            >>> bbox = [-124.564576,32.380179,-113.991265,42.064555] # roughly the states of California and Nevada
            >>> # Just get the red band
            >>> pixels = ds.get_pixels(
            ...             bbox=bbox, 
            ...             datetime=(datetime(2022,1,1), datetime(2022,2,1)),
            ...             pixel_size=(1000,1000),
            ...             asset_bands=AssetBands(asset="B4", bands=[0]),
            ...             )
        """

        if pixel_size is None and shape is None:
            raise ValueError("must specify at least pixel_size or shape")
        elif pixel_size is not None and shape is not None:
            raise ValueError("must specify pixel_size or shape, but not both")

        if content_type not in ("raw", "jpeg", "jpg", "gif", "tiff", "png"):
            raise ValueError("content_type must be one of raw, jpeg, jpg, gif, tiff, png")

        if resampling not in _valid_resampling:
            raise ValueError(f'resampling must be one of {", ".join(_valid_resampling)}')

        if pixel_dtype in ["byte", "uint8"]:
            ptype = pixel_dtype
        else:
            ptype = np.dtype(pixel_dtype).name

        if bbox_srs is not None:
            warnings.warn(
                "bbox_srs is deprecated and will be removed in 1.0.0. Please use bbox_crs"
            )
            bbox_crs = bbox_srs
        if output_srs is not None:
            warnings.warn(
                "output_srs is deprecated and will be removed in 1.0.0. Please use output_crs"
            )
            output_crs = output_srs

        req = {
            "output_extent": bbox,
            "output_extent_spatial_reference": bbox_crs,
            "output_spatial_reference": output_crs,
            "pixel_type": ptype,
            "resampling_method": resampling,
            "content_type": content_type,
            "compress_response": compress,
        }

        if datetime is not None:
            req["time_range"] = [datetime_to_utc(parsedate(d)).isoformat() for d in datetime]

        if asset_bands:
            if isinstance(asset_bands, list):
                ab = [a if isinstance(a, AssetBands) else AssetBands(**a) for a in asset_bands]
                req["asset_bands"] = ab
            elif isinstance(asset_bands, AssetBands):
                req["asset_bands"] = [asset_bands]
            elif isinstance(asset_bands, dict):
                ab = AssetBands(**asset_bands)
                req["asset_bands"] = [ab]
            else:
                raise ValueError("asset_bands must be a list of AssetBands or a single AssetBands")

        if filter:
            req["filter"] = filter

        if pixel_size is not None:
            if isinstance(pixel_size, (list, tuple)):
                req["output_pixel_size"] = pixel_size
            elif isinstance(pixel_size, (int, float)):
                req["output_pixel_size"] = (pixel_size, pixel_size)

        if shape is not None:
            req["output_shape"] = shape

        if no_data is not None:
            req["no_data"] = no_data
        if input_nodata is not None:
            warnings.warn(
                "input_nodata is deprecated and will be removed in 1.0. Use nodata instead"
            )
            req["no_data"] = input_nodata
        if output_nodata is not None:
            warnings.warn("output_nodata is deprecated. This parameter will have not effect")

        if compress:
            boson_client.add_request_headers({"Accept-Encoding": "deflate, gzip"})

        # TODO: use hash when we ensure all datasets have one.
        url = f"{self._root_url('raster')}/pixels"
        res = raise_on_error(boson_client.post(url, **req))

        raw_bytes = res.content

        if content_type == "raw":
            h = res.headers
            bands = int(h["X-Image-Bands"])
            rows = int(h["X-Image-Rows"])
            cols = int(h["X-Image-Columns"])

            x = np.frombuffer(raw_bytes, dtype=pixel_dtype)
            return x.reshape((bands, rows, cols))
        return raw_bytes

    warp = deprecated("1.0.0", "Dataset.warp")(get_pixels)

    def dataset_info(self) -> DatasetInfo:
        """returns information about this Dataset"""
        info = DatasetInfo(
            **raise_on_error(boson_client.get(f"{self._root_url('dataset-info')}/")).json()
        )
        info.provider_config = self.boson_config
        return info

    def view(
        self,
        name: str,
        bbox: Optional[Union[List, Tuple]] = None,
        intersects: Optional[object] = None,
        datetime: Union[List, Tuple] = None,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        filter: Optional[Union[CQLFilter, dict]] = None,
        asset_bands: list = [],
        feature_limit: int = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = None,
        category: str = None,
        type: str = None,
        project: str = None,
        **kwargs,
    ) -> "Dataset":
        """creates a curated view of a ``Dataset``

        This method creates a new ``Dataset`` that is a "view" of an existing dataset. This allows the user
        to provide a set of persistent filters to a ``Dataset`` as a separate ``Object``. A view may also be
        saved in a different ``Project`` than the original. The applied filters affect both a query as
        well as the get_pixels. The final request processed will be the intersection of the view parameters
        with the query.

        Args:
            name: name of the view ``Dataset``
            bbox: The spatial extent for the query as a bounding box. Example: [-180, -90, 180, 90]
            intersects: a geometry to use in the query
            datetime: The temporal extent for the query formatted as a list: [start, end].
            collections: a list of collections to search
            ids: a list of feature/item IDs to filter to
            filter: a CQL2 filter. This is supported by most datasets but will not work for others.
            asset_bands: a list of asset/bands combinations to filter this ``Dataset`` to
            feature_limit: if specified, overrides the max_page_size of the this ``Dataset``
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            domain: domain of the resulting ``Object``
            category: category of the resulting ``Object``
            type: the type of the resulting ``Object``
            project: a new project to save this view to. If None, inherits from the parent ``Dataset``

        """
        if "extent" not in kwargs:
            kwargs["extent"] = self.extent

        collection = _stac_collection_from_kwargs(name, **kwargs)
        _remove_keys(collection, "id", "summaries", "stac_version")

        search_view = {}
        pixels_view = {}

        if bbox is not None:
            if len(bbox) != 4 and len(bbox) != 6:
                raise ValueError("bbox must be length 4 or 6")
            search_view["bbox"] = bbox
            pixels_view["bbox"] = bbox
            collection["extent"]["spatial"]["bbox"] = [bbox]

        if intersects is not None:
            # Geojson geometry OR feature
            if isinstance(intersects, dict):
                try:
                    g = shape(intersects)
                except (ValueError, AttributeError):
                    try:
                        g = shape(intersects["geometry"])
                    except Exception as e:
                        raise ValueError("could not determine type of intersection geometry") from e

            elif hasattr(intersects, "__geo_interface__"):
                g = intersects

            else:
                raise ValueError(
                    "intersection geometry must be either geojson or object with __geo_interface__"
                )

            search_view["intersects"] = g.__geo_interface__
            collection["extent"]["spatial"]["bbox"] = [g.bounds]

        if filter is not None:
            if not (isinstance(filter, dict) or isinstance(filter, dict)):
                raise ValueError("filter must be a valid CQL filter or dictionary")
            if isinstance(filter, dict):
                filter = CQLFilter(**filter)
            search_view["filter"] = filter
            pixels_view["filter"] = filter

        if datetime is not None:
            start = ".."
            end = ".."
            if len(datetime) == 1:
                start = end = _parse_date(datetime[0])
                pixels_view["datetime"] = [start]

            if len(datetime) == 2:
                start = _parse_date(datetime[0])
                end = _parse_date(datetime[1], index=1)
                pixels_view["datetime"] = [start, end]

            search_view["datetime"] = f"{start}/{end}"
            collection["extent"]["temporal"]["intervals"] = [[start, end]]

        if ids is not None:
            # unmarshaled using the STAC JSON marshaler, so it's "ids" not "feature_ids"
            search_view["ids"] = ids
            pixels_view["image_ids"] = ids
        if collections is not None:
            search_view["collections"] = collections
        if asset_bands is not None and len(asset_bands) > 0:
            pixels_view["asset_bands"] = asset_bands

        boson_cfg = BosonConfig(
            provider_name="view",
            properties={
                "provider": {
                    "dataset_name": self.name,
                    "project": self.project.uid,
                    "provider_config": self.boson_config,
                },
                "search_view": search_view,
                "pixels_view": pixels_view,
            },
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )
        if feature_limit is not None:
            boson_cfg.max_page_size = feature_limit

        if domain is None:
            domain = self.domain
        if category is None:
            category = self.category
        if type is None:
            type = self.type
        if project is None:
            project = self.project

        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=self.data_api,
            item_type=self.item_type,
            boson_cfg=boson_cfg,
            domain=domain,
            category=category,
            type=type,
            project=project,
            **collection,
        )

    def union(
        self,
        name: str,
        others: List["Dataset"] = [],
        feature_limit: int = 1000,
        project: Optional[Union[Project, str]] = None,
        ignore_duplicate_fields: bool = False,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a union of this dataset with a list of others

        Creates a new ``Dataset`` that is the ``union`` of this ``Dataset`` with a list of ``others``.
        If ``others`` is an empty list, this creates a union of a dataset with itself, which is essentially
        a virtual copy of the original endowed with any capabilities Boson adds.

        See: :py:func:`geodesic.entanglement.dataset.new_union_dataset`

        Args:
            name: the name of the new ``Dataset``
            others: a list of ``Datasets`` to ``union``
            feature_limit: the max size of a results page from a query/search
            project: the name of the project this will be assigned to
            ignore_duplicate_fields: if True, duplicate fields across providers will be ignored
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """

        return new_union_dataset(
            name=name,
            datasets=[self] + others,
            feature_limit=feature_limit,
            project=project,
            ignore_duplicate_fields=ignore_duplicate_fields,
            domain=domain,
            category=category,
            type=type,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
            **kwargs,
        )

    def join(
        self,
        name: str,
        key: str,
        right_dataset: "Dataset",
        right_key: str,
        drop_duplicates: bool = False,
        drop_fields: List[str] = [],
        right_drop_fields: List[str] = [],
        suffix: str = "_left",
        right_suffix: str = "_right",
        use_geometry: str = "left",
        feature_limit: int = 1000,
        project: Optional[Union[Project, str]] = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a left join of this dataset with another dataset

        See: :py:func:`geodesic.entanglement.dataset.new_join_dataset`

        Args:
            name: the name of the new ``Dataset``
            key: the name of the field in this dataset to join on. This key must exist for there to be output.
                An error will be thrown if the key does not exist for 50% of the features in a query.
            right_dataset: the dataset to join with
            right_key: the name of the field in the right dataset to join on.
            drop_fields: a list of fields to drop from this dataset
            right_drop_fields: a list of fields to drop from the right dataset
            suffix: the suffix to append to fields from this dataset
            right_suffix: the suffix to append to fields from the right dataset
            use_geometry: which geometry to use in the join. "left" will use the left dataset's geometry, "right" will use the right dataset's geometry
            drop_duplicates: if True, duplicate fields across providers will be ignored
            feature_limit: the max size of a results page from a query/search
            project: the name of the project this will be assigned to
            ignore_duplicate_fields: if True, duplicate fields across providers will be ignored
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """

        return new_join_dataset(
            name=name,
            left_dataset=self,
            left_field=key,
            right_dataset=right_dataset,
            right_field=right_key,
            drop_duplicates=drop_duplicates,
            left_drop_fields=drop_fields,
            right_drop_fields=right_drop_fields,
            right_suffix=right_suffix,
            left_suffix=suffix,
            use_geometry=use_geometry,
            feature_limit=feature_limit,
            project=project,
            domain=domain,
            category=category,
            type=type,
            middleware=middleware,
            tile_options=tile_options,
            cache=cache,
            **kwargs,
        )

    def share(self, servicer: str, ttl: Union[pydatetime.timedelta, int, float] = None) -> Token:
        """
        Shares a dataset, producing a token that will allow unauthenticated users to run a proxied boson request

        Args:
            servicer: The name of the servicer to use in the boson request.
            ttl: The time in until the dataset's token should expire. Either a timedelta object or seconds
                 Defaults to -1 (no expiration) if not provided.

        Raises:
            requests.HTTPError: If the user is not permitted to access the dataset or if an error occurred

        Returns:
            a share token created by Ted and its corresponding data
        """
        name = self.name
        project = self.project.uid

        if isinstance(ttl, pydatetime.timedelta):
            ttl = int(ttl.total_seconds())

        if ttl is None:
            ttl = -1
        else:
            if isinstance(ttl, int):
                ttl = ttl
            else:
                raise ValueError("ttl must be an integer")

        params = {}
        params["dataset"] = name
        params["servicer"] = servicer
        params["project"] = project
        params["ttl"] = ttl

        res = raise_on_error(ted_client.post("", **params))
        return Token(**res.json())

    def share_as_arcgis_service(self, ttl: Union[pydatetime.timedelta, int, float] = None) -> Token:
        """Share a dataset as a GeoServices/ArcGIS service

        Args:
            ttl: The time in until the dataset's token should expire. Either a timedelta object or seconds
                 Defaults to -1 (no expiration) if not provided.

        Raises:
            requests.HTTPError: If the user is not permitted to access the dataset or if an error occurred

        Returns:
            a share token created by Ted and its corresponding data
        """

        return self.share(servicer="geoservices", ttl=ttl)

    def share_as_ogc_tiles_service(
        self, ttl: Union[pydatetime.timedelta, int, float] = None
    ) -> Token:
        """Share a dataset as a OGC Tiles service

        Args:
            ttl: The time in until the dataset's token should expire. Either a timedelta object or seconds
                 Defaults to -1 (no expiration) if not provided.

        Raises:
            requests.HTTPError: If the user is not permitted to access the dataset or if an error occurred

        Returns:
            a share token created by Ted and its corresponding data
        """

        return self.share(servicer="tiles", ttl=ttl)

    def command(self, command: str, **kwargs) -> dict:
        """issue a command to this dataset's provider

        Commands can be used to perform operations on a dataset such as reindexing. Most commands
        run in the background and will return immediately. If a command is successfully submitted,
        this should return a message `{"success": True}`, otherwise it will raise an exception with
        the error message.

        Args:
            command: the name of the command to issue. Providers supporting "reindex" will accept this command.
            **kwargs: additional arguments passed to this command.

        """
        return raise_on_error(
            boson_client.post(f"{self._root_url('command')}/{command}", **kwargs)
        ).json()

    def reindex(self, timeout: Union[pydatetime.timedelta, str] = None) -> dict:
        """issue a `reindex` command to this dataset's provider

        Reindexes a dataset. This will reindex the dataset in the background, and will return
        immediately. If the kicking off reindexing is successful, this will return a message
        `{"success": True}`, otherwise it will raise an exception with the error message.

        Args:
            timeout: the maximum time to wait for the reindexing to complete. If None, will use the
                      default timeout of 30 minutes.
        """
        if timeout is None:
            return self.command("reindex")

        class args(_APIObject):
            timeout = _TimeDeltaDescr()

        x = args(timeout=timeout)
        return self.command("reindex", **x)

    def clear_store(self, prefix: str = None) -> dict:
        """clears the persistent store for this dataset

        Some data, such as cached files, indices, and tiles remain in the store.
        Boson isn't always able to recognize when data is stale. This can be called to
        clear out the persistent store for this dataset.

        Args:
            prefix: if specified, only keys with this prefix will be cleared
        """
        kwargs = {}
        if prefix is not None:
            kwargs["prefix"] = prefix
        return self.command("clear-store", **kwargs)

    def clear_tile_cache(self, cache_prefix: str = "default") -> dict:
        """clears the tile cache for this dataset

        Args:
            cache_prefix: if specified, only specified cache will be cleared. "default" is most common
                and refers the the tiles with no additional filtering applied. Beneath this key is the
                Tile Matrix Set used, so by default, all tiles for all tile matrix sets will be cleared
        """
        return self.clear_store(prefix=cache_prefix)

    @staticmethod
    def from_snowflake_table(
        name: str,
        account: str,
        database: str,
        table: str,
        credential: str,
        schema: str = "public",
        warehouse: str = None,
        id_column: str = None,
        geometry_column: str = None,
        datetime_column: str = None,
        feature_limit: int = 8000,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs: dict,
    ) -> "Dataset":
        """create a ``Dataset`` from a Snowflake table.

        This method creates a new ``Dataset`` from an existing Snowflake table.

        Args:
            name: name of the ``Dataset``
            account: Snowflake account string, formatted as ``<orgname>-<account_name>``. Ref url: https://docs.snowflake.com/en/user-guide/admin-account-identifier#using-an-account-name-as-an-identifier
            database: Snowflake database that contains the table
            table: name of the Snowflake table
            credential: name of a credential to access table. Either basic auth or oauth2 refresh token are supported
            schema: Snowflake schema the table resides in
            warehouse: name of the Snowflake warehouse to use
            id_column: name of the column containing a unique identifier. Integer IDs preferred, but not required
            geometry_column: name of the column containing the primary geometry for spatial filtering.
            datetime_column: name of the column containing the primary datetime field for temporal filtering.
            feature_limit: max number of results to return in a single page from a search
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """
        collection = _stac_collection_from_kwargs(name, **kwargs)
        _remove_keys(collection, "id", "summaries", "stac_version")

        properties = dict(
            account=account,
            database=database,
            table=table,
            schema=schema,
        )
        if warehouse is not None:
            properties["warehouse"] = warehouse
        if id_column is not None:
            properties["id_column"] = id_column
        if geometry_column is not None:
            properties["geometry_column"] = geometry_column
        if datetime_column is not None:
            properties["datetime_column"] = datetime_column

        boson_cfg = BosonConfig(
            provider_name="snowflake",
            max_page_size=feature_limit,
            properties=properties,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api="features",
            item_type="other",
            boson_cfg=boson_cfg,
            credentials={
                DEFAULT_CREDENTIAL_KEY: credential,
            },
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    @staticmethod
    def from_arcgis_item(
        name: str,
        item_id: str,
        arcgis_instance: str = "https://www.arcgis.com",
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a new Dataset from an ArcGIS Online/Enterprise item

        Args:
            name: name of the Dataset to create
            item_id: the item ID of the ArcGIS Item Referenced
            arcgis_instance: the base url of the ArcGIS Online or Enterprise root. Defaults to AGOL, MUST be specified
                             for ArcGIS Enterprise instances
            credential: the name or uid of a credential required to access this. Currently, this must be the
                        client credentials of an ArcGIS OAuth2 Application. Public layers do not require credentials.
            layer_id: an integer layer ID to subset a service's set of layers.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset

        Returns:
            a new `Dataset`

        Examples:
            >>> ds = Dataset.from_arcgis_item(
            ...          name="my-dataset",
            ...          item_id="abc123efghj34234kxlk234joi",
            ...          credential="my-arcgis-creds"
            ... )
            >>> ds.save()
        """

        if arcgis_instance.endswith("/"):
            arcgis_instance = arcgis_instance[:-1]
        url = f"{arcgis_instance}/sharing/rest/content/items/{item_id}"

        boson_cfg = BosonConfig(
            provider_name="geoservices",
            url=url,
            thread_safe=True,
            pass_headers=["X-Esri-Authorization"],
            properties={},
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        dataset = boson_dataset(
            name=name,
            boson_cfg=boson_cfg,
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

        return dataset

    @staticmethod
    def from_arcgis_layer(
        name: str,
        url: str,
        arcgis_instance: str = "https://www.arcgis.com",
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a new Dataset from an ArcGIS Online/Enterprise Service URL

        Args:
            name: name of the Dataset to create
            url: the URL of the Feature, Image, or Map Server. This is the layer url, not the Service url.
                 Only the specified layer will be available to the dataset
            arcgis_instance: the base url of the ArcGIS Online or Enterprise root. Defaults to AGOL, MUST be specified
                             for ArcGIS Enterprise instances
            credential: the name or uid of a credential required to access this. Currently, this must be the
                        client credentials of an ArcGIS OAuth2 Application. Public layers do not require credentials.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_arcgis_layer(
            ...          name="my-dataset",
            ...          url="https://services9.arcgis.com/ABC/arcgis/rest/services/SomeLayer/FeatureServer/0",
            ...          credential="my-arcgis-creds"
            ... )
            >>> ds.save()
        """

        if url.endswith("/"):
            url = url[:-1]

        layer_id = url.split("/")[-1]
        try:
            layer_id = int(layer_id)
        except ValueError:
            raise ValueError(
                "invalid url, must be of the form https://<host>/.../LayerName/FeatureServer/<layer_id>"
                f"got {url}"
            )

        url = "/".join(url.split("/")[:-1])
        return Dataset.from_arcgis_service(
            name=name,
            url=url,
            arcgis_instance=arcgis_instance,
            credential=credential,
            layer_id=layer_id,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

    @staticmethod
    def from_arcgis_service(
        name: str,
        url: str,
        arcgis_instance: str = "https://www.arcgis.com",
        credential: str = None,
        layer_id: int = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a new Dataset from an ArcGIS Online/Enterprise Service URL

        Args:
            name: name of the Dataset to create
            url: the URL of the Feature, Image, or Map Server. This is not the layer url, but the Service url.
                 Layers will be enumerated and all accessible from this dataset.
            arcgis_instance: the base url of the ArcGIS Online or Enterprise root. Defaults to AGOL, MUST be specified
                             for ArcGIS Enterprise instances
            credential: the name or uid of a credential required to access this. Currently, this must be the
                        client credentials of an ArcGIS OAuth2 Application. Public layers do not require credentials.
            layer_id: an integer layer ID to subset a service's set of layers.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            gis: the logged in `arcgis.gis.GIS` to use to access the metadata for this item. To access secure content,
                 if this is not specified, the active GIS is used.

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_arcgis_service(
            ...          name="my-dataset",
            ...          url="https://services9.arcgis.com/ABC/arcgis/rest/services/SomeLayer/FeatureServer",
            ...          credential="my-arcgis-creds"
            ... )
            >>> ds.save()
        """

        if url.endswith("/"):
            url = url[:-1]
        if not url.endswith("Server"):
            raise ValueError("url must end with ImageServer, FeatureServer, or MapServer")

        if layer_id is not None:
            url += f"/{layer_id}"

        if "ImageServer" in url:
            data_api = "stac"
            item_type = "raster"
        elif "FeatureServer" in url:
            data_api = "features"
            item_type = "other"
        elif "MapServer" in url:
            data_api = "features"
            item_type = "other"
        else:
            raise ValueError("unsupported service type")

        boson_cfg = BosonConfig(
            provider_name="geoservices",
            url=url,
            thread_safe=True,
            pass_headers=["X-Esri-Authorization"],
            properties={},
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        dataset = boson_dataset(
            name=name,
            keywords=[],
            data_api=data_api,
            item_type=item_type,
            boson_cfg=boson_cfg,
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

        return dataset

    @staticmethod
    def from_stac_collection(
        name: str,
        url: str,
        credential=None,
        item_type: str = "raster",
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Create a new Dataset from a STAC Collection

        Args:
            name: name of the Dataset to create
            url: the url to the collection (either STAC API or OGC API: Features)
            credential: name or uid of the credential to access the API
            item_type: what type of items does this contain? "raster" for raster data, "features" for features, other
                       types, such as point_cloud may be specified, but doesn't alter current internal functionality.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_stac_collection(
            ...          name="landsat-c2l2alb-sr-usgs",
            ...          url="https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2alb-sr"
            ... )
            >>> ds.save()
        """

        if url.endswith("/"):
            url = url[:-1]

        if "collections" not in url:
            raise ValueError("url must be of the form {STAC_ROOT}/collections/:collectionId")

        rs = stac_root_re.match(url)

        try:
            root = rs.group(1)
        except Exception:
            raise ValueError("invalid URL")

        res = get_client().get(url)

        try:
            stac_collection = res.json()
        except Exception:
            raise ValueError("unable to get service metadata. (did you enter the correct url?)")

        stac_extent = stac_collection.get("extent", {})
        spatial_extent = stac_extent.get("spatial", {})
        bbox = spatial_extent.get("bbox", [[-180.0, -90.0, 180.0, 90.0]])
        temporal_extent = stac_extent.get("temporal", {})
        interval = temporal_extent.get("interval", [[None, None]])

        extent = {
            "spatial": {"bbox": bbox},
            "temporal": {"interval": interval},
        }

        if interval[0][1] is None:
            interval[0][1] = pydatetime.datetime(2040, 1, 1).strftime("%Y-%m-%dT%H:%M:%SZ")

        item_assets = stac_collection.get("item_assets", {})

        links = stac_collection.get("links", [])
        extensions = stac_collection.get("stac_extensions", [])
        providers = stac_collection.get("providers", [])

        keywords = stac_collection.get("keywords", [])
        keywords += ["boson"]

        boson_cfg = BosonConfig(
            provider_name="stac",
            url=root,
            thread_safe=True,
            pass_headers=[],
            properties={"collection": stac_collection["id"]},
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        data_api = "stac"

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        dataset = boson_dataset(
            name=name,
            alias=stac_collection.get("title", name),
            description=stac_collection.get("description", ""),
            keywords=keywords,
            license=stac_collection.get("license", ""),
            data_api=data_api,
            item_type=item_type,
            extent=extent,
            boson_cfg=boson_cfg,
            providers=providers,
            links=links,
            item_assets=item_assets,
            stac_extensions=extensions,
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

        return dataset

    @staticmethod
    def from_bucket(
        name: str,
        url: str,
        pattern: str = None,
        region: str = None,
        datetime_field: str = None,
        start_datetime_field: str = None,
        end_datetime_field: str = None,
        oriented: bool = False,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Creates a new Dataset from a Cloud Storage Bucket (S3/GCP/Azure)

        Args:
            name: name of the Dataset to create
            url: the url to the bucket, including the prefix (ex. s3://my-bucket/myprefix, gs://my-bucket/myprefix, ...)
            pattern: a regex to filter for files to index
            region: for S3 buckets, the region where the bucket is
            datetime_field: the name of the metadata key on the file to find a timestamp
            start_datetime_field: the name of the metadata key on the file to find a start timestamp
            end_datetime_field: the name of the metadata key on the file to find an end timestamp
            oriented: Is this oriented imagery? If so, EXIF data will be parsed for geolocation. Anything missing
                      location info will be dropped.
            credential: the name or uid of the credential to access the bucket.
            middleware: configure any boson middleware to be applied to the new dataset.
            kwargs: other metadata that will be set on the Dataset, such as description, alias, etc

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_bucket(
            ...          name="bucket-dataset",
            ...          url="s3://my-bucket/myprefix",
            ...          pattern=r".*\\.tif",
            ...          region="us-west-2",
            ...          datetime_field="TIFFTAG_DATETIME",
            ...          oriented=False,
            ...          credential="my-iam-user",
            ...          description="my dataset is the bomb"
            ...)
            >>> ds.save()

        """

        info = {
            "name": name,
            "alias": kwargs.get("alias", name),
            "description": kwargs.get("description", ""),
            "keywords": kwargs.get("keywords", []),
            "license": kwargs.get("license", "unknown"),
            "data_api": kwargs.get("data_api", "stac"),
            "item_type": kwargs.get("item_type", "raster"),
            "extent": kwargs.get(
                "extent",
                {
                    "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                    "temporal": {"interval": [[None, None]]},
                },
            ),
            "providers": kwargs.get("providers", []),
            "item_assets": kwargs.get("item_assets", {}),
            "links": kwargs.get("links", []),
            "stac_extensions": kwargs.get("stac_extensions", ["item_assets"]),
        }
        if credential is not None:
            info["credentials"] = {STORAGE_CREDENTIAL_KEY: credential}

        if pattern is not None:
            try:
                re.compile(pattern)
            except Exception:
                raise ValueError(f"invalid pattern '{pattern}'")

        properties = {"alias": info["alias"], "description": info["description"]}
        if pattern is not None:
            properties["pattern"] = pattern
        if datetime_field is not None:
            properties["datetime_field"] = datetime_field
        if start_datetime_field is not None:
            properties["start_datetime_field"] = start_datetime_field
        if end_datetime_field is not None:
            properties["end_datetime_field"] = end_datetime_field
        if region is not None:
            properties["region"] = region

        boson_cfg = BosonConfig(
            provider_name="bucket",
            url=url,
            properties=properties,
            thread_safe=True,
            max_page_size=500,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        return boson_dataset(
            boson_cfg=boson_cfg, domain=domain, category=category, type=type, **info
        )

    @staticmethod
    def from_google_earth_engine(
        name: str,
        asset: str,
        credential: str,
        folder: str = "projects/earthengine-public/assets",
        url: str = "https://earthengine-highvolume.googleapis.com",
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Creates a new Dataset from a Google Earth Engine Asset

        Args:
            name: name of the Dataset to create
            asset: the asset in GEE to use (ex. 'LANDSAT/LC09/C02/T1_L2')
            credential: the credential to access this, a Google Earth Engine GCP Service Account. Future will allow
                        the use of a oauth2 refresh token or other.
            folder: by default this is the earth engine public, but you can specify another folder if needed to point
                    to legacy data or personal projects.
            url: the GEE url to use, defaults to the recommended high volume endpoint.
            kwargs: other metadata that will be set on the Dataset, such as description, alias, etc
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset

        Returns:
            a new `Dataset`.

        Examples:
            >>> ds = Dataset.from_google_earth_engine(
            ...          name="landsat-9-c2-gee",
            ...          asset="s3://my-bucket/myprefixLANDSAT/LC09/C02/T1_L2",
            ...          credential="google-earth-engine-svc-account",
            ...          description="my dataset is the bomb"
            ...)
            >>> ds.save()

        """
        info = {
            "name": name,
            "alias": kwargs.get("alias", ""),
            "description": kwargs.get("description", ""),
            "keywords": kwargs.get("keywords", []),
            "stac_extensions": kwargs.get("stac_extensions", ["item_assets"]),
            "credentials": {DEFAULT_CREDENTIAL_KEY: credential},
        }

        boson_cfg = BosonConfig(
            provider_name="google-earth-engine",
            url=url,
            thread_safe=True,
            max_page_size=500,
            properties={"asset": asset, "folder": folder},
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
        )

        return boson_dataset(
            boson_cfg=boson_cfg, domain=domain, category=category, type=type, **info
        )

    @staticmethod
    def from_elasticsearch_index(
        name: str,
        url: str,
        index_pattern: str,
        credential: str = None,
        storage_credential: str = None,
        datetime_field: str = "properties.datetime",
        geometry_field: str = "geometry",
        geometry_type: str = "geo_shape",
        id_field: str = "_id",
        data_api: str = "features",
        item_type: str = "other",
        feature_limit: int = 2000,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """create a new Dataset from an elasticsearch index containing geojson features or STAC items

        Args:
            name: name of the Dataset to create
            url: the DNS name or IP of the elasticsearch host to connect to.
            index_pattern: an elasticsearch index name or index pattern
            credential: name of the Credential object to use. Currently, this only supports basic auth
                (username/password).
            storage_credential: the name of the Credential object to use for storage if any of the data
                referenced in the index requires a credential to access (e.g. cloud storage for STAC)
            datetime_field: the field that is used to search by datetime in the elasticserach index.
            geometry_field: the name of the field that contains the geometry
            geometry_type: the type of the geometry field, either geo_shape or geo_point
            id_field: the name of the field to use as an ID field
            data_api: the data API, either 'stac' or 'features'
            item_type: the type of item. If it's a stac data_api, then it should describe what the data is
            feature_limit: the max number of features the service will return per page.
            middleware: configure any boson middleware to be applied to the new dataset.
            **kwargs: other arguments that will be used to create the collection and provider config.

        Returns:
            A new Dataset. Must call .save() for it to be usable.
        """

        collection = _stac_collection_from_kwargs(name, **kwargs)
        elastic_config = dict(
            disable_retry=kwargs.get("retries", False),
            enable_debug_logger=kwargs.get("enable_debug_logger", False),
            enable_compatibility_mode=kwargs.get("enable_compatibility_mode", False),
            insecure=kwargs.get("insecure", True),
            max_retries=kwargs.get("max_retries", 5),
            feature_limit=feature_limit,
            date_field=datetime_field,
            index_pattern=index_pattern,
            geometry_field=geometry_field,
            geometry_type=geometry_type,
            id_field=id_field,
            collection=dict(**collection),
        )
        elastic_config.update(kwargs)

        credentials = {}
        if credential is not None:
            credentials[DEFAULT_CREDENTIAL_KEY] = credential
        if storage_credential is not None:
            credentials[STORAGE_CREDENTIAL_KEY] = storage_credential

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=data_api,
            item_type=item_type,
            boson_cfg=BosonConfig(
                provider_name="elastic",
                url=url,
                max_page_size=feature_limit,
                properties=elastic_config,
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    @staticmethod
    def from_csv(
        name: str,
        url: str,
        index_data: bool = True,
        crs: str = "EPSG:4326",
        x_field: str = "CoordX",
        y_field: str = "CoordY",
        z_field: str = "CoordZ",
        geom_field: str = "WKT",
        datetime_field: str = None,
        feature_limit: int = 1000,
        region: str = None,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """create a new Dataset from a CSV file in cloud storage

        Args:
            name: name of the Dataset to create
            url: the URL/URI of the data. Can be a cloud storage URI such as s3://<bucket>/key, gs://
            index_data: if true, the data will be copied and spatially indexed for more efficient queries
            crs: a string coordinate reference for the data
            (x/y/z)_field: the field name for the x/y/z fields
            geom_field: the field name containing the geometry in well known text (WKT) or hex encoded well known binary
                (WKB).
            feature_limit: the max number of features this will return per page
            datetime_field: if the data is time enabled, this is the name of the datetime field. The datetime
                must be RFC3339 formatted.
            region: for S3 buckets, the region where the bucket is
            credential: the name of the credential object needed to access this data.
            middleware: configure any boson middleware to be applied to the new dataset.

        """

        csv = dict(x_field=x_field, y_field=y_field, z_field=z_field, geom_field=geom_field)

        return Dataset.from_tabular_data(
            name,
            url,
            index_data=index_data,
            crs=crs,
            feature_limit=feature_limit,
            datetime_field=datetime_field,
            region=region,
            credential=credential,
            csv=csv,
            middleware=middleware,
            cache=cache,
            tile_options=tile_options,
            domain=domain,
            category=category,
            type=type,
            **kwargs,
        )

    @staticmethod
    def from_tabular_data(
        name: str,
        url: str,
        index_data: bool = True,
        crs: str = "EPSG:4326",
        feature_limit: int = 1000,
        datetime_field: str = None,
        region: str = None,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """create a new Dataset from a vector file in cloud storage.

        This can be a Shapefile, GeoJSON Feature Collection, FlatGeobuf, and several others

        Args:
            name: name of the Dataset to create
            url: the URL/URI of the data. Can be a cloud storage URI such as s3://<bucket>/key, gs://
            index_data: if true, the data will be copied and spatially indexed for more efficient queries
            crs: a string coordinate reference for the data
            feature_limit: the max number of features this will return per page
            datetime_field: if the data is time enabled, this is the name of the datetime field. The datetime
                field must RFC3339 formatted.
            region: for S3 buckets, the region where the bucket is
            credential: the name of the credential object needed to access this data.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
        """

        collection = _stac_collection_from_kwargs(name, **kwargs)

        credentials = {}
        if credential is not None:
            credentials = {STORAGE_CREDENTIAL_KEY: credential}

        properties = dict(index_data=index_data, crs=crs, region=region)
        csv = kwargs.pop("csv", None)
        if csv is not None:
            properties["csv"] = csv
        if region is not None:
            properties["region"] = region
        if datetime_field is not None:
            properties["datetime_field"] = datetime_field

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api="features",
            item_type="other",
            boson_cfg=BosonConfig(
                provider_name="tabular",
                url=url,
                max_page_size=feature_limit,
                properties=properties,
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            domain=domain,
            category=category,
            type=type,
            credentials=credentials,
            **collection,
        )

    @staticmethod
    def from_geoparquet(
        name: str,
        url: str,
        feature_limit: int = 1000,
        datetime_field: str = "datetime",
        return_geometry_properties: bool = False,
        expose_partitions_as_layer: bool = True,
        update_existing_index: bool = True,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """creates a dataset from Hive-partitioned GeoParquet files in cloud storage

        Hive-partition GeoParquet is a particular convention typically used when writing data out
        from a parallel process (such as Tesseract or Apache Spark) or when the individual file
        sizes or row counts are too large. This provider indexes these partitions spatially to
        optimize query performance. Hive partitioned parquet is organized like this and we require
        this structure:

        prefix/<root>.parquet
            /key=value_1/<partition-00001>.parquet
            /key=value_2/<partition-00002>.parquet
            /...
            /key=value_m/<partition-n>.parquet

        "root" and "partition-xxxxx" can be whatever provided they both have the parquet suffix.
        Any number oof key/value pairs are allowed in Hive Partitioned data. This can also point
        to a single parquet file.

        Args:
            name: name of the Dataset to create
            url: the path to the <root>.parquet. Format depends on the storage backend.
            feature_limit: the max number of features that this provider will allow returned by a
                single query.
            datetime_field: if the data is time enabled, this is the name of the datetime field. This is the
                name of a column in the parquet dataset that will be used for time filtering. Must be RFC3339
                formatted in order to work.
            return_geometry_properties: if True, will compute and return geometry properties along with
                the features.
            expose_partitions_as_layer: this will create a collection/layer in this Dataset that simply
                has the partition bounding box and count of features within. Can be used as a simple heatmap
            update_existing_index: if the data has been indexed in our scheme by a separate process, set to False
                to use that instead, otherwise this will index the parquet data in the bucket before you
                are able to query it.
            credential: the name of the credential to access the data in cloud storage.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            **kwargs: additional arguments that will be used to create the STAC collection, Dataset description
                Alias, etc.

        """
        if not url.endswith(".parquet"):
            raise ValueError('url must end with ".parquet"')

        collection = _stac_collection_from_kwargs(name, **kwargs)

        credentials = {}
        if credential is not None:
            credentials = {STORAGE_CREDENTIAL_KEY: credential}

        data_api = "features"
        item_type = "other"

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=data_api,
            item_type=item_type,
            boson_cfg=BosonConfig(
                provider_name="geoparquet",
                url=url,
                max_page_size=feature_limit,
                properties={
                    "datetime_field": datetime_field,
                    "expose_partitions_as_layer": expose_partitions_as_layer,
                    "update_existing_index": update_existing_index,
                    "return_geometry_properties": return_geometry_properties,
                },
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    @staticmethod
    def from_remote_provider(
        name: str,
        url: str,
        data_api: str = "features",
        transport_protocol: str = "http",
        additional_properties: dict = {},
        feature_limit: int = 2000,
        credential: str = None,
        middleware: MiddlewareConfig = {},
        cache: CacheConfig = {},
        tile_options: TileOptions = {},
        domain: str = "*",
        category: str = "*",
        type: str = "*",
        **kwargs,
    ) -> "Dataset":
        """Creates a dataset from a server implementing the Boson remote provider interface

        The Boson Remote Provider interface may be implemented using the
        Boson Python SDK (https://pypi.org/project/boson-sdk/). The provider must
        be hosted somewhere and this connects Boson to a remote provider.

        Remote Providers may either implement the Search or the Pixels endpoint (or both).

        Args:
            name: name of the Dataset to create
            url: URL of the server implementing the interface
            data_api: either 'features' or 'raster'.
            transport_protocol: either 'http' or 'grpc'
            additional_properties: additional properties to set on the dataset
            feature_limit: the max number of features that this provider will allow returned
                in a single page.
            credential: the name of the credential to access the api.
            middleware: configure any boson middleware to be applied to the new dataset.
            cache: configure caching for this dataset
            tile_options: configure tile options for this dataset
            **kwargs: additional arguments that will be used to create the STAC collection, Dataset description
                Alias, etc.
        """

        collection = _stac_collection_from_kwargs(name, **kwargs)

        credentials = {}
        if credential is not None:
            credentials = {DEFAULT_CREDENTIAL_KEY: credential}

        data_api = "features"
        item_type = "other"

        properties = {}
        properties.update(additional_properties)
        properties["protocol"] = transport_protocol

        _remove_keys(collection, "id", "summaries", "stac_version")
        return boson_dataset(
            name=name,
            alias=collection.pop("title"),
            data_api=data_api,
            item_type=item_type,
            boson_cfg=BosonConfig(
                provider_name="remote",
                url=url,
                max_page_size=feature_limit,
                properties=properties,
                middleware=middleware,
                cache=cache,
                tile_options=tile_options,
            ),
            credentials=credentials,
            domain=domain,
            category=category,
            type=type,
            **collection,
        )

    def __str__(self) -> str:
        prefix = super().__str__()
        prefix += "  Provider Info:\n"
        prefix += f"    name: {self.boson_config.provider_name}\n"
        prefix += f"    url: {self.boson_config.url}\n"
        prefix += "    properties:\n"
        for key, value in self.boson_config.properties.items():
            prefix += f"      {key}: {value}\n"
        return prefix


def boson_dataset(
    *,
    name: str,
    alias: str = "",
    description: str = "",
    keywords: List[str] = [],
    extent: dict = None,
    boson_cfg: "BosonConfig",
    license: str = "",
    data_api: str = "",
    item_type: str = "",
    providers: list = [],
    item_assets: dict = {},
    links: list = [],
    stac_extensions: list = [],
    credentials={},
    domain: str = "*",
    category: str = "*",
    type: str = "*",
    project: Project = None,
) -> Dataset:
    if not boson_cfg.credentials:
        boson_cfg.credentials = credentials

    if project is None:
        project = get_active_project().uid
    elif isinstance(project, str):
        project = get_project(project).uid
    else:
        project = project.uid

    qualifiers = {
        "name": name,
        "domain": domain,
        "category": category,
        "type": type,
    }

    # Update credentials
    if isinstance(credentials, dict):
        for key, value in credentials.items():
            try:
                cred = get_credential(value)
            except Exception:
                raise ValueError(f"no such credential '{value}'")
            boson_cfg.credentials[key] = cred.uid

    dataset = Dataset(
        name=name,
        alias=alias,
        description=description,
        keywords=keywords,
        license=license,
        data_api=data_api,
        item_type=item_type,
        extent=extent,
        boson_config=boson_cfg,
        providers=providers,
        item_assets=item_assets,
        links=links,
        stac_extensions=stac_extensions,
        services=["boson"],
        object_class="dataset",
        qualifiers=qualifiers,
        project=project,
    )

    return dataset


def _stac_collection_from_kwargs(name: str, **kwargs) -> dict:
    return dict(
        id=name,
        title=kwargs.get("alias", name),
        description=kwargs.get("description", ""),
        keywords=kwargs.get("keywords", []),
        license=kwargs.get("license", ""),
        extent=kwargs.get(
            "extent",
            {
                "spatial": {"bbox": [[-180.0, -90.0, 180.0, 90.0]]},
                "temporal": {"interval": [[None, None]]},
            },
        ),
        providers=kwargs.get("providers", []),
        item_assets=kwargs.get("item_assets", {}),
        links=kwargs.get("links", []),
        stac_extensions=kwargs.get("stac_extensions", []),
        summaries=kwargs.get("summaries", {}),
        stac_version="1.0.0",
    )


def _remove_keys(d: dict, *keys) -> None:
    for key in keys:
        d.pop(key)


def parsedate(dt):
    try:
        return parse(dt)
    except TypeError:
        return dt


class _DatasetDescr(_BaseDescr):
    """A geodesic Dataset descriptor

    Returns a Dataset object, sets the Dataset name on the base object. Dataset
    MUST exist in Entanglement, in a user accessible project/graph.

    """

    def __init__(self, project=None, **kwargs):
        super().__init__(**kwargs)
        self.project = project

    def _get(self, obj: object, objtype=None) -> dict:
        # Try to get the private attribute by name (e.g. '_dataset')
        return getattr(obj, self.private_name, None)

    def _set(self, obj: object, value: object) -> None:
        dataset = self.get_dataset(value)

        # Reset the private attribute (e.g. "_dataset") to None
        setattr(obj, self.private_name, dataset)

        if self.project is not None:
            self.project.__set__(obj, dataset.project)

        self._set_object(obj, dataset.name)

    def get_dataset(self, value):
        # If the Dataset was set, we need to validate that it exists and the user has access
        dataset_name = None
        if isinstance(value, str):
            dataset_name = value
            project = get_active_project().uid
        else:
            dataset = Dataset(**value)
            dataset_name = dataset.name
            project = dataset.project.uid

        try:
            return get_dataset(dataset_name, project=project)
        except Exception:
            # Try to get from 'global'
            try:
                return get_dataset(dataset_name, project="global")
            except Exception as e:
                projects = set([project, "global"])
                raise ValueError(
                    f"dataset '{dataset_name}' does not exist in ({', '.join(projects)}) or"
                    " user doesn't have access"
                ) from e

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (Dataset, str, dict)):
            raise ValueError(f"'{self.public_name}' must be a Dataset or a string (name)")

        # If the Dataset was set, we need to validate that it exists and the user has access
        self.get_dataset(value)


class DatasetList(_APIObject):
    def __init__(self, datasets, names=[]):
        self.names = names
        if len(names) != len(datasets):
            self.names = [dataset.name for dataset in datasets]
        for dataset in datasets:
            self._set_item(dataset.name, dataset)

    def __getitem__(self, k) -> Dataset:
        if isinstance(k, str):
            return super().__getitem__(k)
        elif isinstance(k, int):
            name = self.names[k]
            return super().__getitem__(name)
        else:
            raise KeyError("invalid key")

    def __repr__(self) -> str:
        return f"DatasetList({self.names})"

    def __str__(self) -> str:
        st = "Datasets:\n"
        names = self.names
        ellipsis = False

        unique_projects = set()
        for dataset in self.values():
            unique_projects.add(dataset.project.uid)

        names_str = ", ".join(names)
        if len(names_str) > 100:
            up_to_100 = names_str[:100].split(",")
            names = [x.strip() for x in up_to_100[:-1]]
            # make sure there's at least one
            if len(names) == 0:
                names = [self.names[0]]
            ellipsis = True

        names_st = ", ".join(names)
        st += f"  Names: [{names_st}"
        if ellipsis:
            st += ", ..."
        st += "]\n"
        st += f"  Projects: [{', '.join(list(unique_projects))}]\n"
        st += "  Dataset Count: " + str(len(self.names))

        return st


def new_join_dataset(
    name: str,
    left_dataset: Dataset,
    left_field: str,
    right_dataset: Dataset,
    right_field: str,
    drop_duplicates: bool = False,
    left_drop_fields: List[str] = [],
    right_drop_fields: List[str] = [],
    left_suffix: str = "_left",
    right_suffix: str = "_right",
    use_geometry: str = "left",
    feature_limit: int = 1000,
    project: Optional[Union[Project, str]] = None,
    middleware: MiddlewareConfig = {},
    cache: CacheConfig = {},
    tile_options: TileOptions = {},
    domain: str = "*",
    category: str = "*",
    type: str = "*",
    **kwargs: dict,
) -> "Dataset":
    """Creates a left join of two feature datasets on the values of specific keys.
    Currently this is intended for smaller datasets or used in conjuction with
    the view provider to limit the scope of the join.


    Args:
        name: the name of the new ``Dataset``
        left_dataset: the left dataset to join
        left_field: the field in the left dataset to join on
        right_dataset: the right dataset to join
        right_field: the field in the right dataset to join on
        drop_duplicates: if True, fields shared between the left and right will always use the left
        left_drop_fields: fields to drop from the left dataset
        right_drop_fields: fields to drop from the right dataset
        left_suffix: the suffix to add to the left dataset fields
        right_suffix: the suffix to add to the right dataset fields
        use_geometry: which geometry to use, either 'left' or 'right'
        feature_limit: the max size of a results page from a query/search
        project: the name of the project this will be assigned to
        middleware: configure any boson middleware to be applied to the new dataset.
        cache: configure caching for this dataset
        domain: the domain of the dataset
        category: the category of the dataset
        type: the type of the dataset
    """
    collection = _stac_collection_from_kwargs(name, **kwargs)
    _remove_keys(collection, "id", "summaries", "stac_version")

    properties = dict(
        left_provider=dict(
            dataset_name=left_dataset.name,
            project=left_dataset.project.uid,
            provider_config=left_dataset.boson_config,
        ),
        right_provider=dict(
            dataset_name=right_dataset.name,
            project=right_dataset.project.uid,
            provider_config=right_dataset.boson_config,
        ),
        left_join_options=dict(
            join_on_field=left_field,
            drop_fields=left_drop_fields,
            suffix=left_suffix,
            use_geometry=use_geometry == "left",
        ),
        right_join_options=dict(
            join_on_field=right_field,
            drop_fields=right_drop_fields,
            suffix=right_suffix,
            use_geometry=use_geometry == "right",
        ),
        spatial_join=False,  # spatial joins not supported yet
        drop_duplicates=drop_duplicates,
    )

    boson_cfg = BosonConfig(
        provider_name="join",
        max_page_size=feature_limit,
        properties=properties,
        middleware=middleware,
        cache=cache,
        tile_options=tile_options,
    )

    return boson_dataset(
        name=name,
        alias=collection.pop("title"),
        data_api="stac",
        item_type="features",
        boson_cfg=boson_cfg,
        domain=domain,
        category=category,
        type=type,
        project=project,
        **collection,
    )
