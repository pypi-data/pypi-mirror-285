


with GNATCOLL.GMP.Integers;

with Langkit_Support.Errors;
private with Langkit_Support.Internal.Analysis;
with Langkit_Support.Symbols; use Langkit_Support.Symbols;
with Langkit_Support.Token_Data_Handlers;
use Langkit_Support.Token_Data_Handlers;
with Langkit_Support.Types;   use Langkit_Support.Types;


--  This package provides types and functions used in the whole Librflxlang
--  package tree.

package Librflxlang.Common is

   use Support.Slocs, Support.Text;

   subtype Big_Integer is GNATCOLL.GMP.Integers.Big_Integer;
   --  Shortcut for ``GNATCOLL.GMP.Integers.Big_Integer``

   

   Default_Charset : constant String := "utf-8";
   --  Default charset to use when creating analysis contexts

   ----------------
   -- Exceptions --
   ----------------

   File_Read_Error : exception renames Langkit_Support.Errors.File_Read_Error;
   --  Subprograms may raise this when they cannot open a source file. Note
   --  that this does *not* concern analysis unit getters, which create
   --  diagnostic vectors for such errors.

   Invalid_Input : exception renames Langkit_Support.Errors.Invalid_Input;
   --  Raised by lexing functions (``Librflxlang.Lexer``) when the input
   --  contains an invalid byte sequence.

   Invalid_Symbol_Error : exception renames Langkit_Support.Errors.Invalid_Symbol_Error;
   --  Exception raise when an invalid symbol is passed to a subprogram.

   Invalid_Unit_Name_Error : exception renames Langkit_Support.Errors.Invalid_Unit_Name_Error;
   --  Raised when an invalid unit name is provided.

   Native_Exception : exception renames Langkit_Support.Errors.Native_Exception;
   --  Exception raised in language bindings when the underlying C API reports
   --  an unexpected error that occurred in the library.
   --
   --  This kind of exception is raised for internal errors: they should never
   --  happen in normal situations and if they are raised at some point, it
   --  means the library state is potentially corrupted.
   --
   --  Nevertheless, the library does its best not to crash the program,
   --  materializing internal errors using this kind of exception.

   Precondition_Failure : exception renames Langkit_Support.Errors.Precondition_Failure;
   --  Exception raised when an API is called while its preconditions are not
   --  satisfied.

   Property_Error : exception renames Langkit_Support.Errors.Property_Error;
   --  Exception that is raised when an error occurs while evaluating any
   --  function whose name starts with ``P_``. This is the only exceptions that
   --  such functions can raise.

   Stale_Reference_Error : exception renames Langkit_Support.Errors.Stale_Reference_Error;
   --  Exception raised while trying to access data that was deallocated. This
   --  happens when one tries to use a node whose unit has been reparsed, for
   --  instance.

   Syntax_Error : exception renames Langkit_Support.Errors.Syntax_Error;
   --  Subprograms may raise this when they try to parse invalid syntax. Note
   --  that this does *not* concern analysis unit getters, which create
   --  diagnostic vectors for such errors.

   Unknown_Charset : exception renames Langkit_Support.Errors.Unknown_Charset;
   --  Raised by lexing functions (``Librflxlang.Lexer``) when the input
   --  charset is not supported.

   -------------------
   -- Introspection --
   -------------------

   Bad_Type_Error : exception renames Langkit_Support.Errors.Introspection.Bad_Type_Error;
   --  Raised when introspection functions (``Librflxlang.Introspection``) are
   --  provided mismatching types/values.

   Out_Of_Bounds_Error : exception renames Langkit_Support.Errors.Introspection.Out_Of_Bounds_Error;
   --  Raised when introspection functions (``Librflxlang.Introspection``) are
   --  passed an out of bounds index.

   ---------------
   -- Rewriting --
   ---------------

   Template_Args_Error : exception renames Langkit_Support.Errors.Rewriting.Template_Args_Error;
   --  Exception raised when the provided arguments for a template don't match
   --  what the template expects.

   Template_Format_Error : exception renames Langkit_Support.Errors.Rewriting.Template_Format_Error;
   --  Exception raised when a template has an invalid syntax, such as badly
   --  formatted placeholders.

   Template_Instantiation_Error : exception renames Langkit_Support.Errors.Rewriting.Template_Instantiation_Error;
   --  Exception raised when the instantiation of a template cannot be parsed.

   ---------------
   -- Unparsing --
   ---------------

   Malformed_Tree_Error : exception renames Langkit_Support.Errors.Unparsing.Malformed_Tree_Error;
   --  Raised when unparsing functions working on rewritten trees
   --  (``Librflxlang.Rewriting``) are called on malformed trees.


   ----------------------------
   -- Misc enumeration types --
   ----------------------------

      type Analysis_Unit_Kind is
        (Unit_Specification, Unit_Body)
         with Convention => C;
      --  Specify a kind of analysis unit. Specification units provide an
      --  interface to the outer world while body units provide an
      --  implementation for the corresponding interface.


      function Trace_Image (Self : Analysis_Unit_Kind) return String
      is (Self'Image);

      type Lookup_Kind is
        (Recursive, Flat, Minimal)
         with Convention => C;
      


      function Trace_Image (Self : Lookup_Kind) return String
      is (Self'Image);

      type Designated_Env_Kind is
        (None, Current_Env, Named_Env, Direct_Env)
         with Convention => C;
      --  Discriminant for DesignatedEnv structures.


      function Trace_Image (Self : Designated_Env_Kind) return String
      is (Self'Image);

      type Grammar_Rule is
        (Main_Rule_Rule, Unqualified_Identifier_Rule, Qualified_Identifier_Rule, Numeric_Literal_Rule, Variable_Rule, Sequence_Aggregate_Rule, String_Literal_Rule, Concatenation_Rule, Primary_Rule, Paren_Expression_Rule, Suffix_Rule, Factor_Rule, Term_Rule, Unop_Term_Rule, Simple_Expr_Rule, Relation_Rule, Expression_Rule, Quantified_Expression_Rule, Comprehension_Rule, Call_Rule, Conversion_Rule, Null_Message_Aggregate_Rule, Message_Aggregate_Association_Rule, Message_Aggregate_Association_List_Rule, Message_Aggregate_Rule, Extended_Primary_Rule, Extended_Paren_Expression_Rule, Extended_Choice_List_Rule, Extended_Choices_Rule, Extended_Case_Expression_Rule, Extended_Suffix_Rule, Extended_Factor_Rule, Extended_Term_Rule, Extended_Unop_Term_Rule, Extended_Simple_Expr_Rule, Extended_Relation_Rule, Extended_Expression_Rule, Aspect_Rule, Range_Type_Definition_Rule, Modular_Type_Definition_Rule, Integer_Type_Definition_Rule, If_Condition_Rule, Extended_If_Condition_Rule, Then_Rule, Type_Argument_Rule, Null_Message_Field_Rule, Message_Field_Rule, Message_Field_List_Rule, Value_Range_Rule, Checksum_Association_Rule, Checksum_Aspect_Rule, Byte_Order_Aspect_Rule, Message_Aspect_List_Rule, Message_Type_Definition_Rule, Positional_Enumeration_Rule, Element_Value_Association_Rule, Named_Enumeration_Rule, Enumeration_Aspects_Rule, Enumeration_Type_Definition_Rule, Type_Derivation_Definition_Rule, Sequence_Type_Definition_Rule, Type_Declaration_Rule, Type_Refinement_Rule, Parameter_Rule, Parameter_List_Rule, Formal_Function_Declaration_Rule, Channel_Declaration_Rule, Session_Parameter_Rule, Renaming_Declaration_Rule, Variable_Declaration_Rule, Declaration_Rule, Description_Aspect_Rule, Assignment_Statement_Rule, Message_Field_Assignment_Statement_Rule, List_Attribute_Rule, Reset_Rule, Attribute_Statement_Rule, Action_Rule, Conditional_Transition_Rule, Transition_Rule, State_Body_Rule, State_Rule, Session_Declaration_Rule, Basic_Declaration_Rule, Basic_Declarations_Rule, Package_Declaration_Rule, Context_Item_Rule, Context_Clause_Rule, Specification_Rule)
         with Convention => C;
      --  Gramar rule to use for parsing.


      function Trace_Image (Self : Grammar_Rule) return String
      is (Self'Image);


   -----------
   -- Nodes --
   -----------

   type R_F_L_X_Node_Kind_Type is
     (Rflx_I_D, Rflx_Unqualified_I_D, Rflx_Aspect, Rflx_Attr_First, Rflx_Attr_Has_Data, Rflx_Attr_Head, Rflx_Attr_Last, Rflx_Attr_Opaque, Rflx_Attr_Present, Rflx_Attr_Size, Rflx_Attr_Valid, Rflx_Attr_Valid_Checksum, Rflx_Attr_Stmt_Append, Rflx_Attr_Stmt_Extend, Rflx_Attr_Stmt_Read, Rflx_Attr_Stmt_Write, Rflx_Message_Aggregate_Associations, Rflx_Null_Message_Aggregate, Rflx_Checksum_Val, Rflx_Checksum_Value_Range, Rflx_Byte_Order_Type_Highorderfirst, Rflx_Byte_Order_Type_Loworderfirst, Rflx_Readable, Rflx_Writable, Rflx_Checksum_Assoc, Rflx_Refinement_Decl, Rflx_Session_Decl, Rflx_Type_Decl, Rflx_Description, Rflx_Element_Value_Assoc, Rflx_Attribute, Rflx_Bin_Op, Rflx_Binding, Rflx_Call, Rflx_Case_Expression, Rflx_Choice, Rflx_Comprehension, Rflx_Context_Item, Rflx_Conversion, Rflx_Message_Aggregate, Rflx_Negation, Rflx_Numeric_Literal, Rflx_Paren_Expression, Rflx_Quantified_Expression, Rflx_Select_Node, Rflx_Concatenation, Rflx_Sequence_Aggregate, Rflx_String_Literal, Rflx_Variable, Rflx_Formal_Channel_Decl, Rflx_Formal_Function_Decl, Rflx_Renaming_Decl, Rflx_Variable_Decl, Rflx_Message_Aggregate_Association, Rflx_Byte_Order_Aspect, Rflx_Checksum_Aspect, Rflx_Message_Field, Rflx_Message_Fields, Rflx_Null_Message_Field, Rflx_Op_Add, Rflx_Op_And, Rflx_Op_Div, Rflx_Op_Eq, Rflx_Op_Ge, Rflx_Op_Gt, Rflx_Op_In, Rflx_Op_Le, Rflx_Op_Lt, Rflx_Op_Mod, Rflx_Op_Mul, Rflx_Op_Neq, Rflx_Op_Notin, Rflx_Op_Or, Rflx_Op_Pow, Rflx_Op_Sub, Rflx_Package_Node, Rflx_Parameter, Rflx_Parameters, Rflx_Quantifier_All, Rflx_Quantifier_Some, Rflx_Aspect_List, Rflx_Base_Checksum_Val_List, Rflx_Channel_Attribute_List, Rflx_Checksum_Assoc_List, Rflx_Choice_List, Rflx_Conditional_Transition_List, Rflx_Context_Item_List, Rflx_Declaration_List, Rflx_Element_Value_Assoc_List, Rflx_Expr_List, Rflx_Formal_Decl_List, Rflx_Local_Decl_List, Rflx_Message_Aggregate_Association_List, Rflx_Message_Aspect_List, Rflx_Message_Field_List, Rflx_Numeric_Literal_List, Rflx_Parameter_List, Rflx_R_F_L_X_Node_List, Rflx_State_List, Rflx_Statement_List, Rflx_Term_Assoc_List, Rflx_Then_Node_List, Rflx_Type_Argument_List, Rflx_Unqualified_I_D_List, Rflx_Specification, Rflx_State, Rflx_State_Body, Rflx_Assignment, Rflx_Attribute_Statement, Rflx_Message_Field_Assignment, Rflx_Reset, Rflx_Term_Assoc, Rflx_Then_Node, Rflx_Transition, Rflx_Conditional_Transition, Rflx_Type_Argument, Rflx_Message_Type_Def, Rflx_Null_Message_Type_Def, Rflx_Named_Enumeration_Def, Rflx_Positional_Enumeration_Def, Rflx_Enumeration_Type_Def, Rflx_Modular_Type_Def, Rflx_Range_Type_Def, Rflx_Sequence_Type_Def, Rflx_Type_Derivation_Def);
   --  Type for concrete nodes

   for R_F_L_X_Node_Kind_Type use
     (Rflx_I_D => 1, Rflx_Unqualified_I_D => 2, Rflx_Aspect => 3, Rflx_Attr_First => 4, Rflx_Attr_Has_Data => 5, Rflx_Attr_Head => 6, Rflx_Attr_Last => 7, Rflx_Attr_Opaque => 8, Rflx_Attr_Present => 9, Rflx_Attr_Size => 10, Rflx_Attr_Valid => 11, Rflx_Attr_Valid_Checksum => 12, Rflx_Attr_Stmt_Append => 13, Rflx_Attr_Stmt_Extend => 14, Rflx_Attr_Stmt_Read => 15, Rflx_Attr_Stmt_Write => 16, Rflx_Message_Aggregate_Associations => 17, Rflx_Null_Message_Aggregate => 18, Rflx_Checksum_Val => 19, Rflx_Checksum_Value_Range => 20, Rflx_Byte_Order_Type_Highorderfirst => 21, Rflx_Byte_Order_Type_Loworderfirst => 22, Rflx_Readable => 23, Rflx_Writable => 24, Rflx_Checksum_Assoc => 25, Rflx_Refinement_Decl => 26, Rflx_Session_Decl => 27, Rflx_Type_Decl => 28, Rflx_Description => 29, Rflx_Element_Value_Assoc => 30, Rflx_Attribute => 31, Rflx_Bin_Op => 32, Rflx_Binding => 33, Rflx_Call => 34, Rflx_Case_Expression => 35, Rflx_Choice => 36, Rflx_Comprehension => 37, Rflx_Context_Item => 38, Rflx_Conversion => 39, Rflx_Message_Aggregate => 40, Rflx_Negation => 41, Rflx_Numeric_Literal => 42, Rflx_Paren_Expression => 43, Rflx_Quantified_Expression => 44, Rflx_Select_Node => 45, Rflx_Concatenation => 46, Rflx_Sequence_Aggregate => 47, Rflx_String_Literal => 48, Rflx_Variable => 49, Rflx_Formal_Channel_Decl => 50, Rflx_Formal_Function_Decl => 51, Rflx_Renaming_Decl => 52, Rflx_Variable_Decl => 53, Rflx_Message_Aggregate_Association => 54, Rflx_Byte_Order_Aspect => 55, Rflx_Checksum_Aspect => 56, Rflx_Message_Field => 57, Rflx_Message_Fields => 58, Rflx_Null_Message_Field => 59, Rflx_Op_Add => 60, Rflx_Op_And => 61, Rflx_Op_Div => 62, Rflx_Op_Eq => 63, Rflx_Op_Ge => 64, Rflx_Op_Gt => 65, Rflx_Op_In => 66, Rflx_Op_Le => 67, Rflx_Op_Lt => 68, Rflx_Op_Mod => 69, Rflx_Op_Mul => 70, Rflx_Op_Neq => 71, Rflx_Op_Notin => 72, Rflx_Op_Or => 73, Rflx_Op_Pow => 74, Rflx_Op_Sub => 75, Rflx_Package_Node => 76, Rflx_Parameter => 77, Rflx_Parameters => 78, Rflx_Quantifier_All => 79, Rflx_Quantifier_Some => 80, Rflx_Aspect_List => 81, Rflx_Base_Checksum_Val_List => 82, Rflx_Channel_Attribute_List => 83, Rflx_Checksum_Assoc_List => 84, Rflx_Choice_List => 85, Rflx_Conditional_Transition_List => 86, Rflx_Context_Item_List => 87, Rflx_Declaration_List => 88, Rflx_Element_Value_Assoc_List => 89, Rflx_Expr_List => 90, Rflx_Formal_Decl_List => 91, Rflx_Local_Decl_List => 92, Rflx_Message_Aggregate_Association_List => 93, Rflx_Message_Aspect_List => 94, Rflx_Message_Field_List => 95, Rflx_Numeric_Literal_List => 96, Rflx_Parameter_List => 97, Rflx_R_F_L_X_Node_List => 98, Rflx_State_List => 99, Rflx_Statement_List => 100, Rflx_Term_Assoc_List => 101, Rflx_Then_Node_List => 102, Rflx_Type_Argument_List => 103, Rflx_Unqualified_I_D_List => 104, Rflx_Specification => 105, Rflx_State => 106, Rflx_State_Body => 107, Rflx_Assignment => 108, Rflx_Attribute_Statement => 109, Rflx_Message_Field_Assignment => 110, Rflx_Reset => 111, Rflx_Term_Assoc => 112, Rflx_Then_Node => 113, Rflx_Transition => 114, Rflx_Conditional_Transition => 115, Rflx_Type_Argument => 116, Rflx_Message_Type_Def => 117, Rflx_Null_Message_Type_Def => 118, Rflx_Named_Enumeration_Def => 119, Rflx_Positional_Enumeration_Def => 120, Rflx_Enumeration_Type_Def => 121, Rflx_Modular_Type_Def => 122, Rflx_Range_Type_Def => 123, Rflx_Sequence_Type_Def => 124, Rflx_Type_Derivation_Def => 125);

      subtype Rflx_R_F_L_X_Node is R_F_L_X_Node_Kind_Type
            range Rflx_I_D .. Rflx_Type_Derivation_Def;
      --% no-document: True
      subtype Rflx_Abstract_I_D is R_F_L_X_Node_Kind_Type
            range Rflx_I_D .. Rflx_Unqualified_I_D;
      --% no-document: True
      subtype Rflx_I_D_Range is R_F_L_X_Node_Kind_Type
            range Rflx_I_D .. Rflx_I_D;
      --% no-document: True
      subtype Rflx_Unqualified_I_D_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Unqualified_I_D .. Rflx_Unqualified_I_D;
      --% no-document: True
      subtype Rflx_Aspect_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Aspect .. Rflx_Aspect;
      --% no-document: True
      subtype Rflx_Attr is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_First .. Rflx_Attr_Valid_Checksum;
      --% no-document: True
      subtype Rflx_Attr_First_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_First .. Rflx_Attr_First;
      --% no-document: True
      subtype Rflx_Attr_Has_Data_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Has_Data .. Rflx_Attr_Has_Data;
      --% no-document: True
      subtype Rflx_Attr_Head_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Head .. Rflx_Attr_Head;
      --% no-document: True
      subtype Rflx_Attr_Last_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Last .. Rflx_Attr_Last;
      --% no-document: True
      subtype Rflx_Attr_Opaque_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Opaque .. Rflx_Attr_Opaque;
      --% no-document: True
      subtype Rflx_Attr_Present_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Present .. Rflx_Attr_Present;
      --% no-document: True
      subtype Rflx_Attr_Size_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Size .. Rflx_Attr_Size;
      --% no-document: True
      subtype Rflx_Attr_Valid_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Valid .. Rflx_Attr_Valid;
      --% no-document: True
      subtype Rflx_Attr_Valid_Checksum_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Valid_Checksum .. Rflx_Attr_Valid_Checksum;
      --% no-document: True
      subtype Rflx_Attr_Stmt is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Stmt_Append .. Rflx_Attr_Stmt_Write;
      --% no-document: True
      subtype Rflx_Attr_Stmt_Append_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Stmt_Append .. Rflx_Attr_Stmt_Append;
      --% no-document: True
      subtype Rflx_Attr_Stmt_Extend_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Stmt_Extend .. Rflx_Attr_Stmt_Extend;
      --% no-document: True
      subtype Rflx_Attr_Stmt_Read_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Stmt_Read .. Rflx_Attr_Stmt_Read;
      --% no-document: True
      subtype Rflx_Attr_Stmt_Write_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attr_Stmt_Write .. Rflx_Attr_Stmt_Write;
      --% no-document: True
      subtype Rflx_Base_Aggregate is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Aggregate_Associations .. Rflx_Null_Message_Aggregate;
      --% no-document: True
      subtype Rflx_Message_Aggregate_Associations_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Aggregate_Associations .. Rflx_Message_Aggregate_Associations;
      --% no-document: True
      subtype Rflx_Null_Message_Aggregate_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Null_Message_Aggregate .. Rflx_Null_Message_Aggregate;
      --% no-document: True
      subtype Rflx_Base_Checksum_Val is R_F_L_X_Node_Kind_Type
            range Rflx_Checksum_Val .. Rflx_Checksum_Value_Range;
      --% no-document: True
      subtype Rflx_Checksum_Val_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Checksum_Val .. Rflx_Checksum_Val;
      --% no-document: True
      subtype Rflx_Checksum_Value_Range_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Checksum_Value_Range .. Rflx_Checksum_Value_Range;
      --% no-document: True
      subtype Rflx_Byte_Order_Type is R_F_L_X_Node_Kind_Type
            range Rflx_Byte_Order_Type_Highorderfirst .. Rflx_Byte_Order_Type_Loworderfirst;
      --% no-document: True
      subtype Rflx_Byte_Order_Type_Highorderfirst_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Byte_Order_Type_Highorderfirst .. Rflx_Byte_Order_Type_Highorderfirst;
      --% no-document: True
      subtype Rflx_Byte_Order_Type_Loworderfirst_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Byte_Order_Type_Loworderfirst .. Rflx_Byte_Order_Type_Loworderfirst;
      --% no-document: True
      subtype Rflx_Channel_Attribute is R_F_L_X_Node_Kind_Type
            range Rflx_Readable .. Rflx_Writable;
      --% no-document: True
      subtype Rflx_Readable_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Readable .. Rflx_Readable;
      --% no-document: True
      subtype Rflx_Writable_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Writable .. Rflx_Writable;
      --% no-document: True
      subtype Rflx_Checksum_Assoc_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Checksum_Assoc .. Rflx_Checksum_Assoc;
      --% no-document: True
      subtype Rflx_Declaration is R_F_L_X_Node_Kind_Type
            range Rflx_Refinement_Decl .. Rflx_Type_Decl;
      --% no-document: True
      subtype Rflx_Refinement_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Refinement_Decl .. Rflx_Refinement_Decl;
      --% no-document: True
      subtype Rflx_Session_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Session_Decl .. Rflx_Session_Decl;
      --% no-document: True
      subtype Rflx_Type_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Type_Decl .. Rflx_Type_Decl;
      --% no-document: True
      subtype Rflx_Description_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Description .. Rflx_Description;
      --% no-document: True
      subtype Rflx_Element_Value_Assoc_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Element_Value_Assoc .. Rflx_Element_Value_Assoc;
      --% no-document: True
      subtype Rflx_Expr is R_F_L_X_Node_Kind_Type
            range Rflx_Attribute .. Rflx_Variable;
      --% no-document: True
      subtype Rflx_Attribute_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attribute .. Rflx_Attribute;
      --% no-document: True
      subtype Rflx_Bin_Op_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Bin_Op .. Rflx_Bin_Op;
      --% no-document: True
      subtype Rflx_Binding_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Binding .. Rflx_Binding;
      --% no-document: True
      subtype Rflx_Call_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Call .. Rflx_Call;
      --% no-document: True
      subtype Rflx_Case_Expression_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Case_Expression .. Rflx_Case_Expression;
      --% no-document: True
      subtype Rflx_Choice_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Choice .. Rflx_Choice;
      --% no-document: True
      subtype Rflx_Comprehension_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Comprehension .. Rflx_Comprehension;
      --% no-document: True
      subtype Rflx_Context_Item_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Context_Item .. Rflx_Context_Item;
      --% no-document: True
      subtype Rflx_Conversion_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Conversion .. Rflx_Conversion;
      --% no-document: True
      subtype Rflx_Message_Aggregate_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Aggregate .. Rflx_Message_Aggregate;
      --% no-document: True
      subtype Rflx_Negation_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Negation .. Rflx_Negation;
      --% no-document: True
      subtype Rflx_Numeric_Literal_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Numeric_Literal .. Rflx_Numeric_Literal;
      --% no-document: True
      subtype Rflx_Paren_Expression_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Paren_Expression .. Rflx_Paren_Expression;
      --% no-document: True
      subtype Rflx_Quantified_Expression_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Quantified_Expression .. Rflx_Quantified_Expression;
      --% no-document: True
      subtype Rflx_Select_Node_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Select_Node .. Rflx_Select_Node;
      --% no-document: True
      subtype Rflx_Sequence_Literal is R_F_L_X_Node_Kind_Type
            range Rflx_Concatenation .. Rflx_String_Literal;
      --% no-document: True
      subtype Rflx_Concatenation_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Concatenation .. Rflx_Concatenation;
      --% no-document: True
      subtype Rflx_Sequence_Aggregate_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Sequence_Aggregate .. Rflx_Sequence_Aggregate;
      --% no-document: True
      subtype Rflx_String_Literal_Range is R_F_L_X_Node_Kind_Type
            range Rflx_String_Literal .. Rflx_String_Literal;
      --% no-document: True
      subtype Rflx_Variable_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Variable .. Rflx_Variable;
      --% no-document: True
      subtype Rflx_Formal_Decl is R_F_L_X_Node_Kind_Type
            range Rflx_Formal_Channel_Decl .. Rflx_Formal_Function_Decl;
      --% no-document: True
      subtype Rflx_Formal_Channel_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Formal_Channel_Decl .. Rflx_Formal_Channel_Decl;
      --% no-document: True
      subtype Rflx_Formal_Function_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Formal_Function_Decl .. Rflx_Formal_Function_Decl;
      --% no-document: True
      subtype Rflx_Local_Decl is R_F_L_X_Node_Kind_Type
            range Rflx_Renaming_Decl .. Rflx_Variable_Decl;
      --% no-document: True
      subtype Rflx_Renaming_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Renaming_Decl .. Rflx_Renaming_Decl;
      --% no-document: True
      subtype Rflx_Variable_Decl_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Variable_Decl .. Rflx_Variable_Decl;
      --% no-document: True
      subtype Rflx_Message_Aggregate_Association_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Aggregate_Association .. Rflx_Message_Aggregate_Association;
      --% no-document: True
      subtype Rflx_Message_Aspect is R_F_L_X_Node_Kind_Type
            range Rflx_Byte_Order_Aspect .. Rflx_Checksum_Aspect;
      --% no-document: True
      subtype Rflx_Byte_Order_Aspect_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Byte_Order_Aspect .. Rflx_Byte_Order_Aspect;
      --% no-document: True
      subtype Rflx_Checksum_Aspect_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Checksum_Aspect .. Rflx_Checksum_Aspect;
      --% no-document: True
      subtype Rflx_Message_Field_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Field .. Rflx_Message_Field;
      --% no-document: True
      subtype Rflx_Message_Fields_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Fields .. Rflx_Message_Fields;
      --% no-document: True
      subtype Rflx_Null_Message_Field_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Null_Message_Field .. Rflx_Null_Message_Field;
      --% no-document: True
      subtype Rflx_Op is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Add .. Rflx_Op_Sub;
      --% no-document: True
      subtype Rflx_Op_Add_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Add .. Rflx_Op_Add;
      --% no-document: True
      subtype Rflx_Op_And_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_And .. Rflx_Op_And;
      --% no-document: True
      subtype Rflx_Op_Div_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Div .. Rflx_Op_Div;
      --% no-document: True
      subtype Rflx_Op_Eq_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Eq .. Rflx_Op_Eq;
      --% no-document: True
      subtype Rflx_Op_Ge_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Ge .. Rflx_Op_Ge;
      --% no-document: True
      subtype Rflx_Op_Gt_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Gt .. Rflx_Op_Gt;
      --% no-document: True
      subtype Rflx_Op_In_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_In .. Rflx_Op_In;
      --% no-document: True
      subtype Rflx_Op_Le_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Le .. Rflx_Op_Le;
      --% no-document: True
      subtype Rflx_Op_Lt_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Lt .. Rflx_Op_Lt;
      --% no-document: True
      subtype Rflx_Op_Mod_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Mod .. Rflx_Op_Mod;
      --% no-document: True
      subtype Rflx_Op_Mul_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Mul .. Rflx_Op_Mul;
      --% no-document: True
      subtype Rflx_Op_Neq_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Neq .. Rflx_Op_Neq;
      --% no-document: True
      subtype Rflx_Op_Notin_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Notin .. Rflx_Op_Notin;
      --% no-document: True
      subtype Rflx_Op_Or_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Or .. Rflx_Op_Or;
      --% no-document: True
      subtype Rflx_Op_Pow_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Pow .. Rflx_Op_Pow;
      --% no-document: True
      subtype Rflx_Op_Sub_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Op_Sub .. Rflx_Op_Sub;
      --% no-document: True
      subtype Rflx_Package_Node_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Package_Node .. Rflx_Package_Node;
      --% no-document: True
      subtype Rflx_Parameter_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Parameter .. Rflx_Parameter;
      --% no-document: True
      subtype Rflx_Parameters_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Parameters .. Rflx_Parameters;
      --% no-document: True
      subtype Rflx_Quantifier is R_F_L_X_Node_Kind_Type
            range Rflx_Quantifier_All .. Rflx_Quantifier_Some;
      --% no-document: True
      subtype Rflx_Quantifier_All_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Quantifier_All .. Rflx_Quantifier_All;
      --% no-document: True
      subtype Rflx_Quantifier_Some_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Quantifier_Some .. Rflx_Quantifier_Some;
      --% no-document: True
      subtype Rflx_R_F_L_X_Node_Base_List is R_F_L_X_Node_Kind_Type
            range Rflx_Aspect_List .. Rflx_Unqualified_I_D_List;
      --% no-document: True
      subtype Rflx_Aspect_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Aspect_List .. Rflx_Aspect_List;
      --% no-document: True
      subtype Rflx_Base_Checksum_Val_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Base_Checksum_Val_List .. Rflx_Base_Checksum_Val_List;
      --% no-document: True
      subtype Rflx_Channel_Attribute_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Channel_Attribute_List .. Rflx_Channel_Attribute_List;
      --% no-document: True
      subtype Rflx_Checksum_Assoc_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Checksum_Assoc_List .. Rflx_Checksum_Assoc_List;
      --% no-document: True
      subtype Rflx_Choice_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Choice_List .. Rflx_Choice_List;
      --% no-document: True
      subtype Rflx_Conditional_Transition_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Conditional_Transition_List .. Rflx_Conditional_Transition_List;
      --% no-document: True
      subtype Rflx_Context_Item_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Context_Item_List .. Rflx_Context_Item_List;
      --% no-document: True
      subtype Rflx_Declaration_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Declaration_List .. Rflx_Declaration_List;
      --% no-document: True
      subtype Rflx_Element_Value_Assoc_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Element_Value_Assoc_List .. Rflx_Element_Value_Assoc_List;
      --% no-document: True
      subtype Rflx_Expr_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Expr_List .. Rflx_Expr_List;
      --% no-document: True
      subtype Rflx_Formal_Decl_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Formal_Decl_List .. Rflx_Formal_Decl_List;
      --% no-document: True
      subtype Rflx_Local_Decl_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Local_Decl_List .. Rflx_Local_Decl_List;
      --% no-document: True
      subtype Rflx_Message_Aggregate_Association_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Aggregate_Association_List .. Rflx_Message_Aggregate_Association_List;
      --% no-document: True
      subtype Rflx_Message_Aspect_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Aspect_List .. Rflx_Message_Aspect_List;
      --% no-document: True
      subtype Rflx_Message_Field_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Field_List .. Rflx_Message_Field_List;
      --% no-document: True
      subtype Rflx_Numeric_Literal_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Numeric_Literal_List .. Rflx_Numeric_Literal_List;
      --% no-document: True
      subtype Rflx_Parameter_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Parameter_List .. Rflx_Parameter_List;
      --% no-document: True
      subtype Rflx_R_F_L_X_Node_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_R_F_L_X_Node_List .. Rflx_R_F_L_X_Node_List;
      --% no-document: True
      subtype Rflx_State_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_State_List .. Rflx_State_List;
      --% no-document: True
      subtype Rflx_Statement_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Statement_List .. Rflx_Statement_List;
      --% no-document: True
      subtype Rflx_Term_Assoc_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Term_Assoc_List .. Rflx_Term_Assoc_List;
      --% no-document: True
      subtype Rflx_Then_Node_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Then_Node_List .. Rflx_Then_Node_List;
      --% no-document: True
      subtype Rflx_Type_Argument_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Type_Argument_List .. Rflx_Type_Argument_List;
      --% no-document: True
      subtype Rflx_Unqualified_I_D_List_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Unqualified_I_D_List .. Rflx_Unqualified_I_D_List;
      --% no-document: True
      subtype Rflx_Specification_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Specification .. Rflx_Specification;
      --% no-document: True
      subtype Rflx_State_Range is R_F_L_X_Node_Kind_Type
            range Rflx_State .. Rflx_State;
      --% no-document: True
      subtype Rflx_State_Body_Range is R_F_L_X_Node_Kind_Type
            range Rflx_State_Body .. Rflx_State_Body;
      --% no-document: True
      subtype Rflx_Statement is R_F_L_X_Node_Kind_Type
            range Rflx_Assignment .. Rflx_Reset;
      --% no-document: True
      subtype Rflx_Assignment_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Assignment .. Rflx_Assignment;
      --% no-document: True
      subtype Rflx_Attribute_Statement_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Attribute_Statement .. Rflx_Attribute_Statement;
      --% no-document: True
      subtype Rflx_Message_Field_Assignment_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Field_Assignment .. Rflx_Message_Field_Assignment;
      --% no-document: True
      subtype Rflx_Reset_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Reset .. Rflx_Reset;
      --% no-document: True
      subtype Rflx_Term_Assoc_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Term_Assoc .. Rflx_Term_Assoc;
      --% no-document: True
      subtype Rflx_Then_Node_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Then_Node .. Rflx_Then_Node;
      --% no-document: True
      subtype Rflx_Transition_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Transition .. Rflx_Conditional_Transition;
      --% no-document: True
      subtype Rflx_Conditional_Transition_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Conditional_Transition .. Rflx_Conditional_Transition;
      --% no-document: True
      subtype Rflx_Type_Argument_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Type_Argument .. Rflx_Type_Argument;
      --% no-document: True
      subtype Rflx_Type_Def is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Type_Def .. Rflx_Type_Derivation_Def;
      --% no-document: True
      subtype Rflx_Abstract_Message_Type_Def is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Type_Def .. Rflx_Null_Message_Type_Def;
      --% no-document: True
      subtype Rflx_Message_Type_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Message_Type_Def .. Rflx_Message_Type_Def;
      --% no-document: True
      subtype Rflx_Null_Message_Type_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Null_Message_Type_Def .. Rflx_Null_Message_Type_Def;
      --% no-document: True
      subtype Rflx_Enumeration_Def is R_F_L_X_Node_Kind_Type
            range Rflx_Named_Enumeration_Def .. Rflx_Positional_Enumeration_Def;
      --% no-document: True
      subtype Rflx_Named_Enumeration_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Named_Enumeration_Def .. Rflx_Named_Enumeration_Def;
      --% no-document: True
      subtype Rflx_Positional_Enumeration_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Positional_Enumeration_Def .. Rflx_Positional_Enumeration_Def;
      --% no-document: True
      subtype Rflx_Enumeration_Type_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Enumeration_Type_Def .. Rflx_Enumeration_Type_Def;
      --% no-document: True
      subtype Rflx_Integer_Type_Def is R_F_L_X_Node_Kind_Type
            range Rflx_Modular_Type_Def .. Rflx_Range_Type_Def;
      --% no-document: True
      subtype Rflx_Modular_Type_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Modular_Type_Def .. Rflx_Modular_Type_Def;
      --% no-document: True
      subtype Rflx_Range_Type_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Range_Type_Def .. Rflx_Range_Type_Def;
      --% no-document: True
      subtype Rflx_Sequence_Type_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Sequence_Type_Def .. Rflx_Sequence_Type_Def;
      --% no-document: True
      subtype Rflx_Type_Derivation_Def_Range is R_F_L_X_Node_Kind_Type
            range Rflx_Type_Derivation_Def .. Rflx_Type_Derivation_Def;
      --% no-document: True

   subtype Synthetic_Nodes is R_F_L_X_Node_Kind_Type
      with Static_Predicate =>
         False
   ;
   --  Set of nodes that are synthetic.
      --
      --  Parsers cannot create synthetic nodes, so these correspond to no
      --  source text. These nodes are created dynamically for convenience
      --  during semantic analysis.

   Default_Grammar_Rule : constant Grammar_Rule := Main_Rule_Rule;
   --  Default grammar rule to use when parsing analysis units

   ------------------
   -- Lexer inputs --
   ------------------

   type Lexer_Input_Kind is
     (File,
      --  Readable source file

      Bytes_Buffer,
      --  Buffer of undecoded bytes

      Text_Buffer
      --  Buffer of decoded bytes
   );
   --  Kind of lexer input

   subtype Undecoded_Lexer_Input is
      Lexer_Input_Kind range File ..  Bytes_Buffer;

   ------------
   -- Tokens --
   ------------

   type Token_Kind is (
      Rflx_Termination,
Rflx_Lexing_Failure,
Rflx_Unqualified_Identifier,
Rflx_Package,
Rflx_Is,
Rflx_If,
Rflx_End,
Rflx_Null,
Rflx_Type,
Rflx_Range,
Rflx_With,
Rflx_Mod,
Rflx_Message,
Rflx_Then,
Rflx_Sequence,
Rflx_Of,
Rflx_In,
Rflx_Not,
Rflx_New,
Rflx_For,
Rflx_When,
Rflx_Where,
Rflx_Use,
Rflx_All,
Rflx_Some,
Rflx_Generic,
Rflx_Session,
Rflx_Begin,
Rflx_Return,
Rflx_Function,
Rflx_State,
Rflx_Transition,
Rflx_Goto,
Rflx_Exception,
Rflx_Renames,
Rflx_Channel,
Rflx_Readable,
Rflx_Writable,
Rflx_Desc,
Rflx_Append,
Rflx_Extend,
Rflx_Read,
Rflx_Write,
Rflx_Reset,
Rflx_High_Order_First,
Rflx_Low_Order_First,
Rflx_Case,
Rflx_First,
Rflx_Size,
Rflx_Last,
Rflx_Byte_Order,
Rflx_Checksum,
Rflx_Valid_Checksum,
Rflx_Has_Data,
Rflx_Head,
Rflx_Opaque,
Rflx_Present,
Rflx_Valid,
Rflx_Dot,
Rflx_Comma,
Rflx_Double_Dot,
Rflx_Tick,
Rflx_Hash,
Rflx_Minus,
Rflx_Arrow,
Rflx_L_Par,
Rflx_R_Par,
Rflx_L_Brack,
Rflx_R_Brack,
Rflx_Exp,
Rflx_Mul,
Rflx_Div,
Rflx_Add,
Rflx_Sub,
Rflx_Eq,
Rflx_Neq,
Rflx_Leq,
Rflx_Lt,
Rflx_Le,
Rflx_Gt,
Rflx_Ge,
Rflx_And,
Rflx_Or,
Rflx_Ampersand,
Rflx_Semicolon,
Rflx_Double_Colon,
Rflx_Assignment,
Rflx_Colon,
Rflx_Pipe,
Rflx_Comment,
Rflx_Numeral,
Rflx_String_Literal
   );
   --  Kind of token: indentifier, string literal, ...

   type Token_Family is
     (Default_Family);
   --  Groups of token kinds, to make the processing of some groups of token
   --  uniform.


   Token_Kind_To_Family : array (Token_Kind) of Token_Family :=
     (Rflx_Termination => Default_Family, Rflx_Lexing_Failure => Default_Family, Rflx_Unqualified_Identifier => Default_Family, Rflx_Package => Default_Family, Rflx_Is => Default_Family, Rflx_If => Default_Family, Rflx_End => Default_Family, Rflx_Null => Default_Family, Rflx_Type => Default_Family, Rflx_Range => Default_Family, Rflx_With => Default_Family, Rflx_Mod => Default_Family, Rflx_Message => Default_Family, Rflx_Then => Default_Family, Rflx_Sequence => Default_Family, Rflx_Of => Default_Family, Rflx_In => Default_Family, Rflx_Not => Default_Family, Rflx_New => Default_Family, Rflx_For => Default_Family, Rflx_When => Default_Family, Rflx_Where => Default_Family, Rflx_Use => Default_Family, Rflx_All => Default_Family, Rflx_Some => Default_Family, Rflx_Generic => Default_Family, Rflx_Session => Default_Family, Rflx_Begin => Default_Family, Rflx_Return => Default_Family, Rflx_Function => Default_Family, Rflx_State => Default_Family, Rflx_Transition => Default_Family, Rflx_Goto => Default_Family, Rflx_Exception => Default_Family, Rflx_Renames => Default_Family, Rflx_Channel => Default_Family, Rflx_Readable => Default_Family, Rflx_Writable => Default_Family, Rflx_Desc => Default_Family, Rflx_Append => Default_Family, Rflx_Extend => Default_Family, Rflx_Read => Default_Family, Rflx_Write => Default_Family, Rflx_Reset => Default_Family, Rflx_High_Order_First => Default_Family, Rflx_Low_Order_First => Default_Family, Rflx_Case => Default_Family, Rflx_First => Default_Family, Rflx_Size => Default_Family, Rflx_Last => Default_Family, Rflx_Byte_Order => Default_Family, Rflx_Checksum => Default_Family, Rflx_Valid_Checksum => Default_Family, Rflx_Has_Data => Default_Family, Rflx_Head => Default_Family, Rflx_Opaque => Default_Family, Rflx_Present => Default_Family, Rflx_Valid => Default_Family, Rflx_Dot => Default_Family, Rflx_Comma => Default_Family, Rflx_Double_Dot => Default_Family, Rflx_Tick => Default_Family, Rflx_Hash => Default_Family, Rflx_Minus => Default_Family, Rflx_Arrow => Default_Family, Rflx_L_Par => Default_Family, Rflx_R_Par => Default_Family, Rflx_L_Brack => Default_Family, Rflx_R_Brack => Default_Family, Rflx_Exp => Default_Family, Rflx_Mul => Default_Family, Rflx_Div => Default_Family, Rflx_Add => Default_Family, Rflx_Sub => Default_Family, Rflx_Eq => Default_Family, Rflx_Neq => Default_Family, Rflx_Leq => Default_Family, Rflx_Lt => Default_Family, Rflx_Le => Default_Family, Rflx_Gt => Default_Family, Rflx_Ge => Default_Family, Rflx_And => Default_Family, Rflx_Or => Default_Family, Rflx_Ampersand => Default_Family, Rflx_Semicolon => Default_Family, Rflx_Double_Colon => Default_Family, Rflx_Assignment => Default_Family, Rflx_Colon => Default_Family, Rflx_Pipe => Default_Family, Rflx_Comment => Default_Family, Rflx_Numeral => Default_Family, Rflx_String_Literal => Default_Family);
   --  Associate a token family to all token kinds
   --
   --% document-value: False

   function Token_Kind_Name (Token_Id : Token_Kind) return String;
   --  Return a human-readable name for a token kind.

   function Token_Kind_Literal (Token_Id : Token_Kind) return Text_Type;
   --  Return the canonical literal corresponding to this token kind, or an
   --  empty string if this token has no literal.

   function Token_Error_Image (Token_Id : Token_Kind) return String;
   --  Return a string representation of ``Token_Id`` that is suitable in error
   --  messages.

   function To_Token_Kind (Raw : Raw_Token_Kind) return Token_Kind
      with Inline;
   function From_Token_Kind (Kind : Token_Kind) return Raw_Token_Kind
      with Inline;

   function Is_Token_Node (Kind : R_F_L_X_Node_Kind_Type) return Boolean;
   --  Return whether Kind corresponds to a token node

   function Is_List_Node (Kind : R_F_L_X_Node_Kind_Type) return Boolean;
   --  Return whether Kind corresponds to a list node

   function Is_Error_Node (Kind : R_F_L_X_Node_Kind_Type) return Boolean;
   --  Return whether Kind corresponds to an error node

   type Visit_Status is (Into, Over, Stop);
   --  Helper type to control the node traversal process. See the
   --  ``Librflxlang.Analysis.Traverse`` function.

   -----------------------
   -- Lexical utilities --
   -----------------------

   type Token_Reference is private;
   --  Reference to a token in an analysis unit.

   No_Token : constant Token_Reference;

   type Token_Data_Type is private;

   function "<" (Left, Right : Token_Reference) return Boolean;
   --  Assuming ``Left`` and ``Right`` belong to the same analysis unit, return
   --  whether ``Left`` came before ``Right`` in the source file.

   function Next
     (Token          : Token_Reference;
      Exclude_Trivia : Boolean := False) return Token_Reference;
   --  Return a reference to the next token in the corresponding analysis unit.

   function Previous
     (Token          : Token_Reference;
      Exclude_Trivia : Boolean := False) return Token_Reference;
   --  Return a reference to the previous token in the corresponding analysis
   --  unit.

   function Data (Token : Token_Reference) return Token_Data_Type;
   --  Return the data associated to ``Token``

   function Is_Equivalent (L, R : Token_Reference) return Boolean;
   --  Return whether ``L`` and ``R`` are structurally equivalent tokens. This
   --  means that their position in the stream won't be taken into account,
   --  only the kind and text of the token.

   function Image (Token : Token_Reference) return String;
   --  Debug helper: return a human-readable text to represent a token

   function Text (Token : Token_Reference) return Text_Type;
   --  Return the text of the token as ``Text_Type``

   function Text (First, Last : Token_Reference) return Text_Type;
   --  Compute the source buffer slice corresponding to the text that spans
   --  between the ``First`` and ``Last`` tokens (both included). This yields
   --  an empty slice if ``Last`` actually appears before ``First``.
   --
   --  This raises a ``Constraint_Error`` if ``First`` and ``Last`` don't
   --  belong to the same analysis unit.

   function Get_Symbol (Token : Token_Reference) return Symbol_Type;
   --  Assuming that ``Token`` refers to a token that contains a symbol, return
   --  the corresponding symbol.

   function Kind (Token_Data : Token_Data_Type) return Token_Kind;
   --  Kind for this token.

   function Is_Trivia (Token : Token_Reference) return Boolean;
   --  Return whether this token is a trivia. If it's not, it's a regular
   --  token.

   function Is_Trivia (Token_Data : Token_Data_Type) return Boolean;
   --  Return whether this token is a trivia. If it's not, it's a regular
   --  token.

   function Index (Token : Token_Reference) return Token_Index;
   --  One-based index for this token/trivia. Tokens and trivias get their own
   --  index space.

   function Index (Token_Data : Token_Data_Type) return Token_Index;
   --  One-based index for this token/trivia. Tokens and trivias get their own
   --  index space.

   function Sloc_Range
     (Token_Data : Token_Data_Type) return Source_Location_Range;
   --  Source location range for this token. Note that the end bound is
   --  exclusive.

   function Origin_Filename (Token : Token_Reference) return String;
   --  Return the name of the file whose content was scanned to create Token.
   --  Return an empty string if the source comes from a memory buffer instead
   --  of a file.

   function Origin_Charset (Token : Token_Reference) return String;
   --  Return the charset used to decode the source that was scanned to create
   --  Token. Return an empty string if the source was already decoded during
   --  the scan.

   function Convert
     (TDH      : Token_Data_Handler;
      Token    : Token_Reference;
      Raw_Data : Stored_Token_Data) return Token_Data_Type;
   --  Turn data from ``TDH`` and ``Raw_Data`` into a user-ready token data
   --  record.

   type Child_Or_Trivia is (Child, Trivia);
   --  Discriminator for the ``Child_Record`` type

   function Raw_Data (T : Token_Reference) return Stored_Token_Data;
   --  Return the raw token data for ``T``

   function Token_Node_Kind (Kind : R_F_L_X_Node_Kind_Type) return Token_Kind
      with Pre => Is_Token_Node (Kind);
   --  Return the token kind corresponding to the given token node kind
   --
   --  As unparser are not generated, this always raises a ``Program_Error``
   --  exception.

   


private

   type Token_Safety_Net is record
      Context         : Langkit_Support.Internal.Analysis.Internal_Context;
      Context_Version : Version_Number;
      --  Analysis context and version number at the time this safety net was
      --  produced.
      --
      --  TODO: it is not possible to refer to
      --  $.Implementation.Internal_Context from this spec (otherwise we get a
      --  circular dependency). For now, use the generic pointer from
      --  Langkit_Support (hack), but in the future the Token_Reference type
      --  (and this this safety net type) will go to the generic API, so we
      --  will get rid of this hack.

      TDH_Version : Version_Number;
      --  Version of the token data handler at the time this safety net was
      --  produced.
   end record;
   --  Information to embed in public APIs with token references, used to check
   --  before using the references that they are not stale.

   No_Token_Safety_Net : constant Token_Safety_Net :=
     (Langkit_Support.Internal.Analysis.No_Internal_Context, 0, 0);

   type Token_Reference is record
      TDH : Token_Data_Handler_Access;
      --  Token data handler that owns this token

      Index : Token_Or_Trivia_Index;
      --  Identifier for the trivia or the token this refers to

      Safety_Net : Token_Safety_Net;
   end record;

   procedure Check_Safety_Net (Self : Token_Reference);
   --  If ``Self`` is a stale token reference, raise a
   --  ``Stale_Reference_Error`` error.

   No_Token : constant Token_Reference :=
     (null, No_Token_Or_Trivia_Index, No_Token_Safety_Net);

   type Token_Data_Type is record
      Kind : Token_Kind;
      --  See documentation for the Kind accessor

      Is_Trivia : Boolean;
      --  See documentation for the Is_Trivia accessor

      Index : Token_Index;
      --  See documentation for the Index accessor

      Source_Buffer : Text_Cst_Access;
      --  Text for the original source file

      Source_First : Positive;
      Source_Last  : Natural;
      --  Bounds in Source_Buffer for the text corresponding to this token

      Sloc_Range : Source_Location_Range;
      --  See documenation for the Sloc_Range accessor
   end record;

end Librflxlang.Common;
