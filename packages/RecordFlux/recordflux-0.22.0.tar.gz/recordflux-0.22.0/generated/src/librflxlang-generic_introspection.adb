
pragma Warnings (Off, "referenced");
with Langkit_Support.Internal.Analysis; use Langkit_Support.Internal.Analysis;
with Langkit_Support.Internal.Conversions;
use Langkit_Support.Internal.Conversions;

with Librflxlang.Implementation;
with Librflxlang.Generic_API;       use Librflxlang.Generic_API;
with Librflxlang.Generic_Impl;      use Librflxlang.Generic_Impl;
with Librflxlang.Public_Converters; use Librflxlang.Public_Converters;
with Librflxlang.Private_Converters;
use Librflxlang.Private_Converters;
pragma Warnings (On, "referenced");

package body Librflxlang.Generic_Introspection is

   


      

      ---------
      -- "=" --
      ---------

      overriding function "=" (Left, Right : Internal_Rec_Analysis_Unit_Kind) return Boolean is
      begin
         return Left.Value = Right.Value;
      end "=";

      -------------
      -- Type_Of --
      -------------

      overriding function Type_Of (Value : Internal_Rec_Analysis_Unit_Kind) return Type_Index is
      begin
         return Type_Index_For_Analysis_Unit_Kind;
      end Type_Of;

      -----------
      -- Image --
      -----------

      overriding function Image (Value : Internal_Rec_Analysis_Unit_Kind) return String is
      begin
         return "Analysis_Unit_Kind(" & Value.Value'Image & ")";
      end Image;

      -----------------
      -- Value_Index --
      -----------------

      overriding function Value_Index (Value : Internal_Rec_Analysis_Unit_Kind) return Enum_Value_Index
      is
      begin
         return Analysis_Unit_Kind'Pos (Value.Value) + 1;
      end Value_Index;


      

      ---------
      -- "=" --
      ---------

      overriding function "=" (Left, Right : Internal_Rec_Lookup_Kind) return Boolean is
      begin
         return Left.Value = Right.Value;
      end "=";

      -------------
      -- Type_Of --
      -------------

      overriding function Type_Of (Value : Internal_Rec_Lookup_Kind) return Type_Index is
      begin
         return Type_Index_For_Lookup_Kind;
      end Type_Of;

      -----------
      -- Image --
      -----------

      overriding function Image (Value : Internal_Rec_Lookup_Kind) return String is
      begin
         return "Lookup_Kind(" & Value.Value'Image & ")";
      end Image;

      -----------------
      -- Value_Index --
      -----------------

      overriding function Value_Index (Value : Internal_Rec_Lookup_Kind) return Enum_Value_Index
      is
      begin
         return Lookup_Kind'Pos (Value.Value) + 1;
      end Value_Index;


      

      ---------
      -- "=" --
      ---------

      overriding function "=" (Left, Right : Internal_Rec_Designated_Env_Kind) return Boolean is
      begin
         return Left.Value = Right.Value;
      end "=";

      -------------
      -- Type_Of --
      -------------

      overriding function Type_Of (Value : Internal_Rec_Designated_Env_Kind) return Type_Index is
      begin
         return Type_Index_For_Designated_Env_Kind;
      end Type_Of;

      -----------
      -- Image --
      -----------

      overriding function Image (Value : Internal_Rec_Designated_Env_Kind) return String is
      begin
         return "Designated_Env_Kind(" & Value.Value'Image & ")";
      end Image;

      -----------------
      -- Value_Index --
      -----------------

      overriding function Value_Index (Value : Internal_Rec_Designated_Env_Kind) return Enum_Value_Index
      is
      begin
         return Designated_Env_Kind'Pos (Value.Value) + 1;
      end Value_Index;


      

      ---------
      -- "=" --
      ---------

      overriding function "=" (Left, Right : Internal_Rec_Grammar_Rule) return Boolean is
      begin
         return Left.Value = Right.Value;
      end "=";

      -------------
      -- Type_Of --
      -------------

      overriding function Type_Of (Value : Internal_Rec_Grammar_Rule) return Type_Index is
      begin
         return Type_Index_For_Grammar_Rule;
      end Type_Of;

      -----------
      -- Image --
      -----------

      overriding function Image (Value : Internal_Rec_Grammar_Rule) return String is
      begin
         return "Grammar_Rule(" & Value.Value'Image & ")";
      end Image;

      -----------------
      -- Value_Index --
      -----------------

      overriding function Value_Index (Value : Internal_Rec_Grammar_Rule) return Enum_Value_Index
      is
      begin
         return Grammar_Rule'Pos (Value.Value) + 1;
      end Value_Index;


   -----------------
   -- Create_Enum --
   -----------------

   function Create_Enum
     (Enum_Type   : Type_Index;
      Value_Index : Enum_Value_Index) return Internal_Value_Access
   is
   begin
      case Enum_Type is
            when Type_Index_For_Analysis_Unit_Kind =>
               declare
                  Result : constant Internal_Acc_Analysis_Unit_Kind :=
                    new Internal_Rec_Analysis_Unit_Kind;
               begin
                  Result.Value := Analysis_Unit_Kind'Val (Value_Index - 1);
                  return Internal_Value_Access (Result);
               end;
            when Type_Index_For_Lookup_Kind =>
               declare
                  Result : constant Internal_Acc_Lookup_Kind :=
                    new Internal_Rec_Lookup_Kind;
               begin
                  Result.Value := Lookup_Kind'Val (Value_Index - 1);
                  return Internal_Value_Access (Result);
               end;
            when Type_Index_For_Designated_Env_Kind =>
               declare
                  Result : constant Internal_Acc_Designated_Env_Kind :=
                    new Internal_Rec_Designated_Env_Kind;
               begin
                  Result.Value := Designated_Env_Kind'Val (Value_Index - 1);
                  return Internal_Value_Access (Result);
               end;
            when Type_Index_For_Grammar_Rule =>
               declare
                  Result : constant Internal_Acc_Grammar_Rule :=
                    new Internal_Rec_Grammar_Rule;
               begin
                  Result.Value := Grammar_Rule'Val (Value_Index - 1);
                  return Internal_Value_Access (Result);
               end;

         when others =>
            --  Validation in public wrappers is supposed to prevent calling
            --  this function on non-enum types.
            raise Program_Error;
      end case;
   end Create_Enum;

      

      ---------
      -- "=" --
      ---------

      overriding function "=" (Left, Right : Internal_Rec_R_F_L_X_Node_Array) return Boolean is
      begin
         return Left.Value.all = Right.Value.all;
      end "=";

      -------------
      -- Destroy --
      -------------

      overriding procedure Destroy (Value : in out Internal_Rec_R_F_L_X_Node_Array) is
      begin
         Free (Value.Value);
      end Destroy;

      -------------
      -- Type_Of --
      -------------

      overriding function Type_Of (Value : Internal_Rec_R_F_L_X_Node_Array) return Type_Index is
      begin
         return Type_Index_For_R_F_L_X_Node_Array;
      end Type_Of;

      ------------------
      -- Array_Length --
      ------------------

      overriding function Array_Length (Value : Internal_Rec_R_F_L_X_Node_Array) return Natural is
      begin
         return Value.Value.all'Length;
      end Array_Length;

      ----------------
      -- Array_Item --
      ----------------

      overriding function Array_Item
        (Value : Internal_Rec_R_F_L_X_Node_Array; Index : Positive) return Internal_Value_Access
      is
         Item : R_F_L_X_Node renames Value.Value.all (Index);

         
            Result : Internal_Acc_Node :=  new Internal_Rec_Node;
      begin
            Set_Node (Result, Item);
         return Internal_Value_Access (Result);
      end Array_Item;

      ------------------
      -- Create_Array --
      ------------------

      function Create_Array
        (Values : Internal_Value_Array) return Internal_Acc_R_F_L_X_Node_Array
      is
         Result_Index : Natural := 0;
      begin
         return Result : constant Internal_Acc_R_F_L_X_Node_Array := new Internal_Rec_R_F_L_X_Node_Array do
            Result.Value := new R_F_L_X_Node_Array (1 .. Values'Length);
            for I in Values'Range loop
               Result_Index := Result_Index + 1;
               declare
                  Result_Item : R_F_L_X_Node renames
                    Result.Value (Result_Index);
                  Value       : Internal_Rec_Node renames
                    Internal_Acc_Node (Values (I)).all;
               begin
                     Result_Item := Get_Node (Value);
               end;
            end loop;
         end return;
      end Create_Array;


   ------------------
   -- Create_Array --
   ------------------

   function Create_Array
     (Array_Type : Type_Index;
      Values     : Internal_Value_Array) return Internal_Value_Access is
   begin
      case Array_Type is
            when Type_Index_For_R_F_L_X_Node_Array =>
               declare
                  Result : constant Internal_Acc_R_F_L_X_Node_Array :=
                    Create_Array (Values);
               begin
                  return Internal_Value_Access (Result);
               end;

         when others =>
            --  Validation in public wrappers is supposed to prevent calling
            --  this function on non-array types.
            raise Program_Error;
      end case;
   end Create_Array;



   -------------------
   -- Create_Struct --
   -------------------

   function Create_Struct
     (Struct_Type : Type_Index;
      Values      : Internal_Value_Array) return Internal_Value_Access is
   begin
         pragma Unreferenced (Values);

      case Struct_Type is

         when others =>
            --  Validation in public wrappers is supposed to prevent calling
            --  this function on non-array types.
            return (raise Program_Error);
      end case;
   end Create_Struct;

   ----------------------
   -- Eval_Node_Member --
   ----------------------

   function Eval_Node_Member
     (Node      : Internal_Acc_Node;
      Member    : Struct_Member_Index;
      Arguments : Internal_Value_Array) return Internal_Value_Access
   is
      Int_Entity : constant Implementation.Internal_Entity :=
        +Langkit_Support.Internal.Conversions.Unwrap_Node (Node.Value);
      N          : constant R_F_L_X_Node :=
        Public_Converters.Wrap_Node.all (Int_Entity.Node, Int_Entity.Info);
      Kind       : constant R_F_L_X_Node_Kind_Type := N.Kind;
      Result     : Internal_Value_Access;
   begin
      

      case Member is
when Member_Index_For_Parent =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N.Parent);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Parents =>
declare
Arg_With_Self : Boolean renames Internal_Acc_Bool (Arguments (1)).Value;
begin
declare
R : Internal_Acc_R_F_L_X_Node_Array :=  new Internal_Rec_R_F_L_X_Node_Array;
begin
R.Value := new R_F_L_X_Node_Array'(N.Parents (Arg_With_Self));
Result := Internal_Value_Access (R);
end;
end;
when Member_Index_For_Children =>
declare
R : Internal_Acc_R_F_L_X_Node_Array :=  new Internal_Rec_R_F_L_X_Node_Array;
begin
R.Value := new R_F_L_X_Node_Array'(N.Children);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Token_Start =>
declare
R : Internal_Acc_Token :=  new Internal_Rec_Token;
begin
R.Value := To_Generic (N.Token_Start);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Token_End =>
declare
R : Internal_Acc_Token :=  new Internal_Rec_Token;
begin
R.Value := To_Generic (N.Token_End);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Child_Index =>
declare
R : Internal_Acc_Int :=  new Internal_Rec_Int;
begin
R.Value := N.Child_Index;
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Previous_Sibling =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N.Previous_Sibling);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Next_Sibling =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N.Next_Sibling);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Unit =>
declare
R : Internal_Acc_Analysis_Unit :=  new Internal_Rec_Analysis_Unit;
begin
Set_Unit (R, N.Unit);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Is_Ghost =>
declare
R : Internal_Acc_Bool :=  new Internal_Rec_Bool;
begin
R.Value := N.Is_Ghost;
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Full_Sloc_Image =>
declare
R : Internal_Acc_String :=  new Internal_Rec_String;
begin
R.Value := To_Unbounded_Text (N.Full_Sloc_Image);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
case Rflx_R_F_L_X_Node (Kind) is
when Rflx_I_D_Range =>
declare
N_Bare_I_D : constant Analysis.I_D := N.As_I_D;
begin
case Member is
when Member_Index_For_I_D_F_Package =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_I_D.F_Package);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_I_D_F_Name =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_I_D.F_Name);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Aspect_Range =>
declare
N_Bare_Aspect : constant Analysis.Aspect := N.As_Aspect;
begin
case Member is
when Member_Index_For_Aspect_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Aspect.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Aspect_F_Value =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Aspect.F_Value);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Aggregate_Associations_Range =>
declare
N_Bare_Message_Aggregate_Associations : constant Analysis.Message_Aggregate_Associations := N.As_Message_Aggregate_Associations;
begin
case Member is
when Member_Index_For_Message_Aggregate_Associations_F_Associations =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Aggregate_Associations.F_Associations);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Checksum_Val_Range =>
declare
N_Bare_Checksum_Val : constant Analysis.Checksum_Val := N.As_Checksum_Val;
begin
case Member is
when Member_Index_For_Checksum_Val_F_Data =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Checksum_Val.F_Data);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Checksum_Value_Range_Range =>
declare
N_Bare_Checksum_Value_Range : constant Analysis.Checksum_Value_Range := N.As_Checksum_Value_Range;
begin
case Member is
when Member_Index_For_Checksum_Value_Range_F_First =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Checksum_Value_Range.F_First);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Checksum_Value_Range_F_Last =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Checksum_Value_Range.F_Last);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Checksum_Assoc_Range =>
declare
N_Bare_Checksum_Assoc : constant Analysis.Checksum_Assoc := N.As_Checksum_Assoc;
begin
case Member is
when Member_Index_For_Checksum_Assoc_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Checksum_Assoc.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Checksum_Assoc_F_Covered_Fields =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Checksum_Assoc.F_Covered_Fields);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Refinement_Decl_Range =>
declare
N_Bare_Refinement_Decl : constant Analysis.Refinement_Decl := N.As_Refinement_Decl;
begin
case Member is
when Member_Index_For_Refinement_Decl_F_Pdu =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Refinement_Decl.F_Pdu);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Refinement_Decl_F_Field =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Refinement_Decl.F_Field);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Refinement_Decl_F_Sdu =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Refinement_Decl.F_Sdu);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Refinement_Decl_F_Condition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Refinement_Decl.F_Condition);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Session_Decl_Range =>
declare
N_Bare_Session_Decl : constant Analysis.Session_Decl := N.As_Session_Decl;
begin
case Member is
when Member_Index_For_Session_Decl_F_Parameters =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Session_Decl.F_Parameters);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Session_Decl_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Session_Decl.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Session_Decl_F_Declarations =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Session_Decl.F_Declarations);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Session_Decl_F_States =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Session_Decl.F_States);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Session_Decl_F_End_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Session_Decl.F_End_Identifier);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Type_Decl_Range =>
declare
N_Bare_Type_Decl : constant Analysis.Type_Decl := N.As_Type_Decl;
begin
case Member is
when Member_Index_For_Type_Decl_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Type_Decl.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Type_Decl_F_Parameters =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Type_Decl.F_Parameters);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Type_Decl_F_Definition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Type_Decl.F_Definition);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Description_Range =>
declare
N_Bare_Description : constant Analysis.Description := N.As_Description;
begin
case Member is
when Member_Index_For_Description_F_Content =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Description.F_Content);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Element_Value_Assoc_Range =>
declare
N_Bare_Element_Value_Assoc : constant Analysis.Element_Value_Assoc := N.As_Element_Value_Assoc;
begin
case Member is
when Member_Index_For_Element_Value_Assoc_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Element_Value_Assoc.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Element_Value_Assoc_F_Literal =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Element_Value_Assoc.F_Literal);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Attribute_Range =>
declare
N_Bare_Attribute : constant Analysis.Attribute := N.As_Attribute;
begin
case Member is
when Member_Index_For_Attribute_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Attribute.F_Expression);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Attribute_F_Kind =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Attribute.F_Kind);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Bin_Op_Range =>
declare
N_Bare_Bin_Op : constant Analysis.Bin_Op := N.As_Bin_Op;
begin
case Member is
when Member_Index_For_Bin_Op_F_Left =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Bin_Op.F_Left);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Bin_Op_F_Op =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Bin_Op.F_Op);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Bin_Op_F_Right =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Bin_Op.F_Right);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Binding_Range =>
declare
N_Bare_Binding : constant Analysis.Binding := N.As_Binding;
begin
case Member is
when Member_Index_For_Binding_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Binding.F_Expression);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Binding_F_Bindings =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Binding.F_Bindings);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Call_Range =>
declare
N_Bare_Call : constant Analysis.Call := N.As_Call;
begin
case Member is
when Member_Index_For_Call_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Call.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Call_F_Arguments =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Call.F_Arguments);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Case_Expression_Range =>
declare
N_Bare_Case_Expression : constant Analysis.Case_Expression := N.As_Case_Expression;
begin
case Member is
when Member_Index_For_Case_Expression_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Case_Expression.F_Expression);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Case_Expression_F_Choices =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Case_Expression.F_Choices);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Choice_Range =>
declare
N_Bare_Choice : constant Analysis.Choice := N.As_Choice;
begin
case Member is
when Member_Index_For_Choice_F_Selectors =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Choice.F_Selectors);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Choice_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Choice.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Comprehension_Range =>
declare
N_Bare_Comprehension : constant Analysis.Comprehension := N.As_Comprehension;
begin
case Member is
when Member_Index_For_Comprehension_F_Iterator =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Comprehension.F_Iterator);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Comprehension_F_Sequence =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Comprehension.F_Sequence);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Comprehension_F_Condition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Comprehension.F_Condition);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Comprehension_F_Selector =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Comprehension.F_Selector);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Context_Item_Range =>
declare
N_Bare_Context_Item : constant Analysis.Context_Item := N.As_Context_Item;
begin
case Member is
when Member_Index_For_Context_Item_F_Item =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Context_Item.F_Item);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Conversion_Range =>
declare
N_Bare_Conversion : constant Analysis.Conversion := N.As_Conversion;
begin
case Member is
when Member_Index_For_Conversion_F_Target_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Conversion.F_Target_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Conversion_F_Argument =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Conversion.F_Argument);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Aggregate_Range =>
declare
N_Bare_Message_Aggregate : constant Analysis.Message_Aggregate := N.As_Message_Aggregate;
begin
case Member is
when Member_Index_For_Message_Aggregate_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Aggregate.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Aggregate_F_Values =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Aggregate.F_Values);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Negation_Range =>
declare
N_Bare_Negation : constant Analysis.Negation := N.As_Negation;
begin
case Member is
when Member_Index_For_Negation_F_Data =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Negation.F_Data);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Paren_Expression_Range =>
declare
N_Bare_Paren_Expression : constant Analysis.Paren_Expression := N.As_Paren_Expression;
begin
case Member is
when Member_Index_For_Paren_Expression_F_Data =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Paren_Expression.F_Data);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Quantified_Expression_Range =>
declare
N_Bare_Quantified_Expression : constant Analysis.Quantified_Expression := N.As_Quantified_Expression;
begin
case Member is
when Member_Index_For_Quantified_Expression_F_Operation =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Quantified_Expression.F_Operation);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Quantified_Expression_F_Parameter_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Quantified_Expression.F_Parameter_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Quantified_Expression_F_Iterable =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Quantified_Expression.F_Iterable);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Quantified_Expression_F_Predicate =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Quantified_Expression.F_Predicate);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Select_Node_Range =>
declare
N_Bare_Select_Node : constant Analysis.Select_Node := N.As_Select_Node;
begin
case Member is
when Member_Index_For_Select_Node_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Select_Node.F_Expression);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Select_Node_F_Selector =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Select_Node.F_Selector);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Concatenation_Range =>
declare
N_Bare_Concatenation : constant Analysis.Concatenation := N.As_Concatenation;
begin
case Member is
when Member_Index_For_Concatenation_F_Left =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Concatenation.F_Left);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Concatenation_F_Right =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Concatenation.F_Right);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Sequence_Aggregate_Range =>
declare
N_Bare_Sequence_Aggregate : constant Analysis.Sequence_Aggregate := N.As_Sequence_Aggregate;
begin
case Member is
when Member_Index_For_Sequence_Aggregate_F_Values =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Sequence_Aggregate.F_Values);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Variable_Range =>
declare
N_Bare_Variable : constant Analysis.Variable := N.As_Variable;
begin
case Member is
when Member_Index_For_Variable_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Variable.F_Identifier);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Formal_Channel_Decl_Range =>
declare
N_Bare_Formal_Channel_Decl : constant Analysis.Formal_Channel_Decl := N.As_Formal_Channel_Decl;
begin
case Member is
when Member_Index_For_Formal_Channel_Decl_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Formal_Channel_Decl.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Formal_Channel_Decl_F_Parameters =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Formal_Channel_Decl.F_Parameters);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Formal_Function_Decl_Range =>
declare
N_Bare_Formal_Function_Decl : constant Analysis.Formal_Function_Decl := N.As_Formal_Function_Decl;
begin
case Member is
when Member_Index_For_Formal_Function_Decl_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Formal_Function_Decl.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Formal_Function_Decl_F_Parameters =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Formal_Function_Decl.F_Parameters);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Formal_Function_Decl_F_Return_Type_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Formal_Function_Decl.F_Return_Type_Identifier);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Renaming_Decl_Range =>
declare
N_Bare_Renaming_Decl : constant Analysis.Renaming_Decl := N.As_Renaming_Decl;
begin
case Member is
when Member_Index_For_Renaming_Decl_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Renaming_Decl.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Renaming_Decl_F_Type_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Renaming_Decl.F_Type_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Renaming_Decl_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Renaming_Decl.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Variable_Decl_Range =>
declare
N_Bare_Variable_Decl : constant Analysis.Variable_Decl := N.As_Variable_Decl;
begin
case Member is
when Member_Index_For_Variable_Decl_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Variable_Decl.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Variable_Decl_F_Type_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Variable_Decl.F_Type_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Variable_Decl_F_Initializer =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Variable_Decl.F_Initializer);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Aggregate_Association_Range =>
declare
N_Bare_Message_Aggregate_Association : constant Analysis.Message_Aggregate_Association := N.As_Message_Aggregate_Association;
begin
case Member is
when Member_Index_For_Message_Aggregate_Association_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Aggregate_Association.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Aggregate_Association_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Aggregate_Association.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Byte_Order_Aspect_Range =>
declare
N_Bare_Byte_Order_Aspect : constant Analysis.Byte_Order_Aspect := N.As_Byte_Order_Aspect;
begin
case Member is
when Member_Index_For_Byte_Order_Aspect_F_Byte_Order =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Byte_Order_Aspect.F_Byte_Order);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Checksum_Aspect_Range =>
declare
N_Bare_Checksum_Aspect : constant Analysis.Checksum_Aspect := N.As_Checksum_Aspect;
begin
case Member is
when Member_Index_For_Checksum_Aspect_F_Associations =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Checksum_Aspect.F_Associations);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Field_Range =>
declare
N_Bare_Message_Field : constant Analysis.Message_Field := N.As_Message_Field;
begin
case Member is
when Member_Index_For_Message_Field_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_F_Type_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field.F_Type_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_F_Type_Arguments =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field.F_Type_Arguments);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_F_Aspects =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field.F_Aspects);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_F_Condition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field.F_Condition);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_F_Thens =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field.F_Thens);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Fields_Range =>
declare
N_Bare_Message_Fields : constant Analysis.Message_Fields := N.As_Message_Fields;
begin
case Member is
when Member_Index_For_Message_Fields_F_Initial_Field =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Fields.F_Initial_Field);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Fields_F_Fields =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Fields.F_Fields);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Null_Message_Field_Range =>
declare
N_Bare_Null_Message_Field : constant Analysis.Null_Message_Field := N.As_Null_Message_Field;
begin
case Member is
when Member_Index_For_Null_Message_Field_F_Thens =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Null_Message_Field.F_Thens);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Package_Node_Range =>
declare
N_Bare_Package_Node : constant Analysis.Package_Node := N.As_Package_Node;
begin
case Member is
when Member_Index_For_Package_Node_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Package_Node.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Package_Node_F_Declarations =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Package_Node.F_Declarations);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Package_Node_F_End_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Package_Node.F_End_Identifier);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Parameter_Range =>
declare
N_Bare_Parameter : constant Analysis.Parameter := N.As_Parameter;
begin
case Member is
when Member_Index_For_Parameter_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Parameter.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Parameter_F_Type_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Parameter.F_Type_Identifier);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Parameters_Range =>
declare
N_Bare_Parameters : constant Analysis.Parameters := N.As_Parameters;
begin
case Member is
when Member_Index_For_Parameters_F_Parameters =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Parameters.F_Parameters);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Specification_Range =>
declare
N_Bare_Specification : constant Analysis.Specification := N.As_Specification;
begin
case Member is
when Member_Index_For_Specification_F_Context_Clause =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Specification.F_Context_Clause);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Specification_F_Package_Declaration =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Specification.F_Package_Declaration);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_State_Range =>
declare
N_Bare_State : constant Analysis.State := N.As_State;
begin
case Member is
when Member_Index_For_State_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_F_Description =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State.F_Description);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_F_Body =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State.F_Body);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_State_Body_Range =>
declare
N_Bare_State_Body : constant Analysis.State_Body := N.As_State_Body;
begin
case Member is
when Member_Index_For_State_Body_F_Declarations =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State_Body.F_Declarations);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_Body_F_Actions =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State_Body.F_Actions);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_Body_F_Conditional_Transitions =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State_Body.F_Conditional_Transitions);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_Body_F_Final_Transition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State_Body.F_Final_Transition);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_Body_F_Exception_Transition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State_Body.F_Exception_Transition);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_State_Body_F_End_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_State_Body.F_End_Identifier);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Assignment_Range =>
declare
N_Bare_Assignment : constant Analysis.Assignment := N.As_Assignment;
begin
case Member is
when Member_Index_For_Assignment_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Assignment.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Assignment_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Assignment.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Attribute_Statement_Range =>
declare
N_Bare_Attribute_Statement : constant Analysis.Attribute_Statement := N.As_Attribute_Statement;
begin
case Member is
when Member_Index_For_Attribute_Statement_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Attribute_Statement.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Attribute_Statement_F_Attr =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Attribute_Statement.F_Attr);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Attribute_Statement_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Attribute_Statement.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Field_Assignment_Range =>
declare
N_Bare_Message_Field_Assignment : constant Analysis.Message_Field_Assignment := N.As_Message_Field_Assignment;
begin
case Member is
when Member_Index_For_Message_Field_Assignment_F_Message =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field_Assignment.F_Message);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_Assignment_F_Field =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field_Assignment.F_Field);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Field_Assignment_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Field_Assignment.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Reset_Range =>
declare
N_Bare_Reset : constant Analysis.Reset := N.As_Reset;
begin
case Member is
when Member_Index_For_Reset_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Reset.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Reset_F_Associations =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Reset.F_Associations);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Term_Assoc_Range =>
declare
N_Bare_Term_Assoc : constant Analysis.Term_Assoc := N.As_Term_Assoc;
begin
case Member is
when Member_Index_For_Term_Assoc_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Term_Assoc.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Term_Assoc_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Term_Assoc.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Then_Node_Range =>
declare
N_Bare_Then_Node : constant Analysis.Then_Node := N.As_Then_Node;
begin
case Member is
when Member_Index_For_Then_Node_F_Target =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Then_Node.F_Target);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Then_Node_F_Aspects =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Then_Node.F_Aspects);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Then_Node_F_Condition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Then_Node.F_Condition);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Transition_Range =>
declare
N_Bare_Transition : constant Analysis.Transition := N.As_Transition;
begin
case Member is
when Member_Index_For_Transition_F_Target =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Transition.F_Target);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Transition_F_Description =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Transition.F_Description);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
case Rflx_Transition_Range (Kind) is
when Rflx_Conditional_Transition_Range =>
declare
N_Bare_Conditional_Transition : constant Analysis.Conditional_Transition := N_Bare_Transition.As_Conditional_Transition;
begin
case Member is
when Member_Index_For_Conditional_Transition_F_Condition =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Conditional_Transition.F_Condition);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when others => null;
end case;
end;
when Rflx_Type_Argument_Range =>
declare
N_Bare_Type_Argument : constant Analysis.Type_Argument := N.As_Type_Argument;
begin
case Member is
when Member_Index_For_Type_Argument_F_Identifier =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Type_Argument.F_Identifier);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Type_Argument_F_Expression =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Type_Argument.F_Expression);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Message_Type_Def_Range =>
declare
N_Bare_Message_Type_Def : constant Analysis.Message_Type_Def := N.As_Message_Type_Def;
begin
case Member is
when Member_Index_For_Message_Type_Def_F_Message_Fields =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Type_Def.F_Message_Fields);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Message_Type_Def_F_Aspects =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Message_Type_Def.F_Aspects);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Named_Enumeration_Def_Range =>
declare
N_Bare_Named_Enumeration_Def : constant Analysis.Named_Enumeration_Def := N.As_Named_Enumeration_Def;
begin
case Member is
when Member_Index_For_Named_Enumeration_Def_F_Elements =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Named_Enumeration_Def.F_Elements);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Positional_Enumeration_Def_Range =>
declare
N_Bare_Positional_Enumeration_Def : constant Analysis.Positional_Enumeration_Def := N.As_Positional_Enumeration_Def;
begin
case Member is
when Member_Index_For_Positional_Enumeration_Def_F_Elements =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Positional_Enumeration_Def.F_Elements);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Enumeration_Type_Def_Range =>
declare
N_Bare_Enumeration_Type_Def : constant Analysis.Enumeration_Type_Def := N.As_Enumeration_Type_Def;
begin
case Member is
when Member_Index_For_Enumeration_Type_Def_F_Elements =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Enumeration_Type_Def.F_Elements);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Enumeration_Type_Def_F_Aspects =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Enumeration_Type_Def.F_Aspects);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Modular_Type_Def_Range =>
declare
N_Bare_Modular_Type_Def : constant Analysis.Modular_Type_Def := N.As_Modular_Type_Def;
begin
case Member is
when Member_Index_For_Modular_Type_Def_F_Mod =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Modular_Type_Def.F_Mod);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Range_Type_Def_Range =>
declare
N_Bare_Range_Type_Def : constant Analysis.Range_Type_Def := N.As_Range_Type_Def;
begin
case Member is
when Member_Index_For_Range_Type_Def_F_First =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Range_Type_Def.F_First);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Range_Type_Def_F_Last =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Range_Type_Def.F_Last);
Result := Internal_Value_Access (R);
end;
when Member_Index_For_Range_Type_Def_F_Size =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Range_Type_Def.F_Size);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Sequence_Type_Def_Range =>
declare
N_Bare_Sequence_Type_Def : constant Analysis.Sequence_Type_Def := N.As_Sequence_Type_Def;
begin
case Member is
when Member_Index_For_Sequence_Type_Def_F_Element_Type =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Sequence_Type_Def.F_Element_Type);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when Rflx_Type_Derivation_Def_Range =>
declare
N_Bare_Type_Derivation_Def : constant Analysis.Type_Derivation_Def := N.As_Type_Derivation_Def;
begin
case Member is
when Member_Index_For_Type_Derivation_Def_F_Base =>
declare
R : Internal_Acc_Node :=  new Internal_Rec_Node;
begin
Set_Node (R, N_Bare_Type_Derivation_Def.F_Base);
Result := Internal_Value_Access (R);
end;
when others => null;
end case;
end;
when others => null;
end case;
      pragma Assert (Result /= null);
      return Result;
   end Eval_Node_Member;

   --------------
   -- Set_Unit --
   --------------

   procedure Set_Unit
     (Intr_Value   : Internal_Acc_Analysis_Unit;
      Actual_Value : Analysis_Unit)
   is
      U : constant Internal_Unit :=
        +Public_Converters.Unwrap_Unit (Actual_Value);
   begin
      Intr_Value.Value :=
        Langkit_Support.Internal.Conversions.Wrap_Unit (Self_Id, U);
   end Set_Unit;

   --------------
   -- Get_Unit --
   --------------

   function Get_Unit
     (Intr_Value : Internal_Rec_Analysis_Unit)
      return Analysis_Unit
   is
      U : constant Implementation.Internal_Unit :=
        +Langkit_Support.Internal.Conversions.Unwrap_Unit (Intr_Value.Value);
   begin
      return Public_Converters.Wrap_Unit (U);
   end Get_Unit;

   -----------------
   -- Set_Big_Int --
   -----------------

   procedure Set_Big_Int
     (Intr_Value   : Internal_Acc_Big_Int;
      Actual_Value : Big_Integer) is
   begin
      Intr_Value.Value.Set (Actual_Value);
   end Set_Big_Int;

   -----------------
   -- Get_Big_Int --
   -----------------

   procedure Get_Big_Int
     (Intr_Value   : Internal_Rec_Big_Int;
      Actual_Value : out Big_Integer)
   is
   begin
      Actual_Value.Set (Intr_Value.Value);
   end Get_Big_Int;

   --------------
   -- Set_Node --
   --------------

   procedure Set_Node
     (Intr_Value   : Internal_Acc_Node;
      Actual_Value : R_F_L_X_Node'Class)
   is
      E : constant Internal_Entity := +Unwrap_Entity (Actual_Value);
   begin
      Intr_Value.Value :=
        Langkit_Support.Internal.Conversions.Wrap_Node (Self_Id, E);
   end Set_Node;

   --------------
   -- Get_Node --
   --------------

   function Get_Node
     (Intr_Value : Internal_Rec_Node)
      return R_F_L_X_Node
   is
      E : constant Implementation.Internal_Entity :=
        +Langkit_Support.Internal.Conversions.Unwrap_Node (Intr_Value.Value);
   begin
      return Public_Converters.Wrap_Node (E.Node, E.Info);
   end Get_Node;

end Librflxlang.Generic_Introspection;
