package c;
interface Named { default String name() { return "named"; } }
interface Tagged extends Named { }
class Base implements Tagged { }
public class Leaf extends Base implements Runnable {
  static float F = 0.1f;
  static long L = 1L << 40;
  public void run() { }
  public static Class<?> k() { return Leaf.class; }
  public static java.util.function.Supplier<Leaf> mk() { return Leaf::new; }
  public static long slots(int a, long b, String[] c, double d) { return a + b + c.length + (long) d; }
}
