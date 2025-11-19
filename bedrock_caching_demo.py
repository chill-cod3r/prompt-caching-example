import boto3
import json
import time


def main():
    # 1. Setup Bedrock Client
    # Make sure your AWS credentials are configured (e.g. ~/.aws/credentials or env vars)
    client = boto3.client("bedrock-runtime", region_name="us-west-2")

    # 2. Select a model that supports caching
    # Using Claude 3.5 Haiku
    model_id = "global.anthropic.claude-haiku-4-5-20251001-v1:0"

    # 3. Create a large context to cache
    # Claude 3.5 Sonnet requires a minimum of 1024 tokens to cache
    print("Generating large context...")
    large_text = "This is a test of prompt caching in python. " * 5000

    # 4. Define the system prompt with a cache point
    # The 'cachePoint' block must be a separate item in the list, following the content it caches
    system_prompts = [
        {
            "text": f"You are a helpful assistant. Here is some reference text: {large_text}"
        },
        {"cachePoint": {"type": "default"}},
    ]

    # 5. Define the user message
    messages = [
        {
            "role": "user",
            "content": [
                {"text": "Summarize the reference text briefly."},
                {"cachePoint": {"type": "default"}},
            ],
        }
    ]

    print(f"\n--- Request 1: Creating Cache ---")
    start_time = time.time()
    try:
        response1 = client.converse(
            modelId=model_id, messages=messages, system=system_prompts
        )
        duration1 = time.time() - start_time

        usage1 = response1["usage"]
        print(f"Latency: {duration1:.2f}s")
        print(f"Input Tokens: {usage1['inputTokens']}")
        print(f"Output Tokens: {usage1['outputTokens']}")
        # Check specific caching metrics if available (might be under 'metrics' or specialized fields depending on API version)
        # Note: Boto3 1.35+ structure for usage includes caching details
        print(f"Full Usage Info: {json.dumps(usage1, indent=2)}")

    except Exception as e:
        print(f"Error in Request 1: {e}")
        return

    # 6. Send the EXACT same system prompt again to trigger a cache hit
    # We can change the user message, but the prefix (system prompt) must match exactly

    messages2 = [
        {
            "role": "user",
            "content": [
                {"text": "Summarize the reference text briefly."},
                {"cachePoint": {"type": "default"}},
                {
                    "text": "What is the first sentence of the reference text and what did i already ask you?"
                },
            ],
        }
    ]

    print(f"\n--- Request 2: Using Cache ---")
    start_time = time.time()
    try:
        response2 = client.converse(
            modelId=model_id, messages=messages2, system=system_prompts
        )
        duration2 = time.time() - start_time

        usage2 = response2["usage"]
        print(f"Latency: {duration2:.2f}s")
        print(f"Input Tokens: {usage2['inputTokens']}")
        print(f"Output Tokens: {usage2['outputTokens']}")
        print(f"Full Usage Info: {json.dumps(usage2, indent=2)}")

    except Exception as e:
        print(f"Error in Request 2: {e}")


if __name__ == "__main__":
    main()
