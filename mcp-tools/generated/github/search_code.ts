import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "search_code",
  server: "github",
  description: "Fast code search across GitHub repositories",
  parameters: [
    { name: "query", type: "string", description: "Search query using GitHub code search syntax", required: true },
    { name: "page", type: "number", description: "Page number", required: false },
    { name: "perPage", type: "number", description: "Results per page (1-100)", required: false },
  ],
};

export default definition;
