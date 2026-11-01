package fx;
import net.minecraft.world.effect.*; import net.minecraft.world.entity.LivingEntity; import net.minecraft.world.item.ItemStack;
public class Blade {
  int dur = 80; int lvl = 2;
  public boolean hurtEnemy(ItemStack s, LivingEntity target, LivingEntity self) {
    if (self.m_217043_().nextFloat() > 0.8f) target.m_7292_(new MobEffectInstance(MobEffects.f_19614_, 100, 1));
    target.m_7292_(new MobEffectInstance(MobEffects.f_19615_, 60, 0));
    target.m_7292_(new MobEffectInstance(MobEffects.f_19597_, this.dur, 2));
    target.m_7292_(new MobEffectInstance(MobEffects.f_19597_, 100 + lvl * 20, 1));
    return true;
  }
}
