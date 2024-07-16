#
# GAMS - General Algebraic Modeling System Python API
#
# Copyright (c) 2017-2024 GAMS Development Corp. <support@gams.com>
# Copyright (c) 2017-2024 GAMS Software GmbH <support@gams.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import importlib
import sys
from cerberus import Validator
from gams.connect.agents.pythoncode import PythonCode
from gams.connect.agents.connectagent import ConnectAgent
from gams.connect.errors import GamsConnectException
from gams.control import GamsWorkspace
import gams.transfer as gt


class ConnectDatabase(object):
    def __init__(self, system_directory, container=None, ecdb=None):
        """
        @brief constructor
        @param system_directory GAMS system directory
        @param container Instance of gams.transfer.Container to be used. A new and empty instance is created when omitted (optional)
        @param ecdb Embedded code GAMS database (optional)
        """
        self._system_directory = system_directory
        self._ecdb = ecdb
        self._ws = GamsWorkspace(system_directory=self._system_directory)
        if container is None:
            self._container = gt.Container(system_directory=self._system_directory)
        else:
            self._container = container
        if self._ecdb:
            ecdb._cdb = self

    def __del__(self):
        pass

    def _exec_python_code(self, task):
        transform = PythonCode(self._system_directory, self, task)
        instructions = transform.execute()
        for t2 in instructions:
            self.exec_task(t2)

    def print_log(self, msg):
        if self._ecdb:
            self._ecdb.printLog(msg)
        else:
            print(msg)
            sys.stdout.flush()

    def exec_task(self, task):
        root = list(task.keys())
        if len(root) != 1:
            raise GamsConnectException(
                f"Invalid task definition with {len(root)} root keys instead of 1."
            )
        task_class_name = root[0]
        task = task[task_class_name]
        if task_class_name is None:
            raise GamsConnectException("Task is missing a class name")

        if task_class_name == "PythonCode":
            v = Validator(PythonCode.cerberus())
            if not v.validate(task):
                raise GamsConnectException(
                    f"Validation of input for agent 'PythonCode' failed: {v.errors}"
                )
            self._exec_python_code(task)
        else:
            try:
                mod = importlib.import_module(
                    "gams.connect.agents." + task_class_name.lower()
                )
            except ModuleNotFoundError as e:
                if (
                    e.name != "gams.connect.agents." + task_class_name.lower()
                ):  # the connect agent module itself was found but an import in the source itself did fail
                    raise GamsConnectException(str(e), traceback=True)
                mod = importlib.import_module(task_class_name.lower())
            task_class = vars(mod)[task_class_name]
            task_schema = task_class.cerberus()
            v = Validator(task_schema)
            if not v.validate(task):
                raise GamsConnectException(
                    f"Validation of input for agent '{task_class_name}' failed: {v.errors}"
                )

            if not issubclass(task_class, ConnectAgent):
                raise GamsConnectException(
                    f"Task class '{task_class_name}' has to be derived from gams.connect.agents.connectagent.ConnectAgent",
                    traceback=True,
                )
            task_instance = task_class(self._system_directory, self, task)
            task_instance.open()
            task_instance.execute()
            task_instance.close()

    def _get_container(self):
        return self._container

    container = property(_get_container)

    def _get_ecdb(self):
        return self._ecdb

    ecdb = property(_get_ecdb)
