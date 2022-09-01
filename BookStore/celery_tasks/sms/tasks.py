import uuid
import logging
from celery_tasks.sms.ccp_sms import CCP
from celery_tasks.main import celery_app


# 开启日志功能
logger = logging.getLogger('django')


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    # 发送验证码的函数

    try:
        __business_id = uuid.uuid1()
        result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    except Exception as ex:
        logger.error('发送验证码失败[异常][mobile:%s, message:%s]' % (mobile, ex))

    else:
        if not result:
            logger.info('发送验证码成功[正常][mobile:%s]' % mobile)
        else:
            logger.warning('发送验证码失败[接口问题][mobile:%s]' % mobile)
