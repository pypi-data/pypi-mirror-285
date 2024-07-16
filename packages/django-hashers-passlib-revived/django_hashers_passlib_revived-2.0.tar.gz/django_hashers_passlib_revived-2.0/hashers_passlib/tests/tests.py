# This file is part of django-hashers-passlib
# (https://github.com/mathiasertl/django-hashers-passlib).
#
# django-hashers-passlib is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# django-hashers-passlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# django-hashers-passlib. If not, see <http://www.gnu.org/licenses/>.

"""Test for all hasher classes."""

from collections import OrderedDict

import passlib
import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from pytest_django.fixtures import SettingsWrapper

import hashers_passlib
from hashers_passlib import converters

PASSWORDS = [
    "I",
    "DA",
    "RoJ",
    "THxn",
    "1uzPU",
    "oe331f",
    "qBcP47",
    # 'D4i19w',
    # 'e8qBbIA',
    # 'vzCXzq8',
    # '7xEmLNYW',
    # 'HeVCzQ3I',
    # 'mMIJzMuAo',
    # '4gjjrcCfm',
    # '3Asa788x6g',
    # 'AGwKzVP1SC',
    # 'CWwYP880G4',
    # 'RK8SMEmv0s',
]

# ------------------------------------------------------------------------------
# Test Base Classes
# ------------------------------------------------------------------------------


class BaseMixin:
    hasher = NotImplemented

    @property
    def path(self) -> str:
        """Shortcut for getting the  full classpath to the hasher."""
        return f"{self.hasher.__module__}.{self.hasher.__class__.__name__}"

    def assert_summary(self, encoded: str) -> None:
        """Assert that the summary is as expected."""
        summary = self.hasher.safe_summary(encoded)
        assert isinstance(summary, OrderedDict)
        assert len(summary) >= 1

    @pytest.mark.django_db()
    def test_check(self, settings: SettingsWrapper) -> None:
        """Test creating passwords and checking them again using our hashes."""
        settings.PASSWORD_HASHERS = [self.path]
        for password in PASSWORDS:
            encoded = make_password(password)
            assert check_password(password, encoded)

            self.assert_summary(encoded)

            # test to_orig, done here, to save a few hash-generations
            encoded_orig = self.hasher.to_orig(encoded)
            assert self.hasher.hasher.verify(password, encoded_orig)

            back = self.hasher.from_orig(encoded_orig)
            assert encoded == back

    @pytest.mark.django_db()
    def test_user_model(
        self, settings: SettingsWrapper, django_user_model: User
    ) -> None:
        """Test the django user password."""
        password = "foobar-random"
        user = django_user_model.objects.create(username="foobar")

        settings.PASSWORD_HASHERS = [self.path]
        user.set_password(password)
        user.save()
        assert user.check_password(password)

        # this is False because no hasher recognizes the format
        settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.PBKDF2PasswordHasher"]
        assert not user.check_password(password)

        settings.PASSWORD_HASHERS = [self.path]
        assert user.check_password(password)


class BaseConverterMixin:
    hasher = NotImplemented
    alt_hasher = NotImplemented
    converter = NotImplemented

    def setup_class(self) -> None:
        self.alt_hasher = getattr(passlib.hash, self.converter.__class__.__name__)

    @pytest.mark.django_db()
    def test_base(self, settings: SettingsWrapper) -> None:
        """Basic test for converters."""
        settings.PASSWORD_HASHERS = [self.hasher]
        for password in PASSWORDS:
            orig = self.alt_hasher.encrypt(password)
            conv = self.converter.from_orig(orig)

            # see if we get a working hash:
            assert check_password(password, conv)

            # convert back and test with passlib:
            back = self.converter.to_orig(conv)
            assert orig == back


# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------


class TestDesCrypt(BaseMixin):
    hasher = hashers_passlib.des_crypt()


class TestBsdiCrypt(BaseMixin):
    hasher = hashers_passlib.bsdi_crypt()


class TestBigcrypt(BaseMixin):
    hasher = hashers_passlib.bsdi_crypt()


class TestCrypt16(BaseMixin):
    hasher = hashers_passlib.crypt16()


class TestMd5Crypt(BaseMixin):
    hasher = hashers_passlib.md5_crypt()


class TestSha1Crypt(BaseMixin):
    hasher = hashers_passlib.sha1_crypt()


class TestSunMd5Crypt(BaseMixin):
    hasher = hashers_passlib.sun_md5_crypt()


class TestSha256Crypt(BaseMixin):
    hasher = hashers_passlib.sha256_crypt()


class TestSha512Crypt(BaseMixin):
    hasher = hashers_passlib.sha512_crypt()


class TestAprMd5Crypt(BaseMixin):
    hasher = hashers_passlib.apr_md5_crypt()


class TestBcryptSha256(BaseMixin):
    hasher = hashers_passlib.bcrypt_sha256()


class TestPhpass(BaseMixin):
    hasher = hashers_passlib.phpass()


class TestPbkdf2Sha1(BaseMixin):
    hasher = hashers_passlib.pbkdf2_sha1()


class TestPbkdf2Sha256(BaseMixin):
    hasher = hashers_passlib.pbkdf2_sha256()

    def test_settings(self, settings: SettingsWrapper) -> None:
        """Test passing additional kwargs to the hasher."""
        encoded = self.hasher.encode("foobar", rounds=32)
        assert self.hasher.safe_summary(encoded)["iterations"] == 32

        encoded = self.hasher.encode("foobar", rounds=64)
        assert self.hasher.safe_summary(encoded)["iterations"] == 64

        settings.PASSWORD_HASHERS = [self.path]
        settings.PASSLIB_KEYWORDS = {"pbkdf2_sha256": {"rounds": 64}}
        encoded = self.hasher.encode("foobar")
        assert self.hasher.safe_summary(encoded)["iterations"] == 64


class TestPbkdf2Sha512(BaseMixin):
    hasher = hashers_passlib.pbkdf2_sha512()


class TestCtaPbkdf2Sha1(BaseMixin):
    hasher = hashers_passlib.cta_pbkdf2_sha1()


class TestDlitzPbkdf2Sha1(BaseMixin):
    hasher = hashers_passlib.dlitz_pbkdf2_sha1()


class TestScram(BaseMixin):
    hasher = hashers_passlib.scram()


class TestLdapSaltedMd5(BaseMixin):
    hasher = hashers_passlib.ldap_salted_md5()


class TestLdapSaltedSha1(BaseMixin):
    hasher = hashers_passlib.ldap_salted_sha1()


class TestAtlassianPbkdf2Sha1(BaseMixin):
    hasher = hashers_passlib.atlassian_pbkdf2_sha1()


class TestFshp(BaseMixin):
    hasher = hashers_passlib.fshp()


class TestMssql2000(BaseMixin):
    hasher = hashers_passlib.mssql2000()


class TestMssql2005(BaseMixin):
    hasher = hashers_passlib.mssql2005()


class TestMysql323(BaseMixin):
    hasher = hashers_passlib.mysql323()


class TestMysql41(BaseMixin):
    hasher = hashers_passlib.mysql41()


class TestOracle11(BaseMixin):
    hasher = hashers_passlib.oracle11()


class TestLmhash(BaseMixin):
    hasher = hashers_passlib.lmhash()


class TestNthash(BaseMixin):
    hasher = hashers_passlib.nthash()


class TestCiscoPix(BaseMixin):
    hasher = hashers_passlib.cisco_pix()


class TestCiscoType7(BaseMixin):
    hasher = hashers_passlib.cisco_type7()


class TestGrubPbkdf2Sha512(BaseMixin):
    hasher = hashers_passlib.grub_pbkdf2_sha512()


class TestHexMd4(BaseMixin):
    hasher = hashers_passlib.hex_md4()


class TestHexSha256(BaseMixin):
    hasher = hashers_passlib.hex_sha256()


class TestHexSha512(BaseMixin):
    hasher = hashers_passlib.hex_sha512()


class TestArgon2D(BaseMixin):
    hasher = hashers_passlib.argon2d()


class TestArgon2I(BaseMixin):
    hasher = hashers_passlib.argon2i()


class TestArgon2Id(BaseMixin):
    hasher = hashers_passlib.argon2id()


class TestScrypt(BaseMixin):
    hasher = hashers_passlib.scrypt()


class TestBcrypt(BaseConverterMixin):
    hasher = "django.contrib.auth.hashers.BCryptPasswordHasher"
    converter = converters.bcrypt()


class TestBsdNthash(BaseConverterMixin):
    hasher = "hashers_passlib.nthash"
    converter = converters.bsd_nthash()


class TestLdapMd5(BaseConverterMixin):
    hasher = "django.contrib.auth.hashers.UnsaltedMD5PasswordHasher"
    converter = converters.ldap_md5()


class TestLdapSha1(BaseConverterMixin):
    hasher = "django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher"
    converter = converters.ldap_sha1()


class TestLdapHexMd5(BaseConverterMixin):
    hasher = "django.contrib.auth.hashers.UnsaltedMD5PasswordHasher"
    converter = converters.ldap_hex_md5()


class TestLdapHexSha1(BaseConverterMixin):
    hasher = "django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher"
    converter = converters.ldap_hex_sha1()


class TestLdapDesCrypt(BaseConverterMixin):
    hasher = "hashers_passlib.des_crypt"
    converter = converters.ldap_des_crypt()


class TestLdapBsdiCrypt(BaseConverterMixin):
    hasher = "hashers_passlib.bsdi_crypt"
    converter = converters.ldap_bsdi_crypt()


class TestLdapMd5Crypt(BaseConverterMixin):
    hasher = "hashers_passlib.md5_crypt"
    converter = converters.ldap_md5_crypt()


class TestLdapBcrypt(BaseConverterMixin):
    hasher = "django.contrib.auth.hashers.BCryptPasswordHasher"
    converter = converters.ldap_bcrypt()


class TestLdapSha1Crypt(BaseConverterMixin):
    hasher = "hashers_passlib.sha1_crypt"
    converter = converters.ldap_sha1_crypt()


class TestLdapSha256Crypt(BaseConverterMixin):
    hasher = "hashers_passlib.sha256_crypt"
    converter = converters.ldap_sha256_crypt()


class TestLdapSha512Crypt(BaseConverterMixin):
    hasher = "hashers_passlib.sha512_crypt"
    converter = converters.ldap_sha512_crypt()


class TestLdapPbkdf2Sha1(BaseConverterMixin):
    hasher = "hashers_passlib.pbkdf2_sha1"
    converter = converters.ldap_pbkdf2_sha1()


class TestLdapPbkdf2Sha256(BaseConverterMixin):
    hasher = "hashers_passlib.pbkdf2_sha256"
    converter = converters.ldap_pbkdf2_sha256()


class TestLdapPbkdf2Sha512(BaseConverterMixin):
    hasher = "hashers_passlib.pbkdf2_sha512"
    converter = converters.ldap_pbkdf2_sha512()
