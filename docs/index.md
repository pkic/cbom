---
layout: default
title: CBOM Reference Register
---

# CBOM Reference Register

A maintained register of the standards, regulations and guidance that bear on
Cryptography Bills of Materials — curated by the
[CBOM Profiles Working Group]({{ site.wg.url }}) of the PKI Consortium.

[Browse the references →]({{ '/references/' | relative_url }})

## Why this exists

Almost every jurisdiction now requires organisations to hold **a cryptographic
inventory**. Almost none of them says what that inventory should *look like*.

India's CERT-In guidelines are the notable exception: they name the CBOM outright.
Everywhere else — the EU's NIS Cooperation Group roadmap, the UK's NCSC timelines,
OMB M-23-02 in the United States, the MAS advisory in Singapore — the obligation is
stated and the format is left open.

That gap is the case for a CBOM profile methodology, and this register is the
evidence base for it.

## How it works

The register lives in a single YAML file, [`_data/references.yml`](https://github.com/pkic/pkic_cbom/blob/main/docs/_data/references.yml),
which is the source of truth. The page you see is generated from it. Adding a
reference means adding a YAML entry and opening a pull request — no HTML, no
templates. See [CONTRIBUTING-references.md](https://github.com/pkic/pkic_cbom/blob/main/CONTRIBUTING-references.md).

Keeping the data separate from the presentation also means the register can be
lifted into the pkic.org site (or any other) without rework.
