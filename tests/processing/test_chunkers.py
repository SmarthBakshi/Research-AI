from chunkers.heading_aware import HeadingAwareChunker
from chunkers.sliding_window import SlidingWindowChunker

sample_text = """
1. Introduction
This is an intro section.

1.1 Background
More background info here.

2. Methods
We used a variety of methods.

3. Conclusion
"""

heading_chunks = HeadingAwareChunker().chunk(sample_text)
sliding_chunks = SlidingWindowChunker(window_size=20, stride=10).chunk(sample_text)

print("== Heading-Aware ==")
for c in heading_chunks: print(f"- {c}\n")

print("== Sliding Window ==")
for c in sliding_chunks: print(f"- {c}\n")
