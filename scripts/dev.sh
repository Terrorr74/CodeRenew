#!/bin/bash

# Development helper script
# Quick commands for common development tasks

case "$1" in
  start)
    echo "🚀 Starting development environment..."
    docker-compose up
    ;;

  stop)
    echo "🛑 Stopping development environment..."
    docker-compose down
    ;;

  restart)
    echo "🔄 Restarting development environment..."
    docker-compose restart
    ;;

  logs)
    if [ -n "$2" ]; then
      docker-compose logs -f "$2"
    else
      docker-compose logs -f
    fi
    ;;

  migrate)
    echo "🗄️  Running database migrations..."
    docker-compose exec backend alembic upgrade head
    ;;

  migration)
    if [ -z "$2" ]; then
      echo "❌ Please provide a migration message"
      echo "Usage: ./scripts/dev.sh migration 'your message'"
      exit 1
    fi
    echo "📝 Creating new migration: $2"
    docker-compose exec backend alembic revision --autogenerate -m "$2"
    ;;

  shell)
    if [ "$2" == "backend" ]; then
      docker-compose exec backend /bin/bash
    elif [ "$2" == "frontend" ]; then
      docker-compose exec frontend /bin/sh
    elif [ "$2" == "db" ]; then
      docker-compose exec db psql -U coderenew -d coderenew
    else
      echo "Usage: ./scripts/dev.sh shell [backend|frontend|db]"
    fi
    ;;

  reset)
    echo "🗑️  Resetting database (this will delete all data)..."
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      docker-compose down -v
      docker-compose up -d db
      sleep 3
      docker-compose exec backend alembic upgrade head
      echo "✅ Database reset complete"
    fi
    ;;

  test)
    if [ "$2" == "backend" ]; then
      echo "🧪 Running backend tests..."
      docker-compose exec backend pytest
    elif [ "$2" == "frontend" ]; then
      echo "🧪 Running frontend tests..."
      docker-compose exec frontend npm test
    else
      echo "Usage: ./scripts/dev.sh test [backend|frontend]"
    fi
    ;;

  *)
    echo "CodeRenew Development Helper"
    echo ""
    echo "Usage: ./scripts/dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start              Start all services"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  logs [service]     View logs (optional: specific service)"
    echo "  migrate            Run database migrations"
    echo "  migration 'msg'    Create new migration"
    echo "  shell [service]    Open shell (backend|frontend|db)"
    echo "  reset              Reset database (WARNING: deletes all data)"
    echo "  test [service]     Run tests (backend|frontend)"
    ;;
esac
