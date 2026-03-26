#!/usr/bin/env bash

# Simple integration test for admin_setup_router
# Usage: chmod +x test_admin_setup.sh && ./test_admin_setup.sh

BASE_URL="http://localhost:8000"        # 如果有 /api 前缀，改成 http://localhost:8000/api
SETUP_PREFIX="/admin/setup"

GREEN="\033[32m"
RED="\033[31m"
YELLOW="\033[33m"
RESET="\033[0m"

PASS_COUNT=0
FAIL_COUNT=0

CATEGORY_NAME=""
ALLERGEN_ID=""

# Run test that treats "already exists" as success (idempotent create)
# Returns: 0 for pass, 1 for fail
run_test_idempotent() {
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

  # Check if it's a 2xx success OR a 400 with "already exists"
  if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
    echo -e "${GREEN}✅ PASS${RESET} [$http_code] - $name" >&2
    exit_code=0
  elif [[ "$http_code" == "400" && "$body_content" == *"already exists"* ]]; then
    echo -e "${GREEN}✅ PASS${RESET} [$http_code] - $name (already exists, skipped)" >&2
    exit_code=0
  else
    echo -e "${RED}❌ FAIL${RESET} [$http_code] - $name" >&2
    echo "Response body:" >&2
    echo "$body_content" >&2
    echo >&2
    exit_code=1
  fi

  # stdout 只输出 body，方便外面用 $(...) 捕获纯 JSON
  echo "$body_content"
  rm -f "$tmp_body"
  return $exit_code
}

# ---- Helpers ----

# Returns: 0 for pass, 1 for fail
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

  local exit_code

  # 判定成功：2xx 都算 PASS
  if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
    echo -e "${GREEN}✅ PASS${RESET} [$http_code] - $name" >&2
    exit_code=0
  else
    echo -e "${RED}❌ FAIL${RESET} [$http_code] - $name" >&2
    echo "Response body:" >&2
    cat "$tmp_body" >&2
    echo >&2
    exit_code=1
  fi

  # stdout 只输出 body，方便外面用 $(...) 捕获纯 JSON
  cat "$tmp_body"
  rm -f "$tmp_body"
  return $exit_code
}

# 用 Python 从 JSON 里取字段
extract_json_field() {
  local json="$1"
  local field="$2"
  python3 -c 'import sys, json
field = sys.argv[1]
text = sys.stdin.read()
try:
    data = json.loads(text)
    value = data.get(field)
    if value is not None:
        print(value)
except Exception:
    pass
' "$field" <<< "$json"
}

# ---- Tests ----

echo "Starting admin_setup_router integration tests..." >&2
echo "Base URL: ${BASE_URL}${SETUP_PREFIX}" >&2
echo >&2

# 1) Create Units (Batch) - 不解析 id，只看能否成功
TEST_NAME="Create Units (Batch)"
UNIT_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${SETUP_PREFIX}/units" \
  '[
     {"name": "kilogram", "abbreviation": "kg"},
     {"name": "pound", "abbreviation": "lb"},
     {"name": "gram", "abbreviation": "g"},
     {"name": "ounce", "abbreviation": "oz"}
   ]')
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Batch create units response:" >&2
echo "$UNIT_RESP" >&2
echo >&2

# 2) List Units to verify
TEST_NAME="List Units"
UNITS_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${SETUP_PREFIX}/units" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
echo "Units list response:" >&2
echo "$UNITS_RESP" >&2
echo >&2

# 3) Create Category (Fruit) using unit_names instead of unit_ids
TEST_NAME="Create Category (Fruit)"
CATEGORY_NAME="Fruit"
CATEGORY_BODY=$(cat <<EOF
{
  "name": "${CATEGORY_NAME}",
  "tag": "Whole foods",
  "unit_names": ["kilogram", "pound", "gram"]
}
EOF
)
CAT_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${SETUP_PREFIX}/categories" \
  "$CATEGORY_BODY")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "DEBUG: Category creation response:" >&2
echo "$CAT_RESP" >&2
echo "---" >&2
echo "Using CATEGORY_NAME = $CATEGORY_NAME for subsequent tests" >&2
echo >&2

# 4) List Categories
TEST_NAME="List Categories"
CATEGORIES_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${SETUP_PREFIX}/categories" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
echo "Categories list response:" >&2
echo "$CATEGORIES_RESP" >&2
echo >&2



# 5) Ensure Allergen (Milk) exists
TEST_NAME="Ensure Allergen (Milk) Exists"
ALLERGEN_RESP=$(run_test_idempotent "$TEST_NAME" "POST" \
  "${BASE_URL}${SETUP_PREFIX}/allergens" \
  '{
     "name": "milk"
   }')
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "DEBUG: Allergen creation/ensure response:" >&2
echo "$ALLERGEN_RESP" >&2
echo "---" >&2

# 6) List Allergens
TEST_NAME="List Allergens"
ALLERGENS_RESP=$(run_test "$TEST_NAME" "GET" \
  "${BASE_URL}${SETUP_PREFIX}/allergens" "")
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))
echo "Allergens list response:" >&2
echo "$ALLERGENS_RESP" >&2
echo >&2


# 7) Update Category tag using category name
TEST_NAME="Update Category Tag"
if [[ -z "$CATEGORY_NAME" ]]; then
  echo -e "${RED}跳过${RESET} $TEST_NAME，因为 CATEGORY_NAME 为空（创建分类失败）" >&2
  FAIL_COUNT=$((FAIL_COUNT + 1))
else
  UPDATE_BODY=$(cat <<EOF
{
  "tag": "Fresh produce",
  "unit_names": ["kilogram", "pound", "gram", "ounce"]
}
EOF
)
  UPDATE_RESP=$(run_test "$TEST_NAME" "PUT" \
    "${BASE_URL}${SETUP_PREFIX}/categories/${CATEGORY_NAME}" \
    "$UPDATE_BODY")
  test_result=$?
  [[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

  echo "Category update response:" >&2
  echo "$UPDATE_RESP" >&2
  echo >&2
fi

# 8) Test batch create with duplicates (should skip existing or handle gracefully)
TEST_NAME="Create Units (With Duplicates - Should Skip or Return 2xx)"
DUP_RESP=$(run_test "$TEST_NAME" "POST" \
  "${BASE_URL}${SETUP_PREFIX}/units" \
  '[
     {"name": "kilogram", "abbreviation": "kg"},
     {"name": "liter", "abbreviation": "L"},
     {"name": "milliliter", "abbreviation": "mL"}
   ]')
test_result=$?
[[ $test_result -eq 0 ]] && PASS_COUNT=$((PASS_COUNT + 1)) || FAIL_COUNT=$((FAIL_COUNT + 1))

echo "Duplicate batch create units response:" >&2
echo "$DUP_RESP" >&2
echo >&2

# ---- Summary ----
echo >&2
echo "================= TEST SUMMARY =================" >&2
echo -e "${GREEN}PASS: ${PASS_COUNT}${RESET}" >&2
echo -e "${RED}FAIL: ${FAIL_COUNT}${RESET}" >&2
echo "================================================" >&2
echo "Done." >&2
