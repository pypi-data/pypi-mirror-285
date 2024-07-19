








#ifndef LIBRFLXLANG
#define LIBRFLXLANG

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * This type represents a context for all source analysis. This is the first
 * type you need to create to use librflxlang. It will contain the results of
 * all analysis, and is the main holder for all the data.
 *
 * You can create several analysis contexts if you need to, which enables you,
 * for example to:
 *
 * * analyze several different projects at the same time;
 *
 * * analyze different parts of the same projects in parallel.
 *
 * In the current design, contexts always keep all of their analysis units
 * allocated. If you need to get this memory released, the only option at your
 * disposal is to destroy your analysis context instance.
 *
 * This structure is partially opaque: some fields are exposed to allow direct
 * access, for performance concerns.
 */
typedef struct
{
   uint64_t serial_number;
} *rflx_analysis_context;

/*
 * This type represents the analysis of a single file.
 *
 * This type has strong-reference semantics and is ref-counted. Furthermore, a
 * reference to a unit contains an implicit reference to the context that owns
 * it. This means that keeping a reference to a unit will keep the context and
 * all the unit it contains allocated.
 *
 * This structure is partially opaque: some fields are exposed to allow direct
 * access, for performance concerns.
 */
typedef struct
{
   uint64_t version_number;
} *rflx_analysis_unit;

/*
 * Data type for all nodes. Nodes are assembled to make up a tree.  See the
 * node primitives below to inspect such trees.
 *
 * Unlike for contexts and units, this type has weak-reference semantics:
 * keeping a reference to a node has no effect on the decision to keep the unit
 * that it owns allocated. This means that once all references to the context
 * and units related to a node are dropped, the context and its units are
 * deallocated and the node becomes a stale reference: most operations on it
 * will raise a ``Stale_Reference_Error``.
 *
 * Note that since reparsing an analysis unit deallocates all the nodes it
 * contains, this operation makes all reference to these nodes stale as well.
 */
typedef struct rflx_base_node__struct *rflx_base_node;

/*
 * Kind of AST nodes in parse trees.
 */
typedef enum {
    

        /* r_f_l_x_node (abstract)  */
        /*
         * Root node class for the RecordFlux language.
         */
    

        /* abstract_i_d (abstract)  */
        /*
         * Base class for identifiers.
         */
    

        /*
         * Qualified identifiers which may optionally have a package part (e.g.
         * "Pkg::Foo", "Foo").
         */
        rflx_i_d = 1,
    

        /*
         * Simple, unqualified identifiers, i.e. identifiers without a package
         * part (e.g. "Foo").
         */
        rflx_unqualified_i_d = 2,
    

        /*

         */
        rflx_aspect = 3,
    

        /* attr (abstract)  */
        /*
         * Attribute kind.
         */
    

        /*

         */
        rflx_attr_first = 4,
    

        /*

         */
        rflx_attr_has_data = 5,
    

        /*

         */
        rflx_attr_head = 6,
    

        /*

         */
        rflx_attr_last = 7,
    

        /*

         */
        rflx_attr_opaque = 8,
    

        /*

         */
        rflx_attr_present = 9,
    

        /*

         */
        rflx_attr_size = 10,
    

        /*

         */
        rflx_attr_valid = 11,
    

        /*

         */
        rflx_attr_valid_checksum = 12,
    

        /* attr_stmt (abstract)  */
        /*
         * Attribute statement kind.
         */
    

        /*

         */
        rflx_attr_stmt_append = 13,
    

        /*

         */
        rflx_attr_stmt_extend = 14,
    

        /*

         */
        rflx_attr_stmt_read = 15,
    

        /*

         */
        rflx_attr_stmt_write = 16,
    

        /* base_aggregate (abstract)  */
        /*
         * Base class for message aggregates.
         */
    

        /*

         */
        rflx_message_aggregate_associations = 17,
    

        /*

         */
        rflx_null_message_aggregate = 18,
    

        /* base_checksum_val (abstract)  */
        /*
         * Base class for checksum values.
         */
    

        /*
         * Single checksum value.
         */
        rflx_checksum_val = 19,
    

        /*
         * Checksum value range.
         */
        rflx_checksum_value_range = 20,
    

        /* byte_order_type (abstract)  */
        /*

         */
    

        /*

         */
        rflx_byte_order_type_highorderfirst = 21,
    

        /*

         */
        rflx_byte_order_type_loworderfirst = 22,
    

        /* channel_attribute (abstract)  */
        /*
         * Base class for channel attributes.
         */
    

        /*
         * Channel attribute (channel can be read).
         */
        rflx_readable = 23,
    

        /*
         * Channel attribute (channel can be written).
         */
        rflx_writable = 24,
    

        /*
         * Association between checksum field and list of covered fields.
         */
        rflx_checksum_assoc = 25,
    

        /* declaration (abstract)  */
        /*
         * Base class for declarations (types, refinements, sessions).
         */
    

        /*
         * Refinement declaration (for Message use (Field => Inner_Type)).
         */
        rflx_refinement_decl = 26,
    

        /*

         */
        rflx_session_decl = 27,
    

        /*
         * Type declaration (type Foo is ...).
         */
        rflx_type_decl = 28,
    

        /*
         * String description of an entity.
         */
        rflx_description = 29,
    

        /*
         * Element/value association.
         */
        rflx_element_value_assoc = 30,
    

        /* expr (abstract)  */
        /*
         * Base class for expressions.
         */
    

        /*

         */
        rflx_attribute = 31,
    

        /*
         * Binary operation.
         */
        rflx_bin_op = 32,
    

        /*

         */
        rflx_binding = 33,
    

        /*

         */
        rflx_call = 34,
    

        /*

         */
        rflx_case_expression = 35,
    

        /*

         */
        rflx_choice = 36,
    

        /*

         */
        rflx_comprehension = 37,
    

        /*
         * Import statement (with Package).
         */
        rflx_context_item = 38,
    

        /*

         */
        rflx_conversion = 39,
    

        /*

         */
        rflx_message_aggregate = 40,
    

        /*

         */
        rflx_negation = 41,
    

        /*

         */
        rflx_numeric_literal = 42,
    

        /*
         * Parenthesized expression.
         */
        rflx_paren_expression = 43,
    

        /*

         */
        rflx_quantified_expression = 44,
    

        /*

         */
        rflx_select_node = 45,
    

        /* sequence_literal (abstract)  */
        /*
         * Base class for sequence literals (strings, sequence aggregates).
         */
    

        /*
         * Concatenation of aggregates or string literals.
         */
        rflx_concatenation = 46,
    

        /*
         * List of literal sequence values.
         */
        rflx_sequence_aggregate = 47,
    

        /*
         * Double-quoted string literal.
         */
        rflx_string_literal = 48,
    

        /*

         */
        rflx_variable = 49,
    

        /* formal_decl (abstract)  */
        /*
         * Base class for generic formal session declarations.
         */
    

        /*

         */
        rflx_formal_channel_decl = 50,
    

        /*

         */
        rflx_formal_function_decl = 51,
    

        /* local_decl (abstract)  */
        /*
         * Base class for session or state local declarations.
         */
    

        /*
         * Session renaming declaration.
         */
        rflx_renaming_decl = 52,
    

        /*
         * Session variable declaration.
         */
        rflx_variable_decl = 53,
    

        /*

         */
        rflx_message_aggregate_association = 54,
    

        /* message_aspect (abstract)  */
        /*
         * Base class for message aspects.
         */
    

        /*

         */
        rflx_byte_order_aspect = 55,
    

        /*

         */
        rflx_checksum_aspect = 56,
    

        /*

         */
        rflx_message_field = 57,
    

        /*

         */
        rflx_message_fields = 58,
    

        /*

         */
        rflx_null_message_field = 59,
    

        /* op (abstract)  */
        /*
         * Operators for binary expressions.
         */
    

        /*

         */
        rflx_op_add = 60,
    

        /*

         */
        rflx_op_and = 61,
    

        /*

         */
        rflx_op_div = 62,
    

        /*

         */
        rflx_op_eq = 63,
    

        /*

         */
        rflx_op_ge = 64,
    

        /*

         */
        rflx_op_gt = 65,
    

        /*

         */
        rflx_op_in = 66,
    

        /*

         */
        rflx_op_le = 67,
    

        /*

         */
        rflx_op_lt = 68,
    

        /*

         */
        rflx_op_mod = 69,
    

        /*

         */
        rflx_op_mul = 70,
    

        /*

         */
        rflx_op_neq = 71,
    

        /*

         */
        rflx_op_notin = 72,
    

        /*

         */
        rflx_op_or = 73,
    

        /*

         */
        rflx_op_pow = 74,
    

        /*

         */
        rflx_op_sub = 75,
    

        /*

         */
        rflx_package_node = 76,
    

        /*

         */
        rflx_parameter = 77,
    

        /*

         */
        rflx_parameters = 78,
    

        /* quantifier (abstract)  */
        /*
         * Quantifier kind.
         */
    

        /*

         */
        rflx_quantifier_all = 79,
    

        /*

         */
        rflx_quantifier_some = 80,
    

        /* r_f_l_x_node_base_list (abstract)  */
        /*

         */
    

        /*
         * List of Aspect.
         */
        rflx_aspect_list = 81,
    

        /*
         * List of BaseChecksumVal.
         */
        rflx_base_checksum_val_list = 82,
    

        /*
         * List of ChannelAttribute.
         */
        rflx_channel_attribute_list = 83,
    

        /*
         * List of ChecksumAssoc.
         */
        rflx_checksum_assoc_list = 84,
    

        /*
         * List of Choice.
         */
        rflx_choice_list = 85,
    

        /*
         * List of ConditionalTransition.
         */
        rflx_conditional_transition_list = 86,
    

        /*
         * List of ContextItem.
         */
        rflx_context_item_list = 87,
    

        /*
         * List of Declaration.
         */
        rflx_declaration_list = 88,
    

        /*
         * List of ElementValueAssoc.
         */
        rflx_element_value_assoc_list = 89,
    

        /*
         * List of Expr.
         *
         * This list node can contain one of the following nodes:
         * ``rflx_attribute``, ``rflx_bin_op``, ``rflx_binding``,
         * ``rflx_call``, ``rflx_case_expression``, ``rflx_comprehension``,
         * ``rflx_conversion``, ``rflx_message_aggregate``, ``rflx_negation``,
         * ``rflx_numeric_literal``, ``rflx_paren_expression``,
         * ``rflx_quantified_expression``, ``rflx_select_node``,
         * ``rflx_sequence_literal``, ``rflx_variable``
         */
        rflx_expr_list = 90,
    

        /*
         * List of FormalDecl.
         */
        rflx_formal_decl_list = 91,
    

        /*
         * List of LocalDecl.
         */
        rflx_local_decl_list = 92,
    

        /*
         * List of MessageAggregateAssociation.
         */
        rflx_message_aggregate_association_list = 93,
    

        /*
         * List of MessageAspect.
         */
        rflx_message_aspect_list = 94,
    

        /*
         * List of MessageField.
         */
        rflx_message_field_list = 95,
    

        /*
         * List of NumericLiteral.
         */
        rflx_numeric_literal_list = 96,
    

        /*
         * List of Parameter.
         */
        rflx_parameter_list = 97,
    

        /*
         * List of RFLXNode.
         *
         * This list node can contain one of the following nodes: ``rflx_i_d``,
         * ``rflx_numeric_literal``
         */
        rflx_r_f_l_x_node_list = 98,
    

        /*
         * List of State.
         */
        rflx_state_list = 99,
    

        /*
         * List of Statement.
         */
        rflx_statement_list = 100,
    

        /*
         * List of TermAssoc.
         */
        rflx_term_assoc_list = 101,
    

        /*
         * List of Then.
         */
        rflx_then_node_list = 102,
    

        /*
         * List of TypeArgument.
         */
        rflx_type_argument_list = 103,
    

        /*
         * List of UnqualifiedID.
         */
        rflx_unqualified_i_d_list = 104,
    

        /*
         * RecordFlux specification.
         */
        rflx_specification = 105,
    

        /*
         * Session state.
         */
        rflx_state = 106,
    

        /*
         * Body of a session state.
         */
        rflx_state_body = 107,
    

        /* statement (abstract)  */
        /*
         * Base class for statements.
         */
    

        /*
         * Assignment of expression to unqualified identifier.
         */
        rflx_assignment = 108,
    

        /*
         * Attribute statement.
         */
        rflx_attribute_statement = 109,
    

        /*
         * Assignment of expression to message field.
         */
        rflx_message_field_assignment = 110,
    

        /*
         * Reset statement.
         */
        rflx_reset = 111,
    

        /*

         */
        rflx_term_assoc = 112,
    

        /*
         * Link to field.
         */
        rflx_then_node = 113,
    

        /*
         * Unconditional session state transition.
         */
        rflx_transition = 114,
    

        /*
         * Conditional session state transition.
         */
        rflx_conditional_transition = 115,
    

        /*

         */
        rflx_type_argument = 116,
    

        /* type_def (abstract)  */
        /*
         * Base class for type definitions (integers, messages, type
         * derivations, sequences, enums).
         */
    

        /* abstract_message_type_def (abstract)  */
        /*
         * Base class for message type definitions.
         */
    

        /*

         */
        rflx_message_type_def = 117,
    

        /*

         */
        rflx_null_message_type_def = 118,
    

        /* enumeration_def (abstract)  */
        /*
         * Base class for enumeration definitions.
         */
    

        /*

         */
        rflx_named_enumeration_def = 119,
    

        /*

         */
        rflx_positional_enumeration_def = 120,
    

        /*

         */
        rflx_enumeration_type_def = 121,
    

        /* integer_type_def (abstract)  */
        /*
         * Base class for all integer type definitions.
         */
    

        /*

         */
        rflx_modular_type_def = 122,
    

        /*

         */
        rflx_range_type_def = 123,
    

        /*

         */
        rflx_sequence_type_def = 124,
    

        /*

         */
        rflx_type_derivation_def = 125,
} rflx_node_kind_enum;

/*
 * Reference to a symbol. Symbols are owned by analysis contexts, so they must
 * not outlive them. This type exists only in the C API, and roughly wraps the
 * corresponding Ada type (an array fat pointer).
 */
typedef struct {
   void *data;
   void *bounds;
} rflx_symbol_type;

/*
 * Type to contain Unicode text data.
 */
typedef struct {
   int length;
   int ref_count;
   uint32_t content[1];
} *rflx_string_type;

/*
 * Data type for env rebindings. For internal use only.
 */
typedef struct rflx_env_rebindings_type__struct *rflx_env_rebindings_type;

typedef uint8_t rflx_bool;

/* Helper data structures for source location handling.  */

/*
 * Location in a source file. Line and column numbers are one-based.
 */
typedef struct {
    uint32_t line;
    uint16_t column;
} rflx_source_location;

/*
 * Location of a span of text in a source file.
 */
typedef struct {
    rflx_source_location start;
    rflx_source_location end;
} rflx_source_location_range;


/*
 * String encoded in UTF-32 (native endianness).
 */
typedef struct {
   /*
 * Address for the content of the string.
 */
    uint32_t *chars;
   /*
 * Size of the string (in characters).
 */
    size_t length;

    int is_allocated;
} rflx_text;

/*
 * Arbitrarily large integer.
 */
typedef struct rflx_big_integer__struct *rflx_big_integer;

/*
 * Kind for this token.
 */
typedef enum {
   
      
      RFLX_TERMINATION = 0
      ,
      RFLX_LEXING_FAILURE = 1
      ,
      RFLX_UNQUALIFIED_IDENTIFIER = 2
      ,
      RFLX_PACKAGE = 3
      ,
      RFLX_IS = 4
      ,
      RFLX_IF = 5
      ,
      RFLX_END = 6
      ,
      RFLX_NULL = 7
      ,
      RFLX_TYPE = 8
      ,
      RFLX_RANGE = 9
      ,
      RFLX_WITH = 10
      ,
      RFLX_MOD = 11
      ,
      RFLX_MESSAGE = 12
      ,
      RFLX_THEN = 13
      ,
      RFLX_SEQUENCE = 14
      ,
      RFLX_OF = 15
      ,
      RFLX_IN = 16
      ,
      RFLX_NOT = 17
      ,
      RFLX_NEW = 18
      ,
      RFLX_FOR = 19
      ,
      RFLX_WHEN = 20
      ,
      RFLX_WHERE = 21
      ,
      RFLX_USE = 22
      ,
      RFLX_ALL = 23
      ,
      RFLX_SOME = 24
      ,
      RFLX_GENERIC = 25
      ,
      RFLX_SESSION = 26
      ,
      RFLX_BEGIN = 27
      ,
      RFLX_RETURN = 28
      ,
      RFLX_FUNCTION = 29
      ,
      RFLX_STATE = 30
      ,
      RFLX_TRANSITION = 31
      ,
      RFLX_GOTO = 32
      ,
      RFLX_EXCEPTION = 33
      ,
      RFLX_RENAMES = 34
      ,
      RFLX_CHANNEL = 35
      ,
      RFLX_READABLE = 36
      ,
      RFLX_WRITABLE = 37
      ,
      RFLX_DESC = 38
      ,
      RFLX_APPEND = 39
      ,
      RFLX_EXTEND = 40
      ,
      RFLX_READ = 41
      ,
      RFLX_WRITE = 42
      ,
      RFLX_RESET = 43
      ,
      RFLX_HIGH_ORDER_FIRST = 44
      ,
      RFLX_LOW_ORDER_FIRST = 45
      ,
      RFLX_CASE = 46
      ,
      RFLX_FIRST = 47
      ,
      RFLX_SIZE = 48
      ,
      RFLX_LAST = 49
      ,
      RFLX_BYTE_ORDER = 50
      ,
      RFLX_CHECKSUM = 51
      ,
      RFLX_VALID_CHECKSUM = 52
      ,
      RFLX_HAS_DATA = 53
      ,
      RFLX_HEAD = 54
      ,
      RFLX_OPAQUE = 55
      ,
      RFLX_PRESENT = 56
      ,
      RFLX_VALID = 57
      ,
      RFLX_DOT = 58
      ,
      RFLX_COMMA = 59
      ,
      RFLX_DOUBLE_DOT = 60
      ,
      RFLX_TICK = 61
      ,
      RFLX_HASH = 62
      ,
      RFLX_MINUS = 63
      ,
      RFLX_ARROW = 64
      ,
      RFLX_L_PAR = 65
      ,
      RFLX_R_PAR = 66
      ,
      RFLX_L_BRACK = 67
      ,
      RFLX_R_BRACK = 68
      ,
      RFLX_EXP = 69
      ,
      RFLX_MUL = 70
      ,
      RFLX_DIV = 71
      ,
      RFLX_ADD = 72
      ,
      RFLX_SUB = 73
      ,
      RFLX_EQ = 74
      ,
      RFLX_NEQ = 75
      ,
      RFLX_LEQ = 76
      ,
      RFLX_LT = 77
      ,
      RFLX_LE = 78
      ,
      RFLX_GT = 79
      ,
      RFLX_GE = 80
      ,
      RFLX_AND = 81
      ,
      RFLX_OR = 82
      ,
      RFLX_AMPERSAND = 83
      ,
      RFLX_SEMICOLON = 84
      ,
      RFLX_DOUBLE_COLON = 85
      ,
      RFLX_ASSIGNMENT = 86
      ,
      RFLX_COLON = 87
      ,
      RFLX_PIPE = 88
      ,
      RFLX_COMMENT = 89
      ,
      RFLX_NUMERAL = 90
      ,
      RFLX_STRING_LITERAL = 91
} rflx_token_kind;

typedef struct
{
   uint64_t version;
} *rflx_token_data_handler;

/*
 * Reference to a token in an analysis unit.
 */
typedef struct {
    /* Private data associated to this token, including stale reference
       checking data, or NULL if this designates no token.  */
    rflx_analysis_context context;
    rflx_token_data_handler token_data;

    /* Internal identifiers for this token.  */
    int token_index, trivia_index;
} rflx_token;


/*
 * Diagnostic for an analysis unit: cannot open the source file, parsing error,
 * ...
 */
typedef struct {
    rflx_source_location_range sloc_range;
    rflx_text message;
} rflx_diagnostic;

   typedef enum {
      RFLX_ANALYSIS_UNIT_KIND_UNIT_SPECIFICATION, RFLX_ANALYSIS_UNIT_KIND_UNIT_BODY
   } rflx_analysis_unit_kind;
   /*
    * Specify a kind of analysis unit. Specification units provide an interface
    * to the outer world while body units provide an implementation for the
    * corresponding interface.
    */
   typedef enum {
      RFLX_LOOKUP_KIND_RECURSIVE, RFLX_LOOKUP_KIND_FLAT, RFLX_LOOKUP_KIND_MINIMAL
   } rflx_lookup_kind;
   /*

    */
   typedef enum {
      RFLX_DESIGNATED_ENV_KIND_NONE, RFLX_DESIGNATED_ENV_KIND_CURRENT_ENV, RFLX_DESIGNATED_ENV_KIND_NAMED_ENV, RFLX_DESIGNATED_ENV_KIND_DIRECT_ENV
   } rflx_designated_env_kind;
   /*
    * Discriminant for DesignatedEnv structures.
    */
   typedef enum {
      RFLX_GRAMMAR_RULE_MAIN_RULE_RULE, RFLX_GRAMMAR_RULE_UNQUALIFIED_IDENTIFIER_RULE, RFLX_GRAMMAR_RULE_QUALIFIED_IDENTIFIER_RULE, RFLX_GRAMMAR_RULE_NUMERIC_LITERAL_RULE, RFLX_GRAMMAR_RULE_VARIABLE_RULE, RFLX_GRAMMAR_RULE_SEQUENCE_AGGREGATE_RULE, RFLX_GRAMMAR_RULE_STRING_LITERAL_RULE, RFLX_GRAMMAR_RULE_CONCATENATION_RULE, RFLX_GRAMMAR_RULE_PRIMARY_RULE, RFLX_GRAMMAR_RULE_PAREN_EXPRESSION_RULE, RFLX_GRAMMAR_RULE_SUFFIX_RULE, RFLX_GRAMMAR_RULE_FACTOR_RULE, RFLX_GRAMMAR_RULE_TERM_RULE, RFLX_GRAMMAR_RULE_UNOP_TERM_RULE, RFLX_GRAMMAR_RULE_SIMPLE_EXPR_RULE, RFLX_GRAMMAR_RULE_RELATION_RULE, RFLX_GRAMMAR_RULE_EXPRESSION_RULE, RFLX_GRAMMAR_RULE_QUANTIFIED_EXPRESSION_RULE, RFLX_GRAMMAR_RULE_COMPREHENSION_RULE, RFLX_GRAMMAR_RULE_CALL_RULE, RFLX_GRAMMAR_RULE_CONVERSION_RULE, RFLX_GRAMMAR_RULE_NULL_MESSAGE_AGGREGATE_RULE, RFLX_GRAMMAR_RULE_MESSAGE_AGGREGATE_ASSOCIATION_RULE, RFLX_GRAMMAR_RULE_MESSAGE_AGGREGATE_ASSOCIATION_LIST_RULE, RFLX_GRAMMAR_RULE_MESSAGE_AGGREGATE_RULE, RFLX_GRAMMAR_RULE_EXTENDED_PRIMARY_RULE, RFLX_GRAMMAR_RULE_EXTENDED_PAREN_EXPRESSION_RULE, RFLX_GRAMMAR_RULE_EXTENDED_CHOICE_LIST_RULE, RFLX_GRAMMAR_RULE_EXTENDED_CHOICES_RULE, RFLX_GRAMMAR_RULE_EXTENDED_CASE_EXPRESSION_RULE, RFLX_GRAMMAR_RULE_EXTENDED_SUFFIX_RULE, RFLX_GRAMMAR_RULE_EXTENDED_FACTOR_RULE, RFLX_GRAMMAR_RULE_EXTENDED_TERM_RULE, RFLX_GRAMMAR_RULE_EXTENDED_UNOP_TERM_RULE, RFLX_GRAMMAR_RULE_EXTENDED_SIMPLE_EXPR_RULE, RFLX_GRAMMAR_RULE_EXTENDED_RELATION_RULE, RFLX_GRAMMAR_RULE_EXTENDED_EXPRESSION_RULE, RFLX_GRAMMAR_RULE_ASPECT_RULE, RFLX_GRAMMAR_RULE_RANGE_TYPE_DEFINITION_RULE, RFLX_GRAMMAR_RULE_MODULAR_TYPE_DEFINITION_RULE, RFLX_GRAMMAR_RULE_INTEGER_TYPE_DEFINITION_RULE, RFLX_GRAMMAR_RULE_IF_CONDITION_RULE, RFLX_GRAMMAR_RULE_EXTENDED_IF_CONDITION_RULE, RFLX_GRAMMAR_RULE_THEN_RULE, RFLX_GRAMMAR_RULE_TYPE_ARGUMENT_RULE, RFLX_GRAMMAR_RULE_NULL_MESSAGE_FIELD_RULE, RFLX_GRAMMAR_RULE_MESSAGE_FIELD_RULE, RFLX_GRAMMAR_RULE_MESSAGE_FIELD_LIST_RULE, RFLX_GRAMMAR_RULE_VALUE_RANGE_RULE, RFLX_GRAMMAR_RULE_CHECKSUM_ASSOCIATION_RULE, RFLX_GRAMMAR_RULE_CHECKSUM_ASPECT_RULE, RFLX_GRAMMAR_RULE_BYTE_ORDER_ASPECT_RULE, RFLX_GRAMMAR_RULE_MESSAGE_ASPECT_LIST_RULE, RFLX_GRAMMAR_RULE_MESSAGE_TYPE_DEFINITION_RULE, RFLX_GRAMMAR_RULE_POSITIONAL_ENUMERATION_RULE, RFLX_GRAMMAR_RULE_ELEMENT_VALUE_ASSOCIATION_RULE, RFLX_GRAMMAR_RULE_NAMED_ENUMERATION_RULE, RFLX_GRAMMAR_RULE_ENUMERATION_ASPECTS_RULE, RFLX_GRAMMAR_RULE_ENUMERATION_TYPE_DEFINITION_RULE, RFLX_GRAMMAR_RULE_TYPE_DERIVATION_DEFINITION_RULE, RFLX_GRAMMAR_RULE_SEQUENCE_TYPE_DEFINITION_RULE, RFLX_GRAMMAR_RULE_TYPE_DECLARATION_RULE, RFLX_GRAMMAR_RULE_TYPE_REFINEMENT_RULE, RFLX_GRAMMAR_RULE_PARAMETER_RULE, RFLX_GRAMMAR_RULE_PARAMETER_LIST_RULE, RFLX_GRAMMAR_RULE_FORMAL_FUNCTION_DECLARATION_RULE, RFLX_GRAMMAR_RULE_CHANNEL_DECLARATION_RULE, RFLX_GRAMMAR_RULE_SESSION_PARAMETER_RULE, RFLX_GRAMMAR_RULE_RENAMING_DECLARATION_RULE, RFLX_GRAMMAR_RULE_VARIABLE_DECLARATION_RULE, RFLX_GRAMMAR_RULE_DECLARATION_RULE, RFLX_GRAMMAR_RULE_DESCRIPTION_ASPECT_RULE, RFLX_GRAMMAR_RULE_ASSIGNMENT_STATEMENT_RULE, RFLX_GRAMMAR_RULE_MESSAGE_FIELD_ASSIGNMENT_STATEMENT_RULE, RFLX_GRAMMAR_RULE_LIST_ATTRIBUTE_RULE, RFLX_GRAMMAR_RULE_RESET_RULE, RFLX_GRAMMAR_RULE_ATTRIBUTE_STATEMENT_RULE, RFLX_GRAMMAR_RULE_ACTION_RULE, RFLX_GRAMMAR_RULE_CONDITIONAL_TRANSITION_RULE, RFLX_GRAMMAR_RULE_TRANSITION_RULE, RFLX_GRAMMAR_RULE_STATE_BODY_RULE, RFLX_GRAMMAR_RULE_STATE_RULE, RFLX_GRAMMAR_RULE_SESSION_DECLARATION_RULE, RFLX_GRAMMAR_RULE_BASIC_DECLARATION_RULE, RFLX_GRAMMAR_RULE_BASIC_DECLARATIONS_RULE, RFLX_GRAMMAR_RULE_PACKAGE_DECLARATION_RULE, RFLX_GRAMMAR_RULE_CONTEXT_ITEM_RULE, RFLX_GRAMMAR_RULE_CONTEXT_CLAUSE_RULE, RFLX_GRAMMAR_RULE_SPECIFICATION_RULE
   } rflx_grammar_rule;
   /*
    * Gramar rule to use for parsing.
    */

#define rflx_default_grammar_rule RFLX_GRAMMAR_RULE_MAIN_RULE_RULE

/*
 * Enumerated type describing all possible exceptions that need to be handled
 * in the C bindings.
 */
typedef enum {
      EXCEPTION_FILE_READ_ERROR,
      EXCEPTION_BAD_TYPE_ERROR,
      EXCEPTION_OUT_OF_BOUNDS_ERROR,
      EXCEPTION_INVALID_INPUT,
      EXCEPTION_INVALID_SYMBOL_ERROR,
      EXCEPTION_INVALID_UNIT_NAME_ERROR,
      EXCEPTION_NATIVE_EXCEPTION,
      EXCEPTION_PRECONDITION_FAILURE,
      EXCEPTION_PROPERTY_ERROR,
      EXCEPTION_TEMPLATE_ARGS_ERROR,
      EXCEPTION_TEMPLATE_FORMAT_ERROR,
      EXCEPTION_TEMPLATE_INSTANTIATION_ERROR,
      EXCEPTION_STALE_REFERENCE_ERROR,
      EXCEPTION_SYNTAX_ERROR,
      EXCEPTION_UNKNOWN_CHARSET,
      EXCEPTION_MALFORMED_TREE_ERROR,
} rflx_exception_kind;

/*
 * Holder for native exceptions-related information.  Memory management for
 * this and all the fields is handled by the library: one just has to make sure
 * not to keep references to it.
 *
 * .. TODO: For the moment, this structure contains already formatted
 *    information, but depending on possible future Ada runtime improvements,
 *    this might change.
 */
typedef struct {
   /*
 * The kind of this exception.
 */
   rflx_exception_kind kind;

   /*
 * Message and context information associated with this exception.
 */
   const char *information;
} rflx_exception;

/*
 * Array types incomplete declarations
 */

        

typedef struct rflx_node_array_record *rflx_node_array;


/*
 * Iterator types incomplete declarations
 */

/*
 * An iterator provides a mean to retrieve values one-at-a-time.
 *
 * Currently, each iterator is bound to the analysis context used to create it.
 * Iterators are invalidated as soon as any unit of that analysis is reparsed.
 * Due to the nature of iterators (lazy computations), this invalidation is
 * necessary to avoid use of inconsistent state, such as an iterator trying to
 * use analysis context data that is stale.
 */



typedef void* rflx_node_iterator;



/*
 * Struct types declarations
 */

        



    typedef struct {char dummy;} rflx_internal_metadata;



        



    typedef struct {
            rflx_internal_metadata md;
            rflx_env_rebindings_type rebindings;
            rflx_bool from_rebound;
    } rflx_internal_entity_info;



        



    typedef struct {
            rflx_base_node node;
            rflx_internal_entity_info info;
    } rflx_node;




/*
 * Types for event handler
 */

/*
 * Interface to handle events sent by the analysis context.
 */
typedef struct rflx_event_handler__struct *rflx_event_handler;

/*
 * Callback that will be called when a unit is requested from the context
 * ``Context``.
 *
 * ``Name`` is the name of the requested unit.
 *
 * ``From`` is the unit from which the unit was requested.
 *
 * ``Found`` indicates whether the requested unit was found or not.
 *
 * ``Is_Not_Found_Error`` indicates whether the fact that the unit was not
 * found is an error or not.
 *
 * .. warning:: The interface of this callback is probably subject to change,
 *    so should be treated as experimental.
 */
typedef void (*rflx_event_handler_unit_requested_callback)(
   void *data,
   rflx_analysis_context context,
   rflx_text *name,
   rflx_analysis_unit from,
   rflx_bool found,
   rflx_bool is_not_found_error
);

/*
 * Callback type for functions that are called when destroying an event
 * handler.
 */
typedef void (*rflx_event_handler_destroy_callback)(void *data);

/*
 * Callback that will be called when any unit is parsed from the context
 * ``Context``.
 *
 * ``Unit`` is the resulting unit.
 *
 * ``Reparsed`` indicates whether the unit was reparsed, or whether it was the
 * first parse.
 */
typedef void (*rflx_event_handler_unit_parsed_callback)(
   void *data,
   rflx_analysis_context context,
   rflx_analysis_unit unit,
   rflx_bool reparsed
);

/*
 * Types for file readers
 */

/*
 * Interface to override how source files are fetched and decoded.
 */
typedef struct rflx_file_reader__struct *rflx_file_reader;

/*
 * Callback type for functions that are called when destroying a file reader.
 */
typedef void (*rflx_file_reader_destroy_callback)(void *data);

/*
 * Callback type for functions that are called to fetch the decoded source
 * buffer for a requested filename.
 */
typedef void (*rflx_file_reader_read_callback)(
   void *data,
   const char *filename,
   const char *charset,
   int read_bom,
   rflx_text *buffer,
   rflx_diagnostic *diagnostic
);

/*
 * Types for unit providers
 */

/*
 * Interface to fetch analysis units from a name and a unit kind.
 *
 * The unit provider mechanism provides an abstraction which assumes that to
 * any couple (unit name, unit kind) we can associate at most one source file.
 * This means that several couples can be associated to the same source file,
 * but on the other hand, only one one source file can be associated to a
 * couple.
 *
 * This is used to make the semantic analysis able to switch from one analysis
 * units to another.
 *
 * See the documentation of each unit provider for the exact semantics of the
 * unit name/kind information.
 */
typedef struct rflx_unit_provider__struct *rflx_unit_provider;

/*
 * Types for introspection
 */

/* References to struct/node members.  */
typedef enum {
      rflx_member_ref_i_d_f_package
        = 1,
      rflx_member_ref_i_d_f_name
        = 2,
      rflx_member_ref_aspect_f_identifier
        = 3,
      rflx_member_ref_aspect_f_value
        = 4,
      rflx_member_ref_message_aggregate_associations_f_associations
        = 5,
      rflx_member_ref_checksum_val_f_data
        = 6,
      rflx_member_ref_checksum_value_range_f_first
        = 7,
      rflx_member_ref_checksum_value_range_f_last
        = 8,
      rflx_member_ref_checksum_assoc_f_identifier
        = 9,
      rflx_member_ref_checksum_assoc_f_covered_fields
        = 10,
      rflx_member_ref_refinement_decl_f_pdu
        = 11,
      rflx_member_ref_refinement_decl_f_field
        = 12,
      rflx_member_ref_refinement_decl_f_sdu
        = 13,
      rflx_member_ref_refinement_decl_f_condition
        = 14,
      rflx_member_ref_session_decl_f_parameters
        = 15,
      rflx_member_ref_session_decl_f_identifier
        = 16,
      rflx_member_ref_session_decl_f_declarations
        = 17,
      rflx_member_ref_session_decl_f_states
        = 18,
      rflx_member_ref_session_decl_f_end_identifier
        = 19,
      rflx_member_ref_type_decl_f_identifier
        = 20,
      rflx_member_ref_type_decl_f_parameters
        = 21,
      rflx_member_ref_type_decl_f_definition
        = 22,
      rflx_member_ref_description_f_content
        = 23,
      rflx_member_ref_element_value_assoc_f_identifier
        = 24,
      rflx_member_ref_element_value_assoc_f_literal
        = 25,
      rflx_member_ref_attribute_f_expression
        = 26,
      rflx_member_ref_attribute_f_kind
        = 27,
      rflx_member_ref_bin_op_f_left
        = 28,
      rflx_member_ref_bin_op_f_op
        = 29,
      rflx_member_ref_bin_op_f_right
        = 30,
      rflx_member_ref_binding_f_expression
        = 31,
      rflx_member_ref_binding_f_bindings
        = 32,
      rflx_member_ref_call_f_identifier
        = 33,
      rflx_member_ref_call_f_arguments
        = 34,
      rflx_member_ref_case_expression_f_expression
        = 35,
      rflx_member_ref_case_expression_f_choices
        = 36,
      rflx_member_ref_choice_f_selectors
        = 37,
      rflx_member_ref_choice_f_expression
        = 38,
      rflx_member_ref_comprehension_f_iterator
        = 39,
      rflx_member_ref_comprehension_f_sequence
        = 40,
      rflx_member_ref_comprehension_f_condition
        = 41,
      rflx_member_ref_comprehension_f_selector
        = 42,
      rflx_member_ref_context_item_f_item
        = 43,
      rflx_member_ref_conversion_f_target_identifier
        = 44,
      rflx_member_ref_conversion_f_argument
        = 45,
      rflx_member_ref_message_aggregate_f_identifier
        = 46,
      rflx_member_ref_message_aggregate_f_values
        = 47,
      rflx_member_ref_negation_f_data
        = 48,
      rflx_member_ref_paren_expression_f_data
        = 49,
      rflx_member_ref_quantified_expression_f_operation
        = 50,
      rflx_member_ref_quantified_expression_f_parameter_identifier
        = 51,
      rflx_member_ref_quantified_expression_f_iterable
        = 52,
      rflx_member_ref_quantified_expression_f_predicate
        = 53,
      rflx_member_ref_select_node_f_expression
        = 54,
      rflx_member_ref_select_node_f_selector
        = 55,
      rflx_member_ref_concatenation_f_left
        = 56,
      rflx_member_ref_concatenation_f_right
        = 57,
      rflx_member_ref_sequence_aggregate_f_values
        = 58,
      rflx_member_ref_variable_f_identifier
        = 59,
      rflx_member_ref_formal_channel_decl_f_identifier
        = 60,
      rflx_member_ref_formal_channel_decl_f_parameters
        = 61,
      rflx_member_ref_formal_function_decl_f_identifier
        = 62,
      rflx_member_ref_formal_function_decl_f_parameters
        = 63,
      rflx_member_ref_formal_function_decl_f_return_type_identifier
        = 64,
      rflx_member_ref_renaming_decl_f_identifier
        = 65,
      rflx_member_ref_renaming_decl_f_type_identifier
        = 66,
      rflx_member_ref_renaming_decl_f_expression
        = 67,
      rflx_member_ref_variable_decl_f_identifier
        = 68,
      rflx_member_ref_variable_decl_f_type_identifier
        = 69,
      rflx_member_ref_variable_decl_f_initializer
        = 70,
      rflx_member_ref_message_aggregate_association_f_identifier
        = 71,
      rflx_member_ref_message_aggregate_association_f_expression
        = 72,
      rflx_member_ref_byte_order_aspect_f_byte_order
        = 73,
      rflx_member_ref_checksum_aspect_f_associations
        = 74,
      rflx_member_ref_message_field_f_identifier
        = 75,
      rflx_member_ref_message_field_f_type_identifier
        = 76,
      rflx_member_ref_message_field_f_type_arguments
        = 77,
      rflx_member_ref_message_field_f_aspects
        = 78,
      rflx_member_ref_message_field_f_condition
        = 79,
      rflx_member_ref_message_field_f_thens
        = 80,
      rflx_member_ref_message_fields_f_initial_field
        = 81,
      rflx_member_ref_message_fields_f_fields
        = 82,
      rflx_member_ref_null_message_field_f_thens
        = 83,
      rflx_member_ref_package_node_f_identifier
        = 84,
      rflx_member_ref_package_node_f_declarations
        = 85,
      rflx_member_ref_package_node_f_end_identifier
        = 86,
      rflx_member_ref_parameter_f_identifier
        = 87,
      rflx_member_ref_parameter_f_type_identifier
        = 88,
      rflx_member_ref_parameters_f_parameters
        = 89,
      rflx_member_ref_specification_f_context_clause
        = 90,
      rflx_member_ref_specification_f_package_declaration
        = 91,
      rflx_member_ref_state_f_identifier
        = 92,
      rflx_member_ref_state_f_description
        = 93,
      rflx_member_ref_state_f_body
        = 94,
      rflx_member_ref_state_body_f_declarations
        = 95,
      rflx_member_ref_state_body_f_actions
        = 96,
      rflx_member_ref_state_body_f_conditional_transitions
        = 97,
      rflx_member_ref_state_body_f_final_transition
        = 98,
      rflx_member_ref_state_body_f_exception_transition
        = 99,
      rflx_member_ref_state_body_f_end_identifier
        = 100,
      rflx_member_ref_assignment_f_identifier
        = 101,
      rflx_member_ref_assignment_f_expression
        = 102,
      rflx_member_ref_attribute_statement_f_identifier
        = 103,
      rflx_member_ref_attribute_statement_f_attr
        = 104,
      rflx_member_ref_attribute_statement_f_expression
        = 105,
      rflx_member_ref_message_field_assignment_f_message
        = 106,
      rflx_member_ref_message_field_assignment_f_field
        = 107,
      rflx_member_ref_message_field_assignment_f_expression
        = 108,
      rflx_member_ref_reset_f_identifier
        = 109,
      rflx_member_ref_reset_f_associations
        = 110,
      rflx_member_ref_term_assoc_f_identifier
        = 111,
      rflx_member_ref_term_assoc_f_expression
        = 112,
      rflx_member_ref_then_node_f_target
        = 113,
      rflx_member_ref_then_node_f_aspects
        = 114,
      rflx_member_ref_then_node_f_condition
        = 115,
      rflx_member_ref_transition_f_target
        = 116,
      rflx_member_ref_transition_f_description
        = 117,
      rflx_member_ref_conditional_transition_f_condition
        = 118,
      rflx_member_ref_type_argument_f_identifier
        = 119,
      rflx_member_ref_type_argument_f_expression
        = 120,
      rflx_member_ref_message_type_def_f_message_fields
        = 121,
      rflx_member_ref_message_type_def_f_aspects
        = 122,
      rflx_member_ref_named_enumeration_def_f_elements
        = 123,
      rflx_member_ref_positional_enumeration_def_f_elements
        = 124,
      rflx_member_ref_enumeration_type_def_f_elements
        = 125,
      rflx_member_ref_enumeration_type_def_f_aspects
        = 126,
      rflx_member_ref_modular_type_def_f_mod
        = 127,
      rflx_member_ref_range_type_def_f_first
        = 128,
      rflx_member_ref_range_type_def_f_last
        = 129,
      rflx_member_ref_range_type_def_f_size
        = 130,
      rflx_member_ref_sequence_type_def_f_element_type
        = 131,
      rflx_member_ref_type_derivation_def_f_base
        = 132,
      rflx_member_ref_parent
        = 133,
      rflx_member_ref_parents
        = 134,
      rflx_member_ref_children
        = 135,
      rflx_member_ref_token_start
        = 136,
      rflx_member_ref_token_end
        = 137,
      rflx_member_ref_child_index
        = 138,
      rflx_member_ref_previous_sibling
        = 139,
      rflx_member_ref_next_sibling
        = 140,
      rflx_member_ref_unit
        = 141,
      rflx_member_ref_is_ghost
        = 142,
      rflx_member_ref_full_sloc_image
        = 143,
} rflx_introspection_member_ref;

/*
 * Types for tree rewriting
 */

/*
 * Handle for an analysis context rewriting session
 */
typedef struct rflx_rewriting_handle__struct *rflx_rewriting_handle;

/*
 * Handle for the process of rewriting an analysis unit. Such handles are owned
 * by a Rewriting_Handle instance.
 */
typedef struct rflx_unit_rewriting_handle__struct *rflx_unit_rewriting_handle;

/*
 * Handle for the process of rewriting an AST node. Such handles are owned by a
 * Rewriting_Handle instance.
 */
typedef struct rflx_node_rewriting_handle__struct *rflx_node_rewriting_handle;

/*
 * Result of applying a rewriting session.
 *
 * On success, ``Success`` is true.
 *
 * On failure, ``Success`` is false, ``Unit`` is set to the unit on which
 * rewriting failed, and ``Diagnostics`` is set to related rewriting errors.
 */
typedef struct {
    int success;
    rflx_analysis_unit unit;
    int diagnostics_count;
    rflx_diagnostic *diagnostics;
} rflx_rewriting_apply_result;

/* All the functions below can potentially raise an exception, so
   rflx_get_last_exception must be checked after them even
   before trying to use the returned value.  */


/*
 * Array types declarations
 */

        



/*

 */
struct rflx_node_array_record {
   int n;
   int ref_count;
   rflx_node items[1];
};

/* Create a length-sized array.  */
extern rflx_node_array
rflx_node_array_create(int length);

/* Increment the ref-count for "a".  */
extern void
rflx_node_array_inc_ref(rflx_node_array a);

/* Decrement the ref-count for "a". This deallocates it if the ref-count drops
   to 0.  */
extern void
rflx_node_array_dec_ref(rflx_node_array a);



/*
 * Iterator types declarations
 */





/*
 * Set the next value from the iterator in the given element pointer. Return
 * ``1`` if successful, otherwise ``0``.
 *
 * This raises a ``Stale_Reference_Error`` exception if the iterator is
 * invalidated.
 */
extern int
rflx_node_iterator_next(rflx_node_iterator i, rflx_node* e);

/* Increment the ref-count for "i".  */
extern void
rflx_node_iterator_inc_ref(rflx_node_iterator i);

/* Decrement the ref-count for "i". This deallocates it if the ref-count drops
   to 0.  */
extern void
rflx_node_iterator_dec_ref(rflx_node_iterator i);




/*
 * Analysis primitives
 */

/*
 * Allocate a new analysis context.
 */
extern rflx_analysis_context
rflx_allocate_analysis_context (void);

/*
 * Initialize an analysis context. Must be called right after
 * ``Allocate_Context`` on its result.
 *
 * Having separate primitives for allocation/initialization allows library
 * bindings to have a context wrapper (created between the two calls) ready
 * when callbacks that happen during context initialization (for instance "unit
 * parsed" events).
 */
extern void
rflx_initialize_analysis_context(
   rflx_analysis_context context,
   const char *charset,
   rflx_file_reader file_reader,
   rflx_unit_provider unit_provider,
   rflx_event_handler event_handler,
   int with_trivia,
   int tab_stop
);

/*
 * Increase the reference count to an analysis context. Return the reference
 * for convenience.
 */
extern rflx_analysis_context
rflx_context_incref(rflx_analysis_context context);

/*
 * Decrease the reference count to an analysis context. Destruction happens
 * when the ref-count reaches 0.
 */
extern void
rflx_context_decref(rflx_analysis_context context);

/*
 * If the given string is a valid symbol, yield it as a symbol and return true.
 * Otherwise, return false.
 */
extern int
rflx_context_symbol(rflx_analysis_context context,
                                   rflx_text *text,
                                   rflx_symbol_type *symbol);

/*
 * Debug helper. Set whether ``Property_Error`` exceptions raised in
 * ``Populate_Lexical_Env`` should be discarded. They are by default.
 */
extern void
rflx_context_discard_errors_in_populate_lexical_env(
        rflx_analysis_context context,
        int discard);

/*
 * Create a new analysis unit for ``Filename`` or return the existing one if
 * any. If ``Reparse`` is true and the analysis unit already exists, reparse it
 * from ``Filename``.
 *
 * ``Rule`` controls which grammar rule is used to parse the unit.
 *
 * Use ``Charset`` in order to decode the source. If ``Charset`` is empty then
 * use the context's default charset.
 *
 * If any failure occurs, such as file opening, decoding, lexing or parsing
 * failure, return an analysis unit anyway: errors are described as diagnostics
 * of the returned analysis unit.
 */
extern rflx_analysis_unit
rflx_get_analysis_unit_from_file(
        rflx_analysis_context context,
        const char *filename,
        const char *charset,
        int reparse,
        rflx_grammar_rule rule);

/*
 * Create a new analysis unit for ``Filename`` or return the existing one if
 * any. Whether the analysis unit already exists or not, (re)parse it from the
 * source code in ``Buffer``.
 *
 * ``Rule`` controls which grammar rule is used to parse the unit.
 *
 * Use ``Charset`` in order to decode the source. If ``Charset`` is empty then
 * use the context's default charset.
 *
 * If any failure occurs, such as file opening, decoding, lexing or parsing
 * failure, return an analysis unit anyway: errors are described as diagnostics
 * of the returned analysis unit.
 */
extern rflx_analysis_unit
rflx_get_analysis_unit_from_buffer(
        rflx_analysis_context context,
        const char *filename,
        const char *charset,
        const char *buffer,
        size_t buffer_size,
        rflx_grammar_rule rule);


/*
 * Return the root node for this unit, or ``NULL`` if there is none.
 */
extern void
rflx_unit_root(rflx_analysis_unit unit,
                              rflx_node *result_p);

/*
 * Return a reference to the first token scanned in this unit.
 */
extern void
rflx_unit_first_token(rflx_analysis_unit unit,
                                     rflx_token *token);

/*
 * Return a reference to the last token scanned in this unit.
 */
extern void
rflx_unit_last_token(rflx_analysis_unit unit,
                                    rflx_token *token);

/*
 * Return the number of tokens in this unit.
 */
extern int
rflx_unit_token_count(rflx_analysis_unit unit);

/*
 * Return the number of trivias in this unit. This is 0 for units that were
 * parsed with trivia analysis disabled.
 */
extern int
rflx_unit_trivia_count(rflx_analysis_unit unit);

/*
 * Debug helper: output the lexical envs for the given analysis unit.
 */
extern void
rflx_unit_dump_lexical_env(rflx_analysis_unit unit);

/*
 * Return the filename this unit is associated to.
 *
 * The returned string is dynamically allocated and the caller must free it
 * when done with it.
 */
extern char *
rflx_unit_filename(rflx_analysis_unit unit);

/*
 * Return the number of diagnostics associated to this unit.
 */
extern unsigned
rflx_unit_diagnostic_count(rflx_analysis_unit unit);

/*
 * Get the Nth diagnostic in this unit and store it into ``*diagnostic_p``.
 * Return zero on failure (when N is too big).
 */
extern int
rflx_unit_diagnostic(rflx_analysis_unit unit,
                                    unsigned n,
                                    rflx_diagnostic *diagnostic_p);

/*
 * Return the context that owns this unit.
 */
extern rflx_analysis_context
rflx_unit_context(rflx_analysis_unit context);

/*
 * Reparse an analysis unit from the associated file.
 *
 * Use ``Charset`` in order to decode the source. If ``Charset`` is empty then
 * use the context's default charset.
 *
 * If any failure occurs, such as decoding, lexing or parsing failure,
 * diagnostic are emitted to explain what happened.
 */
extern void
rflx_unit_reparse_from_file(rflx_analysis_unit unit,
                                           const char *charset);

/*
 * Reparse an analysis unit from a buffer.
 *
 * Use ``Charset`` in order to decode the source. If ``Charset`` is empty then
 * use the context's default charset.
 *
 * If any failure occurs, such as decoding, lexing or parsing failure,
 * diagnostic are emitted to explain what happened.
 */
extern void
rflx_unit_reparse_from_buffer (rflx_analysis_unit unit,
                                              const char *charset,
                                              const char *buffer,
                                              size_t buffer_size);

/*
 * Create lexical environments for this analysis unit, according to the
 * specifications given in the language spec.
 *
 * If not done before, it will be automatically called during semantic
 * analysis. Calling it before enables one to control where the latency occurs.
 *
 * Depending on whether errors are discarded (see
 * ``Discard_Errors_In_Populate_Lexical_Env``), return ``0`` on failure and
 * ``1`` on success.
 */
extern int
rflx_unit_populate_lexical_env(
    rflx_analysis_unit unit
);

/*
 * General AST node primitives
 */

/*
 * Create an entity with null entity info for a given node.
 */
extern void
rflx_create_bare_entity(
    rflx_base_node node,
    rflx_node *entity
);

/*
 * Return whether this node is a null node reference.
 */
static inline int
rflx_node_is_null(rflx_node *node) {
    return node->node == NULL;
}

/*
 * Return the kind of this node.
 */
extern rflx_node_kind_enum
rflx_node_kind(rflx_node *node);

/*
 * Helper for textual dump: return the kind name for this node. The returned
 * string is a copy and thus must be free'd by the caller.
 */
extern void
rflx_kind_name(rflx_node_kind_enum kind, rflx_text *result);

/*
 * Return the analysis unit that owns this node.
 */
extern rflx_analysis_unit
rflx_node_unit(rflx_node *node);

/*
 * Return a hash for the given node.
 */
extern uint32_t
rflx_node_hash(rflx_node *node);

/*
 * Return whether the two nodes are equivalent.
 */
extern rflx_bool
rflx_node_is_equivalent(rflx_node *l, rflx_node *r);

/*
 * Return whether this node is a node that contains only a single token.
 */
extern int
rflx_node_is_token_node(rflx_node *node);

/*
 * Return whether this node is synthetic.
 */
extern int
rflx_node_is_synthetic(rflx_node *node);

/*
 * Return a representation of this node as a string.
 */
extern void
rflx_node_image(rflx_node *node,
                               rflx_text *result);

/*
 * Return the source buffer slice corresponding to the text that spans between
 * the first and the last tokens of this node.
 *
 * Note that this returns the empty string for synthetic nodes.
 */
extern void
rflx_node_text(rflx_node *node,
                              rflx_text *text);

/*
 * Return the spanning source location range for this node.
 *
 * Note that this returns the sloc of the parent for synthetic nodes.
 */
extern void
rflx_node_sloc_range(rflx_node *node,
                                    rflx_source_location_range *sloc_range);

/*
 * Return the bottom-most node from in ``Node`` and its children which contains
 * ``Sloc``, or ``NULL`` if there is none.
 */
extern void
rflx_lookup_in_node(rflx_node *node,
                                   const rflx_source_location *sloc,
                                   rflx_node *result_p);

/*
 * Return the number of children in this node.
 */
extern unsigned
rflx_node_children_count(rflx_node *node);

/*
 * Return the Nth child for in this node's fields and store it into
 * ``*child_p``.  Return zero on failure (when ``N`` is too big).
 */
extern int
rflx_node_child(rflx_node *node,
                               unsigned n,
                               rflx_node* child_p);

/*
 * Encode some text using the current locale. The result is dynamically
 * allocated: it is up to the caller to free it when done with it.
 *
 * This is a development helper to make it quick and easy to print token and
 * diagnostic text: it ignores errors (when the locale does not support some
 * characters). Production code should use real conversion routines such as
 * libiconv's in order to deal with UTF-32 texts.
 */
extern char *
rflx_text_to_locale_string(rflx_text *text);

/*
 * Free dynamically allocated memory.
 *
 * This is a helper to free objects from dynamic languages.
 */
extern void
rflx_free(void *address);

/*
 * If this text object owns the buffer it references, free this buffer.
 *
 * Note that even though this accepts a pointer to a text object, it does not
 * deallocates the text object itself but rather the buffer it references.
 */
extern void
rflx_destroy_text(rflx_text *text);

/*
 * Return the text associated to this symbol.
 */
extern void
rflx_symbol_text(rflx_symbol_type *symbol,
                                rflx_text *text);

/*
 * Create a big integer from its string representation (in base 10).
 */
extern rflx_big_integer
rflx_create_big_integer(rflx_text *text);

/*
 * Return the string representation (in base 10) of this big integer.
 */
extern void
rflx_big_integer_text(rflx_big_integer bigint,
                                     rflx_text *text);

/*
 * Decrease the reference count for this big integer.
 */
extern void
rflx_big_integer_decref(rflx_big_integer bigint);

/*
 * Allocate strings to represent the library version number and build date and
 * put them in Version/Build_Date. Callers are expected to call free() on the
 * returned string once done.
 */
extern void
rflx_get_versions(char **version, char **build_date);

/*
 * Create a string value from its content (UTF32 with native endianity).
 *
 * Note that the CONTENT buffer argument is copied: the returned value does not
 * contain a reference to it.
 */
extern rflx_string_type
rflx_create_string(uint32_t *content, int length);

/*
 * Decrease the reference count for this string.
 */
extern void
rflx_string_dec_ref(rflx_string_type self);

/*
 * Kind-specific AST node primitives
 */

/* All these primitives return their result through an OUT parameter.  They
   return a boolean telling whether the operation was successful (it can fail
   if the node does not have the proper type, for instance).  When an AST node
   is returned, its ref-count is left as-is.  */

        



/*
 * Return the syntactic parent for this node. Return null for the root node.
 */
extern int rflx_r_f_l_x_node_parent(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * Return an array that contains the lexical parents, this node included iff
 * ``with_self`` is True. Nearer parents are first in the list.
 */
extern int rflx_r_f_l_x_node_parents(
    rflx_node *node,

        
        rflx_bool
        with_self,

    rflx_node_array *value_p
);


        



/*
 * Return an array that contains the direct lexical children.
 *
 * .. warning:: This constructs a whole array every-time you call it, and as
 *    such is less efficient than calling the ``Child`` built-in.
 */
extern int rflx_r_f_l_x_node_children(
    rflx_node *node,


    rflx_node_array *value_p
);


        



/*
 * Return the first token used to parse this node.
 */
extern int rflx_r_f_l_x_node_token_start(
    rflx_node *node,


    rflx_token *value_p
);


        



/*
 * Return the last token used to parse this node.
 */
extern int rflx_r_f_l_x_node_token_end(
    rflx_node *node,


    rflx_token *value_p
);


        



/*
 * Return the 0-based index for Node in its parent's children.
 */
extern int rflx_r_f_l_x_node_child_index(
    rflx_node *node,


    int *value_p
);


        



/*
 * Return the node's previous sibling, or null if there is no such sibling.
 */
extern int rflx_r_f_l_x_node_previous_sibling(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * Return the node's next sibling, or null if there is no such sibling.
 */
extern int rflx_r_f_l_x_node_next_sibling(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * Return the analysis unit owning this node.
 */
extern int rflx_r_f_l_x_node_unit(
    rflx_node *node,


    rflx_analysis_unit *value_p
);


        



/*
 * Return whether the node is a ghost.
 *
 * Unlike regular nodes, ghost nodes cover no token in the input source: they
 * are logically located instead between two tokens. Both the ``token_start``
 * and the ``token_end`` of all ghost nodes is the token right after this
 * logical position.
 */
extern int rflx_r_f_l_x_node_is_ghost(
    rflx_node *node,


    rflx_bool *value_p
);


        



/*
 * Return a string containing the filename + the sloc in GNU conformant format.
 * Useful to create diagnostics from a node.
 */
extern int rflx_r_f_l_x_node_full_sloc_image(
    rflx_node *node,


    rflx_string_type *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_i_d_f_package(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_i_d_f_name(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_aspect_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_aspect_f_value(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_aggregate_associations_f_associations(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_checksum_val_f_data(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_checksum_value_range_f_first(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_checksum_value_range_f_last(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_checksum_assoc_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_checksum_assoc_f_covered_fields(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_refinement_decl_f_pdu(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_refinement_decl_f_field(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_refinement_decl_f_sdu(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_refinement_decl_f_condition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_session_decl_f_parameters(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_session_decl_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_session_decl_f_declarations(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_session_decl_f_states(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_session_decl_f_end_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_type_decl_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_type_decl_f_parameters(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes:
 * ``rflx_abstract_message_type_def``, ``rflx_enumeration_type_def``,
 * ``rflx_integer_type_def``, ``rflx_sequence_type_def``,
 * ``rflx_type_derivation_def``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_type_decl_f_definition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_description_f_content(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_element_value_assoc_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_element_value_assoc_f_literal(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_attribute_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_attribute_f_kind(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_bin_op_f_left(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_bin_op_f_op(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_bin_op_f_right(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_binding_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_binding_f_bindings(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_call_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field contains a list that itself contains one of the following nodes:
 * ``rflx_attribute``, ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``,
 * ``rflx_case_expression``, ``rflx_comprehension``, ``rflx_conversion``,
 * ``rflx_message_aggregate``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_quantified_expression``,
 * ``rflx_select_node``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_call_f_arguments(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_case_expression_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_case_expression_f_choices(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field contains a list that itself contains one of the following nodes:
 * ``rflx_i_d``, ``rflx_numeric_literal``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_choice_f_selectors(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_choice_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_comprehension_f_iterator(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_comprehension_f_sequence(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_comprehension_f_condition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_comprehension_f_selector(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_context_item_f_item(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_conversion_f_target_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_conversion_f_argument(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_aggregate_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_aggregate_f_values(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_negation_f_data(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_paren_expression_f_data(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_quantified_expression_f_operation(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_quantified_expression_f_parameter_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_quantified_expression_f_iterable(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_quantified_expression_f_predicate(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_select_node_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_select_node_f_selector(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_concatenation_f_left(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes:
 * ``rflx_sequence_aggregate``, ``rflx_string_literal``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_concatenation_f_right(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_sequence_aggregate_f_values(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_variable_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_formal_channel_decl_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_formal_channel_decl_f_parameters(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_formal_function_decl_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_formal_function_decl_f_parameters(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_formal_function_decl_f_return_type_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_renaming_decl_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_renaming_decl_f_type_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_renaming_decl_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_variable_decl_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_variable_decl_f_type_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_variable_decl_f_initializer(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_aggregate_association_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_aggregate_association_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_byte_order_aspect_f_byte_order(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_checksum_aspect_f_associations(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_f_type_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_f_type_arguments(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_f_aspects(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_message_field_f_condition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_f_thens(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_message_fields_f_initial_field(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_fields_f_fields(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_null_message_field_f_thens(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_package_node_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_package_node_f_declarations(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_package_node_f_end_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_parameter_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_parameter_f_type_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_parameters_f_parameters(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_specification_f_context_clause(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_specification_f_package_declaration(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_state_f_description(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_f_body(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_body_f_declarations(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_body_f_actions(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_body_f_conditional_transitions(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_body_f_final_transition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_state_body_f_exception_transition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_state_body_f_end_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_assignment_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_assignment_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_attribute_statement_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_attribute_statement_f_attr(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_attribute_statement_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_assignment_f_message(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_assignment_f_field(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_field_assignment_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_reset_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_reset_f_associations(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_term_assoc_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_term_assoc_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_then_node_f_target(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_then_node_f_aspects(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_then_node_f_condition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_transition_f_target(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field may be null even when there are no parsing errors.
 */
extern int rflx_transition_f_description(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_binding``, ``rflx_call``, ``rflx_case_expression``,
 * ``rflx_comprehension``, ``rflx_conversion``, ``rflx_message_aggregate``,
 * ``rflx_negation``, ``rflx_numeric_literal``, ``rflx_paren_expression``,
 * ``rflx_quantified_expression``, ``rflx_select_node``,
 * ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_conditional_transition_f_condition(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_type_argument_f_identifier(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_type_argument_f_expression(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_type_def_f_message_fields(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_message_type_def_f_aspects(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_named_enumeration_def_f_elements(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_positional_enumeration_def_f_elements(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_enumeration_type_def_f_elements(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_enumeration_type_def_f_aspects(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_modular_type_def_f_mod(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_range_type_def_f_first(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * This field can contain one of the following nodes: ``rflx_attribute``,
 * ``rflx_bin_op``, ``rflx_negation``, ``rflx_numeric_literal``,
 * ``rflx_paren_expression``, ``rflx_sequence_literal``, ``rflx_variable``
 *
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_range_type_def_f_last(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_range_type_def_f_size(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_sequence_type_def_f_element_type(
    rflx_node *node,


    rflx_node *value_p
);


        



/*
 * When there are no parsing errors, this field is never null.
 */
extern int rflx_type_derivation_def_f_base(
    rflx_node *node,


    rflx_node *value_p
);



/*
 * Event handlers
 */

/*
 * Create an event handler. When done with it, the result must be passed to
 * ``rflx_dec_ref_event_handler``.
 *
 * Pass as ``data`` a pointer to hold your private data: it will be passed to
 * all callbacks below.
 *
 * ``destroy`` is a callback that is called by ``rflx_dec_ref_event_handler``
 * to leave a chance to free resources that ``data`` may hold. ``NULL`` can be
 * passed if nothing needs to be done.
 *
 * ``unit_requested`` is a callback that will be called when a unit is
 * requested.
 *
 * .. warning:: Please note that the unit requested callback can be called
 *    *many* times for the same unit, so in all likeliness, those events should
 *    be filtered if they're used to forward diagnostics to the user.
 *
 * ``unit_parsed`` is a callback that will be called when a unit is parsed.
 */
extern rflx_event_handler
rflx_create_event_handler(
   void *data,
   rflx_event_handler_destroy_callback destroy_func,
   rflx_event_handler_unit_requested_callback unit_requested_func,
   rflx_event_handler_unit_parsed_callback unit_parsed_func
);

/*
 * Release an ownership share for this event handler. This destroys the event
 * handler if there are no shares left.
 */
extern void
rflx_dec_ref_event_handler(rflx_event_handler self);

/*
 * File readers
 */

/*
 * Create a file reader. When done with it, the result must be passed to
 * ``rflx_dec_ref_file_reader``.
 *
 * Pass as ``data`` a pointer to hold your private data: it will be passed to
 * all callbacks below.
 *
 * ``destroy`` is a callback that is called by ``rflx_dec_ref_file_reader`` to
 * leave a chance to free resources that ``data`` may hold.
 *
 * ``read`` is a callback. For a given filename/charset and whether to read the
 * BOM (Byte Order Mark), it tries to fetch the contents of the source file,
 * returned in ``Contents``. If there is an error, it must return it in
 * ``Diagnostic`` instead.
 */
extern rflx_file_reader
rflx_create_file_reader(
   void *data,
   rflx_file_reader_destroy_callback destroy_func,
   rflx_file_reader_read_callback read_func
);

/*
 * Release an ownership share for this file reader. This destroys the file
 * reader if there are no shares left.
 */
extern void
rflx_dec_ref_file_reader(rflx_file_reader self);




/*
 * Unit providers
 */

/*
 * Release an ownership share for this unit provider. This destroys the unit
 * provider if there are no shares left.
 */
extern void
rflx_dec_ref_unit_provider(void *data);




/*
 * Misc
 */

/*
 * Return exception information for the last error that happened in the current
 * thread. Will be automatically allocated on error and free'd on the next
 * error.
 */
extern const rflx_exception *
rflx_get_last_exception(void);

/*
 * Return the name of the given exception kind. Callers are responsible for
 * free'ing the result.
 */
extern char *
rflx_exception_name(rflx_exception_kind kind);

/*
 * Kind for this token.
 */
extern int
rflx_token_get_kind(rflx_token *token);

/*
 * Return a human-readable name for a token kind.
 *
 * The returned string is dynamically allocated and the caller must free it
 * when done with it.
 *
 * If the given kind is invalid, return ``NULL`` and set the last exception
 * accordingly.
 */
extern char *
rflx_token_kind_name(rflx_token_kind kind);

/*
 * Return the source location range of the given token.
 */
extern void
rflx_token_sloc_range(rflx_token *token,
                                     rflx_source_location_range *result);

/*
 * Return a reference to the next token in the corresponding analysis unit.
 */
extern void
rflx_token_next(rflx_token *token,
                               rflx_token *next_token);

/*
 * Return a reference to the previous token in the corresponding analysis unit.
 */
extern void
rflx_token_previous(rflx_token *token,
                                   rflx_token *previous_token);

/*
 * Compute the source buffer slice corresponding to the text that spans between
 * the ``First`` and ``Last`` tokens (both included). This yields an empty
 * slice if ``Last`` actually appears before ``First``. Put the result in
 * ``RESULT``.
 *
 * This returns ``0`` if ``First`` and ``Last`` don't belong to the same
 * analysis unit. Return ``1`` if successful.
 */
extern int
rflx_token_range_text(rflx_token *first,
                                     rflx_token *last,
                                     rflx_text *result);

/*
 * Return whether ``L`` and ``R`` are structurally equivalent tokens. This
 * means that their position in the stream won't be taken into account, only
 * the kind and text of the token.
 */
extern rflx_bool
rflx_token_is_equivalent(rflx_token *left,
                                        rflx_token *right);

/*
 * Tree rewriting
 */

/* ... context rewriting... */

/*
 * Return the rewriting handle associated to Context, or No_Rewriting_Handle if
 * Context is not being rewritten.
 */
extern rflx_rewriting_handle
rflx_rewriting_context_to_handle(
    rflx_analysis_context context
);

/*
 * Return the analysis context associated to Handle
 */
extern rflx_analysis_context
rflx_rewriting_handle_to_context(
    rflx_rewriting_handle handle
);

/*
 * Start a rewriting session for Context.
 *
 * This handle will keep track of all changes to do on Context's analysis
 * units. Once the set of changes is complete, call the Apply procedure to
 * actually update Context. This makes it possible to inspect the "old" Context
 * state while creating the list of changes.
 *
 * There can be only one rewriting session per analysis context, so this will
 * raise an Existing_Rewriting_Handle_Error exception if Context already has a
 * living rewriting session.
 */
extern rflx_rewriting_handle
rflx_rewriting_start_rewriting(
    rflx_analysis_context context
);

/*
 * Discard all modifications registered in Handle and close Handle. This
 * invalidates all related unit/node handles.
 */
extern void
rflx_rewriting_abort_rewriting(
    rflx_rewriting_handle context
);

/*
 * Apply all modifications to Handle's analysis context. If that worked, close
 * Handle and return (Success => True). Otherwise, reparsing did not work, so
 * keep Handle and its Context unchanged and return details about the error
 * that happened.
 *
 * Note that on success, this invalidates all related unit/node handles.
 */
extern void
rflx_rewriting_apply(
    rflx_rewriting_handle context,
    rflx_rewriting_apply_result *result
);

/*
 * Free the result of the ``Apply`` operation.
 */
extern void
rflx_rewriting_free_apply_result(
    rflx_rewriting_apply_result *result
);

/*
 * Return the list of unit rewriting handles in the given context handle for
 * units that the Apply primitive will modify.
 *
 * This returns the list as a dynamically allocated NULL-terminated array, that
 * the caller must free when done with it.
 */
extern rflx_unit_rewriting_handle *
rflx_rewriting_unit_handles(
    rflx_rewriting_handle handle
);

/* ... unit rewriting... */

/*
 * Return the rewriting handle corresponding to Unit
 */
extern rflx_unit_rewriting_handle
rflx_rewriting_unit_to_handle(rflx_analysis_unit context);

/*
 * Return the unit corresponding to Handle
 */
extern rflx_analysis_unit
rflx_rewriting_handle_to_unit(
    rflx_unit_rewriting_handle handle
);

/*
 * Return the node handle corresponding to the root of the unit which Handle
 * designates.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_unit_root(
    rflx_unit_rewriting_handle handle
);

/*
 * Set the root node for the unit Handle to Root. This unties the previous root
 * handle. If Root is not No_Node_Rewriting_Handle, this also ties Root to
 * Handle.
 *
 * Root must not already be tied to another analysis unit handle.
 */
extern void
rflx_rewriting_unit_set_root(
    rflx_unit_rewriting_handle handle,
    rflx_node_rewriting_handle root
);

/*
 * Return the text associated to the given unit.
 */
extern void
rflx_rewriting_unit_unparse(
    rflx_unit_rewriting_handle handle,
    rflx_text *result
);

/* ... node rewriting... */

/*
 * Return the rewriting handle corresponding to Node.
 *
 * The owning unit of Node must be free of diagnostics.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_node_to_handle(rflx_base_node context);

/*
 * Return the node which the given rewriting Handle relates to. This can be the
 * null entity if this handle designates a new node.
 */
extern rflx_base_node
rflx_rewriting_handle_to_node(
    rflx_node_rewriting_handle handle
);

/*
 * Return a handle for the rewriting context to which Handle belongs
 */
extern rflx_rewriting_handle
rflx_rewriting_node_to_context(
    rflx_node_rewriting_handle handle
);

/*
 * Turn the given rewritten node Handles designates into text. This is the text
 * that is used in Apply in order to re-create an analysis unit.
 */
extern void
rflx_rewriting_node_unparse(
    rflx_node_rewriting_handle handle,
    rflx_text *result
);

/*
 * Return the kind corresponding to Handle's node
 */
extern rflx_node_kind_enum
rflx_rewriting_kind(rflx_node_rewriting_handle handle);

/*
 * Return a representation of ``Handle`` as a string.
 */
extern void
rflx_rewriting_node_image(
    rflx_node_rewriting_handle handle,
    rflx_text *result
);

/*
 * Return whether this node handle is tied to an analysis unit. If it is not,
 * it can be passed as the Child parameter to Set_Child.
 */
extern int
rflx_rewriting_tied(rflx_node_rewriting_handle handle);

/*
 * Return a handle for the node that is the parent of Handle's node. This is
 * ``No_Rewriting_Handle`` for a node that is not tied to any tree yet.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_parent(rflx_node_rewriting_handle handle);

/*
 * Return the number of children the node represented by Handle has
 */
extern int
rflx_rewriting_children_count(
    rflx_node_rewriting_handle handle
);

/*
 * Return the node that is in the syntax ``Field`` for ``Handle``
 */
extern rflx_node_rewriting_handle
rflx_rewriting_child(
    rflx_node_rewriting_handle handle,
    rflx_introspection_member_ref field
);

/*
 * Return the list of children for ``Handle``.
 *
 * This returns the list as a dynamically allocated array with ``count``
 * elements.  The caller must free it when done with it.
 */
extern void
rflx_rewriting_children(
    rflx_node_rewriting_handle handle,
    rflx_node_rewriting_handle **children,
    int *count
);

/*
 * If ``Child`` is ``No_Rewriting_Node``, untie the syntax field in ``Handle``
 * corresponding to ``Field``, so it can be attached to another one. Otherwise,
 * ``Child`` must have no parent as it will be tied to ``Handle``'s tree.
 */
extern void
rflx_rewriting_set_child(
    rflx_node_rewriting_handle handle,
    rflx_introspection_member_ref field,
    rflx_node_rewriting_handle child
);

/*
 * Return the text associated to the given token node.
 */
extern void
rflx_rewriting_text(
    rflx_node_rewriting_handle handle,
    rflx_text *result
);

/*
 * Override text associated to the given token node.
 */
extern void
rflx_rewriting_set_text(
    rflx_node_rewriting_handle handle,
    rflx_text *text
);

/*
 * If Handle is the root of an analysis unit, untie it and set New_Node as its
 * new root. Otherwise, replace Handle with New_Node in Handle's parent node.
 *
 * Note that: * Handle must be tied to an existing analysis unit handle. *
 * New_Node must not already be tied to another analysis unit handle.
 */
extern void
rflx_rewriting_replace(
    rflx_node_rewriting_handle handle,
    rflx_node_rewriting_handle new_node
);

/*
 * Given a list of node rewriting handles ``H1``, ``H2``, ... ``HN``, replace
 * ``H1`` by ``H2`` in the rewritten tree, replace ``H2`` by ``H3``, etc. and
 * replace ``HN`` by ``H1``.
 *
 * Note that this operation is atomic: if it fails, no replacement is actually
 * performed.
 */
extern void
rflx_rewriting_rotate(
    rflx_node_rewriting_handle *handles,
    int count
);

/* ... list node rewriting... */

/*
 * Assuming ``Handle`` refers to a list node, return a handle to its first
 * child, or ``No_Node_Rewriting_Handle``` if it has no child node.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_first_child(
    rflx_node_rewriting_handle handle
);

/*
 * Assuming ``Handle`` refers to a list node, return a handle to its last
 * child, or ``No_Node_Rewriting_Handle``` if it has no child node.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_last_child(
    rflx_node_rewriting_handle handle
);

/*
 * Assuming ``Handle`` refers to the child of a list node, return a handle to
 * its next sibling, or ``No_Node_Rewriting_Handle``` if it is the last
 * sibling.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_next_child(
    rflx_node_rewriting_handle handle
);

/*
 * Assuming ``Handle`` refers to the child of a list node, return a handle to
 * its previous sibling, or ``No_Node_Rewriting_Handle``` if it is the first
 * sibling.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_previous_child(
    rflx_node_rewriting_handle handle
);

/*
 * Assuming ``Handle`` refers to the child of a list node, insert
 * ``New_Sibling`` as a new child in this list, right before ``Handle``.
 */
extern void
rflx_rewriting_insert_before(
    rflx_node_rewriting_handle handle,
    rflx_node_rewriting_handle new_sibling
);

/*
 * Assuming ``Handle`` refers to the child of a list node, insert
 * ``New_Sibling`` as a new child in this list, right before ``Handle``.
 */
extern void
rflx_rewriting_insert_after(
    rflx_node_rewriting_handle handle,
    rflx_node_rewriting_handle new_sibling
);

/*
 * Assuming ``Handle`` refers to a list node, insert ``New_Child`` to be the
 * first child in this list.
 */
extern void
rflx_rewriting_insert_first(
    rflx_node_rewriting_handle handle,
    rflx_node_rewriting_handle new_sibling
);

/*
 * Assuming ``Handle`` refers to a list node, insert ``New_Child`` to be the
 * last child in this list.
 */
extern void
rflx_rewriting_insert_last(
    rflx_node_rewriting_handle handle,
    rflx_node_rewriting_handle new_sibling
);

/*
 * Assuming Handle refers to the child of a list node, remove it from that
 * list.
 */
extern void
rflx_rewriting_remove_child(
    rflx_node_rewriting_handle handle
);

/* ... node creation... */

/*
 * Create a clone of the Handle node tree. The result is not tied to any
 * analysis unit tree.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_clone(rflx_node_rewriting_handle handle);

/*
 * Create a new node of the given Kind, with empty text (for token nodes) or
 * children (for regular nodes).
 */
extern rflx_node_rewriting_handle
rflx_rewriting_create_node(
    rflx_rewriting_handle handle,
    rflx_node_kind_enum kind
);

/*
 * Create a new token node with the given Kind and Text
 */
extern rflx_node_rewriting_handle
rflx_rewriting_create_token_node(
    rflx_rewriting_handle handle,
    rflx_node_kind_enum kind,
    rflx_text *text
);

/*
 * Create a new regular node of the given Kind and assign it the given
 * Children.
 *
 * Except for lists, which can have any number of children, the size of
 * Children must match the number of children associated to the given Kind.
 * Besides, all given children must not be tied.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_create_regular_node(
    rflx_rewriting_handle handle,
    rflx_node_kind_enum kind,
    rflx_node_rewriting_handle *children,
    int count
);

/*
 * Create a tree of new nodes from the given Template string, replacing
 * placeholders with nodes in Arguments and parsed according to the given
 * grammar Rule.
 */
extern rflx_node_rewriting_handle
rflx_rewriting_create_from_template(
    rflx_rewriting_handle handle,
    rflx_text *src_template,
    rflx_node_rewriting_handle *arguments,
    int count,
    rflx_grammar_rule rule
);




#ifdef __cplusplus
}
#endif

#endif
