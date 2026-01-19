#!/usr/bin/env bash

# Test script for purchase order (receiving) endpoints
# Usage: chmod +x test_purchase_orders.sh && ./test_purchase_orders.sh

BASE_URL="http://localhost:8000"
RECEIVING_PREFIX="/receiving"

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
echo "Testing Purchase Order (Receiving) Endpoints"
echo "==========================================="
echo

# 0) Setup: Ensure we have ingredients (from previous tests)
echo "=== Prerequisite Check ===" >&2
echo "Make sure you have run test_ingredients.sh first to create:" >&2
echo "  - Fruit category with units" >&2
echo "  - Strawberry, Blueberry, Raspberry ingredients" >&2
echo >&2

# Cleanup: Delete existing test orders if needed (not implemented in router yet)
echo "=== Note: No cleanup needed - PO codes are unique by date ===" >&2
echo >&2

# Get today's date in YYYY-MM-DD format
TODAY=$(date +%Y-%m-%d)
echo "Using today's date: $TODAY" >&2
echo >&2

# 1) Create purchase order (Store 01 - Fresh Fruit order)
TEST_NAME="Create Purchase Order (STORE01 - Mixed Vendors)"
PO1_BODY=$(cat <<EOF
{
  "order_date": "$TODAY",
  "store_id": "STORE01",
  "items": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "kilogram",
      "quantity": 50.0,
      "vendor": "Fresh Fruit Suppliers Inc."
    },
    {
      "ingredient_name": "Blueberry",
      "unit_name": "kilogram",
      "quantity": 30.5,
      "vendor": "Fresh Fruit Suppliers Inc."
    },
    {
      "ingredient_name": "Raspberry",
      "unit_name": "gram",
      "quantity": 15000,
      "vendor": "Local Berry Farm"
    }
  ]
}
EOF
)
PO1_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
  "$PO1_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$PO1_RESP" >&2

# Extract PO code for later tests
PO_CODE=$(echo "$PO1_RESP" | grep -o '"po_code":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Using PO_CODE = $PO_CODE for subsequent tests" >&2
echo >&2

# 2) Create another purchase order (Store 02 - Berry order)
TEST_NAME="Create Purchase Order (STORE02 - Berry Mix)"
PO2_BODY=$(cat <<EOF
{
  "order_date": "$TODAY",
  "store_id": "STORE02",
  "items": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "gram",
      "quantity": 8000,
      "vendor": "Local Berry Farm"
    },
    {
      "ingredient_name": "Blueberry",
      "unit_name": "kilogram",
      "quantity": 12.0,
      "vendor": "Local Berry Farm"
    }
  ]
}
EOF
)
PO2_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
  "$PO2_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$PO2_RESP" >&2
echo >&2

# 3) Create purchase order without vendor (optional field)
TEST_NAME="Create Purchase Order (No Vendor)"
PO3_BODY=$(cat <<EOF
{
  "order_date": "$TODAY",
  "store_id": "STORE01",
  "items": [
    {
      "ingredient_name": "Raspberry",
      "unit_name": "kilogram",
      "quantity": 5.5
    }
  ]
}
EOF
)

PO3_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
  "$PO3_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$PO3_RESP" >&2
echo >&2

# 4) List all purchase orders
TEST_NAME="List All Purchase Orders"
LIST_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${RECEIVING_PREFIX}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "List response:" >&2
echo "$LIST_RESP" >&2
echo >&2

# 5) Filter by date range
TEST_NAME="Filter Purchase Orders by Date"
FILTER_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${RECEIVING_PREFIX}?date_from=${TODAY}&date_to=${TODAY}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Filter response:" >&2
echo "$FILTER_RESP" >&2
echo >&2

# 6) Filter by store_id
TEST_NAME="Filter Purchase Orders by Store (STORE01)"
STORE_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${RECEIVING_PREFIX}?store_id=STORE01" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Store filter response:" >&2
echo "$STORE_RESP" >&2
echo >&2

# 7) Get purchase order by PO code
if [[ -n "$PO_CODE" ]]; then
  TEST_NAME="Get Purchase Order by Code ($PO_CODE)"
  # URL-encode the PO code if needed
  ENCODED_PO_CODE="${PO_CODE// /%20}"
  GET_RESP=$(run_test "$TEST_NAME" "GET" \
    "${BASE_URL}${RECEIVING_PREFIX}/${ENCODED_PO_CODE}" "")
  test_result=$?
  [[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

  echo "Get by code response:" >&2
  echo "$GET_RESP" >&2
  echo >&2
else
  echo "⚠️  Skipping GET by code test - no PO code available" >&2
  echo >&2
fi

# 8) Validation test: Try to create order with future date
TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d tomorrow +%Y-%m-%d 2>/dev/null || echo "2026-12-31")
TEST_NAME="Validation Test: Future Date (Should Fail)"
FUTURE_BODY=$(cat <<EOF
{
  "order_date": "$TOMORROW",
  "store_id": "STORE01",
  "items": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "kilogram",
      "quantity": 10.0,
      "vendor": "Test Vendor"
    }
  ]
}
EOF
)
FUTURE_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
  "$FUTURE_BODY")
test_result=$?

# This test expects a 400 error
if [[ $test_result -ne 0 ]]; then
  echo -e "${GREEN}✅ PASS - Validation correctly rejected future date${RESET}" >&2
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo -e "${RED}❌ FAIL - Should have rejected future date${RESET}" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo >&2

# 10) Validation test: Invalid ingredient
TEST_NAME="Validation Test: Invalid Ingredient (Should Fail)"
INVALID_ING_BODY=$(cat <<EOF
{
  "order_date": "$TODAY",
  "store_id": "STORE01",
  "items": [
    {
      "ingredient_name": "NonExistentIngredient",
      "unit_name": "kilogram",
      "quantity": 10.0
    }
  ]
}
EOF
)
INVALID_ING_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
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

# 11) Validation test: Invalid unit for category
TEST_NAME="Validation Test: Invalid Unit for Category (Should Fail)"
INVALID_UNIT_BODY=$(cat <<EOF
{
  "order_date": "$TODAY",
  "store_id": "STORE01",
  "items": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "liter",
      "quantity": 10.0
    }
  ]
}
EOF
)
INVALID_UNIT_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
  "$INVALID_UNIT_BODY")
test_result=$?

if [[ $test_result -ne 0 ]]; then
  echo -e "${GREEN}✅ PASS - Validation correctly rejected invalid unit${RESET}" >&2
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo -e "${RED}❌ FAIL - Should have rejected invalid unit${RESET}" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo >&2

# 12) Validation test: Zero quantity
TEST_NAME="Validation Test: Zero Quantity (Should Fail)"
ZERO_QTY_BODY=$(cat <<EOF
{
  "order_date": "$TODAY",
  "store_id": "STORE01",
  "items": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "kilogram",
      "quantity": 0
    }
  ]
}
EOF
)
ZERO_QTY_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${RECEIVING_PREFIX}" \
  "$ZERO_QTY_BODY")
test_result=$?

if [[ $test_result -ne 0 ]]; then
  echo -e "${GREEN}✅ PASS - Validation correctly rejected zero quantity${RESET}" >&2
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo -e "${RED}❌ FAIL - Should have rejected zero quantity${RESET}" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo >&2

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
