# 📋 ResearchAI Documentation Index

Welcome to the ResearchAI documentation! This index will guide you to the right document based on your needs.

---

## 🎯 Quick Navigation

### 🚀 Getting Started

**Just want to run the system?**
→ Start with **[Workflow Quick Start](WORKFLOW_QUICKSTART.md)**

**Need to install from scratch?**
→ See the main **[README.md](../README.md)** installation section

**Want to understand how it works first?**
→ Read the **[Architecture Overview](ARCHITECTURE.md)**

---

### 📚 Documentation Overview

| Document | Purpose | Audience | Estimated Reading Time |
|----------|---------|----------|----------------------|
| [**WORKFLOW_QUICKSTART.md**](WORKFLOW_QUICKSTART.md) | Step-by-step guide to running the pipeline | Beginners, Users | 15 minutes |
| [**CODEBASE_GUIDE.md**](CODEBASE_GUIDE.md) | Complete codebase explanation and deep dive | Developers | 45 minutes |
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | System architecture and component interactions | Architects, Developers | 30 minutes |
| [**TROUBLESHOOTING.md**](TROUBLESHOOTING.md) | Common issues and solutions | All users | Reference only |

---

## 📖 Documentation by Use Case

### "I want to use ResearchAI"

1. **[README.md](../README.md)** - Understand what ResearchAI does
2. **[WORKFLOW_QUICKSTART.md](WORKFLOW_QUICKSTART.md)** - Run your first pipeline
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix issues if they arise

### "I want to develop/contribute to ResearchAI"

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand the system design
2. **[CODEBASE_GUIDE.md](CODEBASE_GUIDE.md)** - Explore the code in depth
3. **[README.md](../README.md)** - See development setup and contributing guidelines
4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Debug development issues

### "I want to deploy ResearchAI to production"

1. **[CODEBASE_GUIDE.md](CODEBASE_GUIDE.md)** - Understand the system thoroughly
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Plan your deployment architecture
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Prepare for operational issues
4. **[README.md](../README.md)** - Review security and performance notes

### "I want to customize ResearchAI"

1. **[CODEBASE_GUIDE.md](CODEBASE_GUIDE.md)** - Find what to modify
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand component boundaries
3. **[WORKFLOW_QUICKSTART.md](WORKFLOW_QUICKSTART.md)** - Test your changes
4. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Debug custom implementations

---

## 📝 Document Contents Summary

### [WORKFLOW_QUICKSTART.md](WORKFLOW_QUICKSTART.md)
**"Get up and running in 30 minutes"**

Contents:
- ⚡ What the system does (simple explanation)
- 🔄 Three-stage pipeline overview
- 🚀 Complete workflow example with commands
- 🎬 How to monitor and view logs
- 🔍 Understanding your data at each stage
- 📊 Performance expectations
- 🆘 Quick troubleshooting

Best for: First-time users, quick reference

---

### [CODEBASE_GUIDE.md](CODEBASE_GUIDE.md)
**"Complete guide to the entire codebase"**

Contents:
- 🏗️ System architecture (detailed)
- 📂 Repository structure (every directory explained)
- 🔄 Complete data flow workflow (all three DAGs)
- 🧩 Component deep dive (extractors, chunkers, embedders, etc.)
- 🐳 Docker services explained
- 🚀 Development workflow
- 🧪 Testing strategy
- 🔧 Configuration guide
- 🎯 Current status & roadmap
- 🔍 Key design decisions

Best for: Developers, contributors, architects

---

### [ARCHITECTURE.md](ARCHITECTURE.md)
**"Visual guide to system design and interactions"**

Contents:
- 📐 Layered architecture diagram
- 🔄 Data flow architecture (ingestion, processing, embedding)
- 🧩 Component interaction map
- 🔌 API integration points
- 🔀 Event flow diagrams (sequence diagrams)
- 📦 Module organization
- 🔐 Security considerations
- 📊 Monitoring & observability

Best for: Understanding system design, planning integrations

---

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**"Solutions to common problems"**

Contents:
- 🆘 Installation & setup issues
- ⚙️ Airflow problems
- 🗄️ Database issues
- 📦 MinIO issues
- 🔍 OpenSearch issues
- 🔄 Pipeline execution problems
- ❓ Frequently Asked Questions
- 🐞 Debug mode guide
- 📞 How to get more help

Best for: Troubleshooting, debugging, FAQ reference

---

## 🗺️ Learning Path

### Beginner Path (1-2 hours)
```
README.md (20 min)
    ↓
WORKFLOW_QUICKSTART.md (30 min)
    ↓
Run the pipeline (30 min)
    ↓
TROUBLESHOOTING.md (as needed)
```

### Developer Path (3-4 hours)
```
README.md (20 min)
    ↓
ARCHITECTURE.md (45 min)
    ↓
CODEBASE_GUIDE.md (90 min)
    ↓
WORKFLOW_QUICKSTART.md (30 min)
    ↓
Run and modify pipeline (60 min)
```

### Architect Path (2-3 hours)
```
README.md (20 min)
    ↓
ARCHITECTURE.md (60 min)
    ↓
CODEBASE_GUIDE.md (60 min)
    ↓
TROUBLESHOOTING.md - Deployment section (30 min)
```

---

## 🔍 Quick Reference

### Key Concepts Explained

**Concept** | **Explained In**
-----------|----------------
RAG (Retrieval-Augmented Generation) | WORKFLOW_QUICKSTART.md, CODEBASE_GUIDE.md
Vector Embeddings | WORKFLOW_QUICKSTART.md, CODEBASE_GUIDE.md
Hybrid Search (BM25 + Vector) | CODEBASE_GUIDE.md, ARCHITECTURE.md
Chunking Strategy | CODEBASE_GUIDE.md
PDF Extraction (Hybrid Approach) | CODEBASE_GUIDE.md
Airflow DAGs | WORKFLOW_QUICKSTART.md, CODEBASE_GUIDE.md
Docker Architecture | ARCHITECTURE.md
Component Communication | ARCHITECTURE.md

---

### Common Tasks

**Task** | **Find It In**
---------|---------------
Install and setup | README.md
Run the pipeline | WORKFLOW_QUICKSTART.md
Add more papers | WORKFLOW_QUICKSTART.md
Debug failed tasks | TROUBLESHOOTING.md
Modify chunking strategy | CODEBASE_GUIDE.md
Change embedding model | CODEBASE_GUIDE.md, TROUBLESHOOTING.md
Deploy to production | TROUBLESHOOTING.md (FAQ section)
Add custom metadata | TROUBLESHOOTING.md (FAQ section)
Monitor performance | WORKFLOW_QUICKSTART.md, ARCHITECTURE.md
Understand data flow | ARCHITECTURE.md
Navigate codebase | CODEBASE_GUIDE.md
Fix Docker issues | TROUBLESHOOTING.md

---

## 📊 Document Relationship Diagram

```
                    README.md
                  (Entry Point)
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
  WORKFLOW_QUICK   ARCHITECTURE   CODEBASE_GUIDE
     START.md         .md             .md
         │             │             │
         │             │             │
         └─────────────┼─────────────┘
                       │
                       ▼
              TROUBLESHOOTING.md
                 (Reference)
```

---

## 🎯 Goals of Each Document

### README.md
**Goal:** Give overview and get users started quickly
- What is ResearchAI?
- Why use it?
- Quick start commands
- Links to detailed docs

### WORKFLOW_QUICKSTART.md
**Goal:** Enable users to run the pipeline successfully
- Practical, hands-on guide
- Step-by-step instructions
- Expected outputs at each stage
- Visual data transformations

### CODEBASE_GUIDE.md
**Goal:** Help developers understand and modify the code
- Complete code organization
- Design patterns explained
- Implementation details
- Development best practices

### ARCHITECTURE.md
**Goal:** Explain system design and component interactions
- High-level architecture
- Data flows
- Service communication
- Integration points

### TROUBLESHOOTING.md
**Goal:** Help users solve problems independently
- Common error solutions
- FAQ for quick answers
- Debug techniques
- How to get help

---

## 📚 Additional Resources

### External Documentation

**Technology** | **Official Docs**
--------------|------------------
Apache Airflow | https://airflow.apache.org/docs/
OpenSearch | https://opensearch.org/docs/
MinIO | https://min.io/docs/
FastAPI | https://fastapi.tiangolo.com/
Docker | https://docs.docker.com/
HuggingFace | https://huggingface.co/docs/

### Related Papers

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
- [Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906)
- [REALM: Retrieval-Augmented Language Model Pre-Training](https://arxiv.org/abs/2002.08909)

---

## 🤝 Contributing to Documentation

### Documentation Standards

1. **Use clear, simple language**
2. **Include code examples**
3. **Add diagrams where helpful**
4. **Provide step-by-step instructions**
5. **Test all commands before documenting**
6. **Keep sections focused and scannable**
7. **Link between related documents**

### Suggesting Improvements

Found something unclear? Have an idea?

1. Open an issue: "Documentation: [Issue/Suggestion]"
2. Be specific about what's confusing
3. Suggest improvements if possible
4. PRs welcome!

---

## 📅 Document Maintenance

**Last Full Review:** 2025-10-28

**Review Schedule:**
- Minor updates: As code changes
- Major review: Every release
- Version alignment: Match code version

**Maintainers:**
- Primary: Smarth Bakshi
- Contributors: See GitHub contributors

---

## 🎓 Suggested Reading Order by Role

### **Data Scientist**
1. README.md
2. WORKFLOW_QUICKSTART.md
3. CODEBASE_GUIDE.md (Components section)
4. TROUBLESHOOTING.md (FAQ)

### **Backend Developer**
1. README.md
2. ARCHITECTURE.md
3. CODEBASE_GUIDE.md
4. WORKFLOW_QUICKSTART.md (for testing)

### **MLOps Engineer**
1. README.md
2. ARCHITECTURE.md
3. CODEBASE_GUIDE.md
4. TROUBLESHOOTING.md (Deployment section)

### **Product Manager**
1. README.md
2. WORKFLOW_QUICKSTART.md
3. ARCHITECTURE.md (High-level sections)
4. CODEBASE_GUIDE.md (Roadmap section)

### **QA Engineer**
1. README.md
2. WORKFLOW_QUICKSTART.md
3. TROUBLESHOOTING.md
4. CODEBASE_GUIDE.md (Testing section)

---

## 💡 Tips for Using This Documentation

1. **Don't read everything at once** - Use the index to find what you need
2. **Start with quick start** - Get hands-on experience first
3. **Use search** (Ctrl+F) - Find specific topics quickly
4. **Follow links** - Documents reference each other
5. **Try examples** - All code snippets are tested
6. **Bookmark frequently used sections** - Use GitHub's bookmarking
7. **Read error messages carefully** - They often point to the solution

---

## 🔄 Document Updates

To check if documentation is up to date:

```bash
# Check last commit date
git log -1 --format=%ai docs/

# Check if code has changed since docs update
git log --since="2025-10-28" --oneline services/ dags/
```

If code has significantly changed, documentation may need updates.

---

## 📞 Documentation Feedback

Have feedback on the documentation?

**Quick fixes:**
- Open a PR with suggested changes

**Major issues:**
- Open an issue with "Documentation:" prefix

**Questions:**
- Use GitHub Discussions

**Email:**
- bakshismarth.20@gmail.com (for urgent issues)

---

**Welcome to ResearchAI! Happy coding! 🚀**
