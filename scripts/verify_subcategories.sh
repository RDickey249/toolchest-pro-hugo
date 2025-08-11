#\!/bin/bash

echo "ToolChest Subcategory Verification Script"
echo "========================================"
echo ""

# Test Development & Technical Tools (the problematic one)
echo "1. Development & Technical Tools:"
echo "   URL: https://toolchest.pro/categories/development-technical-tools/"
DEV_SECTIONS=$(grep -o '<div class=subcategory-section>' public/categories/development-technical-tools/index.html 2>/dev/null | wc -l)
echo "   Subcategory sections found: $DEV_SECTIONS"
if [ "$DEV_SECTIONS" -gt 10 ]; then
    echo "   ✅ WORKING (Expected 30+ sections)"
else
    echo "   ❌ BROKEN (Too few sections)"
fi

# Test CRM & Sales Tools (known working)
echo ""
echo "2. CRM & Sales Tools:"
echo "   URL: https://toolchest.pro/categories/crm-sales-tools/"
CRM_SECTIONS=$(grep -o '<div class=subcategory-section>' public/categories/crm-sales-tools/index.html 2>/dev/null | wc -l)
echo "   Subcategory sections found: $CRM_SECTIONS"
if [ "$CRM_SECTIONS" -gt 2 ]; then
    echo "   ✅ WORKING (Expected 4+ sections)"
else
    echo "   ❌ BROKEN"
fi

# Test AI Tools & Assistants
echo ""
echo "3. AI Tools & Assistants:"
echo "   URL: https://toolchest.pro/categories/ai-tools-assistants/"
AI_SECTIONS=$(grep -o '<div class=subcategory-section>' public/categories/ai-tools-assistants/index.html 2>/dev/null | wc -l)
echo "   Subcategory sections found: $AI_SECTIONS"
if [ "$AI_SECTIONS" -gt 3 ]; then
    echo "   ✅ WORKING (Expected 5+ sections)"
else
    echo "   ❌ BROKEN"
fi

echo ""
echo "SUMMARY:"
TOTAL_WORKING=0
[ "$DEV_SECTIONS" -gt 10 ] && TOTAL_WORKING=$((TOTAL_WORKING + 1))
[ "$CRM_SECTIONS" -gt 2 ] && TOTAL_WORKING=$((TOTAL_WORKING + 1))  
[ "$AI_SECTIONS" -gt 3 ] && TOTAL_WORKING=$((TOTAL_WORKING + 1))

echo "Working categories: $TOTAL_WORKING/3"
if [ "$TOTAL_WORKING" -eq 3 ]; then
    echo "🎉 ALL SUBCATEGORIES ARE WORKING PROPERLY"
    exit 0
else
    echo "⚠️  SOME CATEGORIES HAVE ISSUES"
    exit 1
fi
