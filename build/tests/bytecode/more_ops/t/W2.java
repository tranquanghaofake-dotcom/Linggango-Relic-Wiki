package t;
import net.minecraft.world.item.ArmorItem;
public class W2 {
  static double BASE = 3.5;
  long cnt = 5L; double dmg = 2.0;
  public static double sd() { return BASE * 2; }
  public static double fld() { W2 w = new W2(); w.dmg += 1.5; return w.dmg; }
  public static long fld2() { W2 w = new W2(); long x = w.cnt++; return x * 100 + w.cnt; }
  public static double expr() { double[] a = {1.0, 2.0}; double y = a[1] = 5.5; return y + a[1]; }
  public static long lmix(long a, int b, double c) { return a * b + (long) c; }
  static double helper(double x, long y) { return x * y; }
  public static double call() { return lmix(3L, 4, 2.9) + helper(1.5, 2L); }
  public static int cmpl() { long a = 5L, b = 7L; return a < b ? 1 : 0; }
  public static String cat2(int n) { return "item_" + n + "_x"; }
  public static String cat3(int n) { return "a\u0001b" + n; }
  public static double lam() { java.util.function.DoubleSupplier f = () -> BASE + 1; return f.getAsDouble(); }
  public static int usw(int v) { switch (v) { case 1: return 10; case 5: return 50; default: return -1; } }
  public static int tsw(ArmorItem.Type t) { switch (t) { case CHESTPLATE: return 8; case LEGGINGS: return 6; default: return 3; } }
  public static int tsw2() { return tsw(ArmorItem.Type.LEGGINGS); }
  public static double dneg() { double d = 2.5; float f = 1.25f; return -d + -f; }
  public static long lshr() { long a = -16L; return (a >> 2) + (a >>> 60); }
  public static int fdiv() { float a = 7f; float b = 2f; return (int) (a / b * 10f); }
  public static long ldiv() { long a = -7000000000000000001L; long b = 3L; return a / b + a % b; }
  public static double drem() { double a = -7.5; double b = 2.0; return a % b; }
  public static int i2c() { int v = -1; return (char) v; }
  public static int sh() { short s = (short) 70000; byte b = (byte) -129; return s + b; }
  public static int boom() { return W3.X; }
}
class W3 { static int X = 4; }
