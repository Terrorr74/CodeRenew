import { ToolDefinition } from '../../registry/tool-loader';

const definition: ToolDefinition = {
  name: "perplexity_search",
  server: "perplexity",
  description: "Performs web search using the Perplexity Search API. Returns ranked search results with titles, URLs, snippets, and metadata. Perfect for finding up-to-date facts, news, or specific information.",
  parameters: [
    { name: "query", type: "string", description: "Search query string", required: true },
    { name: "max_results", type: "number", description: "Maximum number of results to return (1-20, default: 10)", required: false },
    { name: "max_tokens_per_page", type: "number", description: "Maximum tokens to extract per webpage (default: 1024)", required: false },
    { name: "country", type: "string", description: "ISO 3166-1 alpha-2 country code for regional results (e.g., 'US', 'GB')", required: false },
  ],
};

export default definition;
