from heaserver.service.db.aws import AWSPermissionContext, is_account_owner
from heaserver.service.db.awsaction import S3_LIST_BUCKET, S3_CREATE_BUCKET, S3_DELETE_BUCKET, S3_GET_BUCKET_TAGGING, S3_PUT_BUCKET_TAGGING
from heaobject.bucket import AWSBucket
from heaobject.root import DesktopObject, Permission
from aiohttp.web import Request


class S3BucketPermissionsContext(AWSPermissionContext[AWSBucket]):
    def __init__(self, request: Request, volume_id: str, **kwargs):
        actions = [S3_LIST_BUCKET, S3_CREATE_BUCKET, S3_DELETE_BUCKET]
        super().__init__(request=request, volume_id=volume_id, actions=actions, **kwargs)

    async def get_attribute_permissions(self, obj: DesktopObject, attr: str) -> list[Permission]:
        if attr == 'tags' and not await is_account_owner(request=self.request, volume_id=self.volume_id):
            return await self._simulate_perms(obj, [S3_GET_BUCKET_TAGGING, S3_PUT_BUCKET_TAGGING])
        else:
            return await super().get_attribute_permissions(obj, attr)

    def _caller_arn(self, obj: AWSBucket):
        return f'arn:aws:s3:::{obj.bucket_id}'
