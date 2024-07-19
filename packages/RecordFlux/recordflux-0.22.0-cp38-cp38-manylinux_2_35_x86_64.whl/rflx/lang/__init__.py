
"""
Python binding of the Librflxlang API.

Please consider all exported entities whose names that start with an underscore
("_") as internal implementation details. They are not meant to be used
directly.
"""







from __future__ import annotations





import argparse
import collections
import ctypes
import io
import json
import os
import re
import sys
import traceback
from typing import (
    Any, AnyStr, Callable, ClassVar, Dict, Generic, IO, Iterator, List,
    Optional as Opt, TYPE_CHECKING, Tuple, Type, TypeVar, Union
)
import weakref


# Protocol was added to "typing" in Python 3.8
if TYPE_CHECKING:
    from typing import Protocol
else:
    Protocol = object


#
# Low-level binding - First part
#

_so_ext = {
    'win32':  'dll',
    'darwin': 'dylib',
}.get(sys.platform, 'so')

# Loading the shared library here is quite involved as we want to support
# Python packages that embed all the required shared libraries: if we can
# find the shared library in the package directory, import it from there
# directly.

# Directory that contains this __init__.py module
_self_path = os.path.dirname(os.path.abspath(__file__))

# Base and full names for the shared library to load. Full name assumes the
# shared lib is in the package directory.
_c_lib_name = 'librflxlang.{}'.format(_so_ext)
_c_lib_path = os.path.join(_self_path, _c_lib_name)

# If we can find the shared lirbray in the package directory, load it from
# here, otherwise let the dynamic loader find it in the environment. On
# Windows, there is no RPATH trick, so we need to temporarily alter the PATH
# environment variable in order to import the whole closure of DLLs.
_old_env_path = None
if os.path.exists(_c_lib_path):
    if sys.platform == 'win32':
        _old_env_path = os.environ['PATH']
        os.environ['PATH'] = '{}{}{}'.format(_self_path, os.path.pathsep,
                                             os.environ['PATH'])
else:
    _c_lib_path = _c_lib_name


# Finally load the library
_c_lib = ctypes.cdll.LoadLibrary(_c_lib_path)

# Restore the PATH environment variable if we altered it
if _old_env_path is not None:
    os.environ['PATH'] = _old_env_path


def _import_func(name, argtypes, restype, exc_wrap=True):
    """
    Import "name" from the C library, set its arguments/return types and return
    the binding.

    :param str name: Name of the symbol for the function to import.
    :param list[ctypes._CData] argtypes: Types for function argruments.
    :param None|ctypes._CData restype: Function return type, or None if it
        does not return anything.
    :param bool exc_wrap: If True, wrap the returned function to check for
      exceptions.
    """
    func = getattr(_c_lib, name)
    func.argtypes = argtypes
    func.restype = restype

    def check_argcount(args, kwargs):
        argcount = len(args) + len(kwargs)
        if argcount != len(argtypes):
            raise TypeError(
                '{} takes {} positional arguments but {} was given'
                .format(name, len(argtypes), argcount))

    # Wrapper for "func" that raises a NativeException in case of internal
    # error.

    if exc_wrap:
        def wrapper(*args, **kwargs):
            check_argcount(args, kwargs)
            result = func(*args, **kwargs)
            exc = _get_last_exception()
            if exc:
                raise exc.contents._wrap()
            return result
    else:
        def wrapper(*args, **kwargs):
            check_argcount(args, kwargs)
            return func(*args, **kwargs)

    return wrapper


class _Exception(ctypes.Structure):
    _fields_ = [('kind', ctypes.c_int),
                ('information', ctypes.c_char_p)]

    def _wrap(self):
        # Turn information into native strings, i.e. decode bytes.  These
        # strings are only informative, so do not raise an error if decoding
        # fails: do best effort decoding instead to be as helpful as possible.
        info = self.information.decode(errors='replace')
        return _exception_kind_to_type[self.kind](info)


def _type_fullname(t: type) -> str:
    """
    Return the fully qualified name for the given `t` type.
    """
    name = t.__name__
    module = t.__module__
    return (name
            if module in (None, object.__class__.__module__) else
            '{}.{}'.format(module, name))


def _raise_type_error(expected_type_name: str, actual_value: Any) -> Any:
    raise TypeError('{} instance expected, got {} instead'.format(
        expected_type_name, _type_fullname(type(actual_value))
    ))


def _log_uncaught_error(context):
    """
    Log an uncaught exception on stderr.

    Useful to warn users about an exception that occurs in a Python function
    used as a C callback: we cannot let the exception propagate in this case.
    """
    print(f"Uncaught exception in {context}:", file=sys.stderr)
    traceback.print_exc()


_get_last_exception = _import_func(
   'rflx_get_last_exception',
   [], ctypes.POINTER(_Exception),
   exc_wrap=False
)


def _hashable_c_pointer(pointed_type=None):
    """
    Create a "pointer to `pointed_type` type and make it hashable.

    :param pointed_type: ctypes type class. If left to `None`, we return a
        subclass of `ctypes.c_void_p`.
    :rtype: ctypes.POINTER
    """

    if pointed_type is None:
        class _c_type(ctypes.c_void_p):
            @property
            def _pointer_value(self):
                return self.value or 0
    else:
        @property
        def _pointer_value(self):
            return ctypes.cast(self, ctypes.c_void_p).value or 0

        _c_type = ctypes.POINTER(pointed_type)
        _c_type._pointer_value = _pointer_value

    def __hash__(self):
        return self._pointer_value

    def __eq__(self, other):
        return self._pointer_value == other._pointer_value

    def __ne__(self, other):
        return not (self == other)

    _c_type.__hash__ = __hash__
    _c_type.__eq__ = __eq__
    _c_type.__ne__ = __ne__
    return _c_type


def _unwrap_filename(filename: Opt[AnyStr]) -> Opt[bytes]:
    """Turn filename into a suitable C value for filenames."""
    if filename is None:
        return None
    elif isinstance(filename, str):
        return filename.encode()
    elif not isinstance(filename, bytes):
        raise ValueError(f"invalid filename: {filename}")
    else:
        return filename


def _unwrap_charset(charset: Opt[AnyStr]) -> Opt[bytes]:
    """Turn charset into a suitable C value for charsets."""
    if charset is None:
        return None
    elif isinstance(charset, str):
        return charset.encode()
    elif not isinstance(charset, bytes):
        raise ValueError(f"invalid charset: {charset}")
    else:
        return charset


class _text(ctypes.Structure):
    """
    C value for unicode strings. This object is the owner of the underlying
    buffer, so the string will be deallocated when ``self`` is destroyed.

    ``_unwrap`` takes a string/unicode object and returns a ``_text`` instance,
    while ``_wrap`` retuns an unicode instance.
    """
    # The chars field really is a uint32_t* but considering it as a char* here
    # is more convenient for conversion in this binding layer. On the other
    # side, we have to be careful about converting the length when retrieving
    # the chars.
    _fields_ = [("chars", ctypes.POINTER(ctypes.c_char)),
                ("length", ctypes.c_size_t),
                ("is_allocated", ctypes.c_int),]

    encoding = 'utf-32le' if sys.byteorder == 'little' else 'utf-32be'

    # Instances can hold buffers that they own. In this case, the buffer must
    # be deallocated when the instance is destroyed. Thus instances will hold
    # a "text_buffer" attribute that will be automatically destroyed.
    text_buffer = None

    @classmethod
    def _create_buffer(cls, value: AnyStr) -> Tuple[Any, int]:
        """
        Turn `value` into the corresponding UTF-32 string buffer.

        Return both the string buffer and the number of codepoints it contains
        (not the number of bytes!).
        """
        string = cls.cast(value)
        buf = ctypes.create_string_buffer(string.encode(cls.encoding))
        return (buf, len(string))

    @classmethod
    def _decode_buffer(cls, buf: Any, length: int) -> str:
        """
        Decode the UTF-32 string in `buf`.

        :param buf: String buffer (of type `POINTER(c_char_p)`) to decode.
        :param length: Number of codepoints in `buf` (not the number of
            bytes!).
        """
        if length > 0:
            # `length` tells how much UTF-32 chars there are in `buf` but `buf`
            # is a char* so we have to fetch 4 times more bytes than bytes.
            return buf[:4 * length].decode(cls.encoding)
        else:
            return ""

    @classmethod
    def _unwrap(cls, value: AnyStr) -> _text:
        text_buffer, length = cls._create_buffer(value)
        text_buffer_ptr = ctypes.cast(
            ctypes.pointer(text_buffer),
            ctypes.POINTER(ctypes.c_char)
        )
        result = _text(text_buffer_ptr, length)
        result.text_buffer = text_buffer
        return result

    def _wrap(self) -> str:
        return self._decode_buffer(self.chars, self.length)

    @classmethod
    def cast(cls, value: AnyStr) -> str:
        """
        Try to cast ``value`` into an unicode object. Raise a TypeError, or
        raise a string decoding error when this is not possible.
        """
        if isinstance(value, bytes):
            return value.decode('ascii')
        elif not isinstance(value, str):
            _raise_type_error('text string', value)
        else:
            return value

    def __del__(self) -> None:
        _destroy_text(ctypes.byref(self))


class _symbol_type(ctypes.Structure):
    _fields_ = [('data', ctypes.c_void_p),
                ('bounds', ctypes.c_void_p)]

    @classmethod
    def wrap(cls, c_value: Any) -> str:
        # First extract the text associated to this symbol in "text"
        text = _text()
        _symbol_text(ctypes.byref(c_value), ctypes.byref(text))

        # Then wrap this text
        return text._wrap()

    @classmethod
    def unwrap(cls, py_value: AnyStr, context: Any) -> _symbol_type:
        # First turn the given symbol into a low-level text object
        text = _text._unwrap(py_value)

        # Then convert it to a symbol
        result = cls()
        if not _context_symbol(context, ctypes.byref(text),
                               ctypes.byref(result)):
            raise InvalidSymbolError(py_value)
        return result


class _big_integer:

    class c_type(ctypes.c_void_p):
        pass

    def __init__(self, c_value: Any):
        self.c_value = c_value

    @classmethod
    def unwrap(cls, value: int) -> _big_integer:
        if not isinstance(value, int):
            _raise_type_error('int or long', value)

        text = _text._unwrap(str(value))
        c_value = cls.create(ctypes.byref(text))
        return cls(c_value)

    @classmethod
    def wrap(cls, c_value: Any) -> int:
        helper = cls(c_value)
        text = _text()
        cls.text(helper.c_value, ctypes.byref(text))
        return int(text._wrap())

    def clear(self) -> None:
        self.c_value = None

    def __del__(self) -> None:
        self.decref(self.c_value)
        self.clear()

    create = staticmethod(_import_func(
        'rflx_create_big_integer',
        [ctypes.POINTER(_text)], c_type
    ))
    text = staticmethod(_import_func(
        'rflx_big_integer_text',
        [c_type, ctypes.POINTER(_text)], None
    ))
    decref = staticmethod(_import_func(
        'rflx_big_integer_decref',
        [c_type], None
    ))


class _String:
    """
    Helper to wrap/unwrap string values for properties arguments/return types.
    """

    class c_struct(ctypes.Structure):
        _fields_ = [("length", ctypes.c_int),
                    ("ref_count", ctypes.c_int),

                    # See the "chars" field in the _text structure
                    ("content", ctypes.c_char * 1)]
    c_type = ctypes.POINTER(c_struct)

    __slots__ = ("c_value", )

    def __init__(self, c_value):
        self.c_value = c_value

    def __del__(self):
        self.dec_ref(self.c_value)
        self.c_value = None

    @classmethod
    def unwrap(cls, value: AnyStr) -> _String:
        # Convert "value" into the corresponding UTF-32 string buffer
        buf, length = _text._create_buffer(value)
        return cls(cls.create(buf, length))

    @classmethod
    def wrap(cls, value: Any) -> str:
        struct = value.contents

        # "struct.content" will get a one-byte copy of the actual string
        # because of the hack above to handle variable-length struct field. To
        # get the whole string, compute a pointer to this field fierst.
        content_addr = _field_address(struct, "content")
        content = ctypes.pointer(ctypes.c_char.from_address(content_addr))

        return _text._decode_buffer(content, struct.length)

    create = staticmethod(_import_func(
        'rflx_create_string',
        [ctypes.POINTER(ctypes.c_char), ctypes.c_int], c_type
    ))
    dec_ref = staticmethod(_import_func(
        'rflx_string_dec_ref',
        [c_type], None
    ))


if TYPE_CHECKING:
    _EnumType = TypeVar("_EnumType", bound=_Enum)


class _Enum:

    _name: ClassVar[str]
    """
    Name for this enumeration type.
    """

    _c_to_py: ClassVar[List[str]]
    """
    Mapping from C values to user-level Python values.
    """

    _py_to_c: ClassVar[Dict[str, int]]
    """
    Mapping from user-level Python values to C values.
    """

    @classmethod
    def _unwrap(cls, py_value: str) -> int:
        if not isinstance(py_value, str):
            _raise_type_error('str', py_value)
        try:
            return cls._py_to_c[py_value]
        except KeyError:
            raise ValueError('Invalid {}: {}'.format(cls._name, py_value))

    @classmethod
    def _wrap(cls: Type[_EnumType], c_value: Any) -> _EnumType:
        if isinstance(c_value, ctypes.c_int):
            c_value = c_value.value
        return cls._c_to_py[c_value]


class AnalysisUnitKind(_Enum):
    """
    Specify a kind of analysis unit. Specification units provide an interface
    to the outer world while body units provide an implementation for the
    corresponding interface.
    """

    unit_specification = 'unit_specification'
    unit_body = 'unit_body'

    _name = 'AnalysisUnitKind'
    _c_to_py = [
        unit_specification, unit_body]
    _py_to_c = {name: index for index, name in enumerate(_c_to_py)}
class LookupKind(_Enum):
    """

    """

    recursive = 'recursive'
    flat = 'flat'
    minimal = 'minimal'

    _name = 'LookupKind'
    _c_to_py = [
        recursive, flat, minimal]
    _py_to_c = {name: index for index, name in enumerate(_c_to_py)}
class DesignatedEnvKind(_Enum):
    """
    Discriminant for DesignatedEnv structures.
    """

    none = 'none'
    current_env = 'current_env'
    named_env = 'named_env'
    direct_env = 'direct_env'

    _name = 'DesignatedEnvKind'
    _c_to_py = [
        none, current_env, named_env, direct_env]
    _py_to_c = {name: index for index, name in enumerate(_c_to_py)}
class GrammarRule(_Enum):
    """
    Gramar rule to use for parsing.
    """

    main_rule_rule = 'main_rule_rule'
    unqualified_identifier_rule = 'unqualified_identifier_rule'
    qualified_identifier_rule = 'qualified_identifier_rule'
    numeric_literal_rule = 'numeric_literal_rule'
    variable_rule = 'variable_rule'
    sequence_aggregate_rule = 'sequence_aggregate_rule'
    string_literal_rule = 'string_literal_rule'
    concatenation_rule = 'concatenation_rule'
    primary_rule = 'primary_rule'
    paren_expression_rule = 'paren_expression_rule'
    suffix_rule = 'suffix_rule'
    factor_rule = 'factor_rule'
    term_rule = 'term_rule'
    unop_term_rule = 'unop_term_rule'
    simple_expr_rule = 'simple_expr_rule'
    relation_rule = 'relation_rule'
    expression_rule = 'expression_rule'
    quantified_expression_rule = 'quantified_expression_rule'
    comprehension_rule = 'comprehension_rule'
    call_rule = 'call_rule'
    conversion_rule = 'conversion_rule'
    null_message_aggregate_rule = 'null_message_aggregate_rule'
    message_aggregate_association_rule = 'message_aggregate_association_rule'
    message_aggregate_association_list_rule = 'message_aggregate_association_list_rule'
    message_aggregate_rule = 'message_aggregate_rule'
    extended_primary_rule = 'extended_primary_rule'
    extended_paren_expression_rule = 'extended_paren_expression_rule'
    extended_choice_list_rule = 'extended_choice_list_rule'
    extended_choices_rule = 'extended_choices_rule'
    extended_case_expression_rule = 'extended_case_expression_rule'
    extended_suffix_rule = 'extended_suffix_rule'
    extended_factor_rule = 'extended_factor_rule'
    extended_term_rule = 'extended_term_rule'
    extended_unop_term_rule = 'extended_unop_term_rule'
    extended_simple_expr_rule = 'extended_simple_expr_rule'
    extended_relation_rule = 'extended_relation_rule'
    extended_expression_rule = 'extended_expression_rule'
    aspect_rule = 'aspect_rule'
    range_type_definition_rule = 'range_type_definition_rule'
    modular_type_definition_rule = 'modular_type_definition_rule'
    integer_type_definition_rule = 'integer_type_definition_rule'
    if_condition_rule = 'if_condition_rule'
    extended_if_condition_rule = 'extended_if_condition_rule'
    then_rule = 'then_rule'
    type_argument_rule = 'type_argument_rule'
    null_message_field_rule = 'null_message_field_rule'
    message_field_rule = 'message_field_rule'
    message_field_list_rule = 'message_field_list_rule'
    value_range_rule = 'value_range_rule'
    checksum_association_rule = 'checksum_association_rule'
    checksum_aspect_rule = 'checksum_aspect_rule'
    byte_order_aspect_rule = 'byte_order_aspect_rule'
    message_aspect_list_rule = 'message_aspect_list_rule'
    message_type_definition_rule = 'message_type_definition_rule'
    positional_enumeration_rule = 'positional_enumeration_rule'
    element_value_association_rule = 'element_value_association_rule'
    named_enumeration_rule = 'named_enumeration_rule'
    enumeration_aspects_rule = 'enumeration_aspects_rule'
    enumeration_type_definition_rule = 'enumeration_type_definition_rule'
    type_derivation_definition_rule = 'type_derivation_definition_rule'
    sequence_type_definition_rule = 'sequence_type_definition_rule'
    type_declaration_rule = 'type_declaration_rule'
    type_refinement_rule = 'type_refinement_rule'
    parameter_rule = 'parameter_rule'
    parameter_list_rule = 'parameter_list_rule'
    formal_function_declaration_rule = 'formal_function_declaration_rule'
    channel_declaration_rule = 'channel_declaration_rule'
    session_parameter_rule = 'session_parameter_rule'
    renaming_declaration_rule = 'renaming_declaration_rule'
    variable_declaration_rule = 'variable_declaration_rule'
    declaration_rule = 'declaration_rule'
    description_aspect_rule = 'description_aspect_rule'
    assignment_statement_rule = 'assignment_statement_rule'
    message_field_assignment_statement_rule = 'message_field_assignment_statement_rule'
    list_attribute_rule = 'list_attribute_rule'
    reset_rule = 'reset_rule'
    attribute_statement_rule = 'attribute_statement_rule'
    action_rule = 'action_rule'
    conditional_transition_rule = 'conditional_transition_rule'
    transition_rule = 'transition_rule'
    state_body_rule = 'state_body_rule'
    state_rule = 'state_rule'
    session_declaration_rule = 'session_declaration_rule'
    basic_declaration_rule = 'basic_declaration_rule'
    basic_declarations_rule = 'basic_declarations_rule'
    package_declaration_rule = 'package_declaration_rule'
    context_item_rule = 'context_item_rule'
    context_clause_rule = 'context_clause_rule'
    specification_rule = 'specification_rule'

    _name = 'GrammarRule'
    _c_to_py = [
        main_rule_rule, unqualified_identifier_rule, qualified_identifier_rule, numeric_literal_rule, variable_rule, sequence_aggregate_rule, string_literal_rule, concatenation_rule, primary_rule, paren_expression_rule, suffix_rule, factor_rule, term_rule, unop_term_rule, simple_expr_rule, relation_rule, expression_rule, quantified_expression_rule, comprehension_rule, call_rule, conversion_rule, null_message_aggregate_rule, message_aggregate_association_rule, message_aggregate_association_list_rule, message_aggregate_rule, extended_primary_rule, extended_paren_expression_rule, extended_choice_list_rule, extended_choices_rule, extended_case_expression_rule, extended_suffix_rule, extended_factor_rule, extended_term_rule, extended_unop_term_rule, extended_simple_expr_rule, extended_relation_rule, extended_expression_rule, aspect_rule, range_type_definition_rule, modular_type_definition_rule, integer_type_definition_rule, if_condition_rule, extended_if_condition_rule, then_rule, type_argument_rule, null_message_field_rule, message_field_rule, message_field_list_rule, value_range_rule, checksum_association_rule, checksum_aspect_rule, byte_order_aspect_rule, message_aspect_list_rule, message_type_definition_rule, positional_enumeration_rule, element_value_association_rule, named_enumeration_rule, enumeration_aspects_rule, enumeration_type_definition_rule, type_derivation_definition_rule, sequence_type_definition_rule, type_declaration_rule, type_refinement_rule, parameter_rule, parameter_list_rule, formal_function_declaration_rule, channel_declaration_rule, session_parameter_rule, renaming_declaration_rule, variable_declaration_rule, declaration_rule, description_aspect_rule, assignment_statement_rule, message_field_assignment_statement_rule, list_attribute_rule, reset_rule, attribute_statement_rule, action_rule, conditional_transition_rule, transition_rule, state_body_rule, state_rule, session_declaration_rule, basic_declaration_rule, basic_declarations_rule, package_declaration_rule, context_item_rule, context_clause_rule, specification_rule]
    _py_to_c = {name: index for index, name in enumerate(_c_to_py)}


default_grammar_rule = GrammarRule.main_rule_rule


_file_reader = _hashable_c_pointer()
_unit_provider = _hashable_c_pointer()
_event_handler = _hashable_c_pointer()


class _EventHandlerWrapper:
    """
    Wrapper for EventHandler instances, responsible to create the low-level
    event handler value and hold its callbacks.
    """

    __slots__ = (
        "event_handler",
        "c_value",
        "destroy_callback",
        "unit_requested_callback",
        "unit_parsed_callback",
    )

    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler

        # Create the C callbacks (wrappers around the _EventHandlerWrapper
        # static method) and keep references to them in "self" so that they
        # survive at least as long as "self".
        self.destroy_callback = _event_handler_destroy_func(
            _EventHandlerWrapper.destroy_func
        )
        self.unit_requested_callback = _event_handler_unit_requested_func(
            _EventHandlerWrapper.unit_requested_func
        )
        self.unit_parsed_callback = _event_handler_unit_parsed_func(
            _EventHandlerWrapper.unit_parsed_func
        )

        # Create the C-level event handler, which keeps a reference to "self"
        # and uses _EventHandlerWrapper's static methods as callbacks.
        self.c_value = _create_event_handler(
            ctypes.py_object(self),
            self.destroy_callback,
            self.unit_requested_callback,
            self.unit_parsed_callback,
        )

    def __del__(self) -> None:
        _dec_ref_event_handler(self.c_value)
        self.c_value = None

    @classmethod
    def create(
        cls,
        event_handler: Opt[EventHandler]
    ) -> Tuple[Opt[_EventHandlerWrapper], Opt[object]]:
        """
        Helper to wrap an EventHandler instance. Return also the C value that
        is created for that event handler. For convenience, just return None
        for both if ``event_handler`` is None.
        """
        if event_handler is None:
            return None, None
        else:
            eh = cls(event_handler)
            return eh, eh.c_value

    @staticmethod
    def destroy_func(self: _EventHandlerWrapper) -> None:
        pass

    @staticmethod
    def unit_requested_func(self: _EventHandlerWrapper,
                            context: object,
                            name: _text,
                            from_unit: object,
                            found: ctypes.c_uint8,
                            is_not_found_error: ctypes.c_uint8) -> None:
        py_context = AnalysisContext._wrap(context)
        py_name = name.contents._wrap()
        py_from_unit = AnalysisUnit._wrap(from_unit)
        try:
            self.event_handler.unit_requested_callback(
                py_context,
                py_name,
                py_from_unit,
                bool(found),
                bool(is_not_found_error),
            )
        except BaseException as exc:
            _log_uncaught_error("EventHandler.unit_requested_callback")

    @staticmethod
    def unit_parsed_func(self: _EventHandlerWrapper,
                         context: object,
                         unit: object,
                         reparsed: ctypes.c_uint8) -> None:
        py_context = AnalysisContext._wrap(context)
        py_unit = AnalysisUnit._wrap(unit)
        try:
            self.event_handler.unit_parsed_callback(
                py_context,
                py_unit,
                bool(reparsed),
            )
        except BaseException as exc:
            _log_uncaught_error("EventHandler.unit_parsed_callback")


def _canonicalize_buffer(buffer: AnyStr,
                         charset: Opt[bytes]) -> Tuple[bytes, Opt[bytes]]:
    """Canonicalize source buffers to be bytes buffers."""
    if isinstance(buffer, str):
        if charset:
            raise TypeError('`charset` must be null when the buffer is'
                            ' Unicode')
        return (buffer.encode('utf-8'), b'utf-8')
    elif not isinstance(buffer, bytes):
        raise TypeError('`buffer` must be a string')
    else:
        return (buffer, charset)


#
# High-level binding
#


class FileReadError(Exception):
    """
    Subprograms may raise this when they cannot open a source file. Note that
    this does *not* concern analysis unit getters, which create diagnostic
    vectors for such errors.
    """
    pass
class BadTypeError(Exception):
    """
    Raised when introspection functions (``Librflxlang.Introspection``) are
    provided mismatching types/values.
    """
    pass
class OutOfBoundsError(Exception):
    """
    Raised when introspection functions (``Librflxlang.Introspection``) are
    passed an out of bounds index.
    """
    pass
class InvalidInput(Exception):
    """
    Raised by lexing functions (``Librflxlang.Lexer``) when the input contains
    an invalid byte sequence.
    """
    pass
class InvalidSymbolError(Exception):
    """
    Exception raise when an invalid symbol is passed to a subprogram.
    """
    pass
class InvalidUnitNameError(Exception):
    """
    Raised when an invalid unit name is provided.
    """
    pass
class NativeException(Exception):
    """
    Exception raised in language bindings when the underlying C API reports an
    unexpected error that occurred in the library.

    This kind of exception is raised for internal errors: they should never
    happen in normal situations and if they are raised at some point, it means
    the library state is potentially corrupted.

    Nevertheless, the library does its best not to crash the program,
    materializing internal errors using this kind of exception.
    """
    pass
class PreconditionFailure(Exception):
    """
    Exception raised when an API is called while its preconditions are not
    satisfied.
    """
    pass
class PropertyError(Exception):
    """
    Exception that is raised when an error occurs while evaluating any AST node
    method whose name starts with ``p_``. This is the only exceptions that such
    functions can raise.
    """
    pass
class TemplateArgsError(Exception):
    """
    Exception raised when the provided arguments for a template don't match
    what the template expects.
    """
    pass
class TemplateFormatError(Exception):
    """
    Exception raised when a template has an invalid syntax, such as badly
    formatted placeholders.
    """
    pass
class TemplateInstantiationError(Exception):
    """
    Exception raised when the instantiation of a template cannot be parsed.
    """
    pass
class StaleReferenceError(Exception):
    """
    Exception raised while trying to access data that was deallocated. This
    happens when one tries to use a node whose unit has been reparsed, for
    instance.
    """
    pass
class SyntaxError(Exception):
    """
    Subprograms may raise this when they try to parse invalid syntax. Note that
    this does *not* concern analysis unit getters, which create diagnostic
    vectors for such errors.
    """
    pass
class UnknownCharset(Exception):
    """
    Raised by lexing functions (``Librflxlang.Lexer``) when the input charset
    is not supported.
    """
    pass
class MalformedTreeError(Exception):
    """
    Raised when unparsing functions working on rewritten trees
    (``Librflxlang.Rewriting``) are called on malformed trees.
    """
    pass

_exception_kind_to_type = [
    FileReadError,
    BadTypeError,
    OutOfBoundsError,
    InvalidInput,
    InvalidSymbolError,
    InvalidUnitNameError,
    NativeException,
    PreconditionFailure,
    PropertyError,
    TemplateArgsError,
    TemplateFormatError,
    TemplateInstantiationError,
    StaleReferenceError,
    SyntaxError,
    UnknownCharset,
    MalformedTreeError,
]





class EventHandler(Protocol):
    """
    Interface to handle events sent by the analysis context.
    """

    def unit_requested_callback(self,
                                context: AnalysisContext,
                                name: str,
                                from_unit: AnalysisUnit,
                                found: bool,
                                is_not_found_error: bool) -> None:
        """
        Callback that will be called when a unit is requested from the context
        ``Context``.

        ``Name`` is the name of the requested unit.

        ``From`` is the unit from which the unit was requested.

        ``Found`` indicates whether the requested unit was found or not.

        ``Is_Not_Found_Error`` indicates whether the fact that the unit was not
        found is an error or not.

        .. warning:: The interface of this callback is probably subject to
           change, so should be treated as experimental.
        """
        pass

    def unit_parsed_callback(self,
                             context: AnalysisContext,
                             unit: AnalysisUnit,
                             reparsed: bool) -> None:
        """
        Callback that will be called when any unit is parsed from the context
        ``Context``.

        ``Unit`` is the resulting unit.

        ``Reparsed`` indicates whether the unit was reparsed, or whether it was
        the first parse.
        """
        pass


class AnalysisContext:
    """
    This type represents a context for all source analysis. This is the first
    type you need to create to use Librflxlang. It will contain the results of
    all analysis, and is the main holder for all the data.

    You can create several analysis contexts if you need to, which enables you,
    for example to:

    * analyze several different projects at the same time;

    * analyze different parts of the same projects in parallel.

    In the current design, contexts always keep all of their analysis units
    allocated. If you need to get this memory released, the only option at your
    disposal is to destroy your analysis context instance.
    """

    __slots__ = ('_c_value', '_unit_provider', '_event_handler_wrapper',
                 '_serial_number', '_unit_cache', '__weakref__')

    _context_cache: weakref.WeakValueDictionary[Any, AnalysisContext] = (
        weakref.WeakValueDictionary()
    )
    """
    Cache for analysis context wrappers. Indexed by analysis context addresses,
    which are known to stay valid forever (and re-used).

    Unlike unit and node caches, this one should contain weak references so
    that analysis contexts (and their units/nodes) can be free'd when user code
    does not reference them anymore.
    """

    def __init__(self,
                 charset: Opt[str] = None,
                 file_reader: Opt[FileReader] = None,
                 unit_provider: Opt[UnitProvider] = None,
                 event_handler: Opt[EventHandler] = None,
                 with_trivia: bool = True,
                 tab_stop: int = 8,
                 *,
                 _c_value: Any = None) -> None:
        """
        Create a new analysis context.

        ``Charset`` will be used as a default charset to decode input sources
        in analysis units. Please see ``GNATCOLL.Iconv`` for several supported
        charsets. Be careful: passing an unsupported charset is not guaranteed
        to raise an error here. If no charset is provided, ``"utf-8"`` is the
        default.

        .. TODO: Passing an unsupported charset here is not guaranteed to raise
           an error right here, but this would be really helpful for users.

        When ``With_Trivia`` is true, the parsed analysis units will contain
        trivias.

        If provided, ``File_Reader`` will be used to fetch the contents of
        source files instead of the default, which is to just read it from the
        filesystem and decode it using the regular charset rules. Note that if
        provided, all parsing APIs that provide a buffer are forbidden, and any
        use of the rewriting API with the returned context is rejected.

        If provided, ``Unit_Provider`` will be used to query the file name that
        corresponds to a unit reference during semantic analysis. If it is
        ``None``, the default one is used instead.

        If provided, ``Event_Handler`` will be notified when various events
        happen.

        ``Tab_Stop`` is a positive number to describe the effect of tabulation
        characters on the column number in source files.
        """

        # Initialize this field in case we raise an exception during
        # construction, so that the destructor can run later on.
        self._c_value = None

        # Create the analysis context if requested, otherwise increase the
        # refcount of the existing context.
        if _c_value is None:
            _charset = _unwrap_charset(charset)
            if not isinstance(tab_stop, int) or tab_stop < 1:
                raise ValueError(
                    'Invalid tab_stop (positive integer expected)')
            c_file_reader = file_reader._c_value if file_reader else None
            c_unit_provider = unit_provider._c_value if unit_provider else None
            self._event_handler_wrapper, c_event_handler = (
                _EventHandlerWrapper.create(event_handler)
            )
            self._c_value = _allocate_analysis_context()
        else:
            self._c_value = _context_incref(_c_value)

        # Register the context in our cache so that wrapping the context in the
        # future always yields the same instance.
        assert self._c_value not in self._context_cache
        self._context_cache[self._c_value] = self

        # Initialize the serial number and the unit cache
        self._serial_number: Opt[int] = None
        self._unit_cache: Dict[str, AnalysisUnit] = {}
        """
        Cache for AnalysisUnit wrappers, indexed by analysis unit addresses,
        which are known to stay valid as long as the context is alive.
        """

        self._check_unit_cache()

        # Now that we have an AnalysisContext wrapper registered, if we just
        # created the analysis context, also initialize it.
        if _c_value is None:
            _initialize_analysis_context(
                self._c_value,
                _charset,
                c_file_reader,
                c_unit_provider,
                c_event_handler,
                with_trivia,
                tab_stop
            )

        # Keep a reference to the unit provider so that it is live at least as
        # long as the analysis context is live.
        self._unit_provider = unit_provider

    def __del__(self) -> None:
        if self._c_value:
            _context_decref(self._c_value)

    def __eq__(self, other: Any) -> bool:
        return self._c_value == other._c_value

    def __hash__(self) -> int:
        return hash(self._c_value)

    def get_from_file(self,
                      filename: AnyStr,
                      charset: Opt[str] = None,
                      reparse: bool = False,
                      rule: str = default_grammar_rule) -> AnalysisUnit:
        """
        Create a new analysis unit for ``Filename`` or return the existing one
        if any. If ``Reparse`` is true and the analysis unit already exists,
        reparse it from ``Filename``.

        ``Rule`` controls which grammar rule is used to parse the unit.

        Use ``Charset`` in order to decode the source. If ``Charset`` is empty
        then use the context's default charset.

        If any failure occurs, such as file opening, decoding, lexing or
        parsing failure, return an analysis unit anyway: errors are described
        as diagnostics of the returned analysis unit.
        """
        _filename = _unwrap_filename(filename)
        _charset = _unwrap_charset(charset)
        c_value = _get_analysis_unit_from_file(self._c_value, _filename,
                                               _charset, reparse,
                                               GrammarRule._unwrap(rule))
        return AnalysisUnit._wrap(c_value)

    def get_from_buffer(self,
                        filename: AnyStr,
                        buffer: AnyStr,
                        charset: Opt[str] = None,
                        reparse: bool = False,
                        rule: str = default_grammar_rule) -> AnalysisUnit:
        """
        Create a new analysis unit for ``Filename`` or return the existing one
        if any. Whether the analysis unit already exists or not, (re)parse it
        from the source code in ``Buffer``.

        ``Rule`` controls which grammar rule is used to parse the unit.

        Use ``Charset`` in order to decode the source. If ``Charset`` is empty
        then use the context's default charset.

        If any failure occurs, such as file opening, decoding, lexing or
        parsing failure, return an analysis unit anyway: errors are described
        as diagnostics of the returned analysis unit.
        """
        _filename = _unwrap_filename(filename)
        _charset = _unwrap_charset(charset)
        _buffer, _charset = _canonicalize_buffer(buffer, _charset)
        c_value = _get_analysis_unit_from_buffer(self._c_value, _filename,
                                                 _charset,
                                                 _buffer, len(_buffer),
                                                 GrammarRule._unwrap(rule))
        return AnalysisUnit._wrap(c_value)


    def discard_errors_in_populate_lexical_env(self,
                                               discard: bool) -> None:
        """
        Debug helper. Set whether ``Property_Error`` exceptions raised in
        ``Populate_Lexical_Env`` should be discarded. They are by default.
        """
        _discard_errors_in_populate_lexical_env(self._c_value, bool(discard))

    class _c_struct(ctypes.Structure):
        _fields_ = [('serial_number', ctypes.c_uint64)]
    _c_type = _hashable_c_pointer(_c_struct)

    @classmethod
    def _wrap(cls, c_value):
        try:
            return cls._context_cache[c_value]
        except KeyError:
            return cls(_c_value=c_value)

    def _check_unit_cache(self):
        """
        If this context has been re-used, invalidate its unit cache.
        """
        serial_number = self._c_value.contents.serial_number
        if self._serial_number != serial_number:
            self._unit_cache = {}
            self._serial_number = serial_number

    



class AnalysisUnit:
    """
    This type represents the analysis of a single file.
    """

    __slots__ = ('_c_value', '_context_link', '_cache_version_number',
                 '_node_cache')

    class TokenIterator:
        """
        Iterator over the tokens in an analysis unit.
        """

        def __init__(self, first: Opt[Token]):
            self.first: Opt[Token] = first

        def __iter__(self) -> AnalysisUnit.TokenIterator:
            return self

        def __next__(self) -> Token:
            if not self.first:
                raise StopIteration()
            result = self.first
            self.first = self.first.next
            return result
        next = __next__

    def __init__(self, context: AnalysisContext, c_value: Any) -> None:
        """
        This constructor is an implementation detail, and is not meant to be
        used directly. Please use AnalysisContext.get_from_* methods to create
        analysis unit instances instead.
        """
        self._c_value = c_value

        # Keep a reference on the owning context so that we keep it alive at
        # least as long as this unit is alive.
        self._context_link = context

        # Store this wrapper in caches for later re-use
        assert c_value not in context._unit_cache
        context._unit_cache[c_value] = self

        self._cache_version_number: Opt[int] = None
        """
        Last version number we saw for this analysis unit wrapper. If it's
        different from `self._unit_version`, it means that the unit was
        reparsed: in this case we need to clear the node cache below (see the
        `_check_node_cache` method).
        """

        self._node_cache: Dict[Tuple[Any, Any, Any], RFLXNode] = {}
        """
        Cache for all node wrappers in this unit. Indexed by couples:
        (c_value, metadata, rebindings).
        """

        self._check_node_cache()

    def __eq__(self, other: Any) -> bool:
        return self._c_value == other._c_value

    def __hash__(self) -> int:
        return hash(self._c_value)

    @property
    def context(self) -> AnalysisContext:
        """
        Return the context that owns this unit.
        """
        return self._context_link

    def reparse(self,
                buffer: Opt[AnyStr] = None,
                charset: Opt[str] = None) -> None:
        """
        Reparse an analysis unit from a buffer, if provided, or from the
        original file otherwise. If ``Charset`` is empty or ``None``, use the
        last charset successfuly used for this unit, otherwise use it to decode
        the content of the source file.

        If any failure occurs, such as decoding, lexing or parsing failure,
        diagnostic are emitted to explain what happened.
        """
        _charset = _unwrap_charset(charset)
        if buffer is None:
            _unit_reparse_from_file(self._c_value, _charset)
        else:
            _buffer, _charset = _canonicalize_buffer(buffer, _charset)
            _unit_reparse_from_buffer(self._c_value, _charset, _buffer,
                                      len(_buffer))

    def populate_lexical_env(
        self,
    ) -> None:
        """
        Create lexical environments for this analysis unit, according to the
        specifications given in the language spec.

        If not done before, it will be automatically called during semantic
        analysis. Calling it before enables one to control where the latency
        occurs.

        Depending on whether errors are discarded (see
        ``Discard_Errors_In_Populate_Lexical_Env``), raise a ``Property_Error``
        on failure.
        """
        if not _unit_populate_lexical_env(
            self._c_value,
        ):
            raise PropertyError()

    @property
    def root(self) -> RFLXNode:
        """
        Return the root node for this unit, or ``None`` if there is none.
        """
        result = _Entity_c_type()
        _unit_root(self._c_value, ctypes.byref(result))
        return RFLXNode._wrap(result)

    @property
    def first_token(self) -> Opt[Token]:
        """
        Return a reference to the first token scanned in this unit.
        """
        result = Token._c_struct()
        _unit_first_token(self._c_value, ctypes.byref(result))
        return Token._wrap(result)

    @property
    def last_token(self) -> Opt[Token]:
        """
        Return a reference to the last token scanned in this unit.
        """
        result = Token._c_struct()
        _unit_last_token(self._c_value, ctypes.byref(result))
        return Token._wrap(result)

    @property
    def text(self) -> str:
        """
        Return the source buffer associated to this unit.
        """
        if self.first_token:
            assert self.last_token
            return Token.text_range(self.first_token, self.last_token)
        else:
            return ""

    @property
    def token_count(self) -> int:
        """
        Return the number of tokens in this unit.
        """
        return _unit_token_count(self._c_value)

    @property
    def trivia_count(self) -> int:
        """
        Return the number of trivias in this unit. This is 0 for units that
        were parsed with trivia analysis disabled.
        """
        return _unit_trivia_count(self._c_value)

    def lookup_token(self, sloc: Sloc) -> Opt[Token]:
        """
        Look for a token in this unit that contains the given source location.
        If this falls before the first token, return the first token. If this
        falls between two tokens, return the token that appears before. If this
        falls after the last token, return the last token. If there is no token
        in this unit, return no token.
        """
        unit = AnalysisUnit._unwrap(self)
        _sloc = Sloc._c_type._unwrap(sloc)
        result = Token._c_struct()
        _unit_lookup_token(unit, ctypes.byref(_sloc), ctypes.byref(result))
        return Token._wrap(result)

    def _dump_lexical_env(self) -> None:
        """
        Debug helper: output the lexical envs for the given analysis unit.
        """
        unit = AnalysisUnit._unwrap(self)
        _unit_dump_lexical_env(unit)

    def iter_tokens(self) -> AnalysisUnit.TokenIterator:
        """
        Iterator over the tokens in an analysis unit.
        """
        return self.TokenIterator(self.first_token)

    @property
    def filename(self) -> str:
        """
        Return the filename this unit is associated to.
        """
        filename = _unit_filename(self._c_value)
        return _unwrap_str(filename)

    @property
    def diagnostics(self) -> List[Diagnostic]:
        """
        Diagnostics for this unit.
        """
        count = _unit_diagnostic_count(self._c_value)
        result = []
        diag = Diagnostic._c_type()
        for i in range(count):
            success = _unit_diagnostic(self._c_value, i, ctypes.byref(diag))
            assert success
            result.append(diag._wrap())
        return result

    def format_gnu_diagnostic(self, d: Diagnostic) -> str:
        """
        Format a diagnostic in a GNU fashion. See
        <https://www.gnu.org/prep/standards/html_node/Errors.html>.
        """
        sloc = d.sloc_range.start
        prefix = f"{os.path.basename(self.filename)}:"
        if sloc:
            prefix += f"{sloc}:"
        return f"{prefix} {d.message}"

    def __repr__(self) -> str:
        return '<AnalysisUnit {}>'.format(repr(
            os.path.basename(self.filename)
        ))

    class _c_struct(ctypes.Structure):
        _fields_ = [('unit_version', ctypes.c_uint64)]
    _c_type = _hashable_c_pointer(_c_struct)

    @classmethod
    def _wrap(cls, c_value):
        if not c_value:
            return None

        # Invalidate the unit cache if needed, then look for an existing
        # wrapper for this unit.
        context = cls._context(c_value)
        context._check_unit_cache()

        try:
            return context._unit_cache[c_value]
        except KeyError:
            return cls(context, c_value)

    @classmethod
    def _unwrap(cls, value):
        if value is None:
            return value
        elif not isinstance(value, cls):
            _raise_type_error(cls.__name__, value)
        else:
            return value._c_value

    @classmethod
    def _context(cls, c_value) -> AnalysisContext:
        ctx = _unit_context(c_value)
        return AnalysisContext._wrap(ctx)

    @property
    def _unit_version(self) -> int:
        return self._c_value.contents.unit_version

    def _check_node_cache(self) -> None:
        """
        If this unit has been reparsed, invalidate its node cache.
        """
        if self._cache_version_number != self._unit_version:
            self._node_cache = {}
            self._cache_version_number = self._unit_version


class Sloc:
    """
    Location in a source file. Line and column numbers are one-based.
    """

    def __init__(self, line: int, column: int):
        assert line >= 0 and column >= 0
        self.line = line
        self.column = column

    def __bool__(self) -> bool:
        return bool(self.line or self.column)

    def __lt__(self, other: Sloc) -> bool:
        # First compare line numbers...
        if self.line < other.line:
            return True
        elif self.line > other.line:
            return False

        # Past this point, we know that both are on the same line, so now
        # compare column numbers.
        else:
            return self.column < other.column

    def __eq__(self, other: Any) -> bool:
        return self.line == other.line and self.column == other.column

    def __hash__(self) -> int:
        return hash((self.line, self.column))

    def __str__(self) -> str:
        return '{}:{}'.format(self.line, self.column)

    def __repr__(self) -> str:
        return '<Sloc {} at {:#x}>'.format(self, id(self))

    class _c_type(ctypes.Structure):
        _fields_ = [("line", ctypes.c_uint32),
                    ("column", ctypes.c_uint16)]

        def _wrap(self) -> Sloc:
            return Sloc(self.line, self.column)

        @classmethod
        def _unwrap(cls, sloc: Sloc) -> Sloc._c_type:
            return cls(sloc.line, sloc.column)


class SlocRange:
    """
    Location of a span of text in a source file.
    """

    def __init__(self, start: Sloc, end: Sloc):
        self.start = start
        self.end = end

    def __bool__(self) -> bool:
        return bool(self.start or self.end)

    def __lt__(self, other: SlocRange) -> bool:
        raise NotImplementedError('SlocRange comparison not supported')

    def __eq__(self, other: Any) -> bool:
        return self.start == other.start and self.end == other.end

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __str__(self) -> str:
        return '{}-{}'.format(self.start, self.end)

    def __repr__(self) -> str:
        return "<SlocRange {}:{}-{}:{}>".format(
            self.start.line, self.start.column,
            self.end.line, self.end.column
        )

    class _c_type(ctypes.Structure):
        _fields_ = [("start", Sloc._c_type),
                    ("end", Sloc._c_type)]

        def _wrap(self) -> SlocRange:
            return SlocRange(self.start._wrap(), self.end._wrap())


class Diagnostic:
    """
    Diagnostic for an analysis unit: cannot open the source file, parsing
    error, ...
    """

    def __init__(self, sloc_range: SlocRange, message: str):
        self.sloc_range = sloc_range
        self.message = message

    @property
    def as_text(self) -> str:
        return (u'{}: {}'.format(self.sloc_range, self.message)
                if self.sloc_range else
                self.message)

    def __str__(self) -> str:
        return self.as_text

    def __repr__(self) -> str:
        return '<Diagnostic {}>'.format(self)


    class _c_type(ctypes.Structure):
        _fields_ = [('sloc_range', SlocRange._c_type),
                    ('message', _text)]

        def _wrap(self) -> Diagnostic:
            return Diagnostic(self.sloc_range._wrap(), self.message._wrap())


class _tdh_c_struct(ctypes.Structure):
    _fields_ = [('version', ctypes.c_uint64)]
_tdh_c_type = _hashable_c_pointer(_tdh_c_struct)


class Token:
    """
    Reference to a token in an analysis unit.
    """

    __slots__ = ("_c_value", "_context_version", "_tdh_version")

    class _c_struct(ctypes.Structure):
        _fields_ = [('context',      AnalysisContext._c_type),
                    ('token_data',   _tdh_c_type),
                    ('token_index',  ctypes.c_int),
                    ('trivia_index', ctypes.c_int)]
    _c_type = _hashable_c_pointer(_c_struct)

    def __init__(self, c_value: Any):
        """
        This constructor is an implementation detail and is not meant to be
        used directly.
        """
        self._c_value = c_value
        self._context_version = c_value.context.contents.serial_number
        self._tdh_version = c_value.token_data.contents.version

    @classmethod
    def _wrap(cls, c_value: Any) -> Opt[Token]:
        return cls(c_value) if c_value.token_data else None

    @classmethod
    def _unwrap(cls, value):
        cls._check_token(value)
        return value._c_value

    def _check_stale_reference(self) -> None:
        # First, check that the reference to the context is not stale
        if (
            self._c_value.context.contents.serial_number
            != self._context_version
        ):
            raise StaleReferenceError("owning context was deallocated")

        # The context is valid, so the token data handler is, too: check that
        # no reparsing occured.
        if self._c_value.token_data.contents.version != self._tdh_version:
            raise StaleReferenceError("owning unit was reparsed")

    @staticmethod
    def _check_token(value: Any) -> None:
        if not isinstance(value, Token):
            raise TypeError('invalid token: {}'.format(value))
        value._check_stale_reference()

    def _check_same_unit(self, other: Token) -> None:
        if self._c_value.token_data != other._c_value.token_data:
            raise ValueError('{} and {} come from different analysis units'
                             .format(self, other))

    @property
    def next(self) -> Opt[Token]:
        """
        Return a reference to the next token in the corresponding analysis
        unit.
        """
        self._check_stale_reference()
        result = self._c_struct()
        _token_next(ctypes.byref(self._c_value), ctypes.byref(result))
        return self._wrap(result)

    @property
    def previous(self) -> Opt[Token]:
        """
        Return a reference to the previous token in the corresponding analysis
        unit.
        """
        self._check_stale_reference()
        result = self._c_struct()
        _token_previous(ctypes.byref(self._c_value), ctypes.byref(result))
        return self._wrap(result)

    def range_until(self, other: Token) -> Iterator[Token]:
        """
        Return an iterator on the list of tokens that spans between ``self``
        and ``other`` (included). This returns an empty list if the first token
        appears after the other one in the source code. Raise a ``ValueError``
        if both tokens come from different analysis units.
        """
        self._check_stale_reference()
        self._check_token(other)
        self._check_same_unit(other)

        # Keep the generator as a nested function so that the above checks are
        # executed when the generator is created, instead of only when its
        # first item is requested.
        #
        # Note that, because the execution of a generator stops and resumes,
        # the tokens may become stale after it resumes: check for stale
        # references at starting and resuming time.
        def generator() -> Iterator[Token]:
            self._check_stale_reference()
            if other < self:
                return

            yield self
            current = self
            while current < other:
                next = current.next
                assert next is not None
                yield next
                self._check_stale_reference()
                current = next
        return generator()

    def is_equivalent(self, other: Token) -> bool:
        """
        Return whether ``L`` and ``R`` are structurally equivalent tokens. This
        means that their position in the stream won't be taken into account,
        only the kind and text of the token.
        """
        self._check_stale_reference()
        self._check_token(other)
        return bool(_token_is_equivalent(
            ctypes.byref(self._c_value), ctypes.byref(other._c_value))
        )

    @property
    def kind(self) -> str:
        """
        Kind for this token.
        """
        self._check_stale_reference()
        kind = _token_get_kind(self._c_value)
        name = _token_kind_name(kind)
        # The _token_kind_name wrapper is already supposed to handle exceptions
        # so this should always return a non-null value.
        assert name
        return _unwrap_str(name)

    @property
    def is_trivia(self) -> bool:
        """
        Return whether this token is a trivia. If it's not, it's a regular
        token.
        """
        self._check_stale_reference()
        return self._c_value.trivia_index != 0

    @property
    def index(self) -> int:
        """
        Zero-based index for this token/trivia. Tokens and trivias get their
        own index space.
        """
        self._check_stale_reference()
        return (self._c_value.token_index - 1
                if self._c_value.trivia_index == 0 else
                self._c_value.trivia_index - 1)

    @property
    def text(self) -> str:
        """
        Return the text of the given token.
        """
        return self.text_range(self, self)

    @classmethod
    def text_range(cls, first: Token, last: Token) -> str:
        """
        Compute the source buffer slice corresponding to the text that spans
        between the ``First`` and ``Last`` tokens (both included). This yields
        an empty slice if ``Last`` actually appears before ``First``.

        This raises a ``ValueError`` if ``First`` and ``Last`` don't belong to
        the same analysis unit.
        """
        cls._check_token(first)
        cls._check_token(last)
        first._check_same_unit(last)
        result = _text()
        success = _token_range_text(
            ctypes.byref(first._c_value),
            ctypes.byref(last._c_value),
            ctypes.byref(result),
        )
        assert success
        return result._wrap() or u''

    @property
    def sloc_range(self) -> SlocRange:
        """
        Return the source location range of the given token.
        """
        self._check_stale_reference()
        result = SlocRange._c_type()
        _token_sloc_range(ctypes.byref(self._c_value), ctypes.byref(result))
        return result._wrap()

    def __eq__(self, other: Any) -> bool:
        """
        Return whether the two tokens refer to the same token in the same unit.

        Note that this does not actually compares the token data.
        """
        return (isinstance(other, Token)
                and self._identity_tuple == other._identity_tuple)

    def __hash__(self) -> int:
        return hash(self._identity_tuple)

    def __repr__(self) -> str:
        self._check_stale_reference()
        return '<Token {}{} at {}>'.format(
            self.kind,
            ' {}'.format(repr(self.text)) if self.text else '',
            self.sloc_range
        )

    def __lt__(self, other: Opt[Token]):
        """
        Consider that None comes before all tokens. Then, sort by unit, token
        index, and trivia index.
        """
        self._check_stale_reference()

        # None always comes first
        if other is None:
            return False

        self._check_token(other)
        self._check_same_unit(other)
        return self._identity_tuple < other._identity_tuple

    def __le__(self, other: Opt[Token]) -> bool:
        return self == other or self < other

    def __gt__(self, other: Opt[Token]) -> bool:
        return not (self <= other)

    def __ge__(self, other: Opt[Token]) -> bool:
        return not (self < other)

    def to_data(self) -> dict:
        """
        Return a dict representation of this Token.
        """
        return {"kind": "Token", "token_kind": self.kind, "text": self.text}

    @property
    def _identity_tuple(self) -> Tuple[Any, int, int]:
        """
        Return a tuple that return a tuple that contains "identity" information
        for this token. Think of it as a database primary key.

        This property is for internal use only.
        """
        return (
            self._c_value.token_data,
            self._c_value.token_index,
            self._c_value.trivia_index
        )


class FileReader:
    """
    Interface to override how source files are fetched and decoded.
    """

    def __init__(self, c_value: Any):
        """
        This constructor is an implementation detail, and is not meant to be
        used directly.
        """
        self._c_value = c_value

    def __del__(self) -> None:
        _dec_ref_file_reader(self._c_value)





class UnitProvider:
    """
    Interface to fetch analysis units from a name and a unit kind.

    The unit provider mechanism provides an abstraction which assumes that to
    any couple (unit name, unit kind) we can associate at most one source file.
    This means that several couples can be associated to the same source file,
    but on the other hand, only one one source file can be associated to a
    couple.

    This is used to make the semantic analysis able to switch from one analysis
    units to another.

    See the documentation of each unit provider for the exact semantics of the
    unit name/kind information.
    """

    def __init__(self, c_value: Any):
        """
        This constructor is an implementation detail, and is not meant to be
        used directly.
        """
        self._c_value = c_value

    def __del__(self) -> None:
        _dec_ref_unit_provider(self._c_value)





class RFLXNode:
    """
    Root node class for the RecordFlux language.
    """

    is_list_type = False
    __slots__ = ('_unprotected_c_value', '_node_c_value', '_metadata',
                 '_rebindings', '_unprotected_getitem_cache', '_unit',
                 '_unit_version', '_rebindings_version')

    _kind_name: str
    _field_names: Tuple[str, ...]

    
    

    
    @property
    def parent(
        self
    ) -> RFLXNode:
        """
        Return the syntactic parent for this node. Return null for the root
        node.
        """
        

        


        
        c_result = self._eval_field(_Entity_c_type(), _r_f_l_x_node_parent)
        result = RFLXNode._wrap(c_result)


        return result
    
    def parents(
        self, with_self: bool = True
    ) -> List[RFLXNode]:
        """
        Return an array that contains the lexical parents, this node included
        iff ``with_self`` is True. Nearer parents are first in the list.
        """
        

        

        unwrapped_with_self = bool(with_self)

        
        c_result = self._eval_field(_RFLXNodeArrayConverter.c_type(), _r_f_l_x_node_parents, unwrapped_with_self)
        result = _RFLXNodeArrayConverter.wrap(c_result, False)


        return result
    
    @property
    def children(
        self
    ) -> List[RFLXNode]:
        """
        Return an array that contains the direct lexical children.

        .. warning:: This constructs a whole array every-time you call it, and
           as such is less efficient than calling the ``Child`` built-in.
        """
        

        


        
        c_result = self._eval_field(_RFLXNodeArrayConverter.c_type(), _r_f_l_x_node_children)
        result = _RFLXNodeArrayConverter.wrap(c_result, False)


        return result
    
    @property
    def token_start(
        self
    ) -> Opt[Token]:
        """
        Return the first token used to parse this node.
        """
        

        


        
        c_result = self._eval_field(Token._c_struct(), _r_f_l_x_node_token_start)
        result = Token._wrap(c_result)


        return result
    
    @property
    def token_end(
        self
    ) -> Opt[Token]:
        """
        Return the last token used to parse this node.
        """
        

        


        
        c_result = self._eval_field(Token._c_struct(), _r_f_l_x_node_token_end)
        result = Token._wrap(c_result)


        return result
    
    @property
    def child_index(
        self
    ) -> int:
        """
        Return the 0-based index for Node in its parent's children.
        """
        

        


        
        c_result = self._eval_field(ctypes.c_int(), _r_f_l_x_node_child_index)
        result = c_result.value


        return result
    
    @property
    def previous_sibling(
        self
    ) -> RFLXNode:
        """
        Return the node's previous sibling, or null if there is no such
        sibling.
        """
        

        


        
        c_result = self._eval_field(_Entity_c_type(), _r_f_l_x_node_previous_sibling)
        result = RFLXNode._wrap(c_result)


        return result
    
    @property
    def next_sibling(
        self
    ) -> RFLXNode:
        """
        Return the node's next sibling, or null if there is no such sibling.
        """
        

        


        
        c_result = self._eval_field(_Entity_c_type(), _r_f_l_x_node_next_sibling)
        result = RFLXNode._wrap(c_result)


        return result
    
    @property
    def unit(
        self
    ) -> AnalysisUnit:
        """
        Return the analysis unit owning this node.
        """
        

        


        
        c_result = self._eval_field(AnalysisUnit._c_type(), _r_f_l_x_node_unit)
        result = AnalysisUnit._wrap(c_result)


        return result
    
    @property
    def is_ghost(
        self
    ) -> bool:
        """
        Return whether the node is a ghost.

        Unlike regular nodes, ghost nodes cover no token in the input source:
        they are logically located instead between two tokens. Both the
        ``token_start`` and the ``token_end`` of all ghost nodes is the token
        right after this logical position.
        """
        

        


        
        c_result = self._eval_field(ctypes.c_uint8(), _r_f_l_x_node_is_ghost)
        result = bool(c_result.value)


        return result
    
    @property
    def full_sloc_image(
        self
    ) -> str:
        """
        Return a string containing the filename + the sloc in GNU conformant
        format. Useful to create diagnostics from a node.
        """
        

        


        
        c_result = self._eval_field(_String.c_type(), _r_f_l_x_node_full_sloc_image)
        result = _String.wrap(c_result)


        return result

    _field_names = () + (
    )




    def __init__(self, c_value: Any, node_c_value: Any, rebindings: Any):
        """
        This constructor is an implementation detail, and is not meant to be
        used directly. For now, the creation of AST nodes can happen only as
        part of the parsing of an analysis unit.
        """

        self._unprotected_c_value = c_value

        # Access to these fields is unprotected from stale references, but it
        # is supposed to be used only in _id_tuple, which itself should not be
        # used outside of hashing/equality use cases.
        self._node_c_value = node_c_value
        self._rebindings = rebindings

        self._unprotected_getitem_cache: Dict[int,
                                              Opt[RFLXNode]] = {}
        """
        Cache for the __getitem__ override.
        """

        # Information to check before accessing node data that it is still
        # valid.
        self._unit = self._fetch_unit(c_value)
        self._unit_version = self._unit._unit_version
        self._rebindings_version = (
            rebindings.contents.version if rebindings else None
        )

    def _check_stale_reference(self) -> None:
        # We have a reference to the owning unit, so there is no need to
        # check that the unit and the context are still valid. Just check that
        # the unit has not been reparsed.
        if self._unit._unit_version != self._unit_version:
            raise StaleReferenceError("unit was reparsed")

        # Also check that the rebindings are still valid
        if (
            self._rebindings
            and self._rebindings.contents.version != self._rebindings_version
        ):
            raise StaleReferenceError("related unit was reparsed")

    @property
    def _c_value(self) -> Any:
        self._check_stale_reference()
        return self._unprotected_c_value

    @property
    def _getitem_cache(self) -> Dict[int, Opt[RFLXNode]]:
        self._check_stale_reference()
        return self._unprotected_getitem_cache

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, RFLXNode)
            and bool(
                _node_is_equivalent(
                    ctypes.byref(self._unsafe_unwrap),
                    ctypes.byref(other._unsafe_unwrap)
                )
            )
        )

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return _node_hash(ctypes.byref(self._unsafe_unwrap))

    @property
    def kind_name(self) -> str:
        """
        Return the kind of this node.
        """
        return self._kind_name

    @property
    def is_token_node(self) -> bool:
        """
        Return whether this node is a node that contains only a single token.
        """
        node = self._unwrap(self)
        return bool(_node_is_token_node(ctypes.byref(node)))

    @property
    def is_synthetic(self) -> bool:
        """
        Return whether this node is synthetic.
        """
        node = self._unwrap(self)
        return bool(_node_is_synthetic(ctypes.byref(node)))

    @property
    def sloc_range(self) -> SlocRange:
        """
        Return the spanning source location range for this node.

        Note that this returns the sloc of the parent for synthetic nodes.
        """
        node = self._unwrap(self)
        result = SlocRange._c_type()
        _node_sloc_range(ctypes.byref(node), ctypes.byref(result))
        return result._wrap()

    @property
    def text(self) -> str:
        """
        Return the source buffer slice corresponding to the text that spans
        between the first and the last tokens of this node.

        Note that this returns the empty string for synthetic nodes.
        """
        node = self._unwrap(self)
        result = _text()
        _node_text(ctypes.byref(node), ctypes.byref(result))
        return result._wrap()

    @property
    def image(self) -> str:
        """
        Return a representation of this node as a string.
        """
        c_node = self._unwrap(self)
        c_result = _text()
        _node_image(ctypes.byref(c_node), ctypes.byref(c_result))
        return c_result._wrap()

    def lookup(self, sloc: Sloc) -> Opt[RFLXNode]:
        """
        Return the bottom-most node from in ``Node`` and its children which
        contains ``Sloc``, or ``None`` if there is none.
        """
        node = self._unwrap(self)
        c_sloc = Sloc._c_type._unwrap(sloc)
        result = _Entity_c_type()
        _lookup_in_node(ctypes.byref(node), ctypes.byref(c_sloc),
                        ctypes.byref(result))
        return RFLXNode._wrap(result)

    def __bool__(self) -> bool:
        """
        Return always True so that checking a node against None can be done as
        simply as:

        .. code::

           if node:
               ...
        """
        return True

    def __iter__(self) -> Iterator[Opt[RFLXNode]]:
        """
        Return an iterator on the children of this node.
        """
        for i in range(len(self)):
            yield self[i]

    def __len__(self) -> int:
        """
        Return the number of RFLXNode children this node has.
        """
        node = self._unwrap(self)
        return _node_children_count(ctypes.byref(node))

    def __getitem__(self, key: int) -> Opt[RFLXNode]:
        """
        Return the Nth RFLXNode child this node has.

        This handles negative indexes the same way Python lists do. Raise an
        IndexError if "key" is out of range.
        """
        if not isinstance(key, int):
            msg = ('RFLXNode children are integer-indexed'
                   ' (got {})').format(type(key))
            raise TypeError(msg)

        if key < 0:
            key += len(self)

        if key in self._getitem_cache:
            return self._getitem_cache[key]

        node = self._unwrap(self)
        result_struct = _Entity_c_type()
        success = _node_child(
            ctypes.byref(node), key, ctypes.byref(result_struct)
        )
        if not success:
            raise IndexError('child index out of range')
        else:
            result = RFLXNode._wrap(result_struct)
            self._getitem_cache[key] = result
            return result

    def iter_fields(self) -> Iterator[Tuple[str, Opt[RFLXNode]]]:
        """
        Iterate through all the fields this node contains.

        Return an iterator that yields (name, value) couples for all abstract
        fields in this node. If "self" is a list, field names will be
        "item_{n}" with "n" being the index.
        """
        if self.is_list_type:
            for i, value in enumerate(self):
                yield ('item_{}'.format(i), value)
        else:
            for field_name in self._field_names:
                yield (field_name, getattr(self, '{}'.format(field_name)))

    def dump_str(self) -> str:
        """
        Dump the sub-tree to a string in a human-readable format.
        """
        output = io.StringIO()
        self.dump(file=output)
        ret = output.getvalue()
        output.close()
        return ret

    def dump(self, indent: str = '', file: IO[str] = sys.stdout) -> None:
        """
        Dump the sub-tree in a human-readable format on the given file.

        :param str indent: Prefix printed on each line during the dump.

        :param file file: File in which the dump must occur.
        """

        def print_node(name, value):
            if isinstance(value, RFLXNode):
                print('{}{}:'.format(indent, name), file=file)
                value.dump(indent + '  ', file)
            else:
                print('{}{}: {}'.format(indent, name, value), file=file)

        node_repr = str(self)[1:-1]
        print('{}{}{}'.format(
            indent, node_repr,
            ': {}'.format(self.text) if self.is_token_node else ''
        ), file=file)
        indent = indent + '|'
        if self.is_list_type:
            for i, value in enumerate(self):
                print_node("item_{}".format(i), value)
        else:
            for name, value in self.iter_fields():
                print_node(name, value)

    def findall(
        self,
        ast_type_or_pred: Union[Type[RFLXNode],
                                Callable[[RFLXNode], bool]],
        **kwargs: Any
    ) -> List[RFLXNode]:
        """
        Helper for finditer that will return all results as a list. See
        finditer's documentation for more details.
        """
        return list(self.finditer(ast_type_or_pred, **kwargs))

    def find(
        self,
        ast_type_or_pred: Union[Type[RFLXNode],
                                Callable[[RFLXNode], bool]],
        **kwargs: Any
    ) -> Opt[RFLXNode]:
        """
        Helper for finditer that will return only the first result. See
        finditer's documentation for more details.
        """
        try:
            return next(self.finditer(ast_type_or_pred, **kwargs))
        except StopIteration:
            return None

    def finditer(
        self,
        ast_type_or_pred: Union[Type[RFLXNode],
                                Callable[[RFLXNode], bool]],
        **kwargs: Any
    ) -> Iterator[RFLXNode]:
        """
        Find every node corresponding to the passed predicates.

        :param ast_type_or_pred: If supplied with a subclass of RFLXNode, will
           constrain the resulting collection to only the instances of this
           type or any subclass. If supplied with a predicate, it will apply
           the predicate on every node and keep only the ones for which it
           returns True. If supplied with a list of subclasses of RFLXNode, it
           will match all instances of any of them.

        :param kwargs: Allows the user to filter on attributes of the node. For
           every key value association, if the node has an attribute of name
           key that has the specified value, then the child is kept.
        """
        # Create a "pred" function to use as the node filter during the
        # traversal.
        if isinstance(ast_type_or_pred, type):
            sought_type = ast_type_or_pred
            pred = lambda node: isinstance(node, sought_type)
        elif isinstance(ast_type_or_pred, collections.abc.Sequence):
            sought_types = ast_type_or_pred
            pred = lambda node: isinstance(node, tuple(sought_types))
        else:
            pred = ast_type_or_pred

        def match(left, right):
            """
            :param left: Node child to match.
            :param right: Matcher, coming from ``kwargs``.
            """
            if left is None:
                return
            if hasattr(left, "match"):
                return left.match(right)
            else:
                return left == right

        def helper(node):
            for child in node:
                if child is not None:
                    if pred(child):
                        if not kwargs:
                            yield child
                        elif all([match(getattr(child, key, None), val)
                                  for key, val in kwargs.items()]):
                            yield child
                    for c in helper(child):
                        if c is not None:
                            yield c

        return helper(self)

    @property
    def parent_chain(self) -> List[RFLXNode]:
        """
        Return the parent chain of self. Self will be the first element,
        followed by the first parent, then this parent's parent, etc.
        """
        def _parent_chain(node):
            yield node
            if node.parent is not None:
                for p in _parent_chain(node.parent):
                    yield p

        return list(_parent_chain(self))

    def __repr__(self) -> str:
        return self.image

    @property
    def tokens(self) -> Iterator[Token]:
        """
        Return an iterator on the range of tokens that self encompasses.
        """
        start = self.token_start
        end = self.token_end

        # All nodes have non-null start/end tokens
        assert start is not None
        assert end is not None

        while not start == end:
            yield start
            next = start.next
            assert next is not None
            start = next
        yield end

    def to_data(self) -> Union[list, dict]:
        """
        Return a nested python data-structure, constituted only of standard
        data types (dicts, lists, strings, ints, etc), and representing the
        portion of the AST corresponding to this node.
        """
        if self.is_list_type:
            return [i.to_data() for i in self if i is not None]
        else:
            return {n: v.to_data()
                    for n, v in self.iter_fields()
                    if v is not None}

    def to_json(self) -> str:
        """
        Return a JSON representation of this node.
        """
        return json.dumps(self.to_data())

    def is_a(self, *types: Type[RFLXNode]) -> bool:
        """
        Shortcut for isinstance(self, types).
        :rtype: bool
        """
        return isinstance(self, tuple(types))

    if TYPE_CHECKING:
        T = TypeVar('T', bound=RFLXNode)

    def cast(self, typ: Type[T]) -> T:
        """
        Fluent interface style method. Return ``self``, raise an error if self
        is not of type ``typ``.

        :type typ: () -> T
        :rtype: T
        """
        assert isinstance(self, typ)
        return self

    _node_c_type = _hashable_c_pointer()

    @classmethod
    def _wrap(cls, c_value):
        """
        Internal helper to wrap a low-level entity value into an instance of
        the the appropriate high-level Python wrapper subclass.
        """
        node_c_value = c_value.node
        if not node_c_value:
            return None

        rebindings = c_value.info.rebindings
        metadata = c_value.info.md

        # Look for an already existing wrapper for this node
        cache_key = (node_c_value, metadata, rebindings)
        unit = cls._fetch_unit(c_value)
        unit._check_node_cache()
        try:
            return unit._node_cache[cache_key]
        except KeyError:
            pass

        # Pick the right subclass to materialize this node in Python
        kind = _node_kind(ctypes.byref(c_value))
        result = _kind_to_astnode_cls[kind](c_value, node_c_value, rebindings)
        unit._node_cache[cache_key] = result
        return result

    @classmethod
    def _wrap_bare_node(cls, c_value: Any) -> Opt[RFLXNode]:
        return cls._wrap(_Entity_c_type.from_bare_node(c_value))

    @classmethod
    def _unwrap(cls, py_value: Opt[RFLXNode]) -> Any:
        """
        Internal helper to unwrap a high-level ASTNode instance into a
        low-level value. Raise a TypeError if the input value has unexpected
        type.
        """
        if py_value is None:
            return _Entity_c_type._null_value
        elif not isinstance(py_value, RFLXNode):
            _raise_type_error('RFLXNode', py_value)
        else:
            return py_value._c_value

    @property
    def _unsafe_unwrap(self) -> Any:
        """
        Unsafe version of _unwrap, meant for internal uses where we don't want
        to check whether the reference is stale or not.
        """
        return self._unprotected_c_value

    @property
    def _unwrap_einfo(self):
        return self._c_value.info

    @classmethod
    def _fetch_unit(cls, c_value: Any) -> AnalysisUnit:
        return AnalysisUnit._wrap(_node_unit(ctypes.byref(c_value)))

    def _eval_field(self, c_result: Any, c_accessor: Any, *c_args: Any) -> Any:
        """
        Internal helper to evaluate low-level field accessors/properties.

        This calls "c_accessor" on this node with the input arguments and puts
        the result in "c_result". This raises a PropertyError if the evaluation
        failed. Return "c_result" for convenience.
        """
        args = (self._unwrap(self), ) + c_args + (ctypes.byref(c_result), )
        if not c_accessor(*args):
            raise PropertyError()
        return c_result

    def _eval_astnode_field(self, c_accessor: Any) -> Any:
        """
        Internal helper. Wrapper around _eval_field for fields that return an
        AST node and that accept no explicit argument. This is useful as it's
        the most common case of field, so using this wrapper reduces generated
        code length.
        """
        return RFLXNode._wrap(
            self._eval_field(_Entity_c_type(), c_accessor)
        )




class AbstractID(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for identifiers.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class ID(AbstractID):
    """
    Subclass of :py:class:`AbstractID`.

    Qualified identifiers which may optionally have a package part (e.g.
    "Pkg::Foo", "Foo").
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_package(
        self
    ) -> UnqualifiedID:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_i_d_f_package)



        return result
    
    @property
    def f_name(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_i_d_f_name)



        return result

    _field_names = AbstractID._field_names + (
        "f_package",
        "f_name",
    )

    _kind_name = 'ID'






class UnqualifiedID(AbstractID):
    """
    Subclass of :py:class:`AbstractID`.

    Simple, unqualified identifiers, i.e. identifiers without a package part
    (e.g. "Foo").
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = AbstractID._field_names + (
    )

    _kind_name = 'UnqualifiedID'






class Aspect(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_aspect_f_identifier)



        return result
    
    @property
    def f_value(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_aspect_f_value)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_value",
    )

    _kind_name = 'Aspect'






class Attr(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Attribute kind.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class AttrFirst(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrFirst'






class AttrHasData(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrHasData'






class AttrHead(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrHead'






class AttrLast(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrLast'






class AttrOpaque(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrOpaque'






class AttrPresent(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrPresent'






class AttrSize(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrSize'






class AttrValid(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrValid'






class AttrValidChecksum(Attr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Attr._field_names + (
    )

    _kind_name = 'AttrValidChecksum'






class AttrStmt(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Attribute statement kind.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class AttrStmtAppend(AttrStmt):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = AttrStmt._field_names + (
    )

    _kind_name = 'AttrStmtAppend'






class AttrStmtExtend(AttrStmt):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = AttrStmt._field_names + (
    )

    _kind_name = 'AttrStmtExtend'






class AttrStmtRead(AttrStmt):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = AttrStmt._field_names + (
    )

    _kind_name = 'AttrStmtRead'






class AttrStmtWrite(AttrStmt):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = AttrStmt._field_names + (
    )

    _kind_name = 'AttrStmtWrite'






class BaseAggregate(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for message aggregates.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class MessageAggregateAssociations(BaseAggregate):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_associations(
        self
    ) -> MessageAggregateAssociationList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_aggregate_associations_f_associations)



        return result

    _field_names = BaseAggregate._field_names + (
        "f_associations",
    )

    _kind_name = 'MessageAggregateAssociations'






class NullMessageAggregate(BaseAggregate):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = BaseAggregate._field_names + (
    )

    _kind_name = 'NullMessageAggregate'






class BaseChecksumVal(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for checksum values.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class ChecksumVal(BaseChecksumVal):
    """
    Subclass of :py:class:`BaseChecksumVal`.

    Single checksum value.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_data(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_checksum_val_f_data)



        return result

    _field_names = BaseChecksumVal._field_names + (
        "f_data",
    )

    _kind_name = 'ChecksumVal'






class ChecksumValueRange(BaseChecksumVal):
    """
    Subclass of :py:class:`BaseChecksumVal`.

    Checksum value range.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_first(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_checksum_value_range_f_first)



        return result
    
    @property
    def f_last(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_checksum_value_range_f_last)



        return result

    _field_names = BaseChecksumVal._field_names + (
        "f_first",
        "f_last",
    )

    _kind_name = 'ChecksumValueRange'






class ByteOrderType(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class ByteOrderTypeHighorderfirst(ByteOrderType):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = ByteOrderType._field_names + (
    )

    _kind_name = 'ByteOrderTypeHighorderfirst'






class ByteOrderTypeLoworderfirst(ByteOrderType):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = ByteOrderType._field_names + (
    )

    _kind_name = 'ByteOrderTypeLoworderfirst'






class ChannelAttribute(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for channel attributes.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class Readable(ChannelAttribute):
    """
    Subclass of :py:class:`ChannelAttribute`.

    Channel attribute (channel can be read).
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = ChannelAttribute._field_names + (
    )

    _kind_name = 'Readable'






class Writable(ChannelAttribute):
    """
    Subclass of :py:class:`ChannelAttribute`.

    Channel attribute (channel can be written).
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = ChannelAttribute._field_names + (
    )

    _kind_name = 'Writable'






class ChecksumAssoc(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Association between checksum field and list of covered fields.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_checksum_assoc_f_identifier)



        return result
    
    @property
    def f_covered_fields(
        self
    ) -> BaseChecksumValList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_checksum_assoc_f_covered_fields)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_covered_fields",
    )

    _kind_name = 'ChecksumAssoc'






class Declaration(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for declarations (types, refinements, sessions).
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class RefinementDecl(Declaration):
    """
    Subclass of :py:class:`Declaration`.

    Refinement declaration (for Message use (Field => Inner_Type)).
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_pdu(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_refinement_decl_f_pdu)



        return result
    
    @property
    def f_field(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_refinement_decl_f_field)



        return result
    
    @property
    def f_sdu(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_refinement_decl_f_sdu)



        return result
    
    @property
    def f_condition(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_refinement_decl_f_condition)



        return result

    _field_names = Declaration._field_names + (
        "f_pdu",
        "f_field",
        "f_sdu",
        "f_condition",
    )

    _kind_name = 'RefinementDecl'






class SessionDecl(Declaration):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_parameters(
        self
    ) -> FormalDeclList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_session_decl_f_parameters)



        return result
    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_session_decl_f_identifier)



        return result
    
    @property
    def f_declarations(
        self
    ) -> LocalDeclList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_session_decl_f_declarations)



        return result
    
    @property
    def f_states(
        self
    ) -> StateList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_session_decl_f_states)



        return result
    
    @property
    def f_end_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_session_decl_f_end_identifier)



        return result

    _field_names = Declaration._field_names + (
        "f_parameters",
        "f_identifier",
        "f_declarations",
        "f_states",
        "f_end_identifier",
    )

    _kind_name = 'SessionDecl'






class TypeDecl(Declaration):
    """
    Subclass of :py:class:`Declaration`.

    Type declaration (type Foo is ...).
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_type_decl_f_identifier)



        return result
    
    @property
    def f_parameters(
        self
    ) -> Parameters:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_type_decl_f_parameters)



        return result
    
    @property
    def f_definition(
        self
    ) -> TypeDef:
        """
        This field can contain one of the following nodes:
        :py:class:`AbstractMessageTypeDef`, :py:class:`EnumerationTypeDef`,
        :py:class:`IntegerTypeDef`, :py:class:`SequenceTypeDef`,
        :py:class:`TypeDerivationDef`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_type_decl_f_definition)



        return result

    _field_names = Declaration._field_names + (
        "f_identifier",
        "f_parameters",
        "f_definition",
    )

    _kind_name = 'TypeDecl'






class Description(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    String description of an entity.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_content(
        self
    ) -> StringLiteral:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_description_f_content)



        return result

    _field_names = RFLXNode._field_names + (
        "f_content",
    )

    _kind_name = 'Description'






class ElementValueAssoc(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Element/value association.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_element_value_assoc_f_identifier)



        return result
    
    @property
    def f_literal(
        self
    ) -> NumericLiteral:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_element_value_assoc_f_literal)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_literal",
    )

    _kind_name = 'ElementValueAssoc'






class Expr(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for expressions.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class Attribute(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`Binding`, :py:class:`Call`,
        :py:class:`CaseExpression`, :py:class:`Comprehension`,
        :py:class:`Conversion`, :py:class:`MessageAggregate`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_attribute_f_expression)



        return result
    
    @property
    def f_kind(
        self
    ) -> Attr:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_attribute_f_kind)



        return result

    _field_names = Expr._field_names + (
        "f_expression",
        "f_kind",
    )

    _kind_name = 'Attribute'






class BinOp(Expr):
    """
    Subclass of :py:class:`Expr`.

    Binary operation.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_left(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_bin_op_f_left)



        return result
    
    @property
    def f_op(
        self
    ) -> Op:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_bin_op_f_op)



        return result
    
    @property
    def f_right(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_bin_op_f_right)



        return result

    _field_names = Expr._field_names + (
        "f_left",
        "f_op",
        "f_right",
    )

    _kind_name = 'BinOp'






class Binding(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`Binding`, :py:class:`Call`,
        :py:class:`CaseExpression`, :py:class:`Comprehension`,
        :py:class:`Conversion`, :py:class:`MessageAggregate`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_binding_f_expression)



        return result
    
    @property
    def f_bindings(
        self
    ) -> TermAssocList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_binding_f_bindings)



        return result

    _field_names = Expr._field_names + (
        "f_expression",
        "f_bindings",
    )

    _kind_name = 'Binding'






class Call(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_call_f_identifier)



        return result
    
    @property
    def f_arguments(
        self
    ) -> ExprList:
        """
        This field contains a list that itself contains one of the following
        nodes: :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_call_f_arguments)



        return result

    _field_names = Expr._field_names + (
        "f_identifier",
        "f_arguments",
    )

    _kind_name = 'Call'






class CaseExpression(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_case_expression_f_expression)



        return result
    
    @property
    def f_choices(
        self
    ) -> ChoiceList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_case_expression_f_choices)



        return result

    _field_names = Expr._field_names + (
        "f_expression",
        "f_choices",
    )

    _kind_name = 'CaseExpression'






class Choice(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_selectors(
        self
    ) -> RFLXNodeList:
        """
        This field contains a list that itself contains one of the following
        nodes: :py:class:`ID`, :py:class:`NumericLiteral`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_choice_f_selectors)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_choice_f_expression)



        return result

    _field_names = Expr._field_names + (
        "f_selectors",
        "f_expression",
    )

    _kind_name = 'Choice'






class Comprehension(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_iterator(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_comprehension_f_iterator)



        return result
    
    @property
    def f_sequence(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_comprehension_f_sequence)



        return result
    
    @property
    def f_condition(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_comprehension_f_condition)



        return result
    
    @property
    def f_selector(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_comprehension_f_selector)



        return result

    _field_names = Expr._field_names + (
        "f_iterator",
        "f_sequence",
        "f_condition",
        "f_selector",
    )

    _kind_name = 'Comprehension'






class ContextItem(Expr):
    """
    Subclass of :py:class:`Expr`.

    Import statement (with Package).
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_item(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_context_item_f_item)



        return result

    _field_names = Expr._field_names + (
        "f_item",
    )

    _kind_name = 'ContextItem'






class Conversion(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_target_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_conversion_f_target_identifier)



        return result
    
    @property
    def f_argument(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_conversion_f_argument)



        return result

    _field_names = Expr._field_names + (
        "f_target_identifier",
        "f_argument",
    )

    _kind_name = 'Conversion'






class MessageAggregate(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_aggregate_f_identifier)



        return result
    
    @property
    def f_values(
        self
    ) -> BaseAggregate:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_aggregate_f_values)



        return result

    _field_names = Expr._field_names + (
        "f_identifier",
        "f_values",
    )

    _kind_name = 'MessageAggregate'






class Negation(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_data(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`NumericLiteral`,
        :py:class:`ParenExpression`, :py:class:`QuantifiedExpression`,
        :py:class:`SelectNode`, :py:class:`SequenceLiteral`,
        :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_negation_f_data)



        return result

    _field_names = Expr._field_names + (
        "f_data",
    )

    _kind_name = 'Negation'






class NumericLiteral(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Expr._field_names + (
    )

    _kind_name = 'NumericLiteral'






class ParenExpression(Expr):
    """
    Subclass of :py:class:`Expr`.

    Parenthesized expression.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_data(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_paren_expression_f_data)



        return result

    _field_names = Expr._field_names + (
        "f_data",
    )

    _kind_name = 'ParenExpression'






class QuantifiedExpression(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_operation(
        self
    ) -> Quantifier:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_quantified_expression_f_operation)



        return result
    
    @property
    def f_parameter_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_quantified_expression_f_parameter_identifier)



        return result
    
    @property
    def f_iterable(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_quantified_expression_f_iterable)



        return result
    
    @property
    def f_predicate(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_quantified_expression_f_predicate)



        return result

    _field_names = Expr._field_names + (
        "f_operation",
        "f_parameter_identifier",
        "f_iterable",
        "f_predicate",
    )

    _kind_name = 'QuantifiedExpression'






class SelectNode(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`Binding`, :py:class:`Call`,
        :py:class:`CaseExpression`, :py:class:`Comprehension`,
        :py:class:`Conversion`, :py:class:`MessageAggregate`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_select_node_f_expression)



        return result
    
    @property
    def f_selector(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_select_node_f_selector)



        return result

    _field_names = Expr._field_names + (
        "f_expression",
        "f_selector",
    )

    _kind_name = 'SelectNode'






class SequenceLiteral(Expr):
    """
    Subclass of :py:class:`Expr`.

    Base class for sequence literals (strings, sequence aggregates).
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Expr._field_names + (
    )







class Concatenation(SequenceLiteral):
    """
    Subclass of :py:class:`SequenceLiteral`.

    Concatenation of aggregates or string literals.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_left(
        self
    ) -> SequenceLiteral:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_concatenation_f_left)



        return result
    
    @property
    def f_right(
        self
    ) -> SequenceLiteral:
        """
        This field can contain one of the following nodes:
        :py:class:`SequenceAggregate`, :py:class:`StringLiteral`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_concatenation_f_right)



        return result

    _field_names = SequenceLiteral._field_names + (
        "f_left",
        "f_right",
    )

    _kind_name = 'Concatenation'






class SequenceAggregate(SequenceLiteral):
    """
    Subclass of :py:class:`SequenceLiteral`.

    List of literal sequence values.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_values(
        self
    ) -> NumericLiteralList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_sequence_aggregate_f_values)



        return result

    _field_names = SequenceLiteral._field_names + (
        "f_values",
    )

    _kind_name = 'SequenceAggregate'






class StringLiteral(SequenceLiteral):
    """
    Subclass of :py:class:`SequenceLiteral`.

    Double-quoted string literal.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = SequenceLiteral._field_names + (
    )

    _kind_name = 'StringLiteral'






class Variable(Expr):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_variable_f_identifier)



        return result

    _field_names = Expr._field_names + (
        "f_identifier",
    )

    _kind_name = 'Variable'






class FormalDecl(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for generic formal session declarations.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class FormalChannelDecl(FormalDecl):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_formal_channel_decl_f_identifier)



        return result
    
    @property
    def f_parameters(
        self
    ) -> ChannelAttributeList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_formal_channel_decl_f_parameters)



        return result

    _field_names = FormalDecl._field_names + (
        "f_identifier",
        "f_parameters",
    )

    _kind_name = 'FormalChannelDecl'






class FormalFunctionDecl(FormalDecl):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_formal_function_decl_f_identifier)



        return result
    
    @property
    def f_parameters(
        self
    ) -> Parameters:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_formal_function_decl_f_parameters)



        return result
    
    @property
    def f_return_type_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_formal_function_decl_f_return_type_identifier)



        return result

    _field_names = FormalDecl._field_names + (
        "f_identifier",
        "f_parameters",
        "f_return_type_identifier",
    )

    _kind_name = 'FormalFunctionDecl'






class LocalDecl(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for session or state local declarations.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class RenamingDecl(LocalDecl):
    """
    Subclass of :py:class:`LocalDecl`.

    Session renaming declaration.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_renaming_decl_f_identifier)



        return result
    
    @property
    def f_type_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_renaming_decl_f_type_identifier)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_renaming_decl_f_expression)



        return result

    _field_names = LocalDecl._field_names + (
        "f_identifier",
        "f_type_identifier",
        "f_expression",
    )

    _kind_name = 'RenamingDecl'






class VariableDecl(LocalDecl):
    """
    Subclass of :py:class:`LocalDecl`.

    Session variable declaration.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_variable_decl_f_identifier)



        return result
    
    @property
    def f_type_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_variable_decl_f_type_identifier)



        return result
    
    @property
    def f_initializer(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_variable_decl_f_initializer)



        return result

    _field_names = LocalDecl._field_names + (
        "f_identifier",
        "f_type_identifier",
        "f_initializer",
    )

    _kind_name = 'VariableDecl'






class MessageAggregateAssociation(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_aggregate_association_f_identifier)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_aggregate_association_f_expression)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_expression",
    )

    _kind_name = 'MessageAggregateAssociation'






class MessageAspect(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for message aspects.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class ByteOrderAspect(MessageAspect):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_byte_order(
        self
    ) -> ByteOrderType:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_byte_order_aspect_f_byte_order)



        return result

    _field_names = MessageAspect._field_names + (
        "f_byte_order",
    )

    _kind_name = 'ByteOrderAspect'






class ChecksumAspect(MessageAspect):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_associations(
        self
    ) -> ChecksumAssocList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_checksum_aspect_f_associations)



        return result

    _field_names = MessageAspect._field_names + (
        "f_associations",
    )

    _kind_name = 'ChecksumAspect'






class MessageField(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_f_identifier)



        return result
    
    @property
    def f_type_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_f_type_identifier)



        return result
    
    @property
    def f_type_arguments(
        self
    ) -> TypeArgumentList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_f_type_arguments)



        return result
    
    @property
    def f_aspects(
        self
    ) -> AspectList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_f_aspects)



        return result
    
    @property
    def f_condition(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_message_field_f_condition)



        return result
    
    @property
    def f_thens(
        self
    ) -> ThenNodeList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_f_thens)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_type_identifier",
        "f_type_arguments",
        "f_aspects",
        "f_condition",
        "f_thens",
    )

    _kind_name = 'MessageField'






class MessageFields(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_initial_field(
        self
    ) -> NullMessageField:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_message_fields_f_initial_field)



        return result
    
    @property
    def f_fields(
        self
    ) -> MessageFieldList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_fields_f_fields)



        return result

    _field_names = RFLXNode._field_names + (
        "f_initial_field",
        "f_fields",
    )

    _kind_name = 'MessageFields'






class NullMessageField(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_thens(
        self
    ) -> ThenNodeList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_null_message_field_f_thens)



        return result

    _field_names = RFLXNode._field_names + (
        "f_thens",
    )

    _kind_name = 'NullMessageField'






class Op(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Operators for binary expressions.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class OpAdd(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpAdd'






class OpAnd(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpAnd'






class OpDiv(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpDiv'






class OpEq(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpEq'






class OpGe(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpGe'






class OpGt(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpGt'






class OpIn(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpIn'






class OpLe(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpLe'






class OpLt(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpLt'






class OpMod(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpMod'






class OpMul(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpMul'






class OpNeq(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpNeq'






class OpNotin(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpNotin'






class OpOr(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpOr'






class OpPow(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpPow'






class OpSub(Op):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Op._field_names + (
    )

    _kind_name = 'OpSub'






class PackageNode(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_package_node_f_identifier)



        return result
    
    @property
    def f_declarations(
        self
    ) -> DeclarationList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_package_node_f_declarations)



        return result
    
    @property
    def f_end_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_package_node_f_end_identifier)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_declarations",
        "f_end_identifier",
    )

    _kind_name = 'PackageNode'






class Parameter(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_parameter_f_identifier)



        return result
    
    @property
    def f_type_identifier(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_parameter_f_type_identifier)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_type_identifier",
    )

    _kind_name = 'Parameter'






class Parameters(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_parameters(
        self
    ) -> ParameterList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_parameters_f_parameters)



        return result

    _field_names = RFLXNode._field_names + (
        "f_parameters",
    )

    _kind_name = 'Parameters'






class Quantifier(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Quantifier kind.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class QuantifierAll(Quantifier):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Quantifier._field_names + (
    )

    _kind_name = 'QuantifierAll'






class QuantifierSome(Quantifier):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = Quantifier._field_names + (
    )

    _kind_name = 'QuantifierSome'






class RFLXNodeBaseList(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class AspectList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Aspect.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'AspectList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[Aspect]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> Aspect:
        return super().__getitem__(index)  # type: ignore





class BaseChecksumValList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of BaseChecksumVal.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'BaseChecksumValList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[BaseChecksumVal]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> BaseChecksumVal:
        return super().__getitem__(index)  # type: ignore





class ChannelAttributeList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of ChannelAttribute.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ChannelAttributeList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[ChannelAttribute]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> ChannelAttribute:
        return super().__getitem__(index)  # type: ignore





class ChecksumAssocList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of ChecksumAssoc.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ChecksumAssocList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[ChecksumAssoc]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> ChecksumAssoc:
        return super().__getitem__(index)  # type: ignore





class ChoiceList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Choice.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ChoiceList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[Choice]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> Choice:
        return super().__getitem__(index)  # type: ignore





class ConditionalTransitionList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of ConditionalTransition.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ConditionalTransitionList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[ConditionalTransition]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> ConditionalTransition:
        return super().__getitem__(index)  # type: ignore





class ContextItemList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of ContextItem.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ContextItemList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[ContextItem]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> ContextItem:
        return super().__getitem__(index)  # type: ignore





class DeclarationList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Declaration.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'DeclarationList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[Declaration]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> Declaration:
        return super().__getitem__(index)  # type: ignore





class ElementValueAssocList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of ElementValueAssoc.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ElementValueAssocList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[ElementValueAssoc]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> ElementValueAssoc:
        return super().__getitem__(index)  # type: ignore





class ExprList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Expr.

    This list node can contain one of the following nodes:
    :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
    :py:class:`Call`, :py:class:`CaseExpression`, :py:class:`Comprehension`,
    :py:class:`Conversion`, :py:class:`MessageAggregate`, :py:class:`Negation`,
    :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
    :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
    :py:class:`SequenceLiteral`, :py:class:`Variable`
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ExprList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[Expr]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> Expr:
        return super().__getitem__(index)  # type: ignore





class FormalDeclList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of FormalDecl.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'FormalDeclList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[FormalDecl]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> FormalDecl:
        return super().__getitem__(index)  # type: ignore





class LocalDeclList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of LocalDecl.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'LocalDeclList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[LocalDecl]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> LocalDecl:
        return super().__getitem__(index)  # type: ignore





class MessageAggregateAssociationList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of MessageAggregateAssociation.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'MessageAggregateAssociationList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[MessageAggregateAssociation]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> MessageAggregateAssociation:
        return super().__getitem__(index)  # type: ignore





class MessageAspectList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of MessageAspect.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'MessageAspectList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[MessageAspect]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> MessageAspect:
        return super().__getitem__(index)  # type: ignore





class MessageFieldList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of MessageField.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'MessageFieldList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[MessageField]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> MessageField:
        return super().__getitem__(index)  # type: ignore





class NumericLiteralList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of NumericLiteral.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'NumericLiteralList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[NumericLiteral]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> NumericLiteral:
        return super().__getitem__(index)  # type: ignore





class ParameterList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Parameter.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ParameterList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[Parameter]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> Parameter:
        return super().__getitem__(index)  # type: ignore





class RFLXNodeList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of RFLXNode.

    This list node can contain one of the following nodes: :py:class:`ID`,
    :py:class:`NumericLiteral`
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'RFLXNodeList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[RFLXNode]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> RFLXNode:
        return super().__getitem__(index)  # type: ignore





class StateList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of State.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'StateList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[State]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> State:
        return super().__getitem__(index)  # type: ignore





class StatementList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Statement.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'StatementList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[Statement]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> Statement:
        return super().__getitem__(index)  # type: ignore





class TermAssocList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of TermAssoc.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'TermAssocList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[TermAssoc]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> TermAssoc:
        return super().__getitem__(index)  # type: ignore





class ThenNodeList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of Then.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'ThenNodeList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[ThenNode]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> ThenNode:
        return super().__getitem__(index)  # type: ignore





class TypeArgumentList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of TypeArgument.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'TypeArgumentList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[TypeArgument]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> TypeArgument:
        return super().__getitem__(index)  # type: ignore





class UnqualifiedIDList(RFLXNodeBaseList):
    """
    Subclass of :py:class:`RFLXNodeBaseList`.

    List of UnqualifiedID.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNodeBaseList._field_names + (
    )

    _kind_name = 'UnqualifiedIDList'

    is_list_type = True

    def __iter__(
        self
    ) -> Iterator[UnqualifiedID]:
        return super().__iter__()  # type: ignore

    def __getitem__(
        self,
        index: int
    ) -> UnqualifiedID:
        return super().__getitem__(index)  # type: ignore





class Specification(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    RecordFlux specification.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_context_clause(
        self
    ) -> ContextItemList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_specification_f_context_clause)



        return result
    
    @property
    def f_package_declaration(
        self
    ) -> PackageNode:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_specification_f_package_declaration)



        return result

    _field_names = RFLXNode._field_names + (
        "f_context_clause",
        "f_package_declaration",
    )

    _kind_name = 'Specification'






class State(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Session state.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_f_identifier)



        return result
    
    @property
    def f_description(
        self
    ) -> Description:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_state_f_description)



        return result
    
    @property
    def f_body(
        self
    ) -> StateBody:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_f_body)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_description",
        "f_body",
    )

    _kind_name = 'State'






class StateBody(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Body of a session state.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_declarations(
        self
    ) -> LocalDeclList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_body_f_declarations)



        return result
    
    @property
    def f_actions(
        self
    ) -> StatementList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_body_f_actions)



        return result
    
    @property
    def f_conditional_transitions(
        self
    ) -> ConditionalTransitionList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_body_f_conditional_transitions)



        return result
    
    @property
    def f_final_transition(
        self
    ) -> Transition:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_body_f_final_transition)



        return result
    
    @property
    def f_exception_transition(
        self
    ) -> Transition:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_state_body_f_exception_transition)



        return result
    
    @property
    def f_end_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_state_body_f_end_identifier)



        return result

    _field_names = RFLXNode._field_names + (
        "f_declarations",
        "f_actions",
        "f_conditional_transitions",
        "f_final_transition",
        "f_exception_transition",
        "f_end_identifier",
    )

    _kind_name = 'StateBody'






class Statement(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for statements.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class Assignment(Statement):
    """
    Subclass of :py:class:`Statement`.

    Assignment of expression to unqualified identifier.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_assignment_f_identifier)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_assignment_f_expression)



        return result

    _field_names = Statement._field_names + (
        "f_identifier",
        "f_expression",
    )

    _kind_name = 'Assignment'






class AttributeStatement(Statement):
    """
    Subclass of :py:class:`Statement`.

    Attribute statement.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_attribute_statement_f_identifier)



        return result
    
    @property
    def f_attr(
        self
    ) -> AttrStmt:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_attribute_statement_f_attr)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_attribute_statement_f_expression)



        return result

    _field_names = Statement._field_names + (
        "f_identifier",
        "f_attr",
        "f_expression",
    )

    _kind_name = 'AttributeStatement'






class MessageFieldAssignment(Statement):
    """
    Subclass of :py:class:`Statement`.

    Assignment of expression to message field.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_message(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_assignment_f_message)



        return result
    
    @property
    def f_field(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_assignment_f_field)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_field_assignment_f_expression)



        return result

    _field_names = Statement._field_names + (
        "f_message",
        "f_field",
        "f_expression",
    )

    _kind_name = 'MessageFieldAssignment'






class Reset(Statement):
    """
    Subclass of :py:class:`Statement`.

    Reset statement.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_reset_f_identifier)



        return result
    
    @property
    def f_associations(
        self
    ) -> MessageAggregateAssociationList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_reset_f_associations)



        return result

    _field_names = Statement._field_names + (
        "f_identifier",
        "f_associations",
    )

    _kind_name = 'Reset'






class TermAssoc(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_term_assoc_f_identifier)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_term_assoc_f_expression)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_expression",
    )

    _kind_name = 'TermAssoc'






class ThenNode(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Link to field.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_target(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_then_node_f_target)



        return result
    
    @property
    def f_aspects(
        self
    ) -> AspectList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_then_node_f_aspects)



        return result
    
    @property
    def f_condition(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_then_node_f_condition)



        return result

    _field_names = RFLXNode._field_names + (
        "f_target",
        "f_aspects",
        "f_condition",
    )

    _kind_name = 'ThenNode'






class Transition(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Unconditional session state transition.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_target(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_transition_f_target)



        return result
    
    @property
    def f_description(
        self
    ) -> Description:
        """
        This field may be null even when there are no parsing errors.
        """
        

        

        result = self._eval_astnode_field(_transition_f_description)



        return result

    _field_names = RFLXNode._field_names + (
        "f_target",
        "f_description",
    )

    _kind_name = 'Transition'






class ConditionalTransition(Transition):
    """
    Subclass of :py:class:`Transition`.

    Conditional session state transition.
    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_condition(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Binding`,
        :py:class:`Call`, :py:class:`CaseExpression`,
        :py:class:`Comprehension`, :py:class:`Conversion`,
        :py:class:`MessageAggregate`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`QuantifiedExpression`, :py:class:`SelectNode`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_conditional_transition_f_condition)



        return result

    _field_names = Transition._field_names + (
        "f_condition",
    )

    _kind_name = 'ConditionalTransition'






class TypeArgument(RFLXNode):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_identifier(
        self
    ) -> UnqualifiedID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_type_argument_f_identifier)



        return result
    
    @property
    def f_expression(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_type_argument_f_expression)



        return result

    _field_names = RFLXNode._field_names + (
        "f_identifier",
        "f_expression",
    )

    _kind_name = 'TypeArgument'






class TypeDef(RFLXNode):
    """
    Subclass of :py:class:`RFLXNode`.

    Base class for type definitions (integers, messages, type derivations,
    sequences, enums).
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = RFLXNode._field_names + (
    )







class AbstractMessageTypeDef(TypeDef):
    """
    Subclass of :py:class:`TypeDef`.

    Base class for message type definitions.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = TypeDef._field_names + (
    )







class MessageTypeDef(AbstractMessageTypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_message_fields(
        self
    ) -> MessageFields:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_type_def_f_message_fields)



        return result
    
    @property
    def f_aspects(
        self
    ) -> MessageAspectList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_message_type_def_f_aspects)



        return result

    _field_names = AbstractMessageTypeDef._field_names + (
        "f_message_fields",
        "f_aspects",
    )

    _kind_name = 'MessageTypeDef'






class NullMessageTypeDef(AbstractMessageTypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = AbstractMessageTypeDef._field_names + (
    )

    _kind_name = 'NullMessageTypeDef'






class EnumerationDef(TypeDef):
    """
    Subclass of :py:class:`TypeDef`.

    Base class for enumeration definitions.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = TypeDef._field_names + (
    )







class NamedEnumerationDef(EnumerationDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_elements(
        self
    ) -> ElementValueAssocList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_named_enumeration_def_f_elements)



        return result

    _field_names = EnumerationDef._field_names + (
        "f_elements",
    )

    _kind_name = 'NamedEnumerationDef'






class PositionalEnumerationDef(EnumerationDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_elements(
        self
    ) -> UnqualifiedIDList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_positional_enumeration_def_f_elements)



        return result

    _field_names = EnumerationDef._field_names + (
        "f_elements",
    )

    _kind_name = 'PositionalEnumerationDef'






class EnumerationTypeDef(TypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_elements(
        self
    ) -> EnumerationDef:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_enumeration_type_def_f_elements)



        return result
    
    @property
    def f_aspects(
        self
    ) -> AspectList:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_enumeration_type_def_f_aspects)



        return result

    _field_names = TypeDef._field_names + (
        "f_elements",
        "f_aspects",
    )

    _kind_name = 'EnumerationTypeDef'






class IntegerTypeDef(TypeDef):
    """
    Subclass of :py:class:`TypeDef`.

    Base class for all integer type definitions.
    """
    __slots__ : Tuple[str, ...] = ()

    


    _field_names = TypeDef._field_names + (
    )







class ModularTypeDef(IntegerTypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_mod(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_modular_type_def_f_mod)



        return result

    _field_names = IntegerTypeDef._field_names + (
        "f_mod",
    )

    _kind_name = 'ModularTypeDef'






class RangeTypeDef(IntegerTypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_first(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_range_type_def_f_first)



        return result
    
    @property
    def f_last(
        self
    ) -> Expr:
        """
        This field can contain one of the following nodes:
        :py:class:`Attribute`, :py:class:`BinOp`, :py:class:`Negation`,
        :py:class:`NumericLiteral`, :py:class:`ParenExpression`,
        :py:class:`SequenceLiteral`, :py:class:`Variable`

        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_range_type_def_f_last)



        return result
    
    @property
    def f_size(
        self
    ) -> Aspect:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_range_type_def_f_size)



        return result

    _field_names = IntegerTypeDef._field_names + (
        "f_first",
        "f_last",
        "f_size",
    )

    _kind_name = 'RangeTypeDef'






class SequenceTypeDef(TypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_element_type(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_sequence_type_def_f_element_type)



        return result

    _field_names = TypeDef._field_names + (
        "f_element_type",
    )

    _kind_name = 'SequenceTypeDef'






class TypeDerivationDef(TypeDef):
    """

    """
    __slots__ : Tuple[str, ...] = ()

    

    
    @property
    def f_base(
        self
    ) -> ID:
        """
        When there are no parsing errors, this field is never null.
        """
        

        

        result = self._eval_astnode_field(_type_derivation_def_f_base)



        return result

    _field_names = TypeDef._field_names + (
        "f_base",
    )

    _kind_name = 'TypeDerivationDef'






class _EnvRebindingsType_c_type(ctypes.Structure):
    _fields_ = [("version", ctypes.c_uint64)]


_EnvRebindings_c_type = _hashable_c_pointer(_EnvRebindingsType_c_type)




class _BaseStruct:
    """
    Mixin for Ada struct wrappers.
    """

    # Subclasses will override this to a subclass of ctypes.Structure
    _c_type: ClassVar[ctypes.Structure]

    def __getitem__(self, key: int) -> Any:
        if not isinstance(key, int):
            raise TypeError(
               'Tuples items are indexed by integers, not {}'.format(type(key))
            )

        fields = self._c_type._fields_
        if 0 <= key < len(fields):
            field_name, _ = fields[key]
            return getattr(self, field_name)
        else:
            raise IndexError('There is no {}th field'.format(key))

    def __repr__(self) -> str:
        field_names = [
            name
            for name, _ in self._c_type._fields_
            if hasattr(self, name)
        ]
        if field_names:
            fields_suffix = (
                " "
                + " ".join(
                    "{}={}".format(name, getattr(self, name))
                    for name in field_names
                )
            )
        else:
            fields_suffix = ""
        return "<{}{}>".format(type(self).__name__, fields_suffix)

    @property
    def as_tuple(self) -> tuple:
        return tuple(getattr(self, f) for f, _ in self._c_type._fields_)

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, type(self)) and
                self.as_tuple == other.as_tuple)

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __hash__(self) -> int:
        return hash(self.as_tuple)




class _Metadata_c_type(ctypes.Structure):
    _fields_: ClassVar[List[Tuple[str, Any]]] = (
         [
        ('dummy', ctypes.c_byte),
] 
    )
    _null_value: ClassVar[_Metadata_c_type]

    @property
    def as_tuple(self):
        return tuple(getattr(self, f) for f, _ in self._fields_)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.as_tuple == other.as_tuple)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.as_tuple)
class _EntityInfo_c_type(ctypes.Structure):
    _fields_: ClassVar[List[Tuple[str, Any]]] = (
         [
        ('md',
            _Metadata_c_type
         ),
        ('rebindings',
            _EnvRebindings_c_type
         ),
        ('from_rebound',
            ctypes.c_uint8
         ),
] 
    )
    _null_value: ClassVar[_EntityInfo_c_type]
class _Entity_c_type(ctypes.Structure):
    _fields_: ClassVar[List[Tuple[str, Any]]] = (
         [
        ('node',
            RFLXNode._node_c_type
         ),
        ('info',
            _EntityInfo_c_type
         ),
] 
    )
    _null_value: ClassVar[_Entity_c_type]

    @classmethod
    def from_bare_node(cls, node_c_value):
        return cls(node_c_value, _EntityInfo_c_type._null_value)


_Metadata_c_type._null_value = _Metadata_c_type()
_EntityInfo_c_type._null_value = _EntityInfo_c_type(_Metadata_c_type._null_value,
                                                None)


#
# Low-level binding - Second part
#

# For performance, allocate a single C API entity for all uses of null
# entities.
_Entity_c_type._null_value = _Entity_c_type()
_Entity_c_type._null_value.node = None



class _BaseArray:
    """
    Base class for Ada arrays bindings.
    """

    c_element_type: ClassVar[Any]
    """
    Ctype class for array elements.
    """

    items_refcounted = False
    """
    Whether items for this arrays are ref-counted.
    """

    __slots__ = ('c_value', 'length', 'items')

    def __init__(self, c_value):
        self.c_value = c_value

        self.length = c_value.contents.n

        items_addr = _field_address(c_value.contents, 'items')
        items = self.c_element_type.from_address(items_addr)
        self.items = ctypes.pointer(items)

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, list(self))

    def clear(self):
        self.c_value = None
        self.length = None
        self.items = None

    def __del__(self):
        self.dec_ref(self.c_value)
        self.clear()

    @classmethod
    def wrap(cls, c_value, from_field_access):
        helper = cls(c_value)

        result = []
        for i in range(helper.length):
            # In ctypes, accessing an array element does not copy it, which
            # means the the array must live at least as long as the accessed
            # element. We cannot guarantee that, so we must copy the element so
            # that it is independent of the array it comes from.
            #
            # The try/except block tries to do a copy if "item" is indeed a
            # buffer to be copied, and will fail if it's a mere integer, which
            # does not need the buffer copy anyway, hence the "pass".
            item = helper.items[i]
            try:
                item = cls.c_element_type.from_buffer_copy(item)
            except TypeError:
                pass
            result.append(helper.wrap_item(item))

        # If this array value comes from a structure field, we must not call
        # its dec_ref primitive, as it is up to the structure's dec_ref
        # primitive to take care of it.
        if from_field_access:
            helper.clear()

        return result

    @classmethod
    def unwrap(cls, value, context=None):
        if not isinstance(value, list):
            _raise_type_error('list', value)

        # Create a holder for the result
        result = cls(cls.create(len(value)))

        # Unwrap all items at once, preserving their holder so that resources
        # are deallocated if there is an error at some point.
        items = [result.unwrap_item(item, context) for item in value]

        # Initialize the resulting array
        for i, (_, item) in enumerate(items):
            result.items[i] = item

        # At this point, we know that this is successful. We don't want
        # holders to dec-ref the content so that the return array takes over
        # the corresponding refcounting shares.
        if cls.items_refcounted:
            for holder, _ in items:
                holder.clear()

        return result






class _RFLXNodeArrayConverter(_BaseArray):
    """
    Wrapper class for arrays of InternalEntity.

    This class is not meant to be directly instantiated: it is only used to
    convert values that various methods take/return.
    """

    __slots__ = _BaseArray.__slots__
    items_refcounted = False

    @staticmethod
    def wrap_item(item):
        return RFLXNode._wrap(item)

    @staticmethod
    def unwrap_item(item, context=None):
        c_holder = RFLXNode._unwrap(item)
        c_value = c_holder
        return (c_holder, c_value)

    c_element_type = _Entity_c_type

    class c_struct(ctypes.Structure):
        _fields_ = [('n', ctypes.c_int),
                    ('ref_count', ctypes.c_int),
                    ('items', _Entity_c_type * 1)]

    c_type = ctypes.POINTER(c_struct)

    create = staticmethod(_import_func(
        'rflx_node_array_create', [ctypes.c_int], c_type))
    inc_ref = staticmethod(_import_func(
        'rflx_node_array_inc_ref', [c_type], None))
    dec_ref = staticmethod(_import_func(
        'rflx_node_array_dec_ref', [c_type], None))





_IteratedType = TypeVar("_IteratedType")

class _BaseIterator(Generic[_IteratedType]):
    """
Base class for Ada iterator bindings.

An iterator provides a mean to retrieve values one-at-a-time.

Currently, each iterator is bound to the analysis context used to create it.
Iterators are invalidated as soon as any unit of that analysis is reparsed. Due
to the nature of iterators (lazy computations), this invalidation is necessary
to avoid use of inconsistent state, such as an iterator trying to use analysis
context data that is stale.
"""

    _c_element_type: ClassVar[Any]
    """
    Ctype class for iterator elements.
    """

    __slots__ = ('_c_value',)

    def __init__(self, c_value: Any):
        self._c_value = c_value

    def __repr__(self) -> str:
        return '<{}>'.format(type(self).__name__)

    def _clear(self) -> None:
        self._c_value = None

    def __del__(self) -> None:
        self._dec_ref(self._c_value)
        self._clear()

    @classmethod
    def _wrap(cls, c_value: Any) -> Opt[_BaseIterator]:
        return cls(c_value) if c_value else None

    @classmethod
    def unwrap(cls, value: Opt[_BaseIterator]) -> Any:
        if value is None:
            return None
        elif not isinstance(value, cls):
            _raise_type_error(cls.__name__, value)
        else:
            return value._c_value

    def __iter__(self) -> Iterator[_IteratedType]:
        return self

    def __next__(self) -> _IteratedType:
        """
      Return the next value from the iterator. Raises ``StopIteration`` if
      there is no more element to retrieve.

      This raises a ``Stale_Reference_Error`` exception if the iterator is
      invalidated.
      """
        x = self._c_element_type()
        if self._get_next(self._c_value, ctypes.byref(x)):
            return self._wrap_item(x)
        raise StopIteration

    # For Python2 compatibility
    next = __next__

    # The following methods are just for type hints: subclasses override them

    @staticmethod
    def _get_next(c_value: Any, item_ptr: Any) -> Any:
        pass

    @staticmethod
    def _inc_ref(c_value: Any) -> None:
        pass

    @staticmethod
    def _dec_ref(c_value: Any) -> None:
        pass

    @staticmethod
    def _wrap_item(item: Any) -> _IteratedType:
        pass




_free = _import_func(
    'rflx_free',
    [ctypes.c_void_p], None
)

_destroy_text = _import_func(
    'rflx_destroy_text', [ctypes.POINTER(_text)], None
)

_symbol_text = _import_func(
    'rflx_symbol_text',
    [ctypes.POINTER(_symbol_type), ctypes.POINTER(_text)], None
)

_get_versions = _import_func(
    'rflx_get_versions',
    [ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p)], None
)

# Analysis primitives
_allocate_analysis_context = _import_func(
    'rflx_allocate_analysis_context',
    [],
    AnalysisContext._c_type,
)
_initialize_analysis_context = _import_func(
    'rflx_initialize_analysis_context',
    [AnalysisContext._c_type, # context
     ctypes.c_char_p,         # charset
     _file_reader,            # file_reader
     _unit_provider,          # unit_provider
     _event_handler,          # event_handler
     ctypes.c_int,            # with_trivia
     ctypes.c_int],           # tab_stop
    None,
)
_context_incref = _import_func(
    'rflx_context_incref',
    [AnalysisContext._c_type], AnalysisContext._c_type
)
_context_decref = _import_func(
    'rflx_context_decref',
    [AnalysisContext._c_type], None
)
_context_symbol = _import_func(
    'rflx_context_symbol',
    [AnalysisContext._c_type,
     ctypes.POINTER(_text),
     ctypes.POINTER(_symbol_type)], ctypes.c_int
)
_discard_errors_in_populate_lexical_env = _import_func(
   'rflx_context_discard_errors_in_populate_lexical_env',
   [AnalysisContext._c_type, ctypes.c_int], None
)
_get_analysis_unit_from_file = _import_func(
    'rflx_get_analysis_unit_from_file',
    [AnalysisContext._c_type,  # context
     ctypes.c_char_p,          # filename
     ctypes.c_char_p,          # charset
     ctypes.c_int,             # reparse
     ctypes.c_int],            # grammar rule
    AnalysisUnit._c_type
)
_get_analysis_unit_from_buffer = _import_func(
    'rflx_get_analysis_unit_from_buffer',
    [AnalysisContext._c_type,  # context
     ctypes.c_char_p,          # filename
     ctypes.c_char_p,          # charset
     ctypes.c_char_p,          # buffer
     ctypes.c_size_t,          # buffer_size
     ctypes.c_int],            # grammar rule
    AnalysisUnit._c_type
)
_unit_root = _import_func(
    'rflx_unit_root',
    [AnalysisUnit._c_type, ctypes.POINTER(_Entity_c_type)], None
)
_unit_first_token = _import_func(
    "rflx_unit_first_token",
    [AnalysisUnit._c_type, Token._c_type], None
)
_unit_last_token = _import_func(
    "rflx_unit_last_token",
    [AnalysisUnit._c_type, Token._c_type], None
)
_unit_token_count = _import_func(
    "rflx_unit_token_count",
    [AnalysisUnit._c_type], ctypes.c_int
)
_unit_trivia_count = _import_func(
    "rflx_unit_trivia_count",
    [AnalysisUnit._c_type], ctypes.c_int
)
_unit_lookup_token = _import_func(
    "rflx_unit_lookup_token",
    [AnalysisUnit._c_type,
     ctypes.POINTER(Sloc._c_type),
     Token._c_type],
    None
)
_unit_dump_lexical_env = _import_func(
    "rflx_unit_dump_lexical_env",
    [AnalysisUnit._c_type], None
)
_unit_filename = _import_func(
    "rflx_unit_filename",
    [AnalysisUnit._c_type], ctypes.POINTER(ctypes.c_char)
)
_unit_diagnostic_count = _import_func(
    'rflx_unit_diagnostic_count',
    [AnalysisUnit._c_type], ctypes.c_uint
)
_unit_diagnostic = _import_func(
    'rflx_unit_diagnostic',
    [AnalysisUnit._c_type, ctypes.c_uint, ctypes.POINTER(Diagnostic._c_type)],
    ctypes.c_int
)
_unit_context = _import_func(
    'rflx_unit_context',
    [AnalysisUnit._c_type], AnalysisContext._c_type
)
_unit_reparse_from_file = _import_func(
    'rflx_unit_reparse_from_file',
    [AnalysisUnit._c_type,    # unit
     ctypes.c_char_p],        # charset
    ctypes.c_int
)
_unit_reparse_from_buffer = _import_func(
    'rflx_unit_reparse_from_buffer',
    [AnalysisUnit._c_type, # unit
     ctypes.c_char_p,      # charset
     ctypes.c_char_p,      # buffer
     ctypes.c_size_t],     # buffer_size
    None
)
_unit_populate_lexical_env = _import_func(
    'rflx_unit_populate_lexical_env',
    [
        AnalysisUnit._c_type,
    ],
    ctypes.c_int
)

# General AST node primitives
_node_hash = _import_func(
    'rflx_node_hash',
    [ctypes.POINTER(_Entity_c_type)], ctypes.c_uint32
)

_node_is_equivalent = _import_func(
    'rflx_node_is_equivalent',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)], ctypes.c_uint8
)

_node_kind = _import_func(
    'rflx_node_kind',
    [ctypes.POINTER(_Entity_c_type)], ctypes.c_int
)
_node_unit = _import_func(
    'rflx_node_unit',
    [ctypes.POINTER(_Entity_c_type)], AnalysisUnit._c_type
)
_node_is_token_node = _import_func(
    'rflx_node_is_token_node',
    [ctypes.POINTER(_Entity_c_type)], ctypes.c_int
)
_node_is_synthetic = _import_func(
    'rflx_node_is_synthetic',
    [ctypes.POINTER(_Entity_c_type)], ctypes.c_int
)
_node_image = _import_func(
    'rflx_node_image',
    [ctypes.POINTER(_Entity_c_type), ctypes.POINTER(_text)], None
)
_node_text = _import_func(
    'rflx_node_text',
    [ctypes.POINTER(_Entity_c_type), ctypes.POINTER(_text)], None
)
_node_sloc_range = _import_func(
    'rflx_node_sloc_range',
    [ctypes.POINTER(_Entity_c_type), ctypes.POINTER(SlocRange._c_type)], None
)
_lookup_in_node = _import_func(
    'rflx_lookup_in_node',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(Sloc._c_type),
     ctypes.POINTER(_Entity_c_type)], None
)
_node_children_count = _import_func(
    'rflx_node_children_count',
    [ctypes.POINTER(_Entity_c_type)], ctypes.c_uint
)
_node_child = _import_func(
    'rflx_node_child',
    [ctypes.POINTER(_Entity_c_type), ctypes.c_uint, ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)

_r_f_l_x_node_parent = _import_func(
    'rflx_r_f_l_x_node_parent',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_r_f_l_x_node_parents = _import_func(
    'rflx_r_f_l_x_node_parents',
    [ctypes.POINTER(_Entity_c_type),
        
        ctypes.c_uint8,
     ctypes.POINTER(_RFLXNodeArrayConverter.c_type)],
    ctypes.c_int
)
_r_f_l_x_node_children = _import_func(
    'rflx_r_f_l_x_node_children',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_RFLXNodeArrayConverter.c_type)],
    ctypes.c_int
)
_r_f_l_x_node_token_start = _import_func(
    'rflx_r_f_l_x_node_token_start',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(Token._c_struct)],
    ctypes.c_int
)
_r_f_l_x_node_token_end = _import_func(
    'rflx_r_f_l_x_node_token_end',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(Token._c_struct)],
    ctypes.c_int
)
_r_f_l_x_node_child_index = _import_func(
    'rflx_r_f_l_x_node_child_index',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(ctypes.c_int)],
    ctypes.c_int
)
_r_f_l_x_node_previous_sibling = _import_func(
    'rflx_r_f_l_x_node_previous_sibling',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_r_f_l_x_node_next_sibling = _import_func(
    'rflx_r_f_l_x_node_next_sibling',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_r_f_l_x_node_unit = _import_func(
    'rflx_r_f_l_x_node_unit',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(AnalysisUnit._c_type)],
    ctypes.c_int
)
_r_f_l_x_node_is_ghost = _import_func(
    'rflx_r_f_l_x_node_is_ghost',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(ctypes.c_uint8)],
    ctypes.c_int
)
_r_f_l_x_node_full_sloc_image = _import_func(
    'rflx_r_f_l_x_node_full_sloc_image',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_String.c_type)],
    ctypes.c_int
)
_i_d_f_package = _import_func(
    'rflx_i_d_f_package',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_i_d_f_name = _import_func(
    'rflx_i_d_f_name',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_aspect_f_identifier = _import_func(
    'rflx_aspect_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_aspect_f_value = _import_func(
    'rflx_aspect_f_value',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_aggregate_associations_f_associations = _import_func(
    'rflx_message_aggregate_associations_f_associations',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_checksum_val_f_data = _import_func(
    'rflx_checksum_val_f_data',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_checksum_value_range_f_first = _import_func(
    'rflx_checksum_value_range_f_first',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_checksum_value_range_f_last = _import_func(
    'rflx_checksum_value_range_f_last',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_checksum_assoc_f_identifier = _import_func(
    'rflx_checksum_assoc_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_checksum_assoc_f_covered_fields = _import_func(
    'rflx_checksum_assoc_f_covered_fields',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_refinement_decl_f_pdu = _import_func(
    'rflx_refinement_decl_f_pdu',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_refinement_decl_f_field = _import_func(
    'rflx_refinement_decl_f_field',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_refinement_decl_f_sdu = _import_func(
    'rflx_refinement_decl_f_sdu',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_refinement_decl_f_condition = _import_func(
    'rflx_refinement_decl_f_condition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_session_decl_f_parameters = _import_func(
    'rflx_session_decl_f_parameters',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_session_decl_f_identifier = _import_func(
    'rflx_session_decl_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_session_decl_f_declarations = _import_func(
    'rflx_session_decl_f_declarations',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_session_decl_f_states = _import_func(
    'rflx_session_decl_f_states',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_session_decl_f_end_identifier = _import_func(
    'rflx_session_decl_f_end_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_type_decl_f_identifier = _import_func(
    'rflx_type_decl_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_type_decl_f_parameters = _import_func(
    'rflx_type_decl_f_parameters',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_type_decl_f_definition = _import_func(
    'rflx_type_decl_f_definition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_description_f_content = _import_func(
    'rflx_description_f_content',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_element_value_assoc_f_identifier = _import_func(
    'rflx_element_value_assoc_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_element_value_assoc_f_literal = _import_func(
    'rflx_element_value_assoc_f_literal',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_attribute_f_expression = _import_func(
    'rflx_attribute_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_attribute_f_kind = _import_func(
    'rflx_attribute_f_kind',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_bin_op_f_left = _import_func(
    'rflx_bin_op_f_left',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_bin_op_f_op = _import_func(
    'rflx_bin_op_f_op',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_bin_op_f_right = _import_func(
    'rflx_bin_op_f_right',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_binding_f_expression = _import_func(
    'rflx_binding_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_binding_f_bindings = _import_func(
    'rflx_binding_f_bindings',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_call_f_identifier = _import_func(
    'rflx_call_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_call_f_arguments = _import_func(
    'rflx_call_f_arguments',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_case_expression_f_expression = _import_func(
    'rflx_case_expression_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_case_expression_f_choices = _import_func(
    'rflx_case_expression_f_choices',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_choice_f_selectors = _import_func(
    'rflx_choice_f_selectors',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_choice_f_expression = _import_func(
    'rflx_choice_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_comprehension_f_iterator = _import_func(
    'rflx_comprehension_f_iterator',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_comprehension_f_sequence = _import_func(
    'rflx_comprehension_f_sequence',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_comprehension_f_condition = _import_func(
    'rflx_comprehension_f_condition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_comprehension_f_selector = _import_func(
    'rflx_comprehension_f_selector',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_context_item_f_item = _import_func(
    'rflx_context_item_f_item',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_conversion_f_target_identifier = _import_func(
    'rflx_conversion_f_target_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_conversion_f_argument = _import_func(
    'rflx_conversion_f_argument',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_aggregate_f_identifier = _import_func(
    'rflx_message_aggregate_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_aggregate_f_values = _import_func(
    'rflx_message_aggregate_f_values',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_negation_f_data = _import_func(
    'rflx_negation_f_data',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_paren_expression_f_data = _import_func(
    'rflx_paren_expression_f_data',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_quantified_expression_f_operation = _import_func(
    'rflx_quantified_expression_f_operation',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_quantified_expression_f_parameter_identifier = _import_func(
    'rflx_quantified_expression_f_parameter_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_quantified_expression_f_iterable = _import_func(
    'rflx_quantified_expression_f_iterable',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_quantified_expression_f_predicate = _import_func(
    'rflx_quantified_expression_f_predicate',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_select_node_f_expression = _import_func(
    'rflx_select_node_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_select_node_f_selector = _import_func(
    'rflx_select_node_f_selector',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_concatenation_f_left = _import_func(
    'rflx_concatenation_f_left',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_concatenation_f_right = _import_func(
    'rflx_concatenation_f_right',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_sequence_aggregate_f_values = _import_func(
    'rflx_sequence_aggregate_f_values',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_variable_f_identifier = _import_func(
    'rflx_variable_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_formal_channel_decl_f_identifier = _import_func(
    'rflx_formal_channel_decl_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_formal_channel_decl_f_parameters = _import_func(
    'rflx_formal_channel_decl_f_parameters',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_formal_function_decl_f_identifier = _import_func(
    'rflx_formal_function_decl_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_formal_function_decl_f_parameters = _import_func(
    'rflx_formal_function_decl_f_parameters',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_formal_function_decl_f_return_type_identifier = _import_func(
    'rflx_formal_function_decl_f_return_type_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_renaming_decl_f_identifier = _import_func(
    'rflx_renaming_decl_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_renaming_decl_f_type_identifier = _import_func(
    'rflx_renaming_decl_f_type_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_renaming_decl_f_expression = _import_func(
    'rflx_renaming_decl_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_variable_decl_f_identifier = _import_func(
    'rflx_variable_decl_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_variable_decl_f_type_identifier = _import_func(
    'rflx_variable_decl_f_type_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_variable_decl_f_initializer = _import_func(
    'rflx_variable_decl_f_initializer',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_aggregate_association_f_identifier = _import_func(
    'rflx_message_aggregate_association_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_aggregate_association_f_expression = _import_func(
    'rflx_message_aggregate_association_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_byte_order_aspect_f_byte_order = _import_func(
    'rflx_byte_order_aspect_f_byte_order',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_checksum_aspect_f_associations = _import_func(
    'rflx_checksum_aspect_f_associations',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_f_identifier = _import_func(
    'rflx_message_field_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_f_type_identifier = _import_func(
    'rflx_message_field_f_type_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_f_type_arguments = _import_func(
    'rflx_message_field_f_type_arguments',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_f_aspects = _import_func(
    'rflx_message_field_f_aspects',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_f_condition = _import_func(
    'rflx_message_field_f_condition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_f_thens = _import_func(
    'rflx_message_field_f_thens',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_fields_f_initial_field = _import_func(
    'rflx_message_fields_f_initial_field',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_fields_f_fields = _import_func(
    'rflx_message_fields_f_fields',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_null_message_field_f_thens = _import_func(
    'rflx_null_message_field_f_thens',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_package_node_f_identifier = _import_func(
    'rflx_package_node_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_package_node_f_declarations = _import_func(
    'rflx_package_node_f_declarations',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_package_node_f_end_identifier = _import_func(
    'rflx_package_node_f_end_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_parameter_f_identifier = _import_func(
    'rflx_parameter_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_parameter_f_type_identifier = _import_func(
    'rflx_parameter_f_type_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_parameters_f_parameters = _import_func(
    'rflx_parameters_f_parameters',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_specification_f_context_clause = _import_func(
    'rflx_specification_f_context_clause',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_specification_f_package_declaration = _import_func(
    'rflx_specification_f_package_declaration',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_f_identifier = _import_func(
    'rflx_state_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_f_description = _import_func(
    'rflx_state_f_description',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_f_body = _import_func(
    'rflx_state_f_body',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_body_f_declarations = _import_func(
    'rflx_state_body_f_declarations',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_body_f_actions = _import_func(
    'rflx_state_body_f_actions',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_body_f_conditional_transitions = _import_func(
    'rflx_state_body_f_conditional_transitions',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_body_f_final_transition = _import_func(
    'rflx_state_body_f_final_transition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_body_f_exception_transition = _import_func(
    'rflx_state_body_f_exception_transition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_state_body_f_end_identifier = _import_func(
    'rflx_state_body_f_end_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_assignment_f_identifier = _import_func(
    'rflx_assignment_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_assignment_f_expression = _import_func(
    'rflx_assignment_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_attribute_statement_f_identifier = _import_func(
    'rflx_attribute_statement_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_attribute_statement_f_attr = _import_func(
    'rflx_attribute_statement_f_attr',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_attribute_statement_f_expression = _import_func(
    'rflx_attribute_statement_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_assignment_f_message = _import_func(
    'rflx_message_field_assignment_f_message',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_assignment_f_field = _import_func(
    'rflx_message_field_assignment_f_field',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_field_assignment_f_expression = _import_func(
    'rflx_message_field_assignment_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_reset_f_identifier = _import_func(
    'rflx_reset_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_reset_f_associations = _import_func(
    'rflx_reset_f_associations',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_term_assoc_f_identifier = _import_func(
    'rflx_term_assoc_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_term_assoc_f_expression = _import_func(
    'rflx_term_assoc_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_then_node_f_target = _import_func(
    'rflx_then_node_f_target',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_then_node_f_aspects = _import_func(
    'rflx_then_node_f_aspects',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_then_node_f_condition = _import_func(
    'rflx_then_node_f_condition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_transition_f_target = _import_func(
    'rflx_transition_f_target',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_transition_f_description = _import_func(
    'rflx_transition_f_description',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_conditional_transition_f_condition = _import_func(
    'rflx_conditional_transition_f_condition',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_type_argument_f_identifier = _import_func(
    'rflx_type_argument_f_identifier',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_type_argument_f_expression = _import_func(
    'rflx_type_argument_f_expression',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_type_def_f_message_fields = _import_func(
    'rflx_message_type_def_f_message_fields',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_message_type_def_f_aspects = _import_func(
    'rflx_message_type_def_f_aspects',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_named_enumeration_def_f_elements = _import_func(
    'rflx_named_enumeration_def_f_elements',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_positional_enumeration_def_f_elements = _import_func(
    'rflx_positional_enumeration_def_f_elements',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_enumeration_type_def_f_elements = _import_func(
    'rflx_enumeration_type_def_f_elements',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_enumeration_type_def_f_aspects = _import_func(
    'rflx_enumeration_type_def_f_aspects',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_modular_type_def_f_mod = _import_func(
    'rflx_modular_type_def_f_mod',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_range_type_def_f_first = _import_func(
    'rflx_range_type_def_f_first',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_range_type_def_f_last = _import_func(
    'rflx_range_type_def_f_last',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_range_type_def_f_size = _import_func(
    'rflx_range_type_def_f_size',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_sequence_type_def_f_element_type = _import_func(
    'rflx_sequence_type_def_f_element_type',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)
_type_derivation_def_f_base = _import_func(
    'rflx_type_derivation_def_f_base',
    [ctypes.POINTER(_Entity_c_type),
     ctypes.POINTER(_Entity_c_type)],
    ctypes.c_int
)

# File readers
_dec_ref_file_reader = _import_func(
    'rflx_dec_ref_file_reader',
    [_file_reader], None
)



# Event handlers
_event_handler_destroy_func = ctypes.CFUNCTYPE(None, ctypes.py_object)
_event_handler_unit_requested_func = ctypes.CFUNCTYPE(
    None,
    ctypes.py_object,        # data
    AnalysisContext._c_type, # context
    ctypes.POINTER(_text),   # name
    AnalysisUnit._c_type,    # from
    ctypes.c_uint8,          # found
    ctypes.c_uint8,          # is_not_found_error
)
_event_handler_unit_parsed_func = ctypes.CFUNCTYPE(
    None,
    ctypes.py_object,        # data
    AnalysisContext._c_type, # context
    AnalysisUnit._c_type,    # unit
    ctypes.c_uint8,          # reparsed
)
_create_event_handler = _import_func(
    'rflx_create_event_handler',
    [
        ctypes.py_object,
        _event_handler_destroy_func,
        _event_handler_unit_requested_func,
        _event_handler_unit_parsed_func,
    ],
    _event_handler,
)
_dec_ref_event_handler = _import_func(
    'rflx_dec_ref_event_handler', [_event_handler], None
)

# Unit providers
_dec_ref_unit_provider = _import_func(
    'rflx_dec_ref_unit_provider',
    [_unit_provider], None
)



# Misc
_token_get_kind = _import_func(
    "rflx_token_get_kind", [Token._c_type], ctypes.c_int
)
_token_kind_name = _import_func(
    "rflx_token_kind_name",
    [ctypes.c_int], ctypes.POINTER(ctypes.c_char)
)
_token_sloc_range = _import_func(
    "rflx_token_sloc_range",
    [Token._c_type, ctypes.POINTER(SlocRange._c_type)], None
)
_token_next = _import_func(
    "rflx_token_next",
    [Token._c_type, Token._c_type], None
)
_token_is_equivalent = _import_func(
    "rflx_token_is_equivalent",
    [Token._c_type, Token._c_type], ctypes.c_int
)
_token_previous = _import_func(
    "rflx_token_previous",
    [Token._c_type, Token._c_type], None
)
_token_range_text = _import_func(
    "rflx_token_range_text",
    [Token._c_type, Token._c_type, ctypes.POINTER(_text)],
    ctypes.c_int
)


#
# Layering helpers
#

def _unwrap_str(c_char_p_value: Any) -> str:
    """
    Assuming c_char_p_value is a valid char*, convert it to a native Python
    string and free the C pointer.
    """
    result = ctypes.c_char_p(ctypes.addressof(c_char_p_value.contents)).value
    _free(c_char_p_value)
    return (result or b'').decode()


_kind_to_astnode_cls = {
    1: ID,
    2: UnqualifiedID,
    3: Aspect,
    4: AttrFirst,
    5: AttrHasData,
    6: AttrHead,
    7: AttrLast,
    8: AttrOpaque,
    9: AttrPresent,
    10: AttrSize,
    11: AttrValid,
    12: AttrValidChecksum,
    13: AttrStmtAppend,
    14: AttrStmtExtend,
    15: AttrStmtRead,
    16: AttrStmtWrite,
    17: MessageAggregateAssociations,
    18: NullMessageAggregate,
    19: ChecksumVal,
    20: ChecksumValueRange,
    21: ByteOrderTypeHighorderfirst,
    22: ByteOrderTypeLoworderfirst,
    23: Readable,
    24: Writable,
    25: ChecksumAssoc,
    26: RefinementDecl,
    27: SessionDecl,
    28: TypeDecl,
    29: Description,
    30: ElementValueAssoc,
    31: Attribute,
    32: BinOp,
    33: Binding,
    34: Call,
    35: CaseExpression,
    36: Choice,
    37: Comprehension,
    38: ContextItem,
    39: Conversion,
    40: MessageAggregate,
    41: Negation,
    42: NumericLiteral,
    43: ParenExpression,
    44: QuantifiedExpression,
    45: SelectNode,
    46: Concatenation,
    47: SequenceAggregate,
    48: StringLiteral,
    49: Variable,
    50: FormalChannelDecl,
    51: FormalFunctionDecl,
    52: RenamingDecl,
    53: VariableDecl,
    54: MessageAggregateAssociation,
    55: ByteOrderAspect,
    56: ChecksumAspect,
    57: MessageField,
    58: MessageFields,
    59: NullMessageField,
    60: OpAdd,
    61: OpAnd,
    62: OpDiv,
    63: OpEq,
    64: OpGe,
    65: OpGt,
    66: OpIn,
    67: OpLe,
    68: OpLt,
    69: OpMod,
    70: OpMul,
    71: OpNeq,
    72: OpNotin,
    73: OpOr,
    74: OpPow,
    75: OpSub,
    76: PackageNode,
    77: Parameter,
    78: Parameters,
    79: QuantifierAll,
    80: QuantifierSome,
    81: AspectList,
    82: BaseChecksumValList,
    83: ChannelAttributeList,
    84: ChecksumAssocList,
    85: ChoiceList,
    86: ConditionalTransitionList,
    87: ContextItemList,
    88: DeclarationList,
    89: ElementValueAssocList,
    90: ExprList,
    91: FormalDeclList,
    92: LocalDeclList,
    93: MessageAggregateAssociationList,
    94: MessageAspectList,
    95: MessageFieldList,
    96: NumericLiteralList,
    97: ParameterList,
    98: RFLXNodeList,
    99: StateList,
    100: StatementList,
    101: TermAssocList,
    102: ThenNodeList,
    103: TypeArgumentList,
    104: UnqualifiedIDList,
    105: Specification,
    106: State,
    107: StateBody,
    108: Assignment,
    109: AttributeStatement,
    110: MessageFieldAssignment,
    111: Reset,
    112: TermAssoc,
    113: ThenNode,
    114: Transition,
    115: ConditionalTransition,
    116: TypeArgument,
    117: MessageTypeDef,
    118: NullMessageTypeDef,
    119: NamedEnumerationDef,
    120: PositionalEnumerationDef,
    121: EnumerationTypeDef,
    122: ModularTypeDef,
    123: RangeTypeDef,
    124: SequenceTypeDef,
    125: TypeDerivationDef,
}


def _field_address(struct: ctypes.Structure, field_name: str) -> int:
    """
    Get the address of a structure field from a structure value.

    For instance::

        class Foo(ctypes.Structure):
            _fields_ = [('i', ctypes.c_int)]

        f = Foo()
        i_addr =_field_address(f, 'i')
    """
    struct_type = type(struct)
    struct_addr = ctypes.addressof(struct)
    field = getattr(struct_type, field_name)
    field_type = None
    for field_desc in struct_type._fields_:
        f_name = field_desc[0]
        f_type = field_desc[1]
        if f_name == field_name:
            field_type = f_type
            break
    assert field_type is not None
    return struct_addr + field.offset

def _extract_versions() -> Tuple[str, str]:
    v_ptr = ctypes.c_char_p()
    bd_ptr = ctypes.c_char_p()
    _get_versions(ctypes.byref(v_ptr), ctypes.byref(bd_ptr))

    _version = v_ptr.value
    assert isinstance(_version, bytes)
    version = _version.decode()
    _free(v_ptr)

    _build_version = bd_ptr.value
    assert isinstance(_build_version, bytes)
    build_version = _build_version.decode()
    _free(bd_ptr)

    return version, build_version

version, build_date = _extract_versions()


#
# Language specific extensions #
#




#
# App base class
#

class App:
    """
    Base class to regroup logic for an app. We use a class so that
    specific languages implementations can add specific arguments and
    processing by overriding specific methods:

    - `main`, which will be the main method of the app.

    - `add_arguments` to add arguments to the argparse.Parser instance

    - `create_unit_provider` to return a custom unit provider to be used by the
      AnalysisContext.

    - `description` to change the description of the app.

    Inside of `main`, the user can access app specific state:

    - `self.units` is a map of filenames to analysis units.
    - `self.ctx` is the analysis context.
    - `self.u` is the last parsed unit.

    The user can then run the app by calling `App.run()`.

    Here is a small example of an app subclassing `App`, that will simply print
    the tree of every unit passed as argument:

    .. code-block:: python

        from librflxlang import App


        class ExampleApp(App):
            def main(self):
                for u in self.units.values():
                    print u.filename
                    print u.root.dump()

        ExampleApp.run()
    """

    parser: argparse.ArgumentParser
    args: argparse.Namespace
    u: AnalysisUnit
    units: Dict[str, AnalysisUnit]
    ctx: AnalysisContext

    @property
    def description(self) -> str:
        """
        Description for this app. Empty by default.
        """
        return ""

    def __init__(self, args: Opt[List[str]] = None):
        self.parser = argparse.ArgumentParser(description=self.description)
        self.parser.add_argument('files', nargs='*', help='Files')
        self.add_arguments()

        # Parse command line arguments
        self.args = self.parser.parse_args(args)

        self.ctx = AnalysisContext(
            charset='utf-8',
            unit_provider=self.create_unit_provider(),
            event_handler=self.create_event_handler(),
            with_trivia=True,
        )

        files = self.args.files
        if not files:
            files = self.default_get_files()

        # Parse files
        self.units = {}
        for file_name in files:
            self.u = self.ctx.get_from_file(file_name)
            if self.u.diagnostics:
                self.on_parsing_errors(self.u)
            self.units[file_name] = self.u

    def on_parsing_errors(self, unit: AnalysisUnit) -> None:
        """
        Callback invoked during App initialization, when a requested unit has a
        parsing error. By default, print the error on the standard output, but
        subclasses can override this behavior.
        """
        for d in unit.diagnostics:
            print(unit.format_gnu_diagnostic(d))

    def default_get_files(self) -> List[str]:
        """
        When no files are passed by the user on the command line, this method
        will be used. By default, it returns an empty list, but Langkit
        libraries can overload it to customize the behavior to adapt it to the
        specific language and toolchain.
        """
        return []

    def add_arguments(self) -> None:
        """
        Hook for subclasses to add arguments to self.parser. Default
        implementation does nothing.
        """
        pass

    def create_unit_provider(self) -> Opt[UnitProvider]:
        """
        Hook for subclasses to return a custom unit provider.
        Default implementation returns None.
        """
        return None

    def create_event_handler(self) -> Opt[EventHandler]:
        """
        Hook for subclasses to return a custom event handler. Default
        implementation returns None.
        """
        return None

    def main(self) -> None:
        """
        Default implementation for App.main: just iterates on every units and
        call ``process_unit`` on it.
        """
        for u in sorted(self.units.values(), key=lambda u: u.filename):
            self.process_unit(u)

    def process_unit(self, unit: AnalysisUnit) -> None:
        """
        Abstract method that processes one unit. Needs to be subclassed by
        implementors.
        """
        raise NotImplementedError()

    @classmethod
    def run(cls, args: Opt[List[str]]=None) -> None:
        """
        Instantiate and run this application.
        """
        cls(args).main()

    

