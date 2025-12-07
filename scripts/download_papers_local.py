#!/usr/bin/env python3
"""
Download 27 influential research papers from arXiv locally
Then we'll upload them to GCS using gsutil
"""
import os
import urllib.request

# Local directory for downloads
DOWNLOAD_DIR = "/Users/smarthbakshi/Desktop/projects/Research-AI/data/arxiv"

# Curated list of 27 influential papers across NLP, LLM, and Computer Vision
PAPERS = [
    # NLP Papers (9 papers)
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        "arxiv_id": "1810.04805",
        "category": "NLP"
    },
    {
        "title": "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
        "arxiv_id": "1907.11692",
        "category": "NLP"
    },
    {
        "title": "XLNet: Generalized Autoregressive Pretraining",
        "arxiv_id": "1906.08237",
        "category": "NLP"
    },
    {
        "title": "ELECTRA: Pre-training Text Encoders as Discriminators",
        "arxiv_id": "2003.10555",
        "category": "NLP"
    },
    {
        "title": "T5: Text-to-Text Transfer Transformer",
        "arxiv_id": "1910.10683",
        "category": "NLP"
    },
    {
        "title": "BART: Denoising Sequence-to-Sequence Pre-training",
        "arxiv_id": "1910.13461",
        "category": "NLP"
    },
    {
        "title": "Sentence-BERT: Sentence Embeddings using Siamese BERT",
        "arxiv_id": "1908.10084",
        "category": "NLP"
    },
    {
        "title": "DeBERTa: Decoding-enhanced BERT with Disentangled Attention",
        "arxiv_id": "2006.03654",
        "category": "NLP"
    },
    {
        "title": "ALBERT: A Lite BERT for Self-supervised Learning",
        "arxiv_id": "1909.11942",
        "category": "NLP"
    },

    # LLM Papers (9 papers)
    {
        "title": "GPT-2: Language Models are Unsupervised Multitask Learners",
        "arxiv_id": "1908.09203",
        "category": "LLM"
    },
    {
        "title": "GPT-3: Language Models are Few-Shot Learners",
        "arxiv_id": "2005.14165",
        "category": "LLM"
    },
    {
        "title": "InstructGPT: Training language models to follow instructions",
        "arxiv_id": "2203.02155",
        "category": "LLM"
    },
    {
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "arxiv_id": "2302.13971",
        "category": "LLM"
    },
    {
        "title": "LLaMA 2: Open Foundation and Fine-Tuned Chat Models",
        "arxiv_id": "2307.09288",
        "category": "LLM"
    },
    {
        "title": "Chinchilla: Training Compute-Optimal Large Language Models",
        "arxiv_id": "2203.15556",
        "category": "LLM"
    },
    {
        "title": "PaLM: Scaling Language Modeling with Pathways",
        "arxiv_id": "2204.02311",
        "category": "LLM"
    },
    {
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "arxiv_id": "2212.08073",
        "category": "LLM"
    },
    {
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "arxiv_id": "2106.09685",
        "category": "LLM"
    },

    # Computer Vision Papers (9 papers)
    {
        "title": "Vision Transformer (ViT)",
        "arxiv_id": "2010.11929",
        "category": "CV"
    },
    {
        "title": "Swin Transformer: Hierarchical Vision Transformer",
        "arxiv_id": "2103.14030",
        "category": "CV"
    },
    {
        "title": "DETR: End-to-End Object Detection with Transformers",
        "arxiv_id": "2005.12872",
        "category": "CV"
    },
    {
        "title": "Mask R-CNN",
        "arxiv_id": "1703.06870",
        "category": "CV"
    },
    {
        "title": "YOLO v3: An Incremental Improvement",
        "arxiv_id": "1804.02767",
        "category": "CV"
    },
    {
        "title": "Segment Anything (SAM)",
        "arxiv_id": "2304.02643",
        "category": "CV"
    },
    {
        "title": "Stable Diffusion: High-Resolution Image Synthesis",
        "arxiv_id": "2112.10752",
        "category": "CV"
    },
    {
        "title": "DALL-E 2: Hierarchical Text-Conditional Image Generation",
        "arxiv_id": "2204.06125",
        "category": "CV"
    },
    {
        "title": "EfficientNet: Rethinking Model Scaling for CNNs",
        "arxiv_id": "1905.11946",
        "category": "CV"
    }
]

def download_paper(arxiv_id, title, category):
    """Download a paper from arXiv"""
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    filename = f"{category}_{arxiv_id.replace('.', '_')}.pdf"
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Skip if already exists
    if os.path.exists(filepath):
        print(f"   ⏭️  Already exists: {filename}")
        return True

    print(f"📥 Downloading: {title}")
    print(f"   arXiv ID: {arxiv_id}")

    try:
        urllib.request.urlretrieve(url, filepath)
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"   ✓ Downloaded {file_size:.2f} MB to {filepath}\n")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

def main():
    print("🚀 Starting download of 27 research papers...\n")
    print(f"Download directory: {DOWNLOAD_DIR}\n")

    # Create directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Group papers by category
    nlp_papers = [p for p in PAPERS if p["category"] == "NLP"]
    llm_papers = [p for p in PAPERS if p["category"] == "LLM"]
    cv_papers = [p for p in PAPERS if p["category"] == "CV"]

    print(f"📚 Paper breakdown:")
    print(f"   - NLP: {len(nlp_papers)} papers")
    print(f"   - LLM: {len(llm_papers)} papers")
    print(f"   - Computer Vision: {len(cv_papers)} papers")
    print(f"   - Total: {len(PAPERS)} papers\n")
    print("=" * 70 + "\n")

    success_count = 0
    failed_papers = []

    for i, paper in enumerate(PAPERS, 1):
        print(f"[{i}/{len(PAPERS)}] {paper['category']} Paper")
        if download_paper(paper["arxiv_id"], paper["title"], paper["category"]):
            success_count += 1
        else:
            failed_papers.append(paper)

    print("=" * 70)
    print(f"\n✅ Successfully downloaded: {success_count}/{len(PAPERS)} papers")

    if failed_papers:
        print(f"❌ Failed downloads: {len(failed_papers)}")
        for paper in failed_papers:
            print(f"   - {paper['title']} (arXiv:{paper['arxiv_id']})")
    else:
        print("🎉 All papers downloaded successfully!")

    print(f"\n📦 Papers saved in: {DOWNLOAD_DIR}")
    print(f"\n🔄 Next steps:")
    print(f"   1. Upload to GCS: gsutil -m cp {DOWNLOAD_DIR}/*.pdf gs://researchai-pdfs-eu/")
    print(f"   2. OR process locally: python3 scripts/process_local_pdfs.py")

if __name__ == "__main__":
    main()
