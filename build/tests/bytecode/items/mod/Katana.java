package mod; import net.minecraft.world.item.*;
public class Katana extends SwordItem { final double reach; public Katana(Tier t, int d, float s, double reach, Properties p) { super(t, d, s, p); this.reach = reach; } }
