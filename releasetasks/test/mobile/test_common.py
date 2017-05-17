import unittest

from jose import jwt, jws
from jose.constants import ALGORITHMS

from releasetasks import sign_task
from releasetasks.test import generate_scope_validator, PVT_KEY_FILE, PVT_KEY, PUB_KEY, OTHER_PUB_KEY, verify
from releasetasks.test.mobile import (make_task_graph, do_common_assertions,
                                      create_fennec_test_args)
from voluptuous import All, Length, Match, Schema


class TestTaskSigning(unittest.TestCase):

    def setUp(self):
        self.claims_schema = Schema({
            'taskId': 'xyz',
            'exp': int,
        }, extra=True, required=True)

        self.token = sign_task("xyz", pvt_key=PVT_KEY)

        self.decode = jwt.decode(self.token, PUB_KEY, algorithms=[ALGORITHMS.RS512])
        self.verify = jws.verify(self.token, PUB_KEY, algorithms=[ALGORITHMS.RS512])

    def test_decode(self):
        verify(self.decode, self.claims_schema)

    def test_verify(self):
        verify(self.verify, self.claims_schema)

    def test_verify_bad_signature(self):
        token = sign_task("xyz", pvt_key=PVT_KEY)
        self.assertRaises(jws.JWSError, jws.verify, token, OTHER_PUB_KEY, [ALGORITHMS.RS512])


class TestEncryption(unittest.TestCase):
    maxDiff = 30000

    def test_encryption(self):
        self.task_schema = Schema({
            'task': {
                'payload': {
                    'encryptedEnv': All(Length(2), [Match(r'^wcB')])  # Must have 2 elements, starting with wcB
                }
            }
        }, required=True, extra=True)

        test_kwargs = create_fennec_test_args({
            'updates_enabled': True,
            'repo_path': 'foo/bar',
            'branch': 'mozilla-beta',
            'signing_class': 'dep-signing',
            'release_channels': ['beta'],
            'final_verify_channels': ['beta'],
            'signing_pvt_key': PVT_KEY_FILE,
            'en_US_config': {
                "platforms": {
                    "android-4-0-armv7-api15": {"unsigned_task_id": "xyz", "signed_task_id": "xyz"},
                    "android-4-2-x86": {"unsigned_task_id": "xyz", "signed_task_id": "xyz"},
                }
            },
        })

        graph = make_task_graph(**test_kwargs)
        do_common_assertions(graph)


class TestGraphScopes(unittest.TestCase):
    maxDiff = 30000
    graph = None

    def setUp(self):
        self.graph_schema = Schema({
            'scopes': generate_scope_validator(scopes={
                "project:releng:signing:format:gpg",
                "queue:define-task:buildbot-bridge/buildbot-bridge",
                "queue:create-task:buildbot-bridge/buildbot-bridge",
                "queue:task-priority:high"
            }),
            'tasks': None,
        }, extra=True, required=True)

        test_kwargs = create_fennec_test_args({
            'signing_pvt_key': PVT_KEY_FILE,
            'en_US_config': {
                "platforms": {
                    "android-4-0-armv7-api15": {"unsigned_task_id": "xyz", "signed_task_id": "xyx"},
                    "android-4-2-x86": {"unsigned_task_id": "xyz", "signed_task_id": "xyz"},
                }
            },
        })
        self.graph = make_task_graph(**test_kwargs)

    def test_common_assertions(self):
        do_common_assertions(self.graph)

    def test_graph(self):
        verify(self.graph, self.graph_schema)
