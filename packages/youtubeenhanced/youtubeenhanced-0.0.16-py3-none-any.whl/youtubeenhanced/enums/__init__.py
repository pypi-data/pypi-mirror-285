from enum import Enum

class Constants(Enum):
    FILE_DURATION = 9999
    """
    This is the duration, as int value, that will be considered as
    the original video duration and will be used to set the original
    clip (that can be downloaded or load from local storage) duration
    as the final duration. This amount is just to be recognized and 
    will be replaced, when file processed, by the real duration.
    """

class Subtitles(Enum):
    TYPE_JSON3 = 'json3'
    TYPE_SRV1 = 'srv1'
    TYPE_SRV2 = 'srv2'
    TYPE_SRV3 = 'srv3'
    TYPE_TTML = 'ttml'
    TYPE_VTT = 'vtt'
    ALL_ACCEPTED = [
        TYPE_JSON3, TYPE_SRV1, TYPE_SRV2, TYPE_SRV3, TYPE_TTML, TYPE_VTT
    ]

class Language(Enum):
    # TODO: Set all existing languages
    ARABIC = 'ar'
    SPANISH = 'es'
    CHINESE_TRADITIONAL = 'zh-Hant'
    ENGLISH = 'en'
    FRENCH = 'fr'
    GERMAN = 'de'
    HINDI = 'hi'
    JAPANESE = 'ja'
    KOREAN = 'ko'
    PORTUGUESE = 'pt'
    RUSSIAN = 'ru'
    INDONESIAN = 'in'
    TURKISH = 'tr'
    VIETNAMESE = 'vi'
    DEFAULT = 'default'
    ALL_ACCEPTED = [
        ARABIC, SPANISH, CHINESE_TRADITIONAL, ENGLISH, FRENCH, GERMAN, HINDI, JAPANESE,
        KOREAN, PORTUGUESE, RUSSIAN, INDONESIAN, TURKISH, VIETNAMESE, DEFAULT
    ]

class Quality(Enum):
    ULTRA_HD = 2160
    QUAD_HD = 1440
    FULL_HD = 1080
    HD = 720
    SD = 480
    LOW = 360
    MINIMUM = 240
    DEFAULT = 1
    ALL_ACCEPTED = [
        ULTRA_HD, QUAD_HD, FULL_HD, HD, SD, LOW, MINIMUM, DEFAULT
    ]