Port the following TypeScript LRU cache with TTL, weak references, and async eviction to idiomatic Rust using Tokio. The Rust code must:
1. Compile with `cargo build` (no errors)
2. Pass all ported tests
3. Use no `unsafe` blocks
4. Avoid `.clone()` on the hot path (get/put)

```typescript
interface CacheEntry<V> {
  value: V;
  expiresAt: number;
  size: number;
  lastAccessed: number;
  accessCount: number;
}

interface CacheConfig {
  maxEntries: number;
  defaultTtlMs: number;
  maxMemoryBytes: number;
  evictionCheckIntervalMs: number;
  onEvict?: (key: string, reason: 'expired' | 'lru' | 'memory') => void;
}

class LRUCache<V> {
  private entries: Map<string, CacheEntry<V>>;
  private accessOrder: string[];
  private config: CacheConfig;
  private currentMemory: number;
  private evictionTimer: ReturnType<typeof setInterval> | null;
  private weakRefs: Map<string, WeakRef<object>>;
  private stats: { hits: number; misses: number; evictions: number; expirations: number };

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      maxEntries: config.maxEntries ?? 1000,
      defaultTtlMs: config.defaultTtlMs ?? 60000,
      maxMemoryBytes: config.maxMemoryBytes ?? 100 * 1024 * 1024,
      evictionCheckIntervalMs: config.evictionCheckIntervalMs ?? 5000,
      onEvict: config.onEvict,
    };
    this.entries = new Map();
    this.accessOrder = [];
    this.currentMemory = 0;
    this.evictionTimer = null;
    this.weakRefs = new Map();
    this.stats = { hits: 0, misses: 0, evictions: 0, expirations: 0 };
  }

  get(key: string): V | undefined {
    const entry = this.entries.get(key);
    if (!entry) {
      this.stats.misses++;
      return undefined;
    }
    if (Date.now() > entry.expiresAt) {
      this.delete(key, 'expired');
      this.stats.misses++;
      return undefined;
    }
    entry.lastAccessed = Date.now();
    entry.accessCount++;
    this.moveToFront(key);
    this.stats.hits++;
    return entry.value;
  }

  put(key: string, value: V, options: { ttlMs?: number; size?: number } = {}): void {
    const size = options.size ?? this.estimateSize(value);
    const ttl = options.ttlMs ?? this.config.defaultTtlMs;

    if (this.entries.has(key)) {
      const old = this.entries.get(key)!;
      this.currentMemory -= old.size;
    }

    while (this.currentMemory + size > this.config.maxMemoryBytes && this.accessOrder.length > 0) {
      this.evictLRU('memory');
    }

    while (this.entries.size >= this.config.maxEntries && this.accessOrder.length > 0) {
      this.evictLRU('lru');
    }

    const entry: CacheEntry<V> = {
      value,
      expiresAt: Date.now() + ttl,
      size,
      lastAccessed: Date.now(),
      accessCount: 0,
    };

    this.entries.set(key, entry);
    this.currentMemory += size;
    this.moveToFront(key);

    if (typeof value === 'object' && value !== null) {
      this.weakRefs.set(key, new WeakRef(value as object));
    }
  }

  delete(key: string, reason: 'expired' | 'lru' | 'memory' = 'lru'): boolean {
    const entry = this.entries.get(key);
    if (!entry) return false;
    this.entries.delete(key);
    this.currentMemory -= entry.size;
    this.accessOrder = this.accessOrder.filter(k => k !== key);
    this.weakRefs.delete(key);
    if (reason === 'expired') this.stats.expirations++;
    else this.stats.evictions++;
    this.config.onEvict?.(key, reason);
    return true;
  }

  has(key: string): boolean {
    const entry = this.entries.get(key);
    if (!entry) return false;
    if (Date.now() > entry.expiresAt) {
      this.delete(key, 'expired');
      return false;
    }
    return true;
  }

  size(): number { return this.entries.size; }
  memoryUsage(): number { return this.currentMemory; }
  getStats() { return { ...this.stats, size: this.entries.size, memory: this.currentMemory }; }

  clear(): void {
    for (const key of [...this.entries.keys()]) {
      this.delete(key, 'lru');
    }
  }

  startEvictionLoop(): void {
    if (this.evictionTimer) return;
    this.evictionTimer = setInterval(() => this.evictExpired(), this.config.evictionCheckIntervalMs);
  }

  stopEvictionLoop(): void {
    if (this.evictionTimer) {
      clearInterval(this.evictionTimer);
      this.evictionTimer = null;
    }
  }

  keys(): string[] { return [...this.accessOrder]; }
  values(): V[] { return this.accessOrder.map(k => this.entries.get(k)!.value); }

  private moveToFront(key: string): void {
    this.accessOrder = this.accessOrder.filter(k => k !== key);
    this.accessOrder.unshift(key);
  }

  private evictLRU(reason: 'lru' | 'memory'): void {
    const oldest = this.accessOrder.pop();
    if (oldest) this.delete(oldest, reason);
  }

  private evictExpired(): void {
    const now = Date.now();
    const expired: string[] = [];
    for (const [key, entry] of this.entries) {
      if (now > entry.expiresAt) expired.push(key);
    }
    for (const key of expired) this.delete(key, 'expired');

    // Clean up dead weak refs
    for (const [key, ref] of this.weakRefs) {
      if (ref.deref() === undefined && this.entries.has(key)) {
        this.delete(key, 'memory');
      }
    }
  }

  private estimateSize(value: V): number {
    if (typeof value === 'string') return value.length * 2;
    if (typeof value === 'number') return 8;
    if (typeof value === 'boolean') return 4;
    if (value === null || value === undefined) return 0;
    return JSON.stringify(value).length * 2;
  }
}

// Tests
async function runTests() {
  const cache = new LRUCache<string>({ maxEntries: 3, defaultTtlMs: 100 });

  // Basic get/put
  cache.put('a', 'hello');
  console.assert(cache.get('a') === 'hello', 'basic get');
  console.assert(cache.size() === 1, 'size after put');

  // LRU eviction
  cache.put('b', 'world');
  cache.put('c', 'foo');
  cache.put('d', 'bar'); // should evict 'a'
  console.assert(!cache.has('a'), 'lru eviction');
  console.assert(cache.has('d'), 'newest kept');

  // TTL expiration
  cache.clear();
  cache.put('x', 'temp', { ttlMs: 50 });
  await new Promise(r => setTimeout(r, 80));
  console.assert(cache.get('x') === undefined, 'ttl expired');

  // Access order
  cache.clear();
  cache.put('1', 'one');
  cache.put('2', 'two');
  cache.put('3', 'three');
  cache.get('1'); // access '1', making '2' the LRU
  cache.put('4', 'four'); // should evict '2'
  console.assert(!cache.has('2'), 'access order eviction');
  console.assert(cache.has('1'), 'accessed item kept');

  // Stats
  const stats = cache.getStats();
  console.assert(stats.hits > 0, 'has hits');
  console.assert(stats.misses > 0, 'has misses');

  // Eviction loop
  const cache2 = new LRUCache<string>({ maxEntries: 10, defaultTtlMs: 50, evictionCheckIntervalMs: 30 });
  cache2.put('e1', 'val1');
  cache2.startEvictionLoop();
  await new Promise(r => setTimeout(r, 150));
  console.assert(!cache2.has('e1'), 'eviction loop cleared expired');
  cache2.stopEvictionLoop();

  console.log('All tests passed');
}
runTests();
```

Return the complete Rust project: Cargo.toml + src/lib.rs + src/main.rs (with tests as #[cfg(test)] mod tests).
