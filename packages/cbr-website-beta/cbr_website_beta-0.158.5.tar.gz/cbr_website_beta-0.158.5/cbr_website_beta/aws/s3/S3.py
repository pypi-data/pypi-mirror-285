from osbot_aws.AWS_Config                               import aws_config
from osbot_aws.apis.S3                                  import S3
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.decorators.methods.remove_return_value import remove_return_value
from osbot_utils.utils.Files                            import file_extension

S3_DEFAULT_FILE_CONTENT_TYPE = 'binary/octet-stream'
S3_HTML_PAGE_CONTENT_TYPE    = 'text/html; charset=utf-8'
S3_FILES_CONTENT_TYPES       = { '.js'  : 'application/javascript; charset=utf-8',
                                 '.jpg' : 'image/jpeg'                           ,
                                 '.jpeg': 'image/jpeg'                           ,
                                 '.png' : 'image/png'                            ,
                                 '.txt' : 'text/plain; charset=utf-8'            ,
                                 '.pdf' : 'application/pdf'                      ,
                                 '.html': 'text/html; charset=utf-8'             ,
                                 '.css' : 'text/css; charset=utf-8'              ,
                                 '.svg' : 'image/svg+xml'                        ,
                                 '.gif' : 'image/gif'                            ,
                                 '.webp': 'image/webp'                           ,
                                 '.json': 'application/json; charset=utf-8'      ,
                                 '.xml' : 'application/xml; charset=utf-8'       ,
                                 '.zip' : 'application/zip'                      ,
                                 '.mp3' : 'audio/mpeg'                           ,
                                 '.mp4' : 'video/mp4'                            ,
                                 '.avi' : 'video/x-msvideo'                      ,
                                 '.mov' : 'video/quicktime'                      }

# todo: add this to the official OSBot_AWS S3 class
class S3(S3):

    @cache_on_self
    def client(self):
        # todo: understand the impact of having to add the endpoint_url below
        #       we needed this because (some, not all, which is really weird) buckets
        #       were throwing this error when creating the pre-signed URL
        #       <Code>SignatureDoesNotMatch</Code>
        #           <Message>The request signature we calculated does not match the signature you provided. Check your key and signing method.</Message>
        #       this is the comment that gave the solution https://github.com/boto/boto3/issues/1149#issuecomment-793737086
        import boto3
        region_name  = aws_config.region_name()
        #endpoint_url = f'https://s3.{region_name}.amazonaws.com'            # this was causing issues uploading files
        #return boto3.client('s3', region_name=region_name,  endpoint_url=endpoint_url)
        return boto3.client('s3', region_name=region_name)

    def create_pre_signed_url(self, bucket_name, object_name, operation='get_object', expiration=3600):     # 3600 is one hour (60 seconds * 60 minutes)
        response = self.client().generate_presigned_url(operation, Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=expiration)
        return response
    def file_content_type(self, bucket, key):
        return self.file_details(bucket, key).get('ContentType')

    def file_content_type_update(self, bucket, key, metadata, content_type):
        file_copy_kwargs = dict(bucket_source      = bucket      ,
                                key_source         = key         ,
                                bucket_destination = bucket      ,
                                key_destination    = key         ,
                                metadata           = metadata    ,      # in S3 we can't update the content type with also updating the metadata
                                content_type       = content_type)      # i guess this is related to the fact that the content_type is stored as a metadata item
        return self.file_copy(**file_copy_kwargs)

    @remove_return_value('ResponseMetadata')
    def file_copy(self, bucket_source, key_source, bucket_destination, key_destination, metadata=None, content_type=None):
        kwargs_file_copy = dict(CopySource = {'Bucket': bucket_source, 'Key': key_source},
                                Bucket     = bucket_destination                          ,
                                Key        = key_destination                             )
        if metadata is not None:
            kwargs_file_copy['Metadata'         ] = metadata
            kwargs_file_copy['MetadataDirective'] = 'REPLACE'
        if content_type is not None:
            kwargs_file_copy['ContentType'] = content_type
        return self.client().copy_object(**kwargs_file_copy)

    def file_metadata(self, bucket, key):
        return super().file_details(bucket, key).get('Metadata')

    def file_metadata_update(self, bucket, key, metadata):
        file_copy_kwargs = dict(bucket_source      = bucket  ,
                                key_source         = key     ,
                                bucket_destination = bucket  ,
                                key_destination    = key     ,
                                metadata           = metadata)
        return self.file_copy(**file_copy_kwargs)

    # add support for changing the content type

    def file_upload_to_key(self, file, bucket, key, set_content_type=True):
        extra_args   = None
        if set_content_type:
            extension = file_extension(file)
            if extension:
                content_type = S3_FILES_CONTENT_TYPES.get(extension)
                if content_type:
                    extra_args = {'ContentType': content_type}
        upload_args = [file, bucket, key, extra_args]
        self.client().upload_file(*upload_args)                                # upload file
        return True                                                             # return true (if succeeded)