package net.minecraftforge.registries; import java.util.function.Supplier;
public class DeferredRegister<T> { public static <T> DeferredRegister<T> create(Object r, String ns) { return null; } public <I extends T> Object register(String n, Supplier<I> s) { return null; } }
