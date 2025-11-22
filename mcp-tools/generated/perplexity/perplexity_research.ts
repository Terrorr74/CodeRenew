import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "perplexity_research",
  server: "perplexity",
  description: "Performs deep research using the Perplexity API. Uses sonar-deep-research model and returns comprehensive research response with citations.",
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
