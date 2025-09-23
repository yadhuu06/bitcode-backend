

echo "🛑 Stopping Daphne..."
pkill -f "daphne -p 8000"



echo "🛑 (Optional) Stopping Redis server..."
pkill redis-server

echo "✅ All services stopped."
