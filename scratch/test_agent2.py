import json
from agents.provider_discovery.agent import ProviderDiscoveryAgent

def main():
    agent = ProviderDiscoveryAgent(data_path="data/providers.json")
    
    # Mocking the output from Agent 1 (ParsedServiceRequest)
    mock_input = {
        "service_type": "plumber",
        "location": "DHA Lahore",
        "urgency": "high",
        "budget": "under 2000"
    }
    
    print("--- Input to Agent 2 ---")
    print(json.dumps(mock_input, indent=2))
    
    print("\n--- Running Agent 2 ---")
    output = agent.run(mock_input)
    
    print("\n--- Output from Agent 2 ---")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
