"""Module for managing semantic kernel operations and function calls."""

import logging
import sys
import json
from typing import Dict, Any, Optional, Callable
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments
from bullpenfi.auth import authenticator

# Configure the root logger to display logs of INFO level and above
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Add StreamHandler to output to stdout
    ],
)

logger = logging.getLogger(__name__)


class SemanticKernelService:
    """Manages semantic kernel operations and function calls."""

    def __init__(
        self,
        api_key: str,
        ai_model_id: str,
        openai_api_key: str,
    ):
        authenticator.authenticate(api_key)
        self.logger = self._configure_logging()
        self.kernel = self._initialize_kernel(ai_model_id, openai_api_key)

    def _configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        return logging.getLogger(__name__)

    def _initialize_kernel(
        self, ai_model_id: str, openai_api_key: str, json_mode: bool = True
    ):
        json_mode_header = {
            "Content-Type": "application/json",
            "response_format": json.dumps({"type": "json_object"}),
        }
        kernel = sk.Kernel()
        kernel.add_service(
            OpenAIChatCompletion(
                service_id="default",
                ai_model_id=ai_model_id,
                api_key=openai_api_key,
                default_headers=json_mode_header if json_mode else None,
            )
        )
        return kernel

    def load_sk_function(self, plugin_name, function_name):
        """
        Loads a specified plugin from the insight plugins directory, handling various errors.

        Args:
            plugin_name (str): Name of the plugin to load.

        Returns:
            Optional[Callable]: The loaded plugin function, or None if the plugin cannot be loaded.

        Raises:
            KeyError: If the plugin is not found.
            FileNotFoundError: If the plugin directory is not found.
            ImportError: If necessary components for the plugin cannot be imported.
            Exception: For any other unexpected errors.
        """
        try:
            return plugin_name[function_name]
        except KeyError:
            logger.error(
                "Insight function not found in the InsightPlugin.", exc_info=True
            )
            return None
        except FileNotFoundError:
            logger.error("Plugin directory not found.", exc_info=True)
            return None
        except ImportError:
            logger.error(
                "Failed to import the necessary components for the plugin.",
                exc_info=True,
            )
            return None
        # pylint: disable=broad-except
        except Exception as e:
            logger.error(
                "An unexpected error occurred in load_insight_plugin: %s",
                e,
                exc_info=True,
            )
            return None

    async def call_semantic_function(
        self,
        plugin_name: str,
        function_name: str,
        arguments: Dict[str, Any],
        max_tokens: Optional[int] = None,
        max_retries: int = 5,
        result_validator: Callable[[Any], bool] = lambda x: True,
        result_processor: Callable[[str], Any] = lambda x: x,
    ):
        """
        Calls a semantic function with the given parameters and handles retries and validation.

        Args:
            plugin_name (str): Name of the plugin to load.
            function_name (str): Name of the function to call within the plugin.
            arguments (Dict[str, Any]): Arguments to pass to the function.
            max_tokens (Optional[int], optional): Maximum number of tokens to consider. Defaults to None.
            max_retries (int, optional): Maximum number of retries for the function call. Defaults to 5.
            result_validator (Callable[[Any], bool], optional): Function to validate the result. Defaults to always return True.
            result_processor (Callable[[str], Any], optional): Function to process the raw result string. Defaults to identity function.

        Returns:
            Any: The processed and validated result from the semantic function call.

        Raises:
            ValueError: If the function fails to produce a valid result after max_retries.
        """
        if max_tokens is None:
            logger.error("max_tokens is None")
            raise ValueError("max_tokens is None")

        semantic_function = self.load_sk_function(plugin_name, function_name)
        if not semantic_function:
            raise ValueError(f"Failed to load function: {function_name}")

        is_result_valid = False
        retries = 0

        while not is_result_valid and retries < max_retries:
            try:
                llm_result = await self.kernel.invoke(
                    semantic_function,
                    KernelArguments(**arguments),
                )

                # mixpanel.track_llm_usage(
                #     function_name, analytics.get_llm_usage_analytics(llm_result)
                # )

                raw_result = (
                    llm_result.value[0].inner_content.choices[0].message.content
                )
                raw_result = (
                    raw_result.replace("```python", "")
                    .replace("```", "")
                    .replace("json", "")
                )

                processed_result = result_processor(raw_result)

                if result_validator(processed_result):
                    is_result_valid = True
                    return processed_result
                else:
                    logger.info(
                        "Invalid result format for %s, retrying...", function_name
                    )

            # pylint: disable=broad-except
            except Exception as e:
                logger.error(
                    "An error occurred in %s: %s", function_name, e, exc_info=True
                )

            retries += 1

        raise ValueError(
            f"Failed to get valid result for {function_name} after {max_retries} retries"
        )
