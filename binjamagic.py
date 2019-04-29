# binjamagic.py
import gc
import binaryninja

from binaryninja import scriptingprovider

class BinjaMagic(object):
    def __init__(self, ip):
        self.shell = ip
        obj = [o for o in gc.get_objects() if isinstance(
            o, scriptingprovider.PythonScriptingInstance.InterpreterThread)]
        if len(obj) == 1:

            self.bip = obj[0]
        else:
            raise Exception(
                "Couldn't find scriptingprovider. Sure you are in the right kernel?")

        self._init_ns()

    def _init_ns(self):
        self.shell.user_ns['binaryninja'] = binaryninja

    def _update_ns(self):
        """Updates the namespace of the running kernel with the binja magic variables"""
        bip = self.bip
        self.shell.user_ns.update({
            'write_at_cursor': bip.write_at_cursor,
            'get_selected_data': bip.get_selected_data,
            'bv': bip.current_view,
            'current_view': bip.current_view,
            'current_function': bip.current_func,
            'current_basic_block': bip.current_block,
            'current_address': bip.current_addr,
            'here': bip.current_selection_begin,
            'current_selection': (bip.current_selection_begin, bip.current_selection_end),
        })
        if bip.current_func is None:
            self.shell.user_ns['current_llil'] = None
            self.shell.user_ns['current_mlil'] = None
        else:
            self.shell.user_ns['current_llil'] = self.bip.current_func.low_level_il
            self.shell.user_ns['current_mlil'] = self.bip.current_func.medium_level_il

    def pre_execute(self):
        self._update_ns()

    def post_execute(self):
        return

    def shell_initialized(self):
        self._update_ns()


def load_ipython_extension(ip):
    vw = BinjaMagic(ip)
    ip.events.register('pre_execute', vw.pre_execute)
    ip.events.register('post_execute', vw.post_execute)
    ip.events.register('shell_initialized', vw.shell_initialized)
