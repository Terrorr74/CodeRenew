import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "perplexity_reason",
  server: "perplexity",
  description: "Performs advanced reasoning and problem-solving using the sonar-reasoning-pro model. Provides well-reasoned responses for complex analytical tasks.",
  parameters: [
    {
      name: "messages",
      type: "array",
      description: "Array of conversation messages with role and content",
      required: true
    },
    {
      name: "strip_thinking",
      type: "boolean",
      description: "If true, removes <think>...</think> tags to save context tokens. Default is false.",
      required: false
    },
  ],
};

export default definition;
