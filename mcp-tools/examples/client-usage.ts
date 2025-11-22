/**
 * MCP Client Usage Examples
 *
 * Demonstrates programmatic access to MCP servers without Claude's MCP integration
 */

import { createContext7Client, createGitHubClient, createSequentialThinkingClient, createPerplexityClient } from '../index';

/**
 * Example 1: Context7 - Get library documentation
 */
async function exampleContext7() {
  const client = createContext7Client();
  await client.connect();

  // Resolve library ID
  const libraryResult = await client.callTool({
    name: 'resolve-library-id',
    arguments: { libraryName: 'react' }
  });
  console.log('Context7 Libraries:', libraryResult);

  // Get documentation
  const docs = await client.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/react_dev',
      topic: 'hooks'
    }
  });
  console.log('React Hooks Docs:', docs);

  client.disconnect();
}

/**
 * Example 2: GitHub - Search repositories
 */
async function exampleGitHub() {
  // Token is optional - will use GITHUB_PERSONAL_ACCESS_TOKEN from env if not provided
  const client = createGitHubClient();
  await client.connect();

  // Search repositories
  const repos = await client.callTool({
    name: 'search_repositories',
    arguments: { query: 'wordpress scanner', perPage: 5 }
  });
  console.log('GitHub Repositories:', repos);

  // Get file contents
  const file = await client.callTool({
    name: 'get_file_contents',
    arguments: {
      owner: 'Terrorr74',
      repo: 'CodeRenew',
      path: 'README.md'
    }
  });
  console.log('README:', file);

  client.disconnect();
}

/**
 * Example 3: Sequential Thinking - Problem solving
 */
async function exampleSequentialThinking() {
  const client = createSequentialThinkingClient();
  await client.connect();

  // First thought
  const thought1 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: 'Let me break down how to optimize a WordPress plugin scanner...',
      thoughtNumber: 1,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });
  console.log('Thought 1:', thought1);

  // Second thought
  const thought2 = await client.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: 'Key optimization: Use parallel scanning with worker threads...',
      thoughtNumber: 2,
      totalThoughts: 3,
      nextThoughtNeeded: true
    }
  });
  console.log('Thought 2:', thought2);

  client.disconnect();
}

/**
 * Example 4: Perplexity - Web search and research
 */
async function examplePerplexity() {
  // API key is optional - will use PERPLEXITY_API_KEY from env if not provided
  const client = createPerplexityClient();
  await client.connect();

  // Quick web search
  const searchResults = await client.callTool({
    name: 'perplexity_search',
    arguments: {
      query: 'latest WordPress security vulnerabilities 2025',
      max_results: 5
    }
  });
  console.log('Search Results:', searchResults);

  // Conversational AI with web search
  const conversation = await client.callTool({
    name: 'perplexity_ask',
    arguments: {
      messages: [
        { role: 'user', content: 'What are the most common WordPress plugin vulnerabilities?' }
      ]
    }
  });
  console.log('AI Response:', conversation);

  // Deep research with citations
  const research = await client.callTool({
    name: 'perplexity_research',
    arguments: {
      messages: [
        { role: 'user', content: 'Research best practices for WordPress plugin security auditing' }
      ],
      strip_thinking: true
    }
  });
  console.log('Research:', research);

  // Advanced reasoning
  const reasoning = await client.callTool({
    name: 'perplexity_reason',
    arguments: {
      messages: [
        { role: 'user', content: 'Analyze the trade-offs between static analysis and dynamic analysis for WordPress plugin security scanning' }
      ]
    }
  });
  console.log('Reasoning:', reasoning);

  client.disconnect();
}

/**
 * Example 5: Multi-tool workflow
 */
async function exampleWorkflow() {
  // 1. Use sequential thinking to plan
  const thinking = createSequentialThinkingClient();
  await thinking.connect();

  const plan = await thinking.callTool({
    name: 'sequentialthinking',
    arguments: {
      thought: 'To create a WordPress compatibility report: 1) Get latest React docs for modern patterns, 2) Search GitHub for similar scanners, 3) Document findings',
      thoughtNumber: 1,
      totalThoughts: 1,
      nextThoughtNeeded: false
    }
  });

  // 2. Get documentation from Context7
  const context7 = createContext7Client();
  await context7.connect();

  const reactDocs = await context7.callTool({
    name: 'get-library-docs',
    arguments: {
      context7CompatibleLibraryID: '/websites/react_dev',
      topic: 'compatibility'
    }
  });

  // 3. Search GitHub for similar projects
  const github = createGitHubClient();
  await github.connect();

  const similarProjects = await github.callTool({
    name: 'search_repositories',
    arguments: { query: 'wordpress compatibility scanner', perPage: 3 }
  });

  console.log('Workflow complete:', { plan, reactDocs, similarProjects });

  thinking.disconnect();
  context7.disconnect();
  github.disconnect();
}

// Run examples
async function main() {
  try {
    console.log('\n=== Context7 Example ===');
    await exampleContext7();

    console.log('\n=== GitHub Example ===');
    await exampleGitHub();

    console.log('\n=== Sequential Thinking Example ===');
    await exampleSequentialThinking();

    console.log('\n=== Perplexity Example ===');
    await examplePerplexity();

    console.log('\n=== Multi-tool Workflow ===');
    await exampleWorkflow();
  } catch (error) {
    console.error('Error:', error);
  }
}

// Uncomment to run:
// main();
