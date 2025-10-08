# GitHub Auto-Follow Bot with Smart Rate Limit Handling

Automatically follows GitHub users from a list file with built-in spot checking, automatic rate limit handling, and 30-minute auto-wait when limits are reached.

## 🌟 Key Features

✅ **Bulk Follow** - Follow multiple users from a text file  
✅ **Auto Rate Limit Handling** - Automatically waits 30 minutes when rate limit is hit  
✅ **Smart Retry** - Automatically retries after wait period  
✅ **Spot Check System** - Verifies follower count every 10 successful follows  
✅ **Progress Tracking** - Real-time progress with counter and status  
✅ **Skip Already Following** - Automatically skips users you already follow  
✅ **Countdown Timer** - Shows remaining wait time in minutes and seconds  
✅ **Error Handling** - Gracefully handles API errors and restrictions  
✅ **Session Summary** - Shows starting/ending follower count and net gain  
✅ **Interruptible** - Press Ctrl+C anytime to safely stop  

## 🚀 What Makes This Special?

### 1. **Automatic Rate Limit Recovery** ⏰
When GitHub's API rate limit is reached, the script:
- Automatically detects the rate limit
- Calculates exact wait time needed
- Shows countdown timer with remaining time
- Automatically resumes following after wait
- No manual intervention needed!

### Example Log Output
```markdown
⚠️ API limit reached. Reset at: 2025-10-07 15:30:00
⏰ Auto-waiting for 30 minutes before resuming...
💡 You can press Ctrl+C to stop the script if needed.
⏳ Pausing for 29m 45s... Press Ctrl+C to exit.
```

### 2. **Intelligent Spot Checking** 🔍
Verifies your followers every 10 follows to ensure everything works:
- Compares expected vs actual follower increase
- Provides detailed analysis of results
- Helps detect issues early
- Shows pass/partial/fail status

### 3. **User-Friendly Interface** 🎨
- Clear progress indicators
- Professional formatting with boxes and emojis
- Real-time countdown timers
- Detailed success/failure messages
- Comprehensive final summary

## 📋 Requirements

### System Requirements
```
