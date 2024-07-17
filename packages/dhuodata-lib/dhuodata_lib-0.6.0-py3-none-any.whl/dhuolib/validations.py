from pydantic import BaseModel, Field


class ModelBody(BaseModel):
    modelname: str = Field(..., description="Model Name")
    tags: dict = Field(None, description="Tags")
    stage: str = Field(..., description="STAGING|PRODUCTION")
    run_id: str = Field(..., description="Run ID")
    model_uri: str = Field(None, description="Model URI")


class RunExperiment(BaseModel):
    type_model: str = Field(
        ..., description="RANDOM_FOREST|XGBOOST|LINEAR_REGRESSION|LOGISTIC_REGRESSION"
    )
    experiment_name: str = Field(..., description="Experiment Name")
    tags: dict = Field(None, description="Tags")


class RunFiles(BaseModel):
    modelpkl_path: str = Field(..., description="Path to model.pkl")
    requirements_path: str = Field(..., description="Path to requirements.txt")


class ExperimentBody(BaseModel):
    experiment_name: str = Field(..., description="Id")
    experiment_tags: dict = Field(None, description="Tags")


class PredictOnlineModelBody(BaseModel):
    run_id: str = Field(None, description="Run ID")
    modelname: str = Field(..., description="DEPENDENCY|PREDICT")
    stage: str = Field(..., description="STAGING|PRODUCTION")


class PredictBatchModelBody(BaseModel):
    run_id: str = Field(None, description="Run ID")
    modelname: str = Field(..., description="DEPENDENCY|PREDICT")
    stage: str = Field(..., description="STAGING|PRODUCTION")
    batch_model_dir: str = Field(..., description="Batch File")
    experiment_name: str = Field(..., description="Experiment Name")
    type_model: str = Field(
        ..., description="RANDOM_FOREST|XGBOOST|LINEAR_REGRESSION|LOGISTIC_REGRESSION"
    )


class ConnectModel(BaseModel):
    dialect_drive: str = Field(..., description="Dialect")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    host: str = Field(..., description="Host")
    port: str = Field(..., description="Port")
    service_name: str = Field(..., description="Service Name")


class TransitionModel(BaseModel):
    model_name: str = Field(..., description="Model Name")
    version: str = Field(..., description="Version")
    stage: str = Field(..., description="STAGING|PRODUCTION")


class RunSearch(BaseModel):
    filter_string: str = Field(None, description="Filter String")
    max_results: int = Field(None, description="Max Results")
    page_token: str = Field(None, description="Page Token")
    experiment_name: str = Field(..., description="Experiment Name")
