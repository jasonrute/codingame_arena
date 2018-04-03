from subprocess import Popen
from subprocess import PIPE
from threading import Thread
from queue import Queue
from queue import Empty


# Helper functions to avoid blocking of the streams.
# We us this technique: http://stackoverflow.com/a/4896288/3494621

def _enqueue_output(out, queue):
    """
    Wrap the output stream in a queue, which when placed in a thread,
    will avoid blocking.
    """
    for line in iter(out.readline, ""):  # loop over the out file
        queue.put(line)
    out.close()


def _convert_output_stream_to_threaded_queue(out):
    """Convert the output stream to a threaded queue."""
    out_queue = Queue()
    t = Thread(target=_enqueue_output, args=(out, out_queue))
    t.daemon = True  # thread dies with the program
    t.start()
    return out_queue


def _read_non_blocking(queue, timeout):
    """
    Enumerate all the lines currently in the stream queue without waiting for
    more to be added later.  The timeout is how long I wait for something to
    come through the buffer.  Once it does, I read without waiting.
    """
    while True:
        # read line without blocking
        try:
            yield queue.get(timeout=timeout)  # or queue.get_nowait()
            timeout = 0
        except Empty:
            return  # done enumerating


class PlayerProcess:
    """
    Keeps track of a players process including all the tricks we use to avoid
    issues with the streams blocking.
    """

    def __init__(self, program_name, options):
        p = Popen(['python3', '-u', program_name] + options,  # -u prevents
                                                              # buffering on
                                                              # the child's side
                  stdout=PIPE, stdin=PIPE, stderr=PIPE,
                  bufsize=1,  # Prevents buffering parent's end
                  universal_newlines=True)  # Streams are text instead of bytes
        self._process = p
        self._stdout_queue = _convert_output_stream_to_threaded_queue(p.stdout)
        self._stderr_queue = _convert_output_stream_to_threaded_queue(p.stderr)
        self.stdin = p.stdin

    def read_stdout(self, timeout=.1):
        return _read_non_blocking(self._stdout_queue, timeout=timeout)

    def read_stderr(self, timeout=.1):
        return _read_non_blocking(self._stderr_queue, timeout=timeout)

    def kill(self):
        self._process.kill()
