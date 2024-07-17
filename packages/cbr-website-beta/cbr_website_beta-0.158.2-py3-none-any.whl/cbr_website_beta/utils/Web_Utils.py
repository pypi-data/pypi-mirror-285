import os

from osbot_utils.utils.Http import current_host_online


class Web_Utils:

    @staticmethod
    def currently_online():
        return current_host_online()

    # @staticmethod
    # def current_execution_env():
    #     return os.environ.get('EXECUTION_ENV', 'LOCAL')

    @staticmethod
    def running_in_aws():
        return 'AWS_EXECUTION_ENV' in os.environ

    @staticmethod
    def in_aws_code_build():
        return 'CODEBUILD_BUILD_ID' in os.environ