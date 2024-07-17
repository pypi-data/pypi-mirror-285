# Copyright 2016 Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations

from .model import *


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    change_member_notification: NotificationSetting = None
    receive_request_notification: NotificationSetting = None
    remove_request_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.leave_notification = leave_notification
        return self

    def with_change_member_notification(self, change_member_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.change_member_notification = change_member_notification
        return self

    def with_receive_request_notification(self, receive_request_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.receive_request_notification = receive_request_notification
        return self

    def with_remove_request_notification(self, remove_request_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.remove_request_notification = remove_request_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_change_member_notification(NotificationSetting.from_dict(data.get('changeMemberNotification')))\
            .with_receive_request_notification(NotificationSetting.from_dict(data.get('receiveRequestNotification')))\
            .with_remove_request_notification(NotificationSetting.from_dict(data.get('removeRequestNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "changeMemberNotification": self.change_member_notification.to_dict() if self.change_member_notification else None,
            "receiveRequestNotification": self.receive_request_notification.to_dict() if self.receive_request_notification else None,
            "removeRequestNotification": self.remove_request_notification.to_dict() if self.remove_request_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    description: str = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    change_member_notification: NotificationSetting = None
    receive_request_notification: NotificationSetting = None
    remove_request_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.leave_notification = leave_notification
        return self

    def with_change_member_notification(self, change_member_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.change_member_notification = change_member_notification
        return self

    def with_receive_request_notification(self, receive_request_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.receive_request_notification = receive_request_notification
        return self

    def with_remove_request_notification(self, remove_request_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.remove_request_notification = remove_request_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_change_member_notification(NotificationSetting.from_dict(data.get('changeMemberNotification')))\
            .with_receive_request_notification(NotificationSetting.from_dict(data.get('receiveRequestNotification')))\
            .with_remove_request_notification(NotificationSetting.from_dict(data.get('removeRequestNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "changeMemberNotification": self.change_member_notification.to_dict() if self.change_member_notification else None,
            "receiveRequestNotification": self.receive_request_notification.to_dict() if self.receive_request_notification else None,
            "removeRequestNotification": self.remove_request_notification.to_dict() if self.remove_request_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class DumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> DumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DumpUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DumpUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return DumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckDumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CheckDumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckDumpUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckDumpUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckDumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckDumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CleanUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CleanUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckCleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CheckCleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckCleanUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckCleanUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckCleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckCleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class PrepareImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> PrepareImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PrepareImportUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PrepareImportUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return PrepareImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class ImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> ImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> ImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ImportUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ImportUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return ImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> CheckImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> CheckImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckImportUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CheckImportUserDataByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeGuildModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGuildModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGuildModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGuildModelMastersRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeGuildModelMastersRequest]:
        if data is None:
            return None
        return DescribeGuildModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateGuildModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    default_maximum_member_count: int = None
    maximum_member_count: int = None
    roles: List[RoleModel] = None
    guild_master_role: str = None
    guild_member_default_role: str = None
    rejoin_cool_time_minutes: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateGuildModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateGuildModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateGuildModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateGuildModelMasterRequest:
        self.metadata = metadata
        return self

    def with_default_maximum_member_count(self, default_maximum_member_count: int) -> CreateGuildModelMasterRequest:
        self.default_maximum_member_count = default_maximum_member_count
        return self

    def with_maximum_member_count(self, maximum_member_count: int) -> CreateGuildModelMasterRequest:
        self.maximum_member_count = maximum_member_count
        return self

    def with_roles(self, roles: List[RoleModel]) -> CreateGuildModelMasterRequest:
        self.roles = roles
        return self

    def with_guild_master_role(self, guild_master_role: str) -> CreateGuildModelMasterRequest:
        self.guild_master_role = guild_master_role
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> CreateGuildModelMasterRequest:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_rejoin_cool_time_minutes(self, rejoin_cool_time_minutes: int) -> CreateGuildModelMasterRequest:
        self.rejoin_cool_time_minutes = rejoin_cool_time_minutes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGuildModelMasterRequest]:
        if data is None:
            return None
        return CreateGuildModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_maximum_member_count(data.get('defaultMaximumMemberCount'))\
            .with_maximum_member_count(data.get('maximumMemberCount'))\
            .with_roles([
                RoleModel.from_dict(data.get('roles')[i])
                for i in range(len(data.get('roles')) if data.get('roles') else 0)
            ])\
            .with_guild_master_role(data.get('guildMasterRole'))\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))\
            .with_rejoin_cool_time_minutes(data.get('rejoinCoolTimeMinutes'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultMaximumMemberCount": self.default_maximum_member_count,
            "maximumMemberCount": self.maximum_member_count,
            "roles": [
                self.roles[i].to_dict() if self.roles[i] else None
                for i in range(len(self.roles) if self.roles else 0)
            ],
            "guildMasterRole": self.guild_master_role,
            "guildMemberDefaultRole": self.guild_member_default_role,
            "rejoinCoolTimeMinutes": self.rejoin_cool_time_minutes,
        }


class GetGuildModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGuildModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetGuildModelMasterRequest:
        self.guild_model_name = guild_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildModelMasterRequest]:
        if data is None:
            return None
        return GetGuildModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
        }


class UpdateGuildModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    description: str = None
    metadata: str = None
    default_maximum_member_count: int = None
    maximum_member_count: int = None
    roles: List[RoleModel] = None
    guild_master_role: str = None
    guild_member_default_role: str = None
    rejoin_cool_time_minutes: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGuildModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> UpdateGuildModelMasterRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_description(self, description: str) -> UpdateGuildModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateGuildModelMasterRequest:
        self.metadata = metadata
        return self

    def with_default_maximum_member_count(self, default_maximum_member_count: int) -> UpdateGuildModelMasterRequest:
        self.default_maximum_member_count = default_maximum_member_count
        return self

    def with_maximum_member_count(self, maximum_member_count: int) -> UpdateGuildModelMasterRequest:
        self.maximum_member_count = maximum_member_count
        return self

    def with_roles(self, roles: List[RoleModel]) -> UpdateGuildModelMasterRequest:
        self.roles = roles
        return self

    def with_guild_master_role(self, guild_master_role: str) -> UpdateGuildModelMasterRequest:
        self.guild_master_role = guild_master_role
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> UpdateGuildModelMasterRequest:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_rejoin_cool_time_minutes(self, rejoin_cool_time_minutes: int) -> UpdateGuildModelMasterRequest:
        self.rejoin_cool_time_minutes = rejoin_cool_time_minutes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGuildModelMasterRequest]:
        if data is None:
            return None
        return UpdateGuildModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_maximum_member_count(data.get('defaultMaximumMemberCount'))\
            .with_maximum_member_count(data.get('maximumMemberCount'))\
            .with_roles([
                RoleModel.from_dict(data.get('roles')[i])
                for i in range(len(data.get('roles')) if data.get('roles') else 0)
            ])\
            .with_guild_master_role(data.get('guildMasterRole'))\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))\
            .with_rejoin_cool_time_minutes(data.get('rejoinCoolTimeMinutes'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultMaximumMemberCount": self.default_maximum_member_count,
            "maximumMemberCount": self.maximum_member_count,
            "roles": [
                self.roles[i].to_dict() if self.roles[i] else None
                for i in range(len(self.roles) if self.roles else 0)
            ],
            "guildMasterRole": self.guild_master_role,
            "guildMemberDefaultRole": self.guild_member_default_role,
            "rejoinCoolTimeMinutes": self.rejoin_cool_time_minutes,
        }


class DeleteGuildModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGuildModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteGuildModelMasterRequest:
        self.guild_model_name = guild_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGuildModelMasterRequest]:
        if data is None:
            return None
        return DeleteGuildModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
        }


class DescribeGuildModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGuildModelsRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeGuildModelsRequest]:
        if data is None:
            return None
        return DescribeGuildModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetGuildModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGuildModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetGuildModelRequest:
        self.guild_model_name = guild_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildModelRequest]:
        if data is None:
            return None
        return GetGuildModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
        }


class SearchGuildsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    display_name: str = None
    attributes1: List[int] = None
    attributes2: List[int] = None
    attributes3: List[int] = None
    attributes4: List[int] = None
    attributes5: List[int] = None
    join_policies: List[str] = None
    include_full_members_guild: bool = None
    page_token: str = None
    limit: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SearchGuildsRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> SearchGuildsRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> SearchGuildsRequest:
        self.access_token = access_token
        return self

    def with_display_name(self, display_name: str) -> SearchGuildsRequest:
        self.display_name = display_name
        return self

    def with_attributes1(self, attributes1: List[int]) -> SearchGuildsRequest:
        self.attributes1 = attributes1
        return self

    def with_attributes2(self, attributes2: List[int]) -> SearchGuildsRequest:
        self.attributes2 = attributes2
        return self

    def with_attributes3(self, attributes3: List[int]) -> SearchGuildsRequest:
        self.attributes3 = attributes3
        return self

    def with_attributes4(self, attributes4: List[int]) -> SearchGuildsRequest:
        self.attributes4 = attributes4
        return self

    def with_attributes5(self, attributes5: List[int]) -> SearchGuildsRequest:
        self.attributes5 = attributes5
        return self

    def with_join_policies(self, join_policies: List[str]) -> SearchGuildsRequest:
        self.join_policies = join_policies
        return self

    def with_include_full_members_guild(self, include_full_members_guild: bool) -> SearchGuildsRequest:
        self.include_full_members_guild = include_full_members_guild
        return self

    def with_page_token(self, page_token: str) -> SearchGuildsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> SearchGuildsRequest:
        self.limit = limit
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SearchGuildsRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SearchGuildsRequest]:
        if data is None:
            return None
        return SearchGuildsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_display_name(data.get('displayName'))\
            .with_attributes1([
                data.get('attributes1')[i]
                for i in range(len(data.get('attributes1')) if data.get('attributes1') else 0)
            ])\
            .with_attributes2([
                data.get('attributes2')[i]
                for i in range(len(data.get('attributes2')) if data.get('attributes2') else 0)
            ])\
            .with_attributes3([
                data.get('attributes3')[i]
                for i in range(len(data.get('attributes3')) if data.get('attributes3') else 0)
            ])\
            .with_attributes4([
                data.get('attributes4')[i]
                for i in range(len(data.get('attributes4')) if data.get('attributes4') else 0)
            ])\
            .with_attributes5([
                data.get('attributes5')[i]
                for i in range(len(data.get('attributes5')) if data.get('attributes5') else 0)
            ])\
            .with_join_policies([
                data.get('joinPolicies')[i]
                for i in range(len(data.get('joinPolicies')) if data.get('joinPolicies') else 0)
            ])\
            .with_include_full_members_guild(data.get('includeFullMembersGuild'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "displayName": self.display_name,
            "attributes1": [
                self.attributes1[i]
                for i in range(len(self.attributes1) if self.attributes1 else 0)
            ],
            "attributes2": [
                self.attributes2[i]
                for i in range(len(self.attributes2) if self.attributes2 else 0)
            ],
            "attributes3": [
                self.attributes3[i]
                for i in range(len(self.attributes3) if self.attributes3 else 0)
            ],
            "attributes4": [
                self.attributes4[i]
                for i in range(len(self.attributes4) if self.attributes4 else 0)
            ],
            "attributes5": [
                self.attributes5[i]
                for i in range(len(self.attributes5) if self.attributes5 else 0)
            ],
            "joinPolicies": [
                self.join_policies[i]
                for i in range(len(self.join_policies) if self.join_policies else 0)
            ],
            "includeFullMembersGuild": self.include_full_members_guild,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class SearchGuildsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    user_id: str = None
    display_name: str = None
    attributes1: List[int] = None
    attributes2: List[int] = None
    attributes3: List[int] = None
    attributes4: List[int] = None
    attributes5: List[int] = None
    join_policies: List[str] = None
    include_full_members_guild: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SearchGuildsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> SearchGuildsByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_user_id(self, user_id: str) -> SearchGuildsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_display_name(self, display_name: str) -> SearchGuildsByUserIdRequest:
        self.display_name = display_name
        return self

    def with_attributes1(self, attributes1: List[int]) -> SearchGuildsByUserIdRequest:
        self.attributes1 = attributes1
        return self

    def with_attributes2(self, attributes2: List[int]) -> SearchGuildsByUserIdRequest:
        self.attributes2 = attributes2
        return self

    def with_attributes3(self, attributes3: List[int]) -> SearchGuildsByUserIdRequest:
        self.attributes3 = attributes3
        return self

    def with_attributes4(self, attributes4: List[int]) -> SearchGuildsByUserIdRequest:
        self.attributes4 = attributes4
        return self

    def with_attributes5(self, attributes5: List[int]) -> SearchGuildsByUserIdRequest:
        self.attributes5 = attributes5
        return self

    def with_join_policies(self, join_policies: List[str]) -> SearchGuildsByUserIdRequest:
        self.join_policies = join_policies
        return self

    def with_include_full_members_guild(self, include_full_members_guild: bool) -> SearchGuildsByUserIdRequest:
        self.include_full_members_guild = include_full_members_guild
        return self

    def with_page_token(self, page_token: str) -> SearchGuildsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> SearchGuildsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SearchGuildsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SearchGuildsByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SearchGuildsByUserIdRequest]:
        if data is None:
            return None
        return SearchGuildsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_user_id(data.get('userId'))\
            .with_display_name(data.get('displayName'))\
            .with_attributes1([
                data.get('attributes1')[i]
                for i in range(len(data.get('attributes1')) if data.get('attributes1') else 0)
            ])\
            .with_attributes2([
                data.get('attributes2')[i]
                for i in range(len(data.get('attributes2')) if data.get('attributes2') else 0)
            ])\
            .with_attributes3([
                data.get('attributes3')[i]
                for i in range(len(data.get('attributes3')) if data.get('attributes3') else 0)
            ])\
            .with_attributes4([
                data.get('attributes4')[i]
                for i in range(len(data.get('attributes4')) if data.get('attributes4') else 0)
            ])\
            .with_attributes5([
                data.get('attributes5')[i]
                for i in range(len(data.get('attributes5')) if data.get('attributes5') else 0)
            ])\
            .with_join_policies([
                data.get('joinPolicies')[i]
                for i in range(len(data.get('joinPolicies')) if data.get('joinPolicies') else 0)
            ])\
            .with_include_full_members_guild(data.get('includeFullMembersGuild'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "userId": self.user_id,
            "displayName": self.display_name,
            "attributes1": [
                self.attributes1[i]
                for i in range(len(self.attributes1) if self.attributes1 else 0)
            ],
            "attributes2": [
                self.attributes2[i]
                for i in range(len(self.attributes2) if self.attributes2 else 0)
            ],
            "attributes3": [
                self.attributes3[i]
                for i in range(len(self.attributes3) if self.attributes3 else 0)
            ],
            "attributes4": [
                self.attributes4[i]
                for i in range(len(self.attributes4) if self.attributes4 else 0)
            ],
            "attributes5": [
                self.attributes5[i]
                for i in range(len(self.attributes5) if self.attributes5 else 0)
            ],
            "joinPolicies": [
                self.join_policies[i]
                for i in range(len(self.join_policies) if self.join_policies else 0)
            ],
            "includeFullMembersGuild": self.include_full_members_guild,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateGuildRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    display_name: str = None
    attribute1: int = None
    attribute2: int = None
    attribute3: int = None
    attribute4: int = None
    attribute5: int = None
    join_policy: str = None
    custom_roles: List[RoleModel] = None
    guild_member_default_role: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGuildRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateGuildRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> CreateGuildRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_display_name(self, display_name: str) -> CreateGuildRequest:
        self.display_name = display_name
        return self

    def with_attribute1(self, attribute1: int) -> CreateGuildRequest:
        self.attribute1 = attribute1
        return self

    def with_attribute2(self, attribute2: int) -> CreateGuildRequest:
        self.attribute2 = attribute2
        return self

    def with_attribute3(self, attribute3: int) -> CreateGuildRequest:
        self.attribute3 = attribute3
        return self

    def with_attribute4(self, attribute4: int) -> CreateGuildRequest:
        self.attribute4 = attribute4
        return self

    def with_attribute5(self, attribute5: int) -> CreateGuildRequest:
        self.attribute5 = attribute5
        return self

    def with_join_policy(self, join_policy: str) -> CreateGuildRequest:
        self.join_policy = join_policy
        return self

    def with_custom_roles(self, custom_roles: List[RoleModel]) -> CreateGuildRequest:
        self.custom_roles = custom_roles
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> CreateGuildRequest:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGuildRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGuildRequest]:
        if data is None:
            return None
        return CreateGuildRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_display_name(data.get('displayName'))\
            .with_attribute1(data.get('attribute1'))\
            .with_attribute2(data.get('attribute2'))\
            .with_attribute3(data.get('attribute3'))\
            .with_attribute4(data.get('attribute4'))\
            .with_attribute5(data.get('attribute5'))\
            .with_join_policy(data.get('joinPolicy'))\
            .with_custom_roles([
                RoleModel.from_dict(data.get('customRoles')[i])
                for i in range(len(data.get('customRoles')) if data.get('customRoles') else 0)
            ])\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "displayName": self.display_name,
            "attribute1": self.attribute1,
            "attribute2": self.attribute2,
            "attribute3": self.attribute3,
            "attribute4": self.attribute4,
            "attribute5": self.attribute5,
            "joinPolicy": self.join_policy,
            "customRoles": [
                self.custom_roles[i].to_dict() if self.custom_roles[i] else None
                for i in range(len(self.custom_roles) if self.custom_roles else 0)
            ],
            "guildMemberDefaultRole": self.guild_member_default_role,
        }


class CreateGuildByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    display_name: str = None
    attribute1: int = None
    attribute2: int = None
    attribute3: int = None
    attribute4: int = None
    attribute5: int = None
    join_policy: str = None
    custom_roles: List[RoleModel] = None
    guild_member_default_role: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGuildByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateGuildByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> CreateGuildByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_display_name(self, display_name: str) -> CreateGuildByUserIdRequest:
        self.display_name = display_name
        return self

    def with_attribute1(self, attribute1: int) -> CreateGuildByUserIdRequest:
        self.attribute1 = attribute1
        return self

    def with_attribute2(self, attribute2: int) -> CreateGuildByUserIdRequest:
        self.attribute2 = attribute2
        return self

    def with_attribute3(self, attribute3: int) -> CreateGuildByUserIdRequest:
        self.attribute3 = attribute3
        return self

    def with_attribute4(self, attribute4: int) -> CreateGuildByUserIdRequest:
        self.attribute4 = attribute4
        return self

    def with_attribute5(self, attribute5: int) -> CreateGuildByUserIdRequest:
        self.attribute5 = attribute5
        return self

    def with_join_policy(self, join_policy: str) -> CreateGuildByUserIdRequest:
        self.join_policy = join_policy
        return self

    def with_custom_roles(self, custom_roles: List[RoleModel]) -> CreateGuildByUserIdRequest:
        self.custom_roles = custom_roles
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> CreateGuildByUserIdRequest:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateGuildByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGuildByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGuildByUserIdRequest]:
        if data is None:
            return None
        return CreateGuildByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_display_name(data.get('displayName'))\
            .with_attribute1(data.get('attribute1'))\
            .with_attribute2(data.get('attribute2'))\
            .with_attribute3(data.get('attribute3'))\
            .with_attribute4(data.get('attribute4'))\
            .with_attribute5(data.get('attribute5'))\
            .with_join_policy(data.get('joinPolicy'))\
            .with_custom_roles([
                RoleModel.from_dict(data.get('customRoles')[i])
                for i in range(len(data.get('customRoles')) if data.get('customRoles') else 0)
            ])\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "displayName": self.display_name,
            "attribute1": self.attribute1,
            "attribute2": self.attribute2,
            "attribute3": self.attribute3,
            "attribute4": self.attribute4,
            "attribute5": self.attribute5,
            "joinPolicy": self.join_policy,
            "customRoles": [
                self.custom_roles[i].to_dict() if self.custom_roles[i] else None
                for i in range(len(self.custom_roles) if self.custom_roles else 0)
            ],
            "guildMemberDefaultRole": self.guild_member_default_role,
            "timeOffsetToken": self.time_offset_token,
        }


class GetGuildRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    guild_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGuildRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetGuildRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetGuildRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> GetGuildRequest:
        self.guild_name = guild_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildRequest]:
        if data is None:
            return None
        return GetGuildRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
        }


class GetGuildByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    guild_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGuildByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetGuildByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetGuildByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> GetGuildByUserIdRequest:
        self.guild_name = guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetGuildByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildByUserIdRequest]:
        if data is None:
            return None
        return GetGuildByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateGuildRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    display_name: str = None
    attribute1: int = None
    attribute2: int = None
    attribute3: int = None
    attribute4: int = None
    attribute5: int = None
    join_policy: str = None
    custom_roles: List[RoleModel] = None
    guild_member_default_role: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGuildRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> UpdateGuildRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> UpdateGuildRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_display_name(self, display_name: str) -> UpdateGuildRequest:
        self.display_name = display_name
        return self

    def with_attribute1(self, attribute1: int) -> UpdateGuildRequest:
        self.attribute1 = attribute1
        return self

    def with_attribute2(self, attribute2: int) -> UpdateGuildRequest:
        self.attribute2 = attribute2
        return self

    def with_attribute3(self, attribute3: int) -> UpdateGuildRequest:
        self.attribute3 = attribute3
        return self

    def with_attribute4(self, attribute4: int) -> UpdateGuildRequest:
        self.attribute4 = attribute4
        return self

    def with_attribute5(self, attribute5: int) -> UpdateGuildRequest:
        self.attribute5 = attribute5
        return self

    def with_join_policy(self, join_policy: str) -> UpdateGuildRequest:
        self.join_policy = join_policy
        return self

    def with_custom_roles(self, custom_roles: List[RoleModel]) -> UpdateGuildRequest:
        self.custom_roles = custom_roles
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> UpdateGuildRequest:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateGuildRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGuildRequest]:
        if data is None:
            return None
        return UpdateGuildRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_display_name(data.get('displayName'))\
            .with_attribute1(data.get('attribute1'))\
            .with_attribute2(data.get('attribute2'))\
            .with_attribute3(data.get('attribute3'))\
            .with_attribute4(data.get('attribute4'))\
            .with_attribute5(data.get('attribute5'))\
            .with_join_policy(data.get('joinPolicy'))\
            .with_custom_roles([
                RoleModel.from_dict(data.get('customRoles')[i])
                for i in range(len(data.get('customRoles')) if data.get('customRoles') else 0)
            ])\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "displayName": self.display_name,
            "attribute1": self.attribute1,
            "attribute2": self.attribute2,
            "attribute3": self.attribute3,
            "attribute4": self.attribute4,
            "attribute5": self.attribute5,
            "joinPolicy": self.join_policy,
            "customRoles": [
                self.custom_roles[i].to_dict() if self.custom_roles[i] else None
                for i in range(len(self.custom_roles) if self.custom_roles else 0)
            ],
            "guildMemberDefaultRole": self.guild_member_default_role,
        }


class UpdateGuildByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_name: str = None
    guild_model_name: str = None
    display_name: str = None
    attribute1: int = None
    attribute2: int = None
    attribute3: int = None
    attribute4: int = None
    attribute5: int = None
    join_policy: str = None
    custom_roles: List[RoleModel] = None
    guild_member_default_role: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGuildByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_name(self, guild_name: str) -> UpdateGuildByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> UpdateGuildByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_display_name(self, display_name: str) -> UpdateGuildByGuildNameRequest:
        self.display_name = display_name
        return self

    def with_attribute1(self, attribute1: int) -> UpdateGuildByGuildNameRequest:
        self.attribute1 = attribute1
        return self

    def with_attribute2(self, attribute2: int) -> UpdateGuildByGuildNameRequest:
        self.attribute2 = attribute2
        return self

    def with_attribute3(self, attribute3: int) -> UpdateGuildByGuildNameRequest:
        self.attribute3 = attribute3
        return self

    def with_attribute4(self, attribute4: int) -> UpdateGuildByGuildNameRequest:
        self.attribute4 = attribute4
        return self

    def with_attribute5(self, attribute5: int) -> UpdateGuildByGuildNameRequest:
        self.attribute5 = attribute5
        return self

    def with_join_policy(self, join_policy: str) -> UpdateGuildByGuildNameRequest:
        self.join_policy = join_policy
        return self

    def with_custom_roles(self, custom_roles: List[RoleModel]) -> UpdateGuildByGuildNameRequest:
        self.custom_roles = custom_roles
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> UpdateGuildByGuildNameRequest:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateGuildByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGuildByGuildNameRequest]:
        if data is None:
            return None
        return UpdateGuildByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_name(data.get('guildName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_display_name(data.get('displayName'))\
            .with_attribute1(data.get('attribute1'))\
            .with_attribute2(data.get('attribute2'))\
            .with_attribute3(data.get('attribute3'))\
            .with_attribute4(data.get('attribute4'))\
            .with_attribute5(data.get('attribute5'))\
            .with_join_policy(data.get('joinPolicy'))\
            .with_custom_roles([
                RoleModel.from_dict(data.get('customRoles')[i])
                for i in range(len(data.get('customRoles')) if data.get('customRoles') else 0)
            ])\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildName": self.guild_name,
            "guildModelName": self.guild_model_name,
            "displayName": self.display_name,
            "attribute1": self.attribute1,
            "attribute2": self.attribute2,
            "attribute3": self.attribute3,
            "attribute4": self.attribute4,
            "attribute5": self.attribute5,
            "joinPolicy": self.join_policy,
            "customRoles": [
                self.custom_roles[i].to_dict() if self.custom_roles[i] else None
                for i in range(len(self.custom_roles) if self.custom_roles else 0)
            ],
            "guildMemberDefaultRole": self.guild_member_default_role,
        }


class DeleteMemberRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMemberRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteMemberRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> DeleteMemberRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteMemberRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteMemberRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMemberRequest]:
        if data is None:
            return None
        return DeleteMemberRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class DeleteMemberByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMemberByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteMemberByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> DeleteMemberByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteMemberByGuildNameRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteMemberByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMemberByGuildNameRequest]:
        if data is None:
            return None
        return DeleteMemberByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "targetUserId": self.target_user_id,
        }


class UpdateMemberRoleRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    target_user_id: str = None
    role_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMemberRoleRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> UpdateMemberRoleRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> UpdateMemberRoleRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> UpdateMemberRoleRequest:
        self.target_user_id = target_user_id
        return self

    def with_role_name(self, role_name: str) -> UpdateMemberRoleRequest:
        self.role_name = role_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateMemberRoleRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMemberRoleRequest]:
        if data is None:
            return None
        return UpdateMemberRoleRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_role_name(data.get('roleName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
            "roleName": self.role_name,
        }


class UpdateMemberRoleByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    target_user_id: str = None
    role_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMemberRoleByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> UpdateMemberRoleByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> UpdateMemberRoleByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_target_user_id(self, target_user_id: str) -> UpdateMemberRoleByGuildNameRequest:
        self.target_user_id = target_user_id
        return self

    def with_role_name(self, role_name: str) -> UpdateMemberRoleByGuildNameRequest:
        self.role_name = role_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateMemberRoleByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMemberRoleByGuildNameRequest]:
        if data is None:
            return None
        return UpdateMemberRoleByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_role_name(data.get('roleName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "targetUserId": self.target_user_id,
            "roleName": self.role_name,
        }


class DeleteGuildRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGuildRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteGuildRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> DeleteGuildRequest:
        self.access_token = access_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteGuildRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGuildRequest]:
        if data is None:
            return None
        return DeleteGuildRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
        }


class DeleteGuildByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGuildByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteGuildByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> DeleteGuildByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteGuildByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGuildByGuildNameRequest]:
        if data is None:
            return None
        return DeleteGuildByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
        }


class IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_value(self, value: int) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.value = value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest]:
        if data is None:
            return None
        return IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "value": self.value,
        }


class DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_value(self, value: int) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.value = value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest]:
        if data is None:
            return None
        return DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "value": self.value,
        }


class VerifyCurrentMaximumMemberCountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyCurrentMaximumMemberCountRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> VerifyCurrentMaximumMemberCountRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> VerifyCurrentMaximumMemberCountRequest:
        self.access_token = access_token
        return self

    def with_verify_type(self, verify_type: str) -> VerifyCurrentMaximumMemberCountRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyCurrentMaximumMemberCountRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyCurrentMaximumMemberCountRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyCurrentMaximumMemberCountRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyCurrentMaximumMemberCountRequest]:
        if data is None:
            return None
        return VerifyCurrentMaximumMemberCountRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyCurrentMaximumMemberCountByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyCurrentMaximumMemberCountByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyCurrentMaximumMemberCountByGuildNameRequest]:
        if data is None:
            return None
        return VerifyCurrentMaximumMemberCountByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyIncludeMemberRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    access_token: str = None
    verify_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyIncludeMemberRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> VerifyIncludeMemberRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> VerifyIncludeMemberRequest:
        self.guild_name = guild_name
        return self

    def with_access_token(self, access_token: str) -> VerifyIncludeMemberRequest:
        self.access_token = access_token
        return self

    def with_verify_type(self, verify_type: str) -> VerifyIncludeMemberRequest:
        self.verify_type = verify_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyIncludeMemberRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyIncludeMemberRequest]:
        if data is None:
            return None
        return VerifyIncludeMemberRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_access_token(data.get('accessToken'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "accessToken": self.access_token,
            "verifyType": self.verify_type,
        }


class VerifyIncludeMemberByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    user_id: str = None
    verify_type: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyIncludeMemberByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> VerifyIncludeMemberByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> VerifyIncludeMemberByUserIdRequest:
        self.guild_name = guild_name
        return self

    def with_user_id(self, user_id: str) -> VerifyIncludeMemberByUserIdRequest:
        self.user_id = user_id
        return self

    def with_verify_type(self, verify_type: str) -> VerifyIncludeMemberByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyIncludeMemberByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyIncludeMemberByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyIncludeMemberByUserIdRequest]:
        if data is None:
            return None
        return VerifyIncludeMemberByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_user_id(data.get('userId'))\
            .with_verify_type(data.get('verifyType'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "userId": self.user_id,
            "verifyType": self.verify_type,
            "timeOffsetToken": self.time_offset_token,
        }


class SetMaximumCurrentMaximumMemberCountByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_name: str = None
    guild_model_name: str = None
    value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_name(self, guild_name: str) -> SetMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> SetMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_value(self, value: int) -> SetMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.value = value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetMaximumCurrentMaximumMemberCountByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetMaximumCurrentMaximumMemberCountByGuildNameRequest]:
        if data is None:
            return None
        return SetMaximumCurrentMaximumMemberCountByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_name(data.get('guildName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildName": self.guild_name,
            "guildModelName": self.guild_model_name,
            "value": self.value,
        }


class AssumeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    guild_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AssumeRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> AssumeRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> AssumeRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> AssumeRequest:
        self.guild_name = guild_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AssumeRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AssumeRequest]:
        if data is None:
            return None
        return AssumeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
        }


class AssumeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    guild_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AssumeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AssumeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> AssumeByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> AssumeByUserIdRequest:
        self.guild_name = guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AssumeByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AssumeByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AssumeByUserIdRequest]:
        if data is None:
            return None
        return AssumeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "timeOffsetToken": self.time_offset_token,
        }


class IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest]:
        if data is None:
            return None
        return IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest]:
        if data is None:
            return None
        return DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class SetMaximumCurrentMaximumMemberCountByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetMaximumCurrentMaximumMemberCountByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetMaximumCurrentMaximumMemberCountByStampSheetRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetMaximumCurrentMaximumMemberCountByStampSheetRequest]:
        if data is None:
            return None
        return SetMaximumCurrentMaximumMemberCountByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifyCurrentMaximumMemberCountByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyCurrentMaximumMemberCountByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyCurrentMaximumMemberCountByStampTaskRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyCurrentMaximumMemberCountByStampTaskRequest]:
        if data is None:
            return None
        return VerifyCurrentMaximumMemberCountByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyIncludeMemberByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyIncludeMemberByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyIncludeMemberByStampTaskRequest:
        self.key_id = key_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyIncludeMemberByStampTaskRequest]:
        if data is None:
            return None
        return VerifyIncludeMemberByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeJoinedGuildsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeJoinedGuildsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeJoinedGuildsRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DescribeJoinedGuildsRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribeJoinedGuildsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeJoinedGuildsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeJoinedGuildsRequest]:
        if data is None:
            return None
        return DescribeJoinedGuildsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeJoinedGuildsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeJoinedGuildsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeJoinedGuildsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DescribeJoinedGuildsByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribeJoinedGuildsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeJoinedGuildsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeJoinedGuildsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeJoinedGuildsByUserIdRequest]:
        if data is None:
            return None
        return DescribeJoinedGuildsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetJoinedGuildRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    guild_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetJoinedGuildRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetJoinedGuildRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetJoinedGuildRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> GetJoinedGuildRequest:
        self.guild_name = guild_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetJoinedGuildRequest]:
        if data is None:
            return None
        return GetJoinedGuildRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
        }


class GetJoinedGuildByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    guild_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetJoinedGuildByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetJoinedGuildByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetJoinedGuildByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> GetJoinedGuildByUserIdRequest:
        self.guild_name = guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetJoinedGuildByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetJoinedGuildByUserIdRequest]:
        if data is None:
            return None
        return GetJoinedGuildByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "timeOffsetToken": self.time_offset_token,
        }


class WithdrawalRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    guild_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> WithdrawalRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> WithdrawalRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> WithdrawalRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> WithdrawalRequest:
        self.guild_name = guild_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WithdrawalRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WithdrawalRequest]:
        if data is None:
            return None
        return WithdrawalRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
        }


class WithdrawalByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    guild_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> WithdrawalByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> WithdrawalByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> WithdrawalByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> WithdrawalByUserIdRequest:
        self.guild_name = guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> WithdrawalByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WithdrawalByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WithdrawalByUserIdRequest]:
        if data is None:
            return None
        return WithdrawalByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "timeOffsetToken": self.time_offset_token,
        }


class ExportMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> ExportMasterRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExportMasterRequest]:
        if data is None:
            return None
        return ExportMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCurrentGuildMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentGuildMasterRequest:
        self.namespace_name = namespace_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentGuildMasterRequest]:
        if data is None:
            return None
        return GetCurrentGuildMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentGuildMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    settings: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentGuildMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_settings(self, settings: str) -> UpdateCurrentGuildMasterRequest:
        self.settings = settings
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentGuildMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentGuildMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "settings": self.settings,
        }


class UpdateCurrentGuildMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentGuildMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentGuildMasterFromGitHubRequest:
        self.checkout_setting = checkout_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentGuildMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentGuildMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeReceiveRequestsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReceiveRequestsRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DescribeReceiveRequestsRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> DescribeReceiveRequestsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiveRequestsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiveRequestsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeReceiveRequestsRequest]:
        if data is None:
            return None
        return DescribeReceiveRequestsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeReceiveRequestsByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReceiveRequestsByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DescribeReceiveRequestsByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> DescribeReceiveRequestsByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiveRequestsByGuildNameRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiveRequestsByGuildNameRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeReceiveRequestsByGuildNameRequest]:
        if data is None:
            return None
        return DescribeReceiveRequestsByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetReceiveRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    from_user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReceiveRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetReceiveRequestRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> GetReceiveRequestRequest:
        self.access_token = access_token
        return self

    def with_from_user_id(self, from_user_id: str) -> GetReceiveRequestRequest:
        self.from_user_id = from_user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReceiveRequestRequest]:
        if data is None:
            return None
        return GetReceiveRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "fromUserId": self.from_user_id,
        }


class GetReceiveRequestByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    from_user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReceiveRequestByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetReceiveRequestByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> GetReceiveRequestByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_from_user_id(self, from_user_id: str) -> GetReceiveRequestByGuildNameRequest:
        self.from_user_id = from_user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReceiveRequestByGuildNameRequest]:
        if data is None:
            return None
        return GetReceiveRequestByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "fromUserId": self.from_user_id,
        }


class AcceptRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    from_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcceptRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> AcceptRequestRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> AcceptRequestRequest:
        self.access_token = access_token
        return self

    def with_from_user_id(self, from_user_id: str) -> AcceptRequestRequest:
        self.from_user_id = from_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcceptRequestRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcceptRequestRequest]:
        if data is None:
            return None
        return AcceptRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "fromUserId": self.from_user_id,
        }


class AcceptRequestByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    from_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcceptRequestByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> AcceptRequestByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> AcceptRequestByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_from_user_id(self, from_user_id: str) -> AcceptRequestByGuildNameRequest:
        self.from_user_id = from_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcceptRequestByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcceptRequestByGuildNameRequest]:
        if data is None:
            return None
        return AcceptRequestByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "fromUserId": self.from_user_id,
        }


class RejectRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    access_token: str = None
    from_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RejectRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> RejectRequestRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_access_token(self, access_token: str) -> RejectRequestRequest:
        self.access_token = access_token
        return self

    def with_from_user_id(self, from_user_id: str) -> RejectRequestRequest:
        self.from_user_id = from_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RejectRequestRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RejectRequestRequest]:
        if data is None:
            return None
        return RejectRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "accessToken": self.access_token,
            "fromUserId": self.from_user_id,
        }


class RejectRequestByGuildNameRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    guild_model_name: str = None
    guild_name: str = None
    from_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RejectRequestByGuildNameRequest:
        self.namespace_name = namespace_name
        return self

    def with_guild_model_name(self, guild_model_name: str) -> RejectRequestByGuildNameRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> RejectRequestByGuildNameRequest:
        self.guild_name = guild_name
        return self

    def with_from_user_id(self, from_user_id: str) -> RejectRequestByGuildNameRequest:
        self.from_user_id = from_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RejectRequestByGuildNameRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RejectRequestByGuildNameRequest]:
        if data is None:
            return None
        return RejectRequestByGuildNameRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "fromUserId": self.from_user_id,
        }


class DescribeSendRequestsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSendRequestsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSendRequestsRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DescribeSendRequestsRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSendRequestsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSendRequestsRequest:
        self.limit = limit
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeSendRequestsRequest]:
        if data is None:
            return None
        return DescribeSendRequestsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSendRequestsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSendRequestsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSendRequestsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DescribeSendRequestsByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSendRequestsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSendRequestsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSendRequestsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeSendRequestsByUserIdRequest]:
        if data is None:
            return None
        return DescribeSendRequestsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSendRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    target_guild_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSendRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetSendRequestRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetSendRequestRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_target_guild_name(self, target_guild_name: str) -> GetSendRequestRequest:
        self.target_guild_name = target_guild_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSendRequestRequest]:
        if data is None:
            return None
        return GetSendRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_target_guild_name(data.get('targetGuildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "targetGuildName": self.target_guild_name,
        }


class GetSendRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    target_guild_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSendRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetSendRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> GetSendRequestByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_target_guild_name(self, target_guild_name: str) -> GetSendRequestByUserIdRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSendRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSendRequestByUserIdRequest]:
        if data is None:
            return None
        return GetSendRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_target_guild_name(data.get('targetGuildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "targetGuildName": self.target_guild_name,
            "timeOffsetToken": self.time_offset_token,
        }


class SendRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    target_guild_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SendRequestRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> SendRequestRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_target_guild_name(self, target_guild_name: str) -> SendRequestRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendRequestRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SendRequestRequest]:
        if data is None:
            return None
        return SendRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_target_guild_name(data.get('targetGuildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "targetGuildName": self.target_guild_name,
        }


class SendRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    target_guild_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SendRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> SendRequestByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_target_guild_name(self, target_guild_name: str) -> SendRequestByUserIdRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SendRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendRequestByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SendRequestByUserIdRequest]:
        if data is None:
            return None
        return SendRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_target_guild_name(data.get('targetGuildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "targetGuildName": self.target_guild_name,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    guild_model_name: str = None
    target_guild_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteRequestRequest:
        self.access_token = access_token
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteRequestRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_target_guild_name(self, target_guild_name: str) -> DeleteRequestRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteRequestRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRequestRequest]:
        if data is None:
            return None
        return DeleteRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_target_guild_name(data.get('targetGuildName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "guildModelName": self.guild_model_name,
            "targetGuildName": self.target_guild_name,
        }


class DeleteRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    guild_model_name: str = None
    target_guild_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> DeleteRequestByUserIdRequest:
        self.guild_model_name = guild_model_name
        return self

    def with_target_guild_name(self, target_guild_name: str) -> DeleteRequestByUserIdRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteRequestByUserIdRequest:
        self.duplication_avoider = duplication_avoider
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRequestByUserIdRequest]:
        if data is None:
            return None
        return DeleteRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_target_guild_name(data.get('targetGuildName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "guildModelName": self.guild_model_name,
            "targetGuildName": self.target_guild_name,
            "timeOffsetToken": self.time_offset_token,
        }