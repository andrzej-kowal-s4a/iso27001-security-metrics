 
 #!/bin/bash
 
CURRENT_DIR=$(pwd)

echo "Current directory: $CURRENT_DIR"
 # Activate the virtual environment
 source $CURRENT_DIR/venv/bin/activate 
 # Run the script
 python $CURRENT_DIR/weekly_runner.py

 