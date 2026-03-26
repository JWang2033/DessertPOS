#!/usr/bin/env bash

# Test script for inventory management endpoints
# Usage: chmod +x test_inventory.sh && ./test_inventory.sh

BASE_URL="http://localhost:8000"
INVENTORY_PREFIX="/inventory"

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

  echo "Response body:" >&2
  echo "$body_content" >&2
  echo >&2

  local exit_code=0
  if [[ "$http_code" =~ ^2[0-9]{2}$ ]]; then
    echo -e "${GREEN}✅ PASS [$http_code] - ${name}${RESET}" >&2
  else
    echo -e "${RED}❌ FAIL [$http_code] - ${name}${RESET}" >&2
    exit_code=1
  fi

  echo "$body_content"
  rm -f "$tmp_body"
  return $exit_code
}

echo "==========================================="
echo "Testing Inventory Management Endpoints"
echo "==========================================="
echo

# 0) Setup: Ensure we have ingredients (from previous tests)
echo "=== Prerequisite Check ===" >&2
echo "Make sure you have run test_ingredients.sh first to create:" >&2
echo "  - Fruit category with units" >&2
echo "  - Strawberry, Blueberry, Raspberry ingredients with thresholds" >&2
echo >&2

# 1) Create inventory record (Strawberry in Cold Storage)
TEST_NAME="Create Inventory (Strawberry - Cold Storage A)"
INV1_BODY=$(cat <<EOF
{
  "ingredient_name": "Strawberry",
  "unit_name": "kilogram",
  "standard_qty": 50.0,
  "actual_qty": 30.0,
  "location": "Cold Storage A"
}
EOF
)
INV1_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INVENTORY_PREFIX}" \
  "$INV1_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$INV1_RESP" >&2

# Extract inventory_id for later tests
INV_ID=$(echo "$INV1_RESP" | grep -o '"inventory_id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Using INV_ID = $INV_ID for subsequent tests" >&2
echo >&2

# 2) Create inventory record (Blueberry in Cold Storage)
TEST_NAME="Create Inventory (Blueberry - Cold Storage A)"
INV2_BODY=$(cat <<EOF
{
  "ingredient_name": "Blueberry",
  "unit_name": "kilogram",
  "standard_qty": 30.0,
  "actual_qty": 28.0,
  "location": "Cold Storage A"
}
EOF
)
INV2_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INVENTORY_PREFIX}" \
  "$INV2_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$INV2_RESP" >&2
echo >&2

# 3) Create inventory record (Raspberry in Freezer - low stock)
TEST_NAME="Create Inventory (Raspberry - Freezer B - Low Stock)"
INV3_BODY=$(cat <<EOF
{
  "ingredient_name": "Raspberry",
  "unit_name": "gram",
  "standard_qty": 20000,
  "actual_qty": 3000,
  "location": "Freezer B"
}
EOF
)
INV3_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INVENTORY_PREFIX}" \
  "$INV3_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$INV3_RESP" >&2
echo >&2

# 4) List all inventory
TEST_NAME="List All Inventory"
LIST_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INVENTORY_PREFIX}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "List response:" >&2
echo "$LIST_RESP" >&2
echo >&2

# 5) List inventory grouped by location
TEST_NAME="List Inventory (Group by Location)"
GROUP_LOC_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INVENTORY_PREFIX}?group_by=location" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Group by location response:" >&2
echo "$GROUP_LOC_RESP" >&2
echo >&2

# 6) List inventory grouped by restock_needed
TEST_NAME="List Inventory (Group by Restock Needed)"
GROUP_RESTOCK_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INVENTORY_PREFIX}?group_by=restock_needed" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Group by restock_needed response:" >&2
echo "$GROUP_RESTOCK_RESP" >&2
echo >&2

# 7) List inventory sorted by actual_qty
TEST_NAME="List Inventory (Sort by Actual Qty)"
SORT_QTY_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${INVENTORY_PREFIX}?sort_by=actual_qty" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Sort by actual_qty response:" >&2
echo "$SORT_QTY_RESP" >&2
echo >&2

# 8) Update inventory quantity (increase stock)
if [[ -n "$INV_ID" ]]; then
  TEST_NAME="Update Inventory Quantity (ID: $INV_ID)"
  UPDATE_BODY=$(cat <<EOF
{
  "actual_qty": 55.0
}
EOF
)
  UPDATE_RESP=$(run_test "$TEST_NAME" "PUT" \
    "${BASE_URL}${INVENTORY_PREFIX}/${INV_ID}" \
    "$UPDATE_BODY")
  test_result=$?
  [[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

  echo "Update response:" >&2
  echo "$UPDATE_RESP" >&2
  echo >&2
else
  echo "⚠️  Skipping update test - no inventory ID available" >&2
  echo >&2
fi

# 9) Update inventory quantity to trigger restock_needed
if [[ -n "$INV_ID" ]]; then
  TEST_NAME="Update Inventory to Low Stock (Trigger Restock)"
  LOW_STOCK_BODY=$(cat <<EOF
{
  "actual_qty": 5.0
}
EOF
)
  LOW_STOCK_RESP=$(run_test "$TEST_NAME" "PUT" \
    "${BASE_URL}${INVENTORY_PREFIX}/${INV_ID}" \
    "$LOW_STOCK_BODY")
  test_result=$?
  [[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

  echo "Low stock response:" >&2
  echo "$LOW_STOCK_RESP" >&2

  # Check if restock_needed is true
  if echo "$LOW_STOCK_RESP" | grep -q '"restock_needed":true'; then
    echo -e "${GREEN}✅ Restock flag correctly set to true${RESET}" >&2
  else
    echo -e "${YELLOW}⚠️  Restock flag may not be set (check ingredient threshold)${RESET}" >&2
  fi
  echo >&2
else
  echo "⚠️  Skipping low stock test - no inventory ID available" >&2
  echo >&2
fi

# 10) Validation test: Invalid ingredient name
TEST_NAME="Validation Test: Invalid Ingredient (Should Fail)"
INVALID_ING_BODY=$(cat <<EOF
{
  "ingredient_name": "NonExistentIngredient",
  "unit_name": "kilogram",
  "standard_qty": 10.0,
  "actual_qty": 5.0,
  "location": "Storage Room"
}
EOF
)
INVALID_ING_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INVENTORY_PREFIX}" \
  "$INVALID_ING_BODY")
test_result=$?

if [[ $test_result -ne 0 ]]; then
  echo -e "${GREEN}✅ PASS - Validation correctly rejected invalid ingredient${RESET}" >&2
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo -e "${RED}❌ FAIL - Should have rejected invalid ingredient${RESET}" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo >&2

# 11) Validation test: Negative quantity
TEST_NAME="Validation Test: Negative Quantity (Should Fail)"
NEGATIVE_QTY_BODY=$(cat <<EOF
{
  "ingredient_name": "Strawberry",
  "unit_name": "kilogram",
  "standard_qty": 50.0,
  "actual_qty": -10.0,
  "location": "Storage"
}
EOF
)
NEGATIVE_QTY_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${INVENTORY_PREFIX}" \
  "$NEGATIVE_QTY_BODY")
test_result=$?

if [[ $test_result -ne 0 ]]; then
  echo -e "${GREEN}✅ PASS - Validation correctly rejected negative quantity${RESET}" >&2
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo -e "${RED}❌ FAIL - Should have rejected negative quantity${RESET}" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo >&2

# 12) Validation test: Update with negative quantity
if [[ -n "$INV_ID" ]]; then
  TEST_NAME="Validation Test: Update with Negative Qty (Should Fail)"
  NEG_UPDATE_BODY=$(cat <<EOF
{
  "actual_qty": -5.0
}
EOF
)
  NEG_UPDATE_RESP=$(run_test "$TEST_NAME" "PUT" \
    "${BASE_URL}${INVENTORY_PREFIX}/${INV_ID}" \
    "$NEG_UPDATE_BODY")
  test_result=$?

  if [[ $test_result -ne 0 ]]; then
    echo -e "${GREEN}✅ PASS - Validation correctly rejected negative update${RESET}" >&2
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "${RED}❌ FAIL - Should have rejected negative quantity${RESET}" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  echo >&2
fi

# Summary
echo "==========================================="
echo "Test Summary"
echo "==========================================="
echo -e "${GREEN}Passed: $PASS_COUNT${RESET}"
echo -e "${RED}Failed: $FAIL_COUNT${RESET}"
echo "Total: $((PASS_COUNT + FAIL_COUNT))"
echo "==========================================="

if [[ $FAIL_COUNT -eq 0 ]]; then
  echo -e "${GREEN}All tests passed!${RESET}"
  exit 0
else
  echo -e "${RED}Some tests failed.${RESET}"
  exit 1
fi
