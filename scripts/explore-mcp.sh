#!/bin/bash

# MCP Tools Interactive Explorer
# Makes it easy to explore Context7, Sequential Thinking, and Perplexity

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔═══════════════════════════════════════════════╗"
echo "║  MCP TOOLS INTERACTIVE EXPLORER               ║"
echo "║  Context7 + Sequential Thinking + Perplexity  ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check if TypeScript is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found. Please install Node.js"
    exit 1
fi

# Menu function
show_menu() {
    echo ""
    echo "What would you like to explore?"
    echo ""
    echo "  1) 📚 Context7 - Library Documentation"
    echo "  2) 🧠 Sequential Thinking - Problem Breakdown"
    echo "  3) 🔬 Perplexity - Web Research"
    echo "  4) 🎯 Practical Workflow - All Three Together"
    echo "  5) 🚀 Run All Explorations"
    echo "  6) 📖 View Full Guide"
    echo "  0) Exit"
    echo ""
    read -p "Enter your choice (0-6): " choice
}

# Context7 exploration
explore_context7() {
    echo ""
    echo "════════════════════════════════════════"
    echo "📚 CONTEXT7 EXPLORATION"
    echo "════════════════════════════════════════"
    echo ""
    echo "Context7 provides up-to-date library documentation."
    echo "You can search for any library and get relevant docs."
    echo ""

    read -p "Enter library name (e.g., fastapi, react, sqlalchemy): " library
    read -p "Enter topic (e.g., async requests, hooks, migrations): " topic

    echo ""
    echo "🔍 Searching for $library documentation on '$topic'..."
    echo ""

    cd "$PROJECT_ROOT"
    npx tsx -e "
    import { createContext7Client } from './mcp-tools';

    async function search() {
        const client = createContext7Client();
        client.on('error', () => {});
        await client.connect();

        console.log('📋 Step 1: Finding library ID...\n');
        const libs = await client.callTool({
            name: 'resolve-library-id',
            arguments: { libraryName: '$library' }
        });
        console.log(JSON.stringify(libs, null, 2));

        if (libs.libraries && libs.libraries.length > 0) {
            const libId = libs.libraries[0].id;
            console.log('\n📖 Step 2: Fetching documentation...\n');
            const docs = await client.callTool({
                name: 'get-library-docs',
                arguments: {
                    context7CompatibleLibraryID: libId,
                    topic: '$topic'
                }
            });
            console.log(JSON.stringify(docs, null, 2));
        }

        client.disconnect();
    }

    search().catch(console.error);
    "
}

# Sequential Thinking exploration
explore_thinking() {
    echo ""
    echo "════════════════════════════════════════"
    echo "🧠 SEQUENTIAL THINKING EXPLORATION"
    echo "════════════════════════════════════════"
    echo ""
    echo "Sequential Thinking helps break down complex problems."
    echo "Enter your problem and it will analyze it step-by-step."
    echo ""

    read -p "Describe your problem: " problem

    echo ""
    echo "💭 Analyzing problem step-by-step..."
    echo ""

    cd "$PROJECT_ROOT"
    npx tsx -e "
    import { createSequentialThinkingClient } from './mcp-tools';

    async function think() {
        const client = createSequentialThinkingClient();
        client.on('error', () => {});
        await client.connect();

        console.log('🔹 Thought 1: Initial Analysis\n');
        const thought1 = await client.callTool({
            name: 'sequentialthinking',
            arguments: {
                thought: 'Analyzing the problem: $problem',
                thoughtNumber: 1,
                totalThoughts: 1,
                nextThoughtNeeded: false
            }
        });
        console.log(JSON.stringify(thought1, null, 2));

        client.disconnect();
    }

    think().catch(console.error);
    "
}

# Perplexity exploration
explore_perplexity() {
    echo ""
    echo "════════════════════════════════════════"
    echo "🔬 PERPLEXITY EXPLORATION"
    echo "════════════════════════════════════════"
    echo ""

    # Check for API key
    if [ -z "$PERPLEXITY_API_KEY" ]; then
        echo "⚠️  PERPLEXITY_API_KEY not found in environment"
        echo ""
        read -p "Enter your Perplexity API key (or press Enter to skip): " api_key
        if [ -z "$api_key" ]; then
            echo "Skipping Perplexity exploration"
            return
        fi
        export PERPLEXITY_API_KEY="$api_key"
    fi

    echo ""
    echo "Perplexity provides AI-powered web research."
    echo ""

    read -p "Enter your research question: " question

    echo ""
    echo "🔎 Researching..."
    echo ""

    cd "$PROJECT_ROOT"
    npx tsx -e "
    import { createPerplexityClient } from './mcp-tools';

    async function research() {
        const client = createPerplexityClient();
        client.on('error', () => {});
        await client.connect();

        console.log('💬 Asking Perplexity AI...\n');
        const answer = await client.callTool({
            name: 'perplexity_ask',
            arguments: {
                messages: [{
                    role: 'user',
                    content: '$question'
                }]
            }
        });
        console.log(JSON.stringify(answer, null, 2));

        client.disconnect();
    }

    research().catch(console.error);
    "
}

# Run all explorations
run_all() {
    echo ""
    echo "🚀 Running all explorations with demo queries..."
    echo ""

    cd "$PROJECT_ROOT"
    npx tsx mcp-tools/examples/explore-mcp-tools.ts all
}

# Practical workflow
practical_workflow() {
    echo ""
    echo "════════════════════════════════════════"
    echo "🎯 PRACTICAL WORKFLOW DEMO"
    echo "════════════════════════════════════════"
    echo ""
    echo "This demonstrates using all three tools together"
    echo "to plan and implement a feature."
    echo ""

    cd "$PROJECT_ROOT"
    npx tsx mcp-tools/examples/explore-mcp-tools.ts workflow
}

# View guide
view_guide() {
    echo ""
    if command -v less &> /dev/null; then
        less "$PROJECT_ROOT/MCP_TOOLS_GUIDE.md"
    elif command -v more &> /dev/null; then
        more "$PROJECT_ROOT/MCP_TOOLS_GUIDE.md"
    else
        cat "$PROJECT_ROOT/MCP_TOOLS_GUIDE.md"
    fi
}

# Main loop
while true; do
    show_menu

    case $choice in
        1)
            explore_context7
            ;;
        2)
            explore_thinking
            ;;
        3)
            explore_perplexity
            ;;
        4)
            practical_workflow
            ;;
        5)
            run_all
            ;;
        6)
            view_guide
            ;;
        0)
            echo ""
            echo "👋 Goodbye!"
            echo ""
            exit 0
            ;;
        *)
            echo ""
            echo "❌ Invalid choice. Please try again."
            ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done
