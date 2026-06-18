from controlplane.models import FeatureFlag


def get_feature_flag(feature):
    flag, _ = FeatureFlag.objects.get_or_create(feature=feature)
    return flag


def feature_is_enabled(feature):
    flag = FeatureFlag.objects.filter(feature=feature).first()
    if flag is None:
        return True, ''
    return flag.is_enabled, flag.reason
