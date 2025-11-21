import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "get_me",
  server: "github",
  description: "Get details of the authenticated GitHub user",
  parameters: [],
  examples: ['get_me()']
};

export default definition;
