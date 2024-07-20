"""
---
title: "Dataset"
slug: "sdk-ref-dataset"
hidden: false
metadata:
  title: "Dataset"
  description: "Encord SDK Dataset class"
category: "64e481b57b6027003f20aaa0"
---
"""

from datetime import datetime
from pathlib import Path
from typing import Collection, Dict, Iterable, List, Optional, TextIO, Union
from uuid import UUID

from encord.client import EncordClientDataset
from encord.constants.enums import DataType
from encord.http.utils import CloudUploadSettings
from encord.orm.cloud_integration import CloudIntegration
from encord.orm.dataset import (
    AddPrivateDataResponse,
    DataLinkDuplicatesBehavior,
    DataRow,
    DatasetAccessSettings,
    DatasetDataLongPolling,
    DatasetUser,
    DatasetUserRole,
    Image,
    ImageGroup,
    ImageGroupOCR,
    StorageLocation,
    Video,
)
from encord.orm.dataset import Dataset as OrmDataset
from encord.orm.group import DatasetGroup
from encord.storage import StorageFolder
from encord.utilities.hash_utilities import convert_to_uuid


class Dataset:
    """
    Access dataset related data and manipulate the dataset.
    """

    def __init__(self, client: EncordClientDataset, orm_dataset: OrmDataset):
        self._client = client
        self._dataset_instance = orm_dataset

    @property
    def dataset_hash(self) -> str:
        """
        Get the dataset hash (i.e. the Dataset ID).
        """
        return self._dataset_instance.dataset_hash

    @property
    def title(self) -> str:
        return self._dataset_instance.title

    @property
    def description(self) -> str:
        return self._dataset_instance.description

    @property
    def storage_location(self) -> StorageLocation:
        return self._dataset_instance.storage_location

    @property
    def backing_folder_uuid(self) -> Optional[UUID]:
        return self._dataset_instance.backing_folder_uuid

    @property
    def data_rows(self) -> List[DataRow]:
        """
        Part of the response of this function can be configured by the
        :meth:`encord.dataset.Dataset.set_access_settings` method.

        .. code::

            dataset.set_access_settings(DatasetAccessSettings(fetch_client_metadata=True))
            print(dataset.data_rows)
        """
        return self._dataset_instance.data_rows

    def list_data_rows(
        self,
        title_eq: Optional[str] = None,
        title_like: Optional[str] = None,
        created_before: Optional[Union[str, datetime]] = None,
        created_after: Optional[Union[str, datetime]] = None,
        data_types: Optional[List[DataType]] = None,
        data_hashes: Optional[List[str]] = None,
    ) -> List[DataRow]:
        """
        Retrieve dataset rows (pointers to data, labels).

        Args:
            title_eq: optional exact title row filter
            title_like: optional fuzzy title row filter; SQL syntax
            created_before: optional datetime row filter
            created_after: optional datetime row filter
            data_types: optional data types row filter
            data_hashes: optional list of individual data unit hashes to include


        Returns:
            List[DataRow]: A list of DataRows object that match the filter

        Raises:
            AuthorisationError: If the dataset API key is invalid.
            ResourceNotFoundError: If no dataset exists by the specified dataset EntityId.
            UnknownError: If an error occurs while retrieving the dataset.
        """

        return self._client.list_data_rows(title_eq, title_like, created_before, created_after, data_types, data_hashes)

    def refetch_data(self) -> None:
        """
        The Dataset class will only fetch its properties once. Use this function if you suspect the state of those
        properties to be dirty.
        """
        self._dataset_instance = self._client.get_dataset()

    def get_dataset(self) -> OrmDataset:
        """
        This function is exposed for convenience. You are encouraged to use the property accessors instead.
        """
        return self._client.get_dataset()

    def set_access_settings(self, dataset_access_settings: DatasetAccessSettings, *, refetch_data: bool = True) -> None:
        """
        Args:
            dataset_access_settings: The access settings to use going forward
            refetch_data: Whether a `refetch_data()` call should follow the update of the dataset access settings.
        """
        self._client.set_access_settings(dataset_access_settings)
        if refetch_data:
            self.refetch_data()

    def add_users(self, user_emails: List[str], user_role: DatasetUserRole) -> List[DatasetUser]:
        """
        Add users to dataset. If the user was already added, this operation will succeed but the `user_role` will be
        unchanged. The existing `user_role` will be reflected in the `DatasetUser` instance.

        Args:
            user_emails: list of user emails to be added
            user_role: the user role to assign to all users
        """
        return self._client.add_users(user_emails, user_role)

    def list_groups(self) -> Iterable[DatasetGroup]:
        """
        List all groups that have access to a particular dataset
        """
        dataset_hash = convert_to_uuid(self.dataset_hash)
        page = self._client.list_groups(dataset_hash)
        yield from page.results

    def add_group(self, group_hash: Union[List[UUID], UUID], user_role: DatasetUserRole) -> None:
        """
        Add group to a dataset

        Args:
            group_hash: List of group hashes to be added
            user_role: user role that the group will be given

        Returns:
            None
        """
        if isinstance(group_hash, UUID):
            group_hash = [group_hash]
        self._client.add_groups(self.dataset_hash, group_hash, user_role)

    def remove_group(self, group_hash: Union[List[UUID], UUID]):
        """
        Remove group from dataset

        Args:
            group_hash: List of group hashes to be removed

        Returns:
            None
        """
        if isinstance(group_hash, UUID):
            group_hash = [group_hash]
        dataset_hash = convert_to_uuid(self.dataset_hash)
        self._client.remove_groups(dataset_hash, group_hash)

    def upload_video(
        self,
        file_path: Union[str, Path],
        cloud_upload_settings: CloudUploadSettings = CloudUploadSettings(),
        title: Optional[str] = None,
        folder: Optional[Union[UUID, StorageFolder]] = None,
    ) -> Video:
        """
        Upload video to Encord storage.

        Args:
            file_path: path to video e.g. '/home/user/data/video.mp4'
            cloud_upload_settings:
                Settings for uploading data into the cloud. Change this object to overwrite the default values.
            title:
                The video title. If unspecified, this will be the file name. This title should include an extension.
                For example "encord_video.mp4".
            folder: When uploading to a non-mirror dataset, you have to specify the folder to store the file in.
                This can be either a :class:`encord.storage.Folder` instance or the UUID of the folder.

        Returns:
            An object describing the created video, see :class:`encord.orm.dataset.Video`

        Raises:
            UploadOperationNotSupportedError: If trying to upload to external
                                              datasets (e.g. S3/GPC/Azure)
        """

        folder_uuid = folder.uuid if isinstance(folder, StorageFolder) else folder

        return self._client.upload_video(
            file_path, cloud_upload_settings=cloud_upload_settings, title=title, folder_uuid=folder_uuid
        )

    def create_image_group(
        self,
        file_paths: Iterable[Union[str, Path]],
        max_workers: Optional[int] = None,
        cloud_upload_settings: CloudUploadSettings = CloudUploadSettings(),
        title: Optional[str] = None,
        *,
        create_video: bool = True,
        folder: Optional[Union[UUID, StorageFolder]] = None,
    ) -> List[ImageGroup]:
        """
        Create an image group in Encord storage. Choose this type of image upload for sequential images. Else, you can
        choose the :meth:`.Dataset.upload_image` function.

        Args:
            file_paths: a list of paths to images, e.g.
                ['/home/user/data/img1.png', '/home/user/data/img2.png']
            max_workers:
                DEPRECATED: This argument will be ignored
            cloud_upload_settings:
                Settings for uploading data into the cloud. Change this object to overwrite the default values.
            title:
                The title of the image group. If unspecified this will be randomly generated for you. This title should
                NOT include an extension. For example "encord_image_group".
            create_video:
                A flag specifying how image groups are stored. If `True`, a compressed video will be created from
                the image groups. `True` was the previous default support. If `False`, the images
                are saved as a sequence of images.
            folder:
                When uploading to a non-mirror dataset, you have to specify the folder to store the file in.
                This can be either a :class:`encord.storage.Folder` instance or the UUID of the folder.

        Returns:
            A list containing the object(s) describing the created data unit(s).
            See :class:`encord.orm.dataset.ImageGroup`. The list normally contains a single object.

        Raises:
            UploadOperationNotSupportedError: If trying to upload to external
                                              datasets (e.g. S3/GPC/Azure)
            InvalidArgumentError: If the folder is specified, but the dataset is a mirror dataset.
        """
        return self._client.create_image_group(
            file_paths,
            cloud_upload_settings=cloud_upload_settings,
            title=title,
            create_video=create_video,
            folder_uuid=folder.uuid if isinstance(folder, StorageFolder) else folder,
        )

    def create_dicom_series(
        self,
        file_paths: Collection[Union[Path, str]],
        cloud_upload_settings: CloudUploadSettings = CloudUploadSettings(),
        title: Optional[str] = None,
        folder: Optional[Union[UUID, StorageFolder]] = None,
    ) -> Dict:
        """
        Upload a DICOM series to Encord storage

        Args:
            file_paths: a list of paths to DICOM files, e.g.
                ['/home/user/data/DICOM_1.dcm', '/home/user/data/DICOM_2.dcm']
            cloud_upload_settings:
                Settings for uploading data into the cloud. Change this object to overwrite the default values.
            title:
                The title of the DICOM series. If unspecified this will be randomly generated for you. This title should
                NOT include an extension. For example "encord_image_group".
            folder:
                When uploading to a non-mirror dataset, you have to specify the folder to store the file in.
                This can be either a :class:`encord.storage.Folder` instance or the UUID of the folder.
        Returns:
            A dictionary describing the created series.

        Raises:
            UploadOperationNotSupportedError: If trying to upload to external
                                              datasets (e.g. S3/GPC/Azure)
            InvalidArgumentError: If the folder is specified, but the dataset is a mirror dataset.
        """
        return self._client.create_dicom_series(
            file_paths,
            cloud_upload_settings=cloud_upload_settings,
            title=title,
            folder_uuid=folder.uuid if isinstance(folder, StorageFolder) else folder,
        )

    def upload_image(
        self,
        file_path: Union[Path, str],
        title: Optional[str] = None,
        cloud_upload_settings: CloudUploadSettings = CloudUploadSettings(),
        folder: Optional[Union[UUID, StorageFolder]] = None,
    ) -> Image:
        """
        Upload a single image to Encord storage. If your images are sequential we recommend creating an image group via
        the :meth:`.Dataset.create_image_group` function. For more information please compare
        https://docs.encord.com/docs/annotate-images and https://docs.encord.com/docs/annotate-videos

        Args:
            file_path: The file path to the image
            title: The image title. If unspecified, this will be the file name. This title should include an extension.
                For example "encord_image.png".
            cloud_upload_settings:
                Settings for uploading data into the cloud. Change this object to overwrite the default values.
            folder: When uploading to a non-mirror dataset, you have to specify the folder to store the file in.
                This can be either a :class:`encord.storage.Folder` instance or the UUID of the folder.

        """

        folder_uuid = folder.uuid if isinstance(folder, StorageFolder) else folder
        return self._client.upload_image(file_path, title, cloud_upload_settings, folder_uuid)

    def link_items(
        self,
        item_uuids: List[UUID],
        duplicates_behavior: DataLinkDuplicatesBehavior = DataLinkDuplicatesBehavior.SKIP,
    ) -> List[DataRow]:
        """
        Link storage items to the dataset, creating new data rows.

        Args:
            item_uuids: List of item UUIDs to link to the dataset
            duplicates_behaviour: The behavior to follow when encountering duplicates. Defaults to `SKIP`. See also
                :class:`encord.orm.dataset.DataLinkDuplicatesBehavior`
        """
        return self._client.link_items(item_uuids, duplicates_behavior)

    def delete_image_group(self, data_hash: str):
        """
        Delete an image group in Encord storage.

        Args:
            data_hash: the hash of the image group to delete
        """
        return self._client.delete_image_group(data_hash)

    def delete_data(self, data_hashes: Union[List[str], str]):
        """
        Delete a video/image group from a dataset.

        Args:
            data_hashes: list of hash of the videos/image_groups you'd like to delete, all should belong to the same
             dataset
        """
        return self._client.delete_data(data_hashes)

    def add_private_data_to_dataset(
        self,
        integration_id: str,
        private_files: Union[str, Dict, Path, TextIO],
        ignore_errors: bool = False,
    ) -> AddPrivateDataResponse:
        """
        Append data hosted on a private cloud to an existing dataset.

        For a more complete example of safe uploads, please follow the guide found in our docs under
        :ref:`https://python.docs.encord.com/tutorials/datasets.html#adding-data-from-a-private-cloud
        <tutorials/datasets:Adding data from a private cloud>`

        Args:
            integration_id:
                The `EntityId` of the cloud integration you wish to use.
            private_files:
                A `str` path or `Path` object to a json file, json str or python dictionary of the files you wish to add
            ignore_errors:
                When set to `True`, this will prevent individual errors from stopping the upload process.
        Returns:
            add_private_data_response List of DatasetDataInfo objects containing data_hash and title

        """
        return self._client.add_private_data_to_dataset(integration_id, private_files, ignore_errors)

    def add_private_data_to_dataset_start(
        self,
        integration_id: str,
        private_files: Union[str, Dict, Path, TextIO],
        ignore_errors: bool = False,
        *,
        folder: Optional[Union[StorageFolder, UUID]] = None,
    ) -> str:
        """
        Append data hosted on a private cloud to an existing dataset.

        This method inititalizes the upload in Encord's backend.
        Once the upload id has been returned, you can exit the terminal
        while the job continues uninterrupted.

        You can check upload job status at any point using
        the :meth:`add_private_data_to_dataset_get_result` method.
        This can be done in a separate python session to the one
        where the upload was initialized.

        Args:
            integration_id:
                The `EntityId` of the cloud integration you wish to use.
            private_files:
                A `str` path or `Path` object to a json file, json str or python dictionary of the files you wish to add
            ignore_errors:
                When set to `True`, this will prevent individual errors from stopping the upload process.
            folder: When uploading to a non-mirror dataset, you have to specify the folder to store the file in.
                This can be either a :class:`encord.storage.Folder` instance or the UUID of the folder.
        Returns:
            str
                `upload_job_id` - UUID Identifier of upload job.
                This id enables the user to track the job progress via SDK, or web app.
        """
        folder_uuid = folder.uuid if isinstance(folder, StorageFolder) else folder
        return self._client.add_private_data_to_dataset_start(integration_id, private_files, ignore_errors, folder_uuid)

    def add_private_data_to_dataset_get_result(
        self,
        upload_job_id: str,
        timeout_seconds: int = 7 * 24 * 60 * 60,  # 7 days
    ) -> DatasetDataLongPolling:
        """
        Fetch data upload status, perform long polling process for `timeout_seconds`.

        Args:
            upload_job_id:
                UUID Identifier of upload job. This id enables the user to track the job progress via SDK, or web app.
            timeout_seconds:
                Number of seconds the method will wait while waiting for a response.
                If `timeout_seconds == 0`, only a single checking request is performed.
                Response will be immediately returned.
        Returns:
            DatasetDataLongPolling
                Response containing details about job status, errors and progress.
        """
        return self._client.add_private_data_to_dataset_get_result(upload_job_id, timeout_seconds)

    def update_data_item(self, data_hash: str, new_title: str) -> bool:
        """
        DEPRECATED: Use the individual setter properties of the respective :class:`encord.orm.dataset.DataRow`
        instance instead. These can be retrieved via the :meth:`.Dataset.data_rows` function.

        Update a data item

        Args:
            data_hash: str
                Data hash of the item being updated
            new_title:
                String containing the new title of the data item being updated
        Returns:
           Returns a boolean for whether the update was successful

        """
        return self._client.update_data_item(data_hash, new_title)

    def re_encode_data(self, data_hashes: List[str]):
        """
        Launches an async task that can re-encode a list of videos.

        Args:
            data_hashes: list of hash of the videos you'd like to re_encode, all should belong to the same
             dataset
        Returns:
            EntityId(integer) of the async task launched.

        """
        return self._client.re_encode_data(data_hashes)

    def re_encode_data_status(self, job_id: int):
        """
        Returns the status of an existing async task which is aimed at re-encoding videos.

        Args:
            job_id: id of the async task that was launched to re-encode the videos

        Returns:
            ReEncodeVideoTask: Object containing the status of the task, along with info about the new encoded videos
             in case the task has been completed
        """
        return self._client.re_encode_data_status(job_id)

    def run_ocr(self, image_group_id: str) -> List[ImageGroupOCR]:
        """
        Returns an optical character recognition result for a given image group
        Args:
            image_group_id: the id of the image group in this dataset to run OCR on

        Returns:
            Returns a list of ImageGroupOCR objects representing the text and corresponding coordinates
            found in each frame of the image group
        """
        return self._client.run_ocr(image_group_id)

    def get_cloud_integrations(self) -> List[CloudIntegration]:
        return self._client.get_cloud_integrations()
