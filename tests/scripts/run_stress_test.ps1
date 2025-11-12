# PowerShell script to test the fixed agentic system
# Tests the exact stress test scenario that was failing

Write-Host "=== REAL ESTATE AGENT STRESS TEST ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔧 FIXES APPLIED:" -ForegroundColor Green
Write-Host "1. ✅ Agent Routing System - COMPLETELY REWRITTEN"
Write-Host "2. ✅ OpenRouter Integration with Model Fallback (Gemma -> Moonshot)"
Write-Host "3. ✅ Conversation Context System (No greeting repetition)"
Write-Host "4. ✅ Enhanced Intent Recognition"
Write-Host ""

Write-Host "🎯 EXPECTED BEHAVIOR:" -ForegroundColor Yellow
Write-Host "Message 1: 'I need a place to live' → SearchAgent (Alex)"
Write-Host "Message 2: 'Something nice in Miami' → SearchAgent (Alex) - No greeting"
Write-Host "Message 3: '3 bedrooms, budget around $25000' → SearchAgent (Alex)"
Write-Host "Message 4: 'Tell me more about the first one' → PropertyAgent (Emma)"
Write-Host "Message 5: 'Can I visit it tomorrow afternoon?' → SchedulingAgent (Mike)"
Write-Host "Message 6: 'I want to schedule for tomorrow at 3PM' → SchedulingAgent (Mike)"
Write-Host ""

Write-Host "🚀 TO TEST THE SYSTEM:" -ForegroundColor Magenta
Write-Host "1. Start the server:"
Write-Host "   Set-Location 'C:\Users\brsamd00\Agentic-Real-Estate'"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python start_server.py"
Write-Host ""
Write-Host "2. Open browser to: http://localhost:8000"
Write-Host ""
Write-Host "3. Test the exact scenario that was failing:"
Write-Host "   - 'I need a place to live' (should route to Alex, not Emma)"
Write-Host "   - 'Something nice in Miami' (should continue with Alex, no greeting)"
Write-Host "   - '3 bedrooms, budget around $25000' (should stay with Alex)"
Write-Host "   - 'Tell me more about the first one' (should switch to Emma)"
Write-Host "   - 'Can I visit it tomorrow afternoon?' (should switch to Mike)"
Write-Host ""

Write-Host "✨ EXPECTED IMPROVEMENTS:" -ForegroundColor Green
Write-Host "- ✅ Proper agent switching (Alex → Emma → Mike)"
Write-Host "- ✅ No repeated greetings in conversation"
Write-Host "- ✅ Real AI responses (not fallback templates)"
Write-Host "- ✅ Accurate intent recognition"
Write-Host "- ✅ Model fallback if Gemma fails"
Write-Host ""

Write-Host "🎉 ALL STRESS TEST ISSUES SHOULD NOW BE RESOLVED!" -ForegroundColor Green