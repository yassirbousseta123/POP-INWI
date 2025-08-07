# Door Cycle Detection Issue Report

## Glossary of Technical Terms

### Door Cycle
A **door cycle** is a complete sequence of door operation consisting of:
1. **Opening Event**: The moment when the door transitions from closed to open state
2. **Open Period**: The duration when the door remains open
3. **Closing Event**: The moment when the door transitions from open to closed state

**Example**: If a door opens at 10:00 AM and closes at 10:15 AM, this represents one complete cycle with a duration of 15 minutes.

### Door Status Values
- **`1.0`**: Indicates the door is in OPEN state
- **`NaN` (Not a Number)**: Indicates the door is in CLOSED state (absence of signal)
- **Transition**: A change from one state to another (e.g., closed→open or open→closed)

### State Transition
A **state transition** occurs when the door changes from one state to another:
- **Open Transition (0→1)**: Door changes from closed to open
- **Close Transition (1→0)**: Door changes from open to closed

## Issue Summary
The door cycle detection algorithm was incorrectly counting 17,874 cycles with all durations set to 30 minutes, when the actual number of door open/close cycles should be significantly lower.

## Root Cause Analysis

### 1. Original Problem: Incorrect Cycle Counting
The original implementation was counting every single row with `Porte_Status = 1.0` as a separate open event, rather than detecting actual transitions between open and closed states.

#### Original Code (Problematic):
```python
# This counted every row with status 1.0 as an open event
open_events = actual_door_events[actual_door_events['Porte_Status'] == 1]['Timestamp'].tolist()
close_events = actual_door_events[actual_door_events['Porte_Status'] == 0]['Timestamp'].tolist()
```

### 2. Data Structure Issue
The door status data has the following characteristics:
- `1.0` = Door is open
- `NaN` = Door is closed (not explicitly 0)
- Data is sparse: only state changes are recorded

#### Example Data Pattern:
```
Timestamp                | Porte_Status | Interpretation
2024-01-01 10:00:00     | NaN          | Door closed
2024-01-01 10:15:00     | 1.0          | Door opens
2024-01-01 10:15:30     | 1.0          | Door still open
2024-01-01 10:16:00     | 1.0          | Door still open
2024-01-01 10:20:00     | NaN          | Door closes
2024-01-01 10:30:00     | NaN          | Door still closed
2024-01-01 10:45:00     | 1.0          | Door opens again
```

### 3. Fixed Duration Issue
All cycles were being assigned a default 30-minute duration when no matching close event was found:

```python
# Original problematic code
if close_time is None:
    close_time = open_time + timedelta(minutes=30)  # Always 30 minutes!
```

## Implemented Solution

### 1. New Transition Detection Logic
The fix implements proper state transition detection:

```python
# New implementation - detect actual transitions
porte_data['Porte_Status_Clean'] = porte_data['Porte_Status'].fillna(0)
porte_data['Previous_Status'] = porte_data['Porte_Status_Clean'].shift(1)

# Detect open transitions (0 → 1)
open_mask = (porte_data['Previous_Status'] == 0) & (porte_data['Porte_Status_Clean'] == 1)
open_events = porte_data[open_mask]['Timestamp'].tolist()

# Detect close transitions (1 → 0)
close_mask = (porte_data['Previous_Status'] == 1) & (porte_data['Porte_Status_Clean'] == 0)
close_events = porte_data[close_mask]['Timestamp'].tolist()

# Handle edge case: if first value is 1, it's an opening
if porte_data.iloc[0]['Porte_Status_Clean'] == 1:
    open_events.insert(0, porte_data.iloc[0]['Timestamp'])
```

### 2. Improved Cycle Duration Calculation
Instead of defaulting to 30 minutes, the new logic:

```python
if close_time is None:
    # Look for next open event
    next_open_time = None
    if i + 1 < len(open_events):
        next_open_time = open_events[i + 1]
    
    if next_open_time:
        # Use time until next opening
        close_time = next_open_time - timedelta(seconds=1)
        cycle_duration = (close_time - open_time).total_seconds() / 60
    else:
        # Only for last incomplete cycle, use minimal duration
        close_time = open_time + timedelta(minutes=5)
        cycle_duration = 5
```

## Expected Results

### Before Fix:
- **Cycles detected**: 17,874 (incorrect - counting every row with status 1.0)
- **All cycle durations**: 30 minutes (incorrect - hardcoded default)
- **Logic flaw**: Not detecting actual open→close transitions
- **Why wrong**: Each data point with value 1.0 was counted as a separate cycle

### After Fix:
- **Cycles detected**: Actual number of door open→close sequences
- **Cycle durations**: Real durations based on actual close events
- **Proper logic**: Detects state transitions, not individual records
- **Why correct**: Only counts transitions from closed→open as cycle starts

### Real-World Example:
If a door opens 5 times during a day:
- **Before**: Could show 17,874 cycles (if there are that many 1.0 readings)
- **Expected After Fix**: Shows 5 cycles (the actual number of times the door opened and closed)
- **Current Reality**: Only 1 cycle is detected (still incorrect!)

## Data Visualization

### Cycle Detection Visualization

#### Correct Cycle Detection (After Fix):
```
Time →
─────────────────────────────────────────────────────
Door State:  Closed | Open    | Closed | Open  | Closed
Raw Data:    NaN    | 1.0 1.0 | NaN    | 1.0   | NaN
                    ↑         ↑        ↑       ↑
                    Open      Close    Open    Close
                    Event     Event    Event   Event
                    
Cycles:             |←Cycle 1→|        |←Cycle 2→|
Result: 2 cycles detected ✓
```

#### Incorrect Cycle Detection (Before Fix):
```
Time →
─────────────────────────────────────────────────────
Door State:  Closed | Open    | Closed | Open  | Closed
Raw Data:    NaN    | 1.0 1.0 | NaN    | 1.0   | NaN
                    ↑   ↑   ↑          ↑
                    Cycle Cycle        Cycle
                    1    2   3         4
                    
Result: 4 cycles detected (WRONG! - counting each 1.0 as a cycle)
All durations: 30 minutes (hardcoded default)
```

### Debug Information Added
The implementation includes comprehensive debugging:

1. **Data Distribution Display**:
   - Total rows in dataset
   - Count of non-NaN values
   - Value distribution after cleaning

2. **Transition Detection Display**:
   - Shows detected transitions with timestamps
   - Previous vs current status for each transition
   - Total count of open/close events

3. **Cycle Processing Summary**:
   - Total cycles detected
   - Cycles without matching close events
   - Cycles without temperature data
   - Valid cycles with complete data

## Testing Recommendations

1. **Verify with sample data** that has known open/close patterns
2. **Check edge cases**:
   - First record is door open
   - Last record is door open (incomplete cycle)
   - Multiple consecutive open or close events
   - Long gaps between events

3. **Validate cycle durations** match actual time between open and close events

## Impact on Temperature Analysis

### Why Door Cycles Matter
In a refrigeration system, door cycles directly impact temperature:
1. **Temperature Rise**: When door opens, warm air enters, causing temperature to increase
2. **Recovery Period**: After door closes, cooling system works to restore target temperature
3. **Energy Consumption**: Each cycle requires additional energy to re-cool the space

### Importance of Accurate Cycle Detection
- **Incorrect** (17,874 cycles): Suggests extremely frequent door usage, making analysis meaningless
- **Correct** (actual cycles): Allows proper analysis of:
  - Average temperature impact per door opening
  - Recovery time after door closure
  - Energy cost per door cycle
  - Optimization opportunities

## Current Status: Issue Persists

### Despite the implemented fix, the problem is NOT fully resolved:
- **Original Issue**: 17,874 cycles detected (way too many)
- **After Fix**: Only 1 cycle detected (way too few)
- **Expected**: Should detect multiple cycles based on actual door usage

### This indicates potential issues with:
1. **Data Format**: The door status values might not be what we expect
2. **Transition Logic**: The current implementation might be too restrictive
3. **Data Quality**: There might be gaps or inconsistencies in the data
4. **Edge Cases**: The algorithm might not handle all scenarios properly

## Recommended Next Steps

1. **Deep Data Analysis**:
   - Examine raw door status data over a longer time period
   - Check for patterns in how door events are recorded
   - Verify the actual values present in the data

2. **Algorithm Review**:
   - Consider alternative approaches for cycle detection
   - Handle cases where door events might be recorded differently
   - Account for data gaps or missing values

3. **Testing with Known Data**:
   - Create test cases with known door open/close patterns
   - Validate the algorithm against these test cases
   - Identify where the detection fails

## Conclusion

The implemented fix improved the logic but did not fully resolve the issue:
1. **Progress Made**: Moved from counting every data point to detecting transitions
2. **Current Problem**: Only 1 cycle detected instead of the expected multiple cycles
3. **Root Cause**: Still under investigation - likely related to data format or edge cases

### Status Summary
- **From**: 17,874 false cycles (one per data point) ❌
- **Current**: 1 cycle detected (too few) ❌
- **Target**: Actual number of door open/close cycles ⏳

This indicates that while the approach is better, further investigation and refinement of the cycle detection algorithm is needed to accurately capture all door cycles in the system.