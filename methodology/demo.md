---
title: Demo
sideMenu: true
weight: 3
aliases:
- /cbom/methodology/demo.html
linkTitle: Demo
---

> Illustrative working draft of the CBOM Profiles Working Group. This material is not an adopted deliverable.
{.callout-info}

Four example documents, evaluated against the Interface Disclosure Baseline. The first declares both a service and a management interface and conforms. The second omits the management interface and fails a product rule. The third declares both but exercises each of the four disclosure outcomes. The fourth is a subject with no administrative surface at all, which satisfies the management-interface rule by saying so rather than by having one: a structural rule is satisfied by presence or by a stated absence, and silence is neither. In the standalone demo, the carrier version selector shows how the profile's declared acceptance range treats documents written to other versions of CycloneDX. Each of the four is a document committed in the source repository, and the rules come from the published rules file rather than a transcription of it. The standalone demo results are tested against `validate_cbom.py`'s on the same four documents, so the demo and the reference tool cannot quietly disagree.

[Open the interactive conformance example](https://pkic.github.io/cbom/methodology/demo.html). The standalone example runs in the source project; it is not executed by the PKIC content renderer.

| Example | Expected baseline result | Document |
| --- | --- | --- |
| Both service and management interfaces | Conforms | [Conforming CBOM](../../docs/methodology/cbom-pass.cyclonedx.json) |
| Missing management interface | Does not conform | [Missing-interface CBOM](../../docs/methodology/cbom-fail.cyclonedx.json) |
| Disclosure states | Does not conform; distinguishes withheld, unknown, and undeclared | [Disclosure CBOM](../../docs/methodology/cbom-disclosure.cyclonedx.json) |
| No administrative surface | Conforms through stated absence | [No-management-interface CBOM](../../docs/methodology/cbom-noadmin.cyclonedx.json) |

[Download the rules](../../docs/methodology/profile-interface-disclosure.rules.json) and [run the reference validator](../files/). Carrier versions 1.5, 1.6, 1.7, and 1.8 demonstrate refused, legacy, target, and newer-version handling.
