# Task: Implement a Lock-Free Concurrent LRU Cache

## Problem

Design and implement a thread-safe LRU (Least Recently Used) cache in Python that supports concurrent reads and writes without using a global lock. The cache must handle high-throughput scenarios where multiple threads are reading and writing simultaneously.

## Requirements

1. **`LRUCache(capacity: int)`** — Initialize with a fixed capacity
2. **`get(key: str) -> Optional[str]`** — Return the value if key exists (and mark as recently used), otherwise return None
3. **`put(key: str, value: str) -> None`** — Insert or update a key-value pair. If cache is at capacity, evict the least recently used entry.
4. **Thread safety** — Multiple threads can call get/put concurrently without data corruption
5. **Performance** — get and put must be O(1) average time complexity
6. **No global lock** — Use fine-grained locking, lock-free data structures, or other concurrent programming techniques. A single `threading.Lock()` wrapping the entire operation is NOT acceptable.

## Constraints
- Use only Python standard library (threading, collections, etc.)
- The cache must pass concurrent stress tests with 8+ threads
- Must handle at least 100,000 operations per second on a modern machine

## Expected Implementation
- Doubly-linked list for LRU ordering
- Hash map for O(1) key lookup
- Per-node or striped locking for concurrency

## Test Cases
Your implementation will be tested with:
```python
cache = LRUCache(3)
cache.put("a", "1")
cache.put("b", "2")  
cache.put("c", "3")
assert cache.get("a") == "1"  # "a" is now most recently used
cache.put("d", "4")            # evicts "b" (least recently used)
assert cache.get("b") is None  # "b" was evicted
assert cache.get("c") == "3"
assert cache.get("d") == "4"

# Concurrent test: 8 threads doing 10000 ops each
# No crashes, no data corruption, no deadlocks
```
