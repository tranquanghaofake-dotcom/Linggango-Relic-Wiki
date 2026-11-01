package t;
public class U {
  public static int sat() { float a = Float.MAX_VALUE; a = a * 4f; return (int) a; }
  public static int shl() { int a = 1; int n = 31; return a << n; }
  public static int ovf() { int a = 2147483647; int b = 1; return a + b; }
  public static int m1() { int a = 0; int b = 5; return sat() + b; }
}
