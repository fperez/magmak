#!/usr/bin/env python
"""JupyMagmaK - A Magma Kernel for Jupyter
"""

# Stdlib imports
import sys


# IPython imports
from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelbase import Kernel
from IPython.core.interactiveshell import ExecutionInfo, ExecutionResult


# Dbg - to get logging out to the screen for debugging... 
import logging

logging.basicConfig()
logger = logging.getLogger('Magma')
logger.setLevel(logging.DEBUG)


# In reality this will be pulled from sage.magma
class Magma:
    def eval(self, code):
        if code.strip().startswith('boom'):
            error = 'aaah!!!'
            output = f'ERROR: <{code}>'
        else:
            error = None
            output = f"Output from <{code}>"
        return (output, error)


class MagmaKernel(Kernel):
    # Kernel info fields
    implementation = 'Magma'
    implementation_version = '0.1'
    language_info = {
        'name': 'Magma',
        'version': sys.version.split()[0],
        'mimetype': 'text/x-magma',
        'codemirror_mode': {
            'name': 'python',
            'version': sys.version_info[0]
        },
        'pygments_lexer': 'python',
        'nbconvert_exporter': 'python',
        'file_extension': '.magma'
    }

    banner = "Basic Magma Jupyter Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.magma = Magma()


    def process_output(self, output):
        if not self.silent:
            # Send standard output
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)


    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        self.silent = silent
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted = False
        try:
            # Note: timeout=None tells IREPLWrapper to do incremental
            # output.  Also note that the return value from
            # run_command is not needed, because the output was
            # already sent by IREPLWrapper.
            output, error = self.magma.eval(code.rstrip())
            self.process_output(output)
        except KeyboardInterrupt:
            interrupted = True
            # TODO - process partial output, if any

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        if error:
            error_content = {'execution_count': self.execution_count,
                             'ename': '', 'evalue': error, 'traceback': []}

            self.send_response(self.iopub_socket, 'error', error_content)
            error_content['status'] = 'error'
            return error_content
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MagmaKernel)
