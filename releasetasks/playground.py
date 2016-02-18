import os
from releasetasks import make_task_graph


DUMMY_PUBLIC_KEY = os.path.join(os.path.dirname(__file__), "public.key")
PVT_KEY_FILE = os.path.join(os.path.dirname(__file__), "id_rsa")

en_US_config = {
    "platforms": {
        "macosx64": {"task_id": "xyz"},
        "win32": {"task_id": "xyy"}
    }
}
l10n_config = {
    "platforms": {
        "win32": {
            "en_us_binary_url": "https://queue.taskcluster.net/something/firefox.exe",
            "locales": ["de", "en-GB", "zh-TW"],
            "chunks": 1,
        },
        "macosx64": {
            "en_us_binary_url": "https://queue.taskcluster.net/something/firefox.tar.xz",
            "locales": ["de", "en-GB", "zh-TW"],
            "chunks": 1,
        },

    },
    "changesets": {
        "de": "default",
        "en-GB": "default",
        "zh-TW": "default",
    },
}

def main():
    graph = make_task_graph(public_key=DUMMY_PUBLIC_KEY,
                            balrog_username="fake", balrog_password="fake",
                            beetmover_aws_access_key_id="baz",
                            beetmover_aws_secret_access_key="norf",
                            running_tests=True,
                            version="42.0b2",
                            next_version="42.0b3",
                            appVersion="42.0",
                            buildNumber=3,
                            source_enabled=False,
                            updates_enabled=True,
                            bouncer_enabled=False,
                            push_to_candidates_enabled=True,
                            postrelease_version_bump_enabled=False,
                            en_US_config=en_US_config,
                            l10n_config=l10n_config,
                            partial_updates={
                                "38.0": {
                                    "buildNumber": 1,
                                },
                                "37.0": {
                                    "buildNumber": 2,
                                },
                            },
                            balrog_api_root="https://fake.balrog/api",
                            signing_class="release-signing",
                            branch="mozilla-beta",
                            product="firefox",
                            repo_path="releases/mozilla-beta",
                            revision="abcdef123456",
                            release_channels=["beta"],
                            signing_pvt_key=PVT_KEY_FILE)

    import pprint
    pprint.pprint(graph)

if __name__ == '__main__':
    main()

