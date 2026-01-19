#!/usr/bin/env bash

# Test script for ingredient_router endpoints
# Usage: chmod +x test_ingredients.sh && ./test_ingredients.sh

BASE_URL="http://localhost:8000"
INGREDIENTS_PREFIX="/ingredients"

GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
RESET="\033[0m"

PASS_COUNT=0
FAIL_COUNT=0

# Helper function to run tests
run_test() {
  local name="$1"
  local method="$2"
  local url="$3"
  local data="$4"

  echo -e "${YELLOW}=== Running: ${name}${RESET}" >&2

  local tmp_body
  tmp_body=$(mktemp)

  if [[ -n "$data" ]]; then
    http_code=$(curl -s -o "$tmp_body" -w "%{http_code}" \
      -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$data")
  else
    http_code=$(curl -s -o "$tmp_body" -w "%{http_code}" \
      -X "$method" "$url")
  fi

  local body_content
  body_content=$(cat "$tmp_body")
  local exit_code

  if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
    echo -e "${GREEN}✅ PASS${RESET} [$http_code] - $name" >&2
    exit_code=0
  else
    echo -e "${RED}❌ FAIL${RESET} [$http_code] - $name" >&2
    echo "Response body:" >&2
    echo "$body_content" >&2
    echo >&2
    exit_code=1
  fi

  echo "$body_content"
  rm -f "$tmp_body"
  return $exit_code
}

echo "==========================================="
echo "Testing Ingredient Management Endpoints"
echo "==========================================="
echo

# 0) First, ensure we have units and a category (Fruit)
echo "=== Setup: Creating units and category ===" >&2

# Create units first
run_test "Setup Units" "POST" \
  "${BASE_URL}/admin/setup/units" \
  '[
    {"name": "kilogram", "abbreviation": "kg"},
    {"name": "gram", "abbreviation": "g"},
    {"name": "pound", "abbreviation": "lb"}
  ]' > /dev/null 2>&1

# Create Fruit category
run_test "Setup Category (Fruit)" "POST" \
  "${BASE_URL}/admin/setup/categories" \
  '{
    "name": "Fruit",
    "tag": "Fresh fruits",
    "unit_names": ["kilogram", "gram", "pound"]
  }' > /dev/null 2>&1

echo "Setup complete" >&2
echo >&2

# 1) Create single ingredient (requires existing category_id=1)
TEST_NAME="Create Single Ingredient (Strawberry)"
INGREDIENT_BODY=$(cat <<EOF
{
  "name": "Strawberry",
  "category_name": "Fruit",
  "brand": "Fresh Farm",
  "threshold": 10.00,
  "allergen_ids": []
}
EOF
)
INGREDIENT_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INGREDIENTS_PREFIX}" \
  "$INGREDIENT_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$INGREDIENT_RESP" >&2
echo >&2

INGREDIENT_NAME="Strawberry"
echo "Using INGREDIENT_NAME = $INGREDIENT_NAME for subsequent tests" >&2
echo >&2

# 2) Create batch ingredients
TEST_NAME="Create Batch Ingredients"
BATCH_BODY=$(cat <<EOF
[
  {
    "name": "Blueberry",
    "category_name": "Fruit",
    "threshold": 5.00,
    "allergen_ids": []
  },
  {
    "name": "Raspberry",
    "category_name": "Fruit",
    "brand": "Berry Best",
    "threshold": 8.00,
    "allergen_ids": []
  }
]
EOF
)
BATCH_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INGREDIENTS_PREFIX}" \
  "$BATCH_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Batch response:" >&2
echo "$BATCH_RESP" >&2
echo >&2

# 3) List all ingredients
TEST_NAME="List All Ingredients"
LIST_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INGREDIENTS_PREFIX}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "List response:" >&2
echo "$LIST_RESP" >&2
echo >&2

# 4) Search ingredients by name
TEST_NAME="Search Ingredients (q=berry)"
SEARCH_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INGREDIENTS_PREFIX}?q=berry" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Search response:" >&2
echo "$SEARCH_RESP" >&2
echo >&2

# 5) Get single ingredient by name
TEST_NAME="Get Ingredient by Name (Strawberry)"
GET_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INGREDIENTS_PREFIX}/${INGREDIENT_NAME}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Get by name response:" >&2
echo "$GET_RESP" >&2
echo >&2

# 6) Update ingredient by name
TEST_NAME="Update Ingredient by Name"
UPDATE_BODY=$(cat <<EOF
{
  "brand": "Organic Fresh Farm",
  "threshold": 15.00
}
EOF
)
UPDATE_RESP=$(run_test "$TEST_NAME" "PUT" \
  "${BASE_URL}${INGREDIENTS_PREFIX}/${INGREDIENT_NAME}" \
  "$UPDATE_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Update response:" >&2
echo "$UPDATE_RESP" >&2
echo >&2

# Summary
echo >&2
echo "================= TEST SUMMARY =================" >&2
echo -e "${GREEN}PASS: ${PASS_COUNT}${RESET}" >&2
echo -e "${RED}FAIL: ${FAIL_COUNT}${RESET}" >&2
echo "================================================" >&2
echo "Done." >&2
