import time
from typing import Tuple
from uuid import uuid4

from M2Crypto import ASN1, EVP, RSA, X509


def make_request(bits) -> Tuple[X509.Request, EVP.PKey, str]:

    pk = EVP.PKey()
    x = X509.Request()
    rsa = RSA.gen_key(bits, 65537, lambda *x: b"")
    pk.assign_rsa(rsa)
    x.set_pubkey(pk)
    name = x.get_subject()
    name.C = "UK"
    name.CT = "Some State"
    domain = f"{uuid4()}.yuubin.io"
    name.CN = domain
    name.O = "Yuubin Self Signed Authority"  # noqa

    ext1 = X509.new_extension("subjectAltName", f"DNS:{domain}")
    ext2 = X509.new_extension("nsComment", "Yuubin Self signed")
    extstack = X509.X509_Extension_Stack()
    extstack.push(ext1)
    extstack.push(ext2)
    x.add_extensions(extstack)

    x.sign(pk, "sha256")

    return x, pk, domain


def create_self_signed_certificate(cert_path, key_path):

    req, private_key, domain = make_request(2048)

    pkey = req.get_pubkey()
    sub = req.get_subject()

    cert = X509.X509()
    cert.set_serial_number(int(time.time()))
    cert.set_version(0)
    cert.set_subject(sub)
    t = int(time.time()) + time.timezone
    now = ASN1.ASN1_UTCTIME()

    now.set_time(t)
    now_plus_year = ASN1.ASN1_TIME()
    now_plus_year.set_time(t + 60 * 60 * 24 * 365)
    cert.set_not_before(now)
    cert.set_not_after(now_plus_year)

    issuer = X509.X509_Name()
    issuer.C = "UK"
    issuer.CN = domain
    issuer.O = "Yuubin Self Signed Authority"  # noqa
    cert.set_issuer(issuer)
    cert.set_pubkey(pkey)

    ext = X509.new_extension("subjectAltName", f"DNS:{domain}")
    ext.set_critical(0)
    cert.add_ext(ext)

    cert.sign(private_key, "sha256")

    cert.save(cert_path)
    private_key.save_key(key_path, cipher=None, callback=lambda *x: b"")
