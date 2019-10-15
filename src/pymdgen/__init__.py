import importlib
import inspect
import logging
import re

log = logging.getLogger("pymdgen")


def adjust_header_indent(line, section_level):
    """
    Parses a line for a markdown header and fixes the
    indent for the specified section level

    eg. '## Header' with section_level=1 will become
    '# Header"

    Arguments:

    - line(str)
    - section_level(int)

    Returns:

    - str
    """

    m = re.match("[#+] (.+)", line)
    if m:
        line = u"{} {}".format("#" * (section_level), m.group(1))
    return line


def doc_func(name, func, section_level=4):

    """
    return markdown formatted documentation for a function

    Arguments:

    - name(str): function name #FIXME: why is this manual?
    - func(function)
    - section_level(int): markdown section level
    """

    is_property = False

    if isinstance(func, property):
        func = func.fget
        is_property = True

    output = []
    docstr = inspect.getdoc(func)
    # skip functions without a docstr
    if not docstr:
        return output

    spec = inspect.getargspec(func)
    display = []
    end_args = []

    # *args and **kwargs
    if spec[1]:
        end_args.append("*" + spec[1])
    if spec[2]:
        end_args.append("**" + spec[2])

    # check for args with defaults
    if spec[3]:
        args = spec[0][-len(spec[3]) :]
        default_args = list(zip(args, spec[3]))

        # set args to rest
        args = spec[0][: -len(spec[3])]
    else:
        args = spec[0]
        default_args = []

    if args:
        display.append(", ".join(args))
    if default_args:
        display.append(", ".join("%s=%s" % x for x in default_args))
    if end_args:
        display.append(", ".join(end_args))

    if name.find("__") == 0:
        title = "\{}".format(name)
    else:
        title = name

    output.append("{} {}".format("#" * section_level, title))
    output.append("")
    output.append("```")
    if is_property:
        output.append("@property")
    output.append(name + "(" + ", ".join(display) + ")")
    output.append("```")
    output.append("")
    output.append(docstr)
    output.append("")
    output.append("---")

    return output


def parse_class_docstr(docstr, list_attributes, section_level):

    """
    Takes a class doc string markdown and parses it line for line
    to fix and header indent issues as well as collect instanced
    attribute docs

    Arguments

    - docstr(str): markdown formatted class docstr
    - list_attributes(list): collect instance attribute docs into
      this list
    - section_level(int): header indent level

    Returns:

    - list: parsed/fixed output split into lines
    """

    attributes_regex = "[#+] Instanced (Attributes|Properties)"
    header_regex = "[#+] (.+)"

    collect_attributes = False
    out = []

    for line in [l.strip() for l in docstr.split("\n")]:
        if re.match(attributes_regex, line):
            collect_attributes = True
        elif collect_attributes and line:
            list_attributes.append(line)
        elif collect_attributes and list_attributes and not line:
            collect_attributes = False
        else:
            out.append(adjust_header_indent(line, section_level + 1))

    return out


def doc_class(name, cls, section_level=3):
    """
    return markdown formatted documentation for a class

    Arguments

    - name(str): function name #FIXME: why is this manual?
    - cls(class)
    - section_level(int): markdown section level
    """

    output = []
    docstr = inspect.getdoc(cls)
    # skip functions without a docstr
    if not docstr:
        return output

    head_indent = "#" * (section_level + 1)

    out_methods = ["", "{} Methods".format(head_indent), ""]
    out_attributes = ["", "{} Class Attributes".format(head_indent), ""]
    out_instanced_attributes = [
        "",
        "{} Instanced Attributes".format(head_indent),
        "",
        "These attributes / properties will be available on instances of the class",
        "",
    ]

    list_instanced_attributes = []
    list_attributes = []

    # parse the class docstr markdown to:
    # - fix header indent according to section level
    # - collect arbitrary instance attribute documentation
    out_docstr = parse_class_docstr(docstr, list_instanced_attributes, section_level)

    # full mro is probably overkill?
    # base_classes = inspect.getmro(cls)
    base_classes = cls.__bases__
    base_classes = (c.__module__ + "." + c.__name__ for c in base_classes)

    output.append("{} {}".format("#" * section_level, name))
    output.append("")
    output.append("```")
    output.append(name + "(" + ", ".join(base_classes) + ")")
    output.append("```")
    output.append("")
    output.extend(out_docstr)
    output.append("")

    functions = sorted(list(cls.__dict__.items()), key=lambda x: x[0])

    for func_name, func in functions:
        if inspect.isfunction(func):
            out_methods.extend(doc_func(func_name, func, section_level + 2))
        elif isinstance(func, property):
            list_instanced_attributes.extend(doc_property(func_name, func))
        elif hasattr(func, "help"):
            list_attributes.extend(doc_attribute(func_name, func))

    # Append class attribute documentation to output

    if list_attributes:
        output.extend(out_attributes)
        output.extend(sorted(list_attributes))

    # Append instanced attributed documentation to output

    if list_instanced_attributes:
        output.extend(out_instanced_attributes)
        output.extend(sorted(list_instanced_attributes))

    # Append method documentation to output

    if len(out_methods) > 1:
        output.extend(out_methods)

    output.append("")

    return output


def doc_attribute(name, attribute):
    """
    return markdown formatted documentation for a class attribute

    This is an experimental feature that will document any attribute
    set on class as long as the attribute it self has `help` property

    Argument(s):

    - name(str)
    - attribute(function|class|instance)

    Returns:

    - list
    """
    if not hasattr(attribute, "help"):
        return

    output = []
    type_name = None

    if inspect.isclass(attribute):
        type_name = "`{} Class`".format(attribute.__name__)
    elif hasattr(attribute, "__class__"):
        type_name = "`{} Instance`".format(attribute.__class__.__name__)

    try:
        output.append("- {} ({}): {}".format(name, type_name, attribute.help))
    except:
        pass

    return output


def doc_property(name, prop):
    """
    return markdown formatted documentation for a class property

    Argument(s):

    - name(str)
    - prop(property)

    Returns:

    - list
    """
    docstr = inspect.getdoc(prop.fget)
    return ["- {} (`{}`): {}".format(name, "@property", docstr)]


def doc_module(name, debug=False, section_level=3):

    """
    return markdown formatted documentation for a module

    Arguments:

    - name(str): module name
    - debug(bool): log debug messages
    - section_level(int): markdown section level
    """

    if "/" in name or name.endswith(".py"):
        name = name.replace("/", ".")
        name = name.rstrip(".py")

    module = importlib.import_module(name)
    output = []

    output.append("{} {}".format("#" * section_level, module.__name__))

    docstr = inspect.getdoc(module)
    if docstr:
        output.extend(["", docstr])

    output.append("")

    for k, v in inspect.getmembers(module):
        if k == "__builtins__":
            continue
        log.debug("checking %s:%s" % (v, k))
        if inspect.isfunction(v):
            if v.__module__ == module.__name__:
                output.extend(doc_func(k, v, section_level + 1))
        if inspect.isclass(v):
            if v.__module__ == module.__name__:
                output.extend(doc_class(k, v, section_level + 1))

    return output
