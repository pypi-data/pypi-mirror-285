
with Langkit_Support.Generic_API; use Langkit_Support.Generic_API;
with Langkit_Support.Generic_API.Analysis;
use Langkit_Support.Generic_API.Analysis;

with Librflxlang.Analysis; use Librflxlang.Analysis;
with Librflxlang.Common;   use Librflxlang.Common;

package Librflxlang.Generic_API is

   Rflx_Lang_Id : constant Language_Id
     with Import, External_Name => "Librflxlang__language_id";
   --  Unique identifier for Librflxlang

   Self_Id : Language_Id renames Rflx_Lang_Id;
   --  Shortcut for convenience in code generation

   function To_Generic_Context (Context : Analysis_Context) return Lk_Context;
   --  Convert the given ``Context`` into a value suitable to use in the
   --  Langkit generic API.

   function From_Generic_Context
     (Context : Lk_Context) return Analysis_Context;
   --  Convert the ``Context`` value from the Langkit generic API into the
   --  Librflxlang-specific context type. Raise a
   --  ``Langkit_Support.Errors.Precondition_Failure`` if ``Context`` does not
   --  belong to Librflxlang.

   function To_Generic_Unit (Unit : Analysis_Unit) return Lk_Unit;
   --  Convert the given ``Unit`` into a value suitable to use in the Langkit
   --  generic API.

   function From_Generic_Unit (Unit : Lk_Unit) return Analysis_Unit;
   --  Convert the ``Unit`` value from the Langkit generic API into the
   --  Librflxlang-specific unit type. Raise a
   --  ``Langkit_Support.Errors.Precondition_Failure`` if ``Unit`` does not
   --  belong to Librflxlang.

   function To_Generic_Grammar_Rule
     (Rule : Grammar_Rule) return Langkit_Support.Generic_API.Grammar_Rule_Ref;
   --  Convert the given ``rule`` into a value suitable to use in the Langkit
   --  generic API.

   function From_Generic_Grammar_Rule
     (Rule : Langkit_Support.Generic_API.Grammar_Rule_Ref) return Grammar_Rule;
   --  Convert the ``Rule`` value from the Langkit generic API into the
   --  Librflxlang-specific unit type. Raise a
   --  ``Langkit_Support.Errors.Precondition_Failure`` if ``Rule`` does not
   --  belong to Librflxlang or if it is ``No_Grammar_Rule_Ref``.

   function To_Generic_Node
     (Node : R_F_L_X_Node'Class) return Lk_Node;
   --  Convert the given ``Node`` into a value suitable to use in the Langkit
   --  generic API.

   function From_Generic_Node (Node : Lk_Node) return R_F_L_X_Node;
   --  Convert the ``Node`` value from the Langkit generic API into the
   --  Librflxlang-specific unit type. Raise a
   --  ``Langkit_Support.Errors.Precondition_Failure`` if ``Node`` does not
   --  belong to Librflxlang.

end Librflxlang.Generic_API;
