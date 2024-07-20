from ovos_plugin_manager.templates.embeddings import EmbeddingsDB, FaceEmbeddingsRecognizer, VoiceEmbeddingsRecognizer
from ovos_plugin_manager.utils import PluginTypes


def find_embeddings_plugins() -> dict:
    """
    Find all installed plugins
    @return: dict plugin names to entrypoints
    """
    from ovos_plugin_manager.utils import find_plugins
    return find_plugins(PluginTypes.EMBEDDINGS)


def load_embeddings_plugin(module_name: str) -> type(EmbeddingsDB):
    """
    Get an uninstantiated class for the requested module_name
    @param module_name: Plugin entrypoint name to load
    @return: Uninstantiated class
    """
    from ovos_plugin_manager.utils import load_plugin
    return load_plugin(module_name, PluginTypes.EMBEDDINGS)


def find_voice_embeddings_plugins() -> dict:
    """
    Find all installed plugins
    @return: dict plugin names to entrypoints
    """
    from ovos_plugin_manager.utils import find_plugins
    return find_plugins(PluginTypes.VOICE_EMBEDDINGS)


def load_voice_embeddings_plugin(module_name: str) -> type(VoiceEmbeddingsRecognizer):
    """
    Get an uninstantiated class for the requested module_name
    @param module_name: Plugin entrypoint name to load
    @return: Uninstantiated class
    """
    from ovos_plugin_manager.utils import load_plugin
    return load_plugin(module_name, PluginTypes.VOICE_EMBEDDINGS)


def find_face_embeddings_plugins() -> dict:
    """
    Find all installed plugins
    @return: dict plugin names to entrypoints
    """
    from ovos_plugin_manager.utils import find_plugins
    return find_plugins(PluginTypes.FACE_EMBEDDINGS)


def load_face_embeddings_plugin(module_name: str) -> type(FaceEmbeddingsRecognizer):
    """
    Get an uninstantiated class for the requested module_name
    @param module_name: Plugin entrypoint name to load
    @return: Uninstantiated class
    """
    from ovos_plugin_manager.utils import load_plugin
    return load_plugin(module_name, PluginTypes.FACE_EMBEDDINGS)
