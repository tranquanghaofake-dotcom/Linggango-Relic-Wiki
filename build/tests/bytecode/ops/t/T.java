package t;
public class T {
    public static int dec() { int x = 10; x--; return x; }
    public static int sub3() { int x = 10; x -= 3; return x; }
    public static int widesub() { int x = 0; x -= 200; return x; }
    public static int f2i() { float a = 0.7f; int b = 10; return (int)(a * b); }
    public static int f2i2() { float a = 0.3f; float b = 0.6f; return (int)((a + b) * 10f); }
    public static int rem() { int a = -7; int b = 3; return a % b; }
    public static int arr() { int[] p = {3, 8, 6, 3}; p[1] += 2; return p[1]; }
    public static int arrinc() { int[] p = {3, 8, 6, 3}; p[2]++; return p[2]; }
    public static double dbl(long a, double b, int c) { double d = b * 2; long e = a + c; return d + e; }
    public static int sw(String s) { switch (s) { case "a": return 1; case "bb": return 2; default: return 0; } }
    public static int tsw(int v) { switch (v) { case 1: return 10; case 2: return 20; case 3: return 30; default: return -1; } }
    public static String cat(float f, int i) { return "x" + f + "_" + i; }
    public static int i2b() { int v = 200; return (byte) v; }
    public static float fl() { float a = 0.1f; float b = a * 3; return b; }
    public static int loopsum() { int s = 0; for (int i = 0; i < 4; i++) s += i; return s; }
    public static int down() { int s = 0; for (int i = 3; i >= 0; i--) s += i; return s; }
    public static long lshift() { long a = 1; int n = 40; return a << n; }
    public static int idiv() { int a = -7; int b = 2; return a / b; }
    static int[] T2 = new int[]{1, 2, 3};
    public static int cmpd() { double a = 0.5; double b = 0.25; return a > b ? 1 : 0; }
    public static int deflt() { return new K().v(); }
    public static int en() { return M.B.d + M.B.ordinal() * 100; }
    public static int enumsw(M m) { switch (m) { case A: return 1; case B: return 2; default: return 9; } }
    public static int enumsw2() { return enumsw(M.B); }
    public static double dsum() { double[] w = {1.5, 2.5}; double t = 0; for (double x : w) t += x; return t; }
}
interface I { default int v() { return 5; } }
class K implements I {}
enum M { A(3), B(5); final int d; M(int d) { this.d = d; } }
