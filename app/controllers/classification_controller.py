from app.config import TRAINING_FLOW
from app.services.database_service import AIModelInformationService, AIModelPerformanceService, CriticalNGService, CropCategorizingRecordService
from app.services.datasets_service import UnderkillDataProcessing
from app.services.inference_service import YOLOInference
from app.services.logging_service import Logger


class ClassificationController:
    def __init__(self) -> None:
        pass

    @classmethod
    def check_coutinue_train_classification_model(cls, project):
        Logger.info('Check Whether Train Classification Model')
        if 'classification' in TRAINING_FLOW[project]:
            return True
        else:
            return False

    @classmethod
    def get_finetune_type(cls, tablename):
        return tablename.split('_')[0].upper()
    
    @classmethod
    def check_underkills(cls, project, task_name):
        object_detection_underkills = UnderkillDataProcessing.get_object_detection_underkill_path(project, task_name)
        classification_underkills = UnderkillDataProcessing.get_classification_underkill_path(project, task_name)
        object_detection_validations = UnderkillDataProcessing.get_object_detection_validations(project, task_name)
        classification_validations = UnderkillDataProcessing.get_classification_validations(project, task_name)

        if object_detection_underkills and classification_underkills:
            ...
        elif object_detection_underkills:
            result = UnderkillDataProcessing.check_model_pass_or_fail(object_detection_underkills, object_detection_validations)
            return object_detection_underkills, result
        else:
            return [], True

        
    @classmethod
    def upload_crop_categorizing(cls, images, group_type, record_id, finetune_type):
        Logger.info('Upload Database Record Crop Categorizing')
        crop_image_ids = []
        for image_path in images:
            image_uuid = CriticalNGService.get_image_uuid(image_path, group_type)
            image = YOLOInference.read_image(image_path)
            image_size = YOLOInference.get_image_size(image)
            crop_image_id = CropCategorizingRecordService.update_underkill_image(record_id, image_uuid, image_size[0], image_size[1], finetune_type)
            crop_image_ids.append(crop_image_id)

        return crop_image_ids

    @classmethod
    def upload_ai_model_information(cls, model_path, record_id, finetune_type, group_type, model_validate_result): 
        Logger.info('Upload Database Record AI Model Information')
        ip_address = UnderkillDataProcessing.get_ip_address()
        if model_validate_result:
            verified_status = 'APPROVE'
        else:
            verified_status = 'FAIL'
        AIModelInformationService.update(group_type, model_path, ip_address, record_id, finetune_type, verified_status)
        model_id = AIModelInformationService.get_model_id()
        Logger.info(f'Model Path: {model_path}, Validate Result: {verified_status}')

        return model_id

    @classmethod
    def upload_ai_model_performance(cls, project, task_name, model_id, underkills, model_path, crop_image_ids, training_datasets_inferece_task_id):
        Logger.info('Upload Database Record AI Model Performance')
        if 'best.pt' in model_path:
            loss = UnderkillDataProcessing.get_loss(project, task_name)
            accuracy = UnderkillDataProcessing.get_accuracy(underkills, project)

        metrics_result = UnderkillDataProcessing.get_metrics_result(loss, accuracy, crop_image_ids, training_datasets_inferece_task_id)
        false_negative_images = UnderkillDataProcessing.get_false_negative_images(crop_image_ids)
        false_positive_images = UnderkillDataProcessing.get_false_positive_images()

        AIModelPerformanceService.update(model_id, metrics_result, false_negative_images, false_positive_images)
        