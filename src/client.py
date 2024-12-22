import os  # To handle file paths and directories
import sys  # To modify the Python system path for importing modules
import socket  # For creating and managing TCP/IP socket communication
import json  # For serializing and deserializing data to/from JSON format
import argparse  # For handling command-line arguments
import logging  # For logging events during client execution
import time  # To add delays (intervals) between steps

from enum import Enum  # To define enumeration for error codes

# Add paths to sys.path for module imports
current_path = os.path.dirname(os.path.realpath(__file__))  # Current script directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Parent directory of the project
sys.path.extend([current_path, parent_dir])  # Extend sys.path to include these directories for module imports

# Configure logging settings
logging.basicConfig(level=logging.INFO)  # Set log level to INFO for relevant output

# Define error codes using Enum
class ErrorCode(Enum):
    OK = 0  # Success
    TIMEOUT = 1  # Timeout occurred
    OUT_OF_ORDER = 2  # Non-sequential step_id
    UNEXPECTED_ERROR = 3  # Any unexpected error

# Mapping error codes to user-friendly messages
ERROR_MESSAGES = {
    ErrorCode.OK: "성공",
    ErrorCode.TIMEOUT: "클라이언트 타임아웃 초과",
    ErrorCode.OUT_OF_ORDER: "순차적이지 않은 step_id",
    ErrorCode.UNEXPECTED_ERROR: "예기치 못한 서버 오류",
}

# TCPClient class for managing client functionality
class TCPClient:
    def __init__(self, host='localhost', port=8080, json_file='test.json'):
        """
        Initializes the TCPClient with server details and test data.
        - host: Server IP address to connect to
        - port: Server port to connect to
        - json_file: Path to the JSON file containing test data
        """
        self.host = host  # Server host address
        self.port = port  # Server port
        self.steps = self.load_steps(json_file)  # Load test steps from the JSON file
        self.client_socket = None  # Placeholder for the client socket

    def load_steps(self, json_file):
        """
        Loads test steps from a JSON file.
        - json_file: Path to the JSON file
        Returns:
        - List of steps to execute
        """
        with open(json_file, 'r') as file:
            data = json.load(file)  # Load JSON data from the file
        return data.get("test_services", [])  # Extract the "test_services" list or return an empty list

    def log_error(self, step_id, error_code):
        """
        Logs errors based on the error code and step_id.
        - step_id: ID of the step that caused the error
        - error_code: Error code returned by the server
        """
        message = ERROR_MESSAGES.get(ErrorCode(error_code), f"알 수 없는 오류 코드 {error_code}")  # Map error code to message
        logging.error(f"Step {step_id} - {message}")  # Log the error message

    def send_step(self, step):
        """
        Sends a single step to the server and handles the server's response.
        - step: Dictionary containing step details (step_id, timeout, interval)
        """
        try:
            # Create a new socket for each step
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))  # Connect to the server

                # Send step_id and timeout as JSON data
                client_socket.sendall(json.dumps({"step_id": step["step_id"], "timeout": step["timeout"]}).encode())
                
                # Receive the server's response
                response = client_socket.recv(1024)  # Receive up to 1024 bytes
                if response == b"END":  # If server sends "END", terminate the loop
                    return
                response_data = json.loads(response.decode())  # Decode the JSON response
                error_code = response_data.get("error_code", ErrorCode.UNEXPECTED_ERROR.value)  # Extract error code
                
                # Log errors if the response contains an error code
                if error_code != ErrorCode.OK.value:
                    self.log_error(step["step_id"], error_code)
                else:
                    logging.info(f"{step['step_id']} 단계 성공")  # Log success message

                # Sleep for the interval before sending the next step
                time.sleep(step["interval"])

        except socket.timeout:
            # Handle client timeout (log it as INFO rather than ERROR)
            logging.info(f"Step {step['step_id']} 타임아웃 발생으로 종료 ")
        except Exception as e:
            # Log unexpected errors
            logging.error(f"Step {step['step_id']} failed - Reason: Unexpected error: {e}")
    
    def run(self):
        """
        Executes all the test steps sequentially.
        """
        for step in self.steps:  # Iterate through each test step
            logging.info(f"Sending step {step['step_id']} to server")  # Log the current step
            self.send_step(step)  # Send the current step to the server
            time.sleep(step["interval"])  # Wait for the interval before processing the next step

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="TCP Client for testing server communication.")  # Create argument parser
    parser.add_argument(
        "--data",
        choices=["success", "failure"],  # Allow only "success" or "failure" as valid options
        default="success",  # Default to "success_data.json"
        help="Choose the test data file: 'success' for success_data.json, 'failure' for failure_data.json"
    )
    parser.add_argument("--host", default="localhost", help="Specify the server host. Default is 'localhost'.")  # Host option
    parser.add_argument("--port", type=int, default=8080, help="Specify the server port. Default is 8080.")  # Port option
    args = parser.parse_args()  # Parse command-line arguments

    # Determine the JSON file based on the chosen data type (success or failure)
    json_file = os.path.join(parent_dir, "test_data", f"{args.data}_data.json")
    
    # Initialize and run the TCP client
    client = TCPClient(host=args.host, port=args.port, json_file=json_file)
    client.run()  # Start the client execution
