import json
from pathlib import Path

import pytest

from textra_api_wrapper import APIClient
from textra_api_wrapper.client import APIResponseParser


@pytest.mark.slow
def test_client():
    client = APIClient()
    text = "Hello everyone. My name is ｟John.｠"
    res = client.translate(text)

    expected = "皆さんこんにちは、John.と申します。"
    assert res.text == expected
    assert res.original_text == text
    assert res.information["text-s"] == text
    assert res.information["text-t"] == expected
    assert res.request_url == "https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/"


@pytest.mark.slow
def test_ja_to_en():
    client = APIClient(source_lang="ja", target_lang="en")
    text = "こんにちは、皆さん。私の名前は｟タロー｠です"
    res = client.translate(text)

    expected = "Hi everyone. My name is タロー."
    assert res.text == expected
    assert res.original_text == text
    assert res.request_url == "https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/"


@pytest.mark.slow
def test_snapshot(snapshot):
    client = APIClient()
    text = "Hello everyone. My name is ｟John.｠"
    res = client.translate(text)
    j = json.dumps(res.json, ensure_ascii=False, indent=2)
    snapshot.assert_match(j, "translate.json")


@pytest.mark.slow
def test_file(snapshot):
    client = APIClient()
    original_filepath = "tests/text_en.cfg"
    res = client.set_file(original_filepath).json
    res["resultset"]["code"] = "成功は0、重複の場合は900を返しサーバーへのリクエストは行われません"  # noqa
    res["resultset"]["message"] = "完了もしくは重複のメッセージが返ります"
    res["resultset"]["result"]["pid"] = "本来は5桁の数値ですがテスト用に書き換えています"  # noqa

    set_json = json.dumps(res, ensure_ascii=False, indent=2)
    snapshot.assert_match(set_json, "set_file.json")

    res = client.file_status().json
    res["resultset"]["result"]["list"] = [
        "本来は次の形式ですがテスト用に書き換えています",
        {
            "id": 71269,
            "title": "text_en",
            "state": 0,
            "register": "2024-07-16 09:42:53",
        },
    ]
    status_json = json.dumps(res, ensure_ascii=False, indent=2)
    snapshot.assert_match(status_json, "file_status.json")


def test_set_file_return():
    # `set_file`の戻り値から`pid`および`title`を取得する例
    sample_path = "tests/snapshots/test_client/test_file/set_file.json"
    path = Path(sample_path)
    sample_dict = json.loads(path.read_text())
    sample = APIResponseParser(sample_dict)

    assert sample.get("pid") == "本来は5桁の数値ですがテスト用に書き換えています"
    assert sample.request["title"] == "text_en"


def test_file_status_return():
    # `file_status`の戻り値から`id`および`title`が合致したものを取得する例
    sample_path = "tests/snapshots/test_client/test_file/file_status.json"
    path = Path(sample_path)
    sample_dict = json.loads(path.read_text())
    sample = APIResponseParser(sample_dict)
    sample_dict = {
        "id": 71269,
        "title": "text_en",
        "state": 0,
        "register": "2024-07-16 09:42:53",
    }
    assert sample.get_status({"id": 71269}) == sample_dict
    assert sample.get_status({"title": "text_en"}) == sample_dict
    assert sample.get_status({"state": 0}) == sample_dict
    assert sample.get_status({"id": 12345}) is None
