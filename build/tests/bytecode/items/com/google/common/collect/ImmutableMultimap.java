package com.google.common.collect;
public class ImmutableMultimap<K, V> implements Multimap<K, V> { public static <K, V> Builder<K, V> builder() { return null; }
  public static class Builder<K, V> { public Builder<K, V> put(K k, V v) { return this; } public ImmutableMultimap<K, V> build() { return null; } } }
