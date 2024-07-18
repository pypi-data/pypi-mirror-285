"""
This file implements a wrapper for a cache directory for *yet_another_wizz*
catalogs. The cache is designed to hold a pair of a data and an (optional)
random catalog. The patch center coordinates are enforced to be consistent
within a cache. These caches are created by `YawCacheCreate`, but must currently
be removed manually by the user when they are no longer needed.
"""

from __future__ import annotations

import logging
import os
from shutil import rmtree

import numpy as np
from pandas import DataFrame
from yaw.catalogs import NewCatalog
from yaw.catalogs.scipy import ScipyCatalog
from yaw.core.coordinates import Coordinate, CoordSky

__all__ = [
    "YawCache",
]


logger = logging.getLogger(__name__)


def normalise_path(path: str) -> str:
    """Substitute UNIX style home directories and environment variables in path
    names."""
    return os.path.expandvars(os.path.expanduser(path))


def patch_centers_from_file(path: str) -> CoordSky:
    """
    Load a list of patch centers from a file.

    Patch centers are expected to be listed line-by-line as pairs of R.A./Dec.
    in radian, separated by a single space or tab.

    Parameters
    ----------
    path: str
        Path to input file.

    Returns
    -------
    CoordSky
        List of patch centers read from file.
    """
    coords = np.loadtxt(path, ndmin=2)
    try:
        return CoordSky.from_array(coords)
    except Exception as err:
        raise ValueError("invalid coordinate file format or schema") from err


def get_patch_method(
    patch_centers: ScipyCatalog | Coordinate | None,
    patch_name: str | None,
    n_patches: int | None,
) -> ScipyCatalog | Coordinate | str | int:
    """
    Extract the preferred parameter value from the patch parameters, follow a
    hierarchy of preference.

    Parameters
    ----------
    patch_centers : ScipyCatalog, Coordinate or None
        A *yet_another_wizz* catalog or coordinates, or `None` if not set.
    patch_name : str or None
        The name of the column that list the patch indices or `None` if not set.
    n_patches: int or None
        The number of patches to generate using k-means clustering or `None` if
        not set.

    Returns
    -------
    ScipyCatalog, Coordinate, str, or int
        The preferred parameter value to configure the patch creation.

    Raises
    ------
    ValueError
        If all parameter values are set to `None`.
    """
    # NOTE: "consistent" referes to the consistency of patch centers of two
    # catalogs created with a particular patch creation method.
    if patch_centers is not None:  # deterministic and consistent
        return patch_centers
    if patch_name is not None:  # deterministic but assumes consistency
        return patch_name
    if n_patches is not None:  # non-determistic and never consistent
        return n_patches
    raise ValueError("no patch creation method specified")


class YawCatalog:
    """
    Wrapper around a *yet_another_wizz* catalog that is cached on disk in
    spatial patches.

    Parameters
    ----------
    path : str
        Path to the directory in which the data is cached.
    """

    path: str
    """Path to the directory in which the data is cached."""
    catalog: ScipyCatalog | None
    """Catalog instance or `None` if no data is cached yet."""

    def __init__(self, path: str) -> None:
        self.path = normalise_path(path)
        self.catalog = None
        self._patch_center_callback = None

    def set_patch_center_callback(self, cat: YawCatalog | None) -> None:
        """
        Register a different `YawCatalog` instance that defines the patch
        centers to use.

        If set, all patch configuration parameters in `set` are ignored and the
        patch centers of the linked catalog are used instead. Useful to ensure
        that two catalogs have consistent patch centers without explicitly
        setting them a priori.

        Parameters
        ----------
        cat : YawCatalog or None
            The catalog instance that acts are reference for the patch centers.
            If `None`, removes the callback.
        """
        if cat is None:
            self._patch_center_callback = None
        elif isinstance(cat, YawCatalog):
            self._patch_center_callback = lambda: cat.get().centers
        else:
            raise TypeError("referenced catalog is not a 'YawCatalog'")

    def exists(self) -> bool:
        """Whether the catalog's cache directory exists."""
        return os.path.exists(self.path)

    def get(self) -> ScipyCatalog:
        """
        Access the catalog instance without loading all data to memory.

        Retrieves the catalog metadata from disk if not in memory.

        Returns
        -------
        ScipyCatalog
            The cached catalog instance.

        Raises
        ------
        FileNotFoundError
            If not data is cached at the specifed path.
        """
        if not self.exists():
            raise FileNotFoundError(f"no catalog cached at {self.path}")
        if self.catalog is None:
            self.catalog = NewCatalog().from_cache(self.path)
        return self.catalog

    def set(
        self,
        source: DataFrame | str,
        ra_name: str,
        dec_name: str,
        *,
        patch_centers: ScipyCatalog | Coordinate | None = None,
        patch_name: str | None = None,
        n_patches: int | None = None,
        redshift_name: str | None = None,
        weight_name: str | None = None,
        overwrite: bool = False,
        **kwargs,  # pylint: disable=W0613; allows dict-unpacking of whole config
    ) -> ScipyCatalog:
        """
        Split a new data set in spatial patches and cache it.

        Parameters
        ----------
        source : DataFrame or str
            Data source, either a `DataFrame` or a FITS, Parquet, or HDF5 file.
        ra_name : str
            Column name of right ascension data in degrees.
        dec_name : str
            Column name of declination data in degrees.
        patch_centers : ScipyCatalog, Coordinate or None
            A *yet_another_wizz* catalog or coordinates, or `None` if not set.
        patch_name : str or None
            The name of the column that list the patch indices or `None` if not set.
        n_patches: int or None
            The number of patches to generate using k-means clustering or `None` if
            not set.
        redshift_name : str or None, optional
            Column name of redshifts.
        weight_name: str or None, optional
            Column name of per-object weigths.
        overwrite: bool, optional
            Whether to overwrite an existing, cached data set.

        Returns
        -------
        ScipyCatalog
            The cached catalog instance.

        Raises
        ------
        FileExistsError
            If there is already a data set cached and `overwrite` is not set.
        """
        if self.exists():
            if overwrite:
                rmtree(self.path)
            else:
                raise FileExistsError(self.path)
        os.makedirs(self.path)

        # check if any reference catalog is registered that overwrites the
        # provided patch centers
        try:
            patch_centers = self._patch_center_callback()
        except (TypeError, FileNotFoundError):
            pass

        if isinstance(source, str):  # dealing with a file
            patches = get_patch_method(
                patch_centers=patch_centers,
                patch_name=patch_name,
                n_patches=n_patches,
            )
            self.catalog = NewCatalog().from_file(
                filepath=source,
                patches=patches,
                ra=ra_name,
                dec=dec_name,
                redshift=redshift_name,
                weight=weight_name,
                cache_directory=self.path,
            )

        else:
            # ensure that patch_centers are always used if provided
            if patch_centers is not None:
                patch_name = None
                n_patches = None
            self.catalog = NewCatalog().from_dataframe(
                data=source,
                ra_name=ra_name,
                dec_name=dec_name,
                patch_centers=patch_centers,
                patch_name=patch_name,
                n_patches=n_patches,
                redshift_name=redshift_name,
                weight_name=weight_name,
                cache_directory=self.path,
            )

    def drop(self) -> None:
        """Delete the cached data from disk and unset the catalog instance."""
        if self.exists():
            rmtree(self.path)
        self.catalog = None


class YawCache:
    """
    A cache directory for *yet_another_wizz* to store a data and (optional)
    random catalogue.

    The data sets are split into consistent spatial patches used for spatial
    resampling and covariance estiation by *yet_another_wizz* and wrapped by
    `YawCatalog` instances. Once any data set is specifed, the other data set
    will inherit its patch centers.

    Create a new instance with the `create` method or open an existing cache.
    If an existing cache is used, the code checks if the provided directory is a
    valid cache. To interact with the data set and the randoms, directly access
    the methods of the `data` and `rand` attributes.

    Parameters
    ----------
    path : str
        Path at which the data and random catalogues are cached, must exist and
        has to be created with the `create` method.
    """

    _flag_path = ".yaw_cache"  # file to mark a valid cache directory
    path: str
    """Path at which the data and random catalogues are cached."""
    data: YawCatalog
    """Catalog instance for the data set."""
    rand: YawCatalog
    """Catalog instance for the randoms."""

    def __init__(self, path: str) -> None:
        self.path = normalise_path(path)

        if not os.path.exists(self.path):
            raise FileNotFoundError(self.path)
        if not self.is_valid(self.path):
            raise FileNotFoundError(f"not a valid cache directory: {self.path}")

        self.data = YawCatalog(os.path.join(self.path, "data"))
        self.rand = YawCatalog(os.path.join(self.path, "rand"))
        self.data.set_patch_center_callback(self.rand)
        self.rand.set_patch_center_callback(self.data)

    @classmethod
    def is_valid(cls, path: str) -> bool:
        """Whether the provided path is a valid cache."""
        indicator_path = os.path.join(path, cls._flag_path)
        return os.path.exists(indicator_path)

    @classmethod
    def create(cls, path: str, overwrite: bool = False) -> YawCache:
        """
        Create an empty cache directory at the specifed path.

        Parameters
        ----------
        path : str
            Path at which the data and random catalogues are cached.
        overwrite : bool, optional
            Whether to overwrite an existing cache directory.

        Returns
        -------
        YawCache
            The newly created cache instance.
        """
        normalised = normalise_path(path)

        if os.path.exists(normalised):
            if not overwrite:
                raise FileExistsError(normalised)
            # check if path is valid cache directry and *only* then delete it
            try:
                cls(path).drop()
            except FileNotFoundError as err:
                raise OSError("can only overwrite existing cache directories") from err

        logger.info("creating new cache directory '%s'", normalised)
        os.makedirs(normalised)
        # create the flag file
        with open(os.path.join(normalised, cls._flag_path), "w"):
            pass
        return cls(path)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(path='{self.path}')"

    def get_patch_centers(self) -> CoordSky:
        """
        Get the patch center coordinates.

        Returns
        -------
        CoordSky
            The patch center coordinates in radian as
            `yaw.core.coordinates.CoordSky` instance.

        Raises
        ------
        FileNotFoundError
            If not data is cached yet.
        """
        if self.rand.exists():
            return self.rand.get().centers
        if self.data.exists():
            return self.data.get().centers
        raise FileNotFoundError("cache is empty")

    def n_patches(self) -> int:
        """
        Get the number of spatial patches.

        Returns
        -------
        int
            The number of patches.

        Raises
        ------
        FileNotFoundError
            If not data is cached yet.
        """
        return len(self.get_patch_centers())

    def drop(self) -> None:
        """Delete the entire cache directy."""
        logger.info("dropping cache directory '%s'", self.path)
        rmtree(self.path)
