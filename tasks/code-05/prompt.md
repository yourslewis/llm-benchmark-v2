# Task: Median of Two Sorted Arrays with Streaming Extension

## Problem (based on LeetCode #4 — Hard)

Given two sorted arrays `nums1` and `nums2`, find the median of the combined sorted array. The overall run time complexity must be O(log(min(m, n))).

## Part 1: Classic Solution

Implement `findMedianSortedArrays(nums1: List[int], nums2: List[int]) -> float`

### Examples
```
Input: nums1 = [1, 3], nums2 = [2]
Output: 2.0

Input: nums1 = [1, 2], nums2 = [3, 4]
Output: 2.5

Input: nums1 = [], nums2 = [1]
Output: 1.0

Input: nums1 = [1, 3, 5, 7, 9, 11], nums2 = [2, 4, 6, 8, 10, 12]
Output: 6.5
```

### Constraints
- `0 <= m, n <= 10^6` where m = len(nums1), n = len(nums2)
- At least one array is non-empty
- Must be O(log(min(m, n))) — NOT O(m + n) merge

## Part 2: Streaming Extension

Now extend your solution to handle a **streaming** scenario:

Implement `StreamingMedian` class:
```python
class StreamingMedian:
    def __init__(self):
        pass
    
    def add(self, num: int) -> None:
        """Add a number to the stream."""
        pass
    
    def median(self) -> float:
        """Return the current median of all added numbers."""
        pass
```

### Requirements
- `add()` must be O(log n)
- `median()` must be O(1)
- Hint: Use two heaps (max-heap for lower half, min-heap for upper half)

## Constraints
- Python standard library only
- Both parts in the same file
- Include type hints
