# -*- coding: utf8 -*-
"""
Test suite
"""

from bitbucketlock import BitBucketLock

TEST_HOST = "localhost"
TEST_USER = "testuser"
TEST_PASSWORD = "testpassword"


def test_BitBucketLock_init():
    new_instance = BitBucketLock(TEST_HOST, TEST_USER, TEST_PASSWORD)
    assert isinstance(new_instance, BitBucketLock)
    return
