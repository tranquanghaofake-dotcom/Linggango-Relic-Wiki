package fx;
import net.minecraft.world.effect.*; import net.minecraft.world.entity.LivingEntity; import net.minecraft.world.item.ItemStack;
public class Blade2 {
  int dur = 80;
  public boolean hurtEnemy(ItemStack s, LivingEntity target, LivingEntity self) {
    if (self.m_217043_().m_188501_() < 0.25f) target.m_7292_(new MobEffectInstance(MobEffects.f_19614_, 100, 1));
    else target.m_7292_(new MobEffectInstance(MobEffects.f_19615_, 40, 0));
    if (0.1f > self.m_217043_().nextFloat()) self.m_7292_(new MobEffectInstance(MobEffects.f_19597_, 20));
    int secs = 5;
    target.m_7292_(new MobEffectInstance(MobEffects.f_19615_, secs * 20, 2));
    MobEffect e = MobEffects.f_19614_;
    target.m_7292_(new MobEffectInstance(e, this.dur, 0));
    if (self.m_217043_().nextFloat() < 0.5f) helper(target);
    return true;
  }
  void helper(LivingEntity t) { t.m_7292_(new MobEffectInstance(MobEffects.f_19597_, 60, 1)); }
}
