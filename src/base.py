#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Bruce_H_Cottman"
__license__ = "MIT License"
__coverage__ = 0.98


from abc import ABC
from functools import wraps
# from typing import Dict, List
from loguru import logger
# import pydot_ng as pydot
# from IPython.display import Image, display
import sys, os.path
import yaml
from attrdict import AttrDict
# import numpy as np
# from matplotlib import pyplot as plt
# import timeit, math
# from tqdm import tqdm
# import multiprocessing as mp
# from numba import jit

#
import warnings

warnings.filterwarnings("ignore")


def logger(*a,**k):
    """
        Hide most of the paso machinery, so that developer focuses on their function or method.

        Parameters:
            array: (boolean) False
                Pass a Pandas dataframe (False) or numpy array=True.  Mainly for compatibility
                with scikit which requires arrays.

        Parm/wrap Class Instance attibutes: these are attibutes of object_.fun (sef.x) set in this wrapper, if present in Parameter file

    """

    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            _fun_name = fun.__name__

            result = fun(*args, **kwargs)
            # post
            logger.info('{} decotator invoked'.format(k))
            logger.info('{} func invoked'.format(kwargs))
            return result

            return wrapper

        return decorator


### Param class
class Param(object):
    """
    Read in from file(s) the parameters for this service.

        base.yml
        experiment-1 (optional)
        ....         (optional)

        Class Attributes:

            Param.filepath
                init: None

            Param.parameters_D  (dict) Parameter dictionary resulting from reading in ``filepath``.
                init: None


            Setting Class attribute to ``None`` means it initialized by whatever method set it.

    """

    gfilepath = None
    parameters_D = None

    def __init__(self, filepath="", verbose=True):
        """
        Read-in a parameter file on ``filepath`.

        Parameters:
            None

        Returns:
            self (definition of __init__ behavior).

        Note:
            Currently bootstrap to <name>.yaml or from attribute ``experiment_environment``
            from default ``../parameters/base.yaml``  thus any <na00me>.yaml can be used
            without change to current code. Only new code need be added to
            support <nth name>.yaml.

            Notice instance is different on call to class init but resulting
            parameter dictionary is always the same as the file specified by
            parameter  ``experiment_environment``. This means class parameters
            can be called from anywhere to give the same parameters and values. so long a Parm file path

            It also means if dafault.yaml or underlying file specified by
            `experiment_environment`` is changed, parameters class instance is set
            again with a resulting new parameters dictionary.

        Example:

            >>> p = Param.parameter_D
            >>> p['a key']

        """
        if filepath == "":
            filepath = "../parameters/base.yaml"

        Param.gfilepath = filepath
        Param.parameters_D = self._read_parameters(filepath)
        self.parameters_D = Param.parameters_D

    def _read_parameters(self, filepath):
        if os.path.exists(filepath):
            with open(filepath) as f:
                config = yaml.load(f)
                return AttrDict(config)
        else:
            raise_PasoError(
                "read_parameters: The file does not exist:{}".format(filepath)
            )


### Paso class
class Paso(object):
    """
    Creates
        1. Log: default name paso
        2. parameter file : default: '../parameters/base.yaml'
        3. list of pasoes invoked.

        Parameters:
            log_name (str) 'paso'
            verbose: (boolean) True

        Class Attributes:
            pipeLine (list)
                init: []

        Class Instance Attributes::
            self.parameters = None
            self.log_name = log_name
            self.log_file = log_file
            validate_bool_kwarg(verbose, "verbose")
            self.verbose = verbose

    """

    pipeLine = []

    def __init__(
        self, verbose=True, log_name="paso", log_file="", parameters_filepath=""
    ):

        self.log = None

        if parameters_filepath == "":
            self.parameters_filepath = "../parameters/base.yaml"
        else:
            self.parameters_filepath = parameters_filepath

        self.parameters = None
        self.log_name = log_name
        self.log_file = log_file
        validate_bool_kwarg(verbose, "verbose")
        self.verbose = verbose

    def __enter__(self):
        return self.startup()

    def __exit__(self, *args, **kwargs):
        return self.shutdown()


    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    @property
    def log_name(self):
        return self._log_name

    @log_name.setter
    def log_name(self, value):
        self._log_name = value

    @property
    def log_file(self):
        return self._log_file

    @log_file.setter
    def log_file(self, value):
        self._log_file = value

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def parameters_filepath(self):
        return self._parameters_filepath

    @parameters_filepath.setter
    def parameters_filepath(self, value):
        self._parameters_filepath = value

    def startup(self):
        Log(verbose=self.verbose).log(log_name=self._log_name, log_file=self._log_file)
        if self.verbose:
            logger.info("========================================")
        Param(filepath=self.parameters_filepath, verbose=self.verbose)
        if self.verbose:
            logger.info("Read in parameter file: {}".format(self.parameters_filepath))
        #        self.flush()
        Paso.pipeLine.append(["Startup Paso", "square", " "])
        return self

    def shutdown(self):
        Paso.pipeLine.append(["Shutdown Paso", "square", " "])
        if "paso" in Log.log_names:
            del Log.log_names["paso"]
        if "paso" in Log.log_ids:
            logger.remove(Log.log_ids["paso"])
            del Log.log_ids["paso"]

        logger.add(
            sys.stdout, format=" default {time:D.M.YYYY HH:mm:ss} {level} {message}"
        )
        return self

    def display_DAG(self):
        """
        Displays pipeline structure in a jupyter notebook.

        Param:
            pipe (list of tuple): (node_name,shape,edge_label

            Returns:
                graph (pydot.Dot): object_ representing upstream pipeline paso(es).
        """
        graph = self._pasoLine_DAG(_PiPeLiNeS_)
        plt = Image(graph.create_png())
        display(plt)
        return self

    def DAG_as_png(self, filepath):
        """
        Saves pipeline DAG to filepath as png file.

        Parameters:
            pipe (list of tuple): (node_name,shape,edge_label

            filepath (str): filepath to which the png with pipeline visualization should be persisted

        Returns:
            graph (pydot.Dot): object_ representing upstream pipeline paso(es).
        """
        graph = self._pasoLine_DAG(_PiPeLiNeS_)
        graph.write(filepath, format="png")
        return self

    def _pasoLine_DAG(self, pipe):
        """
        DAG of the pasoline.

        Parameters:
            pipe (list of tuple): (node_name,shape,edge_label

        Returns:
            graph (pydot.Dot): object_ representing upstream pipeline paso(es).

        """
        graph = pydot.Dot()
        node_prev = None
        label_prev = "NA"
        for p in pipe:
            if p[1] == "":
                node = pydot.Node(p[0])
            else:
                node = pydot.Node(p[0], shape=p[1])

            graph.add_node(node)

            if node != node_prev and node_prev != None:
                graph.add_edge(pydot.Edge(node_prev, node, label=label_prev))
            label_prev = p[2]
            node_prev = node
        return graph


