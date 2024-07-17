import logging
from logging import Logger
from logging.handlers import TimedRotatingFileHandler


def new_loging(name: str,
               cache: bool = True,
               format: str = "%(asctime)s %(name)s %(levelname)s %(message)s",
               level: int = logging.DEBUG,
               enable_file: bool = False,
               file_dir: str = None,
               file_name: str = "my_log.log",
               file_when: str = "midnight",
               file_interval: int = 1,
               file_backup_count: int = 7,
               file_suffix: str = "%Y-%m-%d",
               ) -> Logger:
    """
    创建日志记录器

    文件轮换策略：when 参数在 TimedRotatingFileHandler 类中用于指定日志文件轮换的时间点，它可以接受以下几种值：
         's'：按秒轮换日志文件，interval 参数设置为具体秒数。
         'm'：按分钟轮换日志文件，interval 参数设置为具体分钟数。
         'h'：按小时轮换日志文件，interval 参数设置为具体小时数。
         'midnight'：每天午夜时轮换日志文件，此时 interval 参数无意义，通常设置为 1。
         除了上述四个常用值，when 参数还可以接受其他时间和日期相关的字符串，它们会与 interval 参数一起工作来定义日志轮换的具体时间点。
         例如，如果 when 设置为'W0'（每周的第一天，通常是星期一），则日志文件将在每周一轮换。

         需要注意的是，对于 'midnight' 以外的 when 值，interval 参数是必需的，用于指定轮换的间隔时间

    :param name:
    :param cache: 是否使用缓存日志记录器, 如果使用，则不会重复创建，如果不使用，则会先移除缓存的实例，再创建新的
    :param format: 日志格式
    :param level: 日志级别，如 logging.DEBUG
    :param enable_file: 是否将日志输出到文件
    :param file_dir: 日志目录
    :param file_name: 文件路径, 如果是相对路径，则相对于当前启动类的所在目录，会创建日志
    :param file_when: 文件轮换策略
    :param file_interval:
    :param file_backup_count:
    :param file_suffix:
    :return:
    """
    # logging.basicConfig(
    #     level=level,
    #     format="%(asctime)s %(name)s %(levelname)s %(message)s ",
    #     datefmt='%Y-%m-%d  %H:%M:%S'
    # )
    is_cached = is_logger_cached(name)
    if cache:
        if is_cached:
            return logging.getLogger(name)
    else:
        # 不要缓存的，确保能创建全新的
        if is_cached:
            # 销毁
            destroy_logger(name)
    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    formatter = logging.Formatter(format)

    # 创建一个StreamHandler，用于将日志输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    if enable_file:
        # 创建一个FileHandler，用于将日志输出到文件
        # 创建一个TimedRotatingFileHandler 对象，每天轮换一次日志文件
        file_path = None
        if file_dir:
            file_path = f'{file_dir}/{file_name}'
        else:
            file_path = file_name
        file_handler = TimedRotatingFileHandler(file_path, when=file_when, interval=file_interval,
                                                backupCount=file_backup_count)
        file_handler.suffix = file_suffix  # 设置日志文件名后缀
        # 设置日志内容格式，如果不设置格式，默认就只有日志内容
        # 比如使用 log.debug("aaa"), 文件中就只有 aaa
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)
    return _logger


def destroy_logger(name: str):
    """ 销毁指定名称的 logging.Logger 实例 """
    logger = logging.getLogger(name)
    if name in logging.Logger.manager.loggerDict:
        del logging.Logger.manager.loggerDict[name]
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()


def is_logger_cached(name: str) -> bool:
    """检查指定名称的 logging.Logger 实例是否是缓存的"""
    return name in logging.Logger.manager.loggerDict
