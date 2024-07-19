import datetime

from typing import List, Union, Any

from dateutil.parser import parse

from geodesic.bases import _APIObject
from geodesic.utils import datetime_to_utc
from geodesic.descriptors import _ListDescr, _StringDescr, _DictDescr
from geodesic.boson.asset_bands import AssetBands

# Middleware types
SEARCH_FILTER_CQL2 = "cql2"
SEARCH_FILTER_SPATIAL = "spatial"
SEARCH_FILTER_DATETIME = "datetime"
SEARCH_TRANSFORM_RENAME_FIELDS = "rename-fields"
SEARCH_TRANSFORM_GEOMETRY = "transform-geometry"
SEARCH_TRANSFORM_COMBINE_FIELDS = "combine-fields"
SEARCH_TRANSFORM_DEFAULT_DATETIME_RANGE = "default-datetime-range"
PIXELS_TRANSFORM_COLORMAP = "colormap"
PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS = "default_asset_bands"
PIXELS_TRANSFORM_RASTERIZE = "rasterize"
PIXELS_TRANSFORM_RESCALE_SHIFT = "rescale-shift"
PIXELS_TRANSFORM_DEFAULT_DATETIME_RANGE = "default-datetime-range"


def parsedate(dt):
    try:
        return parse(dt)
    except TypeError:
        return dt


class _Middleware(_APIObject):
    _limit_setitem = ("type", "properties")
    type = _StringDescr(
        doc="type of middleware to apply to a provider",
        one_of=[
            SEARCH_FILTER_DATETIME,
            SEARCH_FILTER_CQL2,
            SEARCH_FILTER_SPATIAL,
            SEARCH_TRANSFORM_RENAME_FIELDS,
            SEARCH_TRANSFORM_COMBINE_FIELDS,
            SEARCH_TRANSFORM_GEOMETRY,
            SEARCH_TRANSFORM_DEFAULT_DATETIME_RANGE,
            PIXELS_TRANSFORM_COLORMAP,
            PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
            PIXELS_TRANSFORM_RASTERIZE,
            PIXELS_TRANSFORM_RESCALE_SHIFT,
            PIXELS_TRANSFORM_DEFAULT_DATETIME_RANGE,
        ],
    )
    properties = _DictDescr(doc="properties (if any) to configure the middleware")


class SearchFilter(_Middleware):
    @staticmethod
    def cql2_filter() -> "SearchFilter":
        """Adds CQL filtering to a provider that may not implement it natively"""
        return SearchFilter(type=SEARCH_FILTER_CQL2)

    @staticmethod
    def spatial() -> "SearchFilter":
        """Adds spatial filtering to a provider that may not implement it natively"""
        return SearchFilter(type=SEARCH_FILTER_SPATIAL)

    @staticmethod
    def datetime(field: str) -> "SearchFilter":
        """Adds datetime filtering to a provider that may not implement it natively"""
        return SearchFilter(type=SEARCH_FILTER_DATETIME, properties={"datetime_field": field})


class SearchTransform(_Middleware):
    @staticmethod
    def rename_fields(case=None, field_map={}) -> "SearchTransform":
        """rename fields in the `properties` of a search response

        Args:
            case (str, optional): case to apply to the field names. Defaults to None. One of ["upper", "lower"]
            field_map (dict, optional): mapping of old field names to new field names. Defaults to {}.

        Examples:
            >>> # Rename the field "old_field" to "new_field"
            >>> transform = SearchTransform.rename_fields(field_map={"old_field": "new_field"})

            >>> # Rename the field "old_field" to "new_field" and make it uppercase
            >>> transform = SearchTransform.rename_fields(case="upper", field_map={"old_field": "new_field"})
        """
        properties = {"field_map": field_map}
        if case is not None and case in ["upper", "lower"]:
            properties["case"] = case
        elif case is not None:
            raise ValueError(f"case must be one of ['upper', 'lower'], got {case}")

        return SearchTransform(type=SEARCH_TRANSFORM_RENAME_FIELDS, properties=properties)

    @staticmethod
    def combine_fields(
        new_field: str, fields: List[str], separator: str = "", sprintf: str = ""
    ) -> "SearchTransform":
        """combine fields in the `properties` of a search response

        Args:
            new_field (str): name of the new field to create
            fields (List[str]): fields to combine
            separator (str, optional): separator to use when combining fields. Defaults to " ".
            sprintf (str, optional): sprintf format to use when combining fields. This uses golang
            format strings to format the fields into one combined string field. For instance,
            "%d.2 %s" would print "2.00 dollars" if the field values were 2 and "dollars".
            For more information about the formatting see https://pkg.go.dev/fmt.
            All fields must have values for the sprintf to be executed. Defaults to "".

        Examples:
            >>> # Combine the fields STATE_FIPS and COUNTY_FIPS into a new field called FIPS
            >>> transform = SearchTransform.combine_fields(
            ...     new_field="FIPS",
            ...     fields=["STATE_FIPS", "COUNTY_FIPS"],
            ...     separator=""
            ... )

            >>> # Combine the fields STATE_FIPS and COUNTY_FIPS into a new field called FIPS with sprintf formatting
            >>> transform = SearchTransform.combine_fields(
            ...     new_field="FIPS",
            ...     fields=["STATE_FIPS", "COUNTY_FIPS"],
            ...     sprintf="%02d%03d"
            ... )
        """
        return SearchTransform(
            type="combine-fields",
            properties={
                "new_field": new_field,
                "fields": fields,
                "separator": separator,
                "sprintf": sprintf,
            },
        )

    @staticmethod
    def centroid() -> "SearchTransform":
        """Calculate the centroid of the queried geometry

        This middleware will calculate the centroid of the geometry and return it in a new collection
        called "centroid". In the case of multi-geometries, the centroid of the entire geometry will be
        calculated.

        When creating this middleware, most of the time you will want to apply it after
        any filtering happens, so that the centroid is calculated on the filtered geometry. This is
        done by adding it to the `search_transforms_after` list in the `MiddlewareConfig`. See the
        below example.

        Returns:
            SearchTransform: middleware to calculate the centroid of the queried geometry

        Examples:
            >>> # Add the centroid middleware to a dataset view
            >>> ds_with_centroid = ds.view(
            ...     middleware=MiddlewareConfig(
            ...         search_transforms_after=[SearchTransform.centroid()]
            ...     )
            ... )
        """
        return SearchTransform(
            type="transform-geometry",
            properties={
                "transform": "centroid",
                "parameters": {},
            },
        )

    @staticmethod
    def convex_hull() -> "SearchTransform":
        """Calculate the convex hull of the queried geometry

        This middleware will calculate the convex hull of the geometry and return it in a new collection
        called "convex_hull". The convex hull is the smallest convex polygon that encloses the geometry.
        In the case of multi-geometries, the convex hull of the entire geometry will be calculated.

        When creating this middleware, most of the time you will want to apply it after
        any filtering happens, so that the centroid is calculated on the filtered geometry. This is
        done by adding it to the `search_transforms_after` list in the `MiddlewareConfig`. See the
        below example.

        Returns:
            SearchTransform: middleware to calculate the convex hull of the queried geometry

        Examples:
            >>> # Add the convex_hull middleware to a dataset view
            >>> ds_with_convex_hull = ds.view(
            ...     middleware=MiddlewareConfig(
            ...         search_transforms_after=[SearchTransform.convex_hull()]
            ...     )
            ... )
        """
        return SearchTransform(
            type="transform-geometry",
            properties={
                "transform": "convex_hull",
                "parameters": {},
            },
        )

    @staticmethod
    def bounds() -> "SearchTransform":
        """Calculate the bounds of the queried geometry

        This middleware will calculate the bounds of the geometry and return it in a new collection
        called "bounds". The bounds in this case are a rectangle that encloses the geometry.
        In the case of multi-geometries, the bounds of the entire geometry will be calculated.

        When creating this middleware, most of the time you will want to apply it after
        any filtering happens, so that the centroid is calculated on the filtered geometry. This is
        done by adding it to the `search_transforms_after` list in the `MiddlewareConfig`. See the
        below example.

        Returns:
            SearchTransform: middleware to calculate the bounds of the queried geometry

        Examples:
            >>> # Add the bounds middleware to a dataset view
            >>> ds_with_bounds = ds.view(
            ...     middleware=MiddlewareConfig(
            ...         search_transforms_after=[SearchTransform.bounds()]
            ...     )
            ... )
        """
        return SearchTransform(
            type="transform-geometry",
            properties={
                "transform": "bounds",
                "parameters": {},
            },
        )

    @staticmethod
    def simplify(threshold: float, stride: int = 2) -> "SearchTransform":
        """Simplify the queried geometry

        This middleware will simplify the geometry by removing points according to the
        `Ramer-Douglas-Peucker Algorithm<https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm>`_.
        This is useful for reducing the size of the geometry for visualization or other purposes.
        The threshold is approximately the scale at which points will be removed. A smaller
        threshold will cause more points of the original geometry to be kept, and larger will cause
        more to be thrown away. The stride parameter controls how many points are checked against
        the threshold when simplifying. A larger stride will simplify the geometry faster but may
        result in a less accurate simplification. If you are not familiar with this algorithm, it
        is recommended that you leave stride at the default value of 2.

        When creating this middleware, most of the time you will want to apply it after
        any filtering happens, so that the centroid is calculated on the filtered geometry. This is
        done by adding it to the `search_transforms_after` list in the `MiddlewareConfig`. See the
        below example.

        .. note::
            The units of the threshold are the same as the units of the spatial reference of the
            geometry. For instance, if the geometry is in EPSG:4326, the threshold will be in degrees.

        Args:
            threshold (float): distance between points that will be removed
            stride (int, optional): number of points to skip when simplifying. Defaults to 2.

        Returns:
            SearchTransform: middleware to simplify the queried geometry

        Examples:
            >>> # Add the simplify middleware to a dataset view
            >>> simplified_ds = ds.view(
            ...     middleware=MiddlewareConfig(
            ...         search_transforms_after=[SearchTransform.simplify(threshold=0.01, stride=3)]
            ...     )
            ... )
        """
        if threshold < 0:
            raise ValueError("threshold must be greater than or equal to 0")

        if stride < 1:
            raise ValueError("stride must be greater than or equal to 1")

        return SearchTransform(
            type="transform-geometry",
            properties={
                "transform": "simplify",
                "parameters": {"threshold": threshold, "stride": stride},
            },
        )

    @staticmethod
    def default_datetime_range(
        start: Union[datetime.datetime, str] = None,
        end: Union[datetime.datetime, str] = None,
        before_now: datetime.timedelta = None,
    ) -> "SearchTransform":
        """sets the default datetime range in a search request on a Dataset.

        This is useful for when you are creating a dataset that points to a very long time history, but by default
        wish to show a specific time range. This can be useful for things like showing the last 24 hours of data.

        Parameters:
            start: start of the default datetime range. Defaults to None.
            end: end of the default datetime range. Defaults to None.
            before_now: time delta before now to set the start of the default datetime range. If provided, will be used
                instead of start/end and will dynamically be used based on the current time whenever there is a new
                request. Defaults to None.

        Example:

            >>> # Set the default datetime range to be the last 24 hours
            >>> default_datetime_transform = SearchTransform.default_datetime_range(before_now=datetime.timedelta(days=1))

            >>> # Set the default datetime range to be from 2021-01-01 to 2021-01-02
            >>> default_datetime_transform = SearchTransform.default_datetime_range(start="2021-01-01", end="2021-01-02")
        """

        properties = _default_datetime_range_props(start, end, before_now)
        return SearchTransform(type="default-datetime-range", properties=properties)


class PixelsTransform(_Middleware):
    @staticmethod
    def colormap(
        *,
        asset: str,
        band: Union[int, str],
        colormap_name: str = "magma",
        lookup_table: List[List[int]] = None,
        min: float = None,
        max: float = None,
        rescale: bool = False,
        no_data_value: float = None,
        asset_name: str = "colormap",
    ) -> "PixelsTransform":
        """apply a colormap to the pixels data from an existing asset in the dataset

        Args:
            asset: asset to apply the colormap to
            band: band to apply the colormap to
            colormap_name: name of the colormap to apply. Defaults to "magma".
            lookup_table: lookup table to apply. Defaults to None. This can be used to provide a custom colormap
                via a lookup table. In this case, this should be a list of lists where each sublist is a color,
                including the alpha channel. For instance, [[0, 0, 0, 255], [255, 255, 255, 255]] would create a
                colormap that goes from black to white in two steps, splitting values below 0,5 to black and above
                to white.
            min: minimum value of the colormap. Valid only if rescale is True. Defaults to None.
            max: maximum value of the colormap. Valid only if rescale is True. Defaults to None.
            rescale: whether to rescale the colormap to the min and max values. If min/max are None, statistics
                of the dataset (if available) will be used, otherwise the values of the current response will be used.
                Defaults to False.
            no_data_value: value to use for pixels with no data. These values will be transparent. Defaults to None.
            asset_name: name of the asset to create. Defaults to "colormap".

        Examples:
            >>> # Apply the magma colormap to the rasterized band of the asset "rasterized"
            >>> colormap_transform = PixelsTransform.colormap(asset="rasterized", band="rasterized", min=0, max=1000)
        """
        properties = {
            "asset": asset,
            "band": band,
            "colormap_name": colormap_name,
            "rescale": rescale,
            "asset_name": asset_name,
        }
        if lookup_table is not None:
            properties.pop("colormap_name")
            properties["lookup_table"] = lookup_table
        if min is not None:
            properties["min"] = min
        if max is not None:
            properties["max"] = max
        if no_data_value is not None:
            properties["no_data_value"] = no_data_value

        return PixelsTransform(type=PIXELS_TRANSFORM_COLORMAP, properties=properties)

    @staticmethod
    def rescale_shift(
        asset: str,
        bands: List[Union[int, str]] = None,
        scale: List[float] = None,
        shift: List[float] = None,
        clamp: List[float] = None,
        asset_name: str = "rescaled",
    ) -> "PixelsTransform":
        """rescale the pixel values of an asset in a dataset

        Rescales the pixel values of an asset in a dataset by subtracting a shift from the pixel values and then
        dividing by a scale. This is useful for things like normalizing the pixel values of an image to be between
        0 and 1 or 0 and 255, or recalibration pixels values under a linear transformation.

        If scale/shift is not specified, will rescale by the local min/max of the pixel values across all bands. Do not
        use this with tiled services as each tile will be rescaled based on its min/max and the result will be a
        checkerboard pattern. Instead, use the scale/shift parameters to rescale the entire image tile set.

        Args:
            asset: asset to rescale/shift
            bands: bands to rescale/shift. If not specified, will use all bands for the specified asset.
            scale: scale values for each band. This will divide the shifted pixel values by this value.
            shift: shift values for each band. This will subtract this value from the pixel values prior to scaling.
            clamp: If specified, must be 2 numbers to clamp the values between ranges. Values less than clamp[0]
                will be set to clamp[0] and values greater than clamp[1] will be set to clamp[1].
                Defaults to None (no clamping)
            asset_name: name of the asset to create. Defaults to "rescaled".

        Examples:
            >>> # Rescale the pixel values of an asset with values in uint8 to be between 0 and 1
            >>> transform = PixelsTransform.rescale_shift(
            ... asset="my_asset",
            ... bands=[0, 1, 2],
            ... scale=[255],
            ... shift=[0],
            ... asset_name="rescaled"
            ... )

            >>> # Rescale all bands for "my_asset" to be between 0 and 255
            >>> transform = PixelsTransform.rescale_shift(
            ... asset="my_asset",
            ... asset_name="rescaled"
            ... )

            >>> # Rescale "red", "green", and "blue" bands for "image" to be between 0 and 1 using a known min/max
            >>> transform = PixelsTransform.rescale_shift(
            ... asset="image",
            ... bands=["red", "green", "blue"],
            ... scale=[12345, 12345, 12345],
            ... shift=[123, 456, 789],
            ... asset_name="rescaled-rgb"
            ... )
        """
        properties = {
            "asset": asset,
            "asset_name": asset_name,
        }
        if bands is not None:
            properties["bands"] = bands
        if scale is not None and shift is None:
            raise ValueError("Must provide a shift if providing a scale")
        if shift is not None and scale is None:
            raise ValueError("Must provide a scale if providing a shift")
        if scale is not None and shift is not None and len(scale) != len(shift):
            raise ValueError("Scale and shift must be the same length")
        if clamp is not None and len(clamp) != 2:
            raise ValueError("Clamp must be a list of 2 numbers")
        if scale is not None:
            properties["scale"] = scale
        if shift is not None:
            properties["shift"] = shift
        if clamp is not None:
            properties["clamp"] = clamp

        return PixelsTransform(
            type=PIXELS_TRANSFORM_RESCALE_SHIFT,
            properties=properties,
        )

    @staticmethod
    def default_asset_bands(default_asset_bands: List[AssetBands]) -> "PixelsTransform":
        """sets the default value of asset_bands in a pixels request on a Dataset.

        This is useful for when you are creating a static dataset and want to set the default bands that will be
        used in the pixels request or for when you have a dataset that has multiple bands and you want
        to set the default bands that will be used in the pixels request.

        Parameters:
            default_asset_bands: list of AssetBands objects that will be used as the default bands in the pixels request

        Example:

            >>> # Set the default asset bands to be the first band of the rasterized asset
            >>> default_asset_transform = PixelsTransform.default_asset_bands([AssetBands(asset="rasterized", bands=[0])])
        """
        return PixelsTransform(
            type=PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
            properties={"asset_bands": default_asset_bands},
        )

    @staticmethod
    def default_datetime_range(
        start: Union[datetime.datetime, str] = None,
        end: Union[datetime.datetime, str] = None,
        before_now: datetime.timedelta = None,
    ) -> "PixelsTransform":
        """sets the default datetime range in a pixels request on a Dataset.

        This is useful for when you are creating a dataset that points to a very long time history, but by default
        wish to show a specific time range. This can be useful for things like showing the last 24 hours of data.

        Parameters:
            start: start of the default datetime range. Defaults to None.
            end: end of the default datetime range. Defaults to None.
            before_now: time delta before now to set the start of the default datetime range. If provided, will be used
                instead of start/end and will dynamically be used based on the current time whenever there is a new
                request. Defaults to None.

        Example:

            >>> # Set the default datetime range to be the last 24 hours
            >>> default_datetime_transform = PixelsTransform.default_datetime_range(before_now=datetime.timedelta(days=1))

            >>> # Set the default datetime range to be from 2021-01-01 to 2021-01-02
            >>> default_datetime_transform = PixelsTransform.default_datetime_range(start="2021-01-01", end="2021-01-02")
        """

        properties = _default_datetime_range_props(start, end, before_now)
        return PixelsTransform(type="default-datetime-range", properties=properties)

    @staticmethod
    def rasterize(
        attribute_name: str = None,
        value: Any = None,
        use_z: bool = False,
        initialize_value: Any = None,
        invert: bool = False,
        all_touched: bool = False,
        add: bool = False,
        collections: List[str] = [],
        asset_name: str = "rasterized",
        band_name: str = "rasterized",
        feature_limit: int = 25000,
    ) -> "PixelsTransform":
        """creates a rasterized image from a feature collection as a new raster asset

        Rasterize middleware is useful for performing simple aggregations on a feature collection. This can be
        useful for things like creating a population density raster from a feature collection of population
        counts or creating a binary raster from a feature collection of labels in a segmentation task.

        Args:
            attribute_name: attribute name to rasterize. Defaults to None.
            value: value to rasterize. Defaults to None.
            use_z: whether to use the z value of the feature. Defaults to False.
            initialize_value: value to initialize the raster with. Defaults to None.
            invert: invert which pixels are rasterize. Defaults to False.
            all_touched: whether to rasterize all pixels touched by the feature. Defaults to False.
            add: whether to add the raster to the asset. Defaults to False.
            collections: collections to rasterize. Defaults to [] (all collections).
            asset_name: name of the asset to create. Defaults to "rasterized".
            band_name: name of the band to create. Defaults to "rasterized".
            feature_limit: maximum number of features to rasterize. Defaults to 25000.

        Examples:
            >>> # Rasterize the population attribute by summing the values in the attribute for each pixel
            >>> transform = PixelsTransform.rasterize(
            ... attribute_name="population",
            ... add=True,
            ... asset_name="population_raster",
            ... band_name="population"
            ... )

            >>> # Rasterize by object by setting the value to 1 wherever there is an object
            >>> transform = PixelsTransform.rasterize(
            ... value=1
            ... )

            >>> # Rasterize by object by setting the value to 1 wherever there is NOT an object
            >>> transform = PixelsTransform.rasterize(
            ... value=1,
            ... invert=True
            ... )

        """

        if (value is None and attribute_name is None) and (not use_z):
            raise ValueError(
                "Must provide either a value or an attribute_name or use_z must be True."
            )

        return PixelsTransform(
            type=PIXELS_TRANSFORM_RASTERIZE,
            properties={
                "value": value,
                "initialize_value": initialize_value,
                "attribute_name": attribute_name,
                "invert": invert,
                "all_touched": all_touched,
                "use_z": use_z,
                "add": add,
                "collections": collections,
                "asset_name": asset_name,
                "band_name": band_name,
                "feature_limit": feature_limit,
            },
        )


class MiddlewareConfig(_APIObject):
    """Configures the Middleware for a Dataset

    Middleware can be applied to a dataset to perform actions on the data before it is returned to the user, but
    without influencing the underlying data. This can be useful for things like filtering, transforming, or
    enhancing the data in some way. Middleware can be applied to the search and pixels handlers of a dataset.

    Middleware is broken into a few different pieces:

    - Search Filters: These are filters that are applied to the search results of a dataset. They can be used to
        filter the results of a search based on some criteria. These should ONLY be applied to providers that
        don't offer filtering themselves. When in doubt DON'T apply filters. Most providers have them implemented
        and this is generally not needed. If you've implemented a remote provider with a relatively small number
        of features, this can be useful since implementing filtering on the provider side can be difficult.
    - Search Transforms: These are transforms that are applied to the search results of a dataset. They can be used
        to rename fields, combine fields, or otherwise modify the results of a search. These can be applied either
        before or after search filters. In the former case, set `search_transforms_before` and in the latter case,
        set `search_transforms_after`.
    - Pixels Transforms: These are transforms that are applied to the pixels handler of a dataset. They can be used
        to apply colormaps, rescale pixel values, or otherwise modify the pixels data. Many of them can create new
        assets in the dataset while some may modifiy existing assets.
    """

    search_filters = _ListDescr(
        item_type=(SearchFilter, dict),
        coerce_items=True,
        doc="Which filter actions to perform applied to the result of a dataset.",
    )
    search_transforms_before = _ListDescr(
        item_type=(SearchTransform, dict),
        coerce_items=True,
        doc="transforms to be applied to each feature/item in a search response. "
        "This is applied BEFORE any filtering takes place",
    )
    search_transforms_after = _ListDescr(
        item_type=(SearchTransform, dict),
        coerce_items=True,
        doc="transforms to be applied to each feature/item in a search response. "
        "This is applied AFTER any filtering takes place",
    )
    pixels_transforms = _ListDescr(
        item_type=(PixelsTransform, dict),
        coerce_items=True,
        doc="transforms the request/response of a pixels handler. Useful for "
        "things like applying colormaps or more complex transformations on the pixels data.",
    )


def _default_datetime_range_props(
    start: Union[datetime.datetime, str] = None,
    end: Union[datetime.datetime, str] = None,
    before_now: datetime.timedelta = None,
) -> dict:
    if all([start is None, end is None, before_now is None]):
        raise ValueError("Must provide at least a start, end, or before_now")

    datetime_specified = start is not None or end is not None
    before_now_specified = before_now is not None

    if datetime_specified and before_now_specified:
        raise ValueError("Cannot provide both a before_now and a start/end")

    if before_now_specified:
        return {"seconds_before_now": before_now.total_seconds()}

    start = datetime_to_utc(parsedate(start)).isoformat()
    end = datetime_to_utc(parsedate(end)).isoformat()

    return {"datetime": [start, end]}
