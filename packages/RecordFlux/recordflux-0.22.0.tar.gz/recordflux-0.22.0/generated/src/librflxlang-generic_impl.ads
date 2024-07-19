
with Ada.Unchecked_Conversion;

with Langkit_Support.Diagnostics;       use Langkit_Support.Diagnostics;
with Langkit_Support.File_Readers;      use Langkit_Support.File_Readers;
with Langkit_Support.Generic_API;       use Langkit_Support.Generic_API;
with Langkit_Support.Generic_API.Introspection;
use Langkit_Support.Generic_API.Introspection;
with Langkit_Support.Internal;          use Langkit_Support.Internal;
with Langkit_Support.Internal.Analysis; use Langkit_Support.Internal.Analysis;
with Langkit_Support.Internal.Descriptor;
use Langkit_Support.Internal.Descriptor;
with Langkit_Support.Slocs;             use Langkit_Support.Slocs;
with Langkit_Support.Text;              use Langkit_Support.Text;
with Langkit_Support.Types;             use Langkit_Support.Types;

with Librflxlang.Implementation;
with Librflxlang.Generic_Introspection;
use Librflxlang.Generic_Introspection;
with Librflxlang.Private_Converters; use Librflxlang.Private_Converters;

with Librflxlang.Common;

--  This package provide Librflxlang-specific implementations for the
--  generic operations defined in Langkit_Support.Internal.Descriptor.

private package Librflxlang.Generic_Impl is

   function "+" is new Ada.Unchecked_Conversion
     (Internal_Context, Implementation.Internal_Context);
   function "+" is new Ada.Unchecked_Conversion
     (Implementation.Internal_Context, Internal_Context);

   function "+" is new Ada.Unchecked_Conversion
     (Internal_Unit, Implementation.Internal_Unit);
   function "+" is new Ada.Unchecked_Conversion
     (Implementation.Internal_Unit, Internal_Unit);

   function "+" is new Ada.Unchecked_Conversion
     (Internal_Node, Implementation.Bare_R_F_L_X_Node);
   function "+" is new Ada.Unchecked_Conversion
     (Implementation.Bare_R_F_L_X_Node, Internal_Node);

   function "+"
     (Entity : Internal_Entity) return Implementation.Internal_Entity
     with Export,
          External_Name => "Librflxlang__from_generic_internal_entity";
   function "+"
     (Entity : Implementation.Internal_Entity) return Internal_Entity
     with Export,
          External_Name => "Librflxlang__to_generic_internal_entity";

   function "+" (Rule : Grammar_Rule_Index) return Common.Grammar_Rule
   is (Common.Grammar_Rule'Val (Rule - 1));
   --  Grammar rules start at 1 in the generic API: rebase the value before
   --  converting it to the native type.

   function "+" (Token : Common.Token_Reference) return Internal_Token
   is ((Get_Token_TDH (Token), Get_Token_Index (Token)));

   function Wrap_Token
     (Context : Internal_Context;
      Token   : Internal_Token) return Common.Token_Reference
   is (Wrap_Token_Reference (+Context, Token.TDH, Token.Index));

   --  Descriptors for token kinds

   
      
      Token_Kind_Name_1 : aliased constant Text_Type :=
        "Termination";
      
      Token_Kind_Name_2 : aliased constant Text_Type :=
        "Lexing_Failure";
      
      Token_Kind_Name_3 : aliased constant Text_Type :=
        "Unqualified_Identifier";
      
      Token_Kind_Name_4 : aliased constant Text_Type :=
        "Package";
      
      Token_Kind_Name_5 : aliased constant Text_Type :=
        "Is";
      
      Token_Kind_Name_6 : aliased constant Text_Type :=
        "If";
      
      Token_Kind_Name_7 : aliased constant Text_Type :=
        "End";
      
      Token_Kind_Name_8 : aliased constant Text_Type :=
        "Null";
      
      Token_Kind_Name_9 : aliased constant Text_Type :=
        "Type";
      
      Token_Kind_Name_10 : aliased constant Text_Type :=
        "Range";
      
      Token_Kind_Name_11 : aliased constant Text_Type :=
        "With";
      
      Token_Kind_Name_12 : aliased constant Text_Type :=
        "Mod";
      
      Token_Kind_Name_13 : aliased constant Text_Type :=
        "Message";
      
      Token_Kind_Name_14 : aliased constant Text_Type :=
        "Then";
      
      Token_Kind_Name_15 : aliased constant Text_Type :=
        "Sequence";
      
      Token_Kind_Name_16 : aliased constant Text_Type :=
        "Of";
      
      Token_Kind_Name_17 : aliased constant Text_Type :=
        "In";
      
      Token_Kind_Name_18 : aliased constant Text_Type :=
        "Not";
      
      Token_Kind_Name_19 : aliased constant Text_Type :=
        "New";
      
      Token_Kind_Name_20 : aliased constant Text_Type :=
        "For";
      
      Token_Kind_Name_21 : aliased constant Text_Type :=
        "When";
      
      Token_Kind_Name_22 : aliased constant Text_Type :=
        "Where";
      
      Token_Kind_Name_23 : aliased constant Text_Type :=
        "Use";
      
      Token_Kind_Name_24 : aliased constant Text_Type :=
        "All";
      
      Token_Kind_Name_25 : aliased constant Text_Type :=
        "Some";
      
      Token_Kind_Name_26 : aliased constant Text_Type :=
        "Generic";
      
      Token_Kind_Name_27 : aliased constant Text_Type :=
        "Session";
      
      Token_Kind_Name_28 : aliased constant Text_Type :=
        "Begin";
      
      Token_Kind_Name_29 : aliased constant Text_Type :=
        "Return";
      
      Token_Kind_Name_30 : aliased constant Text_Type :=
        "Function";
      
      Token_Kind_Name_31 : aliased constant Text_Type :=
        "State";
      
      Token_Kind_Name_32 : aliased constant Text_Type :=
        "Transition";
      
      Token_Kind_Name_33 : aliased constant Text_Type :=
        "Goto";
      
      Token_Kind_Name_34 : aliased constant Text_Type :=
        "Exception";
      
      Token_Kind_Name_35 : aliased constant Text_Type :=
        "Renames";
      
      Token_Kind_Name_36 : aliased constant Text_Type :=
        "Channel";
      
      Token_Kind_Name_37 : aliased constant Text_Type :=
        "Readable";
      
      Token_Kind_Name_38 : aliased constant Text_Type :=
        "Writable";
      
      Token_Kind_Name_39 : aliased constant Text_Type :=
        "Desc";
      
      Token_Kind_Name_40 : aliased constant Text_Type :=
        "Append";
      
      Token_Kind_Name_41 : aliased constant Text_Type :=
        "Extend";
      
      Token_Kind_Name_42 : aliased constant Text_Type :=
        "Read";
      
      Token_Kind_Name_43 : aliased constant Text_Type :=
        "Write";
      
      Token_Kind_Name_44 : aliased constant Text_Type :=
        "Reset";
      
      Token_Kind_Name_45 : aliased constant Text_Type :=
        "High_Order_First";
      
      Token_Kind_Name_46 : aliased constant Text_Type :=
        "Low_Order_First";
      
      Token_Kind_Name_47 : aliased constant Text_Type :=
        "Case";
      
      Token_Kind_Name_48 : aliased constant Text_Type :=
        "First";
      
      Token_Kind_Name_49 : aliased constant Text_Type :=
        "Size";
      
      Token_Kind_Name_50 : aliased constant Text_Type :=
        "Last";
      
      Token_Kind_Name_51 : aliased constant Text_Type :=
        "Byte_Order";
      
      Token_Kind_Name_52 : aliased constant Text_Type :=
        "Checksum";
      
      Token_Kind_Name_53 : aliased constant Text_Type :=
        "Valid_Checksum";
      
      Token_Kind_Name_54 : aliased constant Text_Type :=
        "Has_Data";
      
      Token_Kind_Name_55 : aliased constant Text_Type :=
        "Head";
      
      Token_Kind_Name_56 : aliased constant Text_Type :=
        "Opaque";
      
      Token_Kind_Name_57 : aliased constant Text_Type :=
        "Present";
      
      Token_Kind_Name_58 : aliased constant Text_Type :=
        "Valid";
      
      Token_Kind_Name_59 : aliased constant Text_Type :=
        "Dot";
      
      Token_Kind_Name_60 : aliased constant Text_Type :=
        "Comma";
      
      Token_Kind_Name_61 : aliased constant Text_Type :=
        "Double_Dot";
      
      Token_Kind_Name_62 : aliased constant Text_Type :=
        "Tick";
      
      Token_Kind_Name_63 : aliased constant Text_Type :=
        "Hash";
      
      Token_Kind_Name_64 : aliased constant Text_Type :=
        "Minus";
      
      Token_Kind_Name_65 : aliased constant Text_Type :=
        "Arrow";
      
      Token_Kind_Name_66 : aliased constant Text_Type :=
        "L_Par";
      
      Token_Kind_Name_67 : aliased constant Text_Type :=
        "R_Par";
      
      Token_Kind_Name_68 : aliased constant Text_Type :=
        "L_Brack";
      
      Token_Kind_Name_69 : aliased constant Text_Type :=
        "R_Brack";
      
      Token_Kind_Name_70 : aliased constant Text_Type :=
        "Exp";
      
      Token_Kind_Name_71 : aliased constant Text_Type :=
        "Mul";
      
      Token_Kind_Name_72 : aliased constant Text_Type :=
        "Div";
      
      Token_Kind_Name_73 : aliased constant Text_Type :=
        "Add";
      
      Token_Kind_Name_74 : aliased constant Text_Type :=
        "Sub";
      
      Token_Kind_Name_75 : aliased constant Text_Type :=
        "Eq";
      
      Token_Kind_Name_76 : aliased constant Text_Type :=
        "Neq";
      
      Token_Kind_Name_77 : aliased constant Text_Type :=
        "Leq";
      
      Token_Kind_Name_78 : aliased constant Text_Type :=
        "Lt";
      
      Token_Kind_Name_79 : aliased constant Text_Type :=
        "Le";
      
      Token_Kind_Name_80 : aliased constant Text_Type :=
        "Gt";
      
      Token_Kind_Name_81 : aliased constant Text_Type :=
        "Ge";
      
      Token_Kind_Name_82 : aliased constant Text_Type :=
        "And";
      
      Token_Kind_Name_83 : aliased constant Text_Type :=
        "Or";
      
      Token_Kind_Name_84 : aliased constant Text_Type :=
        "Ampersand";
      
      Token_Kind_Name_85 : aliased constant Text_Type :=
        "Semicolon";
      
      Token_Kind_Name_86 : aliased constant Text_Type :=
        "Double_Colon";
      
      Token_Kind_Name_87 : aliased constant Text_Type :=
        "Assignment";
      
      Token_Kind_Name_88 : aliased constant Text_Type :=
        "Colon";
      
      Token_Kind_Name_89 : aliased constant Text_Type :=
        "Pipe";
      
      Token_Kind_Name_90 : aliased constant Text_Type :=
        "Comment";
      
      Token_Kind_Name_91 : aliased constant Text_Type :=
        "Numeral";
      
      Token_Kind_Name_92 : aliased constant Text_Type :=
        "String_Literal";
   Token_Kind_Names : aliased constant Token_Kind_Name_Array :=
     (1 => Token_Kind_Name_1'Access, 2 => Token_Kind_Name_2'Access, 3 => Token_Kind_Name_3'Access, 4 => Token_Kind_Name_4'Access, 5 => Token_Kind_Name_5'Access, 6 => Token_Kind_Name_6'Access, 7 => Token_Kind_Name_7'Access, 8 => Token_Kind_Name_8'Access, 9 => Token_Kind_Name_9'Access, 10 => Token_Kind_Name_10'Access, 11 => Token_Kind_Name_11'Access, 12 => Token_Kind_Name_12'Access, 13 => Token_Kind_Name_13'Access, 14 => Token_Kind_Name_14'Access, 15 => Token_Kind_Name_15'Access, 16 => Token_Kind_Name_16'Access, 17 => Token_Kind_Name_17'Access, 18 => Token_Kind_Name_18'Access, 19 => Token_Kind_Name_19'Access, 20 => Token_Kind_Name_20'Access, 21 => Token_Kind_Name_21'Access, 22 => Token_Kind_Name_22'Access, 23 => Token_Kind_Name_23'Access, 24 => Token_Kind_Name_24'Access, 25 => Token_Kind_Name_25'Access, 26 => Token_Kind_Name_26'Access, 27 => Token_Kind_Name_27'Access, 28 => Token_Kind_Name_28'Access, 29 => Token_Kind_Name_29'Access, 30 => Token_Kind_Name_30'Access, 31 => Token_Kind_Name_31'Access, 32 => Token_Kind_Name_32'Access, 33 => Token_Kind_Name_33'Access, 34 => Token_Kind_Name_34'Access, 35 => Token_Kind_Name_35'Access, 36 => Token_Kind_Name_36'Access, 37 => Token_Kind_Name_37'Access, 38 => Token_Kind_Name_38'Access, 39 => Token_Kind_Name_39'Access, 40 => Token_Kind_Name_40'Access, 41 => Token_Kind_Name_41'Access, 42 => Token_Kind_Name_42'Access, 43 => Token_Kind_Name_43'Access, 44 => Token_Kind_Name_44'Access, 45 => Token_Kind_Name_45'Access, 46 => Token_Kind_Name_46'Access, 47 => Token_Kind_Name_47'Access, 48 => Token_Kind_Name_48'Access, 49 => Token_Kind_Name_49'Access, 50 => Token_Kind_Name_50'Access, 51 => Token_Kind_Name_51'Access, 52 => Token_Kind_Name_52'Access, 53 => Token_Kind_Name_53'Access, 54 => Token_Kind_Name_54'Access, 55 => Token_Kind_Name_55'Access, 56 => Token_Kind_Name_56'Access, 57 => Token_Kind_Name_57'Access, 58 => Token_Kind_Name_58'Access, 59 => Token_Kind_Name_59'Access, 60 => Token_Kind_Name_60'Access, 61 => Token_Kind_Name_61'Access, 62 => Token_Kind_Name_62'Access, 63 => Token_Kind_Name_63'Access, 64 => Token_Kind_Name_64'Access, 65 => Token_Kind_Name_65'Access, 66 => Token_Kind_Name_66'Access, 67 => Token_Kind_Name_67'Access, 68 => Token_Kind_Name_68'Access, 69 => Token_Kind_Name_69'Access, 70 => Token_Kind_Name_70'Access, 71 => Token_Kind_Name_71'Access, 72 => Token_Kind_Name_72'Access, 73 => Token_Kind_Name_73'Access, 74 => Token_Kind_Name_74'Access, 75 => Token_Kind_Name_75'Access, 76 => Token_Kind_Name_76'Access, 77 => Token_Kind_Name_77'Access, 78 => Token_Kind_Name_78'Access, 79 => Token_Kind_Name_79'Access, 80 => Token_Kind_Name_80'Access, 81 => Token_Kind_Name_81'Access, 82 => Token_Kind_Name_82'Access, 83 => Token_Kind_Name_83'Access, 84 => Token_Kind_Name_84'Access, 85 => Token_Kind_Name_85'Access, 86 => Token_Kind_Name_86'Access, 87 => Token_Kind_Name_87'Access, 88 => Token_Kind_Name_88'Access, 89 => Token_Kind_Name_89'Access, 90 => Token_Kind_Name_90'Access, 91 => Token_Kind_Name_91'Access, 92 => Token_Kind_Name_92'Access);

   --  Implementations for generic operations on analysis types

   function Create_Context
     (Charset     : String;
      File_Reader : File_Reader_Reference;
      With_Trivia : Boolean;
      Tab_Stop    : Natural) return Internal_Context;

   procedure Context_Inc_Ref (Context : Internal_Context);
   procedure Context_Dec_Ref (Context : in out Internal_Context);
   function Context_Version (Context : Internal_Context) return Version_Number;
   function Context_Has_Unit
     (Context : Internal_Context; Unit_Filename : String) return Boolean;
   function Context_Get_From_File
     (Context           : Internal_Context;
      Filename, Charset : String;
      Reparse           : Boolean;
      Rule              : Grammar_Rule_Index) return Internal_Unit;
   function Context_Get_From_Buffer
     (Context                   : Internal_Context;
      Filename, Buffer, Charset : String;
      Rule                      : Grammar_Rule_Index) return Internal_Unit;

   function Unit_Context (Unit : Internal_Unit) return Internal_Context;
   function Unit_Version (Unit : Internal_Unit) return Version_Number;
   function Unit_Filename (Unit : Internal_Unit) return String;
   function Unit_Diagnostics (Unit : Internal_Unit) return Diagnostics_Access;
   function Unit_Format_GNU_Diagnostic
     (Unit : Internal_Unit; D : Diagnostic) return String;
   function Unit_Root (Unit : Internal_Unit) return Internal_Node;
   function Unit_First_Token (Unit : Internal_Unit) return Internal_Token;
   function Unit_Last_Token (Unit : Internal_Unit) return Internal_Token;
   function Unit_Get_Line
     (Unit : Internal_Unit; Line_Number : Positive) return Text_Type;

   type Internal_Node_Metadata_Type is record
      Ref_Count : Natural;
      Internal  : Implementation.Internal_Metadata;
   end record;
   type Internal_Node_Metadata_Access is
      access all Internal_Node_Metadata_Type;

   function "+" is new Ada.Unchecked_Conversion
     (Internal_Node_Metadata, Internal_Node_Metadata_Access);
   function "+" is new Ada.Unchecked_Conversion
     (Internal_Node_Metadata_Access, Internal_Node_Metadata);

   procedure Node_Metadata_Inc_Ref (Metadata : Internal_Node_Metadata);
   procedure Node_Metadata_Dec_Ref (Metadata : in out Internal_Node_Metadata);
   function Node_Metadata_Compare
     (L, R : Internal_Node_Metadata) return Boolean;

   function Node_Unit (Node : Internal_Node) return Internal_Unit;
   function Node_Kind (Node : Internal_Node) return Type_Index;
   function Node_Parent (Node : Internal_Entity) return Internal_Entity;
   function Node_Parents
     (Node : Internal_Entity; With_Self : Boolean) return Internal_Entity_Array;
   function Node_Children_Count (Node : Internal_Node) return Natural;
   procedure Node_Get_Child
     (Node            : Internal_Node;
      Index           : Positive;
      Index_In_Bounds : out Boolean;
      Result          : out Internal_Node);
   function Node_Fetch_Sibling
     (Node : Internal_Node; Offset : Integer) return Internal_Node;
   function Node_Is_Ghost (Node : Analysis.Internal_Node) return Boolean;
   function Node_Token_Start (Node : Internal_Node) return Internal_Token;
   function Node_Token_End (Node : Internal_Node) return Internal_Token;
   function Node_Text (Node : Internal_Node) return Text_Type;
   function Node_Sloc_Range
     (Node : Internal_Node) return Source_Location_Range;
   function Node_Last_Attempted_Child (Node : Internal_Node) return Integer;

   function Entity_Image (Entity : Internal_Entity) return String;

   function Token_Is_Equivalent
     (Left, Right       : Internal_Token;
      Left_SN, Right_SN : Token_Safety_Net) return Boolean;

   --  Language descriptor table for Librflxlang.
   --
   --  We define it here and export its address to avoid making the
   --  $.Generic_API spec (which is public) depend on other implementation
   --  units, which allows not exporting the many symbols from the private
   --  units when building a shared library (Windows has a small limit for the
   --  number of exported symbols).

   Language_Name : aliased constant Text_Type :=
     "Rflx";

   No_Metadata_Value : aliased Internal_Node_Metadata_Type :=
     (0, Implementation.No_Metadata);
   No_Metadata       : Internal_Node_Metadata_Access :=
     No_Metadata_Value'Access;

   Desc : aliased constant Language_Descriptor :=
     (Language_Name => Language_Name'Access,

      Default_Grammar_Rule => 1,
      Grammar_Rules        => Grammar_Rules'Access,

      Token_Kind_Names => Token_Kind_Names'Access,

      Types          => Generic_Introspection.Types'Access,
      Enum_Types     => Generic_Introspection.Enum_Types'Access,
      Array_Types    => Generic_Introspection.Array_Types'Access,
      Iterator_Types => Generic_Introspection.Iterator_Types'Access,
      Struct_Types   => Generic_Introspection.Struct_Types'Access,
      Builtin_Types  => Generic_Introspection.Builtin_Types'Access,
      First_Node     => Generic_Introspection.First_Node,
      Struct_Members => Generic_Introspection.Struct_Members'Access,
      First_Property => Generic_Introspection.First_Property,

      Create_Context          => Create_Context'Access,
      Context_Inc_Ref         => Context_Inc_Ref'Access,
      Context_Dec_Ref         => Context_Dec_Ref'Access,
      Context_Version         => Context_Version'Access,
      Context_Has_Unit        => Context_Has_Unit'Access,
      Context_Get_From_File   => Context_Get_From_File'Access,
      Context_Get_From_Buffer => Context_Get_From_Buffer'Access,

      Unit_Context               => Unit_Context'Access,
      Unit_Version               => Unit_Version'Access,
      Unit_Filename              => Unit_Filename'Access,
      Unit_Diagnostics           => Unit_Diagnostics'Access,
      Unit_Format_GNU_Diagnostic => Unit_Format_GNU_Diagnostic'Access,
      Unit_Root                  => Unit_Root'Access,
      Unit_First_Token           => Unit_First_Token'Access,
      Unit_Last_Token            => Unit_Last_Token'Access,
      Unit_Get_Line              => Unit_Get_Line'Access,

      Node_Metadata_Inc_Ref => Node_Metadata_Inc_Ref'Access,
      Node_Metadata_Dec_Ref => Node_Metadata_Dec_Ref'Access,
      Node_Metadata_Compare => Node_Metadata_Compare'Access,
      Null_Metadata         => +No_Metadata,

      Node_Unit                 => Node_Unit'Access,
      Node_Kind                 => Node_Kind'Access,
      Node_Parent               => Node_Parent'Access,
      Node_Parents              => Node_Parents'Access,
      Node_Children_Count       => Node_Children_Count'Access,
      Node_Get_Child            => Node_Get_Child'Access,
      Node_Fetch_Sibling        => Node_Fetch_Sibling'Access,
      Node_Is_Ghost             => Node_Is_Ghost'Access,
      Node_Token_Start          => Node_Token_Start'Access,
      Node_Token_End            => Node_Token_End'Access,
      Node_Text                 => Node_Text'Access,
      Node_Sloc_Range           => Node_Sloc_Range'Access,
      Node_Last_Attempted_Child => Node_Last_Attempted_Child'Access,

      Entity_Image => Entity_Image'Access,

      Token_Is_Equivalent => Token_Is_Equivalent'Access,

      Create_Enum      => Create_Enum'Access,
      Create_Array     => Create_Array'Access,
      Create_Struct    => Create_Struct'Access,
      Eval_Node_Member => Eval_Node_Member'Access);

end Librflxlang.Generic_Impl;
