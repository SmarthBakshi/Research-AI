#!/usr/bin/env python3
"""
Check the current indexing status in Cloud SQL
"""
import os
import psycopg2

os.environ["POSTGRES_HOST"] = "35.246.234.51"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "ResearchAI2024Secure!"
os.environ["APP_DB"] = "researchai"
os.environ["POSTGRES_PORT"] = "5432"

conn = psycopg2.connect(
    host=os.environ["POSTGRES_HOST"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    database=os.environ["APP_DB"],
    port=os.environ["POSTGRES_PORT"]
)
cur = conn.cursor()

# Total chunks
cur.execute("SELECT COUNT(*) FROM chunks")
total_chunks = cur.fetchone()[0]

# Indexed chunks
cur.execute("SELECT COUNT(*) FROM chunks WHERE indexed_at IS NOT NULL")
indexed_chunks = cur.fetchone()[0]

# Unindexed chunks
unindexed_chunks = total_chunks - indexed_chunks

# Unique files
cur.execute("SELECT COUNT(DISTINCT source_file) FROM chunks")
total_files = cur.fetchone()[0]

# Indexed files
cur.execute("SELECT COUNT(DISTINCT source_file) FROM chunks WHERE indexed_at IS NOT NULL")
indexed_files = cur.fetchone()[0]

# File breakdown
cur.execute("""
    SELECT
        source_file,
        COUNT(*) as chunk_count,
        MAX(indexed_at) IS NOT NULL as is_indexed
    FROM chunks
    GROUP BY source_file, is_indexed
    ORDER BY is_indexed DESC, source_file
""")
files = cur.fetchall()

conn.close()

print("=" * 70)
print("📊 ResearchAI Indexing Status")
print("=" * 70)
print(f"\n📦 Chunks:")
print(f"   Total: {total_chunks:,}")
print(f"   Indexed: {indexed_chunks:,} ({100*indexed_chunks/total_chunks if total_chunks > 0 else 0:.1f}%)")
print(f"   Pending: {unindexed_chunks:,}")

print(f"\n📚 Files:")
print(f"   Total: {total_files}")
print(f"   Indexed: {indexed_files}")
print(f"   Pending: {total_files - indexed_files}")

if files:
    print(f"\n📋 File Details:")
    indexed_list = [(f[0], f[1]) for f in files if f[2]]
    pending_list = [(f[0], f[1]) for f in files if not f[2]]

    if indexed_list:
        print(f"\n   ✅ Indexed ({len(indexed_list)} files):")
        for filename, count in indexed_list[:10]:  # Show first 10
            print(f"      - {filename}: {count} chunks")
        if len(indexed_list) > 10:
            print(f"      ... and {len(indexed_list) - 10} more")

    if pending_list:
        print(f"\n   ⏳ Pending ({len(pending_list)} files):")
        for filename, count in pending_list[:10]:  # Show first 10
            print(f"      - {filename}: {count} chunks")
        if len(pending_list) > 10:
            print(f"      ... and {len(pending_list) - 10} more")

print("\n" + "=" * 70)
