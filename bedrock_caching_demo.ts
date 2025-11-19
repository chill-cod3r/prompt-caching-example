import {
  BedrockRuntimeClient,
  ConverseCommand,
  Message,
  SystemContentBlock,
} from "@aws-sdk/client-bedrock-runtime";

async function main() {
  // 1. Setup Bedrock Client
  const client = new BedrockRuntimeClient({ region: "us-east-1" });
//   const modelId = "global.anthropic.claude-haiku-4-5-20251001-v1:0";
  const modelId = 'us.anthropic.claude-3-5-haiku-20241022-v1:0';

  // 2. Create large context
  console.log("Generating large context...");
  const largeText =
    "This is a test of prompt caching demonstrating the benefits of prompt caching. ".repeat(
      5000
    );

  // 3. Define system prompt with cachePoint
  // cachePoint must be a separate block in the content array/list
  const systemPrompts: any[] = [
    {
      text: `You are a helpful assistant. Here is some reference text: ${largeText}`,
    },
    {
      cachePoint: { type: "default" },
    },
  ];

  // 4. Request 1
  const message1: Message = {
    role: "user",
    content: [
      { text: "Summarize the reference text briefly." },
      { cachePoint: { type: "default" } },
    ],
  };

  console.log("\n--- Request 1: Creating Cache ---");
  const start1 = Date.now();

  try {
    const command1 = new ConverseCommand({
      modelId,
      messages: [message1],
      system: systemPrompts,
    });

    const response1 = await client.send(command1);
    const duration1 = (Date.now() - start1) / 1000;

    console.log(`Latency: ${duration1.toFixed(2)}s`);
    if (response1.usage) {
      console.log(`Input Tokens: ${response1.usage.inputTokens}`);
      console.log(`Output Tokens: ${response1.usage.outputTokens}`);
      console.log("Full Usage Info:", JSON.stringify(response1.usage, null, 2));
    }
  } catch (error) {
    console.error("Error in Request 1:", error);
    return;
  }

  // 5. Request 2 (Cache Hit)
  const message2: Message = {
    role: "user",
    content: [
      { text: "What is the first sentence of the reference text?" },
    ],
  };

  console.log("\n--- Request 2: Using Cache ---");
  const start2 = Date.now();

  try {
    const command2 = new ConverseCommand({
      modelId,
      messages: [message2],
      system: systemPrompts, // Must be identical for cache hit
    });

    const response2 = await client.send(command2);
    const duration2 = (Date.now() - start2) / 1000;

    console.log(`Latency: ${duration2.toFixed(2)}s`);
    if (response2.usage) {
      console.log(`Input Tokens: ${response2.usage.inputTokens}`);
      console.log(`Output Tokens: ${response2.usage.outputTokens}`);
      console.log("Full Usage Info:", JSON.stringify(response2.usage, null, 2));
    }
  } catch (error) {
    console.error("Error in Request 2:", error);
  }
}

main();
