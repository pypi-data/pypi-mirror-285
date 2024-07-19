
with Ada.Unchecked_Conversion;

with Librflxlang.Implementation;    use Librflxlang.Implementation;
with Librflxlang.Public_Converters; use Librflxlang.Public_Converters;

package body Librflxlang.C is

   function "+" is new Ada.Unchecked_Conversion
     (Internal_Context, System.Address);
   function "+" is new Ada.Unchecked_Conversion
     (System.Address, Internal_Context);

   function "+" is new Ada.Unchecked_Conversion
     (Internal_Unit, System.Address);
   function "+" is new Ada.Unchecked_Conversion
     (System.Address, Internal_Unit);

   ---------------
   -- C_Context --
   ---------------

   function C_Context (Context : Analysis_Context) return System.Address is
   begin
      return +Unwrap_Context (Context);
   end C_Context;

   -----------------
   -- Ada_Context --
   -----------------

   function Ada_Context (Context : System.Address) return Analysis_Context is
   begin
      return Wrap_Context (+Context);
   end Ada_Context;

   ------------
   -- C_Unit --
   ------------

   function C_Unit (Unit : Analysis_Unit) return System.Address is
   begin
      return +Unwrap_Unit (Unit);
   end C_Unit;

   --------------
   -- Ada_Unit --
   --------------

   function Ada_Unit (Unit : System.Address) return Analysis_Unit is
   begin
      return Wrap_Unit (+Unit);
   end Ada_Unit;

end Librflxlang.C;
