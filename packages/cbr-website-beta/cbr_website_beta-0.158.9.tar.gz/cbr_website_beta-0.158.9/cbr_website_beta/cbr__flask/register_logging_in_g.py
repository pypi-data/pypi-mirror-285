# import logging
#
# from flask import g
# from cbr_website_beta.utils.Site_Utils import Site_Utils
#
# LOGGING_LEVEL_FOR_G     = logging.DEBUG
# #LOGGING_FORMAT_FOR_G    = '%(levelname)s: %(message)s'
# LOGGING_FORMAT_FOR_G    = '%(message)s'
# LOGGING_FORMATTER_FOR_G = logging.Formatter(LOGGING_FORMAT_FOR_G)
#
# from flask.globals import _app_ctx_stack
#
# class Logging_in_G(logging.Handler):
#     def emit(self, record):
#         if _app_ctx_stack.top is not None:
#             if hasattr(g, 'log_list'):
#                 g.log_list = getattr(g, 'log_list', [])
#                 #record['level'] = self.level
#                 g.log_req_count = len(g.log_list_all)
#
#                 if type(record.msg) is dict:
#                     record.msg['level'] = record.levelname
#                     record.msg['index'] = g.log_req_count
#                 g.log_list.append(record.msg)
#                 g.log_list_all.append(record.msg)
#
#
#
# def register_logging_in_g(app):
#     if Site_Utils.running_in_pytest():
#         return
#
#     logging_in_handler = Logging_in_G()
#     logging_in_handler.setLevel     (LOGGING_LEVEL_FOR_G   )
#     logging_in_handler.setFormatter(LOGGING_FORMATTER_FOR_G)
#     app.logger.addHandler(logging_in_handler)
#     return app