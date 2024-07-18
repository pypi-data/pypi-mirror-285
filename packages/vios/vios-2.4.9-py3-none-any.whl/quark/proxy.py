# MIT License

# Copyright (c) 2021 YL Feng

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""
Abstract: **about proxy**
    - `Task`: interact with the `QuarkServer` from the view of a task
"""


import asyncio
import inspect
import json
import string
import sys
import time
from collections import defaultdict
from functools import cached_property
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from threading import current_thread

import numpy as np
from loguru import logger

QUARK = Path.home()/'quark'

try:
    with open(QUARK/'startup.json', 'r') as f:
        startup = json.loads(f.read())
        SYSTEMQ = str(Path(startup['site']).resolve())
        if SYSTEMQ.lower() not in sys.path:
            sys.path.append(SYSTEMQ)
except Exception as e:
    logger.error(str(e))
    startup = {}


def setlog(prefix: str = ''):
    logger.remove()
    root = Path.home()/f"Desktop/home/log/proxy/{prefix}"
    path = root/"{time:%Y-%m-%d}.log"
    level = "INFO"
    config = {'handlers': [{'sink': sys.stdout,
                            'level': level},
                           {'sink': path,
                            'rotation': '00:00',
                            'retention': '10 days',
                            'encoding': 'utf-8',
                            'level': level,
                            'backtrace': False, }]}
    # logger.add(path, rotation="20 MB")
    logger.configure(**config)


def debug(circuit: list = [(('Measure', 0), 'Q1001')], tid: int = 0):
    from .app import get_config_by_tid
    from .envelope import ccompile, initialize
    initialize(get_config_by_tid(tid))
    return ccompile(0, {}, circuit, signal='iq')


TABLE = string.digits+string.ascii_uppercase


def basen(number: int, base: int, table: str = TABLE):
    mods = []
    while True:
        div, mod = divmod(number, base)
        mods.append(mod)
        if div == 0:
            mods.reverse()
            return ''.join([table[i] for i in mods])
        number = div


def baser(number: str, base: int, table: str = TABLE):
    return sum([table.index(c)*base**i for i, c in enumerate(reversed(number))])


def dumpv(value):
    # print('ccccccccccccccccccccccc', value)
    # if type(value).__name__ in ['Waveform', 'WaveVStack']:
    #     sl = ShareableList([dump(value)])
    #     result = ('ShareableList', sl.shm.name)
    if isinstance(value, np.ndarray):
        sm = SharedMemory(create=True, size=value.nbytes)
        buf = np.ndarray(value.shape, dtype=value.dtype, buffer=sm.buf)
        buf[:] = value[:]
        result = sm, ('SharedMemory', sm.name, buf.shape, buf.dtype.str)
        # sm.close()
    else:
        result = '', value
    return result


def loadv(value):
    if isinstance(value, tuple) and value[0] == 'SharedMemory':
        name, shape, dtype = value[1:]
        shm = SharedMemory(name=name)
        buf = np.ndarray(shape=shape, dtype=dtype, buffer=shm.buf)
        return shm, buf
    else:
        return '', value


try:
    from IPython import get_ipython

    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell':
        from tqdm.notebook import tqdm  # jupyter notebook or qtconsole
    else:
        # ipython in terminal(TerminalInteractiveShell)
        # None(Win)
        # Nonetype(Mac)
        from tqdm import tqdm
except Exception as e:
    # not installed or Probably IDLE
    from tqdm import tqdm


class Progress(tqdm):
    bar_format = '{desc} {percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'

    def __init__(self, desc='test', total=100, postfix='running', disable: bool = False):
        super().__init__([], desc, total, ncols=None, colour='blue',
                         bar_format=self.bar_format, position=0, postfix=postfix, disable=disable)

    @property
    def max(self):
        return self.total

    @max.setter
    def max(self, value: int):
        self.reset(value)

    def goto(self, index: int):
        self.n = index
        self.refresh()

    def finish(self, success: bool = True):
        self.colour = 'green' if success else 'red'
        # self.set_description_str(str(success))


class Task(object):
    """tracking progress, get result and debug
    """

    handles = {}
    counter = defaultdict(lambda: 0)
    server = None

    def __init__(self, task: dict, timeout: float | None = None, plot: bool = False) -> None:
        """instantiate a task

        Args:
            task (dict): see **quark.app.submit**
            timeout (float | None, optional): timeout for the task. Defaults to None.
            plot (bool, optional): plot result in `quark studio` if True. Defaults to False.
        """
        self.task = task
        self.timeout = timeout
        self.plot = plot

        self.data: dict[str, np.ndarray] = {}  # retrieve data from server
        self.meta = {}  # metainfo like axis
        self.index = 0  # index of data already retrieved
        self.last = 0  # last index of retrieved data

        self.thread = current_thread().name

    @cached_property
    def name(self):
        return self.task['metainfo'].get('name', 'Unknown')

    @cached_property
    def ctx(self):
        return self.step(-9, 'ctx')

    def run(self):
        """submit the task to the `QuarkServer`
        """
        self.stime = time.time()  # start time
        try:
            circuit = self.task['taskinfo']['CIRQ']
            if isinstance(circuit, list) and callable(circuit[0]):
                circuit[0] = inspect.getsource(circuit[0])
        except Exception as e:
            logger.error(f'Failed to get circuit: {e}')
        self.tid = self.server.submit(self.task)

    def cancel(self):
        """cancel the task
        """
        self.server.cancel(self.tid)
        # self.clear()

    def result(self):
        """result of the task
        """
        meta = True if not self.meta else False
        res = self.server.fetch(self.tid, start=self.index, meta=meta)

        if isinstance(res, str):
            return self.data
        elif isinstance(res, tuple):
            if isinstance(res[0], str):
                return self.data
            data, self.meta = res
        else:
            data = res
        self.last = self.index
        self.index += len(data)
        # data.clear()
        self.process(data)

        if callable(self.plot):
            self.plot(self, not meta)
            # self.plot(not meta)

        return self.data

    def status(self, key: str = 'runtime'):
        if key == 'runtime':
            return self.server.track(self.tid)
        elif key == 'compile':
            return self.server.apply('status', user='task')
        else:
            return 'supported arguments are: {rumtime, compile}'

    def report(self):
        return self.server.report(self.tid)

    def step(self, index: int, stage: str = 'raw'):
        """step details

        Args:
            index (int): step index
            stage (str, optional): stage name. Defaults to 'raw'.

        Examples: stage values
            - ini: original instruction
            - raw: preprocessed instruction
            - ctx: compiler context
            - debug: raw data returned from devices
            - trace: time consumption for each channel

        Returns:
            _type_: _description_
        """
        if stage in ['ini', 'raw', 'ctx', 'byp']:
            return self.server.review(self.tid, index)[stage]
        elif stage in ['debug', 'trace']:
            return self.server.track(self.tid, index)[stage]

    def process(self, data: list[dict]):
        for dat in data:
            for k, v in dat.items():
                if k in self.data:
                    self.data[k].append(v)
                else:
                    self.data[k] = [v]

    def update(self):
        try:
            self.result()
        except Exception as e:
            logger.error(f'Failed to fetch result: {e}')

        status = self.status()['status']

        if status in ['Failed', 'Canceled']:
            self.stop(self.tid, False)
            return True
        elif status in ['Running']:
            self.progress.goto(self.index)
            return False
        elif status in ['Finished', 'Archived']:
            self.progress.goto(self.progress.max)
            if hasattr(self, 'app'):
                self.app.save()
            self.stop(self.tid)
            self.result()
            return True

    def clear(self):
        self.counter.clear()
        for tid, handle in self.handles.items():
            self.stop(tid)

    def stop(self, tid: int, success: bool = True):
        try:
            self.progress.finish(success)
            self.handles[tid].cancel()
        except Exception as e:
            pass

    def bar(self, interval: float = 2.0, disable: bool = False):
        """task progress. 

        Tip: tips
            - Reduce the interval if result is empty.
            - If timeout is not None or not 0, task will be blocked, otherwise, the task will be executed asynchronously.

        Args:
            interval (float, optional): time period to retrieve data from `QuarkServer`. Defaults to 2.0.

        Raises:
            TimeoutError: if TimeoutError is raised, the task progress bar will be stopped.
        """
        while True:
            try:
                status = self.status()['status']
                if status in ['Pending']:
                    time.sleep(interval)
                    continue
                elif status == 'Canceled':
                    return 'Task canceled!'
                else:
                    self.progress = Progress(desc=self.name,
                                             total=self.report()['size'],
                                             postfix=self.thread, disable=disable)
                    break
            except Exception as e:
                logger.error(
                    f'Failed to get status: {e},{self.report()}')

        if isinstance(self.timeout, float):
            while True:
                if self.timeout > 0 and (time.time() - self.stime > self.timeout):
                    msg = f'Timeout: {self.timeout}'
                    logger.warning(msg)
                    raise TimeoutError(msg)
                time.sleep(interval)
                if self.update():
                    break
        else:
            self.progress.clear()
            self.refresh(interval)
        self.progress.close()

    def refresh(self, interval: float = 2.0):
        self.progress.display()
        if self.update():
            self.progress.display()
            return
        self.handles[self.tid] = asyncio.get_running_loop(
        ).call_later(interval, self.refresh, *(interval,))


def transpile(task: dict):
    quafuos = str(Path.home()/'Desktop/qusteed/0.2.4')
    if quafuos not in sys.path:
        print('adding quafuos', quafuos)
        sys.path.append(quafuos)

    circuit = task.get('circuit', '')
    tid = task['tid']
    qasm = ''
    if not isinstance(circuit, list):
        from ._cloud import openqasm_to_qlisp
        # if task.get('compile', True):
        from qusteedAPIs import call_transpiler_api
        logger.info(f"\n{'>'*36}[{tid}]circuit:\n{circuit}\n{'>'*36}")
        qasm, final_qubit2cbit, compiled_circuit_information = call_transpiler_api(
            input_circuit=circuit,
            compile=task.get('compile', True),
            backend=task.get('chip', ''))
        # import compiler
        # transpile
        # else:
        #     print('nononononoonoo compile')
        #     qasm = circuit
        mapping = {}
        try:
            with open(Path.home()/'Desktop/home/mapping.json', 'r') as f:
                mapping = json.loads(f.read())
        except Exception as e:
            if task['chip'] == 'Haituo':
                mapping[task['chip']] = {
                    str(i): f'Q{i+39}' for i in range(156)}
            else:
                mapping[task['chip']] = {str(i): f'Q{i+0}' for i in range(156)}
        QMAP = mapping[task['chip']]

        circuit, qubits = openqasm_to_qlisp(qasm, QMAP=QMAP)

    qlisp = ',\n'.join([str(op) for op in circuit])
    logger.info(
        f"\n{'>'*36}[{tid}]qasm:\n{qasm}\n{'>'*36}[{tid}]qlisp:\n[{qlisp}]")

    measure = []
    for ops in circuit:
        if isinstance(ops[0], tuple) and ops[0][0] == 'Measure':
            measure.append((ops[0][1], ops[1]))
    return qasm, [circuit], measure


def update(backend: str, info: dict, token: str = ''):

    quafuos = str(Path.home()/'Desktop/qusteed/0.2.4')
    if quafuos not in sys.path:
        print('adding quafuos', quafuos)
        sys.path.append(quafuos)
    with open(Path.home()/f'Desktop/home/cfg/{backend}.json', 'w') as f:
        f.write(json.dumps(info, indent=4))
    from qusteedAPIs import call_local_backend_api
    call_local_backend_api(backend=backend, chip_info_dict=info)
    logger.warning(f'database of {backend} updated!')

    try:
        from ._cloud import update_chip_info_of_quafu
        msg = update_chip_info_of_quafu(backend.lower(), info, token)
        logger.warning(f'chip info of quafu[{backend.lower()}] updated!')
    except Exception as e:
        msg = f'Failed to update chip info of quafu, {e}'
        logger.critical(msg)

    return {'compiler': f'database of {backend} updated!', 'quafu': msg}


class QuarkProxy(object):

    def __init__(self) -> None:
        from .app import login

        self.server = login()
        setlog()

    def submit(self, task: dict, block: bool = False):
        from .app import submit

        # by server
        # logger.info(f'task will be executed on local machine: {chip}!')
        logger.warning(f'\n\n\n{"#"*80} task start to run ...\n')

        try:
            from home.ylfeng.cloud import get_bias_of_coupler
            bias = get_bias_of_coupler()
        except Exception as e:
            bias = []
            logger.error(f'Failed to get bias of coupler, {e}!')
        circuit = [bias+c for c in task['taskinfo']['CIRQ']]
        task['taskinfo']['CIRQ'] = circuit

        qlisp = ',\n'.join([str(op) for op in circuit[0]])
        qasm = task['metainfo']['coqis']['qasm']
        logger.info(f"\n{'>'*36}qasm:\n{qasm}\n{'>'*36}qlisp:\n[{qlisp}]")

        t: Task = submit(task, block=block)  # local machine
        if block:
            t.bar(0.2, disable=False)  # if block is True
        eid = task['metainfo']['coqis']['eid']
        user = task['metainfo']['coqis']['user']
        logger.warning(f'task {t.tid}[{eid}, {user}] will be executed!')

        return t.tid

    def cancel(self, tid: int):
        return self.server.cancel(tid)

    def status(self, tid: int = 0):
        pass

    def result(self, tid: int, raw: bool = False):
        from .app import get_data_by_tid
        try:
            result = get_data_by_tid(tid, 'count')
            return result if raw else self.process(result)
        except Exception as e:
            return f'No data found for {tid}!'

    @classmethod
    def process(cls, result: dict, dropout: bool = False):
        def _delete_dict(ret: dict, num: int = 0):
            while num > 0:
                tmp = np.cumsum(list(ret.values()))
                ran_num = np.random.randint(tmp[-1]+1)
                ran_pos = np.searchsorted(tmp, ran_num)
                ret[list(ret.keys())[ran_pos]] -= 1
                if ret[list(ret.keys())[ran_pos]] == 0:
                    ret.pop(list(ret.keys())[ran_pos], 0)
                num -= 1

        meta = result['meta']
        coqis = meta.get('coqis', {})
        status = 'Failed'
        if meta['status'] in ['Finished', 'Archived']:
            try:
                # data: list[dict] = result['data']['count']
                data: list[np.ndarray] = result['data']['count']
                status = 'Finished'
            except Exception as e:
                logger.error(f'Failed to postprocess result: {e}')

        dres, cdres = {}, {}
        if status == 'Finished':
            for dat in data:
                # for k, v in dat.items():  # dat[()][0]
                #     dres[k] = dres.get(k, 0)+v
                for kv in dat:
                    if kv[-1] < 0:
                        continue
                    base = tuple(kv[:-1]-1)  # from 1&2 to 0&1
                    dres[base] = dres.get(base, 0)+int(kv[-1])

            try:
                if dropout:
                    shots = meta['other']['shots'] * \
                        len(meta['axis']['repeat']['repeat'])
                    _delete_dict(dres, shots - (shots//1000)*1000)
            except Exception as e:
                logger.error(f'Failed to dropout: {e}')

            try:
                if meta['coqis']['correct']:
                    from home.ylfeng.cloud import correct_readout
                    cdres = correct_readout(dres, meta['other']['measure'])
                else:
                    cdres = {}
            except Exception as e:
                cdres = dres
                logger.error(f'Failed to correct readout, {e}!')

        ret = {'count': {''.join((str(i) for i in k)): v for k, v in dres.items()},
               'corrected': {''.join((str(i) for i in k)): v for k, v in cdres.items()},
               'transpiled': coqis.get('qasm', ''),
               'qlisp': coqis.get('qlisp', ''),
               'tid': meta['tid'],
               'error': meta.get('error', ''),
               'status': status,
               'created': meta['created'],
               'finished': meta['finished'],
               }
        return ret

    def snr(self, data):
        return data
