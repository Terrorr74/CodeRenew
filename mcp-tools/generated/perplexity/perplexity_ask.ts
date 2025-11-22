import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "perplexity_ask",
  server: "perplexity",
  description: "Engages in a conversation using the Sonar API with real-time web search. Uses the sonar-pro model for general-purpose conversational AI.",
  parameters: [
    {
      name: "messages",
      type: "array",
      description: "Array of conversation messages with role and content",
      required: true
    },
  ],
};

export default definition;
