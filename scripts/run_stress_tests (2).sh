#!/bin/bash

# run_stress_tests.sh
# A script to execute KaamYaar stress tests

echo "======================================"
echo "  KaamYaar Stress Testing Suite       "
echo "======================================"

MODE=${1:-all}
HOST="http://localhost:8000"

# Change directory to the root of the backend
cd "$(dirname "$0")/.."

if [ "$MODE" == "locust" ] || [ "$MODE" == "all" ]; then
    echo "Starting Locust Stress Tests (Headless)..."
    echo "Simulating 100 users with a spawn rate of 10 users/sec for 1 minute."
    # Run locust in headless mode as requested by user
    locust -f tests/stress_tests/locustfile.py --headless -u 100 -r 10 --run-time 1m --host $HOST
    echo "Locust tests completed."
    echo ""
fi

if [ "$MODE" == "pytest" ] || [ "$MODE" == "all" ]; then
    echo "Starting Pytest Async Stress Tests..."
    pytest tests/stress_tests/test_stress.py -v -s
    echo "Pytest async tests completed."
    echo ""
fi

echo "All stress tests finished."
