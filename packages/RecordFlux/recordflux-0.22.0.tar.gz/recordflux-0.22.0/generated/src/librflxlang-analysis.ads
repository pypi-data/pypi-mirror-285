







with Ada.Containers;
private with Ada.Containers.Vectors;
private with Ada.Finalization;
with Ada.Strings.Unbounded;

with GNATCOLL.Refcount;


with Langkit_Support.File_Readers; use Langkit_Support.File_Readers;
with Langkit_Support.Lexical_Envs; use Langkit_Support.Lexical_Envs;
with Langkit_Support.Symbols;      use Langkit_Support.Symbols;

with Langkit_Support.Token_Data_Handlers;
use Langkit_Support.Token_Data_Handlers;

with Librflxlang.Common; use Librflxlang.Common;
private with Librflxlang.Implementation;
private with Librflxlang.Debug;




--  This package provides types and primitives to analyze source files as
--  analysis units.
--
--  This is the entry point to parse and process a unit:
--
--  * First create an analysis context with
--    :ada:ref:`Librflxlang.Analysis.Create_Context`.
--
--  * Then get analysis units out of it using the ``Get_From_*`` functions. The
--    most used of them is :ada:ref:`Librflxlang.Analysis.Get_From_File`,
--    which allows you to get an analysis unit out of a file path.
--
--  .. code-block:: ada
--
--      with Libadalang.Analysis;
--
--      procedure Main is
--         package Lib renames Librflxlang.Analysis;
--
--         Context : constant Lib.Analysis_Context := Lib.Create_Context;
--         Unit    : constant Lib.Analysis_Unit :=
--           Context.Get_From_File ("/path/to/source/file");
--      begin
--         Unit.Print;
--      end Main;


package Librflxlang.Analysis is

   use Support.Diagnostics, Support.Slocs, Support.Text;

   type Analysis_Context is tagged private;
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

   type Analysis_Unit is new Langkit_Support.Text.Text_Buffer_Ifc with private;
   --  This type represents the analysis of a single file.
   --
   --  This type has strong-reference semantics and is ref-counted.
   --  Furthermore, a reference to a unit contains an implicit reference to the
   --  context that owns it. This means that keeping a reference to a unit will
   --  keep the context and all the unit it contains allocated.

   No_Analysis_Context : constant Analysis_Context;
   --  Special value to mean the absence of analysis context

   No_Analysis_Unit : constant Analysis_Unit;
   --  Special value to mean the absence of analysis unit. No analysis units
   --  can be passed this value.

   ---------------
   -- AST nodes --
   ---------------

      type R_F_L_X_Node is tagged private;
      --  Data type for all nodes. Nodes are assembled to make up a tree.  See
      --  the node primitives below to inspect such trees.
      --
      --  Unlike for contexts and units, this type has weak-reference
      --  semantics: keeping a reference to a node has no effect on the
      --  decision to keep the unit that it owns allocated. This means that
      --  once all references to the context and units related to a node are
      --  dropped, the context and its units are deallocated and the node
      --  becomes a stale reference: most operations on it will raise a
      --  ``Stale_Reference_Error``.
      --
      --  Note that since reparsing an analysis unit deallocates all the nodes
      --  it contains, this operation makes all reference to these nodes stale
      --  as well.
      --
      --  Root node class for the RecordFlux language.

      function Equals (L, R : R_F_L_X_Node) return Boolean;
      --  Comparison function, meant to compare two nodes.
      --
      --  .. note: For complex reasons, we cannot expose this function as the
      --     ``"="`` operator. This is the function you need to use as the
      --     equality function for containers instantiations.
      type Abstract_I_D is new R_F_L_X_Node with private
      ;
      --  Base class for identifiers.

      type Type_Def is new R_F_L_X_Node with private
      ;
      --  Base class for type definitions (integers, messages, type
      --  derivations, sequences, enums).

      type Abstract_Message_Type_Def is new Type_Def with private
      ;
      --  Base class for message type definitions.

      type Aspect is new R_F_L_X_Node with private
      ;
      

      type R_F_L_X_Node_Base_List is new R_F_L_X_Node with private
      ;
      

      type Aspect_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Aspect_List_First,
                           Next        => Aspect_List_Next,
                           Has_Element => Aspect_List_Has_Element,
                           Element     => Aspect_List_Element)
      ;
      --  List of Aspect.

      type Statement is new R_F_L_X_Node with private
      ;
      --  Base class for statements.

      type Assignment is new Statement with private
      ;
      --  Assignment of expression to unqualified identifier.

      type Attr is new R_F_L_X_Node with private
      ;
      --  Attribute kind.

      type Attr_First is new Attr with private
      ;
      

      type Attr_Has_Data is new Attr with private
      ;
      

      type Attr_Head is new Attr with private
      ;
      

      type Attr_Last is new Attr with private
      ;
      

      type Attr_Opaque is new Attr with private
      ;
      

      type Attr_Present is new Attr with private
      ;
      

      type Attr_Size is new Attr with private
      ;
      

      type Attr_Stmt is new R_F_L_X_Node with private
      ;
      --  Attribute statement kind.

      type Attr_Stmt_Append is new Attr_Stmt with private
      ;
      

      type Attr_Stmt_Extend is new Attr_Stmt with private
      ;
      

      type Attr_Stmt_Read is new Attr_Stmt with private
      ;
      

      type Attr_Stmt_Write is new Attr_Stmt with private
      ;
      

      type Attr_Valid is new Attr with private
      ;
      

      type Attr_Valid_Checksum is new Attr with private
      ;
      

      type Expr is new R_F_L_X_Node with private
      ;
      --  Base class for expressions.

      type Attribute is new Expr with private
      ;
      

      type Attribute_Statement is new Statement with private
      ;
      --  Attribute statement.

      type Base_Aggregate is new R_F_L_X_Node with private
      ;
      --  Base class for message aggregates.

      type Base_Checksum_Val is new R_F_L_X_Node with private
      ;
      --  Base class for checksum values.

      type Base_Checksum_Val_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Base_Checksum_Val_List_First,
                           Next        => Base_Checksum_Val_List_Next,
                           Has_Element => Base_Checksum_Val_List_Has_Element,
                           Element     => Base_Checksum_Val_List_Element)
      ;
      --  List of BaseChecksumVal.

      type Bin_Op is new Expr with private
      ;
      --  Binary operation.

      type Binding is new Expr with private
      ;
      

      type Message_Aspect is new R_F_L_X_Node with private
      ;
      --  Base class for message aspects.

      type Byte_Order_Aspect is new Message_Aspect with private
      ;
      

      type Byte_Order_Type is new R_F_L_X_Node with private
      ;
      

      type Byte_Order_Type_Highorderfirst is new Byte_Order_Type with private
      ;
      

      type Byte_Order_Type_Loworderfirst is new Byte_Order_Type with private
      ;
      

      type Call is new Expr with private
      ;
      

      type Case_Expression is new Expr with private
      ;
      

      type Channel_Attribute is new R_F_L_X_Node with private
      ;
      --  Base class for channel attributes.

      type Channel_Attribute_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Channel_Attribute_List_First,
                           Next        => Channel_Attribute_List_Next,
                           Has_Element => Channel_Attribute_List_Has_Element,
                           Element     => Channel_Attribute_List_Element)
      ;
      --  List of ChannelAttribute.

      type Checksum_Aspect is new Message_Aspect with private
      ;
      

      type Checksum_Assoc is new R_F_L_X_Node with private
      ;
      --  Association between checksum field and list of covered fields.

      type Checksum_Assoc_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Checksum_Assoc_List_First,
                           Next        => Checksum_Assoc_List_Next,
                           Has_Element => Checksum_Assoc_List_Has_Element,
                           Element     => Checksum_Assoc_List_Element)
      ;
      --  List of ChecksumAssoc.

      type Checksum_Val is new Base_Checksum_Val with private
      ;
      --  Single checksum value.

      type Checksum_Value_Range is new Base_Checksum_Val with private
      ;
      --  Checksum value range.

      type Choice is new Expr with private
      ;
      

      type Choice_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Choice_List_First,
                           Next        => Choice_List_Next,
                           Has_Element => Choice_List_Has_Element,
                           Element     => Choice_List_Element)
      ;
      --  List of Choice.

      type Comprehension is new Expr with private
      ;
      

      type Sequence_Literal is new Expr with private
      ;
      --  Base class for sequence literals (strings, sequence aggregates).

      type Concatenation is new Sequence_Literal with private
      ;
      --  Concatenation of aggregates or string literals.

      type Transition is new R_F_L_X_Node with private
      ;
      --  Unconditional session state transition.

      type Conditional_Transition is new Transition with private
      ;
      --  Conditional session state transition.

      type Conditional_Transition_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Conditional_Transition_List_First,
                           Next        => Conditional_Transition_List_Next,
                           Has_Element => Conditional_Transition_List_Has_Element,
                           Element     => Conditional_Transition_List_Element)
      ;
      --  List of ConditionalTransition.

      type Context_Item is new Expr with private
      ;
      --  Import statement (with Package).

      type Context_Item_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Context_Item_List_First,
                           Next        => Context_Item_List_Next,
                           Has_Element => Context_Item_List_Has_Element,
                           Element     => Context_Item_List_Element)
      ;
      --  List of ContextItem.

      type Conversion is new Expr with private
      ;
      

      type Declaration is new R_F_L_X_Node with private
      ;
      --  Base class for declarations (types, refinements, sessions).

      type Declaration_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Declaration_List_First,
                           Next        => Declaration_List_Next,
                           Has_Element => Declaration_List_Has_Element,
                           Element     => Declaration_List_Element)
      ;
      --  List of Declaration.

      type Description is new R_F_L_X_Node with private
      ;
      --  String description of an entity.

      type Element_Value_Assoc is new R_F_L_X_Node with private
      ;
      --  Element/value association.

      type Element_Value_Assoc_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Element_Value_Assoc_List_First,
                           Next        => Element_Value_Assoc_List_Next,
                           Has_Element => Element_Value_Assoc_List_Has_Element,
                           Element     => Element_Value_Assoc_List_Element)
      ;
      --  List of ElementValueAssoc.

      type Enumeration_Def is new Type_Def with private
      ;
      --  Base class for enumeration definitions.

      type Enumeration_Type_Def is new Type_Def with private
      ;
      

      type Expr_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Expr_List_First,
                           Next        => Expr_List_Next,
                           Has_Element => Expr_List_Has_Element,
                           Element     => Expr_List_Element)
      ;
      --  List of Expr.
      --
      --  This list node can contain one of the following nodes:
      --  :ada:ref:`Attribute`, :ada:ref:`Bin_Op`, :ada:ref:`Binding`,
      --  :ada:ref:`Call`, :ada:ref:`Case_Expression`,
      --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
      --  :ada:ref:`Message_Aggregate`, :ada:ref:`Negation`,
      --  :ada:ref:`Numeric_Literal`, :ada:ref:`Paren_Expression`,
      --  :ada:ref:`Quantified_Expression`, :ada:ref:`Select_Node`,
      --  :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`

      type Formal_Decl is new R_F_L_X_Node with private
      ;
      --  Base class for generic formal session declarations.

      type Formal_Channel_Decl is new Formal_Decl with private
      ;
      

      type Formal_Decl_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Formal_Decl_List_First,
                           Next        => Formal_Decl_List_Next,
                           Has_Element => Formal_Decl_List_Has_Element,
                           Element     => Formal_Decl_List_Element)
      ;
      --  List of FormalDecl.

      type Formal_Function_Decl is new Formal_Decl with private
      ;
      

      type I_D is new Abstract_I_D with private
      ;
      --  Qualified identifiers which may optionally have a package part (e.g.
      --  "Pkg::Foo", "Foo").

      type Integer_Type_Def is new Type_Def with private
      ;
      --  Base class for all integer type definitions.

      type Local_Decl is new R_F_L_X_Node with private
      ;
      --  Base class for session or state local declarations.

      type Local_Decl_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Local_Decl_List_First,
                           Next        => Local_Decl_List_Next,
                           Has_Element => Local_Decl_List_Has_Element,
                           Element     => Local_Decl_List_Element)
      ;
      --  List of LocalDecl.

      type Message_Aggregate is new Expr with private
      ;
      

      type Message_Aggregate_Association is new R_F_L_X_Node with private
      ;
      

      type Message_Aggregate_Association_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Message_Aggregate_Association_List_First,
                           Next        => Message_Aggregate_Association_List_Next,
                           Has_Element => Message_Aggregate_Association_List_Has_Element,
                           Element     => Message_Aggregate_Association_List_Element)
      ;
      --  List of MessageAggregateAssociation.

      type Message_Aggregate_Associations is new Base_Aggregate with private
      ;
      

      type Message_Aspect_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Message_Aspect_List_First,
                           Next        => Message_Aspect_List_Next,
                           Has_Element => Message_Aspect_List_Has_Element,
                           Element     => Message_Aspect_List_Element)
      ;
      --  List of MessageAspect.

      type Message_Field is new R_F_L_X_Node with private
      ;
      

      type Message_Field_Assignment is new Statement with private
      ;
      --  Assignment of expression to message field.

      type Message_Field_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Message_Field_List_First,
                           Next        => Message_Field_List_Next,
                           Has_Element => Message_Field_List_Has_Element,
                           Element     => Message_Field_List_Element)
      ;
      --  List of MessageField.

      type Message_Fields is new R_F_L_X_Node with private
      ;
      

      type Message_Type_Def is new Abstract_Message_Type_Def with private
      ;
      

      type Modular_Type_Def is new Integer_Type_Def with private
      ;
      

      type Named_Enumeration_Def is new Enumeration_Def with private
      ;
      

      type Negation is new Expr with private
      ;
      

      type Null_Message_Aggregate is new Base_Aggregate with private
      ;
      

      type Null_Message_Field is new R_F_L_X_Node with private
      ;
      

      type Null_Message_Type_Def is new Abstract_Message_Type_Def with private
      ;
      

      type Numeric_Literal is new Expr with private
      ;
      

      type Numeric_Literal_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Numeric_Literal_List_First,
                           Next        => Numeric_Literal_List_Next,
                           Has_Element => Numeric_Literal_List_Has_Element,
                           Element     => Numeric_Literal_List_Element)
      ;
      --  List of NumericLiteral.

      type Op is new R_F_L_X_Node with private
      ;
      --  Operators for binary expressions.

      type Op_Add is new Op with private
      ;
      

      type Op_And is new Op with private
      ;
      

      type Op_Div is new Op with private
      ;
      

      type Op_Eq is new Op with private
      ;
      

      type Op_Ge is new Op with private
      ;
      

      type Op_Gt is new Op with private
      ;
      

      type Op_In is new Op with private
      ;
      

      type Op_Le is new Op with private
      ;
      

      type Op_Lt is new Op with private
      ;
      

      type Op_Mod is new Op with private
      ;
      

      type Op_Mul is new Op with private
      ;
      

      type Op_Neq is new Op with private
      ;
      

      type Op_Notin is new Op with private
      ;
      

      type Op_Or is new Op with private
      ;
      

      type Op_Pow is new Op with private
      ;
      

      type Op_Sub is new Op with private
      ;
      

      type Package_Node is new R_F_L_X_Node with private
      ;
      

      type Parameter is new R_F_L_X_Node with private
      ;
      

      type Parameter_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Parameter_List_First,
                           Next        => Parameter_List_Next,
                           Has_Element => Parameter_List_Has_Element,
                           Element     => Parameter_List_Element)
      ;
      --  List of Parameter.

      type Parameters is new R_F_L_X_Node with private
      ;
      

      type Paren_Expression is new Expr with private
      ;
      --  Parenthesized expression.

      type Positional_Enumeration_Def is new Enumeration_Def with private
      ;
      

      type Quantified_Expression is new Expr with private
      ;
      

      type Quantifier is new R_F_L_X_Node with private
      ;
      --  Quantifier kind.

      type Quantifier_All is new Quantifier with private
      ;
      

      type Quantifier_Some is new Quantifier with private
      ;
      

      type R_F_L_X_Node_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => R_F_L_X_Node_List_First,
                           Next        => R_F_L_X_Node_List_Next,
                           Has_Element => R_F_L_X_Node_List_Has_Element,
                           Element     => R_F_L_X_Node_List_Element)
      ;
      --  List of RFLXNode.
      --
      --  This list node can contain one of the following nodes:
      --  :ada:ref:`I_D`, :ada:ref:`Numeric_Literal`

      type Range_Type_Def is new Integer_Type_Def with private
      ;
      

      type Readable is new Channel_Attribute with private
      ;
      --  Channel attribute (channel can be read).

      type Refinement_Decl is new Declaration with private
      ;
      --  Refinement declaration (for Message use (Field => Inner_Type)).

      type Renaming_Decl is new Local_Decl with private
      ;
      --  Session renaming declaration.

      type Reset is new Statement with private
      ;
      --  Reset statement.

      type Select_Node is new Expr with private
      ;
      

      type Sequence_Aggregate is new Sequence_Literal with private
      ;
      --  List of literal sequence values.

      type Sequence_Type_Def is new Type_Def with private
      ;
      

      type Session_Decl is new Declaration with private
      ;
      

      type Specification is new R_F_L_X_Node with private
      ;
      --  RecordFlux specification.

      type State is new R_F_L_X_Node with private
      ;
      --  Session state.

      type State_Body is new R_F_L_X_Node with private
      ;
      --  Body of a session state.

      type State_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => State_List_First,
                           Next        => State_List_Next,
                           Has_Element => State_List_Has_Element,
                           Element     => State_List_Element)
      ;
      --  List of State.

      type Statement_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Statement_List_First,
                           Next        => Statement_List_Next,
                           Has_Element => Statement_List_Has_Element,
                           Element     => Statement_List_Element)
      ;
      --  List of Statement.

      type String_Literal is new Sequence_Literal with private
      ;
      --  Double-quoted string literal.

      type Term_Assoc is new R_F_L_X_Node with private
      ;
      

      type Term_Assoc_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Term_Assoc_List_First,
                           Next        => Term_Assoc_List_Next,
                           Has_Element => Term_Assoc_List_Has_Element,
                           Element     => Term_Assoc_List_Element)
      ;
      --  List of TermAssoc.

      type Then_Node is new R_F_L_X_Node with private
      ;
      --  Link to field.

      type Then_Node_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Then_Node_List_First,
                           Next        => Then_Node_List_Next,
                           Has_Element => Then_Node_List_Has_Element,
                           Element     => Then_Node_List_Element)
      ;
      --  List of Then.

      type Type_Argument is new R_F_L_X_Node with private
      ;
      

      type Type_Argument_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Type_Argument_List_First,
                           Next        => Type_Argument_List_Next,
                           Has_Element => Type_Argument_List_Has_Element,
                           Element     => Type_Argument_List_Element)
      ;
      --  List of TypeArgument.

      type Type_Decl is new Declaration with private
      ;
      --  Type declaration (type Foo is ...).

      type Type_Derivation_Def is new Type_Def with private
      ;
      

      type Unqualified_I_D is new Abstract_I_D with private
      ;
      --  Simple, unqualified identifiers, i.e. identifiers without a package
      --  part (e.g. "Foo").

      type Unqualified_I_D_List is new R_F_L_X_Node_Base_List with private
         with Iterable => (First       => Unqualified_I_D_List_First,
                           Next        => Unqualified_I_D_List_Next,
                           Has_Element => Unqualified_I_D_List_Has_Element,
                           Element     => Unqualified_I_D_List_Element)
      ;
      --  List of UnqualifiedID.

      type Variable is new Expr with private
      ;
      

      type Variable_Decl is new Local_Decl with private
      ;
      --  Session variable declaration.

      type Writable is new Channel_Attribute with private
      ;
      --  Channel attribute (channel can be written).


      No_R_F_L_X_Node : constant R_F_L_X_Node;
      --  Special value to represent the absence of a node. Note that every
      --  node type derived from the root type has a similar ``No_Node``
      --  constant.
      No_Abstract_I_D : constant Abstract_I_D;
      --% no-document: True
      No_Type_Def : constant Type_Def;
      --% no-document: True
      No_Abstract_Message_Type_Def : constant Abstract_Message_Type_Def;
      --% no-document: True
      No_Aspect : constant Aspect;
      --% no-document: True
      No_R_F_L_X_Node_Base_List : constant R_F_L_X_Node_Base_List;
      --% no-document: True
      No_Aspect_List : constant Aspect_List;
      --% no-document: True
      No_Statement : constant Statement;
      --% no-document: True
      No_Assignment : constant Assignment;
      --% no-document: True
      No_Attr : constant Attr;
      --% no-document: True
      No_Attr_First : constant Attr_First;
      --% no-document: True
      No_Attr_Has_Data : constant Attr_Has_Data;
      --% no-document: True
      No_Attr_Head : constant Attr_Head;
      --% no-document: True
      No_Attr_Last : constant Attr_Last;
      --% no-document: True
      No_Attr_Opaque : constant Attr_Opaque;
      --% no-document: True
      No_Attr_Present : constant Attr_Present;
      --% no-document: True
      No_Attr_Size : constant Attr_Size;
      --% no-document: True
      No_Attr_Stmt : constant Attr_Stmt;
      --% no-document: True
      No_Attr_Stmt_Append : constant Attr_Stmt_Append;
      --% no-document: True
      No_Attr_Stmt_Extend : constant Attr_Stmt_Extend;
      --% no-document: True
      No_Attr_Stmt_Read : constant Attr_Stmt_Read;
      --% no-document: True
      No_Attr_Stmt_Write : constant Attr_Stmt_Write;
      --% no-document: True
      No_Attr_Valid : constant Attr_Valid;
      --% no-document: True
      No_Attr_Valid_Checksum : constant Attr_Valid_Checksum;
      --% no-document: True
      No_Expr : constant Expr;
      --% no-document: True
      No_Attribute : constant Attribute;
      --% no-document: True
      No_Attribute_Statement : constant Attribute_Statement;
      --% no-document: True
      No_Base_Aggregate : constant Base_Aggregate;
      --% no-document: True
      No_Base_Checksum_Val : constant Base_Checksum_Val;
      --% no-document: True
      No_Base_Checksum_Val_List : constant Base_Checksum_Val_List;
      --% no-document: True
      No_Bin_Op : constant Bin_Op;
      --% no-document: True
      No_Binding : constant Binding;
      --% no-document: True
      No_Message_Aspect : constant Message_Aspect;
      --% no-document: True
      No_Byte_Order_Aspect : constant Byte_Order_Aspect;
      --% no-document: True
      No_Byte_Order_Type : constant Byte_Order_Type;
      --% no-document: True
      No_Byte_Order_Type_Highorderfirst : constant Byte_Order_Type_Highorderfirst;
      --% no-document: True
      No_Byte_Order_Type_Loworderfirst : constant Byte_Order_Type_Loworderfirst;
      --% no-document: True
      No_Call : constant Call;
      --% no-document: True
      No_Case_Expression : constant Case_Expression;
      --% no-document: True
      No_Channel_Attribute : constant Channel_Attribute;
      --% no-document: True
      No_Channel_Attribute_List : constant Channel_Attribute_List;
      --% no-document: True
      No_Checksum_Aspect : constant Checksum_Aspect;
      --% no-document: True
      No_Checksum_Assoc : constant Checksum_Assoc;
      --% no-document: True
      No_Checksum_Assoc_List : constant Checksum_Assoc_List;
      --% no-document: True
      No_Checksum_Val : constant Checksum_Val;
      --% no-document: True
      No_Checksum_Value_Range : constant Checksum_Value_Range;
      --% no-document: True
      No_Choice : constant Choice;
      --% no-document: True
      No_Choice_List : constant Choice_List;
      --% no-document: True
      No_Comprehension : constant Comprehension;
      --% no-document: True
      No_Sequence_Literal : constant Sequence_Literal;
      --% no-document: True
      No_Concatenation : constant Concatenation;
      --% no-document: True
      No_Transition : constant Transition;
      --% no-document: True
      No_Conditional_Transition : constant Conditional_Transition;
      --% no-document: True
      No_Conditional_Transition_List : constant Conditional_Transition_List;
      --% no-document: True
      No_Context_Item : constant Context_Item;
      --% no-document: True
      No_Context_Item_List : constant Context_Item_List;
      --% no-document: True
      No_Conversion : constant Conversion;
      --% no-document: True
      No_Declaration : constant Declaration;
      --% no-document: True
      No_Declaration_List : constant Declaration_List;
      --% no-document: True
      No_Description : constant Description;
      --% no-document: True
      No_Element_Value_Assoc : constant Element_Value_Assoc;
      --% no-document: True
      No_Element_Value_Assoc_List : constant Element_Value_Assoc_List;
      --% no-document: True
      No_Enumeration_Def : constant Enumeration_Def;
      --% no-document: True
      No_Enumeration_Type_Def : constant Enumeration_Type_Def;
      --% no-document: True
      No_Expr_List : constant Expr_List;
      --% no-document: True
      No_Formal_Decl : constant Formal_Decl;
      --% no-document: True
      No_Formal_Channel_Decl : constant Formal_Channel_Decl;
      --% no-document: True
      No_Formal_Decl_List : constant Formal_Decl_List;
      --% no-document: True
      No_Formal_Function_Decl : constant Formal_Function_Decl;
      --% no-document: True
      No_I_D : constant I_D;
      --% no-document: True
      No_Integer_Type_Def : constant Integer_Type_Def;
      --% no-document: True
      No_Local_Decl : constant Local_Decl;
      --% no-document: True
      No_Local_Decl_List : constant Local_Decl_List;
      --% no-document: True
      No_Message_Aggregate : constant Message_Aggregate;
      --% no-document: True
      No_Message_Aggregate_Association : constant Message_Aggregate_Association;
      --% no-document: True
      No_Message_Aggregate_Association_List : constant Message_Aggregate_Association_List;
      --% no-document: True
      No_Message_Aggregate_Associations : constant Message_Aggregate_Associations;
      --% no-document: True
      No_Message_Aspect_List : constant Message_Aspect_List;
      --% no-document: True
      No_Message_Field : constant Message_Field;
      --% no-document: True
      No_Message_Field_Assignment : constant Message_Field_Assignment;
      --% no-document: True
      No_Message_Field_List : constant Message_Field_List;
      --% no-document: True
      No_Message_Fields : constant Message_Fields;
      --% no-document: True
      No_Message_Type_Def : constant Message_Type_Def;
      --% no-document: True
      No_Modular_Type_Def : constant Modular_Type_Def;
      --% no-document: True
      No_Named_Enumeration_Def : constant Named_Enumeration_Def;
      --% no-document: True
      No_Negation : constant Negation;
      --% no-document: True
      No_Null_Message_Aggregate : constant Null_Message_Aggregate;
      --% no-document: True
      No_Null_Message_Field : constant Null_Message_Field;
      --% no-document: True
      No_Null_Message_Type_Def : constant Null_Message_Type_Def;
      --% no-document: True
      No_Numeric_Literal : constant Numeric_Literal;
      --% no-document: True
      No_Numeric_Literal_List : constant Numeric_Literal_List;
      --% no-document: True
      No_Op : constant Op;
      --% no-document: True
      No_Op_Add : constant Op_Add;
      --% no-document: True
      No_Op_And : constant Op_And;
      --% no-document: True
      No_Op_Div : constant Op_Div;
      --% no-document: True
      No_Op_Eq : constant Op_Eq;
      --% no-document: True
      No_Op_Ge : constant Op_Ge;
      --% no-document: True
      No_Op_Gt : constant Op_Gt;
      --% no-document: True
      No_Op_In : constant Op_In;
      --% no-document: True
      No_Op_Le : constant Op_Le;
      --% no-document: True
      No_Op_Lt : constant Op_Lt;
      --% no-document: True
      No_Op_Mod : constant Op_Mod;
      --% no-document: True
      No_Op_Mul : constant Op_Mul;
      --% no-document: True
      No_Op_Neq : constant Op_Neq;
      --% no-document: True
      No_Op_Notin : constant Op_Notin;
      --% no-document: True
      No_Op_Or : constant Op_Or;
      --% no-document: True
      No_Op_Pow : constant Op_Pow;
      --% no-document: True
      No_Op_Sub : constant Op_Sub;
      --% no-document: True
      No_Package_Node : constant Package_Node;
      --% no-document: True
      No_Parameter : constant Parameter;
      --% no-document: True
      No_Parameter_List : constant Parameter_List;
      --% no-document: True
      No_Parameters : constant Parameters;
      --% no-document: True
      No_Paren_Expression : constant Paren_Expression;
      --% no-document: True
      No_Positional_Enumeration_Def : constant Positional_Enumeration_Def;
      --% no-document: True
      No_Quantified_Expression : constant Quantified_Expression;
      --% no-document: True
      No_Quantifier : constant Quantifier;
      --% no-document: True
      No_Quantifier_All : constant Quantifier_All;
      --% no-document: True
      No_Quantifier_Some : constant Quantifier_Some;
      --% no-document: True
      No_R_F_L_X_Node_List : constant R_F_L_X_Node_List;
      --% no-document: True
      No_Range_Type_Def : constant Range_Type_Def;
      --% no-document: True
      No_Readable : constant Readable;
      --% no-document: True
      No_Refinement_Decl : constant Refinement_Decl;
      --% no-document: True
      No_Renaming_Decl : constant Renaming_Decl;
      --% no-document: True
      No_Reset : constant Reset;
      --% no-document: True
      No_Select_Node : constant Select_Node;
      --% no-document: True
      No_Sequence_Aggregate : constant Sequence_Aggregate;
      --% no-document: True
      No_Sequence_Type_Def : constant Sequence_Type_Def;
      --% no-document: True
      No_Session_Decl : constant Session_Decl;
      --% no-document: True
      No_Specification : constant Specification;
      --% no-document: True
      No_State : constant State;
      --% no-document: True
      No_State_Body : constant State_Body;
      --% no-document: True
      No_State_List : constant State_List;
      --% no-document: True
      No_Statement_List : constant Statement_List;
      --% no-document: True
      No_String_Literal : constant String_Literal;
      --% no-document: True
      No_Term_Assoc : constant Term_Assoc;
      --% no-document: True
      No_Term_Assoc_List : constant Term_Assoc_List;
      --% no-document: True
      No_Then_Node : constant Then_Node;
      --% no-document: True
      No_Then_Node_List : constant Then_Node_List;
      --% no-document: True
      No_Type_Argument : constant Type_Argument;
      --% no-document: True
      No_Type_Argument_List : constant Type_Argument_List;
      --% no-document: True
      No_Type_Decl : constant Type_Decl;
      --% no-document: True
      No_Type_Derivation_Def : constant Type_Derivation_Def;
      --% no-document: True
      No_Unqualified_I_D : constant Unqualified_I_D;
      --% no-document: True
      No_Unqualified_I_D_List : constant Unqualified_I_D_List;
      --% no-document: True
      No_Variable : constant Variable;
      --% no-document: True
      No_Variable_Decl : constant Variable_Decl;
      --% no-document: True
      No_Writable : constant Writable;
      --% no-document: True

   function Is_Null (Node : R_F_L_X_Node'Class) return Boolean;
   --  Return whether this node is a null node reference.

   function Is_Token_Node
     (Node : R_F_L_X_Node'Class) return Boolean;
   --  Return whether this node is a node that contains only a single token.

   function Is_Synthetic
     (Node : R_F_L_X_Node'Class) return Boolean;
   --  Return whether this node is synthetic.

   function "=" (L, R : R_F_L_X_Node'Class) return Boolean;
   --  Return whether ``L`` and ``R`` designate the same node

   function Image (Node : R_F_L_X_Node'Class) return String;
   --  Return a short string describing ``Node``, or None" if ``Node.Is_Null``
   --  is true.

   -------------------
   -- Event handler --
   -------------------

   type Event_Handler_Interface is interface;
   --  Interface to handle events sent by the analysis context.

   procedure Unit_Requested_Callback
     (Self               : in out Event_Handler_Interface;
      Context            : Analysis_Context'Class;
      Name               : Text_Type;
      From               : Analysis_Unit'Class;
      Found              : Boolean;
      Is_Not_Found_Error : Boolean) is null;
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

   procedure Unit_Parsed_Callback
     (Self     : in out Event_Handler_Interface;
      Context  : Analysis_Context'Class;
      Unit     : Analysis_Unit'Class;
      Reparsed : Boolean) is null;
   --  Callback that will be called when any unit is parsed from the context
   --  ``Context``.
   --
   --  ``Unit`` is the resulting unit.
   --
   --  ``Reparsed`` indicates whether the unit was reparsed, or whether it was
   --  the first parse.

   procedure Release (Self : in out Event_Handler_Interface) is abstract;
   --  Actions to perform when releasing resources associated to Self

   procedure Do_Release (Self : in out Event_Handler_Interface'Class);
   --  Helper for the instantiation below

   package Event_Handler_References is new GNATCOLL.Refcount.Shared_Pointers
     (Event_Handler_Interface'Class, Do_Release);

   subtype Event_Handler_Reference is Event_Handler_References.Ref;
   No_Event_Handler_Ref : Event_Handler_Reference renames
      Event_Handler_References.Null_Ref;

   function Create_Event_Handler_Reference
     (Handler : Event_Handler_Interface'Class) return Event_Handler_Reference;
   --  Simple wrapper around the GNATCOLL.Refcount API to create event handler
   --  references.

   --------------------
   -- Unit providers --
   --------------------

   type Unit_Provider_Interface is interface;
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

   function Get_Unit_Filename
     (Provider : Unit_Provider_Interface;
      Name     : Text_Type;
      Kind     : Analysis_Unit_Kind) return String is abstract;
   --  Return the filename corresponding to the given unit name/unit kind.
   --  Raise a ``Property_Error`` if the given unit name is not valid.

   procedure Get_Unit_Location
     (Provider       : Unit_Provider_Interface;
      Name           : Text_Type;
      Kind           : Analysis_Unit_Kind;
      Filename       : in out Ada.Strings.Unbounded.Unbounded_String;
      PLE_Root_Index : in out Natural) is null;
   --  Like ``Get_Unit_Filename``, but return both the source file that
   --  ``Name``/``Kind`` designate (in ``Filename``) and the index of the PLE
   --  root inside that unit (in ``PLE_Root_Index``). If ``PLE_Root_Index`` is
   --  left to 0 upon return, discard the result and switch to the PLE root
   --  unaware ``Get_Unit_Filename`` function.

   function Get_Unit
     (Provider : Unit_Provider_Interface;
      Context  : Analysis_Context'Class;
      Name     : Text_Type;
      Kind     : Analysis_Unit_Kind;
      Charset  : String := "";
      Reparse  : Boolean := False) return Analysis_Unit'Class is abstract;
   --  Fetch and return the analysis unit referenced by the given unit name.
   --  Raise a ``Property_Error`` if the given unit name is not valid.

   procedure Get_Unit_And_PLE_Root
     (Provider       : Unit_Provider_Interface;
      Context        : Analysis_Context'Class;
      Name           : Text_Type;
      Kind           : Analysis_Unit_Kind;
      Charset        : String := "";
      Reparse        : Boolean := False;
      Unit           : in out Analysis_Unit'Class;
      PLE_Root_Index : in out Natural) is null;
   --  Like ``Get_Unit``, but return both the analysis unit that
   --  ``Name``/``Kind`` designate (in ``Unit``) and the index of the PLE root
   --  inside that unit (in ``PLE_Root_Index``). If ``PLE_Root_Index`` is left
   --  to 0 upon return, discard the result and switch to the PLE root unaware
   --  ``Get_Unit`` function.

   procedure Release (Provider : in out Unit_Provider_Interface) is abstract;
   --  Actions to perform when releasing resources associated to Provider

   procedure Do_Release (Provider : in out Unit_Provider_Interface'Class);
   --  Helper for the instantiation below

   package Unit_Provider_References is new GNATCOLL.Refcount.Shared_Pointers
     (Unit_Provider_Interface'Class, Do_Release);

   subtype Unit_Provider_Reference is Unit_Provider_References.Ref;
   No_Unit_Provider_Reference : Unit_Provider_Reference renames
      Unit_Provider_References.Null_Ref;

   function Create_Unit_Provider_Reference
     (Provider : Unit_Provider_Interface'Class) return Unit_Provider_Reference;
   --  Simple wrapper around the GNATCOLL.Refcount API to create unit provider
   --  references.

   ---------------------------------
   -- Analysis context primitives --
   ---------------------------------

   function Create_Context
     (Charset       : String := Default_Charset;
      File_Reader   : File_Reader_Reference := No_File_Reader_Reference;
      Unit_Provider : Unit_Provider_Reference := No_Unit_Provider_Reference;
      Event_Handler : Event_Handler_Reference := No_Event_Handler_Ref;
      With_Trivia   : Boolean := True;
      Tab_Stop      : Positive := 8)
      return Analysis_Context;
   --  Create a new analysis context.
   --
   --  ``Charset`` will be used as a default charset to decode input sources in
   --  analysis units. Please see ``GNATCOLL.Iconv`` for several supported
   --  charsets. Be careful: passing an unsupported charset is not guaranteed
   --  to raise an error here. If no charset is provided, ``"utf-8"`` is the
   --  default.
   --
   --  .. TODO: Passing an unsupported charset here is not guaranteed to raise
   --     an error right here, but this would be really helpful for users.
   --
   --  When ``With_Trivia`` is true, the parsed analysis units will contain
   --  trivias.
   --
   --  If provided, ``File_Reader`` will be used to fetch the contents of
   --  source files instead of the default, which is to just read it from the
   --  filesystem and decode it using the regular charset rules. Note that if
   --  provided, all parsing APIs that provide a buffer are forbidden, and any
   --  use of the rewriting API with the returned context is rejected.
   --
   --  If provided, ``Unit_Provider`` will be used to query the file name that
   --  corresponds to a unit reference during semantic analysis. If it is
   --  ``null``, the default one is used instead.
   --
   --  If provided, ``Event_Handler`` will be notified when various events
   --  happen.
   --
   --  ``Tab_Stop`` is a positive number to describe the effect of tabulation
   --  characters on the column number in source files.
   --% belongs-to: Analysis_Context

   function Has_Unit
     (Context       : Analysis_Context'Class;
      Unit_Filename : String) return Boolean;
   --  Return whether ``Context`` contains a unit correponding to
   --  ``Unit_Filename``.

   function Get_From_File
     (Context  : Analysis_Context'Class;
      Filename : String;
      Charset  : String := "";
      Reparse  : Boolean := False;
      Rule     : Grammar_Rule := Default_Grammar_Rule) return Analysis_Unit;
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
   --
   --  It is invalid to pass ``True`` to ``Reparse`` if a rewriting context is
   --  active.

   function Get_From_Buffer
     (Context  : Analysis_Context'Class;
      Filename : String;
      Charset  : String := "";
      Buffer   : String;
      Rule     : Grammar_Rule := Default_Grammar_Rule) return Analysis_Unit;
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
   --
   --  Calling this is invalid if a rewriting context is active.

   function Get_From_Buffer
     (Context  : Analysis_Context'Class;
      Filename : String;
      Charset  : String := "";
      Buffer   : Ada.Strings.Unbounded.Unbounded_String;
      Rule     : Grammar_Rule := Default_Grammar_Rule) return Analysis_Unit;
   --  Likewise, but working on an unbounded string

   function Get_With_Error
     (Context  : Analysis_Context'Class;
      Filename : String;
      Error    : Text_Type;
      Charset  : String := "";
      Rule     : Grammar_Rule := Default_Grammar_Rule) return Analysis_Unit;
   --  If a Unit for ``Filename`` already exists, return it unchanged.
   --  Otherwise, create an empty analysis unit for ``Filename`` with a
   --  diagnostic that contains the ``Error`` message.


   function Unit_Provider
     (Context : Analysis_Context'Class) return Unit_Provider_Reference;
   --  Return the unit provider for ``Context``
   --
   --% belongs-to: Analysis_Context

   function Hash (Context : Analysis_Context) return Ada.Containers.Hash_Type;
   --  Return a hash for this context, to be used in hash tables.

   function Has_With_Trivia (Context : Analysis_Context'Class) return Boolean;
   --  Return whether ``Context`` keeps trivia when parsing units

   procedure Discard_Errors_In_Populate_Lexical_Env
     (Context : Analysis_Context'Class; Discard : Boolean);
   --  Debug helper. Set whether ``Property_Error`` exceptions raised in
   --  ``Populate_Lexical_Env`` should be discarded. They are by default.

   procedure Set_Logic_Resolution_Timeout
     (Context : Analysis_Context'Class; Timeout : Natural);
   --  If ``Timeout`` is greater than zero, set a timeout for the resolution of
   --  logic equations. The unit is the number of steps in ANY/ALL relations.
   --  If ``Timeout`` is zero, disable the timeout. By default, the timeout is
   --  ``100 000`` steps.

   procedure Set_Lookup_Cache_Mode (Mode : Lookup_Cache_Kind);
   --  Set the lexical environments lookup cache mode according to ``Mode``.
   --  Note: Mainly meant for debugging the default mode.

   function Has_Rewriting_Handle
     (Context : Analysis_Context'Class) return Boolean;
   --  Return whether ``Context`` has a rewriting handler (see
   --  ``Librflxlang.Rewriting``), i.e. whether it is in the process of
   --  rewriting. If true, this means that the set of currently loaded analysis
   --  units is frozen until the rewriting process is done.

   function Get_Symbol_Table
     (Context : Analysis_Context'Class) return Symbol_Table;
   --  Return the symbol table attached to this context. Useful for users
   --  needing their own symbolization and wanting to share it with their
   --  language frontend.
   --
   --  WARNING: EXPERIMENTAL & UNSAFE - The Symbol_Table exposes an unsafe API,
   --  that might be subject to some changes, use with caution.

   ------------------------------
   -- Analysis unit primitives --
   ------------------------------

   function Context (Unit : Analysis_Unit'Class) return Analysis_Context;
   --  Return the context that owns this unit.

   function Hash (Unit : Analysis_Unit) return Ada.Containers.Hash_Type;
   --  Return a hash for this unit, to be used in hash tables.

   procedure Reparse (Unit : Analysis_Unit'Class; Charset : String := "");
   --  Reparse an analysis unit from the associated file.
   --
   --  Use ``Charset`` in order to decode the source. If ``Charset`` is empty
   --  then use the context's default charset.
   --
   --  If any failure occurs, such as decoding, lexing or parsing failure,
   --  diagnostic are emitted to explain what happened.

   procedure Reparse
     (Unit    : Analysis_Unit'Class;
      Charset : String := "";
      Buffer  : String);
   --  Reparse an analysis unit from a buffer.
   --
   --  Use ``Charset`` in order to decode the source. If ``Charset`` is empty
   --  then use the context's default charset.
   --
   --  If any failure occurs, such as decoding, lexing or parsing failure,
   --  diagnostic are emitted to explain what happened.

   procedure Populate_Lexical_Env
     (Unit : Analysis_Unit'Class
     );
   --  Create lexical environments for this analysis unit, according to the
   --  specifications given in the language spec.
   --
   --  If not done before, it will be automatically called during semantic
   --  analysis. Calling it before enables one to control where the latency
   --  occurs.
   --
   --  Depending on whether errors are discarded (see
   --  ``Discard_Errors_In_Populate_Lexical_Env``), raise a ``Property_Error``
   --  on failure.

   function Get_Filename (Unit : Analysis_Unit'Class) return String;
   --  Return the filename this unit is associated to.

   function Get_Charset (Unit : Analysis_Unit'Class) return String;
   --  Return the charset that was used to parse Unit

   function Has_Diagnostics (Unit : Analysis_Unit'Class) return Boolean;
   --  Return whether this unit has associated diagnostics.

   function Diagnostics (Unit : Analysis_Unit'Class) return Diagnostics_Array;
   --  Return an array that contains the diagnostics associated to this unit.

   function Format_GNU_Diagnostic
     (Unit : Analysis_Unit'Class; D : Diagnostic) return String;
   --  Format a diagnostic in a GNU fashion. See
   --  <https://www.gnu.org/prep/standards/html_node/Errors.html>.

   pragma Warnings (Off, "defined after private extension");
   function Root (Unit : Analysis_Unit'Class) return R_F_L_X_Node;
   --  Return the root node for this unit, or ``null`` if there is none.
   pragma Warnings (On, "defined after private extension");

   function First_Token (Unit : Analysis_Unit'Class) return Token_Reference;
   --  Return a reference to the first token scanned in this unit.

   function Last_Token (Unit : Analysis_Unit'Class) return Token_Reference;
   --  Return a reference to the last token scanned in this unit.

   function Token_Count (Unit : Analysis_Unit'Class) return Natural;
   --  Return the number of tokens in this unit.

   function Trivia_Count (Unit : Analysis_Unit'Class) return Natural;
   --  Return the number of trivias in this unit. This is 0 for units that were
   --  parsed with trivia analysis disabled.

   function Unit (Token : Token_Reference) return Analysis_Unit;
   --  Return the analysis unit that owns ``Token``

   function Text (Unit : Analysis_Unit'Class) return Text_Type;
   --  Return the source buffer associated to this unit.

   function Lookup_Token
     (Unit : Analysis_Unit'Class; Sloc : Source_Location)
      return Token_Reference;
   --  Look for a token in this unit that contains the given source location.
   --  If this falls before the first token, return the first token. If this
   --  falls between two tokens, return the token that appears before. If this
   --  falls after the last token, return the last token. If there is no token
   --  in this unit, return no token.

   procedure Dump_Lexical_Env (Unit : Analysis_Unit'Class);
   --  Debug helper: output the lexical envs for the given analysis unit.

   procedure Trigger_Envs_Debug (Is_Active : Boolean);
   --  Debug helper: activate debug traces for lexical envs lookups

   procedure Print (Unit : Analysis_Unit'Class; Show_Slocs : Boolean := True);
   --  Debug helper: output the AST and eventual diagnostic for this unit on
   --  standard output.
   --
   --  If Show_Slocs, include AST nodes' source locations in the output.

   procedure PP_Trivia (Unit : Analysis_Unit'Class);
   --  Debug helper: output a minimal AST with mixed trivias

   overriding function Get_Line
     (Unit : Analysis_Unit; Line_Number : Positive) return Text_Type;
   --  Return the line of text at line number ``Line_Number``

   type Child_Record (Kind : Child_Or_Trivia := Child) is record
      case Kind is
         when Child =>
            Node : R_F_L_X_Node;
         when Trivia =>
            Trivia : Token_Reference;
      end case;
   end record;
   --  Variant that holds either an AST node or a token

   type Children_Array is private
      with Iterable => (First       => First,
                        Next        => Next,
                        Has_Element => Has_Element,
                        Element     => Element,
                        Last        => Last,
                        Previous    => Previous);
   --  This iterable type holds an array of ``Child`` or ``Trivia`` nodes

   function First (Self : Children_Array) return Natural;
   --  Return the first child or trivia cursor corresponding to the children
   --  array. Helper for the ``Iterable`` aspect.

   function Last (Self : Children_Array) return Natural;
   --  Return the last child or trivia cursor corresponding to the children
   --  array. Helper for the ``Iterable`` aspect.

   function Next (Self : Children_Array; Pos  : Natural) return Natural;
   --  Return the child or trivia cursor that follows ``Self`` in the children
   --  array. Helper for the ``Iterable`` aspect.

   function Previous (Self : Children_Array; Pos  : Natural) return Natural;
   --  Return the child or trivia cursor that follows ``Self`` in the children
   --  array. Helper for the ``Iterable`` aspect.

   function Has_Element (Self : Children_Array; Pos  : Natural) return Boolean;
   --  Return if ``Pos`` is in ``Self``'s iteration range. Helper for the
   --  ``Iterable`` aspect.

   function Element
     (Self : Children_Array;
      Pos  : Natural) return Child_Record;
   --  Return the child of trivia node at position ``Pos`` in ``Self``. Helper
   --  for the ``Iterable`` aspect.

   function Children_And_Trivia
     (Node : R_F_L_X_Node'Class) return Children_Array;
   --  Return the children of this node interleaved with Trivia token nodes, so
   --  that:
   --
   --  - Every trivia contained between ``Node.Start_Token`` and
   --    ``Node.End_Token - 1`` will be part of the returned array.
   --
   --  - Nodes and trivias will be lexically ordered.

   ---------------------
   -- Composite types --
   ---------------------

            
   type R_F_L_X_Node_Array is
      array (Positive range <>) of R_F_L_X_Node;



   --------------------
   -- Token Iterator --
   --------------------

   type Token_Iterator is private
      with Iterable => (First       => First_Token,
                        Next        => Next_Token,
                        Has_Element => Has_Element,
                        Element     => Element);
   --  Allow iteration on a range of tokens corresponding to a node

   function First_Token (Self : Token_Iterator) return Token_Reference;
   --  Return the first token corresponding to the node

   function Next_Token
     (Self : Token_Iterator; Tok : Token_Reference) return Token_Reference;
   --  Return the token that follows Tok in the token stream

   function Has_Element
     (Self : Token_Iterator; Tok : Token_Reference) return Boolean;
   --  Return if Tok is in Self's iteration range

   function Element
     (Self : Token_Iterator; Tok : Token_Reference) return Token_Reference;
   --  Identity function: helper for the Iterable aspect

   -------------------------
   -- AST Node primitives --
   -------------------------

   function Kind
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node_Kind_Type;
   function Kind_Name (Node : R_F_L_X_Node'Class) return String;
   --  Return the concrete kind for Node

   pragma Warnings (Off, "defined after private extension");




         
   function Parent
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node;
   --  Return the syntactic parent for this node. Return null for the root
   --  node.
   --% belongs-to: R_F_L_X_Node

         
   function Parents
     (Node : R_F_L_X_Node'Class;
      With_Self : Boolean := True) return R_F_L_X_Node_Array;
   --  Return an array that contains the lexical parents, this node included
   --  iff ``with_self`` is True. Nearer parents are first in the list.
   --% belongs-to: R_F_L_X_Node

         
   function Children
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node_Array;
   --  Return an array that contains the direct lexical children.
   --
   --  .. warning:: This constructs a whole array every-time you call it, and
   --     as such is less efficient than calling the ``Child`` built-in.
   --% belongs-to: R_F_L_X_Node

         
   function Token_Start
     (Node : R_F_L_X_Node'Class) return Token_Reference;
   --  Return the first token used to parse this node.
   --% belongs-to: R_F_L_X_Node

         
   function Token_End
     (Node : R_F_L_X_Node'Class) return Token_Reference;
   --  Return the last token used to parse this node.
   --% belongs-to: R_F_L_X_Node

         
   function Child_Index
     (Node : R_F_L_X_Node'Class) return Integer;
   --  Return the 0-based index for Node in its parent's children.
   --% belongs-to: R_F_L_X_Node

         
   function Previous_Sibling
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node;
   --  Return the node's previous sibling, or null if there is no such sibling.
   --% belongs-to: R_F_L_X_Node

         
   function Next_Sibling
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node;
   --  Return the node's next sibling, or null if there is no such sibling.
   --% belongs-to: R_F_L_X_Node

         
   function Unit
     (Node : R_F_L_X_Node'Class) return Analysis_Unit;
   --  Return the analysis unit owning this node.
   --% belongs-to: R_F_L_X_Node

         
   function Is_Ghost
     (Node : R_F_L_X_Node'Class) return Boolean;
   --  Return whether the node is a ghost.
   --
   --  Unlike regular nodes, ghost nodes cover no token in the input source:
   --  they are logically located instead between two tokens. Both the
   --  ``token_start`` and the ``token_end`` of all ghost nodes is the token
   --  right after this logical position.
   --% belongs-to: R_F_L_X_Node

         
   function Full_Sloc_Image
     (Node : R_F_L_X_Node'Class) return Text_Type;
   --  Return a string containing the filename + the sloc in GNU conformant
   --  format. Useful to create diagnostics from a node.
   --% belongs-to: R_F_L_X_Node




















         
   

   function F_Identifier
     (Node : Aspect'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Aspect


         
   

   function F_Value
     (Node : Aspect'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Aspect










         function List_Child
           (Node : Aspect_List'Class; Index : Positive)
            return Aspect;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Aspect_List_First (Node : Aspect_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Aspect_List_Next
           (Node : Aspect_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Aspect_List_Has_Element
           (Node : Aspect_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Aspect_List_Element
           (Node : Aspect_List; Cursor : Positive)
            return Aspect'Class;
         --  Implementation detail for the Iterable aspect











         
   

   function F_Identifier
     (Node : Assignment'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Assignment


         
   

   function F_Expression
     (Node : Assignment'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Assignment























































































         
   

   function F_Expression
     (Node : Attribute'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Binding`, :ada:ref:`Call`, :ada:ref:`Case_Expression`,
   --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
   --  :ada:ref:`Message_Aggregate`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Attribute


         
   

   function F_Kind
     (Node : Attribute'Class) return Attr;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Attribute

      function F_Kind
        (Node : Attribute'Class) return Rflx_Attr;
      --% belongs-to: Attribute






         
   

   function F_Identifier
     (Node : Attribute_Statement'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Attribute_Statement


         
   

   function F_Attr
     (Node : Attribute_Statement'Class) return Attr_Stmt;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Attribute_Statement

      function F_Attr
        (Node : Attribute_Statement'Class) return Rflx_Attr_Stmt;
      --% belongs-to: Attribute_Statement

         
   

   function F_Expression
     (Node : Attribute_Statement'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Attribute_Statement















         function List_Child
           (Node : Base_Checksum_Val_List'Class; Index : Positive)
            return Base_Checksum_Val;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Base_Checksum_Val_List_First (Node : Base_Checksum_Val_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Base_Checksum_Val_List_Next
           (Node : Base_Checksum_Val_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Base_Checksum_Val_List_Has_Element
           (Node : Base_Checksum_Val_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Base_Checksum_Val_List_Element
           (Node : Base_Checksum_Val_List; Cursor : Positive)
            return Base_Checksum_Val'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Left
     (Node : Bin_Op'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Bin_Op


         
   

   function F_Op
     (Node : Bin_Op'Class) return Op;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Bin_Op

      function F_Op
        (Node : Bin_Op'Class) return Rflx_Op;
      --% belongs-to: Bin_Op

         
   

   function F_Right
     (Node : Bin_Op'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Bin_Op







         
   

   function F_Expression
     (Node : Binding'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Binding`, :ada:ref:`Call`, :ada:ref:`Case_Expression`,
   --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
   --  :ada:ref:`Message_Aggregate`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Binding


         
   

   function F_Bindings
     (Node : Binding'Class) return Term_Assoc_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Binding












         
   

   function F_Byte_Order
     (Node : Byte_Order_Aspect'Class) return Byte_Order_Type;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Byte_Order_Aspect

      function F_Byte_Order
        (Node : Byte_Order_Aspect'Class) return Rflx_Byte_Order_Type;
      --% belongs-to: Byte_Order_Aspect





















         
   

   function F_Identifier
     (Node : Call'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Call


         
   

   function F_Arguments
     (Node : Call'Class) return Expr_List;
   --  This field contains a list that itself contains one of the following
   --  nodes: :ada:ref:`Attribute`, :ada:ref:`Bin_Op`, :ada:ref:`Binding`,
   --  :ada:ref:`Call`, :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Call







         
   

   function F_Expression
     (Node : Case_Expression'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Case_Expression


         
   

   function F_Choices
     (Node : Case_Expression'Class) return Choice_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Case_Expression










         function List_Child
           (Node : Channel_Attribute_List'Class; Index : Positive)
            return Channel_Attribute;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Channel_Attribute_List_First (Node : Channel_Attribute_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Channel_Attribute_List_Next
           (Node : Channel_Attribute_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Channel_Attribute_List_Has_Element
           (Node : Channel_Attribute_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Channel_Attribute_List_Element
           (Node : Channel_Attribute_List; Cursor : Positive)
            return Channel_Attribute'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Associations
     (Node : Checksum_Aspect'Class) return Checksum_Assoc_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Checksum_Aspect







         
   

   function F_Identifier
     (Node : Checksum_Assoc'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Checksum_Assoc


         
   

   function F_Covered_Fields
     (Node : Checksum_Assoc'Class) return Base_Checksum_Val_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Checksum_Assoc





         function List_Child
           (Node : Checksum_Assoc_List'Class; Index : Positive)
            return Checksum_Assoc;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Checksum_Assoc_List_First (Node : Checksum_Assoc_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Checksum_Assoc_List_Next
           (Node : Checksum_Assoc_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Checksum_Assoc_List_Has_Element
           (Node : Checksum_Assoc_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Checksum_Assoc_List_Element
           (Node : Checksum_Assoc_List; Cursor : Positive)
            return Checksum_Assoc'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Data
     (Node : Checksum_Val'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Checksum_Val







         
   

   function F_First
     (Node : Checksum_Value_Range'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Checksum_Value_Range


         
   

   function F_Last
     (Node : Checksum_Value_Range'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Checksum_Value_Range







         
   

   function F_Selectors
     (Node : Choice'Class) return R_F_L_X_Node_List;
   --  This field contains a list that itself contains one of the following
   --  nodes: :ada:ref:`I_D`, :ada:ref:`Numeric_Literal`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Choice


         
   

   function F_Expression
     (Node : Choice'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Choice





         function List_Child
           (Node : Choice_List'Class; Index : Positive)
            return Choice;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Choice_List_First (Node : Choice_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Choice_List_Next
           (Node : Choice_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Choice_List_Has_Element
           (Node : Choice_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Choice_List_Element
           (Node : Choice_List; Cursor : Positive)
            return Choice'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Iterator
     (Node : Comprehension'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Comprehension


         
   

   function F_Sequence
     (Node : Comprehension'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Comprehension


         
   

   function F_Condition
     (Node : Comprehension'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Comprehension


         
   

   function F_Selector
     (Node : Comprehension'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Comprehension












         
   

   function F_Left
     (Node : Concatenation'Class) return Sequence_Literal;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Concatenation


         
   

   function F_Right
     (Node : Concatenation'Class) return Sequence_Literal;
   --  This field can contain one of the following nodes:
   --  :ada:ref:`Sequence_Aggregate`, :ada:ref:`String_Literal`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Concatenation







         
   

   function F_Target
     (Node : Transition'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Transition


         
   

   function F_Description
     (Node : Transition'Class) return Description;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Transition







         
   

   function F_Condition
     (Node : Conditional_Transition'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Conditional_Transition





         function List_Child
           (Node : Conditional_Transition_List'Class; Index : Positive)
            return Conditional_Transition;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Conditional_Transition_List_First (Node : Conditional_Transition_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Conditional_Transition_List_Next
           (Node : Conditional_Transition_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Conditional_Transition_List_Has_Element
           (Node : Conditional_Transition_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Conditional_Transition_List_Element
           (Node : Conditional_Transition_List; Cursor : Positive)
            return Conditional_Transition'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Item
     (Node : Context_Item'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Context_Item





         function List_Child
           (Node : Context_Item_List'Class; Index : Positive)
            return Context_Item;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Context_Item_List_First (Node : Context_Item_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Context_Item_List_Next
           (Node : Context_Item_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Context_Item_List_Has_Element
           (Node : Context_Item_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Context_Item_List_Element
           (Node : Context_Item_List; Cursor : Positive)
            return Context_Item'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Target_Identifier
     (Node : Conversion'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Conversion


         
   

   function F_Argument
     (Node : Conversion'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Conversion










         function List_Child
           (Node : Declaration_List'Class; Index : Positive)
            return Declaration;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Declaration_List_First (Node : Declaration_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Declaration_List_Next
           (Node : Declaration_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Declaration_List_Has_Element
           (Node : Declaration_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Declaration_List_Element
           (Node : Declaration_List; Cursor : Positive)
            return Declaration'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Content
     (Node : Description'Class) return String_Literal;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Description







         
   

   function F_Identifier
     (Node : Element_Value_Assoc'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Element_Value_Assoc


         
   

   function F_Literal
     (Node : Element_Value_Assoc'Class) return Numeric_Literal;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Element_Value_Assoc





         function List_Child
           (Node : Element_Value_Assoc_List'Class; Index : Positive)
            return Element_Value_Assoc;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Element_Value_Assoc_List_First (Node : Element_Value_Assoc_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Element_Value_Assoc_List_Next
           (Node : Element_Value_Assoc_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Element_Value_Assoc_List_Has_Element
           (Node : Element_Value_Assoc_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Element_Value_Assoc_List_Element
           (Node : Element_Value_Assoc_List; Cursor : Positive)
            return Element_Value_Assoc'Class;
         --  Implementation detail for the Iterable aspect











         
   

   function F_Elements
     (Node : Enumeration_Type_Def'Class) return Enumeration_Def;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Enumeration_Type_Def


         
   

   function F_Aspects
     (Node : Enumeration_Type_Def'Class) return Aspect_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Enumeration_Type_Def





         function List_Child
           (Node : Expr_List'Class; Index : Positive)
            return Expr;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Expr_List_First (Node : Expr_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Expr_List_Next
           (Node : Expr_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Expr_List_Has_Element
           (Node : Expr_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Expr_List_Element
           (Node : Expr_List; Cursor : Positive)
            return Expr'Class;
         --  Implementation detail for the Iterable aspect











         
   

   function F_Identifier
     (Node : Formal_Channel_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Formal_Channel_Decl


         
   

   function F_Parameters
     (Node : Formal_Channel_Decl'Class) return Channel_Attribute_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Formal_Channel_Decl





         function List_Child
           (Node : Formal_Decl_List'Class; Index : Positive)
            return Formal_Decl;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Formal_Decl_List_First (Node : Formal_Decl_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Formal_Decl_List_Next
           (Node : Formal_Decl_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Formal_Decl_List_Has_Element
           (Node : Formal_Decl_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Formal_Decl_List_Element
           (Node : Formal_Decl_List; Cursor : Positive)
            return Formal_Decl'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Identifier
     (Node : Formal_Function_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Formal_Function_Decl


         
   

   function F_Parameters
     (Node : Formal_Function_Decl'Class) return Parameters;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Formal_Function_Decl


         
   

   function F_Return_Type_Identifier
     (Node : Formal_Function_Decl'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Formal_Function_Decl







         
   

   function F_Package
     (Node : I_D'Class) return Unqualified_I_D;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: I_D


         
   

   function F_Name
     (Node : I_D'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: I_D















         function List_Child
           (Node : Local_Decl_List'Class; Index : Positive)
            return Local_Decl;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Local_Decl_List_First (Node : Local_Decl_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Local_Decl_List_Next
           (Node : Local_Decl_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Local_Decl_List_Has_Element
           (Node : Local_Decl_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Local_Decl_List_Element
           (Node : Local_Decl_List; Cursor : Positive)
            return Local_Decl'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Identifier
     (Node : Message_Aggregate'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Aggregate


         
   

   function F_Values
     (Node : Message_Aggregate'Class) return Base_Aggregate;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Aggregate







         
   

   function F_Identifier
     (Node : Message_Aggregate_Association'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Aggregate_Association


         
   

   function F_Expression
     (Node : Message_Aggregate_Association'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Aggregate_Association





         function List_Child
           (Node : Message_Aggregate_Association_List'Class; Index : Positive)
            return Message_Aggregate_Association;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Message_Aggregate_Association_List_First (Node : Message_Aggregate_Association_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Message_Aggregate_Association_List_Next
           (Node : Message_Aggregate_Association_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Message_Aggregate_Association_List_Has_Element
           (Node : Message_Aggregate_Association_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Message_Aggregate_Association_List_Element
           (Node : Message_Aggregate_Association_List; Cursor : Positive)
            return Message_Aggregate_Association'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Associations
     (Node : Message_Aggregate_Associations'Class) return Message_Aggregate_Association_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Aggregate_Associations





         function List_Child
           (Node : Message_Aspect_List'Class; Index : Positive)
            return Message_Aspect;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Message_Aspect_List_First (Node : Message_Aspect_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Message_Aspect_List_Next
           (Node : Message_Aspect_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Message_Aspect_List_Has_Element
           (Node : Message_Aspect_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Message_Aspect_List_Element
           (Node : Message_Aspect_List; Cursor : Positive)
            return Message_Aspect'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Identifier
     (Node : Message_Field'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field


         
   

   function F_Type_Identifier
     (Node : Message_Field'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field


         
   

   function F_Type_Arguments
     (Node : Message_Field'Class) return Type_Argument_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field


         
   

   function F_Aspects
     (Node : Message_Field'Class) return Aspect_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field


         
   

   function F_Condition
     (Node : Message_Field'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Message_Field


         
   

   function F_Thens
     (Node : Message_Field'Class) return Then_Node_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field







         
   

   function F_Message
     (Node : Message_Field_Assignment'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field_Assignment


         
   

   function F_Field
     (Node : Message_Field_Assignment'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field_Assignment


         
   

   function F_Expression
     (Node : Message_Field_Assignment'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Field_Assignment





         function List_Child
           (Node : Message_Field_List'Class; Index : Positive)
            return Message_Field;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Message_Field_List_First (Node : Message_Field_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Message_Field_List_Next
           (Node : Message_Field_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Message_Field_List_Has_Element
           (Node : Message_Field_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Message_Field_List_Element
           (Node : Message_Field_List; Cursor : Positive)
            return Message_Field'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Initial_Field
     (Node : Message_Fields'Class) return Null_Message_Field;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Message_Fields


         
   

   function F_Fields
     (Node : Message_Fields'Class) return Message_Field_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Fields







         
   

   function F_Message_Fields
     (Node : Message_Type_Def'Class) return Message_Fields;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Type_Def


         
   

   function F_Aspects
     (Node : Message_Type_Def'Class) return Message_Aspect_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Message_Type_Def







         
   

   function F_Mod
     (Node : Modular_Type_Def'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Modular_Type_Def







         
   

   function F_Elements
     (Node : Named_Enumeration_Def'Class) return Element_Value_Assoc_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Named_Enumeration_Def







         
   

   function F_Data
     (Node : Negation'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Numeric_Literal`, :ada:ref:`Paren_Expression`,
   --  :ada:ref:`Quantified_Expression`, :ada:ref:`Select_Node`,
   --  :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Negation












         
   

   function F_Thens
     (Node : Null_Message_Field'Class) return Then_Node_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Null_Message_Field















         function List_Child
           (Node : Numeric_Literal_List'Class; Index : Positive)
            return Numeric_Literal;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Numeric_Literal_List_First (Node : Numeric_Literal_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Numeric_Literal_List_Next
           (Node : Numeric_Literal_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Numeric_Literal_List_Has_Element
           (Node : Numeric_Literal_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Numeric_Literal_List_Element
           (Node : Numeric_Literal_List; Cursor : Positive)
            return Numeric_Literal'Class;
         --  Implementation detail for the Iterable aspect



























































































         
   

   function F_Identifier
     (Node : Package_Node'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Package_Node


         
   

   function F_Declarations
     (Node : Package_Node'Class) return Declaration_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Package_Node


         
   

   function F_End_Identifier
     (Node : Package_Node'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Package_Node







         
   

   function F_Identifier
     (Node : Parameter'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Parameter


         
   

   function F_Type_Identifier
     (Node : Parameter'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Parameter





         function List_Child
           (Node : Parameter_List'Class; Index : Positive)
            return Parameter;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Parameter_List_First (Node : Parameter_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Parameter_List_Next
           (Node : Parameter_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Parameter_List_Has_Element
           (Node : Parameter_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Parameter_List_Element
           (Node : Parameter_List; Cursor : Positive)
            return Parameter'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Parameters
     (Node : Parameters'Class) return Parameter_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Parameters







         
   

   function F_Data
     (Node : Paren_Expression'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Paren_Expression







         
   

   function F_Elements
     (Node : Positional_Enumeration_Def'Class) return Unqualified_I_D_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Positional_Enumeration_Def







         
   

   function F_Operation
     (Node : Quantified_Expression'Class) return Quantifier;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Quantified_Expression

      function F_Operation
        (Node : Quantified_Expression'Class) return Rflx_Quantifier;
      --% belongs-to: Quantified_Expression

         
   

   function F_Parameter_Identifier
     (Node : Quantified_Expression'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Quantified_Expression


         
   

   function F_Iterable
     (Node : Quantified_Expression'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Quantified_Expression


         
   

   function F_Predicate
     (Node : Quantified_Expression'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Quantified_Expression





















         function R_F_L_X_Node_List_First (Node : R_F_L_X_Node_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function R_F_L_X_Node_List_Next
           (Node : R_F_L_X_Node_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function R_F_L_X_Node_List_Has_Element
           (Node : R_F_L_X_Node_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function R_F_L_X_Node_List_Element
           (Node : R_F_L_X_Node_List; Cursor : Positive)
            return R_F_L_X_Node'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_First
     (Node : Range_Type_Def'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Range_Type_Def


         
   

   function F_Last
     (Node : Range_Type_Def'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Range_Type_Def


         
   

   function F_Size
     (Node : Range_Type_Def'Class) return Aspect;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Range_Type_Def












         
   

   function F_Pdu
     (Node : Refinement_Decl'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Refinement_Decl


         
   

   function F_Field
     (Node : Refinement_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Refinement_Decl


         
   

   function F_Sdu
     (Node : Refinement_Decl'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Refinement_Decl


         
   

   function F_Condition
     (Node : Refinement_Decl'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Refinement_Decl







         
   

   function F_Identifier
     (Node : Renaming_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Renaming_Decl


         
   

   function F_Type_Identifier
     (Node : Renaming_Decl'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Renaming_Decl


         
   

   function F_Expression
     (Node : Renaming_Decl'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Renaming_Decl







         
   

   function F_Identifier
     (Node : Reset'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Reset


         
   

   function F_Associations
     (Node : Reset'Class) return Message_Aggregate_Association_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Reset







         
   

   function F_Expression
     (Node : Select_Node'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Binding`, :ada:ref:`Call`, :ada:ref:`Case_Expression`,
   --  :ada:ref:`Comprehension`, :ada:ref:`Conversion`,
   --  :ada:ref:`Message_Aggregate`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Select_Node


         
   

   function F_Selector
     (Node : Select_Node'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Select_Node







         
   

   function F_Values
     (Node : Sequence_Aggregate'Class) return Numeric_Literal_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Sequence_Aggregate







         
   

   function F_Element_Type
     (Node : Sequence_Type_Def'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Sequence_Type_Def







         
   

   function F_Parameters
     (Node : Session_Decl'Class) return Formal_Decl_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Session_Decl


         
   

   function F_Identifier
     (Node : Session_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Session_Decl


         
   

   function F_Declarations
     (Node : Session_Decl'Class) return Local_Decl_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Session_Decl


         
   

   function F_States
     (Node : Session_Decl'Class) return State_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Session_Decl


         
   

   function F_End_Identifier
     (Node : Session_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Session_Decl







         
   

   function F_Context_Clause
     (Node : Specification'Class) return Context_Item_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Specification


         
   

   function F_Package_Declaration
     (Node : Specification'Class) return Package_Node;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Specification







         
   

   function F_Identifier
     (Node : State'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State


         
   

   function F_Description
     (Node : State'Class) return Description;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: State


         
   

   function F_Body
     (Node : State'Class) return State_Body;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State







         
   

   function F_Declarations
     (Node : State_Body'Class) return Local_Decl_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State_Body


         
   

   function F_Actions
     (Node : State_Body'Class) return Statement_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State_Body


         
   

   function F_Conditional_Transitions
     (Node : State_Body'Class) return Conditional_Transition_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State_Body


         
   

   function F_Final_Transition
     (Node : State_Body'Class) return Transition;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State_Body


         
   

   function F_Exception_Transition
     (Node : State_Body'Class) return Transition;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: State_Body


         
   

   function F_End_Identifier
     (Node : State_Body'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: State_Body





         function List_Child
           (Node : State_List'Class; Index : Positive)
            return State;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function State_List_First (Node : State_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function State_List_Next
           (Node : State_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function State_List_Has_Element
           (Node : State_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function State_List_Element
           (Node : State_List; Cursor : Positive)
            return State'Class;
         --  Implementation detail for the Iterable aspect




         function List_Child
           (Node : Statement_List'Class; Index : Positive)
            return Statement;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Statement_List_First (Node : Statement_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Statement_List_Next
           (Node : Statement_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Statement_List_Has_Element
           (Node : Statement_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Statement_List_Element
           (Node : Statement_List; Cursor : Positive)
            return Statement'Class;
         --  Implementation detail for the Iterable aspect











         
   

   function F_Identifier
     (Node : Term_Assoc'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Term_Assoc


         
   

   function F_Expression
     (Node : Term_Assoc'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Term_Assoc





         function List_Child
           (Node : Term_Assoc_List'Class; Index : Positive)
            return Term_Assoc;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Term_Assoc_List_First (Node : Term_Assoc_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Term_Assoc_List_Next
           (Node : Term_Assoc_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Term_Assoc_List_Has_Element
           (Node : Term_Assoc_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Term_Assoc_List_Element
           (Node : Term_Assoc_List; Cursor : Positive)
            return Term_Assoc'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Target
     (Node : Then_Node'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Then_Node


         
   

   function F_Aspects
     (Node : Then_Node'Class) return Aspect_List;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Then_Node


         
   

   function F_Condition
     (Node : Then_Node'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Then_Node





         function List_Child
           (Node : Then_Node_List'Class; Index : Positive)
            return Then_Node;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Then_Node_List_First (Node : Then_Node_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Then_Node_List_Next
           (Node : Then_Node_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Then_Node_List_Has_Element
           (Node : Then_Node_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Then_Node_List_Element
           (Node : Then_Node_List; Cursor : Positive)
            return Then_Node'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Identifier
     (Node : Type_Argument'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Type_Argument


         
   

   function F_Expression
     (Node : Type_Argument'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Sequence_Literal`,
   --  :ada:ref:`Variable`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Type_Argument





         function List_Child
           (Node : Type_Argument_List'Class; Index : Positive)
            return Type_Argument;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Type_Argument_List_First (Node : Type_Argument_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Type_Argument_List_Next
           (Node : Type_Argument_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Type_Argument_List_Has_Element
           (Node : Type_Argument_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Type_Argument_List_Element
           (Node : Type_Argument_List; Cursor : Positive)
            return Type_Argument'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Identifier
     (Node : Type_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Type_Decl


         
   

   function F_Parameters
     (Node : Type_Decl'Class) return Parameters;
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Type_Decl


         
   

   function F_Definition
     (Node : Type_Decl'Class) return Type_Def;
   --  This field can contain one of the following nodes:
   --  :ada:ref:`Abstract_Message_Type_Def`, :ada:ref:`Enumeration_Type_Def`,
   --  :ada:ref:`Integer_Type_Def`, :ada:ref:`Sequence_Type_Def`,
   --  :ada:ref:`Type_Derivation_Def`
   --
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Type_Decl







         
   

   function F_Base
     (Node : Type_Derivation_Def'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Type_Derivation_Def










         function List_Child
           (Node : Unqualified_I_D_List'Class; Index : Positive)
            return Unqualified_I_D;
         --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has
         --  no such child.

         function Unqualified_I_D_List_First (Node : Unqualified_I_D_List) return Positive;
         --  Implementation detail for the Iterable aspect

         function Unqualified_I_D_List_Next
           (Node : Unqualified_I_D_List; Cursor : Positive) return Positive;
         --  Implementation detail for the Iterable aspect

         function Unqualified_I_D_List_Has_Element
           (Node : Unqualified_I_D_List; Cursor : Positive) return Boolean;
         --  Implementation detail for the Iterable aspect

         function Unqualified_I_D_List_Element
           (Node : Unqualified_I_D_List; Cursor : Positive)
            return Unqualified_I_D'Class;
         --  Implementation detail for the Iterable aspect






         
   

   function F_Identifier
     (Node : Variable'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Variable







         
   

   function F_Identifier
     (Node : Variable_Decl'Class) return Unqualified_I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Variable_Decl


         
   

   function F_Type_Identifier
     (Node : Variable_Decl'Class) return I_D;
   --  When there are no parsing errors, this field is never null.
   --% belongs-to: Variable_Decl


         
   

   function F_Initializer
     (Node : Variable_Decl'Class) return Expr;
   --  This field can contain one of the following nodes: :ada:ref:`Attribute`,
   --  :ada:ref:`Bin_Op`, :ada:ref:`Binding`, :ada:ref:`Call`,
   --  :ada:ref:`Case_Expression`, :ada:ref:`Comprehension`,
   --  :ada:ref:`Conversion`, :ada:ref:`Message_Aggregate`,
   --  :ada:ref:`Negation`, :ada:ref:`Numeric_Literal`,
   --  :ada:ref:`Paren_Expression`, :ada:ref:`Quantified_Expression`,
   --  :ada:ref:`Select_Node`, :ada:ref:`Sequence_Literal`, :ada:ref:`Variable`
   --
   --  This field may be null even when there are no parsing errors.
   --% belongs-to: Variable_Decl









   pragma Warnings (On, "defined after private extension");

   -------------------------------
   -- Tree traversal operations --
   -------------------------------

   function Children_Count
     (Node : R_F_L_X_Node'Class) return Natural;
   --  Return the number of children ``Node`` has

   function First_Child_Index
     (Node : R_F_L_X_Node'Class) return Natural;
   --  Return the index of the first child ``Node`` has

   function Last_Child_Index
     (Node : R_F_L_X_Node'Class) return Natural;
   --  Return the index of the last child ``Node`` has, or 0 if there is no
   --  child.

   pragma Warnings (Off, "defined after private extension");
   procedure Get_Child
     (Node            : R_F_L_X_Node'Class;
      Index           : Positive;
      Index_In_Bounds : out Boolean;
      Result          : out R_F_L_X_Node);
   --  Return the ``Index``'th child of node, storing it into ``Result``.
   --
   --  Child indexing is 1-based. Store in ``Index_In_Bounds`` whether ``Node``
   --  had such a child: if not (i.e. ``Index`` is out-of-bounds), set
   --  ``Result`` to a null node.

   function Child
     (Node  : R_F_L_X_Node'Class;
      Index : Positive)
      return R_F_L_X_Node;
   --  Return the ``Index``'th child of ``Node``, or null if ``Node`` has no
   --  such child.

   function First_Child
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node;
   --  Return the first child ``Node`` has, or ``No_R_F_L_X_Node``
   --  if there is none.

   function Last_Child
     (Node : R_F_L_X_Node'Class) return R_F_L_X_Node;
   --  Return the last child ``Node`` has, or ``No_R_F_L_X_Node`` if
   --  there is none.
   pragma Warnings (On, "defined after private extension");

   function Traverse
     (Node  : R_F_L_X_Node'Class;
      Visit : access function (Node : R_F_L_X_Node'Class)
                               return Visit_Status)
     return Visit_Status;
   --  Call ``Visit`` on ``Node`` and all its children, transitively. Calls
   --  happen in prefix order (i.e. top-down and left first). The traversal is
   --  controlled as follows by the result returned by Visit:
   --
   --  ``Into``
   --     The traversal continues normally with the syntactic children of the
   --     node just processed.
   --
   --  ``Over``
   --     The children of the node just processed are skipped and excluded from
   --     the traversal, but otherwise processing continues elsewhere in the
   --     tree.
   --
   --  ``Stop``
   --     The entire traversal is immediately abandoned, and the original call
   --     to ``Traverse`` returns ``Stop``.

   procedure Traverse
     (Node  : R_F_L_X_Node'Class;
      Visit : access function (Node : R_F_L_X_Node'Class)
                               return Visit_Status);
   --  This is the same as ``Traverse`` function except that no result is
   --  returned i.e. the ``Traverse`` function is called and the result is
   --  simply discarded.

   ----------------------------------------
   -- Source location-related operations --
   ----------------------------------------

   function Sloc_Range
     (Node : R_F_L_X_Node'Class) return Source_Location_Range;
   --  Return the source location range corresponding to the set of tokens from
   --  which Node was parsed.

   function Compare
     (Node : R_F_L_X_Node'Class;
      Sloc : Source_Location) return Relative_Position;
   --  Compare Sloc to the sloc range of Node

   pragma Warnings (Off, "defined after private extension");
   function Lookup
     (Node : R_F_L_X_Node'Class;
      Sloc : Source_Location) return R_F_L_X_Node;
   --  Look for the bottom-most AST node whose sloc range contains Sloc. Return
   --  it, or null if no such node was found.
   pragma Warnings (On, "defined after private extension");

   -----------------------
   -- Lexical utilities --
   -----------------------

   function Text (Node : R_F_L_X_Node'Class) return Text_Type;
   --  Return the source buffer slice corresponding to the text that spans
   --  between the first and the last tokens of this node.
   --
   --  Note that this returns the empty string for synthetic nodes.

   function Token_Range
     (Node : R_F_L_X_Node'Class) return Token_Iterator;
   --  Return an iterator on the range of tokens encompassed by Node

   


   -------------------
   -- Debug helpers --
   -------------------

   procedure Print
     (Node        : R_F_L_X_Node'Class;
      Show_Slocs  : Boolean := True;
      Line_Prefix : String := "");
   --  Debug helper: print to standard output Node and all its children.
   --
   --  If Show_Slocs, include AST nodes' source locations in the output.
   --
   --  Line_Prefix is prepended to each output line.

   procedure PP_Trivia
     (Node        : R_F_L_X_Node'Class;
      Line_Prefix : String := "");
   --  Debug helper: print to standard output Node and all its children along
   --  with the trivia associated to them. Line_Prefix is prepended to each
   --  output line.

   procedure Assign_Names_To_Logic_Vars (Node : R_F_L_X_Node'Class);
   --  Debug helper: Assign names to every logical variable in the root node,
   --  so that we can trace logical variables.

   --  The following As_* functions convert references to nodes from one type
   --  to another (R_F_L_X_Node can refer to any node type). They
   --  raise a Constraint_Error if the conversion is invalid.

   pragma Warnings (Off, "defined after private extension");
      function As_R_F_L_X_Node
        (Node : R_F_L_X_Node'Class) return R_F_L_X_Node;
      --% no-document: True
      function As_Abstract_I_D
        (Node : R_F_L_X_Node'Class) return Abstract_I_D;
      --% no-document: True
      function As_Type_Def
        (Node : R_F_L_X_Node'Class) return Type_Def;
      --% no-document: True
      function As_Abstract_Message_Type_Def
        (Node : R_F_L_X_Node'Class) return Abstract_Message_Type_Def;
      --% no-document: True
      function As_Aspect
        (Node : R_F_L_X_Node'Class) return Aspect;
      --% no-document: True
      function As_R_F_L_X_Node_Base_List
        (Node : R_F_L_X_Node'Class) return R_F_L_X_Node_Base_List;
      --% no-document: True
      function As_Aspect_List
        (Node : R_F_L_X_Node'Class) return Aspect_List;
      --% no-document: True
      function As_Statement
        (Node : R_F_L_X_Node'Class) return Statement;
      --% no-document: True
      function As_Assignment
        (Node : R_F_L_X_Node'Class) return Assignment;
      --% no-document: True
      function As_Attr
        (Node : R_F_L_X_Node'Class) return Attr;
      --% no-document: True
      function As_Attr_First
        (Node : R_F_L_X_Node'Class) return Attr_First;
      --% no-document: True
      function As_Attr_Has_Data
        (Node : R_F_L_X_Node'Class) return Attr_Has_Data;
      --% no-document: True
      function As_Attr_Head
        (Node : R_F_L_X_Node'Class) return Attr_Head;
      --% no-document: True
      function As_Attr_Last
        (Node : R_F_L_X_Node'Class) return Attr_Last;
      --% no-document: True
      function As_Attr_Opaque
        (Node : R_F_L_X_Node'Class) return Attr_Opaque;
      --% no-document: True
      function As_Attr_Present
        (Node : R_F_L_X_Node'Class) return Attr_Present;
      --% no-document: True
      function As_Attr_Size
        (Node : R_F_L_X_Node'Class) return Attr_Size;
      --% no-document: True
      function As_Attr_Stmt
        (Node : R_F_L_X_Node'Class) return Attr_Stmt;
      --% no-document: True
      function As_Attr_Stmt_Append
        (Node : R_F_L_X_Node'Class) return Attr_Stmt_Append;
      --% no-document: True
      function As_Attr_Stmt_Extend
        (Node : R_F_L_X_Node'Class) return Attr_Stmt_Extend;
      --% no-document: True
      function As_Attr_Stmt_Read
        (Node : R_F_L_X_Node'Class) return Attr_Stmt_Read;
      --% no-document: True
      function As_Attr_Stmt_Write
        (Node : R_F_L_X_Node'Class) return Attr_Stmt_Write;
      --% no-document: True
      function As_Attr_Valid
        (Node : R_F_L_X_Node'Class) return Attr_Valid;
      --% no-document: True
      function As_Attr_Valid_Checksum
        (Node : R_F_L_X_Node'Class) return Attr_Valid_Checksum;
      --% no-document: True
      function As_Expr
        (Node : R_F_L_X_Node'Class) return Expr;
      --% no-document: True
      function As_Attribute
        (Node : R_F_L_X_Node'Class) return Attribute;
      --% no-document: True
      function As_Attribute_Statement
        (Node : R_F_L_X_Node'Class) return Attribute_Statement;
      --% no-document: True
      function As_Base_Aggregate
        (Node : R_F_L_X_Node'Class) return Base_Aggregate;
      --% no-document: True
      function As_Base_Checksum_Val
        (Node : R_F_L_X_Node'Class) return Base_Checksum_Val;
      --% no-document: True
      function As_Base_Checksum_Val_List
        (Node : R_F_L_X_Node'Class) return Base_Checksum_Val_List;
      --% no-document: True
      function As_Bin_Op
        (Node : R_F_L_X_Node'Class) return Bin_Op;
      --% no-document: True
      function As_Binding
        (Node : R_F_L_X_Node'Class) return Binding;
      --% no-document: True
      function As_Message_Aspect
        (Node : R_F_L_X_Node'Class) return Message_Aspect;
      --% no-document: True
      function As_Byte_Order_Aspect
        (Node : R_F_L_X_Node'Class) return Byte_Order_Aspect;
      --% no-document: True
      function As_Byte_Order_Type
        (Node : R_F_L_X_Node'Class) return Byte_Order_Type;
      --% no-document: True
      function As_Byte_Order_Type_Highorderfirst
        (Node : R_F_L_X_Node'Class) return Byte_Order_Type_Highorderfirst;
      --% no-document: True
      function As_Byte_Order_Type_Loworderfirst
        (Node : R_F_L_X_Node'Class) return Byte_Order_Type_Loworderfirst;
      --% no-document: True
      function As_Call
        (Node : R_F_L_X_Node'Class) return Call;
      --% no-document: True
      function As_Case_Expression
        (Node : R_F_L_X_Node'Class) return Case_Expression;
      --% no-document: True
      function As_Channel_Attribute
        (Node : R_F_L_X_Node'Class) return Channel_Attribute;
      --% no-document: True
      function As_Channel_Attribute_List
        (Node : R_F_L_X_Node'Class) return Channel_Attribute_List;
      --% no-document: True
      function As_Checksum_Aspect
        (Node : R_F_L_X_Node'Class) return Checksum_Aspect;
      --% no-document: True
      function As_Checksum_Assoc
        (Node : R_F_L_X_Node'Class) return Checksum_Assoc;
      --% no-document: True
      function As_Checksum_Assoc_List
        (Node : R_F_L_X_Node'Class) return Checksum_Assoc_List;
      --% no-document: True
      function As_Checksum_Val
        (Node : R_F_L_X_Node'Class) return Checksum_Val;
      --% no-document: True
      function As_Checksum_Value_Range
        (Node : R_F_L_X_Node'Class) return Checksum_Value_Range;
      --% no-document: True
      function As_Choice
        (Node : R_F_L_X_Node'Class) return Choice;
      --% no-document: True
      function As_Choice_List
        (Node : R_F_L_X_Node'Class) return Choice_List;
      --% no-document: True
      function As_Comprehension
        (Node : R_F_L_X_Node'Class) return Comprehension;
      --% no-document: True
      function As_Sequence_Literal
        (Node : R_F_L_X_Node'Class) return Sequence_Literal;
      --% no-document: True
      function As_Concatenation
        (Node : R_F_L_X_Node'Class) return Concatenation;
      --% no-document: True
      function As_Transition
        (Node : R_F_L_X_Node'Class) return Transition;
      --% no-document: True
      function As_Conditional_Transition
        (Node : R_F_L_X_Node'Class) return Conditional_Transition;
      --% no-document: True
      function As_Conditional_Transition_List
        (Node : R_F_L_X_Node'Class) return Conditional_Transition_List;
      --% no-document: True
      function As_Context_Item
        (Node : R_F_L_X_Node'Class) return Context_Item;
      --% no-document: True
      function As_Context_Item_List
        (Node : R_F_L_X_Node'Class) return Context_Item_List;
      --% no-document: True
      function As_Conversion
        (Node : R_F_L_X_Node'Class) return Conversion;
      --% no-document: True
      function As_Declaration
        (Node : R_F_L_X_Node'Class) return Declaration;
      --% no-document: True
      function As_Declaration_List
        (Node : R_F_L_X_Node'Class) return Declaration_List;
      --% no-document: True
      function As_Description
        (Node : R_F_L_X_Node'Class) return Description;
      --% no-document: True
      function As_Element_Value_Assoc
        (Node : R_F_L_X_Node'Class) return Element_Value_Assoc;
      --% no-document: True
      function As_Element_Value_Assoc_List
        (Node : R_F_L_X_Node'Class) return Element_Value_Assoc_List;
      --% no-document: True
      function As_Enumeration_Def
        (Node : R_F_L_X_Node'Class) return Enumeration_Def;
      --% no-document: True
      function As_Enumeration_Type_Def
        (Node : R_F_L_X_Node'Class) return Enumeration_Type_Def;
      --% no-document: True
      function As_Expr_List
        (Node : R_F_L_X_Node'Class) return Expr_List;
      --% no-document: True
      function As_Formal_Decl
        (Node : R_F_L_X_Node'Class) return Formal_Decl;
      --% no-document: True
      function As_Formal_Channel_Decl
        (Node : R_F_L_X_Node'Class) return Formal_Channel_Decl;
      --% no-document: True
      function As_Formal_Decl_List
        (Node : R_F_L_X_Node'Class) return Formal_Decl_List;
      --% no-document: True
      function As_Formal_Function_Decl
        (Node : R_F_L_X_Node'Class) return Formal_Function_Decl;
      --% no-document: True
      function As_I_D
        (Node : R_F_L_X_Node'Class) return I_D;
      --% no-document: True
      function As_Integer_Type_Def
        (Node : R_F_L_X_Node'Class) return Integer_Type_Def;
      --% no-document: True
      function As_Local_Decl
        (Node : R_F_L_X_Node'Class) return Local_Decl;
      --% no-document: True
      function As_Local_Decl_List
        (Node : R_F_L_X_Node'Class) return Local_Decl_List;
      --% no-document: True
      function As_Message_Aggregate
        (Node : R_F_L_X_Node'Class) return Message_Aggregate;
      --% no-document: True
      function As_Message_Aggregate_Association
        (Node : R_F_L_X_Node'Class) return Message_Aggregate_Association;
      --% no-document: True
      function As_Message_Aggregate_Association_List
        (Node : R_F_L_X_Node'Class) return Message_Aggregate_Association_List;
      --% no-document: True
      function As_Message_Aggregate_Associations
        (Node : R_F_L_X_Node'Class) return Message_Aggregate_Associations;
      --% no-document: True
      function As_Message_Aspect_List
        (Node : R_F_L_X_Node'Class) return Message_Aspect_List;
      --% no-document: True
      function As_Message_Field
        (Node : R_F_L_X_Node'Class) return Message_Field;
      --% no-document: True
      function As_Message_Field_Assignment
        (Node : R_F_L_X_Node'Class) return Message_Field_Assignment;
      --% no-document: True
      function As_Message_Field_List
        (Node : R_F_L_X_Node'Class) return Message_Field_List;
      --% no-document: True
      function As_Message_Fields
        (Node : R_F_L_X_Node'Class) return Message_Fields;
      --% no-document: True
      function As_Message_Type_Def
        (Node : R_F_L_X_Node'Class) return Message_Type_Def;
      --% no-document: True
      function As_Modular_Type_Def
        (Node : R_F_L_X_Node'Class) return Modular_Type_Def;
      --% no-document: True
      function As_Named_Enumeration_Def
        (Node : R_F_L_X_Node'Class) return Named_Enumeration_Def;
      --% no-document: True
      function As_Negation
        (Node : R_F_L_X_Node'Class) return Negation;
      --% no-document: True
      function As_Null_Message_Aggregate
        (Node : R_F_L_X_Node'Class) return Null_Message_Aggregate;
      --% no-document: True
      function As_Null_Message_Field
        (Node : R_F_L_X_Node'Class) return Null_Message_Field;
      --% no-document: True
      function As_Null_Message_Type_Def
        (Node : R_F_L_X_Node'Class) return Null_Message_Type_Def;
      --% no-document: True
      function As_Numeric_Literal
        (Node : R_F_L_X_Node'Class) return Numeric_Literal;
      --% no-document: True
      function As_Numeric_Literal_List
        (Node : R_F_L_X_Node'Class) return Numeric_Literal_List;
      --% no-document: True
      function As_Op
        (Node : R_F_L_X_Node'Class) return Op;
      --% no-document: True
      function As_Op_Add
        (Node : R_F_L_X_Node'Class) return Op_Add;
      --% no-document: True
      function As_Op_And
        (Node : R_F_L_X_Node'Class) return Op_And;
      --% no-document: True
      function As_Op_Div
        (Node : R_F_L_X_Node'Class) return Op_Div;
      --% no-document: True
      function As_Op_Eq
        (Node : R_F_L_X_Node'Class) return Op_Eq;
      --% no-document: True
      function As_Op_Ge
        (Node : R_F_L_X_Node'Class) return Op_Ge;
      --% no-document: True
      function As_Op_Gt
        (Node : R_F_L_X_Node'Class) return Op_Gt;
      --% no-document: True
      function As_Op_In
        (Node : R_F_L_X_Node'Class) return Op_In;
      --% no-document: True
      function As_Op_Le
        (Node : R_F_L_X_Node'Class) return Op_Le;
      --% no-document: True
      function As_Op_Lt
        (Node : R_F_L_X_Node'Class) return Op_Lt;
      --% no-document: True
      function As_Op_Mod
        (Node : R_F_L_X_Node'Class) return Op_Mod;
      --% no-document: True
      function As_Op_Mul
        (Node : R_F_L_X_Node'Class) return Op_Mul;
      --% no-document: True
      function As_Op_Neq
        (Node : R_F_L_X_Node'Class) return Op_Neq;
      --% no-document: True
      function As_Op_Notin
        (Node : R_F_L_X_Node'Class) return Op_Notin;
      --% no-document: True
      function As_Op_Or
        (Node : R_F_L_X_Node'Class) return Op_Or;
      --% no-document: True
      function As_Op_Pow
        (Node : R_F_L_X_Node'Class) return Op_Pow;
      --% no-document: True
      function As_Op_Sub
        (Node : R_F_L_X_Node'Class) return Op_Sub;
      --% no-document: True
      function As_Package_Node
        (Node : R_F_L_X_Node'Class) return Package_Node;
      --% no-document: True
      function As_Parameter
        (Node : R_F_L_X_Node'Class) return Parameter;
      --% no-document: True
      function As_Parameter_List
        (Node : R_F_L_X_Node'Class) return Parameter_List;
      --% no-document: True
      function As_Parameters
        (Node : R_F_L_X_Node'Class) return Parameters;
      --% no-document: True
      function As_Paren_Expression
        (Node : R_F_L_X_Node'Class) return Paren_Expression;
      --% no-document: True
      function As_Positional_Enumeration_Def
        (Node : R_F_L_X_Node'Class) return Positional_Enumeration_Def;
      --% no-document: True
      function As_Quantified_Expression
        (Node : R_F_L_X_Node'Class) return Quantified_Expression;
      --% no-document: True
      function As_Quantifier
        (Node : R_F_L_X_Node'Class) return Quantifier;
      --% no-document: True
      function As_Quantifier_All
        (Node : R_F_L_X_Node'Class) return Quantifier_All;
      --% no-document: True
      function As_Quantifier_Some
        (Node : R_F_L_X_Node'Class) return Quantifier_Some;
      --% no-document: True
      function As_R_F_L_X_Node_List
        (Node : R_F_L_X_Node'Class) return R_F_L_X_Node_List;
      --% no-document: True
      function As_Range_Type_Def
        (Node : R_F_L_X_Node'Class) return Range_Type_Def;
      --% no-document: True
      function As_Readable
        (Node : R_F_L_X_Node'Class) return Readable;
      --% no-document: True
      function As_Refinement_Decl
        (Node : R_F_L_X_Node'Class) return Refinement_Decl;
      --% no-document: True
      function As_Renaming_Decl
        (Node : R_F_L_X_Node'Class) return Renaming_Decl;
      --% no-document: True
      function As_Reset
        (Node : R_F_L_X_Node'Class) return Reset;
      --% no-document: True
      function As_Select_Node
        (Node : R_F_L_X_Node'Class) return Select_Node;
      --% no-document: True
      function As_Sequence_Aggregate
        (Node : R_F_L_X_Node'Class) return Sequence_Aggregate;
      --% no-document: True
      function As_Sequence_Type_Def
        (Node : R_F_L_X_Node'Class) return Sequence_Type_Def;
      --% no-document: True
      function As_Session_Decl
        (Node : R_F_L_X_Node'Class) return Session_Decl;
      --% no-document: True
      function As_Specification
        (Node : R_F_L_X_Node'Class) return Specification;
      --% no-document: True
      function As_State
        (Node : R_F_L_X_Node'Class) return State;
      --% no-document: True
      function As_State_Body
        (Node : R_F_L_X_Node'Class) return State_Body;
      --% no-document: True
      function As_State_List
        (Node : R_F_L_X_Node'Class) return State_List;
      --% no-document: True
      function As_Statement_List
        (Node : R_F_L_X_Node'Class) return Statement_List;
      --% no-document: True
      function As_String_Literal
        (Node : R_F_L_X_Node'Class) return String_Literal;
      --% no-document: True
      function As_Term_Assoc
        (Node : R_F_L_X_Node'Class) return Term_Assoc;
      --% no-document: True
      function As_Term_Assoc_List
        (Node : R_F_L_X_Node'Class) return Term_Assoc_List;
      --% no-document: True
      function As_Then_Node
        (Node : R_F_L_X_Node'Class) return Then_Node;
      --% no-document: True
      function As_Then_Node_List
        (Node : R_F_L_X_Node'Class) return Then_Node_List;
      --% no-document: True
      function As_Type_Argument
        (Node : R_F_L_X_Node'Class) return Type_Argument;
      --% no-document: True
      function As_Type_Argument_List
        (Node : R_F_L_X_Node'Class) return Type_Argument_List;
      --% no-document: True
      function As_Type_Decl
        (Node : R_F_L_X_Node'Class) return Type_Decl;
      --% no-document: True
      function As_Type_Derivation_Def
        (Node : R_F_L_X_Node'Class) return Type_Derivation_Def;
      --% no-document: True
      function As_Unqualified_I_D
        (Node : R_F_L_X_Node'Class) return Unqualified_I_D;
      --% no-document: True
      function As_Unqualified_I_D_List
        (Node : R_F_L_X_Node'Class) return Unqualified_I_D_List;
      --% no-document: True
      function As_Variable
        (Node : R_F_L_X_Node'Class) return Variable;
      --% no-document: True
      function As_Variable_Decl
        (Node : R_F_L_X_Node'Class) return Variable_Decl;
      --% no-document: True
      function As_Writable
        (Node : R_F_L_X_Node'Class) return Writable;
      --% no-document: True

   function Hash
     (Node : R_F_L_X_Node) return Ada.Containers.Hash_Type;
   --  Generic hash function, to be used for nodes as keys in hash tables
   pragma Warnings (On, "defined after private extension");

private

   type Internal_Context_Access is
      access all Implementation.Analysis_Context_Type;
   type Internal_Unit_Access is
      access all Implementation.Analysis_Unit_Type;

   type Analysis_Context is new Ada.Finalization.Controlled with record
      Internal : Internal_Context_Access;
   end record;

   overriding procedure Initialize (Context : in out Analysis_Context);
   overriding procedure Adjust (Context : in out Analysis_Context);
   overriding procedure Finalize (Context : in out Analysis_Context);

   type Analysis_Unit is new Langkit_Support.Text.Text_Buffer_Ifc with record
      Internal : Internal_Unit_Access;

      Context : Analysis_Context;
      --  Keep a reference to the owning context so that the context lives as
      --  long as there is at least one reference to one of its units.
   end record;

   No_Analysis_Context : constant Analysis_Context :=
     (Ada.Finalization.Controlled with Internal => null);
   No_Analysis_Unit    : constant Analysis_Unit :=
     (Internal => null,
      Context  => (Ada.Finalization.Controlled with Internal => null));

   --------------------------
   -- AST nodes (internal) --
   --------------------------

         type R_F_L_X_Node is tagged record
            Internal   : Implementation.AST_Envs.Entity;
            Safety_Net : Implementation.Node_Safety_Net;
         end record;
      No_R_F_L_X_Node : constant R_F_L_X_Node :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Abstract_I_D is new R_F_L_X_Node with null record;
      No_Abstract_I_D : constant Abstract_I_D :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Type_Def is new R_F_L_X_Node with null record;
      No_Type_Def : constant Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Abstract_Message_Type_Def is new Type_Def with null record;
      No_Abstract_Message_Type_Def : constant Abstract_Message_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Aspect is new R_F_L_X_Node with null record;
      No_Aspect : constant Aspect :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type R_F_L_X_Node_Base_List is new R_F_L_X_Node with null record;
      No_R_F_L_X_Node_Base_List : constant R_F_L_X_Node_Base_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Aspect_List is new R_F_L_X_Node_Base_List with null record;
      No_Aspect_List : constant Aspect_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Statement is new R_F_L_X_Node with null record;
      No_Statement : constant Statement :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Assignment is new Statement with null record;
      No_Assignment : constant Assignment :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr is new R_F_L_X_Node with null record;
      No_Attr : constant Attr :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_First is new Attr with null record;
      No_Attr_First : constant Attr_First :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Has_Data is new Attr with null record;
      No_Attr_Has_Data : constant Attr_Has_Data :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Head is new Attr with null record;
      No_Attr_Head : constant Attr_Head :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Last is new Attr with null record;
      No_Attr_Last : constant Attr_Last :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Opaque is new Attr with null record;
      No_Attr_Opaque : constant Attr_Opaque :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Present is new Attr with null record;
      No_Attr_Present : constant Attr_Present :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Size is new Attr with null record;
      No_Attr_Size : constant Attr_Size :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Stmt is new R_F_L_X_Node with null record;
      No_Attr_Stmt : constant Attr_Stmt :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Stmt_Append is new Attr_Stmt with null record;
      No_Attr_Stmt_Append : constant Attr_Stmt_Append :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Stmt_Extend is new Attr_Stmt with null record;
      No_Attr_Stmt_Extend : constant Attr_Stmt_Extend :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Stmt_Read is new Attr_Stmt with null record;
      No_Attr_Stmt_Read : constant Attr_Stmt_Read :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Stmt_Write is new Attr_Stmt with null record;
      No_Attr_Stmt_Write : constant Attr_Stmt_Write :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Valid is new Attr with null record;
      No_Attr_Valid : constant Attr_Valid :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attr_Valid_Checksum is new Attr with null record;
      No_Attr_Valid_Checksum : constant Attr_Valid_Checksum :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Expr is new R_F_L_X_Node with null record;
      No_Expr : constant Expr :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attribute is new Expr with null record;
      No_Attribute : constant Attribute :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Attribute_Statement is new Statement with null record;
      No_Attribute_Statement : constant Attribute_Statement :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Base_Aggregate is new R_F_L_X_Node with null record;
      No_Base_Aggregate : constant Base_Aggregate :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Base_Checksum_Val is new R_F_L_X_Node with null record;
      No_Base_Checksum_Val : constant Base_Checksum_Val :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Base_Checksum_Val_List is new R_F_L_X_Node_Base_List with null record;
      No_Base_Checksum_Val_List : constant Base_Checksum_Val_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Bin_Op is new Expr with null record;
      No_Bin_Op : constant Bin_Op :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Binding is new Expr with null record;
      No_Binding : constant Binding :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Aspect is new R_F_L_X_Node with null record;
      No_Message_Aspect : constant Message_Aspect :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Byte_Order_Aspect is new Message_Aspect with null record;
      No_Byte_Order_Aspect : constant Byte_Order_Aspect :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Byte_Order_Type is new R_F_L_X_Node with null record;
      No_Byte_Order_Type : constant Byte_Order_Type :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Byte_Order_Type_Highorderfirst is new Byte_Order_Type with null record;
      No_Byte_Order_Type_Highorderfirst : constant Byte_Order_Type_Highorderfirst :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Byte_Order_Type_Loworderfirst is new Byte_Order_Type with null record;
      No_Byte_Order_Type_Loworderfirst : constant Byte_Order_Type_Loworderfirst :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Call is new Expr with null record;
      No_Call : constant Call :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Case_Expression is new Expr with null record;
      No_Case_Expression : constant Case_Expression :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Channel_Attribute is new R_F_L_X_Node with null record;
      No_Channel_Attribute : constant Channel_Attribute :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Channel_Attribute_List is new R_F_L_X_Node_Base_List with null record;
      No_Channel_Attribute_List : constant Channel_Attribute_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Checksum_Aspect is new Message_Aspect with null record;
      No_Checksum_Aspect : constant Checksum_Aspect :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Checksum_Assoc is new R_F_L_X_Node with null record;
      No_Checksum_Assoc : constant Checksum_Assoc :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Checksum_Assoc_List is new R_F_L_X_Node_Base_List with null record;
      No_Checksum_Assoc_List : constant Checksum_Assoc_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Checksum_Val is new Base_Checksum_Val with null record;
      No_Checksum_Val : constant Checksum_Val :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Checksum_Value_Range is new Base_Checksum_Val with null record;
      No_Checksum_Value_Range : constant Checksum_Value_Range :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Choice is new Expr with null record;
      No_Choice : constant Choice :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Choice_List is new R_F_L_X_Node_Base_List with null record;
      No_Choice_List : constant Choice_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Comprehension is new Expr with null record;
      No_Comprehension : constant Comprehension :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Sequence_Literal is new Expr with null record;
      No_Sequence_Literal : constant Sequence_Literal :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Concatenation is new Sequence_Literal with null record;
      No_Concatenation : constant Concatenation :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Transition is new R_F_L_X_Node with null record;
      No_Transition : constant Transition :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Conditional_Transition is new Transition with null record;
      No_Conditional_Transition : constant Conditional_Transition :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Conditional_Transition_List is new R_F_L_X_Node_Base_List with null record;
      No_Conditional_Transition_List : constant Conditional_Transition_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Context_Item is new Expr with null record;
      No_Context_Item : constant Context_Item :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Context_Item_List is new R_F_L_X_Node_Base_List with null record;
      No_Context_Item_List : constant Context_Item_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Conversion is new Expr with null record;
      No_Conversion : constant Conversion :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Declaration is new R_F_L_X_Node with null record;
      No_Declaration : constant Declaration :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Declaration_List is new R_F_L_X_Node_Base_List with null record;
      No_Declaration_List : constant Declaration_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Description is new R_F_L_X_Node with null record;
      No_Description : constant Description :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Element_Value_Assoc is new R_F_L_X_Node with null record;
      No_Element_Value_Assoc : constant Element_Value_Assoc :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Element_Value_Assoc_List is new R_F_L_X_Node_Base_List with null record;
      No_Element_Value_Assoc_List : constant Element_Value_Assoc_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Enumeration_Def is new Type_Def with null record;
      No_Enumeration_Def : constant Enumeration_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Enumeration_Type_Def is new Type_Def with null record;
      No_Enumeration_Type_Def : constant Enumeration_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Expr_List is new R_F_L_X_Node_Base_List with null record;
      No_Expr_List : constant Expr_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Formal_Decl is new R_F_L_X_Node with null record;
      No_Formal_Decl : constant Formal_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Formal_Channel_Decl is new Formal_Decl with null record;
      No_Formal_Channel_Decl : constant Formal_Channel_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Formal_Decl_List is new R_F_L_X_Node_Base_List with null record;
      No_Formal_Decl_List : constant Formal_Decl_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Formal_Function_Decl is new Formal_Decl with null record;
      No_Formal_Function_Decl : constant Formal_Function_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type I_D is new Abstract_I_D with null record;
      No_I_D : constant I_D :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Integer_Type_Def is new Type_Def with null record;
      No_Integer_Type_Def : constant Integer_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Local_Decl is new R_F_L_X_Node with null record;
      No_Local_Decl : constant Local_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Local_Decl_List is new R_F_L_X_Node_Base_List with null record;
      No_Local_Decl_List : constant Local_Decl_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Aggregate is new Expr with null record;
      No_Message_Aggregate : constant Message_Aggregate :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Aggregate_Association is new R_F_L_X_Node with null record;
      No_Message_Aggregate_Association : constant Message_Aggregate_Association :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Aggregate_Association_List is new R_F_L_X_Node_Base_List with null record;
      No_Message_Aggregate_Association_List : constant Message_Aggregate_Association_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Aggregate_Associations is new Base_Aggregate with null record;
      No_Message_Aggregate_Associations : constant Message_Aggregate_Associations :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Aspect_List is new R_F_L_X_Node_Base_List with null record;
      No_Message_Aspect_List : constant Message_Aspect_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Field is new R_F_L_X_Node with null record;
      No_Message_Field : constant Message_Field :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Field_Assignment is new Statement with null record;
      No_Message_Field_Assignment : constant Message_Field_Assignment :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Field_List is new R_F_L_X_Node_Base_List with null record;
      No_Message_Field_List : constant Message_Field_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Fields is new R_F_L_X_Node with null record;
      No_Message_Fields : constant Message_Fields :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Message_Type_Def is new Abstract_Message_Type_Def with null record;
      No_Message_Type_Def : constant Message_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Modular_Type_Def is new Integer_Type_Def with null record;
      No_Modular_Type_Def : constant Modular_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Named_Enumeration_Def is new Enumeration_Def with null record;
      No_Named_Enumeration_Def : constant Named_Enumeration_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Negation is new Expr with null record;
      No_Negation : constant Negation :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Null_Message_Aggregate is new Base_Aggregate with null record;
      No_Null_Message_Aggregate : constant Null_Message_Aggregate :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Null_Message_Field is new R_F_L_X_Node with null record;
      No_Null_Message_Field : constant Null_Message_Field :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Null_Message_Type_Def is new Abstract_Message_Type_Def with null record;
      No_Null_Message_Type_Def : constant Null_Message_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Numeric_Literal is new Expr with null record;
      No_Numeric_Literal : constant Numeric_Literal :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Numeric_Literal_List is new R_F_L_X_Node_Base_List with null record;
      No_Numeric_Literal_List : constant Numeric_Literal_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op is new R_F_L_X_Node with null record;
      No_Op : constant Op :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Add is new Op with null record;
      No_Op_Add : constant Op_Add :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_And is new Op with null record;
      No_Op_And : constant Op_And :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Div is new Op with null record;
      No_Op_Div : constant Op_Div :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Eq is new Op with null record;
      No_Op_Eq : constant Op_Eq :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Ge is new Op with null record;
      No_Op_Ge : constant Op_Ge :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Gt is new Op with null record;
      No_Op_Gt : constant Op_Gt :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_In is new Op with null record;
      No_Op_In : constant Op_In :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Le is new Op with null record;
      No_Op_Le : constant Op_Le :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Lt is new Op with null record;
      No_Op_Lt : constant Op_Lt :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Mod is new Op with null record;
      No_Op_Mod : constant Op_Mod :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Mul is new Op with null record;
      No_Op_Mul : constant Op_Mul :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Neq is new Op with null record;
      No_Op_Neq : constant Op_Neq :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Notin is new Op with null record;
      No_Op_Notin : constant Op_Notin :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Or is new Op with null record;
      No_Op_Or : constant Op_Or :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Pow is new Op with null record;
      No_Op_Pow : constant Op_Pow :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Op_Sub is new Op with null record;
      No_Op_Sub : constant Op_Sub :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Package_Node is new R_F_L_X_Node with null record;
      No_Package_Node : constant Package_Node :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Parameter is new R_F_L_X_Node with null record;
      No_Parameter : constant Parameter :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Parameter_List is new R_F_L_X_Node_Base_List with null record;
      No_Parameter_List : constant Parameter_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Parameters is new R_F_L_X_Node with null record;
      No_Parameters : constant Parameters :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Paren_Expression is new Expr with null record;
      No_Paren_Expression : constant Paren_Expression :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Positional_Enumeration_Def is new Enumeration_Def with null record;
      No_Positional_Enumeration_Def : constant Positional_Enumeration_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Quantified_Expression is new Expr with null record;
      No_Quantified_Expression : constant Quantified_Expression :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Quantifier is new R_F_L_X_Node with null record;
      No_Quantifier : constant Quantifier :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Quantifier_All is new Quantifier with null record;
      No_Quantifier_All : constant Quantifier_All :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Quantifier_Some is new Quantifier with null record;
      No_Quantifier_Some : constant Quantifier_Some :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type R_F_L_X_Node_List is new R_F_L_X_Node_Base_List with null record;
      No_R_F_L_X_Node_List : constant R_F_L_X_Node_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Range_Type_Def is new Integer_Type_Def with null record;
      No_Range_Type_Def : constant Range_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Readable is new Channel_Attribute with null record;
      No_Readable : constant Readable :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Refinement_Decl is new Declaration with null record;
      No_Refinement_Decl : constant Refinement_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Renaming_Decl is new Local_Decl with null record;
      No_Renaming_Decl : constant Renaming_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Reset is new Statement with null record;
      No_Reset : constant Reset :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Select_Node is new Expr with null record;
      No_Select_Node : constant Select_Node :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Sequence_Aggregate is new Sequence_Literal with null record;
      No_Sequence_Aggregate : constant Sequence_Aggregate :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Sequence_Type_Def is new Type_Def with null record;
      No_Sequence_Type_Def : constant Sequence_Type_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Session_Decl is new Declaration with null record;
      No_Session_Decl : constant Session_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Specification is new R_F_L_X_Node with null record;
      No_Specification : constant Specification :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type State is new R_F_L_X_Node with null record;
      No_State : constant State :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type State_Body is new R_F_L_X_Node with null record;
      No_State_Body : constant State_Body :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type State_List is new R_F_L_X_Node_Base_List with null record;
      No_State_List : constant State_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Statement_List is new R_F_L_X_Node_Base_List with null record;
      No_Statement_List : constant Statement_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type String_Literal is new Sequence_Literal with null record;
      No_String_Literal : constant String_Literal :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Term_Assoc is new R_F_L_X_Node with null record;
      No_Term_Assoc : constant Term_Assoc :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Term_Assoc_List is new R_F_L_X_Node_Base_List with null record;
      No_Term_Assoc_List : constant Term_Assoc_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Then_Node is new R_F_L_X_Node with null record;
      No_Then_Node : constant Then_Node :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Then_Node_List is new R_F_L_X_Node_Base_List with null record;
      No_Then_Node_List : constant Then_Node_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Type_Argument is new R_F_L_X_Node with null record;
      No_Type_Argument : constant Type_Argument :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Type_Argument_List is new R_F_L_X_Node_Base_List with null record;
      No_Type_Argument_List : constant Type_Argument_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Type_Decl is new Declaration with null record;
      No_Type_Decl : constant Type_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Type_Derivation_Def is new Type_Def with null record;
      No_Type_Derivation_Def : constant Type_Derivation_Def :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Unqualified_I_D is new Abstract_I_D with null record;
      No_Unqualified_I_D : constant Unqualified_I_D :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Unqualified_I_D_List is new R_F_L_X_Node_Base_List with null record;
      No_Unqualified_I_D_List : constant Unqualified_I_D_List :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Variable is new Expr with null record;
      No_Variable : constant Variable :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Variable_Decl is new Local_Decl with null record;
      No_Variable_Decl : constant Variable_Decl :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);
         type Writable is new Channel_Attribute with null record;
      No_Writable : constant Writable :=
        (Internal   => Implementation.No_Entity,
         Safety_Net => Implementation.No_Node_Safety_Net);

   package Child_Record_Vectors is new Ada.Containers.Vectors
     (Index_Type   => Positive,
      Element_Type => Child_Record);

   type Children_Array is record
      Children : Child_Record_Vectors.Vector;
   end record;

   procedure Check_Safety_Net (Self : R_F_L_X_Node'Class);
   --  Check that Self's node and rebindings are still valid, raising a
   --  Stale_Reference_Error if one is not.

   --------------------------------
   -- Token Iterator (internals) --
   --------------------------------

   type Token_Iterator is record
      Node : R_F_L_X_Node;
      Last : Token_Index;
   end record;

   ---------------------------------
   -- Composite types (internals) --
   ---------------------------------

            


   --  The dummy references to these packages forces them to be included in
   --  statically linked builds (thanks to the binder). This benefits the GDB
   --  helpers at no cost.

   Version : String renames Librflxlang.Version;
   procedure RN (Node : Librflxlang.Implementation.Bare_R_F_L_X_Node)
      renames Librflxlang.Debug.PN;

end Librflxlang.Analysis;
