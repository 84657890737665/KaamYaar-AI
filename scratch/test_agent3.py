import json
import logging
from agents.provider_discovery.agent import ProviderDiscoveryAgent
from agents.matching_ranker.agent import MatchingRankerAgent
from dotenv import load_dotenv

load_dotenv()

# Set logging level to see the scores
logging.basicConfig(level=logging.INFO)

def main():
    agent2 = ProviderDiscoveryAgent(data_path="data/providers.json")
    agent3 = MatchingRankerAgent()
    
    mock_parsed_request = {
        "service_type": "electrician",
        "location": "Saddar Karachi",
        "urgency": "high",
        "budget": "under 5000",
        "primary_language": "Roman Urdu"
    }
    
    print("\n" + "="*50)
    print("--- Running Agent 2 (Provider Discovery) ---")
    agent2_output = agent2.run({"parsed_request": mock_parsed_request})
    
    print(f"Found {agent2_output['total_found']} candidates.")
    
    print("\n" + "="*50)
    print("--- Running Agent 3 (Matching & Ranker) ---")
    agent3_input = {
        "candidates": agent2_output["candidates"],
        "parsed_request": mock_parsed_request
    }
    
    output = agent3.run(agent3_input)
    
    print("\n" + "="*50)
    print("--- Output from Agent 3 (JSON) ---")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
