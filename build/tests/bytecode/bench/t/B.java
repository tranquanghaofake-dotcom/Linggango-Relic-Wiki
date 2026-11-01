package t;
public class B { public static int bench() { int s = 0; float f = 0.5f; long l = 1L; for (int i = 0; i < 200000; i++) { s += i % 7; f = f * 1.0001f + 0.1f; l += i; } return s + (int) f + (int) (l & 7); } }
