# -*- coding: utf-8 -*-
import os

import pytest
import requests

from httpdbg.mode_script import run_script
from httpdbg.__main__ import pyhttpdbg_entry_point
from httpdbg.server import httpdbg
from httpdbg.server import httpdbg_srv


@pytest.mark.script
def test_run_script_from_pyhttpdbg_entry_point(httpbin, monkeypatch):
    script_to_run = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "demo_run_script.py"
    )
    monkeypatch.setattr(
        "sys.argv", ["pyhttpdbg", "--script", script_to_run, httpbin.url]
    )

    pyhttpdbg_entry_point(test_mode=True)


@pytest.mark.script
def test_run_script(httpbin, httpdbg_port):
    with httpdbg_srv(httpdbg_port) as records:
        with httpdbg(records):
            script_to_run = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "demo_run_script.py"
            )
            run_script([script_to_run, httpbin.url])

        ret = requests.get(f"http://127.0.0.1:{httpdbg_port}/requests")

    reqs = ret.json()["requests"]

    assert len(reqs) == 2
    assert reqs[list(reqs.keys())[0]]["url"] == httpbin.url + "/get"
    assert reqs[list(reqs.keys())[1]]["url"] == httpbin.url + "/post"


@pytest.mark.script
def test_run_script_with_exception(httpbin, httpdbg_port, capsys):
    with httpdbg_srv(httpdbg_port) as records:
        with httpdbg(records):
            script_to_run = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "demo_run_script.py"
            )
            run_script([script_to_run, httpbin.url, "raise_exception"])

        ret = requests.get(f"http://127.0.0.1:{httpdbg_port}/requests")

    reqs = ret.json()["requests"]

    assert len(reqs) == 1
    assert reqs[list(reqs.keys())[0]]["url"] == httpbin.url + "/get"

    assert "--raise_exception--" in capsys.readouterr().err


@pytest.mark.script
def test_run_script_no_args(httpbin, capsys):
    with pytest.raises(SystemExit):
        run_script([])


@pytest.mark.script
def test_run_script_not_a_python_script(httpbin, capsys):
    with pytest.raises(SystemExit):
        run_script(["not_a_path_to_a_python_script"])


@pytest.mark.api
@pytest.mark.script
def test_run_script_initiator(httpbin, httpdbg_port):

    with httpdbg_srv(httpdbg_port) as records:

        PYTEST_CURRENT_TEST = os.environ["PYTEST_CURRENT_TEST"]
        os.environ.pop("PYTEST_CURRENT_TEST")

        with httpdbg(records):
            script_to_run = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "demo_run_script.py"
            )
            run_script([script_to_run, httpbin.url])

        os.environ["PYTEST_CURRENT_TEST"] = PYTEST_CURRENT_TEST

        ret = requests.get(f"http://127.0.0.1:{httpdbg_port}/requests")

    reqs = ret.json()["requests"]

    assert (
        reqs[list(reqs.keys())[0]]["initiator"].get("short_label")
        == '    _ = requests.get(f"{base_url}/get")'
    )
    assert 'demo_run_script.py", line 8,' in reqs[list(reqs.keys())[0]][
        "initiator"
    ].get("long_label")
    assert '_ = requests.get(f"{base_url}/get")' in reqs[list(reqs.keys())[0]][
        "initiator"
    ].get("long_label")
