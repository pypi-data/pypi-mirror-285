from snowflake.ml.dataset import Dataset
from fosforml.model_manager import snowflakesession as SnowflakeSession
import pandas as pd
import snowflake,json

class DatasetManager:
    def __init__(self,
                 model_name,
                 version_name,
                 session
                ):
        self.model_name = model_name
        self.version_name = version_name
        self.session_instance = SnowflakeSession()
        self.datasets_obj = self.get_or_create_dataset_object(model_name,version_name,session)
    
    def get_or_create_dataset_object(self,model_name,version_name,session):
        datasets_obj = Dataset(session=session,
                                database=self.session_instance.connection_params['database'],
                                schema =self.session_instance.connection_params['schema'],
                                name=f"{model_name}_{version_name}"
                                )
        try:
            datasets_obj.create(session=session,name=f"{model_name}_{version_name}")
        except Exception as e:
            datasets_obj.load(session=session,name=f"{model_name}_{version_name}")
        
        return datasets_obj
    
    def upload_datasets(self,session,datasets: dict):
        try:
            for dataset_name, dataset in datasets.items():
                if dataset is None:
                    continue
                snowpark_dataset = self.get_snowpark_dataset(session,dataset)
                purpose = self.get_dataset_purpose(dataset_name)
                self.datasets_obj.create_version(version=dataset_name,
                                                 input_dataframe=snowpark_dataset,
                                                 comment=json.dumps(
                                                            {
                                                                "purpose": purpose,
                                                                "dataset_type": "Table"
                                                            }
                                                        ))
                
            return True,f"Successfully uploaded {self.model_name} datasets."
        except Exception as e:
            print(e)
            raise Exception(e)
        
    def remove_datasets(self):
        try:
            self.datasets_obj.delete()
            return True,f"Successfully removed {self.model_name} datasets."
        except Exception as e:
            raise Exception(e)
    
    @staticmethod
    def get_dataset_purpose(dataset_name):
        if "x_train" in dataset_name.lower():
            return "Training"
        elif "y_train" in dataset_name.lower():
            return "Training"
        elif "x_test" in dataset_name.lower():
            return "Inference"
        elif "y_test" in dataset_name.lower():
            return "Inference"
        elif "y_pred" in dataset_name.lower():
            return "Validation"
        elif "prob" in dataset_name.lower():
            return "Validation"           
        
    def get_snowpark_dataset(self,session,dataset):
        if isinstance(dataset,snowflake.snowpark.dataframe.DataFrame):
            return dataset
        elif isinstance(dataset,pd.DataFrame):
            if dataset.empty:
                raise Exception("Empty dataframe provided. Please provide a non-empty dataframe.")
            return session.create_dataframe(dataset)
        elif isinstance(dataset,pd.Series):
            if dataset.empty:
                raise Exception("Empty series provided. Please provide a non-empty series.")
            return session.create_dataframe(dataset.to_list())
        else:
            raise Exception("Invalid dataset type. Please provide a pandas DataFrame or Series object.")    

class Metadata:
    def __init__(self, model_registry):
        self.model_registry = model_registry

    def update_model_registry(self,
                              model_name,
                              model_description,
                              model_tags,
                              session
                              ):
        try:
            model = self.model_registry.get_model(model_name=model_name)
            model.description = model_description
            self.set_model_tags(session,
                                model,
                                model_name,
                                tags=model_tags)
            return True, f"Successfully updated model metadata for {model_name}."
        except Exception as e:
            return False, f"Failed to update model metadata for {model_name}. {str(e)}"

    def set_model_tags(self,
                       session,
                       model,
                       model_name,
                       tags={}):
        try:
            for tag_name,tag_value in tags.items():
                session.sql(f"create tag if not exists {tag_name}").collect()
                model.set_tag(
                            tag_name = tag_name,
                            tag_value = tag_value
                            )
        except Exception as e:
            print(f"Failed to set tags for model {model_name}.")
            print(e)
            # raise Exception(f"Failed to set tags for model {model_name}")
        

    

