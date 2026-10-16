---
title: Tooling
sideMenu: true
weight: 40
aliases:
- /cbom/tooling/
description: Software that generates, consumes, validates or analyses Cryptography
  Bills of Materials.
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

The complete editorial register is published below. Use the site search or your browser’s find command to locate an entry. [Open the original interactive register](https://pkic.github.io/cbom/tooling/).

**A listing is not an endorsement.** A tool is listed when its maintainer's own material states that it works with CBOMs, and each entry links to that statement. Nothing here has been tested by the working group: no entry is a claim that a tool's output conforms to a profile, and the tool requirements in the [Conformance](../methodology/conformance/) section are not assessed. Details change quickly — check the source before relying on one.

## ac-scanner

**Primary function:** Generates

Open source · AGPL-3.0 Active

### [AC Scanner](https://github.com/qubitac/AC-Scanner)

qubitac · checked 13 Sep 2026

A network scanner that outputs a CBOM as structured JSON. Its README does not say which format the JSON follows.

**Does**

Generates

**Finds cryptography in**

Network traffic

[Where CBOM support is stated ↗](https://github.com/qubitac/AC-Scanner)

## appviewx-pqc-assessment

**Primary function:** Generates

Free tier Active

### [AppViewX PQC Assessment Tool](https://www.appviewx.com/blogs/appviewx-avx-one-pqc-assessment-tool-kickstart-your-pqc-readiness-journey-with-complete-cryptographic-visibility/)

AppViewX · checked 13 Sep 2026

Scans code, dependencies, certificates and configuration, gives a PQC readiness score, and generates a CBOM in CycloneDX or CSV. Free with registration.

**Does**

Generates Analyses

**Finds cryptography in**

Source code Certificates and keystores Configuration

**Formats**

CycloneDX

[Where CBOM support is stated ↗](https://www.appviewx.com/blogs/appviewx-avx-one-pqc-assessment-tool-kickstart-your-pqc-readiness-journey-with-complete-cryptographic-visibility/)

## aqtive-guard

**Primary function:** Consumes

Commercial Active

### [AQtive Guard](https://www.aqtiveguard.com/)

SandboxAQ · checked 13 Sep 2026

A platform for discovering and managing cryptographic assets that imports CBOM files produced by other tools. The product site also says it generates CBOMs; the export format is not stated.

**Does**

Consumes Generates Analyses

**Formats**

CycloneDX 1.4 (import) CycloneDX 1.6 (import)

[Where CBOM support is stated ↗](https://docs.aqtiveguard.com/data-sources/cbom/)

## bf-cbom

**Primary function:** Analyses

Open source · GPL-3.0-only Active

### [BF-CBOM](https://github.com/SEG-UNIBE/BF-CBOM)

Software Engineering Group, University of Bern · checked 13 Sep 2026

A research framework that runs several CBOM generators in containers and compares their output side by side.

**Does**

Analyses Consumes Visualises

[Where CBOM support is stated ↗](https://github.com/SEG-UNIBE/BF-CBOM)

## cbom-compliance

**Primary function:** Validates

Free tier Active verify

### [CBOM Compliance](https://cbomcompliance.com/)

NextGenRails · checked 13 Sep 2026

A web service that grades the cryptographic assets in an uploaded BOM against NIST PQC deadlines. The site gives no company details beyond a contact address.

**Does**

Validates Consumes Analyses

**Formats**

CycloneDX 1.6 CycloneDX 1.7 SPDX

[Where CBOM support is stated ↗](https://cbomcompliance.com/)

## cipheriq-cbom-explorer

**Primary function:** Visualises

Open source · GPL-3.0-or-later Active

### [CBOM Explorer](https://github.com/CipherIQ/cbom-explorer)

CipherIQ · checked 13 Sep 2026

A browser-based viewer that loads a CBOM and shows its assets and dependencies as an interactive graph. Also offered under a commercial licence.

**Does**

Visualises Consumes

**Formats**

CycloneDX 1.6 CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/CipherIQ/cbom-explorer)

## cipheriq-cbom-generator

**Primary function:** Generates

Open source · GPL-3.0-or-later Active

### [CBOM Generator](https://github.com/CipherIQ/cbom-generator)

CipherIQ · checked 13 Sep 2026

A static scanner for Linux systems that inventories certificates, keys, algorithms, cryptographic libraries and services. Also offered under a commercial licence.

**Does**

Generates

**Finds cryptography in**

Filesystems Certificates and keystores Configuration

**Formats**

CycloneDX 1.6 CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/CipherIQ/cbom-generator)

## cbom-secure

**Primary function:** Generates

Commercial Active

### [CBOM Secure](https://www.encryptionconsulting.com/cryptographic-discovery-inventory/)

Encryption Consulting · checked 13 Sep 2026

A discovery and inventory product with sensors for cloud platforms, HSMs, TLS endpoints, directories, databases, filesystems, source code and binaries.

**Does**

Generates Analyses

**Finds cryptography in**

Source code Binaries Filesystems Network traffic Cloud services Certificates and keystores

**Formats**

CycloneDX 1.6 CycloneDX 1.7

[Where CBOM support is stated ↗](https://www.encryptionconsulting.com/cryptographic-discovery-inventory/)

## codeql-cbom-action

**Primary function:** Generates

Open source · MIT Active

### [cbom-action](https://github.com/advanced-security/cbom-action)

GitHub (advanced-security) · checked 13 Sep 2026

GitHub Actions that build a crypto bill of materials from CodeQL analysis across a set of repositories and languages. The output format is not documented.

**Does**

Generates

**Finds cryptography in**

Source code

[Where CBOM support is stated ↗](https://github.com/advanced-security/cbom-action)

## cbom-lens

**Primary function:** Generates

Open source · Apache-2.0 Active

### [CBOM-Lens](https://github.com/OmniTrustILM/cbom-lens)

OmniTrust (formerly 3Key Company, CZERTAINLY) · checked 13 Sep 2026

A command-line tool or service that finds certificates, keys, secrets and algorithms on filesystems, in container images and on network ports, and writes a CBOM.

**Does**

Generates

**Finds cryptography in**

Filesystems Container images Network traffic Certificates and keystores

**Formats**

CycloneDX 1.6 CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/OmniTrustILM/cbom-lens)

## cbom-repository

**Primary function:** Stores and manages

Open source · Apache-2.0 Active

### [CBOM-Repository](https://github.com/OmniTrustILM/cbom-repository)

OmniTrust (formerly 3Key Company, CZERTAINLY) · checked 13 Sep 2026

A REST service on S3-compatible storage for uploading, versioning, retrieving and searching CBOMs in JSON.

**Does**

Stores and manages Consumes

**Formats**

CycloneDX 1.6 CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/OmniTrustILM/cbom-repository)

## cbom4cert

**Primary function:** Generates

Open source · Apache-2.0 Active

### [cbom4cert](https://github.com/anthonyharrison/cbom4cert)

Anthony Harrison · checked 13 Sep 2026

Generates a CBOM for installed certificates. One of few tools offering SPDX output, which its README describes as incomplete.

**Does**

Generates

**Finds cryptography in**

Certificates and keystores

**Formats**

CycloneDX SPDX (incomplete)

[Where CBOM support is stated ↗](https://github.com/anthonyharrison/cbom4cert)

## cbomctl

**Primary function:** Analyses

Open source · Apache-2.0 Active

### [cbomctl](https://github.com/lvlrSajjad/cbomctl)

Sadjad Asadi · checked 13 Sep 2026

Takes a CBOM from any generator and evaluates it against several national PQC policies. It does not scan anything itself.

**Does**

Analyses Consumes

**Formats**

CycloneDX

[Where CBOM support is stated ↗](https://github.com/lvlrSajjad/cbomctl)

## cbomkit

**Primary function:** Generates

Open source · Apache-2.0 Active

### [CBOMkit](https://github.com/cbomkit/cbomkit)

Post-Quantum Cryptography Alliance (Linux Foundation); originally IBM Research · checked 13 Sep 2026

A service with a web viewer, an API and a database: it generates CBOMs from repositories, displays uploaded CBOMs, checks them against compliance policies, and stores them behind a REST API.

**Does**

Generates Stores and manages Visualises Analyses Consumes

**Finds cryptography in**

Source code

[Where CBOM support is stated ↗](https://github.com/cbomkit/cbomkit)

## cbomkit-action

**Primary function:** Generates

Open source · Apache-2.0 Active

### [CBOMkit-action](https://github.com/cbomkit/cbomkit-action)

Post-Quantum Cryptography Alliance (CBOMkit project) · checked 13 Sep 2026

A GitHub Action that finds the modules in a repository, scans their Java and Python source, and produces one CBOM per module as a workflow artifact.

**Does**

Generates

**Finds cryptography in**

Source code

[Where CBOM support is stated ↗](https://github.com/cbomkit/cbomkit-action)

## cbomkit-theia

**Primary function:** Generates

Open source · Apache-2.0 Active

### [CBOMkit-theia](https://github.com/cbomkit/cbomkit-theia)

Post-Quantum Cryptography Alliance (CBOMkit project) · checked 13 Sep 2026

A command-line tool that finds certificates, keys, secrets and cryptographic configuration in container images and directories and writes a CBOM, or enriches an existing one. It does not scan source code.

**Does**

Generates Consumes

**Finds cryptography in**

Container images Filesystems Certificates and keystores Configuration

**Formats**

CycloneDX 1.6

[Where CBOM support is stated ↗](https://github.com/cbomkit/cbomkit-theia)

## cdxgen

**Primary function:** Generates

Open source · Apache-2.0 Active

### [cdxgen](https://github.com/cdxgen/cdxgen)

cdxgen project (OWASP) · checked 13 Sep 2026

A general BOM generator whose CBOM coverage is Java keystores and certificates and algorithm use in JavaScript and TypeScript source; its tracebom command records cryptographic activity while a command runs.

**Does**

Generates

**Finds cryptography in**

Certificates and keystores Source code Running systems

**Formats**

CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/cdxgen/cdxgen)

## cryptamap

**Primary function:** Generates

Open source · MIT-0 Active

### [CryptaMap](https://github.com/aws-samples/sample-CryptaMap)

AWS Samples · checked 13 Sep 2026

Builds an organisation-wide inventory of cryptography in AWS services as a CBOM. A sample project rather than a supported AWS product.

**Does**

Generates Analyses

**Finds cryptography in**

Cloud services

**Formats**

CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/aws-samples/sample-CryptaMap)

## cryptarch

**Primary function:** Generates

Open source · Apache-2.0 Active

### [cryptarch](https://github.com/jhammant/cryptarch)

jhammant · checked 13 Sep 2026

A scanner for network endpoints and certificates that can write its findings as a CBOM.

**Does**

Generates

**Finds cryptography in**

Network traffic Certificates and keystores

**Formats**

CycloneDX 1.6

[Where CBOM support is stated ↗](https://github.com/jhammant/cryptarch)

## cryptobom-forge

**Primary function:** Generates

Open source · GPL-3.0 Active

### [Cryptobom Forge](https://github.com/Santandersecurityresearch/cryptobom-forge)

Santander Security Research · checked 13 Sep 2026

Turns CodeQL analysis results into a CBOM and checks a CBOM against rules, reporting in SARIF. Its documented output uses the CBOM extension that preceded CycloneDX 1.6.

**Does**

Generates Analyses

**Finds cryptography in**

Source code

**Formats**

CycloneDX 1.4 with the pre-standard CBOM extension

[Where CBOM support is stated ↗](https://github.com/Santandersecurityresearch/cryptobom-forge)

## cryptodeps

**Primary function:** Generates

Open source · Apache-2.0 Active

### [CryptoDeps](https://github.com/csnp/cryptodeps)

CSNP (QRAMM Toolkit) · checked 13 Sep 2026

Analyses a project's dependencies for cryptography and can report as a CBOM. The sample output in its README declares CycloneDX 1.5, which predates cryptographic assets in CycloneDX.

**Does**

Generates

**Finds cryptography in**

Source code

[Where CBOM support is stated ↗](https://github.com/csnp/cryptodeps)

## cryptoscan

**Primary function:** Generates

Open source · Apache-2.0 Active

### [CryptoScan](https://github.com/csnp/cryptoscan)

CSNP (QRAMM Toolkit) · checked 13 Sep 2026

A source code scanner with a CBOM output format. The sample output in its README declares specVersion 1.0, and CycloneDX 1.6 cryptographic properties are listed as planned.

**Does**

Generates

**Finds cryptography in**

Source code

[Where CBOM support is stated ↗](https://github.com/csnp/cryptoscan)

## dynamiccbom

**Primary function:** Generates

Open source · MIT Active

### [DynamicCBOM](https://github.com/SEG-UNIBE/DynamicCBOM)

Software Engineering Group, University of Bern · checked 13 Sep 2026

Experimental software that traces OpenSSL 3 calls at runtime with eBPF and writes a CBOM, without changing the traced program.

**Does**

Generates

**Finds cryptography in**

Running systems

**Formats**

CycloneDX 1.6

[Where CBOM support is stated ↗](https://github.com/SEG-UNIBE/DynamicCBOM)

## ibm-guardium-cryptography-manager

**Primary function:** Consumes

Commercial Active verify

### [IBM Guardium Cryptography Manager](https://www.ibm.com/docs/en/guardium-cm/2.0.x?topic=getting-portfolio-view-code-repositories)

IBM · checked 13 Sep 2026

Imports code repository findings from IBM Quantum Safe Explorer, including CBOMs, into a portfolio view. CBOM is mentioned only as an imported data type.

**Does**

Consumes Analyses

[Where CBOM support is stated ↗](https://www.ibm.com/docs/en/guardium-cm/2.0.x?topic=getting-portfolio-view-code-repositories)

## ibm-quantum-safe-explorer

**Primary function:** Generates

Commercial Active

### [IBM Quantum Safe Explorer](https://www.ibm.com/docs/en/quantum-safe/quantum-safe-explorer/2.x?topic=quantum-safe-explorer-overview)

IBM · checked 13 Sep 2026

Scans source code in several languages for quantum-vulnerable cryptography and reports as a CBOM, among other formats. The documentation does not name a CycloneDX version.

**Does**

Generates

**Finds cryptography in**

Source code

[Where CBOM support is stated ↗](https://www.ibm.com/docs/en/quantum-safe/quantum-safe-explorer/2.x?topic=quantum-safe-explorer-overview)

## keyfactor-agilesec

**Primary function:** Generates

Commercial Active

### [Keyfactor AgileSec](https://docs.keyfactor.com/agilesec/latest/agilesec-3-4-release-notes)

Keyfactor (formerly InfoSec Global) · checked 13 Sep 2026

A cryptographic inventory platform that exports its findings as a CBOM for each scanned source, from release 3.4.

**Does**

Generates Analyses

**Finds cryptography in**

Source code Binaries Configuration

**Formats**

CycloneDX 1.6

[Where CBOM support is stated ↗](https://docs.keyfactor.com/agilesec/latest/agilesec-3-4-release-notes)

## open-quantum-secure

**Primary function:** Generates

Open source · MIT Active

### [open-quantum-secure](https://github.com/jimbo111/open-quantum-secure)

jimbo111 · checked 13 Sep 2026

A scanner that combines its own findings with those of other engines, such as CryptoScan, cdxgen and CBOMkit-theia, into one CBOM.

**Does**

Generates Analyses

**Finds cryptography in**

Source code Binaries Network traffic Certificates and keystores

**Formats**

CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/jimbo111/open-quantum-secure)

## pqaudit

**Primary function:** Generates

Open source · MIT Active

### [pqaudit](https://github.com/PQCWorld/pqaudit)

PQCWorld · checked 13 Sep 2026

An audit tool for quantum-vulnerable cryptography in code, configuration and endpoints that reports as a CBOM.

**Does**

Generates

**Finds cryptography in**

Source code Configuration Network traffic

**Formats**

CycloneDX 1.6

[Where CBOM support is stated ↗](https://github.com/PQCWorld/pqaudit)

## pqc-readiness-cli

**Primary function:** Generates

Open source · MIT Active

### [pqc-readiness-cli](https://github.com/qtonicquantum/pqc-readiness-cli)

Qtonic Quantum · checked 13 Sep 2026

Reads PEM and DER certificate files and writes a CBOM.

**Does**

Generates

**Finds cryptography in**

Certificates and keystores

**Formats**

CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/qtonicquantum/pqc-readiness-cli)

## quantakrypto-pqc-tools

**Primary function:** Generates

Open source · Apache-2.0 Active

### [pqc-tools](https://github.com/quantakrypto/pqc-tools)

quantakrypto (Dandelion Labs) · checked 13 Sep 2026

A set of scanners for source code and network endpoints whose outputs include a CBOM. Its README does not name the CBOM format.

**Does**

Generates Analyses

**Finds cryptography in**

Source code Network traffic

[Where CBOM support is stated ↗](https://github.com/quantakrypto/pqc-tools)

## qcecuring-cbom

**Primary function:** Generates

Commercial Active

### [QCecuring CBOM](https://www.qcecuring.com/product/cbom)

QCecuring · checked 13 Sep 2026

A discovery product covering code repositories, directories, certificate authorities, web servers, cloud platforms, HSMs and Kubernetes that reports in CycloneDX JSON and XML.

**Does**

Generates Analyses

**Finds cryptography in**

Source code Certificates and keystores Network traffic Cloud services

**Formats**

CycloneDX

[Where CBOM support is stated ↗](https://www.qcecuring.com/product/cbom)

## qinsight-atlas

**Primary function:** Generates

Commercial Active

### [Qinsight Atlas](https://www.qinsight.com/product-cryptographic-posture-management)

Qinsight · checked 13 Sep 2026

A cryptographic posture management platform that builds a CBOM for each scanned source. The product page does not name a format.

**Does**

Generates Analyses

**Finds cryptography in**

Cloud services Source code Running systems

[Where CBOM support is stated ↗](https://www.qinsight.com/product-cryptographic-posture-management)

## qscout

**Primary function:** Analyses

Commercial Active

### [QScout](https://qtonicquantum.com/qscout)

Qtonic Quantum (formerly Qryptonic) · checked 13 Sep 2026

An assessment service and platform for quantum cryptographic risk with CBOM output among its deliverables.

**Does**

Analyses Generates

**Formats**

CycloneDX 1.7

[Where CBOM support is stated ↗](https://qtonicquantum.com/qscout)

## quprotect-r3

**Primary function:** Generates

Commercial Active

### [QuProtect R3](https://www.qusecure.com/cryptographic-bill-of-materials-cbom/)

QuSecure · checked 13 Sep 2026

A PQC platform whose reporting component produces CBOMs from the inventory its sensors build.

**Does**

Generates Analyses

**Formats**

CycloneDX

[Where CBOM support is stated ↗](https://www.qusecure.com/cryptographic-bill-of-materials-cbom/)

## qvision

**Primary function:** Generates

Commercial Active

### [QVision](https://www.pqstation.com/qvision)

PQStation · checked 13 Sep 2026

A discovery platform that reconciles network, certificate, filesystem and source code observations into one CBOM.

**Does**

Generates Analyses

**Finds cryptography in**

Network traffic Certificates and keystores Filesystems Source code

**Formats**

CycloneDX 1.7

[Where CBOM support is stated ↗](https://www.pqstation.com/qvision)

## sbom-tools

**Primary function:** Analyses

Open source · MIT Active

### [sbom-tools](https://github.com/sbom-tool/sbom-tools)

sbom-tool project · checked 13 Sep 2026

A tool for diffing, quality scoring and compliance checks of BOMs that reads the cryptographic properties of CycloneDX 1.6 and 1.7 documents and tells a CBOM from an SBOM.

**Does**

Analyses Consumes Validates Visualises

**Formats**

CycloneDX 1.6 CycloneDX 1.7

[Where CBOM support is stated ↗](https://github.com/sbom-tool/sbom-tools)

## sonar-cryptography

**Primary function:** Generates

Open source · Apache-2.0 Active

### [Sonar Cryptography Plugin](https://github.com/cbomkit/sonar-cryptography)

Post-Quantum Cryptography Alliance (CBOMkit project) · checked 13 Sep 2026

A SonarQube plugin, also known as CBOMkit-hyperion, that detects cryptographic assets in Java, Python and Go source and writes a CBOM when its Cryptographic Inventory rule is enabled.

**Does**

Generates

**Finds cryptography in**

Source code

**Formats**

CycloneDX 1.6

[Where CBOM support is stated ↗](https://github.com/cbomkit/sonar-cryptography)

## csnp-tls-analyzer

**Primary function:** Generates

Open source · MIT Active

### [TLS Analyzer](https://github.com/csnp/tls-analyzer)

CSNP (QRAMM Toolkit) · checked 13 Sep 2026

Analyses TLS endpoints and can report as a CBOM.

**Does**

Generates

**Finds cryptography in**

Network traffic

**Formats**

CycloneDX

[Where CBOM support is stated ↗](https://github.com/csnp/tls-analyzer)

## tychon-cryptographic-inventory

**Primary function:** Generates

Commercial Active

### [TYCHON Cryptographic Inventory](https://tychon.io/tychoncryptographicinventory/)

TYCHON · checked 13 Sep 2026

A cryptographic inventory product with quantum readiness scoring that lists CBOM as an inventory output.

**Does**

Generates Analyses

**Formats**

CycloneDX

[Where CBOM support is stated ↗](https://tychon.io/tychoncryptographicinventory/)

**Know a tool that should be here, or an entry that is out of date?** Email [cbom@lists.pkic.org](mailto:cbom@lists.pkic.org?subject=CBOM%20tool%20suggestion) with a link to where its maintainer states CBOM support — see [Contributing](../contributing/#suggest-a-tool). Maintainers update `tooling.md`, retaining the evidence link and nonendorsement statement, using the [shared publication format](https://github.com/pkic/cbom/blob/main/PUBLICATION.md).
