import sys

class GSharePredictor:
    def __init__(self, M, N):
        self.M = M  # Table size
        self.N = N  # History length
        self.gbh = 0  # Global Branch History register (N bits)
        self.pht_size = 1 << M  # 2^M entries
        self.pht = [2] * self.pht_size  # Initialize all counters to 2 (Weakly Taken)
        self.predictions = 0
        self.mispredictions = 0
    
    # These are the steps to make prediction
    def make_prediction(self, program_counter):
        # Step 1: Remove 2 LSBs and get M bits from PC
        pc_without_lsbs = program_counter >> 2
        extracted_pc_bits = pc_without_lsbs & ((1 << self.M) - 1)
        
        # Step 2: Prepare M-bit history by shifting GBH
        if self.N == 0:
            shifted_history = 0 # No history when N = 0
        else: 
            shifted_history = self.gbh << (self.M - self.N)
        # Step 3: Calculate final index using XOR
        pht_index = extracted_pc_bits ^ shifted_history
        
        # Step 4: Make prediction
        predictor_value = self.pht[pht_index]
        predicted_taken = (predictor_value >= 2)
        
        return pht_index, predicted_taken
    
    def update_predictor(self, pht_index, actual_taken):
        # Update PHT counter
        current_counter = self.pht[pht_index]
        if actual_taken:
            current_counter = min(3, current_counter + 1)  # Saturate at 3
        else:
            current_counter = max(0, current_counter - 1)  # Saturate at 0
        self.pht[pht_index] = current_counter
        
        # Update Global Branch History (only if N > 0)
        if self.N > 0:
            # Shift right by 1 bit
            self.gbh = self.gbh >> 1
            # Insert actual outcome at MSB
            if actual_taken:
                self.gbh = self.gbh | (1 << (self.N - 1))
    
    def process_branch(self, program_counter, branch_result):
        # Validate input first
        if branch_result not in ('t', 'n'):
            print(f"Warning: Invalid outcome '{branch_result}' for PC {program_counter:08x}")
            return
        
        self.predictions += 1
        # Convert outcome to boolean
        actual_taken = (branch_result == 't')
        # Make prediction
        pht_index, predicted_taken = self.make_prediction(program_counter)
        # Check for misprediction
        if predicted_taken != actual_taken:
            self.mispredictions += 1
        # Update predictor
        self.update_predictor(pht_index, actual_taken)
    
    def get_misprediction_rate(self):
        if self.predictions == 0:
            return 0.0
        return (self.mispredictions / self.predictions) * 100  # Convert to percentage

def parse_trace_line(input_line):
    line_parts = input_line.strip().split()
    if len(line_parts) < 2:
        return None, None
    
    try:
        address_value = int(line_parts[0], 16)  # Convert hex to integer
        branch_outcome = line_parts[1].lower()
        if branch_outcome not in ['t', 'n']:
            return None, None
        return address_value, branch_outcome
    except ValueError:
        return None, None

# Check to see if the command has 5 arguments
def main():
    if len(sys.argv) != 5:
        print("Error: Wrong number of arguments")
        print("Correct format on Mac: python sim.py gshare <M> <N> <trace_file>")
        print("Example: python sim.py gshare 4 2 mcf_trace.txt")
        sys.exit(1)
    
    predictor_type, m_value_str, n_value_str, input_filename = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    if predictor_type != "gshare":
        print(f"Error: Unsupported mode '{predictor_type}'. Only 'gshare' is available.")
        sys.exit(1)
    
    try:
        m_parameter = int(m_value_str)
        n_parameter = int(n_value_str)
    except ValueError:
        print(f"Error: M and N must be integers")
        sys.exit(1)
    
    if m_parameter <= 0:
        print(f"Error: M must be positive")
        sys.exit(1)
    
    if n_parameter < 0:
        print(f"Error: N cannot be negative")
        sys.exit(1)
        
    if n_parameter > m_parameter:
        print(f"Error: N ({n_parameter}) cannot be greater than M ({m_parameter})")
        sys.exit(1)
    
    # Initialize predictor
    predictor = GSharePredictor(m_parameter, n_parameter)
    
    # Check the trace files here and show errors if anything's wrong
    try:
        with open(input_filename, 'r') as input_file:
            for current_line_number, current_line_content in enumerate(input_file, 1):
                parsed_data = parse_trace_line(current_line_content)
                if parsed_data is None:
                    if current_line_content.strip():
                        print(f"Warning: Skipping invalid line {current_line_number}: {current_line_content.strip()}")
                    continue
                
                program_counter_value, branch_outcome_value = parsed_data
                predictor.process_branch(program_counter_value, branch_outcome_value)

    except FileNotFoundError:
        print(f"Error: Trace file '{input_filename}' not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: No permission to read '{input_filename}'")
        sys.exit(1)
    except Exception as error_details:
        print(f"Error reading trace file: {error_details}")
        sys.exit(1)
    
    # Output
    misprediction_rate = predictor.get_misprediction_rate()
    
    # Print the output
    print(f"{m_parameter} {n_parameter} {misprediction_rate:.2f}")

if __name__ == "__main__":
    main()