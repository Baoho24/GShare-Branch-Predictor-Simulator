The project evaluates branch prediction accuracy using program execution traces and demonstrates how shared history and prediction tables impact performance.


# Features
- Simulates shared branch prediction mechanisms
- Supports branch trace–driven simulation
- Tracks prediction accuracy and misprediction rate

## How It Works
1. Reads a branch trace containing branch outcomes  
2. Uses a shared prediction structure to make predictions  
3. Updates prediction state based on actual outcomes  
4. Computes accuracy and misprediction statistics  

---

## How to run the program
There are 2 different trace files, replace the trace_file.txt with the actual name before running:
python SIM.py [trace_file.txt]
