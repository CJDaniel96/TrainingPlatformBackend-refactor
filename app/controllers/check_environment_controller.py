from app.services.check_environment_service import CheckDatasetsEnvironment, CheckModelEnvironment, CheckTmpEnvironment, ClearLocalDataset
from app.services.logging_service import Logger


class CheckEnvironmentController:
    @classmethod
    def check_data_environment(cls):
        CheckTmpEnvironment.check_tmp_path()

        CheckDatasetsEnvironment.check_origin_datasets_path()
        CheckDatasetsEnvironment.check_object_detection_basicline_datasets_path()
        CheckDatasetsEnvironment.check_classification_basicline_datasets_path()
        CheckDatasetsEnvironment.check_object_detection_train_datasets_path()
        CheckDatasetsEnvironment.check_classification_train_datasets_path()
        CheckDatasetsEnvironment.check_object_detection_validation_datasets_path()
        CheckDatasetsEnvironment.check_classification_validation_datasets_path()
        CheckDatasetsEnvironment.check_object_detection_inference_datasets_path()
        CheckDatasetsEnvironment.check_classification_inference_datasets_path()
        CheckDatasetsEnvironment.check_object_detection_underkill_datasets_path()
        CheckDatasetsEnvironment.check_classification_underkill_datasets_path()
        CheckDatasetsEnvironment.check_yolo_train_yamls_path()

    @classmethod
    def check_model_environment(cls):
        CheckModelEnvironment.check_classification_inference_models_dir()
        CheckModelEnvironment.check_gan_inference_models_dir()
        CheckModelEnvironment.check_mobilenet_train_models_dir()
        CheckModelEnvironment.check_metric_learning_train_models_dir()
        CheckModelEnvironment.check_yolo_inference_models_dir()
        CheckModelEnvironment.check_yolo_train_models_dir()

    @classmethod
    def clear_local_data(cls, status, project, task_name):
        if status == 'OD_Initialized':
            Logger.warn('Clear object detecion local dataset!')
            ClearLocalDataset.clear_object_detection_local_dataset(project, task_name)
        elif status == 'CLS_Initialized':
            Logger.warn('Clear classification local dataset!')
            ClearLocalDataset.clear_classification_local_dataset(project, task_name)