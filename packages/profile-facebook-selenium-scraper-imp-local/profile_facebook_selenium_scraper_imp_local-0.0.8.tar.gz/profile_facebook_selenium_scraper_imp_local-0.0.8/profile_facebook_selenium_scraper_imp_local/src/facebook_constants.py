from logger_local.LoggerComponentEnum import LoggerComponentEnum


class FacebookLocalConstants:
    DEVELOPER_EMAIL = 'neomi.b@circ.zoce'
    PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_COMPONENT_ID = 245
    PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_COMPONENT_NAME = 'Profile facebook selenium scraper'
    PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL__CODE_LOGGER_OBJECT = {
        'component_id': PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_COMPONENT_ID,
        'component_name': PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': DEVELOPER_EMAIL
    }
    PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_TEST_LOGGER_OBJECT = {
        'component_id': PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_COMPONENT_ID,
        'component_name': PROFILE_FACEBOOK_SELENIUM_SCRAPER_IMP_LOCAL_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
        'developer_email': DEVELOPER_EMAIL
    }

    UNKNOWN_FACEBOOK_ID = 0
