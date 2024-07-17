import requests
from typing import Dict, Any, Optional

class PropsAI:
    def __init__(self, api_key: str, providers_keys: Optional[Dict[str, Optional[str]]] = None):
        self.api_key = api_key
        self.base_url = "https://props-api.propsai.workers.dev/experiments/unittest/feedback"
        self.providers_keys = providers_keys or {
            "openai": None,
            "groq": None,
            "anthropic": None,
            "google": None,
        }

    def generate_headers(
        self,
        api_key: str,
        provider: str,
        metadata: Dict[str, str],
        session_id: str
    ) -> Dict[str, str]:
        """
        Generate headers with provider keys included.

        :param api_key: The API key.
        :param provider: The provider name.
        :param metadata: Metadata dictionary.
        :param session_id: The session ID.
        :return: A dictionary containing headers.
        """
        headers = {
            "x-props-key": api_key,
            "x-props-provider": provider,
            "x-props-metadata": str(metadata),
            "x-props-session-id": session_id,
        }
        
        # Include provider keys in the headers
        for provider_key, key in self.providers_keys.items():
            if key:
                headers[f"x-props-{provider_key}-key"] = key

        return headers

    def send_feedback(
        self,
        feedback_id: str,
        experiment_id: str,
        context_id: str,
        metric_id: str,
        value: str
    ) -> Dict[str, Any]:
        """
        Send a POST request to the feedback endpoint.

        :param feedback_id: The feedback ID.
        :param experiment_id: The experiment ID.
        :param context_id: The context ID.
        :param metric_id: The metric ID.
        :param value: The feedback value.
        :return: A dictionary containing the status code and response text.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        # Include provider keys in the headers
        for provider, key in self.providers_keys.items():
            if key:
                headers[f"x-props-{provider}-key"] = key

        data = {
            "id": feedback_id,
            "experimentId": experiment_id,
            "contextId": context_id,
            "metricId": metric_id,
            "value": value,
        }

        response = requests.post(self.base_url, headers=headers, json=data)
        return {
            "status_code": response.status_code,
            "response_text": response.text,
        }

# Example usage:
if __name__ == "__main__":
    props_ai = PropsAI(
        api_key="api_key",
        providers_keys={
            "openai": "<TEST_PYTHON_SDK_OPENAI_KEY>",
            "groq": "<TEST_PYTHON_SDK_GROQ_KEY>",
            "anthropic": "<TEST_PYTHON_SDK_ANTHROPIC_KEY>",
            "google": "<TEST_PYTHON_SDK_GOOGLE_KEY>",
        }
    )

    # Example of generating headers
    headers = props_ai.generate_headers(
        api_key="api_key",
        provider="openai",
        metadata={"user": "test_user"},
        session_id="test_session_id"
    )
    print(f"Generated headers: {headers}")

    # POST request example
    post_response = props_ai.send_feedback(
        feedback_id="feedbackIdTest",
        experiment_id="<TEST_PYTHON_SDK_EXPERIMENT_ID>",
        context_id="<TEST_PYTHON_SDK_CONTEXT_ID>",
        metric_id="metricIdTest",
        value="feedbackValueTest"
    )
    
    print(f"POST response status: {post_response['status_code']}")
    print(f"POST response body: {post_response['response_text']}")
