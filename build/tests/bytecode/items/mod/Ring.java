package mod;
import net.minecraft.world.item.Item; import net.minecraft.world.entity.EquipmentSlot; import net.minecraft.world.entity.ai.attributes.*;
import com.google.common.collect.*; import java.util.UUID;
public class Ring extends Item { final double bonus; final long seed = 12345678901L;
  public Ring(double bonus, Properties p) { super(p); this.bonus = bonus; }
  public Multimap<Attribute, AttributeModifier> m_7167_(EquipmentSlot slot) {
    if (slot == EquipmentSlot.MAINHAND) { ImmutableMultimap.Builder<Attribute, AttributeModifier> b = ImmutableMultimap.builder();
      b.put(Attributes.f_22281_, new AttributeModifier(UUID.randomUUID(), "x", this.bonus * 1.5D, AttributeModifier.Operation.ADDITION));
      b.put(Attributes.f_22283_, new AttributeModifier(UUID.randomUUID(), "y", -0.1D, AttributeModifier.Operation.MULTIPLY_BASE));
      return b.build(); }
    return super.m_7167_(slot); } }
