
with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;
with Ada.Unchecked_Conversion;

with System;

with GNATCOLL.Iconv;
with GNATCOLL.VFS; use GNATCOLL.VFS;

with Langkit_Support.Generic_API; use Langkit_Support.Generic_API;
with Langkit_Support.Generic_API.Analysis;
use Langkit_Support.Generic_API.Analysis;
with Langkit_Support.Internal.Analysis;
with Langkit_Support.Internal.Conversions;

with Librflxlang.Generic_API;
with Librflxlang.Implementation; use Librflxlang.Implementation;
with Librflxlang.Lexer_Implementation;
use Librflxlang.Lexer_Implementation;
with Librflxlang.Private_Converters;


package body Librflxlang.Common is

   Is_Token_Node_Kind : constant array (R_F_L_X_Node_Kind_Type) of Boolean :=
     (Rflx_I_D => False, Rflx_Unqualified_I_D => True, Rflx_Aspect => False, Rflx_Attr_First => False, Rflx_Attr_Has_Data => False, Rflx_Attr_Head => False, Rflx_Attr_Last => False, Rflx_Attr_Opaque => False, Rflx_Attr_Present => False, Rflx_Attr_Size => False, Rflx_Attr_Valid => False, Rflx_Attr_Valid_Checksum => False, Rflx_Attr_Stmt_Append => False, Rflx_Attr_Stmt_Extend => False, Rflx_Attr_Stmt_Read => False, Rflx_Attr_Stmt_Write => False, Rflx_Message_Aggregate_Associations => False, Rflx_Null_Message_Aggregate => False, Rflx_Checksum_Val => False, Rflx_Checksum_Value_Range => False, Rflx_Byte_Order_Type_Highorderfirst => False, Rflx_Byte_Order_Type_Loworderfirst => False, Rflx_Readable => False, Rflx_Writable => False, Rflx_Checksum_Assoc => False, Rflx_Refinement_Decl => False, Rflx_Session_Decl => False, Rflx_Type_Decl => False, Rflx_Description => False, Rflx_Element_Value_Assoc => False, Rflx_Attribute => False, Rflx_Bin_Op => False, Rflx_Binding => False, Rflx_Call => False, Rflx_Case_Expression => False, Rflx_Choice => False, Rflx_Comprehension => False, Rflx_Context_Item => False, Rflx_Conversion => False, Rflx_Message_Aggregate => False, Rflx_Negation => False, Rflx_Numeric_Literal => True, Rflx_Paren_Expression => False, Rflx_Quantified_Expression => False, Rflx_Select_Node => False, Rflx_Concatenation => False, Rflx_Sequence_Aggregate => False, Rflx_String_Literal => True, Rflx_Variable => False, Rflx_Formal_Channel_Decl => False, Rflx_Formal_Function_Decl => False, Rflx_Renaming_Decl => False, Rflx_Variable_Decl => False, Rflx_Message_Aggregate_Association => False, Rflx_Byte_Order_Aspect => False, Rflx_Checksum_Aspect => False, Rflx_Message_Field => False, Rflx_Message_Fields => False, Rflx_Null_Message_Field => False, Rflx_Op_Add => False, Rflx_Op_And => False, Rflx_Op_Div => False, Rflx_Op_Eq => False, Rflx_Op_Ge => False, Rflx_Op_Gt => False, Rflx_Op_In => False, Rflx_Op_Le => False, Rflx_Op_Lt => False, Rflx_Op_Mod => False, Rflx_Op_Mul => False, Rflx_Op_Neq => False, Rflx_Op_Notin => False, Rflx_Op_Or => False, Rflx_Op_Pow => False, Rflx_Op_Sub => False, Rflx_Package_Node => False, Rflx_Parameter => False, Rflx_Parameters => False, Rflx_Quantifier_All => False, Rflx_Quantifier_Some => False, Rflx_Aspect_List => False, Rflx_Base_Checksum_Val_List => False, Rflx_Channel_Attribute_List => False, Rflx_Checksum_Assoc_List => False, Rflx_Choice_List => False, Rflx_Conditional_Transition_List => False, Rflx_Context_Item_List => False, Rflx_Declaration_List => False, Rflx_Element_Value_Assoc_List => False, Rflx_Expr_List => False, Rflx_Formal_Decl_List => False, Rflx_Local_Decl_List => False, Rflx_Message_Aggregate_Association_List => False, Rflx_Message_Aspect_List => False, Rflx_Message_Field_List => False, Rflx_Numeric_Literal_List => False, Rflx_Parameter_List => False, Rflx_R_F_L_X_Node_List => False, Rflx_State_List => False, Rflx_Statement_List => False, Rflx_Term_Assoc_List => False, Rflx_Then_Node_List => False, Rflx_Type_Argument_List => False, Rflx_Unqualified_I_D_List => False, Rflx_Specification => False, Rflx_State => False, Rflx_State_Body => False, Rflx_Assignment => False, Rflx_Attribute_Statement => False, Rflx_Message_Field_Assignment => False, Rflx_Reset => False, Rflx_Term_Assoc => False, Rflx_Then_Node => False, Rflx_Transition => False, Rflx_Conditional_Transition => False, Rflx_Type_Argument => False, Rflx_Message_Type_Def => False, Rflx_Null_Message_Type_Def => False, Rflx_Named_Enumeration_Def => False, Rflx_Positional_Enumeration_Def => False, Rflx_Enumeration_Type_Def => False, Rflx_Modular_Type_Def => False, Rflx_Range_Type_Def => False, Rflx_Sequence_Type_Def => False, Rflx_Type_Derivation_Def => False);
   --  For each node kind, return whether it is a node that contains only a
   --  single token.

   Is_Error_Node_Kind : constant array (R_F_L_X_Node_Kind_Type) of Boolean :=
     (Rflx_I_D => False, Rflx_Unqualified_I_D => False, Rflx_Aspect => False, Rflx_Attr_First => False, Rflx_Attr_Has_Data => False, Rflx_Attr_Head => False, Rflx_Attr_Last => False, Rflx_Attr_Opaque => False, Rflx_Attr_Present => False, Rflx_Attr_Size => False, Rflx_Attr_Valid => False, Rflx_Attr_Valid_Checksum => False, Rflx_Attr_Stmt_Append => False, Rflx_Attr_Stmt_Extend => False, Rflx_Attr_Stmt_Read => False, Rflx_Attr_Stmt_Write => False, Rflx_Message_Aggregate_Associations => False, Rflx_Null_Message_Aggregate => False, Rflx_Checksum_Val => False, Rflx_Checksum_Value_Range => False, Rflx_Byte_Order_Type_Highorderfirst => False, Rflx_Byte_Order_Type_Loworderfirst => False, Rflx_Readable => False, Rflx_Writable => False, Rflx_Checksum_Assoc => False, Rflx_Refinement_Decl => False, Rflx_Session_Decl => False, Rflx_Type_Decl => False, Rflx_Description => False, Rflx_Element_Value_Assoc => False, Rflx_Attribute => False, Rflx_Bin_Op => False, Rflx_Binding => False, Rflx_Call => False, Rflx_Case_Expression => False, Rflx_Choice => False, Rflx_Comprehension => False, Rflx_Context_Item => False, Rflx_Conversion => False, Rflx_Message_Aggregate => False, Rflx_Negation => False, Rflx_Numeric_Literal => False, Rflx_Paren_Expression => False, Rflx_Quantified_Expression => False, Rflx_Select_Node => False, Rflx_Concatenation => False, Rflx_Sequence_Aggregate => False, Rflx_String_Literal => False, Rflx_Variable => False, Rflx_Formal_Channel_Decl => False, Rflx_Formal_Function_Decl => False, Rflx_Renaming_Decl => False, Rflx_Variable_Decl => False, Rflx_Message_Aggregate_Association => False, Rflx_Byte_Order_Aspect => False, Rflx_Checksum_Aspect => False, Rflx_Message_Field => False, Rflx_Message_Fields => False, Rflx_Null_Message_Field => False, Rflx_Op_Add => False, Rflx_Op_And => False, Rflx_Op_Div => False, Rflx_Op_Eq => False, Rflx_Op_Ge => False, Rflx_Op_Gt => False, Rflx_Op_In => False, Rflx_Op_Le => False, Rflx_Op_Lt => False, Rflx_Op_Mod => False, Rflx_Op_Mul => False, Rflx_Op_Neq => False, Rflx_Op_Notin => False, Rflx_Op_Or => False, Rflx_Op_Pow => False, Rflx_Op_Sub => False, Rflx_Package_Node => False, Rflx_Parameter => False, Rflx_Parameters => False, Rflx_Quantifier_All => False, Rflx_Quantifier_Some => False, Rflx_Aspect_List => False, Rflx_Base_Checksum_Val_List => False, Rflx_Channel_Attribute_List => False, Rflx_Checksum_Assoc_List => False, Rflx_Choice_List => False, Rflx_Conditional_Transition_List => False, Rflx_Context_Item_List => False, Rflx_Declaration_List => False, Rflx_Element_Value_Assoc_List => False, Rflx_Expr_List => False, Rflx_Formal_Decl_List => False, Rflx_Local_Decl_List => False, Rflx_Message_Aggregate_Association_List => False, Rflx_Message_Aspect_List => False, Rflx_Message_Field_List => False, Rflx_Numeric_Literal_List => False, Rflx_Parameter_List => False, Rflx_R_F_L_X_Node_List => False, Rflx_State_List => False, Rflx_Statement_List => False, Rflx_Term_Assoc_List => False, Rflx_Then_Node_List => False, Rflx_Type_Argument_List => False, Rflx_Unqualified_I_D_List => False, Rflx_Specification => False, Rflx_State => False, Rflx_State_Body => False, Rflx_Assignment => False, Rflx_Attribute_Statement => False, Rflx_Message_Field_Assignment => False, Rflx_Reset => False, Rflx_Term_Assoc => False, Rflx_Then_Node => False, Rflx_Transition => False, Rflx_Conditional_Transition => False, Rflx_Type_Argument => False, Rflx_Message_Type_Def => False, Rflx_Null_Message_Type_Def => False, Rflx_Named_Enumeration_Def => False, Rflx_Positional_Enumeration_Def => False, Rflx_Enumeration_Type_Def => False, Rflx_Modular_Type_Def => False, Rflx_Range_Type_Def => False, Rflx_Sequence_Type_Def => False, Rflx_Type_Derivation_Def => False);
   --  For each node kind, return whether it is an error node

   function Wrap_Token_Reference
     (Context : Internal_Context;
      TDH     : Token_Data_Handler_Access;
      Index   : Token_Or_Trivia_Index) return Token_Reference;
   function Get_Token_Context (Token : Token_Reference) return Internal_Context;
   function Get_Token_Unit (Token : Token_Reference) return Internal_Unit;
   function Get_Token_TDH
     (Token : Token_Reference) return Token_Data_Handler_Access;
   function Get_Token_Index
     (Token : Token_Reference) return Token_Or_Trivia_Index;
   procedure Extract_Token_Text
     (Token         : Token_Data_Type;
      Source_Buffer : out Text_Cst_Access;
      First         : out Positive;
      Last          : out Natural);
   --  Implementations for converters soft-links

   function From_Generic (Token : Lk_Token) return Common.Token_Reference
     with Export, External_Name => "Librflxlang__from_generic_token";
   function To_Generic (Token : Common.Token_Reference) return Lk_Token
     with Export, External_Name => "Librflxlang__to_generic_token";
   --  Implementation for converters hard-links in Private_Converters

   function "+" is new Ada.Unchecked_Conversion
     (Langkit_Support.Internal.Analysis.Internal_Context, Internal_Context);
   function "+" is new Ada.Unchecked_Conversion
     (Internal_Context, Langkit_Support.Internal.Analysis.Internal_Context);

   function Rewrap_Token
     (Origin : Token_Reference;
      Index  : Token_Or_Trivia_Index) return Token_Reference;
   --  Create a token reference for ``Index`` using the token data handler
   --  reference from ``Origin``.

   Token_Kind_To_Literals : constant array (Token_Kind) of Text_Access := (
   

         Rflx_Unqualified_Identifier => new Text_Type'("First"),
         
         Rflx_Valid_Checksum => new Text_Type'("Valid_Checksum"),
         
         Rflx_Has_Data => new Text_Type'("Has_Data"),
         
         Rflx_Head => new Text_Type'("Head"),
         
         Rflx_Opaque => new Text_Type'("Opaque"),
         
         Rflx_Present => new Text_Type'("Present"),
         
         Rflx_Valid => new Text_Type'("Valid"),
         
         Rflx_Checksum => new Text_Type'("Checksum"),
         
         Rflx_Package => new Text_Type'("package"),
         
         Rflx_Is => new Text_Type'("is"),
         
         Rflx_If => new Text_Type'("if"),
         
         Rflx_End => new Text_Type'("end"),
         
         Rflx_Null => new Text_Type'("null"),
         
         Rflx_Type => new Text_Type'("type"),
         
         Rflx_Range => new Text_Type'("range"),
         
         Rflx_With => new Text_Type'("with"),
         
         Rflx_Mod => new Text_Type'("mod"),
         
         Rflx_Message => new Text_Type'("message"),
         
         Rflx_Then => new Text_Type'("then"),
         
         Rflx_Sequence => new Text_Type'("sequence"),
         
         Rflx_Of => new Text_Type'("of"),
         
         Rflx_In => new Text_Type'("in"),
         
         Rflx_Not => new Text_Type'("not"),
         
         Rflx_New => new Text_Type'("new"),
         
         Rflx_For => new Text_Type'("for"),
         
         Rflx_When => new Text_Type'("when"),
         
         Rflx_Where => new Text_Type'("where"),
         
         Rflx_Use => new Text_Type'("use"),
         
         Rflx_All => new Text_Type'("all"),
         
         Rflx_Some => new Text_Type'("some"),
         
         Rflx_Generic => new Text_Type'("generic"),
         
         Rflx_Session => new Text_Type'("session"),
         
         Rflx_Begin => new Text_Type'("begin"),
         
         Rflx_Return => new Text_Type'("return"),
         
         Rflx_Function => new Text_Type'("function"),
         
         Rflx_State => new Text_Type'("state"),
         
         Rflx_Transition => new Text_Type'("transition"),
         
         Rflx_Goto => new Text_Type'("goto"),
         
         Rflx_Exception => new Text_Type'("exception"),
         
         Rflx_Renames => new Text_Type'("renames"),
         
         Rflx_Case => new Text_Type'("case"),
         
         Rflx_Channel => new Text_Type'("Channel"),
         
         Rflx_Readable => new Text_Type'("Readable"),
         
         Rflx_Writable => new Text_Type'("Writable"),
         
         Rflx_Desc => new Text_Type'("Desc"),
         
         Rflx_Append => new Text_Type'("Append"),
         
         Rflx_Extend => new Text_Type'("Extend"),
         
         Rflx_Read => new Text_Type'("Read"),
         
         Rflx_Write => new Text_Type'("Write"),
         
         Rflx_Reset => new Text_Type'("Reset"),
         
         Rflx_Byte_Order => new Text_Type'("Byte_Order"),
         
         Rflx_High_Order_First => new Text_Type'("High_Order_First"),
         
         Rflx_Low_Order_First => new Text_Type'("Low_Order_First"),
         
         Rflx_Semicolon => new Text_Type'(";"),
         
         Rflx_Double_Colon => new Text_Type'("::"),
         
         Rflx_Assignment => new Text_Type'(":="),
         
         Rflx_Colon => new Text_Type'(":"),
         
         Rflx_L_Par => new Text_Type'("("),
         
         Rflx_R_Par => new Text_Type'(")"),
         
         Rflx_L_Brack => new Text_Type'("["),
         
         Rflx_R_Brack => new Text_Type'("]"),
         
         Rflx_Double_Dot => new Text_Type'(".."),
         
         Rflx_Dot => new Text_Type'("."),
         
         Rflx_Comma => new Text_Type'(","),
         
         Rflx_Tick => new Text_Type'("'"),
         
         Rflx_Hash => new Text_Type'("#"),
         
         Rflx_Exp => new Text_Type'("**"),
         
         Rflx_Mul => new Text_Type'("*"),
         
         Rflx_Neq => new Text_Type'("/="),
         
         Rflx_Div => new Text_Type'("/"),
         
         Rflx_Add => new Text_Type'("+"),
         
         Rflx_Sub => new Text_Type'("-"),
         
         Rflx_Eq => new Text_Type'("="),
         
         Rflx_Le => new Text_Type'("<="),
         
         Rflx_Lt => new Text_Type'("<"),
         
         Rflx_Ge => new Text_Type'(">="),
         
         Rflx_Gt => new Text_Type'(">"),
         
         Rflx_Pipe => new Text_Type'("|"),
         
         Rflx_And => new Text_Type'("and"),
         
         Rflx_Or => new Text_Type'("or"),
         
         Rflx_Ampersand => new Text_Type'("&"),
         
         Rflx_Arrow => new Text_Type'("=>"),
         
      others => new Text_Type'("")
   );

   Token_Kind_Names : constant array (Token_Kind) of String_Access := (
          Rflx_Unqualified_Identifier =>
             new String'("Unqualified_Identifier")
              ,
          Rflx_Package =>
             new String'("Package")
              ,
          Rflx_Is =>
             new String'("Is")
              ,
          Rflx_If =>
             new String'("If")
              ,
          Rflx_End =>
             new String'("End")
              ,
          Rflx_Null =>
             new String'("Null")
              ,
          Rflx_Type =>
             new String'("Type")
              ,
          Rflx_Range =>
             new String'("Range")
              ,
          Rflx_With =>
             new String'("With")
              ,
          Rflx_Mod =>
             new String'("Mod")
              ,
          Rflx_Message =>
             new String'("Message")
              ,
          Rflx_Then =>
             new String'("Then")
              ,
          Rflx_Sequence =>
             new String'("Sequence")
              ,
          Rflx_Of =>
             new String'("Of")
              ,
          Rflx_In =>
             new String'("In")
              ,
          Rflx_Not =>
             new String'("Not")
              ,
          Rflx_New =>
             new String'("New")
              ,
          Rflx_For =>
             new String'("For")
              ,
          Rflx_When =>
             new String'("When")
              ,
          Rflx_Where =>
             new String'("Where")
              ,
          Rflx_Use =>
             new String'("Use")
              ,
          Rflx_All =>
             new String'("All")
              ,
          Rflx_Some =>
             new String'("Some")
              ,
          Rflx_Generic =>
             new String'("Generic")
              ,
          Rflx_Session =>
             new String'("Session")
              ,
          Rflx_Begin =>
             new String'("Begin")
              ,
          Rflx_Return =>
             new String'("Return")
              ,
          Rflx_Function =>
             new String'("Function")
              ,
          Rflx_State =>
             new String'("State")
              ,
          Rflx_Transition =>
             new String'("Transition")
              ,
          Rflx_Goto =>
             new String'("Goto")
              ,
          Rflx_Exception =>
             new String'("Exception")
              ,
          Rflx_Renames =>
             new String'("Renames")
              ,
          Rflx_Channel =>
             new String'("Channel")
              ,
          Rflx_Readable =>
             new String'("Readable")
              ,
          Rflx_Writable =>
             new String'("Writable")
              ,
          Rflx_Desc =>
             new String'("Desc")
              ,
          Rflx_Append =>
             new String'("Append")
              ,
          Rflx_Extend =>
             new String'("Extend")
              ,
          Rflx_Read =>
             new String'("Read")
              ,
          Rflx_Write =>
             new String'("Write")
              ,
          Rflx_Reset =>
             new String'("Reset")
              ,
          Rflx_High_Order_First =>
             new String'("High_Order_First")
              ,
          Rflx_Low_Order_First =>
             new String'("Low_Order_First")
              ,
          Rflx_Case =>
             new String'("Case")
              ,
          Rflx_First =>
             new String'("First")
              ,
          Rflx_Size =>
             new String'("Size")
              ,
          Rflx_Last =>
             new String'("Last")
              ,
          Rflx_Byte_Order =>
             new String'("Byte_Order")
              ,
          Rflx_Checksum =>
             new String'("Checksum")
              ,
          Rflx_Valid_Checksum =>
             new String'("Valid_Checksum")
              ,
          Rflx_Has_Data =>
             new String'("Has_Data")
              ,
          Rflx_Head =>
             new String'("Head")
              ,
          Rflx_Opaque =>
             new String'("Opaque")
              ,
          Rflx_Present =>
             new String'("Present")
              ,
          Rflx_Valid =>
             new String'("Valid")
              ,
          Rflx_Dot =>
             new String'("Dot")
              ,
          Rflx_Comma =>
             new String'("Comma")
              ,
          Rflx_Double_Dot =>
             new String'("Double_Dot")
              ,
          Rflx_Tick =>
             new String'("Tick")
              ,
          Rflx_Hash =>
             new String'("Hash")
              ,
          Rflx_Minus =>
             new String'("Minus")
              ,
          Rflx_Arrow =>
             new String'("Arrow")
              ,
          Rflx_L_Par =>
             new String'("L_Par")
              ,
          Rflx_R_Par =>
             new String'("R_Par")
              ,
          Rflx_L_Brack =>
             new String'("L_Brack")
              ,
          Rflx_R_Brack =>
             new String'("R_Brack")
              ,
          Rflx_Exp =>
             new String'("Exp")
              ,
          Rflx_Mul =>
             new String'("Mul")
              ,
          Rflx_Div =>
             new String'("Div")
              ,
          Rflx_Add =>
             new String'("Add")
              ,
          Rflx_Sub =>
             new String'("Sub")
              ,
          Rflx_Eq =>
             new String'("Eq")
              ,
          Rflx_Neq =>
             new String'("Neq")
              ,
          Rflx_Leq =>
             new String'("Leq")
              ,
          Rflx_Lt =>
             new String'("Lt")
              ,
          Rflx_Le =>
             new String'("Le")
              ,
          Rflx_Gt =>
             new String'("Gt")
              ,
          Rflx_Ge =>
             new String'("Ge")
              ,
          Rflx_And =>
             new String'("And")
              ,
          Rflx_Or =>
             new String'("Or")
              ,
          Rflx_Ampersand =>
             new String'("Ampersand")
              ,
          Rflx_Semicolon =>
             new String'("Semicolon")
              ,
          Rflx_Double_Colon =>
             new String'("Double_Colon")
              ,
          Rflx_Assignment =>
             new String'("Assignment")
              ,
          Rflx_Colon =>
             new String'("Colon")
              ,
          Rflx_Pipe =>
             new String'("Pipe")
              ,
          Rflx_Comment =>
             new String'("Comment")
              ,
          Rflx_Numeral =>
             new String'("Numeral")
              ,
          Rflx_String_Literal =>
             new String'("String_Literal")
              ,
          Rflx_Termination =>
             new String'("Termination")
              ,
          Rflx_Lexing_Failure =>
             new String'("Lexing_Failure")
   );

   ---------------------
   -- Token_Kind_Name --
   ---------------------

   function Token_Kind_Name (Token_Id : Token_Kind) return String is
     (Token_Kind_Names (Token_Id).all);

   ------------------------
   -- Token_Kind_Literal --
   ------------------------

   function Token_Kind_Literal (Token_Id : Token_Kind) return Text_Type is
     (Token_Kind_To_Literals (Token_Id).all);

   -----------------------
   -- Token_Error_Image --
   -----------------------

   function Token_Error_Image (Token_Id : Token_Kind) return String is
      Literal : constant Text_Type := Token_Kind_Literal (Token_Id);
   begin
      return (if Literal /= ""
              then "'" & Image (Literal) & "'"
              else Token_Kind_Name (Token_Id));
   end Token_Error_Image;

   function To_Token_Kind (Raw : Raw_Token_Kind) return Token_Kind
   is (Token_Kind'Val (Raw));

   function From_Token_Kind (Kind : Token_Kind) return Raw_Token_Kind
   is (Token_Kind'Pos (Kind));

   -------------------
   -- Is_Token_Node --
   -------------------

   function Is_Token_Node (Kind : R_F_L_X_Node_Kind_Type) return Boolean is
   begin
      return Is_Token_Node_Kind (Kind);
   end Is_Token_Node;

   -------------------
   -- Is_Error_Node --
   -------------------

   function Is_Error_Node (Kind : R_F_L_X_Node_Kind_Type) return Boolean is
   begin
      return Is_Error_Node_Kind (Kind);
   end Is_Error_Node;

   ------------------
   -- Is_List_Node --
   ------------------

   function Is_List_Node (Kind : R_F_L_X_Node_Kind_Type) return Boolean is
   begin
         return Kind in Rflx_R_F_L_X_Node_Base_List;
   end Is_List_Node;

   ------------------
   -- Rewrap_Token --
   ------------------

   function Rewrap_Token
     (Origin : Token_Reference;
      Index  : Token_Or_Trivia_Index) return Token_Reference is
   begin
      return (if Index = No_Token_Or_Trivia_Index
              then No_Token
              else (Origin.TDH, Index, Origin.Safety_Net));
   end Rewrap_Token;

   ----------------------
   -- Check_Safety_Net --
   ----------------------

   procedure Check_Safety_Net (Self : Token_Reference) is
      SN  : Token_Safety_Net renames Self.Safety_Net;
      Ctx : constant Internal_Context := +SN.Context;
   begin
      if Self.TDH /= null
         and then (Ctx.Serial_Number /= SN.Context_Version
                   or else Self.TDH.Version /= SN.TDH_Version)
      then
         raise Stale_Reference_Error;
      end if;
   end Check_Safety_Net;

   ---------
   -- "<" --
   ---------

   function "<" (Left, Right : Token_Reference) return Boolean is
      pragma Assert (Left.TDH = Right.TDH);
   begin
      Check_Safety_Net (Left);
      Check_Safety_Net (Right);
      if Left.Index.Token < Right.Index.Token then
         return True;

      elsif Left.Index.Token = Right.Index.Token then
         return Left.Index.Trivia < Right.Index.Trivia;

      else
         return False;
      end if;
   end "<";

   ----------
   -- Next --
   ----------

   function Next
     (Token          : Token_Reference;
      Exclude_Trivia : Boolean := False) return Token_Reference is
   begin
      Check_Safety_Net (Token);
      return (if Token.TDH = null
              then No_Token
              else Rewrap_Token (Token,
                                 Next (Token.Index, Token.TDH.all,
                                       Exclude_Trivia)));
   end Next;

   --------------
   -- Previous --
   --------------

   function Previous
     (Token          : Token_Reference;
      Exclude_Trivia : Boolean := False) return Token_Reference is
   begin
      Check_Safety_Net (Token);
      return (if Token.TDH = null
              then No_Token
              else Rewrap_Token (Token,
                                 Previous (Token.Index, Token.TDH.all,
                                           Exclude_Trivia)));
   end Previous;

   ----------------
   -- Get_Symbol --
   ----------------

   function Get_Symbol (Token : Token_Reference) return Symbol_Type is
   begin
      Check_Safety_Net (Token);
      if Token.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      return Get_Symbol (Token.Index, Token.TDH.all);
   end Get_Symbol;

   ----------
   -- Data --
   ----------

   function Data (Token : Token_Reference) return Token_Data_Type is
   begin
      Check_Safety_Net (Token);
      if Token.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      return Convert (Token.TDH.all, Token, Raw_Data (Token));
   end Data;

   ----------
   -- Text --
   ----------

   function Text (Token : Token_Reference) return Text_Type is
      RD : constant Stored_Token_Data := Raw_Data (Token);
   begin
      Check_Safety_Net (Token);
      if Token.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      return Token.TDH.Source_Buffer (RD.Source_First .. RD.Source_Last);
   end Text;

   ----------
   -- Text --
   ----------

   function Text (First, Last : Token_Reference) return Text_Type is
      FD, LD : Token_Data_Type;
   begin
      Check_Safety_Net (First);
      Check_Safety_Net (Last);
      if First.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      if First.TDH /= Last.TDH then
         raise Precondition_Failure with
            "token arguments must belong to the same source";
      end if;
      FD := Data (First);
      LD := Data (Last);
      return FD.Source_Buffer.all (FD.Source_First .. LD.Source_Last);
   end Text;

   ----------
   -- Kind --
   ----------

   function Kind (Token_Data : Token_Data_Type) return Token_Kind is
   begin
      return Token_Data.Kind;
   end Kind;

   ---------------
   -- Is_Trivia --
   ---------------

   function Is_Trivia (Token : Token_Reference) return Boolean is
   begin
      Check_Safety_Net (Token);
      return Token.Index.Trivia /= No_Token_Index;
   end Is_Trivia;

   ---------------
   -- Is_Trivia --
   ---------------

   function Is_Trivia (Token_Data : Token_Data_Type) return Boolean is
   begin
      return Token_Data.Is_Trivia;
   end Is_Trivia;

   -----------
   -- Index --
   -----------

   function Index (Token : Token_Reference) return Token_Index is
   begin
      Check_Safety_Net (Token);
      return (if Token.Index.Trivia = No_Token_Index
              then Token.Index.Token
              else Token.Index.Trivia);
   end Index;

   -----------
   -- Index --
   -----------

   function Index (Token_Data : Token_Data_Type) return Token_Index is
   begin
      return Token_Data.Index;
   end Index;

   ----------------
   -- Sloc_Range --
   ----------------

   function Sloc_Range
     (Token_Data : Token_Data_Type) return Source_Location_Range
   is
   begin
      return Token_Data.Sloc_Range;
   end Sloc_Range;

   ---------------------
   -- Origin_Filename --
   ---------------------

   function Origin_Filename (Token : Token_Reference) return String is
   begin
      Check_Safety_Net (Token);
      if Token.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      return +Token.TDH.Filename.Full_Name;
   end Origin_Filename;

   --------------------
   -- Origin_Charset --
   --------------------

   function Origin_Charset (Token : Token_Reference) return String is
   begin
      Check_Safety_Net (Token);
      if Token.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      return To_String (Token.TDH.Charset);
   end Origin_Charset;

   -------------------
   -- Is_Equivalent --
   -------------------

   function Is_Equivalent (L, R : Token_Reference) return Boolean is
      DL : constant Token_Data_Type := Data (L);
      DR : constant Token_Data_Type := Data (R);
      TL : constant Text_Type := Text (L);
      TR : constant Text_Type := Text (R);
   begin
      return DL.Kind = DR.Kind and then TL = TR;
   end Is_Equivalent;

   -----------
   -- Image --
   -----------

   function Image (Token : Token_Reference) return String is
      D : constant Token_Data_Type := Data (Token);
   begin
      return ("<Token Kind=" & Token_Kind_Name (D.Kind) &
              " Text=" & Image (Text (Token), With_Quotes => True) & ">");
   end Image;

   --------------
   -- Raw_Data --
   --------------

   function Raw_Data (T : Token_Reference) return Stored_Token_Data is
   begin
      Check_Safety_Net (T);
      if T.TDH = null then
         raise Precondition_Failure with "null token argument";
      end if;
      return
        (if T.Index.Trivia = No_Token_Index
         then Token_Vectors.Get (T.TDH.Tokens, Natural (T.Index.Token))
         else Trivia_Vectors.Get (T.TDH.Trivias, Natural (T.Index.Trivia)).T);
   end Raw_Data;

   -------------
   -- Convert --
   -------------

   function Convert
     (TDH      : Token_Data_Handler;
      Token    : Token_Reference;
      Raw_Data : Stored_Token_Data) return Token_Data_Type is
   begin
      Check_Safety_Net (Token);
      return (Kind          => To_Token_Kind (Raw_Data.Kind),
              Is_Trivia     => Token.Index.Trivia /= No_Token_Index,
              Index         => (if Token.Index.Trivia = No_Token_Index
                                then Token.Index.Token
                                else Token.Index.Trivia),
              Source_Buffer => Text_Cst_Access (TDH.Source_Buffer),
              Source_First  => Raw_Data.Source_First,
              Source_Last   => Raw_Data.Source_Last,
              Sloc_Range    => Sloc_Range (TDH, Raw_Data));
   end Convert;

   ------------------
   -- From_Generic --
   ------------------

   function From_Generic (Token : Lk_Token) return Common.Token_Reference is
      use Langkit_Support.Internal.Conversions;
      Id         : Any_Language_Id;
      Data       : Langkit_Support.Internal.Analysis.Internal_Token;
      Safety_Net : Langkit_Support.Internal.Analysis.Token_Safety_Net;
   begin
      Unwrap_Token (Token, Id, Data, Safety_Net);
      pragma Assert (Id = Generic_API.Self_Id);
      return (Data.TDH,
              Data.Index,
              (Safety_Net.Context,
               Safety_Net.Context_Version,
               Safety_Net.TDH_Version));
   end From_Generic;

   ----------------
   -- To_Generic --
   ----------------

   function To_Generic (Token : Common.Token_Reference) return Lk_Token is
      use Langkit_Support.Internal.Conversions;
   begin
      return Wrap_Token
        (Generic_API.Self_Id,
         (Token.TDH, Token.Index),
         (Token.Safety_Net.Context,
          Token.Safety_Net.Context_Version,
          Token.Safety_Net.TDH_Version));
   end To_Generic;

   --------------------------
   -- Wrap_Token_Reference --
   --------------------------

   function Wrap_Token_Reference
     (Context : Internal_Context;
      TDH     : Token_Data_Handler_Access;
      Index   : Token_Or_Trivia_Index) return Token_Reference is
   begin
      if Index = No_Token_Or_Trivia_Index then
         return No_Token;
      end if;

      declare
         SN : constant Token_Safety_Net :=
           (Context         => +Context,
            Context_Version => Context.Serial_Number,
            TDH_Version     => TDH.Version);
      begin
        return (TDH, Index, SN);
      end;
   end Wrap_Token_Reference;

   --------------------
   -- Get_Token_Unit --
   --------------------

   function Get_Token_Unit (Token : Token_Reference) return Internal_Unit is
      function "+" is new Ada.Unchecked_Conversion
        (System.Address, Internal_Unit);
   begin
      if Token = No_Token then
         raise Precondition_Failure with "null token argument";
      end if;
      Check_Safety_Net (Token);
      return +Token.TDH.Owner;
   end Get_Token_Unit;

   -----------------------
   -- Get_Token_Context --
   -----------------------

   function Get_Token_Context
     (Token : Token_Reference) return Internal_Context is
   begin
      return +Token.Safety_Net.Context;
   end Get_Token_Context;

   -------------------
   -- Get_Token_TDH --
   -------------------

   function Get_Token_TDH
     (Token : Token_Reference) return Token_Data_Handler_Access is
   begin
      return Token.TDH;
   end Get_Token_TDH;

   ---------------------
   -- Get_Token_Index --
   ---------------------

   function Get_Token_Index
     (Token : Token_Reference) return Token_Or_Trivia_Index is
   begin
      return Token.Index;
   end Get_Token_Index;

   ------------------------
   -- Extract_Token_Text --
   ------------------------

   procedure Extract_Token_Text
     (Token         : Token_Data_Type;
      Source_Buffer : out Text_Cst_Access;
      First         : out Positive;
      Last          : out Natural) is
   begin
      Source_Buffer := Token.Source_Buffer;
      First := Token.Source_First;
      Last := Token.Source_Last;
   end Extract_Token_Text;

   ---------------------
   -- Token_Node_Kind --
   ---------------------

   function Token_Node_Kind (Kind : R_F_L_X_Node_Kind_Type) return Token_Kind is
      
   begin
         pragma Unreferenced (Kind);
         return (raise Program_Error);
   end Token_Node_Kind;


begin
   --  Check that we actually have full Libiconv support: as nothing works
   --  without it, we explicitly check support here instead of letting
   --  user-unfriendly errors happen during lexing.

   if not GNATCOLL.Iconv.Has_Iconv then
      raise Program_Error with "Libiconv is not available";
   end if;


   Private_Converters.Wrap_Token_Reference := Wrap_Token_Reference'Access;
   Private_Converters.Get_Token_Context := Get_Token_Context'Access;
   Private_Converters.Get_Token_Unit := Get_Token_Unit'Access;
   Private_Converters.Get_Token_TDH := Get_Token_TDH'Access;
   Private_Converters.Get_Token_Index := Get_Token_Index'Access;
   Private_Converters.Extract_Token_Text := Extract_Token_Text'Access;
end Librflxlang.Common;
