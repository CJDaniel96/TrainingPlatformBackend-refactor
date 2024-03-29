from datetime import timedelta
import json
import os
import random
import uuid
from app.config import IMAGE_POOL_DOWNLOAD_PREFIX, IMAGES_ASSIGN_LIGHT_TYPE, RECORD_STATUSES, SITE, SMART_FILTER_NUMBER
from app.services.logging_service import Logger
from data.config import DATABASES
from data.database.ai import AiModelInfo, AiModelPerf, CLSTrainingInfo, CategoryMapping, CriticalNg, CropCategorizingRecord, ImagePool, IriRecord, ODTrainingInfo, UploadData, UrdRecord
from data.database.amr_info import AmrRawData
from data.database.sessions import create_session


AI_DATABASE = DATABASES['ai']['DATABASE']
AMR_INFO_DATABASE = DATABASES['amr_info']['DATABASE']
CVAT_DATABASE = DATABASES['cvat']['DATABASE']


class IRIRecordService:
    @classmethod
    def status(cls):
        with create_session(AI_DATABASE) as session:
            return session.query(IriRecord).filter(
                IriRecord.status.in_(RECORD_STATUSES['IRI'])
            ).order_by(IriRecord.update_time).first()

    @classmethod
    def update_line(cls, id, lines):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                'line': repr(lines).replace('\'', '"')
            })
            session.commit()

    @classmethod
    def update_site(cls, id):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                'site': SITE
            })
            session.commit()

    @classmethod
    def update_status(cls, id, status):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                "status": status
            })
            session.commit()

    @classmethod
    def update_task_id(cls, id, task_id):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                "task_id": task_id
            })
            session.commit()

    @classmethod
    def update_task_name(cls, id, task_name):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                "task": task_name
            })
            session.commit()

    @classmethod
    def update_od_training_status(cls, id, od_training_status):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                "od_training": od_training_status
            })
            session.commit()

    @classmethod
    def update_cls_training_status(cls, id, cls_training_status):
        with create_session(AI_DATABASE) as session:
            session.query(IriRecord).filter(IriRecord.id == id).update({
                "cls_training": cls_training_status
            })
            session.commit()

    @classmethod
    def get_tasks(cls, tasks_id):
        with create_session(AI_DATABASE) as session:
            data = session.query(IriRecord).filter(
                IriRecord.task_id.in_(tasks_id)
            ).all()
        
        return [[obj.task_id, obj.task] for obj in data]


class URDRecordService:
    @classmethod
    def status(cls):
        with create_session(AI_DATABASE) as session:
            return session.query(UrdRecord).filter(
                UrdRecord.status.in_(RECORD_STATUSES['URD'])
            ).order_by(UrdRecord.update_time).first()

    @classmethod
    def update_line(cls, id, lines):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                'line': repr(lines).replace('\'', '"')
            })
            session.commit()

    @classmethod
    def update_site(cls, id):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                'site': SITE
            })
            session.commit()

    @classmethod
    def update_status(cls, id, status):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                "status": status
            })
            session.commit()

    @classmethod
    def update_task_id(cls, id, task_id):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                "task_id": task_id
            })
            session.commit()

    @classmethod
    def update_task_name(cls, id, task_name):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                "task": task_name
            })
            session.commit()

    @classmethod
    def update_od_training_status(cls, id, od_training_status):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                "od_training": od_training_status
            })
            session.commit()

    @classmethod
    def update_cls_training_status(cls, id, cls_training_status):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                "cls_training": cls_training_status
            })
            session.commit()

    @classmethod
    def get_tasks(cls, tasks_id):
        with create_session(AI_DATABASE) as session:
            data = session.query(UrdRecord).filter(
                UrdRecord.task_id.in_(tasks_id)
            ).all()
        
        return [[obj.task_id, obj.task] for obj in data]

    @classmethod
    def update_category_ready(cls, id):
        with create_session(AI_DATABASE) as session:
            session.query(UrdRecord).filter(UrdRecord.id == id).update({
                "category_ready": True
            })
            session.commit()


class ImagePoolService:
    def smart_filter_images(self, images):
        buffer = []
        dataset = {}
        for line in images:
            for data in images[line]:
                buffer.append([line, data])

        random.shuffle(buffer)

        for data in buffer[:SMART_FILTER_NUMBER]:
            if data[0] not in dataset:
                dataset[data[0]] = [data[1]]
            else:
                dataset[data[0]].append(data[1])

        return dataset

    @classmethod
    def get_images(cls):...

    @classmethod
    def get_image_pool(cls):
        with create_session(AI_DATABASE) as session:
            return session.query(ImagePool).all()


class ImageDataService(ImagePoolService):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def check_assign_image_light_type(cls, site, group_type):
        if site in IMAGES_ASSIGN_LIGHT_TYPE and group_type in IMAGES_ASSIGN_LIGHT_TYPE[site]:
            return True
        else:
            return False

    @classmethod
    def get_image_by_assign_light_type(cls, site, line, group_type, start_date, end_date, smart_filter=False, is_covered=True, ai_result='0'):
        Logger.info('Get Images UUID by assign light type from query data')
        images = {}
        with create_session(AMR_INFO_DATABASE) as session:
            end_date += timedelta(days=1)
            for each_line in eval(line):
                data = session.query(AmrRawData.image_path).filter(
                    AmrRawData.site == site,
                    AmrRawData.line_id == each_line,
                    AmrRawData.image_name.like(f'%{IMAGES_ASSIGN_LIGHT_TYPE[site][group_type]}%'),
                    AmrRawData.group_type == group_type,
                    AmrRawData.create_time.between(start_date, end_date),
                    AmrRawData.is_covered == is_covered,
                    AmrRawData.ai_result == ai_result
                ).all()

                images[each_line] = [each_line + '/' + obj.image_path for obj in data]

            if smart_filter:
                images = cls().smart_filter_images(images)

            return images

    @classmethod
    def get_images(cls, site, line, group_type, start_date, end_date, smart_filter=False, is_covered=True, ai_result='0'):
        Logger.info('Get Images UUID from query data')
        images = {}
        with create_session(AMR_INFO_DATABASE) as session:
            end_date += timedelta(days=1)
            for each_line in eval(line):
                data = session.query(AmrRawData.image_path).filter(
                    AmrRawData.site == site,
                    AmrRawData.line_id == each_line,
                    AmrRawData.group_type == group_type,
                    AmrRawData.create_time.between(start_date, end_date),
                    AmrRawData.is_covered == is_covered,
                    AmrRawData.ai_result == ai_result
                ).all()

                images[each_line] = [each_line + '/' + obj.image_path for obj in data]

            if smart_filter:
                images = cls().smart_filter_images(images)

            return images

    @classmethod
    def get_image_uuid(cls, image):
        image_name = os.path.basename(image)
        date_time = image_name.split('_')[0]
        date = date_time[:4] + '-' + date_time[4:6] + '-' + date_time[6:8]
        image_path = f'{date}/{date_time}/{image_name}'

        with create_session(AMR_INFO_DATABASE) as session:
            data = session.query(AmrRawData.uuid).filter(AmrRawData.image_path == image_path).first()

        return data.uuid


class UploadDataService(ImagePoolService):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_images(self, uuids):
        Logger.info('Get Images UUID from upload data')
        images = {}
        with create_session(AMR_INFO_DATABASE) as session:
            data = session.query(AmrRawData).filter(AmrRawData.uuid.in_(eval(uuids))).all()
            for obj in data:
                if obj.line_id not in images:
                    images[obj.line_id] = [IMAGE_POOL_DOWNLOAD_PREFIX + '/' + obj.line_id + '/' + obj.image_path]
                else:
                    images[obj.line_id].append(IMAGE_POOL_DOWNLOAD_PREFIX + '/' + obj.line_id + '/' + obj.image_path)

            return images


class UploadImageDataService(ImagePoolService):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_images(self, uuids, line='upload_image'):
        Logger.info('Get Images UUID from upload images data')
        images = {}
        with create_session(AI_DATABASE) as session:
            data = session.query(UploadData).filter(UploadData.uuid.in_(eval(uuids))).all()
            image_pool = session.query(ImagePool.prefix).filter(ImagePool.line == line).first()
            for obj in data:
                if obj.line_id not in images:
                    images[obj.line_id] = [IMAGE_POOL_DOWNLOAD_PREFIX + '/' + image_pool.prefix + '/' + obj.image_path]
                else:
                    images[obj.line_id].append(IMAGE_POOL_DOWNLOAD_PREFIX + '/' + image_pool.prefix + '/' + obj.image_path)

            return images
        

class TrainingInfoService:
    def __init__(self) -> None:
        pass

    @classmethod
    def get_object_detection_tasks_id(cls, task_id, comp_type, val_status='APPROVE'):
        with create_session(AI_DATABASE) as session:
            data = session.query(ODTrainingInfo).filter(
                ODTrainingInfo.task_id < task_id,
                ODTrainingInfo.comp_type == comp_type,
                ODTrainingInfo.val_status == val_status
            ).all()

        return [obj.task_id for obj in data]
        
    @classmethod
    def get_classification_tasks_id(cls, task_id, comp_type, val_status='APPROVE'):
        with create_session(AI_DATABASE) as session:
            data = session.query(CLSTrainingInfo).filter(
                CLSTrainingInfo.task_id < task_id,
                CLSTrainingInfo.comp_type == comp_type,
                CLSTrainingInfo.val_status == val_status
            ).all()

        return [obj.task_id for obj in data]
    
    @classmethod
    def get_object_detection_model_version(cls, comp_type, val_status):
        with create_session(AI_DATABASE) as session:
            data = session.query(ODTrainingInfo).filter(
                ODTrainingInfo.comp_type == comp_type,
                ODTrainingInfo.val_status == val_status
            ).order_by(ODTrainingInfo.model_version.desc()).first()

        if data:
            return data.model_version
        else:
            return '0'

    @classmethod
    def get_classification_model_version(cls, comp_type, val_status):
        with create_session(AI_DATABASE) as session:
            data = session.query(CLSTrainingInfo).filter(
                CLSTrainingInfo.comp_type == comp_type,
                CLSTrainingInfo.val_status == val_status
            ).order_by(CLSTrainingInfo.model_version.desc()).first()

        if data:
            return data.model_version
        else:
            return '0'
        
    @classmethod
    def insert_object_detection_result(cls, task_id, comp_type, val_status, model_version): 
        with create_session(AI_DATABASE) as session:
            session.add(ODTrainingInfo(
                task_id=task_id,
                comp_type=comp_type,
                val_status=val_status,
                model_version=model_version
            ))
            session.commit()

    @classmethod
    def insert_classification_result(cls, task_id, comp_type, val_status, model_version):
        with create_session(AI_DATABASE) as session:
            session.add(CLSTrainingInfo(
                task_id=task_id,
                comp_type=comp_type,
                val_status=val_status,
                model_version=model_version
            ))
            session.commit()


class CategoryMappingService:
    def __init__(self) -> None:
        pass

    @classmethod
    def get_class_names(cls, site, group_type, project):
        with create_session(AI_DATABASE) as session:
            data = session.query(CategoryMapping.labels).filter(
                CategoryMapping.site == site,
                CategoryMapping.group_type == group_type,
                CategoryMapping.project == project
            ).first()

        labels = eval(data.labels)

        return list(labels.keys())

    @classmethod
    def get_class_dict(cls, site, group_type, project):
        with create_session(AI_DATABASE) as session:
            data = session.query(CategoryMapping.labels).filter(
                CategoryMapping.site == site,
                CategoryMapping.group_type == group_type,
                CategoryMapping.project == project
            ).first()

        labels = eval(data.labels)

        return labels

    @classmethod
    def get_ok_category(cls, site, group_type, project):
        with create_session(AI_DATABASE) as session:
            data = session.query(CategoryMapping.ok_category).filter(
                CategoryMapping.site == site,
                CategoryMapping.group_type == group_type,
                CategoryMapping.project == project
            ).first()

        labels = eval(data.ok_category)

        return labels


class CropCategorizingRecordService:
    def __init__(self) -> None:
        pass

    @classmethod
    def update_underkill_image(cls, finetune_id, image_id, image_hight, image_wide, finetune_type, categorizing_code='OK', crop_name='ORG', critical_ng=True):
        try:
            with create_session(AI_DATABASE) as session:
                session.add(CropCategorizingRecord(
                    finetune_id=finetune_id, 
                    img_id=image_id, 
                    crop_name=crop_name,
                    x_min=0,
                    y_min=0,
                    x_max=image_wide,
                    y_max=image_hight,
                    categorizing_code=categorizing_code,
                    finetune_type=finetune_type,
                    critical_ng=critical_ng
                ))
                session.commit()

            return finetune_type + '@' + str(finetune_id) + '@' + image_id + '@' + crop_name
        except:
            return


class CriticalNGService:
    def __init__(self) -> None:
        pass

    @classmethod
    def get_image_uuid(cls, image, group_type, crop_name='ORG'):
        image_path = f'{group_type}/{crop_name}/{os.path.basename(image)}'
        with create_session(AI_DATABASE) as session:
            data = session.query(CriticalNg.img_id).filter(CriticalNg.image_path == image_path).first()

        return data.img_id

    @classmethod
    def insert_new_images(cls, group_type, image_path, crop_name='ORG'):
        image_path = f'{group_type}/{crop_name}/{os.path.basename(image_path)}'
        with create_session(AI_DATABASE) as session:
            session.add(CriticalNg(
                img_id=uuid.uuid4(), 
                image_path=image_path, 
                group_type=group_type
            ))
            session.commit()
    
    @classmethod
    def delete_images_by_group_type(cls, group_type):
        with create_session(AI_DATABASE) as session:
            session.query(CriticalNg).filter(CriticalNg.group_type == group_type).delete()
            session.commit()


class AIModelInformationService:
    def __init__(self) -> None:
        pass

    @classmethod
    def update(cls, group_type, model_path, ip_address, finetune_id, finetune_type, verified_status, crop_name='ORG'):
        with create_session(AI_DATABASE) as session:
            session.add(AiModelInfo(
                model_type=group_type,
                model_name=crop_name,
                model_path=f'{ip_address}//{os.path.abspath(model_path)}',
                verified_status=verified_status,
                finetune_id=finetune_id,
                finetune_type=finetune_type
            ))
            session.commit()

    @classmethod
    def get_model_id(cls):
        with create_session(AI_DATABASE) as session:
            data = session.query(AiModelInfo.model_id).order_by(AiModelInfo.model_id.desc()).first()

        return data.model_id
        

class AIModelPerformanceService:
    def __init__(self) -> None:
        pass

    @classmethod
    def update(cls, model_id, metrics_result, false_negative_images, false_positive_images):
        with create_session(AI_DATABASE) as session:
            session.add(AiModelPerf(
                model_id=model_id,
                metrics_result=json.dumps(metrics_result),
                false_negative_imgs=json.dumps(false_negative_images),
                false_positive_imgs=json.dumps(false_positive_images)
            ))
            session.commit()