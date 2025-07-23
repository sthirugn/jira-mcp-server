#!/bin/bash
# Weekly Team Summary Runner
# Convenient wrapper script for generating Jira team summaries

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUMMARY_SCRIPT="$SCRIPT_DIR/weekly_team_summary.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_help() {
    echo "Weekly Team Summary Runner"
    echo "========================="
    echo ""
    echo "Usage:"
    echo "  $0 [option]"
    echo ""
    echo "Options:"
    echo "  current      Generate summary for current week (Monday-Sunday)"
    echo "  last         Generate summary for last week" 
    echo "  this         Same as 'current'"
    echo "  YYYY-MM-DD   Generate summary starting from this date (7 days)"
    echo "  help         Show this help message"
    echo ""
    echo "Custom date range:"
    echo "  $0 YYYY-MM-DD YYYY-MM-DD    Start date and end date"
    echo ""
    echo "Examples:"
    echo "  $0 current                   # Current week"
    echo "  $0 last                      # Last week"
    echo "  $0 2024-07-15               # Week starting July 15"
    echo "  $0 2024-07-15 2024-07-22    # Specific date range"
}

# Function to get Monday of current week
get_monday() {
    local date_ref="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -j -f "%Y-%m-%d" "$date_ref" -v-monday +"%Y-%m-%d" 2>/dev/null || \
        date -v-$(date +%u)d -v+1d +"%Y-%m-%d"
    else
        # Linux
        date -d "$date_ref - $(date -d "$date_ref" +%u) days + 1 day" +"%Y-%m-%d" 2>/dev/null || \
        date -d "monday" +"%Y-%m-%d"
    fi
}

# Function to add days to a date
add_days() {
    local date_input="$1"
    local days="$2"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -j -f "%Y-%m-%d" "$date_input" -v+"$days"d +"%Y-%m-%d"
    else
        # Linux
        date -d "$date_input + $days days" +"%Y-%m-%d"
    fi
}

# Check if virtual environment is active
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${YELLOW}Warning: Virtual environment not detected.${NC}"
        echo "Make sure you have activated your Python virtual environment with the required packages."
        echo ""
    fi
}

# Main logic
case "${1:-current}" in
    "help"|"-h"|"--help")
        print_help
        exit 0
        ;;
    "current"|"this"|"")
        echo -e "${BLUE}📅 Generating summary for current week...${NC}"
        check_venv
        python3 "$SUMMARY_SCRIPT"
        ;;
    "last")
        echo -e "${BLUE}📅 Generating summary for last week...${NC}"
        today=$(date +"%Y-%m-%d")
        last_monday=$(get_monday "$(date -d "$today - 7 days" +"%Y-%m-%d")")
        last_sunday=$(add_days "$last_monday" 6)
        check_venv
        python3 "$SUMMARY_SCRIPT" "$last_monday" "$last_sunday"
        ;;
    *[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]*)
        # Date format detected
        start_date="$1"
        if [[ -n "$2" && "$2" =~ ^[0-9]{4}-[0-1][0-9]-[0-3][0-9]$ ]]; then
            # Two dates provided
            end_date="$2"
            echo -e "${BLUE}📅 Generating summary for $start_date to $end_date...${NC}"
        else
            # Single date provided, calculate end date
            end_date=$(add_days "$start_date" 6)
            echo -e "${BLUE}📅 Generating summary for week starting $start_date (to $end_date)...${NC}"
        fi
        check_venv
        python3 "$SUMMARY_SCRIPT" "$start_date" "$end_date"
        ;;
    *)
        echo -e "${RED}Error: Unknown option '$1'${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac

# Check if report was generated
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✅ Summary generation completed!${NC}"
    echo "Report files are saved in the current directory."
    echo ""
    echo "Recent reports:"
    ls -lt Reports/team_summary_*.md 2>/dev/null | head -3 || echo "No report files found."
else
    echo -e "${RED}❌ Summary generation failed!${NC}"
    exit 1
fi 