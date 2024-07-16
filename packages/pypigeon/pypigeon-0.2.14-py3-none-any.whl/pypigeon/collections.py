"""Interactions with collections, items, and data tables"""
import os.path
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from typing import BinaryIO
from typing import cast
from typing import Literal
from typing import Optional
from typing import overload
from typing import TextIO
from typing import TYPE_CHECKING
from typing import Union

import pandas as pd
import pyarrow as pa  # type: ignore
from tqdm.auto import tqdm

from . import item_io
from .pigeon_core import AuthenticatedClient as CoreAuthClient
from .pigeon_core import Paginator
from .pigeon_core.api.items import collections_items_list_items
from .pigeon_core.api.tables import collections_tables_get_table_data
from .pigeon_core.models import Collection
from .pigeon_core.models import CollectionsItemsListItemsResponse200
from .pigeon_core.models import Item
from .pigeon_core.models import ItemParser
from .pigeon_core.models import ItemType
from .pigeon_core.models import TableData
from .pigeon_core.types import UNSET


def pyarrow_schema_from_json_schema(js: dict[str, Any]) -> pa.Schema:
    """Build a PyArrow schema from a JSON schema.

    Args:
        js: JSON schema as dict

    """
    schema_parts = []
    for field, definition in js["properties"].items():
        field_s: dict[str, Any] = {"name": field}
        js_type = definition.get("type")
        js_format = definition.get("format")
        if js_type == "integer":
            field_s["type"] = pa.int64()
        elif js_type == "number":
            field_s["type"] = pa.float64()
        elif js_type == "string":
            if js_format == "date":
                field_s["type"] = pa.date32()
            elif js_format == "time":
                field_s["type"] = pa.time32()
            elif js_format == "datetime":
                field_s["type"] = pa.timestamp("s")
            elif js_format == "duration":
                field_s["type"] = pa.duration("s")
            else:
                field_s["type"] = pa.string()
        elif js_type == "boolean":
            field_s["type"] = pa.bool_()

        if "type" not in field_s:
            raise Exception(f"not yet supporting JSON schema: {definition}")

        # TODO: add data element ref
        field_s["metadata"] = {"dataElement": "..."}

        schema_parts.append(pa.field(**field_s))

    return pa.schema(schema_parts)


class FolderMixin:
    """Folder interaction methods as a mixin class.

    This class is used by :py:class:`PigeonCollection` and
    :py:class:`PigeonFolder`.

    """

    def __init__(
        self,
        collection: "PigeonCollection",
        full_path: Optional[str],
        core: CoreAuthClient,
    ) -> None:
        self._top = collection
        self._path = full_path
        self._client = core

    def _join_path(self, append: str) -> str:
        if self._path is None:
            return append
        return os.path.join(self._path, append)

    def folder(self, folder_name: str) -> "PigeonFolder":
        """Open the named folder.

        Args:
            folder_name (str): the name of the folder to open
        """
        model = collections_items_list_items.sync(
            client=self._client,
            collection_id=self._top.id,
            version_id=self._top.version_id,
            in_path=UNSET if self._path is None else self._path,
            in_folder="ROOT" if self._path is None else UNSET,
            name=folder_name,
            type=[ItemType.FOLDER],
        )
        if len(model.items) != 1:
            raise Exception(f"folder not found: {folder_name}")
        return PigeonFolder(self._top, self, model.items[0], self._client)

    def __getitem__(self, item_path: str) -> "PigeonItem":
        """Retrieve an item in this folder.

        Relative paths are supported, such as ``folder_a/folder_b/item_c``.
        """
        if "/" in item_path:
            folder_name, path_remain = item_path.split("/", 1)
            return self.folder(folder_name)[path_remain]

        model = collections_items_list_items.sync(
            client=self._client,
            collection_id=self._top.id,
            version_id=self._top.version_id,
            in_path=UNSET if self._path is None else self._path,
            in_folder="ROOT" if self._path is None else UNSET,
            name=item_path,
        )
        if len(model.items) != 1:
            if self._path is None:
                msg = f"in top level, item not found: {item_path}"
            else:
                msg = f"in folder {self._path}, item not found: {item_path}"
            raise Exception(msg)
        return PigeonItem(self._top, self, model.items[0], self._client)

    def __iter__(self) -> Iterator["PigeonItem"]:
        """Iterate over all items in this folder."""
        paginator = Paginator[CollectionsItemsListItemsResponse200](
            collections_items_list_items,
            self._client,
        )
        kwargs = {"collection_id": self._top.id, "version_id": self._top.version_id}
        if self._path is None:
            kwargs["in_folder"] = "ROOT"
        else:
            kwargs["in_path"] = self._path

        for item_page in paginator.paginate(**kwargs):
            for item in item_page.items:
                yield PigeonItem(self._top, self, item, self._client)

    def walk(self) -> Iterator["PigeonItem"]:
        """Iterate over all items in this folder, and all subfolders."""
        for item in self:
            yield item
            if isinstance(item, PigeonFolder):
                yield from item

    def get_table(self, item_path: str) -> pd.DataFrame:
        """Retrieve the tabular contents of an item as a :py:class:`pd.DataFrame`.

        Args:
            item_path:
                The path to the item relative to the current folder.
                Accepts slashes ('/') for items in subfolders.

        """
        return self[item_path].table()

    def write_table(
        self,
        item_path: str,
        dataframe: pd.DataFrame,
        format: Literal["csv", "parquet"] = "csv",
        **kwargs: Any,
    ) -> None:
        """Write a :py:class:`pd.DataFrame` to the named item.

        Args:
            item_path:
                The path to the item relative to the current folder.
                Accepts slashes ('/') for items in subfolders.

            dataframe: The dataframe to be written.

            format: One of the supported formats (``csv`` or ``parquet``).

            **kwargs:
                Any other arguments to be passed to the Pandas export
                function. See the documentation for
                :py:func:`pd.DataFrame.to_csv` or
                :py:func:`pd.DataFrame.to_parquet` for valid
                arguments.

        """
        metadata = {
            "Content-Type": {
                "csv": "text/csv",
                "parquet": "application/vnd.apache.parquet",
            }[format]
        }
        with self._top.open(item_path, "wb", parser=format, metadata=metadata) as fp:
            if format == "csv":
                kwargs.setdefault("index", False)
                dataframe.to_csv(fp, mode="wb", **kwargs)
            elif format == "parquet":
                dataframe.to_parquet(fp, **kwargs)


if TYPE_CHECKING:
    ColumnsType = Union[pd.Series[type[object]], pa.Schema]
else:
    ColumnsType = Union[pd.Series, pa.Schema]


class PigeonCollection(FolderMixin):
    """Represents a collection on a Pigeon instance.

    Typically created by one of the collection methods in
    :py:class:`pypigeon.client.PigeonClient`.

    In addition to collection-specific attributes and methods, this
    class also behaves as a folder (representing the top level of the
    collection's folder structure). See :py:class:`FolderMixin` for
    those methods.

    """

    def __init__(self, model: Collection, core: CoreAuthClient) -> None:
        self._model = model
        FolderMixin.__init__(self, self, None, core)

    @property
    def name(self) -> str:
        """Collection name"""
        return self._model.name

    @property
    def id(self) -> str:
        """Collection internal ID"""
        return self._model.id

    @property
    def version_id(self) -> str:
        """Current version ID"""
        return self._model.version_ids[0]

    @property
    def description(self) -> str:
        """Collection text description"""
        return self._model.description

    @property
    def created_on(self) -> datetime:
        """Datetime when collection was created"""
        return self._model.created_on

    def __repr__(self) -> str:
        return (
            f"<PigeonCollection: name={self.name} version={self.version_id}"
            f" id={self.id}>"
        )

    @overload
    def open(self, item_path: str, mode: Literal["r"]) -> TextIO:
        ...

    @overload
    def open(self, item_path: str, mode: Literal["rb"]) -> BinaryIO:
        ...

    @overload
    def open(
        self,
        item_path: str,
        mode: Literal["w"],
        *,
        parser: Optional[str] = None,
        columns: Optional[ColumnsType] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> TextIO:
        ...

    @overload
    def open(
        self,
        item_path: str,
        mode: Literal["wb"],
        *,
        parser: Optional[str] = None,
        columns: Optional[ColumnsType] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> BinaryIO:
        ...

    def open(
        self,
        item_path: str,
        mode: item_io.ItemIOModes = "r",
        *,
        parser: Optional[str] = None,
        columns: Optional[ColumnsType] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Union[BinaryIO, TextIO]:
        r"""Open an item for reading or writing.

        When writing an item, it is important to use the returned
        file-like object either in a context manager or else call its
        :py:func:`close` method when writing is complete, otherwise
        the full contents of the file may not be written.

        Suggested usage::

            with collection.open('new-item', 'wb') as fp:
                fp.write(b'my item content, as much as I have\n')

        Args:
            item_path:
                The path to the item relative to the top level of the
                collection. Accepts slashes ('/') for items located in
                subfolders.

            mode:
                One of the following values, depending on the desired
                interaction mode:

                * ``r`` - reading, text mode
                * ``rb`` - reading, binary mode
                * ``w`` - writing, text mode
                * ``wb`` - writing, binary mode

            parser:
                If writing, optionally specify the item parser type.
                Typical values for this would be ``csv`` or
                ``parquet``.

            columns:
                If writing, optionally specify the item column schema.
                Requires ``parser`` to be set.

            metadata:
                If writing, optionally specify the item metadata.
                Typical values for this would be something like
                ``{"content-type": "text-csv"}``.

        Returns:
            A file-like interface, either :py:class:`BinaryIO` or
            :py:class:`TextIO` depending on whether the file was to be
            opened in binary or text mode. When writing, the return
            will be an instance of
            :py:class:`.item_io.PigeonItemCreatorBinary` or
            :py:class:`.item_io.PigeonItemCreatorText`.

        """
        # when reading, the item needs to exist, so this is the quickest way
        if mode in ("r", "rb"):
            return self[item_path].open(mode)

        elif mode in ("w", "wb"):
            _columns = None  # TODO: convert column schema
            _parser = ItemParser(name=parser) if parser else None
            _metadata = metadata

            if "/" in item_path:
                folder_path, item_name = item_path.rsplit("/", 1)
                folder_id = self[folder_path].id
            else:
                item_name = item_path
                folder_id = "ROOT"

            if mode == "w":
                return item_io.PigeonItemCreatorText(
                    self.id,
                    self.version_id,
                    item_name,
                    self._client,
                    folder_id=folder_id,
                    type="file",
                    columns=_columns,
                    parser=_parser,
                    metadata=_metadata,
                )

            elif mode == "wb":
                return item_io.PigeonItemCreatorBinary(
                    self.id,
                    self.version_id,
                    item_name,
                    self._client,
                    folder_id=folder_id,
                    type="file",
                    columns=_columns,
                    parser=_parser,
                    metadata=_metadata,
                )

        raise Exception("mode not found")


class PigeonItem:
    """Represents an item within a collection."""

    #: Collection that contains this item
    collection: PigeonCollection

    #: Folder that contains this item
    in_folder: FolderMixin

    def __new__(
        cls,
        collection: PigeonCollection,
        in_folder: FolderMixin,
        model: Item,
        core: CoreAuthClient,
    ) -> "PigeonItem":
        if model.type == ItemType.FOLDER and cls is PigeonItem:
            # Automatically create an instance of PigeonFolder when
            # the item is a folder
            return PigeonFolder.__new__(
                PigeonFolder, collection, in_folder, model, core
            )
        return super().__new__(cls)

    def __init__(
        self,
        collection: PigeonCollection,
        in_folder: FolderMixin,
        model: Item,
        core: CoreAuthClient,
    ) -> None:
        self.collection = collection
        self.in_folder = in_folder
        self._model = model
        self._client = core

    @property
    def name(self) -> str:
        """Item name"""
        return self._model.name

    @property
    def path(self) -> str:
        """Item fully qualified path"""
        return self.in_folder._join_path(self.name)

    @property
    def id(self) -> str:
        """Item internal ID"""
        return self._model.id

    @property
    def type(self) -> ItemType:
        """Item type (``file``, ``folder``, ``dataview``, etc.)"""
        return self._model.type

    @property
    def created_on(self) -> datetime:
        """Datetime item was created"""
        return self._model.created_on

    def __repr__(self) -> str:
        return (
            f"<PigeonItem: name={self.name} path={self.path} type={self.type}"
            f" id={self.id}>"
        )

    @overload
    def open(self, mode: item_io.ItemBinaryModes) -> BinaryIO:
        ...

    @overload
    def open(self, mode: item_io.ItemTextModes) -> TextIO:
        ...

    def open(self, mode: item_io.ItemIOModes = "r") -> Union[BinaryIO, TextIO]:
        r"""Open this item for reading or writing.

        When writing an item, it is important to use the returned
        file-like object either in a context manager or else call its
        :py:func:`close` method when writing is complete, otherwise
        the full contents of the file may not be written.

        Suggested usage::

            with item.open('wb') as fp:
                fp.write(b'my item content, as much as I have\n')

        Args:
            mode:
                One of the following values, depending on the desired
                interaction mode:

                * ``r`` - reading, text mode
                * ``rb`` - reading, binary mode
                * ``w`` - writing, text mode
                * ``wb`` - writing, binary mode

        Returns:
            A file-like interface, either :py:class:`BinaryIO` or
            :py:class:`TextIO` depending on whether the file was to be
            opened in binary or text mode. When writing, the return
            will be an instance of
            :py:class:`.item_io.PigeonItemWriterBinary` or
            :py:class:`.item_io.PigeonItemWriterText`.

        """
        if mode == "rb" or mode == "r":
            return item_io.read_item(
                mode,
                self.collection.id,
                self.collection.version_id,
                self.id,
                self._client,
            )

        elif mode == "wb":
            return item_io.PigeonItemWriterBinary(
                self.collection.id, self.collection.version_id, self.id, self._client
            )

        elif mode == "w":
            return item_io.PigeonItemWriterText(
                self.collection.id, self.collection.version_id, self.id, self._client
            )

    def table(self) -> pd.DataFrame:
        """Retrieve the tabular contents of this item as a :py:class:`pd.DataFrame`."""

        def _get_data() -> Iterator[pa.RecordBatch]:
            paginator = Paginator[TableData](
                collections_tables_get_table_data, self._client
            )
            kwargs = {
                "collection_id": self.collection.id,
                "version_id": self.collection.version_id,
                "table_name": self.id,
            }
            with tqdm(desc=f"Loading {self.path}") as pbar:
                for item_page in paginator.paginate(**kwargs):
                    yield pa.RecordBatch.from_pylist(
                        [row.to_dict() for row in item_page.data],
                        schema=pyarrow_schema_from_json_schema(
                            item_page.data_model.to_dict()
                        ),
                    )
                    pbar.total = item_page.pagination.total_items
                    pbar.update(len(item_page.data))

        return cast(pd.DataFrame, pa.Table.from_batches(_get_data()).to_pandas())


class PigeonFolder(PigeonItem, FolderMixin):
    """Represents a folder within a collection.

    Note that folders cannot be opened as data streams, so the
    :py:meth:`open` method will always return :py:exc:`OSError`.

    """

    def __init__(
        self,
        collection: PigeonCollection,
        in_folder: FolderMixin,
        model: Item,
        core: CoreAuthClient,
    ) -> None:
        PigeonItem.__init__(self, collection, in_folder, model, core)
        FolderMixin.__init__(self, collection, in_folder._join_path(model.name), core)

    def __repr__(self) -> str:
        return (
            f"<PigeonFolder: name={self.name} path={self.path} type={self.type}"
            f" id={self.id}>"
        )

    @overload
    def open(self, mode: item_io.ItemBinaryModes) -> BinaryIO:
        ...

    @overload
    def open(self, mode: item_io.ItemTextModes) -> TextIO:
        ...

    def open(self, mode: item_io.ItemIOModes = "r") -> Union[BinaryIO, TextIO]:
        """N/A - folders cannot be opened.

        Raises: :py:exc:`OSError` always
        """
        raise OSError("cannot open folders")
