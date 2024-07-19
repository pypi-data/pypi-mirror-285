








with Ada.Exceptions;                  use Ada.Exceptions;
with Ada.Strings.Wide_Wide_Unbounded; use Ada.Strings.Wide_Wide_Unbounded;
with Ada.Unchecked_Conversion;

with System;

with Interfaces;           use Interfaces;
with Interfaces.C;         use Interfaces.C;
with Interfaces.C.Strings; use Interfaces.C.Strings;

with Langkit_Support.Slocs; use Langkit_Support.Slocs;
with Langkit_Support.Text;  use Langkit_Support.Text;

with Librflxlang.Common;   use Librflxlang.Common;




--  Internal package: defines data types and subprograms to provide the
--  implementation of the exported C API (see the corresponding C header file).

package Librflxlang.Implementation.C is

   subtype rflx_analysis_context is Internal_Context;
   --  This type represents a context for all source analysis. This is the
   --  first type you need to create to use Librflxlang. It will contain the
   --  results of all analysis, and is the main holder for all the data.
   --
   --  You can create several analysis contexts if you need to, which enables
   --  you, for example to:
   --
   --  * analyze several different projects at the same time;
   --
   --  * analyze different parts of the same projects in parallel.
   --
   --  In the current design, contexts always keep all of their analysis units
   --  allocated. If you need to get this memory released, the only option at
   --  your disposal is to destroy your analysis context instance.
   --
   --  This structure is partially opaque: some fields are exposed to allow
   --  direct access, for performance concerns.

   subtype rflx_analysis_unit is Internal_Unit;
   --  This type represents the analysis of a single file.
   --
   --  This type has strong-reference semantics and is ref-counted.
   --  Furthermore, a reference to a unit contains an implicit reference to the
   --  context that owns it. This means that keeping a reference to a unit will
   --  keep the context and all the unit it contains allocated.
   --
   --  This structure is partially opaque: some fields are exposed to allow
   --  direct access, for performance concerns.

   type rflx_base_node is new System.Address;
   --  Data type for all nodes. Nodes are assembled to make up a tree.  See the
   --  node primitives below to inspect such trees.
   --
   --  Unlike for contexts and units, this type has weak-reference semantics:
   --  keeping a reference to a node has no effect on the decision to keep the
   --  unit that it owns allocated. This means that once all references to the
   --  context and units related to a node are dropped, the context and its
   --  units are deallocated and the node becomes a stale reference: most
   --  operations on it will raise a ``Stale_Reference_Error``.
   --
   --  Note that since reparsing an analysis unit deallocates all the nodes it
   --  contains, this operation makes all reference to these nodes stale as
   --  well.

   type rflx_node_kind_enum is new int;
   --  Kind of AST nodes in parse trees.

   



subtype rflx_node is Internal_Entity;
type rflx_node_Ptr is access Internal_Entity;




   type rflx_symbol_type is record
      Data, Bounds : System.Address;
   end record
      with Convention => C;
   --  Reference to a symbol. Symbols are owned by analysis contexts, so they
   --  must not outlive them. This type exists only in the C API, and roughly
   --  wraps the corresponding Ada type (an array fat pointer).

   subtype rflx_string_type is String_Type;

   --  Helper data structures for source location handling

   type rflx_source_location is record
      Line   : Unsigned_32;
      Column : Unsigned_16;
   end record
     with Convention => C;

   type rflx_source_location_range is record
      Start_S, End_S : rflx_source_location;
   end record
     with Convention => C;

   type rflx_text is record
      Chars  : System.Address;
      --  Address for the content of the string.

      Length : size_t;
      --  Size of the string (in characters).

      Is_Allocated : int;
   end record
     with Convention => C;
   --  String encoded in UTF-32 (native endianness).

   type rflx_big_integer is new System.Address;
   --  Arbitrarily large integer.

   type rflx_token is record
      Context                   : rflx_analysis_context;
      Token_Data                : Token_Data_Handler_Access;
      Token_Index, Trivia_Index : int;
   end record
     with Convention => C;
   --  Reference to a token in an analysis unit.

   type rflx_diagnostic is record
      Sloc_Range : rflx_source_location_range;
      Message    : rflx_text;
      --  When the API returns a diagnostic, it is up to the caller to free the
      --  message string.
   end record
     with Convention => C;
   --  Diagnostic for an analysis unit: cannot open the source file, parsing
   --  error, ...

   type rflx_exception_kind is (
      Exception_File_Read_Error, Exception_Bad_Type_Error, Exception_Out_Of_Bounds_Error, Exception_Invalid_Input, Exception_Invalid_Symbol_Error, Exception_Invalid_Unit_Name_Error, Exception_Native_Exception, Exception_Precondition_Failure, Exception_Property_Error, Exception_Template_Args_Error, Exception_Template_Format_Error, Exception_Template_Instantiation_Error, Exception_Stale_Reference_Error, Exception_Syntax_Error, Exception_Unknown_Charset, Exception_Malformed_Tree_Error
   ) with Convention => C;
   --  Enumerated type describing all possible exceptions that need to be
   --  handled in the C bindings.

   type rflx_exception is record
      Kind : rflx_exception_kind;
      --  The kind of this exception.

      Information : chars_ptr;
      --  Message and context information associated with this exception.
   end record;
   --  Holder for native exceptions-related information.  Memory management for
   --  this and all the fields is handled by the library: one just has to make
   --  sure not to keep references to it.
   --
   --  .. TODO: For the moment, this structure contains already formatted
   --     information, but depending on possible future Ada runtime
   --     improvements, this might change.

   type rflx_exception_Ptr is access rflx_exception;

   type rflx_bool is new Unsigned_8;
   subtype uint32_t is Unsigned_32;

      subtype rflx_analysis_unit_kind is Analysis_Unit_Kind;
      subtype rflx_lookup_kind is Lookup_Kind;
      subtype rflx_designated_env_kind is Designated_Env_Kind;
      subtype rflx_grammar_rule is Grammar_Rule;

   procedure Free (Address : System.Address)
     with Export        => True,
          Convention    => C,
          External_Name => "rflx_free";
   --  Free dynamically allocated memory.
   --
   --  This is a helper to free objects from dynamic languages.
   --  Helper to free objects in dynamic languages

   procedure rflx_destroy_text (T : access rflx_text)
     with Export        => True,
          Convention    => C,
          External_Name => "rflx_destroy_text";
   --  If this text object owns the buffer it references, free this buffer.
   --
   --  Note that even though this accepts a pointer to a text object, it does
   --  not deallocates the text object itself but rather the buffer it
   --  references.

   procedure rflx_symbol_text
     (Symbol : access rflx_symbol_type; Text : access rflx_text)
      with Export, Convention => C,
           External_Name => "rflx_symbol_text";
   --  Return the text associated to this symbol.

   function rflx_create_big_integer
     (Text : access rflx_text) return rflx_big_integer
      with Export, Convention => C,
           External_Name => "rflx_create_big_integer";
   --  Create a big integer from its string representation (in base 10).

   procedure rflx_big_integer_text
     (Bigint : rflx_big_integer; Text : access rflx_text)
      with Export, Convention => C,
           External_Name => "rflx_big_integer_text";
   --  Return the string representation (in base 10) of this big integer.

   procedure rflx_big_integer_decref
     (Bigint : rflx_big_integer)
      with Export, Convention => C,
           External_Name => "rflx_big_integer_decref";
   --  Decrease the reference count for this big integer.

   procedure rflx_get_versions
     (Version, Build_Date : access chars_ptr)
      with Export, Convention => C,
           External_Name => "rflx_get_versions";
   --  Allocate strings to represent the library version number and build date
   --  and put them in Version/Build_Date. Callers are expected to call free()
   --  on the returned string once done.

   function rflx_create_string
     (Content : System.Address; Length : int) return rflx_string_type
      with Export, Convention => C,
           External_Name => "rflx_create_string";
   --  Create a string value from its content (UTF32 with native endianity).
   --
   --  Note that the CONTENT buffer argument is copied: the returned value does
   --  not contain a reference to it.

   procedure rflx_string_dec_ref (Self : rflx_string_type)
      with Export, Convention => C,
           External_Name => "rflx_string_dec_ref";
   --  Decrease the reference count for this string.

   ------------------
   -- File readers --
   ------------------

   type rflx_file_reader is new System.Address;
   --  Interface to override how source files are fetched and decoded.

   type rflx_file_reader_destroy_callback is access procedure
     (Data : System.Address)
      with Convention => C;
   --  Callback type for functions that are called when destroying a file
   --  reader.

   type rflx_file_reader_read_callback is access procedure
     (Data       : System.Address;
      Filename   : chars_ptr;
      Charset    : chars_ptr;
      Read_BOM   : int;
      Buffer     : access rflx_text;
      Diagnostic : access rflx_diagnostic)
      with Convention => C;
   --  Callback type for functions that are called to fetch the decoded source
   --  buffer for a requested filename.

   --------------------
   -- Event handlers --
   --------------------

   type rflx_event_handler is new System.Address;
   --  Interface to handle events sent by the analysis context.

   type rflx_event_handler_unit_requested_callback is access procedure
     (Data               : System.Address;
      Context            : rflx_analysis_context;
      Name               : access constant rflx_text;
      From               : rflx_analysis_unit;
      Found              : rflx_bool;
      Is_Not_Found_Error : rflx_bool)
      with Convention => C;
   --  Callback that will be called when a unit is requested from the context
   --  ``Context``.
   --
   --  ``Name`` is the name of the requested unit.
   --
   --  ``From`` is the unit from which the unit was requested.
   --
   --  ``Found`` indicates whether the requested unit was found or not.
   --
   --  ``Is_Not_Found_Error`` indicates whether the fact that the unit was not
   --  found is an error or not.
   --
   --  .. warning:: The interface of this callback is probably subject to
   --     change, so should be treated as experimental.

   type rflx_event_handler_unit_parsed_callback is access procedure
     (Data     : System.Address;
      Context  : rflx_analysis_context;
      Unit     : rflx_analysis_unit;
      Reparsed : rflx_bool)
      with Convention => C;
   --  Callback that will be called when any unit is parsed from the context
   --  ``Context``.
   --
   --  ``Unit`` is the resulting unit.
   --
   --  ``Reparsed`` indicates whether the unit was reparsed, or whether it was
   --  the first parse.

   type rflx_event_handler_destroy_callback is access procedure
     (Data : System.Address)
      with Convention => C;
   --  Callback type for functions that are called when destroying an event
   --  handler.

   --------------------
   -- Unit providers --
   --------------------

   type rflx_unit_provider is new System.Address;
   --  Interface to fetch analysis units from a name and a unit kind.
   --
   --  The unit provider mechanism provides an abstraction which assumes that
   --  to any couple (unit name, unit kind) we can associate at most one source
   --  file. This means that several couples can be associated to the same
   --  source file, but on the other hand, only one one source file can be
   --  associated to a couple.
   --
   --  This is used to make the semantic analysis able to switch from one
   --  analysis units to another.
   --
   --  See the documentation of each unit provider for the exact semantics of
   --  the unit name/kind information.

   -------------------------
   -- Analysis primitives --
   -------------------------

   function rflx_allocate_analysis_context
     return rflx_analysis_context
     with Export,
          Convention    => C,
          External_name => "rflx_allocate_analysis_context";
   --  Allocate a new analysis context.

   procedure rflx_initialize_analysis_context
     (Context       : rflx_analysis_context;
      Charset       : chars_ptr;
      File_Reader   : rflx_file_reader;
      Unit_Provider : rflx_unit_provider;
      Event_Handler : rflx_event_handler;
      With_Trivia   : int;
      Tab_Stop      : int)
      with Export,
           Convention    => C,
           External_name => "rflx_initialize_analysis_context";
   --  Initialize an analysis context. Must be called right after
   --  ``Allocate_Context`` on its result.
   --
   --  Having separate primitives for allocation/initialization allows library
   --  bindings to have a context wrapper (created between the two calls) ready
   --  when callbacks that happen during context initialization (for instance
   --  "unit parsed" events).

   function rflx_context_incref
     (Context : rflx_analysis_context)
      return rflx_analysis_context
      with Export        => True,
           Convention    => C,
           External_name => "rflx_context_incref";
   --  Increase the reference count to an analysis context. Return the
   --  reference for convenience.

   procedure rflx_context_decref
     (Context : rflx_analysis_context)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_context_decref";
   --  Decrease the reference count to an analysis context. Destruction happens
   --  when the ref-count reaches 0.

   function rflx_context_symbol
     (Context : rflx_analysis_context;
      Text    : access rflx_text;
      Symbol  : access rflx_symbol_type) return int
      with Export, Convention => C,
           External_name => "rflx_context_symbol";
   --  If the given string is a valid symbol, yield it as a symbol and return
   --  true. Otherwise, return false.

   procedure rflx_context_discard_errors_in_populate_lexical_env
     (Context : rflx_analysis_context;
      Discard : int)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_context_discard_errors_in_populate_lexical_env";
   --  Debug helper. Set whether ``Property_Error`` exceptions raised in
   --  ``Populate_Lexical_Env`` should be discarded. They are by default.

   function rflx_get_analysis_unit_from_file
     (Context           : rflx_analysis_context;
      Filename, Charset : chars_ptr;
      Reparse           : int;
      Rule              : rflx_grammar_rule)
      return rflx_analysis_unit
      with Export        => True,
           Convention    => C,
           External_name =>
              "rflx_get_analysis_unit_from_file";
   --  Create a new analysis unit for ``Filename`` or return the existing one
   --  if any. If ``Reparse`` is true and the analysis unit already exists,
   --  reparse it from ``Filename``.
   --
   --  ``Rule`` controls which grammar rule is used to parse the unit.
   --
   --  Use ``Charset`` in order to decode the source. If ``Charset`` is empty
   --  then use the context's default charset.
   --
   --  If any failure occurs, such as file opening, decoding, lexing or parsing
   --  failure, return an analysis unit anyway: errors are described as
   --  diagnostics of the returned analysis unit.

   function rflx_get_analysis_unit_from_buffer
     (Context           : rflx_analysis_context;
      Filename, Charset : chars_ptr;
      Buffer            : chars_ptr;
      Buffer_Size       : size_t;
      Rule              : rflx_grammar_rule)
      return rflx_analysis_unit
      with Export        => True,
           Convention    => C,
           External_name =>
              "rflx_get_analysis_unit_from_buffer";
   --  Create a new analysis unit for ``Filename`` or return the existing one
   --  if any. Whether the analysis unit already exists or not, (re)parse it
   --  from the source code in ``Buffer``.
   --
   --  ``Rule`` controls which grammar rule is used to parse the unit.
   --
   --  Use ``Charset`` in order to decode the source. If ``Charset`` is empty
   --  then use the context's default charset.
   --
   --  If any failure occurs, such as file opening, decoding, lexing or parsing
   --  failure, return an analysis unit anyway: errors are described as
   --  diagnostics of the returned analysis unit.


   procedure rflx_unit_root
     (Unit     : rflx_analysis_unit;
      Result_P : rflx_node_Ptr)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_root";
   --  Return the root node for this unit, or ``NULL`` if there is none.

   procedure rflx_unit_first_token
     (Unit  : rflx_analysis_unit;
      Token : access rflx_token)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_first_token";
   --  Return a reference to the first token scanned in this unit.

   procedure rflx_unit_last_token
     (Unit  : rflx_analysis_unit;
      Token : access rflx_token)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_last_token";
   --  Return a reference to the last token scanned in this unit.

   function rflx_unit_token_count
     (Unit : rflx_analysis_unit) return int
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_unit_token_count";
   --  Return the number of tokens in this unit.

   function rflx_unit_trivia_count
     (Unit : rflx_analysis_unit) return int
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_unit_trivia_count";
   --  Return the number of trivias in this unit. This is 0 for units that were
   --  parsed with trivia analysis disabled.

   procedure rflx_unit_lookup_token
     (Unit   : rflx_analysis_unit;
      Sloc   : access rflx_source_location;
      Result : access rflx_token)
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_unit_lookup_token";
   --  Look for a token in this unit that contains the given source location.
   --  If this falls before the first token, return the first token. If this
   --  falls between two tokens, return the token that appears before. If this
   --  falls after the last token, return the last token. If there is no token
   --  in this unit, return no token.

   procedure rflx_unit_dump_lexical_env
     (Unit : rflx_analysis_unit)
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_unit_dump_lexical_env";

   function rflx_unit_filename
     (Unit : rflx_analysis_unit)
      return chars_ptr
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_filename";
   --  Return the filename this unit is associated to.
   --
   --  The returned string is dynamically allocated and the caller must free it
   --  when done with it.

   function rflx_unit_diagnostic_count
     (Unit : rflx_analysis_unit) return unsigned
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_diagnostic_count";
   --  Return the number of diagnostics associated to this unit.

   function rflx_unit_diagnostic
     (Unit         : rflx_analysis_unit;
      N            : unsigned;
      Diagnostic_P : access rflx_diagnostic) return int
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_diagnostic";
   --  Get the Nth diagnostic in this unit and store it into ``*diagnostic_p``.
   --  Return zero on failure (when N is too big).

   function rflx_unit_context
     (Unit : rflx_analysis_unit)
      return rflx_analysis_context
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_context";
   --  Return the context that owns this unit.

   procedure rflx_unit_reparse_from_file
     (Unit : rflx_analysis_unit; Charset : chars_ptr)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_reparse_from_file";
   --  Reparse an analysis unit from the associated file.
   --
   --  Use ``Charset`` in order to decode the source. If ``Charset`` is empty
   --  then use the context's default charset.
   --
   --  If any failure occurs, such as decoding, lexing or parsing failure,
   --  diagnostic are emitted to explain what happened.

   procedure rflx_unit_reparse_from_buffer
     (Unit        : rflx_analysis_unit;
      Charset     : chars_ptr;
      Buffer      : chars_ptr;
      Buffer_Size : size_t)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_reparse_from_buffer";
   --  Reparse an analysis unit from a buffer.
   --
   --  Use ``Charset`` in order to decode the source. If ``Charset`` is empty
   --  then use the context's default charset.
   --
   --  If any failure occurs, such as decoding, lexing or parsing failure,
   --  diagnostic are emitted to explain what happened.

   function rflx_unit_populate_lexical_env
     (Unit : rflx_analysis_unit
   ) return int
      with Export        => True,
           Convention    => C,
           External_name => "rflx_unit_populate_lexical_env";
   --  Create lexical environments for this analysis unit, according to the
   --  specifications given in the language spec.
   --
   --  If not done before, it will be automatically called during semantic
   --  analysis. Calling it before enables one to control where the latency
   --  occurs.
   --
   --  Depending on whether errors are discarded (see
   --  ``Discard_Errors_In_Populate_Lexical_Env``), return ``0`` on failure and
   --  ``1`` on success.

   ---------------------------------
   -- General AST node primitives --
   ---------------------------------

   procedure rflx_create_bare_entity
     (Node   : rflx_base_node;
      Entity : access rflx_node)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_create_bare_entity";
   --  Create an entity with null entity info for a given node.

   function rflx_is_equivalent
     (L, R : rflx_node_Ptr) return rflx_bool
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_is_equivalent";
   --  Return whether the two nodes are equivalent.

   function rflx_hash
     (Node : rflx_node_Ptr) return uint32_t
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_hash";
   --  Return a hash for the given node.

   function rflx_node_kind
     (Node : rflx_node_Ptr) return rflx_node_kind_enum
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_kind";
   --  Return the kind of this node.

   procedure rflx_kind_name
     (Kind : rflx_node_kind_enum; Result : access rflx_text)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_kind_name";
   --  Helper for textual dump: return the kind name for this node. The
   --  returned string is a copy and thus must be free'd by the caller.

   function rflx_node_unit
     (Node : rflx_node_Ptr) return rflx_analysis_unit
      with Export => True,
           Convention => C,
           External_Name => "rflx_node_unit";
   --  Return the analysis unit that owns this node.

   function rflx_is_token_node
     (Node : rflx_node_Ptr) return int
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_is_token_node";
   --  Return whether this node is a node that contains only a single token.

   function rflx_is_synthetic
     (Node : rflx_node_Ptr) return int
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_is_synthetic";
   --  Return whether this node is synthetic.

   procedure rflx_node_image
     (Node : rflx_node_Ptr; Result : access rflx_text)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_image";
   --  Return a representation of this node as a string.

   procedure rflx_node_text
     (Node : rflx_node_Ptr;
      Text : access rflx_text)
      with Export, Convention => C,
           External_Name      => "rflx_node_text";
   --  Return the source buffer slice corresponding to the text that spans
   --  between the first and the last tokens of this node.
   --
   --  Note that this returns the empty string for synthetic nodes.

   procedure rflx_node_sloc_range
     (Node         : rflx_node_Ptr;
      Sloc_Range_P : access rflx_source_location_range)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_sloc_range";
   --  Return the spanning source location range for this node.
   --
   --  Note that this returns the sloc of the parent for synthetic nodes.

   procedure rflx_lookup_in_node
     (Node   : rflx_node_Ptr;
      Sloc   : rflx_source_location;
      Result : rflx_node_Ptr)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_lookup_in_node";
   --  Return the bottom-most node from in ``Node`` and its children which
   --  contains ``Sloc``, or ``NULL`` if there is none.

   function rflx_node_children_count
     (Node : rflx_node_Ptr) return unsigned
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_children_count";
   --  Return the number of children in this node.

   function rflx_node_child
     (Node    : rflx_node_Ptr;
      N       : unsigned;
      Child_P : rflx_node_Ptr) return int
      with Export        => True,
           Convention    => C,
           External_name => "rflx_node_child";
   --  Return the Nth child for in this node's fields and store it into
   --  ``*child_p``.  Return zero on failure (when ``N`` is too big).

   function rflx_text_to_locale_string
     (Text : rflx_text) return System.Address
      with Export        => True,
           Convention    => C,
           External_name => "rflx_text_to_locale_string";
   --  Encode some text using the current locale. The result is dynamically
   --  allocated: it is up to the caller to free it when done with it.
   --
   --  This is a development helper to make it quick and easy to print token
   --  and diagnostic text: it ignores errors (when the locale does not support
   --  some characters). Production code should use real conversion routines
   --  such as libiconv's in order to deal with UTF-32 texts.

   ------------------
   -- File readers --
   ------------------

   function rflx_create_file_reader
     (Data         : System.Address;
      Destroy_Func : rflx_file_reader_destroy_callback;
      Read_Func    : rflx_file_reader_read_callback) return rflx_file_reader
      with Export        => True,
           Convention    => C,
           External_name => "rflx_create_file_reader";
   --  Create a file reader. When done with it, the result must be passed to
   --  ``rflx_dec_ref_file_reader``.
   --
   --  Pass as ``data`` a pointer to hold your private data: it will be passed
   --  to all callbacks below.
   --
   --  ``destroy`` is a callback that is called by ``rflx_dec_ref_file_reader``
   --  to leave a chance to free resources that ``data`` may hold.
   --
   --  ``read`` is a callback. For a given filename/charset and whether to read
   --  the BOM (Byte Order Mark), it tries to fetch the contents of the source
   --  file, returned in ``Contents``. If there is an error, it must return it
   --  in ``Diagnostic`` instead.

   procedure rflx_dec_ref_file_reader
     (File_Reader : rflx_file_reader)
      with Export        => True,
           Convention    => C,
           External_name =>
              "rflx_dec_ref_file_reader";
   --  Release an ownership share for this file reader. This destroys the file
   --  reader if there are no shares left.

   


   --------------------
   -- Event handlers --
   --------------------

   function rflx_create_event_handler
     (Data                : System.Address;
      Destroy_Func        : rflx_event_handler_destroy_callback;
      Unit_Requested_Func : rflx_event_handler_unit_requested_callback;
      Unit_Parsed_Func    : rflx_event_handler_unit_parsed_callback)
      return rflx_event_handler
      with Export        => True,
           Convention    => C,
           External_name => "rflx_create_event_handler";
   --  Create an event handler. When done with it, the result must be passed to
   --  ``rflx_dec_ref_event_handler``.
   --
   --  Pass as ``data`` a pointer to hold your private data: it will be passed
   --  to all callbacks below.
   --
   --  ``destroy`` is a callback that is called by
   --  ``rflx_dec_ref_event_handler`` to leave a chance to free resources that
   --  ``data`` may hold. ``NULL`` can be passed if nothing needs to be done.
   --
   --  ``unit_requested`` is a callback that will be called when a unit is
   --  requested.
   --
   --  .. warning:: Please note that the unit requested callback can be called
   --     *many* times for the same unit, so in all likeliness, those events
   --     should be filtered if they're used to forward diagnostics to the
   --     user.
   --
   --  ``unit_parsed`` is a callback that will be called when a unit is parsed.

   procedure rflx_dec_ref_event_handler
     (Handler : rflx_event_handler)
      with Export        => True,
           Convention    => C,
           External_name =>
              "rflx_dec_ref_event_handler";
   --  Release an ownership share for this event handler. This destroys the
   --  event handler if there are no shares left.

   


   --------------------
   -- Unit providers --
   --------------------

   procedure rflx_dec_ref_unit_provider
     (Provider : rflx_unit_provider)
      with Export        => True,
           Convention    => C,
           External_name =>
              "rflx_dec_ref_unit_provider";
   --  Release an ownership share for this unit provider. This destroys the
   --  unit provider if there are no shares left.

   


   ------------------
   -- Struct types --
   ------------------


   -----------------
   -- Array types --
   -----------------

         



subtype rflx_node_array is Internal_Entity_Array_Access;
type rflx_node_array_Ptr is access Internal_Entity_Array_Access;

function rflx_node_array_create (Length : int) return Internal_Entity_Array_Access
   with Export        => True,
        Convention    => C,
        External_name => "rflx_node_array_create";

procedure rflx_node_array_inc_ref (A : Internal_Entity_Array_Access)
   with Export        => True,
        Convention    => C,
        External_name => "rflx_node_array_inc_ref";

procedure rflx_node_array_dec_ref (A : Internal_Entity_Array_Access)
   with Export        => True,
        Convention    => C,
        External_name => "rflx_node_array_dec_ref";



   --------------------
   -- Iterator types --
   --------------------


   ----------
   -- Misc --
   ----------

   function rflx_get_last_exception return rflx_exception_Ptr
     with Export        => True,
          Convention    => C,
          External_Name => "rflx_get_last_exception";
   --  Return exception information for the last error that happened in the
   --  current thread. Will be automatically allocated on error and free'd on
   --  the next error.

   function rflx_exception_name
     (Kind : rflx_exception_kind) return chars_ptr
      with Export, Convention => C;
   --  Return the name of the given exception kind. Callers are responsible for
   --  free'ing the result.

   procedure Clear_Last_Exception;
   --  Free the information contained in Last_Exception

   procedure Set_Last_Exception (Exc : Exception_Occurrence);
   --  Free the information contained in Last_Exception and replace it with
   --  newly allocated information from Exc.

   procedure Set_Last_Exception (Id : Exception_Id; Message : String);
   --  Likewise, but put destructured exception information. This is useful to
   --  pass messages that are longer than what the Ada runtime accepts (i.e.
   --  allows to avoid truncated error messages).

   function rflx_token_get_kind
     (Token : rflx_token) return int
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_token_get_kind";
   --  Kind for this token.

   function rflx_token_kind_name (Kind : int) return chars_ptr
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_token_kind_name";
   --  Return a human-readable name for a token kind.
   --
   --  The returned string is dynamically allocated and the caller must free it
   --  when done with it.
   --
   --  If the given kind is invalid, return ``NULL`` and set the last exception
   --  accordingly.

   procedure rflx_token_sloc_range
     (Token : rflx_token; Result : access rflx_source_location_range)
      with Export        => True,
           Convention    => C,
           External_Name => "rflx_token_sloc_range";
   --  Return the source location range of the given token.

   procedure rflx_token_next
     (Token      : rflx_token;
      Next_Token : access rflx_token)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_token_next";
   --  Return a reference to the next token in the corresponding analysis unit.

   procedure rflx_token_previous
     (Token          : rflx_token;
      Previous_Token : access rflx_token)
      with Export        => True,
           Convention    => C,
           External_name => "rflx_token_previous";
   --  Return a reference to the previous token in the corresponding analysis
   --  unit.

   function rflx_token_range_text
     (First, Last : rflx_token;
      Text        : access rflx_text) return int
      with Export => True,
           Convention => C,
           External_Name => "rflx_token_range_text";
   --  Compute the source buffer slice corresponding to the text that spans
   --  between the ``First`` and ``Last`` tokens (both included). This yields
   --  an empty slice if ``Last`` actually appears before ``First``. Put the
   --  result in ``RESULT``.
   --
   --  This returns ``0`` if ``First`` and ``Last`` don't belong to the same
   --  analysis unit. Return ``1`` if successful.

   function rflx_token_is_equivalent
     (Left  : rflx_token;
      Right : rflx_token) return rflx_bool
      with Export        => True,
           Convention    => C,
           External_name => "rflx_token_is_equivalent";
   --  Return whether ``L`` and ``R`` are structurally equivalent tokens. This
   --  means that their position in the stream won't be taken into account,
   --  only the kind and text of the token.

   ---------------------------------------
   -- Kind-specific AST node primitives --
   ---------------------------------------

   --  All these primitives return their result through an OUT parameter. They
   --  return a boolean telling whether the operation was successful (it can
   --  fail if the node does not have the proper type, for instance). When an
   --  AST node is returned, its ref-count is left as-is.

           
   

   
   

   function rflx_r_f_l_x_node_parent
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_parent";
   --  Return the syntactic parent for this node. Return null for the root
   --  node.

           
   

   
   

   function rflx_r_f_l_x_node_parents
     (Node : rflx_node_Ptr;

         With_Self :
            
            rflx_bool;

      Value_P : access rflx_node_array) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_parents";
   --  Return an array that contains the lexical parents, this node included
   --  iff ``with_self`` is True. Nearer parents are first in the list.

           
   

   
   

   function rflx_r_f_l_x_node_children
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node_array) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_children";
   --  Return an array that contains the direct lexical children.
   --
   --  .. warning:: This constructs a whole array every-time you call it, and
   --     as such is less efficient than calling the ``Child`` built-in.

           
   

   
   

   function rflx_r_f_l_x_node_token_start
     (Node : rflx_node_Ptr;


      Value_P : access rflx_token) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_token_start";
   --  Return the first token used to parse this node.

           
   

   
   

   function rflx_r_f_l_x_node_token_end
     (Node : rflx_node_Ptr;


      Value_P : access rflx_token) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_token_end";
   --  Return the last token used to parse this node.

           
   

   
   

   function rflx_r_f_l_x_node_child_index
     (Node : rflx_node_Ptr;


      Value_P : access int) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_child_index";
   --  Return the 0-based index for Node in its parent's children.

           
   

   
   

   function rflx_r_f_l_x_node_previous_sibling
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_previous_sibling";
   --  Return the node's previous sibling, or null if there is no such sibling.

           
   

   
   

   function rflx_r_f_l_x_node_next_sibling
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_next_sibling";
   --  Return the node's next sibling, or null if there is no such sibling.

           
   

   
   

   function rflx_r_f_l_x_node_unit
     (Node : rflx_node_Ptr;


      Value_P : access rflx_analysis_unit) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_unit";
   --  Return the analysis unit owning this node.

           
   

   
   

   function rflx_r_f_l_x_node_is_ghost
     (Node : rflx_node_Ptr;


      Value_P : access rflx_bool) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_is_ghost";
   --  Return whether the node is a ghost.
   --
   --  Unlike regular nodes, ghost nodes cover no token in the input source:
   --  they are logically located instead between two tokens. Both the
   --  ``token_start`` and the ``token_end`` of all ghost nodes is the token
   --  right after this logical position.

           
   

   
   

   function rflx_r_f_l_x_node_full_sloc_image
     (Node : rflx_node_Ptr;


      Value_P : access rflx_string_type) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_r_f_l_x_node_full_sloc_image";
   --  Return a string containing the filename + the sloc in GNU conformant
   --  format. Useful to create diagnostics from a node.

           
   

   
   

   function rflx_i_d_f_package
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_i_d_f_package";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_i_d_f_name
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_i_d_f_name";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_aspect_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_aspect_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_aspect_f_value
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_aspect_f_value";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_message_aggregate_associations_f_associations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_aggregate_associations_f_associations";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_checksum_val_f_data
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_checksum_val_f_data";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_checksum_value_range_f_first
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_checksum_value_range_f_first";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_checksum_value_range_f_last
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_checksum_value_range_f_last";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_checksum_assoc_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_checksum_assoc_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_checksum_assoc_f_covered_fields
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_checksum_assoc_f_covered_fields";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_refinement_decl_f_pdu
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_refinement_decl_f_pdu";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_refinement_decl_f_field
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_refinement_decl_f_field";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_refinement_decl_f_sdu
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_refinement_decl_f_sdu";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_refinement_decl_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_refinement_decl_f_condition";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_session_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_session_decl_f_parameters";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_session_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_session_decl_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_session_decl_f_declarations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_session_decl_f_declarations";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_session_decl_f_states
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_session_decl_f_states";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_session_decl_f_end_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_session_decl_f_end_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_type_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_type_decl_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_type_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_type_decl_f_parameters";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_type_decl_f_definition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_type_decl_f_definition";
   --  This field can contain one of the following nodes:
   --  :ada:ref:`Abstract_Message_Type_Def`, :ada:ref:`Enumeration_Type_Def`,
   --  :ada:ref:`Integer_Type_Def`, :ada:ref:`Sequence_Type_Def`,
   --  :ada:ref:`Type_Derivation_Def`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_description_f_content
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_description_f_content";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_element_value_assoc_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_element_value_assoc_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_element_value_assoc_f_literal
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_element_value_assoc_f_literal";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_attribute_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_attribute_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Binding`, :ada:ref:`Call`, :ada:ref:`Case_Expression`,
   --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
   --  :ada:ref:`Message_Aggregate`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_attribute_f_kind
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_attribute_f_kind";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_bin_op_f_left
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_bin_op_f_left";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_bin_op_f_op
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_bin_op_f_op";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_bin_op_f_right
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_bin_op_f_right";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_binding_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_binding_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Binding`, :ada:ref:`Call`, :ada:ref:`Case_Expression`,
   --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
   --  :ada:ref:`Message_Aggregate`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_binding_f_bindings
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_binding_f_bindings";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_call_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_call_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_call_f_arguments
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_call_f_arguments";
   --  This field contains a list that itself contains one of the following
   --  nodes: :ada:ref:`Attribute`, :ada:ref:`Bin_Op`, :ada:ref:`Binding`,
   --  :ada:ref:`Call`, :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_case_expression_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_case_expression_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_case_expression_f_choices
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_case_expression_f_choices";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_choice_f_selectors
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_choice_f_selectors";
   --  This field contains a list that itself contains one of the following
   --  nodes: :ada:ref:`I_D`, :ada:ref:`Numeric_Literal`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_choice_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_choice_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_comprehension_f_iterator
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_comprehension_f_iterator";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_comprehension_f_sequence
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_comprehension_f_sequence";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_comprehension_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_comprehension_f_condition";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_comprehension_f_selector
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_comprehension_f_selector";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_context_item_f_item
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_context_item_f_item";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_conversion_f_target_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_conversion_f_target_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_conversion_f_argument
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_conversion_f_argument";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_aggregate_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_aggregate_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_aggregate_f_values
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_aggregate_f_values";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_negation_f_data
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_negation_f_data";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Numeric_Literal`, :ada:ref:`Paren_Expression`,
   --  :ada:ref:`Quantified_Expression`, :ada:ref:`Select_Node`,
   --  :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_paren_expression_f_data
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_paren_expression_f_data";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_quantified_expression_f_operation
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_quantified_expression_f_operation";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_quantified_expression_f_parameter_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_quantified_expression_f_parameter_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_quantified_expression_f_iterable
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_quantified_expression_f_iterable";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_quantified_expression_f_predicate
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_quantified_expression_f_predicate";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_select_node_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_select_node_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Binding`, :ada:ref:`Call`, :ada:ref:`Case_Expression`,
   --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
   --  :ada:ref:`Message_Aggregate`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_select_node_f_selector
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_select_node_f_selector";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_concatenation_f_left
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_concatenation_f_left";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_concatenation_f_right
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_concatenation_f_right";
   --  This field can contain one of the following nodes:
   --  :ada:ref:`Sequence_Aggregate`, :ada:ref:`String_Literal`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_sequence_aggregate_f_values
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_sequence_aggregate_f_values";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_variable_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_variable_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_formal_channel_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_formal_channel_decl_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_formal_channel_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_formal_channel_decl_f_parameters";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_formal_function_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_formal_function_decl_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_formal_function_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_formal_function_decl_f_parameters";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_formal_function_decl_f_return_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_formal_function_decl_f_return_type_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_renaming_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_renaming_decl_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_renaming_decl_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_renaming_decl_f_type_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_renaming_decl_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_renaming_decl_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_variable_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_variable_decl_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_variable_decl_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_variable_decl_f_type_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_variable_decl_f_initializer
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_variable_decl_f_initializer";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_message_aggregate_association_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_aggregate_association_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_aggregate_association_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_aggregate_association_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_byte_order_aspect_f_byte_order
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_byte_order_aspect_f_byte_order";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_checksum_aspect_f_associations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_checksum_aspect_f_associations";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_f_type_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_f_type_arguments
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_f_type_arguments";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_f_aspects";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_f_condition";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_message_field_f_thens
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_f_thens";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_fields_f_initial_field
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_fields_f_initial_field";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_message_fields_f_fields
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_fields_f_fields";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_null_message_field_f_thens
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_null_message_field_f_thens";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_package_node_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_package_node_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_package_node_f_declarations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_package_node_f_declarations";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_package_node_f_end_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_package_node_f_end_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_parameter_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_parameter_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_parameter_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_parameter_f_type_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_parameters_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_parameters_f_parameters";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_specification_f_context_clause
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_specification_f_context_clause";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_specification_f_package_declaration
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_specification_f_package_declaration";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_f_description
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_f_description";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_state_f_body
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_f_body";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_body_f_declarations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_body_f_declarations";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_body_f_actions
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_body_f_actions";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_body_f_conditional_transitions
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_body_f_conditional_transitions";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_body_f_final_transition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_body_f_final_transition";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_state_body_f_exception_transition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_body_f_exception_transition";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_state_body_f_end_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_state_body_f_end_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_assignment_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_assignment_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_assignment_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_assignment_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_attribute_statement_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_attribute_statement_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_attribute_statement_f_attr
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_attribute_statement_f_attr";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_attribute_statement_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_attribute_statement_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_assignment_f_message
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_assignment_f_message";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_assignment_f_field
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_assignment_f_field";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_field_assignment_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_field_assignment_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_reset_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_reset_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_reset_f_associations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_reset_f_associations";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_term_assoc_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_term_assoc_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_term_assoc_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_term_assoc_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_then_node_f_target
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_then_node_f_target";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_then_node_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_then_node_f_aspects";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_then_node_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_then_node_f_condition";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_transition_f_target
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_transition_f_target";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_transition_f_description
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_transition_f_description";
   --  This field may be null even when there are no parsing errors.

           
   

   
   

   function rflx_conditional_transition_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_conditional_transition_f_condition";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_type_argument_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_type_argument_f_identifier";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_type_argument_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_type_argument_f_expression";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_type_def_f_message_fields
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_type_def_f_message_fields";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_message_type_def_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_message_type_def_f_aspects";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_named_enumeration_def_f_elements
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_named_enumeration_def_f_elements";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_positional_enumeration_def_f_elements
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_positional_enumeration_def_f_elements";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_enumeration_type_def_f_elements
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_enumeration_type_def_f_elements";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_enumeration_type_def_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_enumeration_type_def_f_aspects";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_modular_type_def_f_mod
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_modular_type_def_f_mod";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_range_type_def_f_first
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_range_type_def_f_first";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_range_type_def_f_last
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_range_type_def_f_last";
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_range_type_def_f_size
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_range_type_def_f_size";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_sequence_type_def_f_element_type
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_sequence_type_def_f_element_type";
   --  When there are no parsing errors, this field is never null.

           
   

   
   

   function rflx_type_derivation_def_f_base
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

      with Export        => True,
           Convention    => C,
           External_name => "rflx_type_derivation_def_f_base";
   --  When there are no parsing errors, this field is never null.


   ------------------------
   -- Conversion helpers --
   ------------------------

   --  The following conversion helpers are use by the various C bindings

   function Wrap (S : Source_Location) return rflx_source_location is
     ((Unsigned_32 (S.Line), Unsigned_16 (S.Column)));
   function Unwrap (S : rflx_source_location) return Source_Location is
     ((Line_Number (S.Line), Column_Number (S.Column)));

   function Wrap (S : Source_Location_Range) return rflx_source_location_range is
     ((Start_S => (Unsigned_32 (S.Start_Line), Unsigned_16 (S.Start_Column)),
       End_S   => (Unsigned_32 (S.End_Line),   Unsigned_16 (S.End_Column))));
   function Unwrap (S : rflx_source_location_range) return Source_Location_Range is
     ((Line_Number (S.Start_S.Line),
       Line_Number (S.End_S.Line),
       Column_Number (S.Start_S.Column),
       Column_Number (S.End_S.Column)));

   function Wrap (S : Unbounded_Wide_Wide_String) return rflx_text;

   function Wrap_Alloc (S : Text_Type) return rflx_text;
   function Wrap_Alloc (S : Unbounded_Wide_Wide_String) return rflx_text;
   function Wrap
     (S     : Text_Cst_Access;
      First : Positive;
      Last  : Natural) return rflx_text;

   function Wrap (T : Text_Cst_Access) return rflx_text is
     (if T = null
      then (Chars => System.Null_Address, Length => 0, Is_Allocated => 0)
      else (Chars => T.all'Address, Length => T.all'Length, Is_Allocated => 0));
   function Wrap (T : Text_Access) return rflx_text is
     (Wrap (Text_Cst_Access (T)));

   function Wrap_Big_Integer is new Ada.Unchecked_Conversion
     (Big_Integer_Type, rflx_big_integer);
   function Unwrap_Big_Integer is new Ada.Unchecked_Conversion
     (rflx_big_integer, Big_Integer_Type);

   --  Probably because the following conversions involve fat pointers, using
   --  the No_Strict_Aliasing pragma here has no effect. Silence the warning,
   --  since all read/writes for the pointed values are made through the "real"
   --  fat pointer (Symbol_Type) and not the fake one (rflx_symbol_type): strict
   --  aliasing issues should not happen.

   pragma Warnings (Off, "possible aliasing problem for type");
   function Wrap_Symbol is new Ada.Unchecked_Conversion
     (Symbol_Type, rflx_symbol_type);
   function Unwrap_Symbol is new Ada.Unchecked_Conversion
     (rflx_symbol_type, Symbol_Type);
   pragma Warnings (On, "possible aliasing problem for type");

   function Wrap is new Ada.Unchecked_Conversion
     (Bare_R_F_L_X_Node, rflx_base_node);
   function Unwrap is new Ada.Unchecked_Conversion
     (rflx_base_node, Bare_R_F_L_X_Node);

   function Wrap (Token : Token_Reference) return rflx_token;
   function Unwrap (Token : rflx_token) return Token_Reference;

   function Wrap_Private_File_Reader is new Ada.Unchecked_Conversion
     (Internal_File_Reader_Access, rflx_file_reader);
   function Unwrap_Private_File_Reader is new Ada.Unchecked_Conversion
     (rflx_file_reader, Internal_File_Reader_Access);

   function Wrap_Private_Event_Handler is new Ada.Unchecked_Conversion
     (Internal_Event_Handler_Access, rflx_event_handler);
   function Unwrap_Private_Event_Handler is new Ada.Unchecked_Conversion
     (rflx_event_handler, Internal_Event_Handler_Access);

   function Wrap_Private_Provider is new Ada.Unchecked_Conversion
     (Internal_Unit_Provider_Access, rflx_unit_provider);
   function Unwrap_Private_Provider is new Ada.Unchecked_Conversion
     (rflx_unit_provider, Internal_Unit_Provider_Access);

   function Convert is new Ada.Unchecked_Conversion
     (chars_ptr, System.Address);



end Librflxlang.Implementation.C;
