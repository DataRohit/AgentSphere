# Third-party imports
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Local application imports
from apps.llms.models.choices.api_types import ApiType

# Map the api types to the respective client
api_type_to_client = {
    ApiType.GOOGLE: OpenAIChatCompletionClient,
}
