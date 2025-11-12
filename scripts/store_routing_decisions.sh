#!/bin/bash

##
# Store Routing Decisions in Memory via Claude Flow Hooks
#
# This script integrates with claude-flow hooks to store routing decisions
# in persistent memory for analysis and optimization.
##

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Storing Routing Decisions in Memory ===${NC}\n"

# Function to store routing decision
store_routing_decision() {
    local agent="$1"
    local target="$2"
    local intent="$3"
    local confidence="$4"
    local trigger="$5"

    echo -e "${YELLOW}Storing routing decision: ${agent} -> ${target}${NC}"

    # Store in memory via claude-flow hooks
    npx claude-flow@alpha hooks post-edit \
        --file "app/agents/router.py" \
        --memory-key "swarm/routing/${agent}_to_${target}" \
        --value "{\"intent\":\"${intent}\",\"confidence\":${confidence},\"trigger\":\"${trigger}\",\"timestamp\":\"$(date -Iseconds)\"}"

    echo -e "${GREEN}✓ Decision stored${NC}\n"
}

# Store coordination metadata
echo -e "${YELLOW}Storing coordination metadata...${NC}"

npx claude-flow@alpha hooks post-task \
    --task-id "routing_system_update" \
    --success true \
    --memory-key "swarm/shared/routing_config" \
    --value "{
        \"version\": \"1.0.0\",
        \"agents\": [\"search_agent\", \"property_agent\", \"scheduling_agent\"],
        \"routing_patterns\": {
            \"search_to_property\": \"properties_found\",
            \"search_to_scheduling\": \"scheduling_requested\",
            \"property_to_search\": \"new_search_requested\",
            \"property_to_scheduling\": \"scheduling_requested\",
            \"scheduling_to_search\": \"new_search_requested\",
            \"scheduling_to_property\": \"property_analysis_requested\"
        },
        \"context_preservation\": true,
        \"intent_detection\": true,
        \"updated_at\": \"$(date -Iseconds)\"
    }"

echo -e "${GREEN}✓ Coordination metadata stored${NC}\n"

# Store example routing patterns
echo -e "${YELLOW}Storing routing patterns...${NC}"

store_routing_decision "search_agent" "property_agent" "property_analysis" "0.9" "properties_found"
store_routing_decision "search_agent" "scheduling_agent" "scheduling" "0.85" "scheduling_requested"
store_routing_decision "property_agent" "search_agent" "search" "0.9" "new_search_requested"
store_routing_decision "property_agent" "scheduling_agent" "scheduling" "0.95" "scheduling_requested"
store_routing_decision "scheduling_agent" "search_agent" "search" "0.9" "new_search_requested"
store_routing_decision "scheduling_agent" "property_agent" "property_analysis" "0.85" "property_analysis_requested"

echo -e "${GREEN}✓ All routing patterns stored${NC}\n"

# Store handoff validation rules
echo -e "${YELLOW}Storing handoff validation rules...${NC}"

npx claude-flow@alpha hooks notify \
    --message "Handoff Validation Rules Updated" \
    --memory-key "swarm/shared/handoff_rules" \
    --value "{
        \"rules\": {
            \"scheduling_requires_property\": true,
            \"max_handoff_count\": 3,
            \"context_preservation_required\": true
        },
        \"updated_at\": \"$(date -Iseconds)\"
    }"

echo -e "${GREEN}✓ Validation rules stored${NC}\n"

echo -e "${BLUE}=== Memory Storage Complete ===${NC}"
echo -e "${GREEN}✓ All routing decisions and metadata stored in memory${NC}"
echo -e "${YELLOW}→ Routing system ready for coordination${NC}\n"
