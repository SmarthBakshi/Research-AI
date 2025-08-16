from services.ingestion.arxiv.writer import MinIOWriter

def ingest_pdfs_from_metadata(metadata: list[dict]):
    writer = MinIOWriter()
    results = []

    for entry in metadata:
        # Get arXiv ID (assuming present in entry['id'] or parse from alternate link)
        arxiv_id = None
        for key in ["id", "arxiv_id", "identifier"]:  # flexible fallback
            if key in entry:
                arxiv_id = entry[key].split("/")[-1].strip()
                break

        if not arxiv_id:
            print(f"❌ Skipping entry with no arXiv ID: {entry.get('title', 'Unknown Title')}")
            continue

        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        print(f"⬇️ Downloading PDF for: {arxiv_id}")

        try:
            content_hash = writer.write_pdf(pdf_url)
            results.append({
                "arxiv_id": arxiv_id,
                "pdf_url": pdf_url,
                "content_hash": content_hash,
            })
        except Exception as e:
            print(f"❌ Failed to process {arxiv_id}: {e}")

    return results
