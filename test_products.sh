#!/usr/bin/env bash

# Test script for semi-finished products (prepped items) endpoints
# Usage: chmod +x test_products.sh && ./test_products.sh

BASE_URL="http://localhost:8000"
PRODUCTS_PREFIX="/prepped-items"

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
echo "Testing Semi-Finished Products Endpoints"
echo "==========================================="
echo

# 0) Setup: Ensure we have ingredients (from previous tests)
echo "=== Prerequisite Check ===" >&2
echo "Make sure you have run test_ingredients.sh first to create:" >&2
echo "  - Fruit category with units" >&2
echo "  - Strawberry, Blueberry, Raspberry ingredients" >&2
echo >&2

# Cleanup: Delete existing test products if they exist
echo "=== Cleanup: Deleting existing test products ===" >&2
curl -s -X DELETE "${BASE_URL}${PRODUCTS_PREFIX}/Strawberry%20Compote" > /dev/null 2>&1
curl -s -X DELETE "${BASE_URL}${PRODUCTS_PREFIX}/Berry%20Mix" > /dev/null 2>&1
curl -s -X DELETE "${BASE_URL}${PRODUCTS_PREFIX}/Invalid%20Product" > /dev/null 2>&1
echo "Cleanup complete" >&2
echo >&2

# 1) Create semi-finished product (Strawberry Compote)
TEST_NAME="Create Semi-Finished Product (Strawberry Compote)"
PRODUCT_BODY=$(cat <<EOF
{
  "name": "Strawberry Compote",
  "prep_time_hours": 1.5,
  "ingredients": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "kilogram",
      "quantity": 2.0
    },
    {
      "ingredient_name": "Blueberry",
      "unit_name": "gram",
      "quantity": 500
    }
  ]
}
EOF
)
PRODUCT_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${PRODUCTS_PREFIX}" \
  "$PRODUCT_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$PRODUCT_RESP" >&2
echo >&2

PRODUCT_NAME="Strawberry Compote"
echo "Using PRODUCT_NAME = $PRODUCT_NAME for subsequent tests" >&2
echo >&2

# 2) Create another semi-finished product (Berry Mix)
TEST_NAME="Create Semi-Finished Product (Berry Mix)"
PRODUCT2_BODY=$(cat <<EOF
{
  "name": "Berry Mix",
  "prep_time_hours": 0.5,
  "ingredients": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "gram",
      "quantity": 300
    },
    {
      "ingredient_name": "Blueberry",
      "unit_name": "gram",
      "quantity": 200
    },
    {
      "ingredient_name": "Raspberry",
      "unit_name": "gram",
      "quantity": 250
    }
  ]
}
EOF
)
PRODUCT2_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${PRODUCTS_PREFIX}" \
  "$PRODUCT2_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Response:" >&2
echo "$PRODUCT2_RESP" >&2
echo >&2

# 3) List all semi-finished products
TEST_NAME="List All Semi-Finished Products"
LIST_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${PRODUCTS_PREFIX}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "List response:" >&2
echo "$LIST_RESP" >&2
echo >&2

# 4) Search semi-finished products by name
TEST_NAME="Search Semi-Finished Products (name=Berry)"
SEARCH_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${PRODUCTS_PREFIX}?name=Berry" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Search response:" >&2
echo "$SEARCH_RESP" >&2
echo >&2

# 5) Get semi-finished product by name
TEST_NAME="Get Semi-Finished Product by Name (Strawberry Compote)"
# URL-encode the product name (replace spaces with %20)
ENCODED_PRODUCT_NAME="${PRODUCT_NAME// /%20}"
GET_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${PRODUCTS_PREFIX}/${ENCODED_PRODUCT_NAME}" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Get by name response:" >&2
echo "$GET_RESP" >&2
echo >&2

# 6) Update semi-finished product
TEST_NAME="Update Semi-Finished Product"
UPDATE_BODY=$(cat <<EOF
{
  "prep_time_hours": 2.0,
  "ingredients": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "kilogram",
      "quantity": 2.5
    },
    {
      "ingredient_name": "Blueberry",
      "unit_name": "kilogram",
      "quantity": 0.8
    },
    {
      "ingredient_name": "Raspberry",
      "unit_name": "gram",
      "quantity": 300
    }
  ]
}
EOF
)
UPDATE_RESP=$(run_test "$TEST_NAME" "PUT" \
  "${BASE_URL}${PRODUCTS_PREFIX}/${ENCODED_PRODUCT_NAME}" \
  "$UPDATE_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Update response:" >&2
echo "$UPDATE_RESP" >&2
echo >&2

# 7) Test validation: Try to create with invalid unit
TEST_NAME="Validation Test: Invalid Unit for Category"
INVALID_BODY=$(cat <<EOF
{
  "name": "Invalid Product",
  "prep_time_hours": 1.0,
  "ingredients": [
    {
      "ingredient_name": "Strawberry",
      "unit_name": "liter",
      "quantity": 1.0
    }
  ]
}
EOF
)
INVALID_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${PRODUCTS_PREFIX}" \
  "$INVALID_BODY")
test_result=$?
# This should fail (400), so we invert the logic
if [[ $test_result -eq 1 ]]; then
  echo -e "${GREEN}✅ PASS${RESET} - Validation correctly rejected invalid unit" >&2
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo -e "${RED}❌ FAIL${RESET} - Should have rejected invalid unit" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi
echo >&2

# Summary
echo >&2
echo "================= TEST SUMMARY =================" >&2
echo -e "${GREEN}PASS: ${PASS_COUNT}${RESET}" >&2
echo -e "${RED}FAIL: ${FAIL_COUNT}${RESET}" >&2
echo "================================================" >&2
echo "Done." >&2
