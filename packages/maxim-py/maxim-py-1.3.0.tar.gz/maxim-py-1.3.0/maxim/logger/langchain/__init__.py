import logging
import sys

logger = logging.getLogger("MaximSDK")

try:
    import langchain

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

if not LANGCHAIN_AVAILABLE:
    logger.error(
        "LangChain is not available. You can't use MaximLangchainTracer.")
