import json
from pathlib import Path

import pytest

from textra_api_wrapper import APIClient
from textra_api_wrapper.api_response_parser import APIResponseParser


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


def effect(state, pid, title):
    return APIResponseParser(
        {
            "resultset": {
                "code": 0,
                "message": "",
                "request": {
                    "url": "https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/",
                },
                "result": {
                    "list": [
                        {
                            "id": pid,
                            "title": title,
                            "state": state,
                            "register": "2024-07-16 09:42:53",
                        }
                    ]
                },
            }
        }
    )


@pytest.fixture
def mock_file_status(mocker):
    return mocker.patch.object(
        APIClient,
        "file_status",
        side_effect=[
            effect(0, 12345, "text_en_01"),
            effect(1, 12345, "text_en_01"),
            effect(2, 12345, "text_en_01"),
            effect(0, 67890, "text_en_02"),
            effect(1, 67890, "text_en_02"),
            effect(2, 67890, "text_en_02"),
        ],
    )


@pytest.fixture
def mock_get_file(mocker):
    return mocker.patch.object(
        APIClient, "get_file", side_effect=["case 1", "case 2", "case 3"]
    )


class TestFile:
    def test_wait_completion(self, mock_file_status):
        client = APIClient()
        for i, status in enumerate(client.wait_completion(12345, sleep=0.1)):
            if i == 0:
                assert status == "waiting"
            elif i == 1:
                assert status == "now translating"
            elif i == 2:
                assert status == ["text_en_01"]
            else:
                raise AssertionError("Unexpected status: {}".format(status))

        assert mock_file_status.call_count == 3

    def test_get_files(self, mock_get_file, mock_file_status, mocker):
        client = APIClient()
        files = client.get_files(
            [12345, 67890], sleep=0.1, output_dir="/tmp", extension="csv"
        )
        assert mock_get_file.call_count == 2
        assert mock_file_status.call_count == 6
        assert files == ["case 1", "case 2"]
        assert mock_get_file.call_args_list == [
            mocker.call(12345, path="/tmp/text_en_01.csv", encoding="utf-8"),
            mocker.call(67890, path="/tmp/text_en_02.csv", encoding="utf-8"),
        ]


@pytest.mark.slow
def test_translate_files(tmpdir):
    client = APIClient()
    files = ["tests/text_en.cfg", "tests/text_en02.txt"]
    res = client.translate_files(files, output_dir=tmpdir, extension="csv")
    new_file_1 = tmpdir.join("text_en.csv").read()
    new_file_2 = tmpdir.join("text_en02.csv").read()
    assert "ハイテク大手、革新的なAIツールを発表" in new_file_1
    assert "太陽光発電でグリーンエネルギーのマイルストーンを達成" in new_file_2
    assert res[0] == new_file_1
    assert res[1] == new_file_2
