package mod; import net.minecraft.world.item.*; import net.minecraftforge.registries.DeferredRegister;
public class ModItems { public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(null, "mod");
  public static final Object KATANA = ITEMS.register("katana", () -> new Katana(Tiers.DIAMOND, 3, -2.4F, 1.5D, new Item.Properties()));
  public static final Object RING = ITEMS.register("ring", () -> new Ring(5.0D, new Item.Properties())); }
