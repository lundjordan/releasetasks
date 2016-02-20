import unittest

from releasetasks.test import make_task_graph, PVT_KEY_FILE, \
    do_common_assertions, get_task_by_name


class TestBalrogSubmission(unittest.TestCase):
    maxDiff = 30000
    graph = None
    task = None
    payload = None

    def setUp(self):
        self.graph = make_task_graph(
            version="42.0b2",
            next_version="42.0b3",
            appVersion="42.0",
            buildNumber=3,
            source_enabled=False,
            en_US_config={
                "platforms": {
                    "macosx64": {},
                    "win32": {},
                    "win64": {},
                    "linux": {},
                    "linux64": {},
                }
            },
            l10n_config={},
            repo_path="releases/foo",
            product="firefox",
            revision="fedcba654321",
            partial_updates={
                "38.0": {
                    "buildNumber": 1,
                },
                "37.0": {
                    "buildNumber": 2,
                },
            },
            branch="foo",
            updates_enabled=False,
            bouncer_enabled=True,
            push_to_candidates_enabled=False,
            postrelease_version_bump_enabled=False,
            signing_class="release-signing",
            release_channels=["foo"],
            balrog_api_root="http://balrog/api",
            signing_pvt_key=PVT_KEY_FILE,
        )
        self.task = get_task_by_name(self.graph,
                                     "release-foo_firefox_bncr_sub")
        self.payload = self.task["task"]["payload"]

    def test_common_assertions(self):
        do_common_assertions(self.graph)

    def test_provisioner(self):
        self.assertEqual(self.task["task"]["provisionerId"], "buildbot-bridge")

    def test_worker_type(self):
        self.assertEqual(self.task["task"]["workerType"], "buildbot-bridge")

    def test_scopes_present(self):
        self.assertFalse("scopes" in self.task)

    def test_partials(self):
        self.assertEqual(self.payload["properties"]["partial_versions"],
                         "37.0build2, 38.0build1")

    def test_build_number(self):
        self.assertEqual(self.payload["properties"]["build_number"], 3)

    def test_graph_scopes(self):
        expected_graph_scopes = set([
            "queue:task-priority:high",
        ])
        self.assertTrue(expected_graph_scopes.issubset(self.graph["scopes"]))

    def test_repo_path(self):
        self.assertEqual(self.payload["properties"]["repo_path"],
                         "releases/foo")

    def test_script_repo_revision(self):
        self.assertEqual(self.payload["properties"]["script_repo_revision"],
                         "fedcba654321")
