# EternalWeb User Guide & Web Archiving Insights

This document contains instructions, development philosophy, and technical cores of EternalWeb.

## 🌟 Philosophy: Why EternalWeb?

The Internet is the vastest repository of human knowledge, yet the most fragile. The theological materials or news articles you see today might vanish as '404 Not Found' tomorrow.

EternalWeb is not just a downloader. it is a **Digital Time Capsule** to guard the truth, and a shield for knowledge to be passed down to future generations.

---

## 🔍 Web Archive vs SingleFile: What's the Difference?

Choose the best tool based on your preservation goals.

| Category | Web Archive (Service/WARC) | SingleFile (SingleFile/HTML) |
| :--- | :--- | :--- |
| **Method** | Collects browsing sessions & network packets | Compresses current DOM state into a single HTML |
| **Usage** | Preserving site state, dynamic features | Personal collection, offline reading, clean docs |
| **Pros** | High fidelity for React, SPA, complex sites | Single file management, no external dependencies |
| **Cons** | Requires a viewer, files can be heavy | Real-time dynamic API features are limited |

---

## 🏗️ EternalWeb 3-Level Unified Architecture

EternalWeb combines the best of both worlds into a **3-Level System**.

### Level 1: Fast Preservation (SingleFile Engine)
- Inlines all images, styles, and fonts into a single HTML file using Base64.
- No complex folder structures; copy a single file and view it anywhere with the original design.

### Level 2: Interactive Preservation (ArchiveWeb.page Engine)
- Modern web is 'Biological'. JavaScript constantly talks to servers even after loading.
- Level 2 records the 'process' of browsing, creating a 'living' archive where buttons and menus still work offline.

### Level 3: Deep Archive (ArchiveBox Engine)
- Gathers assets beyond a single page, covering the entire site structure.
- Simultaneously saves in WARC, PDF, Screenshots, Media, and Source Code to minimize data loss risk.

---

## ❓ Why do some archives break?

Because modern web pages are no longer simple 'documents' but **'Real-time Software'**.

1. **API Dependency**: Saved files are detached from the server-side database. If a request for "fetch latest comments" has no server to answer, that area will remain empty.
2. **Path Issues**: If scripts are hardcoded to work only on specific URLs rather than local filesystems, rendering breaks.
3. **Security Walls**: Content behind logins or paywalls cannot be accessed by automated scrapers.

---

## 🚀 Best Practices

1. **Vital Text Data**: Save with SingleFile (Level 1) and use the 'Remove Scripts' option for the safest long-term readability.
2. **Complex Web Apps**: Record manually using ArchiveWeb.page (Level 2) by clicking through the site.
3. **Evidence Collection**: Use ArchiveBox (Level 3) to secure PDF and Screenshots for maximum credibility.

---

Best Regards,
**Rhee Hose**
*Initial Development: 2026-01-20 KST*
