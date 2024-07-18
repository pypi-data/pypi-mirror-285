import looker_sdk
from looker_sdk.sdk.api40.methods import Looker40SDK
from looker_sdk import models40 as mdls
import pandas as pd
import json

class Connect:
    def __init__(self, looker_ini_path):
        self.sdk = self.make_sdk(looker_ini_path)

    def make_sdk(self, looker_ini_path):
        sdk: looker_sdk.Looker40SDK = looker_sdk.init40(looker_ini_path)
        return sdk

    def model_setting(self, model_name=None):
        response = self.sdk.update_lookml_model(
            lookml_model_name=model_name,
            body=mdls.WriteLookmlModel(
                unlimited_db_connections=False
            )
        )
        return response

class GetData:
    @staticmethod
    def get_query(sdk, model=None, view=None, sort_by=None, sort_type='', is_total=False, fields=None, pivots=None, fill_fields=None, filters=None, limit=500):
        query = mdls.WriteQuery(
            model=model,
            view=view,
            fields=fields,
            filters=filters,
            pivots = pivots,
            fill_fields = fill_fields,
            sorts=[f"{sort_by} {sort_type}"],
            limit=limit,
            total=is_total
        )
        response = sdk.create_query(body=query)
        query_id = response.id
        response_query = sdk.run_query(
            query_id=str(query_id),
            result_format="json"
        )
        data_json = json.loads(response_query)
        df = pd.DataFrame(data_json)
        return df

    @staticmethod
    def get_look(sdk, look_id, limit=500):
        response = sdk.run_look(look_id=str(look_id), result_format="json", limit=int(limit))
        data = json.loads(response)
        df = pd.DataFrame(data)
        return df