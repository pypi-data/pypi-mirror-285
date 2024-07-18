from snowflake.ml.registry import Registry
from .snowflakesession import snowflakesession as SnowflakeSession
from .utilities import DatasetManager, Metadata
from fosforml.utils import get_headers
from fosforml.constants import NotebooksAPI
from datetime import datetime
import json,requests,os
import pandas as pd
from fosforml.constants import ModelConstants
from fosforml.model_manager import snowflakesession

class ModelRegistry:
    def __init__(self,session):
        self.session_instance = SnowflakeSession()
        self.snowflake_session = session
        self.model_registry = Registry(session=self.snowflake_session, 
                                       database_name=self.session_instance.connection_params['database'],
                                       schema_name=self.session_instance.connection_params['schema']
                                       )
        self.models_info = self.model_registry.show_models()

    def register_model(self,
                       model,
                       score,
                       model_name,
                       dataset_name,
                       dataset_source,
                       description,
                       conda_dependencies,
                       model_flavour,
                       model_type,
                       sf_input_dataframe,
                       x_train,
                       y_train,
                       x_test,
                       y_test,
                       y_pred,
                       prob,
                       python_version,
                       source,
                       metadata,
                       prediction_column=None,
                       target_column=None
                       ):
        
        if score :
            return False, "score fuction not supported, implementation is in progress ..."

        versioning_errors, model_version = self.get_model_version(self.model_registry,model_name)
        if versioning_errors:
            return False,model_version
        
        metrics_errors,metrics = self.get_model_metrics(
                                        source=source,
                                        model=model,
                                        session=self.snowflake_session,
                                        metadata=metadata,
                                        model_type=model_type,
                                        model_flavour=model_flavour,
                                        x_train=x_train,
                                        y_train=y_train,
                                        x_test=x_test,
                                        y_test=y_test,
                                        y_pred=y_pred,
                                        prob=prob,
                                        sf_input_dataframe=sf_input_dataframe,
                                        dataset_source=dataset_source,
                                        dataset_name=dataset_name,
                                        prediction_column=prediction_column,
                                        target_column=target_column
                                        )
        if metrics_errors:
            return False,metrics

        metrics['python_version'] = python_version
        metrics['conda_dependencies'] = conda_dependencies
        metrics['algorithm_type'] = os.getenv('algorithm_type',None)
        metrics['algorithm'] = os.getenv('algorithm',None)
        metrics['experiment_name'] = os.getenv('experiment_name',None)
        metrics['run_id'] = os.getenv('run_id',None)
        metrics['experiment_id'] = os.getenv('experiment_id',None)
        metrics['flavour'] = model_flavour
        metrics['model_type'] = model_type

        ## register model

        try:
            self.model_registry.log_model(
                   model,
                   model_name=model_name,
                   version_name=model_version,
                   comment=description,
                   conda_dependencies=conda_dependencies,
                   metrics=metrics,
                   sample_input_data=sf_input_dataframe if model_flavour.lower() == "snowflake" else x_test,
                   python_version=python_version  
                  )
        except Exception as e:
            return False,f"Failed to register model '{model_name}'. {str(e)}"
        
        ## upload model datasets
        dataset_manager = DatasetManager(model_name=model_name,
                                         version_name=model_version,
                                         session=self.snowflake_session
                                         )
        ds_status,ds_message = dataset_manager.upload_datasets(
                                session=self.snowflake_session,
                                datasets={
                                        # "x_train": x_train,
                                        # "y_train": y_train,
                                        "x_test": x_test,
                                        "y_test": y_test,
                                        # "y_pred": y_pred,
                                        # "prob": prob
                                    })

        if not ds_status:
            return False,ds_message

        ## update model metadata
        metadata = Metadata(model_registry=self.model_registry)
        metadata_status,metadata_message = metadata.update_model_registry(
            session=self.snowflake_session,
            model_name=model_name,
            model_description=description,
            model_tags={
                "FLAVOR": model_flavour,
                "MODELTYPE": model_type,
                "CREATEDON" : metrics['created_on']
            }
        )

        if not metadata_status:
            return False,metadata_message
        
        return True,f"Model '{model_name}' registered successfully."

    def update_model_details(self,
                             model_name,
                             comments,
                             model_tags):
        metadata = Metadata(model_registry=self.model_registry)
        return metadata.update_model_registry(
            session=self.snowflake_session,
            model_name=model_name,
            model_description=comments,
            model_tags=model_tags
        )

    def get_model_details(self, model_name):
        pass

    def get_model_version(self, registry, model_name):
        model_info = pd.DataFrame(); models_data = pd.DataFrame()
        try:
            models_data = registry.show_models()       
        except Exception as e:
            return True,f"Failed to get model version. {str(e)}"
        
        if models_data.empty :
            return False,"v1"
                
        model_info = models_data[models_data['name']==model_name.upper()]

        if model_info.empty:
            return False,"v1"

        model_info = models_data[models_data['name']==model_name.upper()]
        model_versions = json.loads(model_info.versions.to_list()[0])
        if not model_versions:
            return False,"v1"
        else:
            last_version = max(model_versions,key=lambda x: int(x[1:]),default='v0')
            return False, f"v{int(last_version[1:])+1}"
    
    def get_model_metrics(self,
                          source,
                          model,
                          session,
                          metadata,
                          model_type,
                          model_flavour,
                          x_train=None,
                          y_train=None,
                          x_test=None,
                          y_test=None,
                          y_pred=None,
                          prob=None,
                          sf_input_dataframe=None,
                          dataset_source="",
                          dataset_name="",
                          prediction_column=None,
                          target_column=None
                            ):
        
        metrics = {}
        dataset_errors,model_dataset_details = self.get_dataset_details(
            model=model,session=session,
            model_flavour=model_flavour,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
            y_pred=y_pred,
            prob=prob,
            sf_input_dataframe=sf_input_dataframe,
            dataset_name=dataset_name,
            dataset_source=dataset_source,
            target_column=target_column,
            prediction_column=prediction_column,
            model_type=model_type
        )
        if dataset_errors:
            return True, model_dataset_details['message']
        
        metrics['dataset_details'] = model_dataset_details['ui_display'] if 'ui_display' in model_dataset_details else {}

        buildtime_metrics_errors,buildtime_metrics = self.get_model_performance_metrics(model,
                                                                      model_flavour,
                                                                      model_type,
                                                                      model_dataset_details
                                                                      )
        if buildtime_metrics_errors:
            return True,buildtime_metrics['message']
        
        metrics['model_metrics'] = buildtime_metrics

        metrics['hyper_parameters'] = model_dataset_details['hyper_parameters']

        source_errors,source_info = self.get_source_details(source)
        if source_errors:
            return True,source_info['message']

        metrics['created_on'] = session.sql("SELECT TO_CHAR(CURRENT_TIMESTAMP,'YYYY-MM-DD HH24:MI:SS')").to_pandas().squeeze()
        metrics['created_by'] = os.getenv('userId',None)
        metrics['status'] = source_info['status']
        metrics['source'] = source_info['source']
        if metrics['source'] == "NOTEBOOK":
            metrics['Repo_Details'] = source_info['repo_details']
        metrics['metadata'] = metadata if metadata else None

        return False, metrics

    def get_hyper_parameters(self,model):
        try:
            if str(type(model)).find("snowflake") > 0:
                return model.to_sklearn().get_params()
            else:
                return model.get_params()
        except Exception as e:
            return f"Failed to get hyper parameters. {str(e)}"

    def get_model_performance_metrics(self,model,
                                      model_flavour,
                                      model_type,
                                      model_dataset_details
                                      ):
        try:
            sf_true_cn = [] ; sf_pred_cn = [] ; sf_pred_proba_cn = [] 
            sf_input_cols = model_dataset_details['metadata']['feature_names']
            if model_flavour.lower() == ModelConstants.sklearn_model_flavour and str(type(model)).find(ModelConstants.sklearn_model_flavour) > 0:
                

                for col in model_dataset_details['final_df'].columns:
                    if col[1:-1].lower() == model_dataset_details['metadata']['target_column'][0].lower():
                        sf_true_cn.append(col)

                    if col[1:-1].lower() == model_dataset_details['metadata']['prediction_column'][0].lower():
                        sf_pred_cn.append(col)
                    
                    if col in model_dataset_details['metadata']['prob_columns']:
                        sf_pred_proba_cn.append(col)
                    else:
                        for prob_col in model_dataset_details['metadata']['prob_columns']:
                            if prob_col in col:
                                sf_pred_proba_cn.append(col)
                                
                                            
            else:
                sf_true_cn = model_dataset_details['metadata']['target_column']
                sf_pred_cn = model_dataset_details['metadata']['prediction_column']
                sf_pred_proba_cn = model_dataset_details['metadata']['prob_columns']

            if sf_true_cn is None or sf_pred_cn is None :
                return True, {"message": "Failed to get 'target_column' and 'prediction_column'."}

            if model_type.lower() == "classification":
                from fosforml.model_manager.model_metrics import Classification
                classification_metrics = Classification(
                    model_obj=model_dataset_details['model_obj'],
                    sf_df=model_dataset_details['final_df'],
                    true_cn=sf_true_cn,
                    pred_cn=sf_pred_cn,
                    pred_proba_cn=sf_pred_proba_cn,
                    sf_input_cols=sf_input_cols
                )
                return False, classification_metrics.get_metrics()
            
            if model_type.lower() == "regression":
                from fosforml.model_manager.model_metrics import Regression
                regression_metrics = Regression(
                                                model=model_dataset_details['model_obj'],
                                                sf_df=model_dataset_details['final_df'], 
                                                true_cn=sf_true_cn,
                                                pred_cn=sf_pred_cn,
                                                pred_proba_cn=sf_pred_proba_cn,
                                                sf_input_cols=sf_input_cols
                                                )
                return False, regression_metrics.get_metrics()
            
            else:
                return True,{"message": "Invalid model type, please provide valid model type as classification or regression"} 
            
        except Exception as msg:
            raise Exception(f"Failed to get model performance metrics. {str(msg)}")
            # return True, {"message": f"Failed to get model performance metrics. {str(msg)}"}
        
        # dummy_data = [{'tag': 'feature_importance', 'model_metric_value': [{'column_name': 'DEPARTMENT', 'importance': 0.14061672606947828}, {'column_name': 'SATISFACTION_LEVEL', 'importance': 0.1104329386548882}, {'column_name': 'LAST_EVALUATION', 'importance': 0.1350624049528422}, {'column_name': 'NUMBER_PROJECT', 'importance': 0.04248402957988852}, {'column_name': 'AVERAGE_MONTLY_HOURS', 'importance': 0.2118735496815215}, {'column_name': 'TIME_SPEND_COMPANY', 'importance': 0.10658202765565672}, {'column_name': 'WORK_ACCIDENT', 'importance': 0.010641980974635002}, {'column_name': 'LEFT', 'importance': 0.16529938539291036}, {'column_name': 'PROMOTION_LAST_5YEARS', 'importance': 0.0770069570381792}]}, {'tag': 'confusion_matrix', 'model_metric_value': [{'column_1_counter': 0, 'column_2_counter': 0, 'prediction': 1404.0, 'column_1': 0, 'column_2': 0}, {'column_1_counter': 0, 'column_2_counter': 1, 'prediction': 380.0, 'column_1': 0, 'column_2': 1}, {'column_1_counter': 1, 'column_2_counter': 0, 'prediction': 1129.0, 'column_1': 1, 'column_2': 0}, {'column_1_counter': 1, 'column_2_counter': 1, 'prediction': 483.0, 'column_1': 1, 'column_2': 1}]}, {'tag': 'detailed_matrix', 'model_metric_value': {'accuracy_score': 0.555654, 'precision_score': 0.5596755504055619, 'recall_score': 0.29962779156327546, 'f1_score': 0.3903030303030303, 'log_loss': 16.01586365258474, 'roc_auc_score': 0.5433116536291713}}, {'tag': 'roc_auc', 'model_metric_value': {'fpr': [0.0, 0.21300448430493274, 1.0], 'tpr': [0.0, 0.29962779156327546, 1.0], 'data': 0.5433116536291713}}]
        # return "dummy_data"
    
    def get_source_details(self,source):
        source_info = {}
        if source is None or source == "":
            source_info['status'] = "Registered"
            source_info['source'] = "NOTEBOOK"
            source_info['repo_details'] = self.get_repo_details()

        elif source is not None and  source.upper() == "EXPERIMENT":
            source_info['status'] = "Experimented"
            source_info['source'] = "EXPERIMENT"

        elif source is not None and source.upper() == "BYOM":
            source_info['status'] = "Deploying"
            source_info['source'] = "BYOM"
            
        elif source is not None and source.upper() == "NOTEBOOK" :
            source_info['status'] = "Registered"
            source_info['source'] = "NOTEBOOK"
            source_info['repo_details'] = self.get_repo_details()    
        else:
            return True, {"message": f"Invalid source. Please provide valid source as Experiment, BYOM or Notebook."}

        return False,source_info

    def get_repo_details(self):
        from fosforml.constants import UserConfigs
        repo_key = UserConfigs.repo_key
        repo_details = []
        
        try:
            if repo_key.lower() in os.environ or repo_key.upper() in os.environ:
                repo_details = os.environ.get(repo_key,'[]')
                return json.loads(repo_details.replace("\\",""))
            else:
                url = NotebooksAPI.notebooks_api_server_url + NotebooksAPI.git_repo
                headers = get_headers()
                response = requests.get(url, headers=headers).json()
                return response
        except Exception as e:
            return repo_details

    def get_dataset_details(self,model,
            session,
            model_flavour,
            x_train=None,
            y_train=None,
            x_test=None,
            y_test=None,
            y_pred=None,
            prob=None,
            sf_input_dataframe=None,
            dataset_name="",
            dataset_source="",
            target_column=None,
            prediction_column=None,
            model_type=None):
        

        dataset_details = {}
        dataset_metadata = {}
        dataset_ui_display = []
        purpose = DatasetManager.get_dataset_purpose
        connection_params = snowflakesession().connection_params
        if model_flavour.lower() == "snowflake" and str(type(model)).find("snowflake") > 0:
            try:

                if not hasattr(model,"label_cols") and target_column is None:
                   return True, {"message": f"Failed to register model, 'target_column' is required to register the model ."}
                
                if not hasattr(model,"output_cols") and prediction_column is None:
                   return True, {"message": f"Failed to register model, 'prediction_column' is required to register the model ."}
                
                if len(model.label_cols) < 1 and target_column is None:
                   return True, {"message": f"Failed to register model, 'target_column' is required to register the model ."}
                
                if len(model.output_cols) < 1 and prediction_column is None:
                   return True, {"message": f"Failed to register model, 'prediction_column' is required to register the model ."}


                dataset_metadata['feature_names'] = model.input_cols if hasattr(model,"input_cols") else []
                dataset_metadata['target_column'] = model.label_cols if all([hasattr(model,"label_cols"),len(model.label_cols)>0]) else [target_column]
                dataset_metadata['prediction_column'] = model.output_cols if all([hasattr(model,"output_cols"),len(model.output_cols)>0]) else [prediction_column]

                from fosforml.utils import load_model_artifacts
                try:
                    model_artifacts = load_model_artifacts(
                                                        session=session,
                                                        model_type=model_type,
                                                        model_obj=model,
                                                        snowflake_model=True,
                                                        snowflake_df=sf_input_dataframe
                                                        )
                except Exception as msg:
                    # return True, {"message": f"Failed to load model artifacts. {str(msg)}"}
                    raise Exception(f"Failed to load model artifacts. {str(msg)}")

                prob_columns =[]
                try:
                    prob_columns = list(
                    set(sf_input_dataframe.columns) - set(dataset_metadata['feature_names']) -set(dataset_metadata['target_column']) - set(dataset_metadata['prediction_column'])
                )
                except:
                    pass
                dataset_metadata['prob_columns'] = prob_columns
                    
                
                dataset_details['final_df'] = model_artifacts['final_df']
                dataset_details['hyper_parameters'] = model_artifacts['hyper_parameters']
                dataset_details['model_obj'] = model_artifacts['model_obj']

                temp_ui_data = {
                'dataset_type' : 'Dataset',
                'purpose' : 'Traning',
                'source' : dataset_source,
                'database': connection_params['database'],
                'schema': connection_params['schema'],
                'dataset_name': f'{dataset_name}_snowflake_training_dataset',
                'target_column': dataset_metadata['target_column'][0]
            }   
                dataset_ui_display.append(temp_ui_data)

                
            except Exception as msg:
                print(msg)
                return True, {"message": f"Failed to fetch dataset details from snowflake."}

        elif model_flavour.lower() == "sklearn" and str(type(model)).find("sklearn") > 0:
            try:
                dataset_metadata['feature_names'] = x_test.columns.to_list()
                dataset_metadata['target_column'] = [y_test.squeeze().name] if isinstance(y_train,pd.DataFrame) else [y_test.name]
                dataset_metadata['prediction_column'] = [y_pred.squeeze().name] if isinstance(y_pred,pd.DataFrame) else [y_train.name]
                if isinstance(prob,pd.DataFrame):
                    dataset_metadata['prob_columns'] = prob.columns.to_list()
                else:
                    dataset_metadata['prob_columns'] = []
                
                if x_train is not None:
                    x_train_data = {
                        'dataset_type' : 'Dataset',
                        'purpose' : purpose('x_train'),
                        'source' : dataset_source,
                        'database': connection_params['database'],
                        'schema': connection_params['schema'],
                        'dataset_name': f'{dataset_name}_x_train',
                    }
                    dataset_ui_display.append(x_train_data)

                if y_train is not None:
                    y_train_data = {
                        'dataset_type' : 'Dataset',
                        'purpose' : purpose('y_train'),
                        'source' : dataset_source,
                        'database': connection_params['database'],
                        'schema': connection_params['schema'],
                        'dataset_name': f'{dataset_name}_y_train',
                        'target_column': dataset_metadata['target_column'][0]
                    }
                    dataset_ui_display.append(y_train_data)

                if x_test is not None:
                    x_test_data = {
                        'dataset_type' : 'Dataset',
                        'purpose' : purpose('x_test'),
                        'source' : dataset_source,
                        'database': connection_params['database'],
                        'schema': connection_params['schema'],
                        'dataset_name': f'{dataset_name}_x_test'
                    }
                    dataset_ui_display.append(x_test_data)

                if y_test is not None:
                    y_test_data = {
                        'dataset_type' : 'Dataset',
                        'purpose' : purpose('y_test'),
                        'source' : dataset_source,
                        'database': connection_params['database'],
                        'schema': connection_params['schema'],
                        'dataset_name': f'{dataset_name}_y_test',
                        'target_column': dataset_metadata['target_column'][0]
                    }
                    dataset_ui_display.append(y_test_data)

                if y_pred is not None:
                    y_pred_data = {
                        'dataset_type' : 'Dataset',
                        'purpose' : purpose('y_pred'),
                        'source' : dataset_source,
                        'database': connection_params['database'],
                        'schema': connection_params['schema'],
                        'dataset_name': f'{dataset_name}_y_pred',
                        'pred_column': dataset_metadata['prediction_column'][0]
                    }
                    dataset_ui_display.append(y_pred_data)

                if prob is not None:
                    prob_data = {
                        'dataset_type' : 'Dataset',
                        'purpose' : purpose('prob'),
                        'source' : dataset_source,
                        'database': connection_params['database'],
                        'schema': connection_params['schema'],
                        'dataset_name': f'{dataset_name}_prob',
                        'prob_columns': dataset_metadata['prob_columns']
                    }
                    dataset_ui_display.append(prob_data)

                from fosforml.utils import load_model_artifacts
                try:
                    model_artifacts = load_model_artifacts(
                                                        session=session,
                                                        model_type=model_type,
                                                        model_obj=model,
                                                        snowflake_model=False,
                                                        x_test=x_test,
                                                        y_test=y_test,
                                                        y_pred=y_pred,
                                                        y_prob=prob
                                                        )
                except Exception as msg:
                    return True, {"message": f"Failed to load model artifacts. {str(msg)}"}
                    # raise Exception(f"Failed to load model artifacts. {str(msg)}")
                    
                dataset_details['final_df'] = model_artifacts['final_df']
                dataset_details['hyper_parameters'] = model_artifacts['hyper_parameters']
                dataset_details['model_obj'] = model_artifacts['model_obj']

            except Exception as msg:
                return True, {"message": f"Failed to get dataset details. {str(msg)}"}
                # raise Exception(f"Failed to get dataset details. {str(msg)}")  
        
        dataset_details['metadata'] = dataset_metadata
        dataset_details['ui_display'] = dataset_ui_display
        dataset_details['message'] = "Dataset details fetched successfully."
        
        return False,dataset_details


    def get_validation_df(self,df,no_rows):
        if df is not None and not df.empty:
            if isinstance(df,pd.DataFrame):
                return df.reset_index(drop=True).iloc[:no_rows,:]
            if isinstance(df,pd.Series):
                return df.to_frame().reset_index(drop=True).iloc[:no_rows,:]

