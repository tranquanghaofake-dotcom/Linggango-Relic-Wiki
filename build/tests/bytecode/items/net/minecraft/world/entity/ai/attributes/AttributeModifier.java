package net.minecraft.world.entity.ai.attributes; import java.util.UUID;
public class AttributeModifier { public enum Operation { ADDITION, MULTIPLY_BASE, MULTIPLY_TOTAL } public AttributeModifier(UUID u, String n, double a, Operation o) {} }
