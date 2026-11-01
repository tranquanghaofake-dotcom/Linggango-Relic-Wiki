package mod;
import net.minecraft.world.entity.EquipmentSlot;
public class A {
  public static int prot(EquipmentSlot s) { switch (s) { case HEAD: return 3; case CHEST: return 8; default: return 0; } }
  public static int protIf(EquipmentSlot s) { return s == EquipmentSlot.CHEST ? 8 : 0; }
  static float scaled(String id, float base) { return base * 2f; }
  public static float dmg() { return scaled("katana", 7f); }
}
