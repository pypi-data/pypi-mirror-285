"""
Based on the framework architecture which is CQRS, you are supposed to
import this setting into your main Django settings, so they could be
integrated and migrations of this framework will be recognized
"""

MIGRATION_MODULES = {
    'simple_media_manager': 'simple_media_manager.infrastructure.migrations',
}
