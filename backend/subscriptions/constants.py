from dataclasses import dataclass


class Feature:
    DOCUMENT_GENERATION = 'document_generation'
    DOCUMENT_EXPORT = 'document_export'
    COMPETITOR_INTELLIGENCE = 'competitor_intelligence'
    TEAM_COLLABORATION = 'team_collaboration'
    ADVANCED_AUDIT = 'advanced_audit'

    ALL = (
        DOCUMENT_GENERATION,
        DOCUMENT_EXPORT,
        COMPETITOR_INTELLIGENCE,
        TEAM_COLLABORATION,
        ADVANCED_AUDIT,
    )


class CompanyRole:
    OWNER = 'owner'
    MANAGER = 'manager'
    ANALYST = 'analyst'
    VIEWER = 'viewer'


@dataclass(frozen=True)
class FeaturePolicy:
    required_plan: str
    allowed_roles: tuple[str, ...]
    requires_stir: bool = False


FEATURE_POLICIES = {
    Feature.DOCUMENT_GENERATION: FeaturePolicy(
        required_plan='business',
        allowed_roles=(CompanyRole.OWNER, CompanyRole.MANAGER),
        requires_stir=True,
    ),
    Feature.DOCUMENT_EXPORT: FeaturePolicy(
        required_plan='business',
        allowed_roles=(CompanyRole.OWNER, CompanyRole.MANAGER),
        requires_stir=True,
    ),
    Feature.COMPETITOR_INTELLIGENCE: FeaturePolicy(
        required_plan='business',
        allowed_roles=(
            CompanyRole.OWNER,
            CompanyRole.MANAGER,
            CompanyRole.ANALYST,
        ),
    ),
    Feature.TEAM_COLLABORATION: FeaturePolicy(
        required_plan='business',
        allowed_roles=(CompanyRole.OWNER, CompanyRole.MANAGER),
    ),
    Feature.ADVANCED_AUDIT: FeaturePolicy(
        required_plan='enterprise',
        allowed_roles=(CompanyRole.OWNER,),
    ),
}


METRIC_LIMIT_KEYS = {
    'ai_analysis': 'ai_analysis_monthly',
    'document_generation': 'document_generation_monthly',
    'document_export': 'document_export_monthly',
    'competitor_query': 'competitor_query_monthly',
}
