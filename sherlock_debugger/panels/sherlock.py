from django.template.loader import render_to_string
from debug_toolbar.panels import DebugPanel
import inspect
try:
    import threading
except ImportError:
    threading = None

CONSTANT_ID = 1
RECORDS = {}


class DebugRecord(object):
    def __init__(self, *args, **kwargs):
        pass


def clear_record_for_current_thread():
    if threading is None:
        t_id = CONSTANT_ID
    else:
        t_id = threading.currentThread()
    RECORDS[t_id] = []


def get_record_for_current_thread():
    if threading is None:
        t_id = CONSTANT_ID
    else:
        t_id = threading.currentThread()
    if t_id not in RECORDS:
        RECORDS[t_id] = []
    return RECORDS[t_id]


def log_record(record):
    slot = get_record_for_current_thread()
    slot.append(record)


def debug_class(the_class, record):
    """ Adds class and module information
    """
    record.class_name = the_class.__name__
    record.docs = the_class.__doc__
    module = inspect.getmodule(the_class)
    debug_module(module, record)
    #record.source_file = inspect.getsourcefile(the_class)


def debug_module(module, record):
    import __builtin__
    record.source_file = "__builtin__"
    if module != __builtin__:
        record.source_file = inspect.getsourcefile(module)
        console_debug(record.source_file)
    record.module_name = module.__name__


def console_debug(value):
    print "**************"
    print value


def debug_default(value, record):
    __class = value.__class__
    debug_class(__class, record)


def debug(value, *args, **kwargs):
    stack = inspect.stack()[1]
    frm = stack[0]

    record = DebugRecord()
    record.globals = frm.f_globals
    record.locals = frm.f_locals
    record.value = str(value)
    record.invoked = {}
    record.invoked['file'] = stack[1]
    record.invoked['line'] = stack[2]
    record.invoked['function'] = stack[3]
    #record.invoked = "%s @ line %s inside %s view" % (stack[1],
    #                                                  stack[2], stack[3])

    if inspect.isclass(value):
        debug_class(value, record)
    elif inspect.ismodule(value):
        debug_module(value, record)
    else:
        debug_default(value, record)

    # To include:
    # record.docs
    # globals
    # locals
    record.dir = dir(record)
    log_record(record)


class SherlockDebugPanel(DebugPanel):

    name = 'ShelockDebug'
    template = 'sherlock_debugger/panels/sherlock.html'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(SherlockDebugPanel, self).__init__(*args, **kwargs)
        clear_record_for_current_thread()

    def nav_title(self):
        return 'Sherlock Debugger'

    def nav_subtitle(self):
        return "Sherlock subtitle"

    def title(self):
        return 'All values to debug'

    def url(self):
        return ''

    def content(self):

        context = self.context.copy()

        records = get_record_for_current_thread()
        context.update({
            'records': records,
            'count': len(records)
        })

        return render_to_string(self.template, context)
