import http.client
import json
import logging
from typing import List, Optional

from ..models.dataset import DatasetEntry
from ..models.folder import Folder
from ..models.prompt import (Prompt, VersionAndRulesWithPromptId,
                             VersionsAndRules)


class MaximAPI:
    @staticmethod
    def __make_network_call(base_url: str, api_key: str, method: str, endpoint: str, body: Optional[str] = None) -> http.client.HTTPResponse:
        if base_url.startswith("http://"):
            conn = http.client.HTTPConnection(base_url.split("//")[1])
        else:
            conn = http.client.HTTPSConnection(base_url.split("//")[1])
        headers = {"x-maxim-api-key": api_key}
        conn.request(method, endpoint, body, headers)
        res = conn.getresponse()
        return res

    @staticmethod
    def getPrompt(base_url: str, api_key: str, id: str) -> VersionsAndRules:
        res = MaximAPI.__make_network_call(
            base_url, api_key, "GET", f"/api/sdk/v3/prompts?promptId={id}")
        if res.status != 200:
            raise Exception(
                f"Error while getting prompt: {res.status} - {res.reason}")
        data = res.read()
        logging.debug(data.decode())
        return VersionsAndRules(**json.loads(data.decode()))

    @staticmethod
    def getPrompts(base_url: str, api_key: str) -> List[VersionAndRulesWithPromptId]:
        res = MaximAPI.__make_network_call(
            base_url, api_key, "GET", "/api/sdk/v3/prompts")
        if res.status != 200:
            raise Exception(
                f"Error while getting prompts: {res.status} - {res.reason}")
        data = res.read()
        return [VersionAndRulesWithPromptId.from_dict(data) for data in json.loads(data)['data']]

    @staticmethod
    def getFolder(base_url: str, api_key: str, id: str) -> Folder:
        res = MaximAPI.__make_network_call(
            base_url, api_key, "GET", f"/api/sdk/v3/folders?folderId={id}")
        if res.status != 200:
            raise Exception(f"Error: {res.status} - {res.reason}")
        data = res.read()
        json_response = json.loads(data.decode())
        if 'tags' not in json_response:
            json_response['tags'] = {}
        return Folder(**json_response['data'])

    @staticmethod
    def getFolders(base_url: str, api_key: str) -> List[Folder]:
        res = MaximAPI.__make_network_call(
            base_url, api_key, "GET", "/api/sdk/v3/folders")
        if res.status != 200:
            raise Exception(f"Error: {res.status} - {res.reason}")
        data = res.read()
        json_response = json.loads(data.decode())
        for elem in json_response['data']:
            if 'tags' not in elem:
                elem['tags'] = {}
        return [Folder(**elem) for elem in json_response['data']]

    @staticmethod
    def addDatasetEntries(base_url: str, api_key: str, dataset_id: str, dataset_entries: List[DatasetEntry]) -> dict:
        res = MaximAPI.__make_network_call(base_url, api_key, "POST", "/api/sdk/v3/datasets/entries", json.dumps(
            {"datasetId": dataset_id, "entries": [entry.to_json() for entry in dataset_entries]}))
        if res.status != 200:
            raise Exception(f"Error: {res.status} - {res.reason}")
        response_data = res.read()
        return json.loads(response_data.decode())

    @staticmethod
    def doesLogRepositoryExist(base_url: str, api_key: str, logger_id: str) -> bool:
        try:
            res = MaximAPI.__make_network_call(
                base_url, api_key, "GET", f"/api/sdk/v3/log-repositories?loggerId={logger_id}")
            if res.status != 200:
                raise Exception(f"Error: {res.status} - {res.reason}")
            response_data = res.read()
            json_response = json.loads(response_data.decode())
            if 'error' in json_response:
                return False
            return True
        except Exception as e:
            return False

    @staticmethod
    def pushLogs(base_url: str, api_key: str, repository_id: str, logs: str) -> None:
        try:
            res = MaximAPI.__make_network_call(
                base_url, api_key, "POST", f"/api/sdk/v3/log?id={repository_id}", logs)
            if res.status != 200:
                raise Exception(f"Error: {res.status} - {res.reason}")
            response_data = res.read()
            json_response = json.loads(response_data.decode())
            if 'error' in json_response:
                raise Exception(json_response['error'])
        except Exception as e:
            raise Exception(e)
