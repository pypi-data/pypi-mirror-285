








with Ada.Finalization;
pragma Warnings (Off, "is an internal GNAT unit");
with Ada.Strings.Wide_Wide_Unbounded.Aux;
use Ada.Strings.Wide_Wide_Unbounded.Aux;
pragma Warnings (On, "is an internal GNAT unit");

with System.Memory;
use type System.Address;

with GNATCOLL.Iconv;

with Langkit_Support.Diagnostics; use Langkit_Support.Diagnostics;
with Langkit_Support.Text;        use Langkit_Support.Text;

with Librflxlang.Private_Converters;
use Librflxlang.Private_Converters;


          with Langkit_Support.Errors;


package body Librflxlang.Implementation.C is

   --  Avoid hiding from $.Lexer
   subtype Token_Data_Type is Common.Token_Data_Type;

   --------------------
   -- Event handlers --
   --------------------

   type C_Event_Handler is limited new
      Ada.Finalization.Limited_Controlled
      and Internal_Event_Handler
   with record
      Ref_Count           : Natural;
      Data                : System.Address;
      Destroy_Func        : rflx_event_handler_destroy_callback;
      Unit_Requested_Func : rflx_event_handler_unit_requested_callback;
      Unit_Parsed_Func    : rflx_event_handler_unit_parsed_callback;
   end record;

   overriding procedure Finalize (Self : in out C_Event_Handler);
   overriding procedure Inc_Ref (Self : in out C_Event_Handler);
   overriding function Dec_Ref (Self : in out C_Event_Handler) return Boolean;

   overriding procedure Unit_Requested_Callback
     (Self               : in out C_Event_Handler;
      Context            : Internal_Context;
      Name               : Text_Type;
      From               : Internal_Unit;
      Found              : Boolean;
      Is_Not_Found_Error : Boolean);

   overriding procedure Unit_Parsed_Callback
     (Self     : in out C_Event_Handler;
      Context  : Internal_Context;
      Unit     : Internal_Unit;
      Reparsed : Boolean);

   ------------------
   -- File readers --
   ------------------

   type C_File_Reader is limited new
      Ada.Finalization.Limited_Controlled
      and Internal_File_Reader
   with record
      Ref_Count    : Natural;
      Data         : System.Address;
      Destroy_Func : rflx_file_reader_destroy_callback;
      Read_Func    : rflx_file_reader_read_callback;
   end record;

   type C_File_Reader_Access is access all C_File_Reader;

   overriding procedure Finalize (Self : in out C_File_Reader);
   overriding procedure Inc_Ref (Self : in out C_File_Reader);
   overriding function Dec_Ref (Self : in out C_File_Reader) return Boolean;
   overriding procedure Read
     (Self        : C_File_Reader;
      Filename    : String;
      Charset     : String;
      Read_BOM    : Boolean;
      Contents    : out Decoded_File_Contents;
      Diagnostics : in out Diagnostics_Vectors.Vector);

   function Value_Or_Empty (S : chars_ptr) return String
   --  If S is null, return an empty string. Return Value (S) otherwise.
   is (if S = Null_Ptr
       then ""
       else Value (S));

   Last_Exception : rflx_exception_Ptr := null;

   ----------
   -- Free --
   ----------

   procedure Free (Address : System.Address) is
      procedure C_Free (Address : System.Address)
        with Import        => True,
             Convention    => C,
             External_Name => "free";
   begin
      C_Free (Address);
   end Free;

   -------------------------
   -- Analysis primitives --
   -------------------------

   function rflx_allocate_analysis_context
     return rflx_analysis_context is
   begin
      Clear_Last_Exception;
      begin
         return Allocate_Context;
      exception
         when Exc : others =>
            Set_Last_Exception (Exc);
            return null;
      end;
   end;

   procedure rflx_initialize_analysis_context
     (Context       : rflx_analysis_context;
      Charset       : chars_ptr;
      File_Reader   : rflx_file_reader;
      Unit_Provider : rflx_unit_provider;
      Event_Handler : rflx_event_handler;
      With_Trivia   : int;
      Tab_Stop      : int) is
   begin
      Clear_Last_Exception;

      declare
         C : constant String :=
           (if Charset = Null_Ptr
            then "utf-8"
            else Value (Charset));
      begin
         Initialize_Context
            (Context       => Context,
             Charset       => C,
             File_Reader   => Unwrap_Private_File_Reader (File_Reader),
             Unit_Provider => Unwrap_Private_Provider (Unit_Provider),
             Event_Handler => Unwrap_Private_Event_Handler (Event_Handler),
             With_Trivia   => With_Trivia /= 0,
             Tab_Stop      => Natural (Tab_Stop));
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_context_incref
     (Context : rflx_analysis_context) return rflx_analysis_context is
   begin
      Clear_Last_Exception;
      Inc_Ref (Context);
      return Context;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return null;
   end;

   procedure rflx_context_decref
     (Context : rflx_analysis_context)
   is
      Context_Var : Internal_Context := Context;
   begin
      Clear_Last_Exception;
      Dec_Ref (Context_Var);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_context_symbol
     (Context : rflx_analysis_context;
      Text    : access rflx_text;
      Symbol  : access rflx_symbol_type) return int
   is
      Raw_Text : Text_Type (1 .. Natural (Text.Length))
         with Import, Address => Text.Chars;
   begin
      Clear_Last_Exception;
      Symbol.all := Wrap_Symbol (Lookup_Symbol (Context, Raw_Text));
      return 1;
   exception
      when Invalid_Symbol_Error =>
         return 0;
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   procedure rflx_context_discard_errors_in_populate_lexical_env
     (Context : rflx_analysis_context;
      Discard : int) is
   begin
      Clear_Last_Exception;
      Discard_Errors_In_Populate_Lexical_Env (Context, Discard /= 0);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_get_analysis_unit_from_file
     (Context           : rflx_analysis_context;
      Filename, Charset : chars_ptr;
      Reparse           : int;
      Rule              : rflx_grammar_rule) return rflx_analysis_unit is
   begin
      Clear_Last_Exception;

      return Get_From_File
        (Context,
         Value (Filename),
         Value_Or_Empty (Charset),
         Reparse /= 0,
         Rule);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return null;
   end;

   function rflx_get_analysis_unit_from_buffer
     (Context           : rflx_analysis_context;
      Filename, Charset : chars_ptr;
      Buffer            : chars_ptr;
      Buffer_Size       : size_t;
      Rule              : rflx_grammar_rule) return rflx_analysis_unit is
   begin
      Clear_Last_Exception;

      declare
         Buffer_Str : String (1 .. Natural (Buffer_Size))
            with Import, Address => Convert (Buffer);
      begin
         return Get_From_Buffer
           (Context,
            Value (Filename),
            Value_Or_Empty (Charset),
            Buffer_Str,
            Rule);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return null;
   end;


   procedure rflx_unit_root
     (Unit     : rflx_analysis_unit;
      Result_P : rflx_node_Ptr) is
   begin
      Clear_Last_Exception;

      Result_P.all := (Unit.Ast_Root, No_Entity_Info);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_unit_first_token
     (Unit  : rflx_analysis_unit;
      Token : access rflx_token) is
   begin
      Clear_Last_Exception;

      declare
         T : constant Token_Reference := First_Token (Unit);
      begin
         Token.all := Wrap (T);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_unit_last_token
     (Unit  : rflx_analysis_unit;
      Token : access rflx_token) is
   begin
      Clear_Last_Exception;

      declare
         T : constant Token_Reference := Last_Token (Unit);
      begin
         Token.all := Wrap (T);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_unit_token_count
     (Unit : rflx_analysis_unit) return int is
   begin
      Clear_Last_Exception;

      return int (Token_Count (Unit));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return -1;
   end;

   function rflx_unit_trivia_count
     (Unit : rflx_analysis_unit) return int is
   begin
      Clear_Last_Exception;

      return int (Trivia_Count (Unit));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return -1;
   end;

   procedure rflx_unit_lookup_token
     (Unit   : rflx_analysis_unit;
      Sloc   : access rflx_source_location;
      Result : access rflx_token) is
   begin
      Clear_Last_Exception;

      declare
         S   : constant Source_Location := Unwrap (Sloc.all);
         Tok : constant Token_Reference := Lookup_Token (Unit, S);
      begin
         Result.all := Wrap (Tok);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_unit_dump_lexical_env
     (Unit : rflx_analysis_unit) is
   begin
      Clear_Last_Exception;
      Dump_Lexical_Env (Unit);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_unit_filename
     (Unit : rflx_analysis_unit) return chars_ptr is
   begin
      Clear_Last_Exception;

      return New_String (Get_Filename (Unit));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return Null_Ptr;
   end;

   function rflx_unit_diagnostic_count
     (Unit : rflx_analysis_unit) return unsigned is
   begin
      Clear_Last_Exception;

      return unsigned (Unit.Diagnostics.Length);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_unit_diagnostic
     (Unit         : rflx_analysis_unit;
      N            : unsigned;
      Diagnostic_P : access rflx_diagnostic) return int
   is
   begin
      Clear_Last_Exception;

      if N < unsigned (Unit.Diagnostics.Length) then
         declare
            D_In  : Diagnostic renames Unit.Diagnostics (Natural (N) + 1);
            D_Out : rflx_diagnostic renames Diagnostic_P.all;
         begin
            D_Out.Sloc_Range := Wrap (D_In.Sloc_Range);
            D_Out.Message := Wrap (D_In.Message);
            return 1;
         end;
      else
         return 0;
      end if;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_unit_context
     (Unit : rflx_analysis_unit) return rflx_analysis_context is
   begin
      Clear_Last_Exception;
      return Unit.Context;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return null;
   end;

   procedure rflx_unit_reparse_from_file
     (Unit : rflx_analysis_unit; Charset : chars_ptr) is
   begin
      Clear_Last_Exception;

      Reparse (Unit, Value_Or_Empty (Charset));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_unit_reparse_from_buffer
     (Unit        : rflx_analysis_unit;
      Charset     : chars_ptr;
      Buffer      : chars_ptr;
      Buffer_Size : size_t) is
   begin
      Clear_Last_Exception;

      declare
         Buffer_Str : String (1 .. Natural (Buffer_Size))
            with Import, Address => Convert (Buffer);
      begin
         Reparse (Unit, Value_Or_Empty (Charset), Buffer_Str);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_unit_populate_lexical_env
     (Unit : rflx_analysis_unit
   ) return int is
   begin
      Clear_Last_Exception;
      Populate_Lexical_Env
        (Unit, 1);
      return 1;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   ---------------------------------
   -- General AST node primitives --
   ---------------------------------

   Node_Kind_Names : constant array (R_F_L_X_Node_Kind_Type) of Text_Access :=
     (Rflx_I_D => new Text_Type'(To_Text ("ID")), Rflx_Unqualified_I_D => new Text_Type'(To_Text ("UnqualifiedID")), Rflx_Aspect => new Text_Type'(To_Text ("Aspect")), Rflx_Attr_First => new Text_Type'(To_Text ("AttrFirst")), Rflx_Attr_Has_Data => new Text_Type'(To_Text ("AttrHasData")), Rflx_Attr_Head => new Text_Type'(To_Text ("AttrHead")), Rflx_Attr_Last => new Text_Type'(To_Text ("AttrLast")), Rflx_Attr_Opaque => new Text_Type'(To_Text ("AttrOpaque")), Rflx_Attr_Present => new Text_Type'(To_Text ("AttrPresent")), Rflx_Attr_Size => new Text_Type'(To_Text ("AttrSize")), Rflx_Attr_Valid => new Text_Type'(To_Text ("AttrValid")), Rflx_Attr_Valid_Checksum => new Text_Type'(To_Text ("AttrValidChecksum")), Rflx_Attr_Stmt_Append => new Text_Type'(To_Text ("AttrStmtAppend")), Rflx_Attr_Stmt_Extend => new Text_Type'(To_Text ("AttrStmtExtend")), Rflx_Attr_Stmt_Read => new Text_Type'(To_Text ("AttrStmtRead")), Rflx_Attr_Stmt_Write => new Text_Type'(To_Text ("AttrStmtWrite")), Rflx_Message_Aggregate_Associations => new Text_Type'(To_Text ("MessageAggregateAssociations")), Rflx_Null_Message_Aggregate => new Text_Type'(To_Text ("NullMessageAggregate")), Rflx_Checksum_Val => new Text_Type'(To_Text ("ChecksumVal")), Rflx_Checksum_Value_Range => new Text_Type'(To_Text ("ChecksumValueRange")), Rflx_Byte_Order_Type_Highorderfirst => new Text_Type'(To_Text ("ByteOrderTypeHighorderfirst")), Rflx_Byte_Order_Type_Loworderfirst => new Text_Type'(To_Text ("ByteOrderTypeLoworderfirst")), Rflx_Readable => new Text_Type'(To_Text ("Readable")), Rflx_Writable => new Text_Type'(To_Text ("Writable")), Rflx_Checksum_Assoc => new Text_Type'(To_Text ("ChecksumAssoc")), Rflx_Refinement_Decl => new Text_Type'(To_Text ("RefinementDecl")), Rflx_Session_Decl => new Text_Type'(To_Text ("SessionDecl")), Rflx_Type_Decl => new Text_Type'(To_Text ("TypeDecl")), Rflx_Description => new Text_Type'(To_Text ("Description")), Rflx_Element_Value_Assoc => new Text_Type'(To_Text ("ElementValueAssoc")), Rflx_Attribute => new Text_Type'(To_Text ("Attribute")), Rflx_Bin_Op => new Text_Type'(To_Text ("BinOp")), Rflx_Binding => new Text_Type'(To_Text ("Binding")), Rflx_Call => new Text_Type'(To_Text ("Call")), Rflx_Case_Expression => new Text_Type'(To_Text ("CaseExpression")), Rflx_Choice => new Text_Type'(To_Text ("Choice")), Rflx_Comprehension => new Text_Type'(To_Text ("Comprehension")), Rflx_Context_Item => new Text_Type'(To_Text ("ContextItem")), Rflx_Conversion => new Text_Type'(To_Text ("Conversion")), Rflx_Message_Aggregate => new Text_Type'(To_Text ("MessageAggregate")), Rflx_Negation => new Text_Type'(To_Text ("Negation")), Rflx_Numeric_Literal => new Text_Type'(To_Text ("NumericLiteral")), Rflx_Paren_Expression => new Text_Type'(To_Text ("ParenExpression")), Rflx_Quantified_Expression => new Text_Type'(To_Text ("QuantifiedExpression")), Rflx_Select_Node => new Text_Type'(To_Text ("SelectNode")), Rflx_Concatenation => new Text_Type'(To_Text ("Concatenation")), Rflx_Sequence_Aggregate => new Text_Type'(To_Text ("SequenceAggregate")), Rflx_String_Literal => new Text_Type'(To_Text ("StringLiteral")), Rflx_Variable => new Text_Type'(To_Text ("Variable")), Rflx_Formal_Channel_Decl => new Text_Type'(To_Text ("FormalChannelDecl")), Rflx_Formal_Function_Decl => new Text_Type'(To_Text ("FormalFunctionDecl")), Rflx_Renaming_Decl => new Text_Type'(To_Text ("RenamingDecl")), Rflx_Variable_Decl => new Text_Type'(To_Text ("VariableDecl")), Rflx_Message_Aggregate_Association => new Text_Type'(To_Text ("MessageAggregateAssociation")), Rflx_Byte_Order_Aspect => new Text_Type'(To_Text ("ByteOrderAspect")), Rflx_Checksum_Aspect => new Text_Type'(To_Text ("ChecksumAspect")), Rflx_Message_Field => new Text_Type'(To_Text ("MessageField")), Rflx_Message_Fields => new Text_Type'(To_Text ("MessageFields")), Rflx_Null_Message_Field => new Text_Type'(To_Text ("NullMessageField")), Rflx_Op_Add => new Text_Type'(To_Text ("OpAdd")), Rflx_Op_And => new Text_Type'(To_Text ("OpAnd")), Rflx_Op_Div => new Text_Type'(To_Text ("OpDiv")), Rflx_Op_Eq => new Text_Type'(To_Text ("OpEq")), Rflx_Op_Ge => new Text_Type'(To_Text ("OpGe")), Rflx_Op_Gt => new Text_Type'(To_Text ("OpGt")), Rflx_Op_In => new Text_Type'(To_Text ("OpIn")), Rflx_Op_Le => new Text_Type'(To_Text ("OpLe")), Rflx_Op_Lt => new Text_Type'(To_Text ("OpLt")), Rflx_Op_Mod => new Text_Type'(To_Text ("OpMod")), Rflx_Op_Mul => new Text_Type'(To_Text ("OpMul")), Rflx_Op_Neq => new Text_Type'(To_Text ("OpNeq")), Rflx_Op_Notin => new Text_Type'(To_Text ("OpNotin")), Rflx_Op_Or => new Text_Type'(To_Text ("OpOr")), Rflx_Op_Pow => new Text_Type'(To_Text ("OpPow")), Rflx_Op_Sub => new Text_Type'(To_Text ("OpSub")), Rflx_Package_Node => new Text_Type'(To_Text ("PackageNode")), Rflx_Parameter => new Text_Type'(To_Text ("Parameter")), Rflx_Parameters => new Text_Type'(To_Text ("Parameters")), Rflx_Quantifier_All => new Text_Type'(To_Text ("QuantifierAll")), Rflx_Quantifier_Some => new Text_Type'(To_Text ("QuantifierSome")), Rflx_Aspect_List => new Text_Type'(To_Text ("AspectList")), Rflx_Base_Checksum_Val_List => new Text_Type'(To_Text ("BaseChecksumValList")), Rflx_Channel_Attribute_List => new Text_Type'(To_Text ("ChannelAttributeList")), Rflx_Checksum_Assoc_List => new Text_Type'(To_Text ("ChecksumAssocList")), Rflx_Choice_List => new Text_Type'(To_Text ("ChoiceList")), Rflx_Conditional_Transition_List => new Text_Type'(To_Text ("ConditionalTransitionList")), Rflx_Context_Item_List => new Text_Type'(To_Text ("ContextItemList")), Rflx_Declaration_List => new Text_Type'(To_Text ("DeclarationList")), Rflx_Element_Value_Assoc_List => new Text_Type'(To_Text ("ElementValueAssocList")), Rflx_Expr_List => new Text_Type'(To_Text ("ExprList")), Rflx_Formal_Decl_List => new Text_Type'(To_Text ("FormalDeclList")), Rflx_Local_Decl_List => new Text_Type'(To_Text ("LocalDeclList")), Rflx_Message_Aggregate_Association_List => new Text_Type'(To_Text ("MessageAggregateAssociationList")), Rflx_Message_Aspect_List => new Text_Type'(To_Text ("MessageAspectList")), Rflx_Message_Field_List => new Text_Type'(To_Text ("MessageFieldList")), Rflx_Numeric_Literal_List => new Text_Type'(To_Text ("NumericLiteralList")), Rflx_Parameter_List => new Text_Type'(To_Text ("ParameterList")), Rflx_R_F_L_X_Node_List => new Text_Type'(To_Text ("RFLXNodeList")), Rflx_State_List => new Text_Type'(To_Text ("StateList")), Rflx_Statement_List => new Text_Type'(To_Text ("StatementList")), Rflx_Term_Assoc_List => new Text_Type'(To_Text ("TermAssocList")), Rflx_Then_Node_List => new Text_Type'(To_Text ("ThenNodeList")), Rflx_Type_Argument_List => new Text_Type'(To_Text ("TypeArgumentList")), Rflx_Unqualified_I_D_List => new Text_Type'(To_Text ("UnqualifiedIDList")), Rflx_Specification => new Text_Type'(To_Text ("Specification")), Rflx_State => new Text_Type'(To_Text ("State")), Rflx_State_Body => new Text_Type'(To_Text ("StateBody")), Rflx_Assignment => new Text_Type'(To_Text ("Assignment")), Rflx_Attribute_Statement => new Text_Type'(To_Text ("AttributeStatement")), Rflx_Message_Field_Assignment => new Text_Type'(To_Text ("MessageFieldAssignment")), Rflx_Reset => new Text_Type'(To_Text ("Reset")), Rflx_Term_Assoc => new Text_Type'(To_Text ("TermAssoc")), Rflx_Then_Node => new Text_Type'(To_Text ("ThenNode")), Rflx_Transition => new Text_Type'(To_Text ("Transition")), Rflx_Conditional_Transition => new Text_Type'(To_Text ("ConditionalTransition")), Rflx_Type_Argument => new Text_Type'(To_Text ("TypeArgument")), Rflx_Message_Type_Def => new Text_Type'(To_Text ("MessageTypeDef")), Rflx_Null_Message_Type_Def => new Text_Type'(To_Text ("NullMessageTypeDef")), Rflx_Named_Enumeration_Def => new Text_Type'(To_Text ("NamedEnumerationDef")), Rflx_Positional_Enumeration_Def => new Text_Type'(To_Text ("PositionalEnumerationDef")), Rflx_Enumeration_Type_Def => new Text_Type'(To_Text ("EnumerationTypeDef")), Rflx_Modular_Type_Def => new Text_Type'(To_Text ("ModularTypeDef")), Rflx_Range_Type_Def => new Text_Type'(To_Text ("RangeTypeDef")), Rflx_Sequence_Type_Def => new Text_Type'(To_Text ("SequenceTypeDef")), Rflx_Type_Derivation_Def => new Text_Type'(To_Text ("TypeDerivationDef")));

   function rflx_node_kind
     (Node : rflx_node_Ptr) return rflx_node_kind_enum is
   begin
      Clear_Last_Exception;

      declare
         K : constant R_F_L_X_Node_Kind_Type := Node.Node.Kind;
      begin
         return rflx_node_kind_enum (K'Enum_Rep);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return rflx_node_kind_enum'First;
   end;

   procedure rflx_kind_name
     (Kind : rflx_node_kind_enum; Result : access rflx_text) is
   begin
      Clear_Last_Exception;

      declare
         K    : constant R_F_L_X_Node_Kind_Type := R_F_L_X_Node_Kind_Type'Enum_Val (Kind);
         Name : Text_Access renames Node_Kind_Names (K);
      begin
         Result.all := (Chars        => Name.all'Address,
                        Length       => Name'Length,
                        Is_Allocated => 0);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_node_unit
     (Node : rflx_node_Ptr) return rflx_analysis_unit is
   begin
      Clear_Last_Exception;
      return Node.Node.Unit;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return null;
   end;

   procedure rflx_create_bare_entity
     (Node   : rflx_base_node;
      Entity : access rflx_node)
   is
   begin
      Clear_Last_Exception;
      Entity.all := (Node => Unwrap (Node), Info => No_Entity_Info);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_is_equivalent
     (L, R : rflx_node_Ptr) return rflx_bool
   is
   begin
      Clear_Last_Exception;
      return rflx_bool (Boolean'Pos (Compare_Entity (L.all, R.all)));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_hash
     (Node : rflx_node_Ptr) return uint32_t
   is
   begin
      Clear_Last_Exception;
      return uint32_t (Hash_Entity (Node.all));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_is_token_node
     (Node : rflx_node_Ptr) return int is
   begin
      Clear_Last_Exception;
      return Boolean'Pos (Is_Token_Node (Node.Node));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_is_synthetic
     (Node : rflx_node_Ptr) return int is
   begin
      Clear_Last_Exception;
      return Boolean'Pos (Is_Synthetic (Node.Node));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   procedure rflx_node_image
     (Node : rflx_node_Ptr; Result : access rflx_text) is
   begin
      Clear_Last_Exception;
      declare
         Img : constant Text_Type := Text_Image (Node.all);
      begin
         Result.all := Wrap_Alloc (Img);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_node_text
     (Node : rflx_node_Ptr;
      Text : access rflx_text) is
   begin
      Clear_Last_Exception;
      Text.all := Wrap_Alloc (Implementation.Text (Node.Node));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_node_sloc_range
     (Node         : rflx_node_Ptr;
      Sloc_Range_P : access rflx_source_location_range) is
   begin
      Clear_Last_Exception;

      Sloc_Range_P.all := Wrap (Sloc_Range (Node.Node));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_lookup_in_node
     (Node   : rflx_node_Ptr;
      Sloc   : rflx_source_location;
      Result : rflx_node_Ptr) is
   begin
      Clear_Last_Exception;

      declare
         S : constant Source_Location := Unwrap (Sloc);
      begin
         Result.all := (Lookup (Node.Node, S), Node.Info);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_node_children_count
     (Node : rflx_node_Ptr) return unsigned is
   begin
      Clear_Last_Exception;
      return unsigned (Children_Count (Node.Node));
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_node_child
     (Node    : rflx_node_Ptr;
      N       : unsigned;
      Child_P : rflx_node_Ptr) return int is
   begin
      Clear_Last_Exception;

      declare
         Result : Bare_R_F_L_X_Node;
         Exists : Boolean;
      begin
         if N > unsigned (Natural'Last) then
            return 0;
         end if;
         Get_Child (Node.Node, Natural (N) + 1, Exists, Result);
         if Exists then
            Child_P.all := (Result, Node.Info);
            return 1;
         else
            return 0;
         end if;
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_text_to_locale_string
     (Text : rflx_text) return System.Address is
   begin
      Clear_Last_Exception;

      declare
         use GNATCOLL.Iconv;

         Input_Byte_Size : constant size_t := 4 * Text.Length;

         Output_Byte_Size : constant size_t := Input_Byte_Size + 1;
         --  Assuming no encoding will take more than 4 bytes per character, 4
         --  times the size of the input text plus one null byte should be
         --  enough to hold the result. This is a development helper anyway, so
         --  we don't have performance concerns.

         Result : constant System.Address := System.Memory.Alloc
           (System.Memory.size_t (Output_Byte_Size));
         --  Buffer we are going to return to the caller. We use
         --  System.Memory.Alloc so that users can call C's "free" function in
         --  order to free it.

         Input : String (1 .. Natural (Input_Byte_Size));
         for Input'Address use Text.Chars;

         Output : String (1 .. Natural (Output_Byte_Size));
         for Output'Address use Result;

         State                     : Iconv_T;
         Input_Index, Output_Index : Positive := 1;
         Status                    : Iconv_Result;

         From_Code : constant String :=
           (if System."=" (System.Default_Bit_Order, System.Low_Order_First)
            then UTF32LE
            else UTF32BE);

      begin
         --  GNATCOLL.Iconv raises Constraint_Error exceptions for empty
         --  strings, so handle them ourselves.

         if Input_Byte_Size = 0 then
            Output (1) := ASCII.NUL;
         end if;

         --  Encode to the locale. Don't bother with error checking...

         Set_Locale;
         State := Iconv_Open
           (To_Code         => Locale,
            From_Code       => From_Code,
            Transliteration => True,
            Ignore          => True);
         Iconv (State, Input, Input_Index, Output, Output_Index, Status);
         Iconv_Close (State);

         --  Don't forget the trailing NULL character to keep C programs happy
         Output (Output_Index) := ASCII.NUL;

         return Result;
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return System.Null_Address;
   end;

   ----------
   -- Wrap --
   ----------

   function Wrap (S : Unbounded_Wide_Wide_String) return rflx_text is
      Chars  : Big_Wide_Wide_String_Access;
      Length : Natural;
   begin
      Get_Wide_Wide_String (S, Chars, Length);
      return (Chars.all'Address, size_t (Length), 0);
   end Wrap;

   ------------------------
   -- Set_Last_Exception --
   ------------------------

   procedure Set_Last_Exception (Exc : Exception_Occurrence) is
   begin
      Set_Last_Exception (Exception_Identity (Exc), Exception_Message (Exc));
   end Set_Last_Exception;

   ------------------------
   -- Set_Last_Exception --
   ------------------------

   procedure Set_Last_Exception (Id : Exception_Id; Message : String) is
   begin
      --  If it's the first time, allocate room for the exception information

      if Last_Exception = null then
         Last_Exception := new rflx_exception;

      --  If it is not the first time, free memory allocated for the last
      --  exception.

      elsif Last_Exception.Information /= Null_Ptr then
         Free (Last_Exception.Information);
      end if;

      --  Get the kind corresponding to Exc

      if Id = Langkit_Support.Errors.File_Read_Error'Identity then
         Last_Exception.Kind := Exception_File_Read_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Introspection.Bad_Type_Error'Identity then
         Last_Exception.Kind := Exception_Bad_Type_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Introspection.Out_Of_Bounds_Error'Identity then
         Last_Exception.Kind := Exception_Out_Of_Bounds_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Invalid_Input'Identity then
         Last_Exception.Kind := Exception_Invalid_Input;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Invalid_Symbol_Error'Identity then
         Last_Exception.Kind := Exception_Invalid_Symbol_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Invalid_Unit_Name_Error'Identity then
         Last_Exception.Kind := Exception_Invalid_Unit_Name_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Native_Exception'Identity then
         Last_Exception.Kind := Exception_Native_Exception;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Precondition_Failure'Identity then
         Last_Exception.Kind := Exception_Precondition_Failure;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Property_Error'Identity then
         Last_Exception.Kind := Exception_Property_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Rewriting.Template_Args_Error'Identity then
         Last_Exception.Kind := Exception_Template_Args_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Rewriting.Template_Format_Error'Identity then
         Last_Exception.Kind := Exception_Template_Format_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Rewriting.Template_Instantiation_Error'Identity then
         Last_Exception.Kind := Exception_Template_Instantiation_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Stale_Reference_Error'Identity then
         Last_Exception.Kind := Exception_Stale_Reference_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Syntax_Error'Identity then
         Last_Exception.Kind := Exception_Syntax_Error;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Unknown_Charset'Identity then
         Last_Exception.Kind := Exception_Unknown_Charset;
         Last_Exception.Information := New_String (Message);
      elsif Id = Langkit_Support.Errors.Unparsing.Malformed_Tree_Error'Identity then
         Last_Exception.Kind := Exception_Malformed_Tree_Error;
         Last_Exception.Information := New_String (Message);
      else
         Last_Exception.Kind := Exception_Native_Exception;
         Last_Exception.Information := New_String (Message);
      end if;
   end Set_Last_Exception;

   --------------------------
   -- Clear_Last_Exception --
   --------------------------

   procedure Clear_Last_Exception is
   begin
      if Last_Exception /= null then
         Free (Last_Exception.Information);
      end if;
   end Clear_Last_Exception;

   function rflx_get_last_exception return rflx_exception_Ptr
   is
   begin
      if Last_Exception = null
         or else Last_Exception.Information = Null_Ptr
      then
         return null;
      else
         return Last_Exception;
      end if;
   end;

   function rflx_exception_name
     (Kind : rflx_exception_kind) return chars_ptr is
   begin
      return New_String (Kind'Image);
   end;

   function rflx_token_get_kind
     (Token : rflx_token) return int is
   begin
      Clear_Last_Exception;
      declare
         T : constant Token_Reference := Unwrap (Token);
         D : constant Token_Data_Type := Data (T);
      begin
         return Kind (D)'Enum_Rep;
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_token_kind_name (Kind : int) return chars_ptr
   is
      K : Token_Kind;
   begin
      begin
         K := Token_Kind'Enum_Val (Kind);
      exception
         when Exc : Constraint_Error =>
            Set_Last_Exception (Exc);
            return Null_Ptr;
      end;

      return New_String (Token_Kind_Name (K));
   end;

   procedure rflx_token_sloc_range
     (Token : rflx_token; Result : access rflx_source_location_range) is
   begin
      Clear_Last_Exception;
      declare
         T : constant Token_Reference := Unwrap (Token);
         D : constant Token_Data_Type := Data (T);
      begin
         Result.all := Wrap (Sloc_Range (D));
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_token_next
     (Token      : rflx_token;
      Next_Token : access rflx_token)
   is
   begin
      Clear_Last_Exception;
      declare
         T  : constant Token_Reference := Unwrap (Token);
         NT : constant Token_Reference := Next (T);
      begin
         Next_Token.all := Wrap (NT);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_token_previous
     (Token          : rflx_token;
      Previous_Token : access rflx_token)
   is
   begin
      Clear_Last_Exception;
      declare
         T  : constant Token_Reference := Unwrap (Token);
         PT : constant Token_Reference := Previous (T);
      begin
         Previous_Token.all := Wrap (PT);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_token_range_text
     (First, Last : rflx_token;
      Text        : access rflx_text) return int
   is
   begin
      Clear_Last_Exception;
      declare
         FD : constant Token_Data_Type := Data (Unwrap (First));
         LD : constant Token_Data_Type := Data (Unwrap (Last));

         First_Source_Buffer, Last_Source_Buffer : Text_Cst_Access;
         First_Index, Ignored_First              : Positive;
         Last_Index, Ignored_Last                : Natural;
      begin
         Extract_Token_Text
           (FD, First_Source_Buffer, First_Index, Ignored_Last);
         Extract_Token_Text
           (LD, Last_Source_Buffer, Ignored_First, Last_Index);
         if First_Source_Buffer /= Last_Source_Buffer then
            return 0;
         end if;
         Text.all := Wrap (First_Source_Buffer, First_Index, Last_Index);
         return 1;
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   function rflx_token_is_equivalent
     (Left  : rflx_token;
      Right : rflx_token) return rflx_bool
   is
   begin
      Clear_Last_Exception;
         declare
         L  : constant Token_Reference := Unwrap (Left);
         R  : constant Token_Reference := Unwrap (Right);
      begin
         return rflx_bool (Boolean'Pos (Is_Equivalent (L, R)));
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end;

   ----------------
   -- Wrap_Alloc --
   ----------------

   function Wrap_Alloc (S : Text_Type) return rflx_text is
      T : Text_Access := new Text_Type'(S);
   begin
      return rflx_text'(T.all'Address, T.all'Length, Is_Allocated => 1);
   end Wrap_Alloc;

   ----------------
   -- Wrap_Alloc --
   ----------------

   function Wrap_Alloc (S : Unbounded_Wide_Wide_String) return rflx_text is
      Chars     : Big_Wide_Wide_String_Access;
      Length    : Natural;
      Allocated : Text_Access;
   begin
      Get_Wide_Wide_String (S, Chars, Length);
      Allocated := new Text_Type (1 .. Length);
      Allocated.all := Chars (1 .. Length);
      return (Allocated.all'Address, Allocated.all'Length, 1);
   end Wrap_Alloc;

   ----------
   -- Wrap --
   ----------

   function Wrap
     (S     : Text_Cst_Access;
      First : Positive;
      Last  : Natural) return rflx_text
   is
      Substring : Text_Type renames S (First .. Last);
   begin
      return (if First > Last
              then (Chars        => System.Null_Address,
                    Length       => 0,
                    Is_Allocated => 0)
              else (Chars        => S (First)'Address,
                    Length       => Substring'Length,
                    Is_Allocated => 0));
   end Wrap;

   procedure rflx_destroy_text (T : access rflx_text) is
   begin
      Clear_Last_Exception;
      declare
         use System;
      begin
         if T.Is_Allocated /= 0 and then T.Chars /= System.Null_Address then
            declare
               TT : Text_Type (1 .. Natural (T.Length));
               for TT'Address use T.Chars;
               TA : Text_Access := TT'Unrestricted_Access;
            begin
               Free (TA);
            end;
            T.Chars := System.Null_Address;
         end if;
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_symbol_text
     (Symbol : access rflx_symbol_type; Text : access rflx_text) is
   begin
      Clear_Last_Exception;
      declare
         Sym    : constant Symbol_Type := Unwrap_Symbol (Symbol.all);
         Result : constant Text_Type :=
           (if Sym = null then "" else Image (Sym));
      begin
         Text.all := Wrap_Alloc (Result);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_create_big_integer
     (Text : access rflx_text) return rflx_big_integer is
   begin
      Clear_Last_Exception;
      declare
         T      : Text_Type (1 .. Natural (Text.Length))
            with Import, Address => Text.Chars;
         Image  : constant String := Langkit_Support.Text.Image (T);
         Result : constant Big_Integer_Type := Create_Big_Integer (Image);
      begin
         return Wrap_Big_Integer (Result);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return rflx_big_integer (System.Null_Address);
   end rflx_create_big_integer;

   procedure rflx_big_integer_text
     (Bigint : rflx_big_integer; Text : access rflx_text) is
   begin
      Clear_Last_Exception;
      declare
         BI    : constant Big_Integer_Type := Unwrap_Big_Integer (Bigint);
         Image : constant String := BI.Value.Image;
      begin
         Text.all := Wrap_Alloc (To_Text (Image));
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_big_integer_decref
     (Bigint : rflx_big_integer) is
   begin
      Clear_Last_Exception;
      declare
         BI : Big_Integer_Type := Unwrap_Big_Integer (Bigint);
      begin
         Dec_Ref (BI);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_get_versions
     (Version, Build_Date : access chars_ptr)
   is
   begin
      Clear_Last_Exception;
      Version.all := New_String (Librflxlang.Version);
      Build_Date.all := New_String (Librflxlang.Build_Date);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_create_string
     (Content : System.Address; Length : int) return rflx_string_type
   is
      Value : Text_Type (1 .. Integer (Length))
        with Import, Address => Content;
   begin
      Clear_Last_Exception;
      return Create_String (Value);
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return null;
   end;

   procedure rflx_string_dec_ref (Self : rflx_string_type) is
   begin
      Clear_Last_Exception;
      declare
         Self_Var : String_Type := Self;
      begin
         Dec_Ref (Self_Var);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   procedure rflx_dec_ref_unit_provider
     (Provider : rflx_unit_provider) is
   begin
      Clear_Last_Exception;
      declare
         P : Internal_Unit_Provider_Access :=
            Unwrap_Private_Provider (Provider);
      begin
         Dec_Ref (P);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   function rflx_create_event_handler
     (Data                : System.Address;
      Destroy_Func        : rflx_event_handler_destroy_callback;
      Unit_Requested_Func : rflx_event_handler_unit_requested_callback;
      Unit_Parsed_Func    : rflx_event_handler_unit_parsed_callback)
      return rflx_event_handler is
   begin
      Clear_Last_Exception;
      declare
         Result : constant Internal_Event_Handler_Access :=
           new C_Event_Handler'
             (Ada.Finalization.Limited_Controlled with
              Ref_Count           => 1,
              Data                => Data,
              Destroy_Func        => Destroy_Func,
              Unit_Requested_Func => Unit_Requested_Func,
              Unit_Parsed_Func    => Unit_Parsed_Func);
      begin
         return Wrap_Private_Event_Handler (Result);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return rflx_event_handler (System.Null_Address);
   end;

   procedure rflx_dec_ref_event_handler
     (Handler : rflx_event_handler) is
   begin
      Clear_Last_Exception;
      declare
         P : Internal_Event_Handler_Access :=
            Unwrap_Private_Event_Handler (Handler);
      begin
         Dec_Ref (P);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   --------------
   -- Finalize --
   --------------

   overriding procedure Finalize (Self : in out C_File_Reader) is
   begin
      Self.Destroy_Func (Self.Data);
   end Finalize;

   -------------
   -- Inc_Ref --
   -------------

   overriding procedure Inc_Ref (Self : in out C_File_Reader) is
   begin
      Self.Ref_Count := Self.Ref_Count + 1;
   end Inc_Ref;

   -------------
   -- Dec_Ref --
   -------------

   overriding function Dec_Ref (Self : in out C_File_Reader) return Boolean is
   begin
      Self.Ref_Count := Self.Ref_Count - 1;
      if Self.Ref_Count = 0 then
         return True;
      else
         return False;
      end if;
   end Dec_Ref;

   ----------
   -- Read --
   ----------

   overriding procedure Read
     (Self        : C_File_Reader;
      Filename    : String;
      Charset     : String;
      Read_BOM    : Boolean;
      Contents    : out Decoded_File_Contents;
      Diagnostics : in out Diagnostics_Vectors.Vector)
   is
      C_Filename : chars_ptr := New_String (Filename);
      C_Charset  : chars_ptr := New_String (Charset);
      C_Read_BOM : constant int := (if Read_BOM then 1 else 0);

      C_Contents   : aliased rflx_text;
      C_Diagnostic : aliased rflx_diagnostic :=
        (Sloc_Range => <>,
         Message    => (Chars        => Null_Address,
                        Length       => 0,
                        Is_Allocated => 0));
   begin
      Self.Read_Func.all
        (Self.Data, C_Filename, C_Charset, C_Read_BOM, C_Contents'Access,
         C_Diagnostic'Access);

      if C_Diagnostic.Message.Chars = Null_Address then

         --  If there is a diagnostic (an error), there is no content to return

         declare
            Message : Text_Type (1 .. Natural (C_Diagnostic.Message.Length))
               with Import,
                    Convention => Ada,
                    Address    => C_Diagnostic.Message.Chars;
         begin
            Append (Diagnostics,
                    Unwrap (C_Diagnostic.Sloc_Range),
                    Message);
         end;

      else
         --  Otherwise, create a copy of the buffer

         declare
            Buffer : Text_Type (1 .. Natural (C_Contents.Length))
               with Import, Convention => Ada, Address => C_Contents.Chars;
         begin
            Contents.Buffer := new Text_Type (Buffer'Range);
            Contents.First := Buffer'First;
            Contents.Last := Buffer'Last;
            Contents.Buffer.all := Buffer;
         end;
      end if;

      Free (C_Filename);
      Free (C_Charset);
   end Read;

   function rflx_create_file_reader
     (Data         : System.Address;
      Destroy_Func : rflx_file_reader_destroy_callback;
      Read_Func    : rflx_file_reader_read_callback) return rflx_file_reader
   is
   begin
      Clear_Last_Exception;
      declare
         Result : constant C_File_Reader_Access := new C_File_Reader'
           (Ada.Finalization.Limited_Controlled with
            Ref_Count    => 1,
            Data         => Data,
            Destroy_Func => Destroy_Func,
            Read_Func    => Read_Func);
      begin
         return Wrap_Private_File_Reader (Internal_File_Reader_Access (Result));
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return rflx_file_reader (System.Null_Address);
   end;

   procedure rflx_dec_ref_file_reader
     (File_Reader : rflx_file_reader) is
   begin
      Clear_Last_Exception;
      declare
         P : Internal_File_Reader_Access :=
            Unwrap_Private_File_Reader (File_Reader);
      begin
         Dec_Ref (P);
      end;
   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
   end;

   


   --------------
   -- Finalize --
   --------------

   overriding procedure Finalize (Self : in out C_Event_Handler) is
   begin
      if Self.Destroy_Func /= null then
          Self.Destroy_Func (Self.Data);
      end if;
   end Finalize;

   -------------
   -- Inc_Ref --
   -------------

   overriding procedure Inc_Ref (Self : in out C_Event_Handler) is
   begin
      Self.Ref_Count := Self.Ref_Count + 1;
   end Inc_Ref;

   -------------
   -- Dec_Ref --
   -------------

   overriding function Dec_Ref (Self : in out C_Event_Handler) return Boolean
   is
   begin
      Self.Ref_Count := Self.Ref_Count - 1;
      if Self.Ref_Count = 0 then
         return True;
      else
         return False;
      end if;
   end Dec_Ref;

   -----------------------------
   -- Unit_Requested_Callback --
   -----------------------------

   overriding procedure Unit_Requested_Callback
     (Self               : in out C_Event_Handler;
      Context            : Internal_Context;
      Name               : Text_Type;
      From               : Internal_Unit;
      Found              : Boolean;
      Is_Not_Found_Error : Boolean)
   is
      Name_Access : constant Text_Cst_Access := Name'Unrestricted_Access;
      C_Name      : aliased constant rflx_text := Wrap (Name_Access);
   begin
      Self.Unit_Requested_Func
        (Self.Data,
         Context,
         C_Name'Access,
         From,
         (if Found then 1 else 0),
         (if Is_Not_Found_Error then 1 else 0));
   end Unit_Requested_Callback;

   --------------------------
   -- Unit_Parsed_Callback --
   --------------------------

   overriding procedure Unit_Parsed_Callback
     (Self     : in out C_Event_Handler;
      Context  : Internal_Context;
      Unit     : Internal_Unit;
      Reparsed : Boolean)
   is
   begin
      Self.Unit_Parsed_Func
        (Self.Data, Context, Unit, (if Reparsed then 1 else 0));
   end Unit_Parsed_Callback;

   


   ----------
   -- Wrap --
   ----------

   function Wrap (Token : Token_Reference) return rflx_token is
   begin
      if Token = No_Token then
         return (Token_Data   => null,
                 Token_Index  => -1,
                 Trivia_Index => -1,
                 others       => <>);
      end if;

      declare
         Index : constant Token_Or_Trivia_Index := Get_Token_Index (Token);
      begin
         return (Context         => Get_Token_Context (Token),
                 Token_Data      => Get_Token_TDH (Token),
                 Token_Index     => int (Index.Token),
                 Trivia_Index    => int (Index.Trivia));
      end;
   end Wrap;

   ------------
   -- Unwrap --
   ------------

   function Unwrap (Token : rflx_token) return Token_Reference is
   begin
      return (if Token.Token_Data = null
              then No_Token
              else Wrap_Token_Reference
                     (Token.Context,
                      Token.Token_Data,
                      (Token  => Token_Index (Token.Token_Index),
                       Trivia => Token_Index (Token.Trivia_Index))));
   end Unwrap;

   ---------------------------------------
   -- Kind-specific AST node primitives --
   ---------------------------------------

           

   

   
   

   function rflx_r_f_l_x_node_parent
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Internal_Entity;
         begin
            Result := Librflxlang.Implementation.Parent (Unwrapped_Node, E_Info => Node.Info);

            Value_P.all :=
                  (Result.Node, Result.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_parent;


           

   

   
   

   function rflx_r_f_l_x_node_parents
     (Node : rflx_node_Ptr;

         With_Self :
            
            rflx_bool;

      Value_P : access rflx_node_array) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
         
         Unwrapped_With_Self : constant Boolean :=
               With_Self /= 0
         ;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Internal_Entity_Array_Access;
         begin
            Result := Librflxlang.Implementation.Parents (Unwrapped_Node, With_Self => Unwrapped_With_Self, E_Info => Node.Info);

            Value_P.all :=
                   Result
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_parents;


           

   

   
   

   function rflx_r_f_l_x_node_children
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node_array) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Internal_Entity_Array_Access;
         begin
            Result := Librflxlang.Implementation.Children (Unwrapped_Node, E_Info => Node.Info);

            Value_P.all :=
                   Result
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_children;


           

   

   
   

   function rflx_r_f_l_x_node_token_start
     (Node : rflx_node_Ptr;


      Value_P : access rflx_token) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Token_Reference;
         begin
            Result := Librflxlang.Implementation.Token_Start (Unwrapped_Node);

            Value_P.all :=
                   Wrap (Result)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_token_start;


           

   

   
   

   function rflx_r_f_l_x_node_token_end
     (Node : rflx_node_Ptr;


      Value_P : access rflx_token) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Token_Reference;
         begin
            Result := Librflxlang.Implementation.Token_End (Unwrapped_Node);

            Value_P.all :=
                   Wrap (Result)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_token_end;


           

   

   
   

   function rflx_r_f_l_x_node_child_index
     (Node : rflx_node_Ptr;


      Value_P : access int) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Integer;
         begin
            Result := Librflxlang.Implementation.Child_Index (Unwrapped_Node);

            Value_P.all :=
                   int (Result)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_child_index;


           

   

   
   

   function rflx_r_f_l_x_node_previous_sibling
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Internal_Entity;
         begin
            Result := Librflxlang.Implementation.Previous_Sibling (Unwrapped_Node, E_Info => Node.Info);

            Value_P.all :=
                  (Result.Node, Result.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_previous_sibling;


           

   

   
   

   function rflx_r_f_l_x_node_next_sibling
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Internal_Entity;
         begin
            Result := Librflxlang.Implementation.Next_Sibling (Unwrapped_Node, E_Info => Node.Info);

            Value_P.all :=
                  (Result.Node, Result.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_next_sibling;


           

   

   
   

   function rflx_r_f_l_x_node_unit
     (Node : rflx_node_Ptr;


      Value_P : access rflx_analysis_unit) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Internal_Unit;
         begin
            Result := Librflxlang.Implementation.Unit (Unwrapped_Node);

            Value_P.all :=
                   Result
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_unit;


           

   

   
   

   function rflx_r_f_l_x_node_is_ghost
     (Node : rflx_node_Ptr;


      Value_P : access rflx_bool) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : Boolean;
         begin
            Result := Librflxlang.Implementation.Is_Ghost (Unwrapped_Node);

            Value_P.all :=
                   rflx_bool (Boolean'Pos (Result))
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_is_ghost;


           

   

   
   

   function rflx_r_f_l_x_node_full_sloc_image
     (Node : rflx_node_Ptr;


      Value_P : access rflx_string_type) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;



         declare
            

            Result : String_Type;
         begin
            Result := Librflxlang.Implementation.Full_Sloc_Image (Unwrapped_Node);

            Value_P.all :=
                   Result
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;


   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_r_f_l_x_node_full_sloc_image;


           

   

   
   

   function rflx_i_d_f_package
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_I_D_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := I_D_F_Package (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_i_d_f_package;


           

   

   
   

   function rflx_i_d_f_name
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_I_D_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := I_D_F_Name (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_i_d_f_name;


           

   

   
   

   function rflx_aspect_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Aspect_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Aspect_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_aspect_f_identifier;


           

   

   
   

   function rflx_aspect_f_value
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Aspect_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Aspect_F_Value (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_aspect_f_value;


           

   

   
   

   function rflx_message_aggregate_associations_f_associations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Aggregate_Associations_Range then

         declare
            

            Result : Bare_Message_Aggregate_Association_List;
         begin
            Result := Message_Aggregate_Associations_F_Associations (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_aggregate_associations_f_associations;


           

   

   
   

   function rflx_checksum_val_f_data
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Checksum_Val_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Checksum_Val_F_Data (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_checksum_val_f_data;


           

   

   
   

   function rflx_checksum_value_range_f_first
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Checksum_Value_Range_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Checksum_Value_Range_F_First (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_checksum_value_range_f_first;


           

   

   
   

   function rflx_checksum_value_range_f_last
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Checksum_Value_Range_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Checksum_Value_Range_F_Last (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_checksum_value_range_f_last;


           

   

   
   

   function rflx_checksum_assoc_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Checksum_Assoc_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Checksum_Assoc_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_checksum_assoc_f_identifier;


           

   

   
   

   function rflx_checksum_assoc_f_covered_fields
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Checksum_Assoc_Range then

         declare
            

            Result : Bare_Base_Checksum_Val_List;
         begin
            Result := Checksum_Assoc_F_Covered_Fields (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_checksum_assoc_f_covered_fields;


           

   

   
   

   function rflx_refinement_decl_f_pdu
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Refinement_Decl_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Refinement_Decl_F_Pdu (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_refinement_decl_f_pdu;


           

   

   
   

   function rflx_refinement_decl_f_field
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Refinement_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Refinement_Decl_F_Field (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_refinement_decl_f_field;


           

   

   
   

   function rflx_refinement_decl_f_sdu
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Refinement_Decl_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Refinement_Decl_F_Sdu (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_refinement_decl_f_sdu;


           

   

   
   

   function rflx_refinement_decl_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Refinement_Decl_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Refinement_Decl_F_Condition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_refinement_decl_f_condition;


           

   

   
   

   function rflx_session_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Session_Decl_Range then

         declare
            

            Result : Bare_Formal_Decl_List;
         begin
            Result := Session_Decl_F_Parameters (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_session_decl_f_parameters;


           

   

   
   

   function rflx_session_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Session_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Session_Decl_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_session_decl_f_identifier;


           

   

   
   

   function rflx_session_decl_f_declarations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Session_Decl_Range then

         declare
            

            Result : Bare_Local_Decl_List;
         begin
            Result := Session_Decl_F_Declarations (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_session_decl_f_declarations;


           

   

   
   

   function rflx_session_decl_f_states
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Session_Decl_Range then

         declare
            

            Result : Bare_State_List;
         begin
            Result := Session_Decl_F_States (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_session_decl_f_states;


           

   

   
   

   function rflx_session_decl_f_end_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Session_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Session_Decl_F_End_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_session_decl_f_end_identifier;


           

   

   
   

   function rflx_type_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Type_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Type_Decl_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_type_decl_f_identifier;


           

   

   
   

   function rflx_type_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Type_Decl_Range then

         declare
            

            Result : Bare_Parameters;
         begin
            Result := Type_Decl_F_Parameters (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_type_decl_f_parameters;


           

   

   
   

   function rflx_type_decl_f_definition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Type_Decl_Range then

         declare
            

            Result : Bare_Type_Def;
         begin
            Result := Type_Decl_F_Definition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_type_decl_f_definition;


           

   

   
   

   function rflx_description_f_content
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Description_Range then

         declare
            

            Result : Bare_String_Literal;
         begin
            Result := Description_F_Content (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_description_f_content;


           

   

   
   

   function rflx_element_value_assoc_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Element_Value_Assoc_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Element_Value_Assoc_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_element_value_assoc_f_identifier;


           

   

   
   

   function rflx_element_value_assoc_f_literal
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Element_Value_Assoc_Range then

         declare
            

            Result : Bare_Numeric_Literal;
         begin
            Result := Element_Value_Assoc_F_Literal (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_element_value_assoc_f_literal;


           

   

   
   

   function rflx_attribute_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Attribute_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Attribute_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_attribute_f_expression;


           

   

   
   

   function rflx_attribute_f_kind
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Attribute_Range then

         declare
            

            Result : Bare_Attr;
         begin
            Result := Attribute_F_Kind (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_attribute_f_kind;


           

   

   
   

   function rflx_bin_op_f_left
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Bin_Op_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Bin_Op_F_Left (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_bin_op_f_left;


           

   

   
   

   function rflx_bin_op_f_op
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Bin_Op_Range then

         declare
            

            Result : Bare_Op;
         begin
            Result := Bin_Op_F_Op (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_bin_op_f_op;


           

   

   
   

   function rflx_bin_op_f_right
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Bin_Op_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Bin_Op_F_Right (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_bin_op_f_right;


           

   

   
   

   function rflx_binding_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Binding_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Binding_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_binding_f_expression;


           

   

   
   

   function rflx_binding_f_bindings
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Binding_Range then

         declare
            

            Result : Bare_Term_Assoc_List;
         begin
            Result := Binding_F_Bindings (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_binding_f_bindings;


           

   

   
   

   function rflx_call_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Call_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Call_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_call_f_identifier;


           

   

   
   

   function rflx_call_f_arguments
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Call_Range then

         declare
            

            Result : Bare_Expr_List;
         begin
            Result := Call_F_Arguments (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_call_f_arguments;


           

   

   
   

   function rflx_case_expression_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Case_Expression_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Case_Expression_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_case_expression_f_expression;


           

   

   
   

   function rflx_case_expression_f_choices
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Case_Expression_Range then

         declare
            

            Result : Bare_Choice_List;
         begin
            Result := Case_Expression_F_Choices (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_case_expression_f_choices;


           

   

   
   

   function rflx_choice_f_selectors
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Choice_Range then

         declare
            

            Result : Bare_R_F_L_X_Node_List;
         begin
            Result := Choice_F_Selectors (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_choice_f_selectors;


           

   

   
   

   function rflx_choice_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Choice_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Choice_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_choice_f_expression;


           

   

   
   

   function rflx_comprehension_f_iterator
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Comprehension_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Comprehension_F_Iterator (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_comprehension_f_iterator;


           

   

   
   

   function rflx_comprehension_f_sequence
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Comprehension_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Comprehension_F_Sequence (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_comprehension_f_sequence;


           

   

   
   

   function rflx_comprehension_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Comprehension_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Comprehension_F_Condition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_comprehension_f_condition;


           

   

   
   

   function rflx_comprehension_f_selector
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Comprehension_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Comprehension_F_Selector (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_comprehension_f_selector;


           

   

   
   

   function rflx_context_item_f_item
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Context_Item_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Context_Item_F_Item (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_context_item_f_item;


           

   

   
   

   function rflx_conversion_f_target_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Conversion_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Conversion_F_Target_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_conversion_f_target_identifier;


           

   

   
   

   function rflx_conversion_f_argument
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Conversion_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Conversion_F_Argument (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_conversion_f_argument;


           

   

   
   

   function rflx_message_aggregate_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Aggregate_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Message_Aggregate_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_aggregate_f_identifier;


           

   

   
   

   function rflx_message_aggregate_f_values
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Aggregate_Range then

         declare
            

            Result : Bare_Base_Aggregate;
         begin
            Result := Message_Aggregate_F_Values (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_aggregate_f_values;


           

   

   
   

   function rflx_negation_f_data
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Negation_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Negation_F_Data (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_negation_f_data;


           

   

   
   

   function rflx_paren_expression_f_data
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Paren_Expression_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Paren_Expression_F_Data (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_paren_expression_f_data;


           

   

   
   

   function rflx_quantified_expression_f_operation
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Quantified_Expression_Range then

         declare
            

            Result : Bare_Quantifier;
         begin
            Result := Quantified_Expression_F_Operation (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_quantified_expression_f_operation;


           

   

   
   

   function rflx_quantified_expression_f_parameter_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Quantified_Expression_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Quantified_Expression_F_Parameter_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_quantified_expression_f_parameter_identifier;


           

   

   
   

   function rflx_quantified_expression_f_iterable
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Quantified_Expression_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Quantified_Expression_F_Iterable (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_quantified_expression_f_iterable;


           

   

   
   

   function rflx_quantified_expression_f_predicate
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Quantified_Expression_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Quantified_Expression_F_Predicate (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_quantified_expression_f_predicate;


           

   

   
   

   function rflx_select_node_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Select_Node_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Select_Node_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_select_node_f_expression;


           

   

   
   

   function rflx_select_node_f_selector
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Select_Node_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Select_Node_F_Selector (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_select_node_f_selector;


           

   

   
   

   function rflx_concatenation_f_left
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Concatenation_Range then

         declare
            

            Result : Bare_Sequence_Literal;
         begin
            Result := Concatenation_F_Left (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_concatenation_f_left;


           

   

   
   

   function rflx_concatenation_f_right
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Concatenation_Range then

         declare
            

            Result : Bare_Sequence_Literal;
         begin
            Result := Concatenation_F_Right (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_concatenation_f_right;


           

   

   
   

   function rflx_sequence_aggregate_f_values
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Sequence_Aggregate_Range then

         declare
            

            Result : Bare_Numeric_Literal_List;
         begin
            Result := Sequence_Aggregate_F_Values (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_sequence_aggregate_f_values;


           

   

   
   

   function rflx_variable_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Variable_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Variable_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_variable_f_identifier;


           

   

   
   

   function rflx_formal_channel_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Formal_Channel_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Formal_Channel_Decl_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_formal_channel_decl_f_identifier;


           

   

   
   

   function rflx_formal_channel_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Formal_Channel_Decl_Range then

         declare
            

            Result : Bare_Channel_Attribute_List;
         begin
            Result := Formal_Channel_Decl_F_Parameters (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_formal_channel_decl_f_parameters;


           

   

   
   

   function rflx_formal_function_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Formal_Function_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Formal_Function_Decl_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_formal_function_decl_f_identifier;


           

   

   
   

   function rflx_formal_function_decl_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Formal_Function_Decl_Range then

         declare
            

            Result : Bare_Parameters;
         begin
            Result := Formal_Function_Decl_F_Parameters (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_formal_function_decl_f_parameters;


           

   

   
   

   function rflx_formal_function_decl_f_return_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Formal_Function_Decl_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Formal_Function_Decl_F_Return_Type_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_formal_function_decl_f_return_type_identifier;


           

   

   
   

   function rflx_renaming_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Renaming_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Renaming_Decl_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_renaming_decl_f_identifier;


           

   

   
   

   function rflx_renaming_decl_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Renaming_Decl_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Renaming_Decl_F_Type_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_renaming_decl_f_type_identifier;


           

   

   
   

   function rflx_renaming_decl_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Renaming_Decl_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Renaming_Decl_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_renaming_decl_f_expression;


           

   

   
   

   function rflx_variable_decl_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Variable_Decl_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Variable_Decl_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_variable_decl_f_identifier;


           

   

   
   

   function rflx_variable_decl_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Variable_Decl_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Variable_Decl_F_Type_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_variable_decl_f_type_identifier;


           

   

   
   

   function rflx_variable_decl_f_initializer
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Variable_Decl_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Variable_Decl_F_Initializer (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_variable_decl_f_initializer;


           

   

   
   

   function rflx_message_aggregate_association_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Aggregate_Association_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Message_Aggregate_Association_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_aggregate_association_f_identifier;


           

   

   
   

   function rflx_message_aggregate_association_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Aggregate_Association_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Message_Aggregate_Association_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_aggregate_association_f_expression;


           

   

   
   

   function rflx_byte_order_aspect_f_byte_order
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Byte_Order_Aspect_Range then

         declare
            

            Result : Bare_Byte_Order_Type;
         begin
            Result := Byte_Order_Aspect_F_Byte_Order (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_byte_order_aspect_f_byte_order;


           

   

   
   

   function rflx_checksum_aspect_f_associations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Checksum_Aspect_Range then

         declare
            

            Result : Bare_Checksum_Assoc_List;
         begin
            Result := Checksum_Aspect_F_Associations (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_checksum_aspect_f_associations;


           

   

   
   

   function rflx_message_field_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Message_Field_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_f_identifier;


           

   

   
   

   function rflx_message_field_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Message_Field_F_Type_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_f_type_identifier;


           

   

   
   

   function rflx_message_field_f_type_arguments
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Range then

         declare
            

            Result : Bare_Type_Argument_List;
         begin
            Result := Message_Field_F_Type_Arguments (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_f_type_arguments;


           

   

   
   

   function rflx_message_field_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Range then

         declare
            

            Result : Bare_Aspect_List;
         begin
            Result := Message_Field_F_Aspects (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_f_aspects;


           

   

   
   

   function rflx_message_field_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Message_Field_F_Condition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_f_condition;


           

   

   
   

   function rflx_message_field_f_thens
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Range then

         declare
            

            Result : Bare_Then_Node_List;
         begin
            Result := Message_Field_F_Thens (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_f_thens;


           

   

   
   

   function rflx_message_fields_f_initial_field
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Fields_Range then

         declare
            

            Result : Bare_Null_Message_Field;
         begin
            Result := Message_Fields_F_Initial_Field (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_fields_f_initial_field;


           

   

   
   

   function rflx_message_fields_f_fields
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Fields_Range then

         declare
            

            Result : Bare_Message_Field_List;
         begin
            Result := Message_Fields_F_Fields (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_fields_f_fields;


           

   

   
   

   function rflx_null_message_field_f_thens
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Null_Message_Field_Range then

         declare
            

            Result : Bare_Then_Node_List;
         begin
            Result := Null_Message_Field_F_Thens (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_null_message_field_f_thens;


           

   

   
   

   function rflx_package_node_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Package_Node_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Package_Node_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_package_node_f_identifier;


           

   

   
   

   function rflx_package_node_f_declarations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Package_Node_Range then

         declare
            

            Result : Bare_Declaration_List;
         begin
            Result := Package_Node_F_Declarations (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_package_node_f_declarations;


           

   

   
   

   function rflx_package_node_f_end_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Package_Node_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Package_Node_F_End_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_package_node_f_end_identifier;


           

   

   
   

   function rflx_parameter_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Parameter_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Parameter_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_parameter_f_identifier;


           

   

   
   

   function rflx_parameter_f_type_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Parameter_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Parameter_F_Type_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_parameter_f_type_identifier;


           

   

   
   

   function rflx_parameters_f_parameters
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Parameters_Range then

         declare
            

            Result : Bare_Parameter_List;
         begin
            Result := Parameters_F_Parameters (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_parameters_f_parameters;


           

   

   
   

   function rflx_specification_f_context_clause
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Specification_Range then

         declare
            

            Result : Bare_Context_Item_List;
         begin
            Result := Specification_F_Context_Clause (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_specification_f_context_clause;


           

   

   
   

   function rflx_specification_f_package_declaration
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Specification_Range then

         declare
            

            Result : Bare_Package_Node;
         begin
            Result := Specification_F_Package_Declaration (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_specification_f_package_declaration;


           

   

   
   

   function rflx_state_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := State_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_f_identifier;


           

   

   
   

   function rflx_state_f_description
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Range then

         declare
            

            Result : Bare_Description;
         begin
            Result := State_F_Description (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_f_description;


           

   

   
   

   function rflx_state_f_body
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Range then

         declare
            

            Result : Bare_State_Body;
         begin
            Result := State_F_Body (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_f_body;


           

   

   
   

   function rflx_state_body_f_declarations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Body_Range then

         declare
            

            Result : Bare_Local_Decl_List;
         begin
            Result := State_Body_F_Declarations (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_body_f_declarations;


           

   

   
   

   function rflx_state_body_f_actions
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Body_Range then

         declare
            

            Result : Bare_Statement_List;
         begin
            Result := State_Body_F_Actions (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_body_f_actions;


           

   

   
   

   function rflx_state_body_f_conditional_transitions
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Body_Range then

         declare
            

            Result : Bare_Conditional_Transition_List;
         begin
            Result := State_Body_F_Conditional_Transitions (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_body_f_conditional_transitions;


           

   

   
   

   function rflx_state_body_f_final_transition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Body_Range then

         declare
            

            Result : Bare_Transition;
         begin
            Result := State_Body_F_Final_Transition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_body_f_final_transition;


           

   

   
   

   function rflx_state_body_f_exception_transition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Body_Range then

         declare
            

            Result : Bare_Transition;
         begin
            Result := State_Body_F_Exception_Transition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_body_f_exception_transition;


           

   

   
   

   function rflx_state_body_f_end_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_State_Body_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := State_Body_F_End_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_state_body_f_end_identifier;


           

   

   
   

   function rflx_assignment_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Assignment_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Assignment_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_assignment_f_identifier;


           

   

   
   

   function rflx_assignment_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Assignment_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Assignment_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_assignment_f_expression;


           

   

   
   

   function rflx_attribute_statement_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Attribute_Statement_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Attribute_Statement_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_attribute_statement_f_identifier;


           

   

   
   

   function rflx_attribute_statement_f_attr
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Attribute_Statement_Range then

         declare
            

            Result : Bare_Attr_Stmt;
         begin
            Result := Attribute_Statement_F_Attr (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_attribute_statement_f_attr;


           

   

   
   

   function rflx_attribute_statement_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Attribute_Statement_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Attribute_Statement_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_attribute_statement_f_expression;


           

   

   
   

   function rflx_message_field_assignment_f_message
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Assignment_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Message_Field_Assignment_F_Message (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_assignment_f_message;


           

   

   
   

   function rflx_message_field_assignment_f_field
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Assignment_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Message_Field_Assignment_F_Field (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_assignment_f_field;


           

   

   
   

   function rflx_message_field_assignment_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Field_Assignment_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Message_Field_Assignment_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_field_assignment_f_expression;


           

   

   
   

   function rflx_reset_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Reset_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Reset_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_reset_f_identifier;


           

   

   
   

   function rflx_reset_f_associations
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Reset_Range then

         declare
            

            Result : Bare_Message_Aggregate_Association_List;
         begin
            Result := Reset_F_Associations (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_reset_f_associations;


           

   

   
   

   function rflx_term_assoc_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Term_Assoc_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Term_Assoc_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_term_assoc_f_identifier;


           

   

   
   

   function rflx_term_assoc_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Term_Assoc_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Term_Assoc_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_term_assoc_f_expression;


           

   

   
   

   function rflx_then_node_f_target
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Then_Node_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Then_Node_F_Target (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_then_node_f_target;


           

   

   
   

   function rflx_then_node_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Then_Node_Range then

         declare
            

            Result : Bare_Aspect_List;
         begin
            Result := Then_Node_F_Aspects (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_then_node_f_aspects;


           

   

   
   

   function rflx_then_node_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Then_Node_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Then_Node_F_Condition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_then_node_f_condition;


           

   

   
   

   function rflx_transition_f_target
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Transition_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Transition_F_Target (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_transition_f_target;


           

   

   
   

   function rflx_transition_f_description
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Transition_Range then

         declare
            

            Result : Bare_Description;
         begin
            Result := Transition_F_Description (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_transition_f_description;


           

   

   
   

   function rflx_conditional_transition_f_condition
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Conditional_Transition_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Conditional_Transition_F_Condition (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_conditional_transition_f_condition;


           

   

   
   

   function rflx_type_argument_f_identifier
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Type_Argument_Range then

         declare
            

            Result : Bare_Unqualified_I_D;
         begin
            Result := Type_Argument_F_Identifier (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_type_argument_f_identifier;


           

   

   
   

   function rflx_type_argument_f_expression
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Type_Argument_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Type_Argument_F_Expression (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_type_argument_f_expression;


           

   

   
   

   function rflx_message_type_def_f_message_fields
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Type_Def_Range then

         declare
            

            Result : Bare_Message_Fields;
         begin
            Result := Message_Type_Def_F_Message_Fields (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_type_def_f_message_fields;


           

   

   
   

   function rflx_message_type_def_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Message_Type_Def_Range then

         declare
            

            Result : Bare_Message_Aspect_List;
         begin
            Result := Message_Type_Def_F_Aspects (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_message_type_def_f_aspects;


           

   

   
   

   function rflx_named_enumeration_def_f_elements
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Named_Enumeration_Def_Range then

         declare
            

            Result : Bare_Element_Value_Assoc_List;
         begin
            Result := Named_Enumeration_Def_F_Elements (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_named_enumeration_def_f_elements;


           

   

   
   

   function rflx_positional_enumeration_def_f_elements
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Positional_Enumeration_Def_Range then

         declare
            

            Result : Bare_Unqualified_I_D_List;
         begin
            Result := Positional_Enumeration_Def_F_Elements (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_positional_enumeration_def_f_elements;


           

   

   
   

   function rflx_enumeration_type_def_f_elements
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Enumeration_Type_Def_Range then

         declare
            

            Result : Bare_Enumeration_Def;
         begin
            Result := Enumeration_Type_Def_F_Elements (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_enumeration_type_def_f_elements;


           

   

   
   

   function rflx_enumeration_type_def_f_aspects
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Enumeration_Type_Def_Range then

         declare
            

            Result : Bare_Aspect_List;
         begin
            Result := Enumeration_Type_Def_F_Aspects (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_enumeration_type_def_f_aspects;


           

   

   
   

   function rflx_modular_type_def_f_mod
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Modular_Type_Def_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Modular_Type_Def_F_Mod (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_modular_type_def_f_mod;


           

   

   
   

   function rflx_range_type_def_f_first
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Range_Type_Def_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Range_Type_Def_F_First (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_range_type_def_f_first;


           

   

   
   

   function rflx_range_type_def_f_last
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Range_Type_Def_Range then

         declare
            

            Result : Bare_Expr;
         begin
            Result := Range_Type_Def_F_Last (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_range_type_def_f_last;


           

   

   
   

   function rflx_range_type_def_f_size
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Range_Type_Def_Range then

         declare
            

            Result : Bare_Aspect;
         begin
            Result := Range_Type_Def_F_Size (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_range_type_def_f_size;


           

   

   
   

   function rflx_sequence_type_def_f_element_type
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Sequence_Type_Def_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Sequence_Type_Def_F_Element_Type (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_sequence_type_def_f_element_type;


           

   

   
   

   function rflx_type_derivation_def_f_base
     (Node : rflx_node_Ptr;


      Value_P : access rflx_node) return int

   is
      Unwrapped_Node : constant Bare_R_F_L_X_Node := Node.Node;
   begin
      Clear_Last_Exception;


      if Unwrapped_Node.Kind in Rflx_Type_Derivation_Def_Range then

         declare
            

            Result : Bare_I_D;
         begin
            Result := Type_Derivation_Def_F_Base (Unwrapped_Node);

            Value_P.all :=
                   (Result, Node.Info)
            ;

            return 1;
         exception
            when Exc : Property_Error =>
               Set_Last_Exception (Exc);
               return 0;
         end;

      else
         return 0;
      end if;

   exception
      when Exc : others =>
         Set_Last_Exception (Exc);
         return 0;
   end rflx_type_derivation_def_f_base;



         






         



function rflx_node_array_create (Length : int) return Internal_Entity_Array_Access is
begin
   Clear_Last_Exception;
   return Create_Internal_Entity_Array (Natural (Length));
exception
   when Exc : others =>
      Set_Last_Exception (Exc);
      return null;
end rflx_node_array_create;

procedure rflx_node_array_inc_ref (A : Internal_Entity_Array_Access) is
begin
   Clear_Last_Exception;
   Inc_Ref (A);
exception
   when Exc : others =>
      Set_Last_Exception (Exc);
end;

procedure rflx_node_array_dec_ref (A : Internal_Entity_Array_Access) is
begin
   Clear_Last_Exception;
   declare
      A_Var : Internal_Entity_Array_Access := A;
   begin
      Dec_Ref (A_Var);
   end;
exception
   when Exc : others =>
      Set_Last_Exception (Exc);
end;




end Librflxlang.Implementation.C;
