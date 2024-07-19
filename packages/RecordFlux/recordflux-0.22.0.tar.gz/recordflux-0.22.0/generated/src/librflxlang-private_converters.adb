
with Langkit_Support.Internal.Analysis; use Langkit_Support.Internal.Analysis;
with Langkit_Support.Internal.Conversions;
use Langkit_Support.Internal.Conversions;

with Librflxlang.Generic_API; use Librflxlang.Generic_API;

package body Librflxlang.Private_Converters is

   function "+"
     (Entity : Langkit_Support.Internal.Analysis.Internal_Entity)
      return Implementation.Internal_Entity
     with Import,
          External_Name => "Librflxlang__from_generic_internal_entity";
   function "+"
     (Entity : Implementation.Internal_Entity)
      return Langkit_Support.Internal.Analysis.Internal_Entity
     with Import,
          External_Name => "Librflxlang__to_generic_internal_entity";
   --  See the corresponding exports in $.Generic_Impl

   -----------------------
   -- From_Generic_Node --
   -----------------------

   function From_Generic_Node
     (Node : Lk_Node) return Implementation.Internal_Entity is
   begin
      return +Unwrap_Node (Node);
   end From_Generic_Node;

   ---------------------
   -- To_Generic_Node --
   ---------------------

   function To_Generic_Node
     (Entity : Implementation.Internal_Entity) return Lk_Node is
   begin
      return Wrap_Node (Self_Id, +Entity);
   end To_Generic_Node;

end Librflxlang.Private_Converters;
