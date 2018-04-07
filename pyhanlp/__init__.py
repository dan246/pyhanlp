# -*- coding:utf-8 -*-
# Author：hankcs, Hai Liang Wang<hailiang.hl.wang@gmail.com>
# Date: 2018-03-18 19:49
from __future__ import division
from __future__ import print_function

import os

from jpype import *

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
if sys.version_info[0] < 3:
    # noinspection PyUnresolvedReferences,PyCompatibility
    reload(sys), sys.setdefaultencoding("utf-8")


def _start_jvm_for_hanlp():
    global STATIC_ROOT, hanlp_installed_data_version, HANLP_JAR_PATH, PATH_CONFIG, HANLP_JAR_VERSION, HANLP_DATA_PATH
    # Get ENV
    ENVIRON = os.environ.copy()
    # Load variables in Environment
    if "HANLP_VERBOSE" in ENVIRON:
        HANLP_VERBOSE = int(ENVIRON["HANLP_VERBOSE"])
    else:
        HANLP_VERBOSE = 0

    if "HANLP_STATIC_ROOT" in ENVIRON:
        STATIC_ROOT = ENVIRON["HANLP_STATIC_ROOT"]
        if HANLP_VERBOSE:
            print('使用环境变量 HANLP_STATIC_ROOT={}'.format(STATIC_ROOT))

        def hanlp_installed_data_version():
            return '手动安装'
    else:
        from pyhanlp.static import STATIC_ROOT, hanlp_installed_data_version
    if "HANLP_JAR_PATH" in ENVIRON:
        HANLP_JAR_PATH = ENVIRON["HANLP_JAR_PATH"]
        if HANLP_VERBOSE:
            print('使用环境变量 HANLP_JAR_PATH={}'.format(HANLP_JAR_PATH))
    else:
        from pyhanlp.static import HANLP_JAR_PATH
    if "HANLP_JVM_XMS" in ENVIRON:
        HANLP_JVM_XMS = ENVIRON["HANLP_JVM_XMS"]
    else:
        HANLP_JVM_XMS = "1g"
    if "HANLP_JVM_XMX" in ENVIRON:
        HANLP_JVM_XMX = ENVIRON["HANLP_JVM_XMX"]
    else:
        HANLP_JVM_XMX = "1g"
    if os.path.exists(HANLP_JAR_PATH) and os.path.exists(STATIC_ROOT):
        PATH_CONFIG = os.path.join(STATIC_ROOT, 'hanlp.properties')
        HANLP_JAR_VERSION = os.path.basename(HANLP_JAR_PATH)[len('hanlp-'):-len('.jar')]
        HANLP_DATA_PATH = os.path.join(STATIC_ROOT, 'data')

        if HANLP_VERBOSE:
            print("加载 HanLP jar [%s] ..." % HANLP_JAR_PATH)
            print("加载 HanLP config [%s/hanlp.properties] ..." % (STATIC_ROOT))
            print("加载 HanLP data [%s/data] ..." % (STATIC_ROOT))
    else:
        raise BaseException(
            "Error: %s or %s does not exists." %
            (HANLP_JAR_PATH, STATIC_ROOT))
    JAVA_JAR_CLASSPATH = "-Djava.class.path=%s%s%s" % (
        HANLP_JAR_PATH, os.pathsep, STATIC_ROOT)
    if HANLP_VERBOSE: print("设置 JAVA_JAR_CLASSPATH [%s]" % JAVA_JAR_CLASSPATH)
    # 启动JVM
    startJVM(
        getDefaultJVMPath(),
        JAVA_JAR_CLASSPATH,
        "-Xms%s" %
        HANLP_JVM_XMS,
        "-Xmx%s" %
        HANLP_JVM_XMX)


_start_jvm_for_hanlp()


def attach_jvm_to_thread():
    """
    use attachThreadToJVM to fix multi-thread issues: https://github.com/hankcs/pyhanlp/issues/7
    """
    if not isThreadAttachedToJVM():
        attachThreadToJVM()


class SafeJClass(object):
    def __init__(self, proxy):
        """
        JClass的线程安全版
        :param proxy: Java类的完整路径，或者一个Java对象
        """
        self._proxy = JClass(proxy) if type(proxy) is str else proxy

    def __getattr__(self, attr):
        attach_jvm_to_thread()
        return getattr(self._proxy, attr)

    def __call__(self, *args):
        if args:
            proxy = self._proxy(*args)
        else:
            proxy = self._proxy()
        return SafeJClass(proxy)


# API列表
CustomDictionary = SafeJClass('com.hankcs.hanlp.dictionary.CustomDictionary')
HanLP = SafeJClass('com.hankcs.hanlp.HanLP')
PerceptronLexicalAnalyzer = SafeJClass('com.hankcs.hanlp.model.perceptron.PerceptronLexicalAnalyzer')
