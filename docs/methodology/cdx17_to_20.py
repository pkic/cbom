#!/usr/bin/env python3
"""Convert a CycloneDX 1.6 or 1.7 CBOM to CycloneDX 2.0.

Covers the constructs the PKIC CBOM profiles use. It targets the 2.0 schema the
profiles are pinned to (CycloneDX/specification, 2.0-dev, commit 76f185c), and
will need revisiting when 2.0 is released.

  1.x                                         2.0
  bomFormat                                   specFormat
  metadata.component                          inventories[0].subject
  components[], services[]                    inventories[0].components[]
                                              (a service becomes type 'service')
  purl                                        identifiers[] asserted by a party
  supplier / manufacturer on a component      parties[] with a role
  protocolProperties.cryptoRefArray           protocolProperties.relatedCryptographicAssets
  relatedCryptoMaterialProperties.algorithmRef  relatedCryptographicAssets
  certificateProperties.signatureAlgorithmRef   relatedCryptographicAssets
  securedBy.algorithmRef (string)             securedBy.algorithmRef (array)
  algorithmProperties.curve                   algorithmProperties.ellipticCurve
  algorithmProperties.certificationLevel      dropped; use certifications[]
  algorithmProperties.implementationPlatform  array
  service.data, authenticated, x-trust-boundary, trustZone   dropped
  compositions[].assemblies                   compositions[].targets, kind 'components'
  metadata.properties pkic:example:comment    $comment

Properties named pkic:profile:* are carried unchanged. The CycloneDX 1.x
property 'pkic:profile:subjectIdentifier' becomes an identifier with the custom
scheme 'tag-uri'. The property 'pkic:profile:moduleValidationScheme' on a
library, with a 'certification-report' external reference, becomes a
certifications[] entry.

Usage: python3 cdx17_to_20.py <in-1.x.json> <out-2.0.json>
"""
import copy
import json
import sys

P = "pkic:profile:"
INVENTORY_REF = "inventory:subject"
ASSERTER_REF = "party:document-author"
CURVES = {"x25519": "other/Curve25519", "x448": "other/Curve448", "ed25519": "other/Ed25519",
          "ed448": "other/Ed448", "secp256r1": "secg/secp256r1", "p-256": "nist/P-256",
          "secp384r1": "secg/secp384r1", "p-384": "nist/P-384", "secp521r1": "secg/secp521r1",
          "p-521": "nist/P-521"}
VALIDATION_SCHEMES = {"fips-140-3": "FIPS 140-3", "fips-140-2": "FIPS 140-2",
                      "iso-19790": "ISO/IEC 19790", "cavp": "CAVP"}


def org(entity):
    if not entity:
        return None
    o = {"name": entity.get("name", "unnamed")}
    urls = entity.get("url") or []
    if urls:
        o["url"] = [{"name": "website", "url": u} for u in urls]
    return o


def party(ref, role, entity):
    p = {"bom-ref": ref, "roles": [{"role": role}]}
    o = org(entity)
    if o:
        p["organization"] = o
    return p


def related(refs, comps, default="algorithm"):
    out = []
    for r in refs:
        kind = comps.get(r, {}).get("cryptoProperties", {}).get("assetType", default)
        out.append({"type": {"algorithm": "algorithm", "certificate": "certificate",
                             "related-crypto-material": "key", "protocol": "protocol"}.get(kind, default),
                    "ref": r})
    return out


def convert_component(c, comps, asserter, is_service=False):
    c = copy.deepcopy(c)
    if is_service:
        c["type"] = "service"
        for k in ("data", "authenticated", "x-trust-boundary", "trustZone", "provider", "services"):
            c.pop(k, None)
    parties = []
    for role in ("supplier", "manufacturer"):
        ent = c.pop(role, None)
        if ent:
            parties.append(party("party:%s:%s" % (c.get("bom-ref", "c"), role), role, ent))
    props = c.get("properties", [])
    idents = []
    purl = c.pop("purl", None)
    if purl:
        idents.append({"scheme": "purl", "value": purl})
    tag = [p for p in props if p["name"] == P + "subjectIdentifier"]
    if tag:
        idents.append({"scheme": {"name": "tag-uri", "description": "A tag URI (RFC 4151)."},
                       "value": tag[0]["value"]})
        props = [p for p in props if p["name"] != P + "subjectIdentifier"]
    if idents:
        c["identifiers"] = [{"party": asserter, "identities": idents}]
    # Module validation moves to certifications[] when the scheme is a real one.
    scheme = [p["value"] for p in props if p["name"] == P + "moduleValidationScheme"]
    if scheme and scheme[0] != "none":
        cert = {"standard": VALIDATION_SCHEMES.get(scheme[0], scheme[0])}
        for ref in c.get("externalReferences", []):
            if ref.get("type") == "certification-report":
                cert["url"] = ref.get("url")
        c["certifications"] = [cert]
    if parties:
        c["parties"] = parties
    if props:
        c["properties"] = props
    elif "properties" in c:
        del c["properties"]

    cp = c.get("cryptoProperties")
    if cp:
        ap = cp.get("algorithmProperties")
        if ap:
            ap.pop("certificationLevel", None)
            curve = ap.pop("curve", None)
            if curve:
                mapped = CURVES.get(str(curve).lower())
                if mapped:
                    ap["ellipticCurve"] = mapped
            plat = ap.get("implementationPlatform")
            if plat and not isinstance(plat, list):
                ap["implementationPlatform"] = [plat]
        pp = cp.get("protocolProperties")
        if pp and "cryptoRefArray" in pp:
            rel = related(pp.pop("cryptoRefArray"), comps)
            pp["relatedCryptographicAssets"] = rel + pp.get("relatedCryptographicAssets", [])
        if pp and not pp.get("relatedCryptographicAssets"):
            pp.pop("relatedCryptographicAssets", None)
        rm = cp.get("relatedCryptoMaterialProperties")
        if rm:
            alg = rm.pop("algorithmRef", None)
            if alg:
                rm["relatedCryptographicAssets"] = related([alg], comps)
            sb = rm.get("securedBy")
            if sb and isinstance(sb.get("algorithmRef"), str):
                sb["algorithmRef"] = [sb["algorithmRef"]]
        cert = cp.get("certificateProperties")
        if cert:
            rel = []
            for key in ("signatureAlgorithmRef", "subjectPublicKeyRef"):
                v = cert.pop(key, None)
                if v:
                    rel += related([v], comps)
            if rel:
                cert["relatedCryptographicAssets"] = rel + cert.get("relatedCryptographicAssets", [])
    return c


def convert(bom):
    if str(bom.get("specVersion", "")).startswith("2."):
        return copy.deepcopy(bom)
    src = copy.deepcopy(bom)
    md = src.get("metadata", {})
    comps = {c.get("bom-ref"): c for c in src.get("components", [])}
    subject = md.pop("component", {"type": "application", "name": "unnamed"})
    asserter = ASSERTER_REF

    out = {"specFormat": "CycloneDX", "specVersion": "2.0"}
    note = src.pop("$comment", None)
    mprops = [p for p in md.get("properties", []) if p.get("name") != "pkic:example:comment"]
    for p in md.get("properties", []):
        if p.get("name") == "pkic:example:comment":
            note = p["value"]
    if note:
        out["$comment"] = note
    for k in ("serialNumber", "version"):
        if k in src:
            out[k] = src[k]
    md = {k: v for k, v in md.items() if k != "properties"}
    if mprops:
        md["properties"] = mprops
    if "tools" in md and isinstance(md["tools"], dict):
        md["tools"]["components"] = [convert_component(t, {}, asserter) for t in md["tools"].get("components", [])]
    out["metadata"] = md

    subj = convert_component(subject, comps, asserter)
    author = md.get("supplier") or {"name": "document author"}
    subj.setdefault("parties", []).insert(0, party(asserter, "author", author))
    entries = [convert_component(c, comps, asserter) for c in src.get("components", [])]
    entries += [convert_component(s, comps, asserter, is_service=True) for s in src.get("services", [])]
    out["inventories"] = [{"bom-ref": INVENTORY_REF, "subject": subj, "components": entries}]
    if src.get("dependencies"):
        out["dependencies"] = src["dependencies"]
    comps_out = []
    for comp in src.get("compositions", []):
        comps_out.append({"kind": "components", "aggregate": comp.get("aggregate", "not-specified"),
                          "targets": [INVENTORY_REF]})
    if comps_out:
        out["compositions"] = comps_out
    if src.get("externalReferences"):
        out["externalReferences"] = src["externalReferences"]
    if src.get("properties"):
        out["properties"] = src["properties"]
    return out


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    bom = json.load(open(argv[1], encoding="utf-8"))
    with open(argv[2], "w", encoding="utf-8") as fh:
        json.dump(convert(bom), fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
