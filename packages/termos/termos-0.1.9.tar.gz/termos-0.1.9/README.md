## Update README.md

Add information about the logout command to your `README.md`:

```markdown
## Usage

Run a task:
```bash
termos run --task "Your task description here"
```

Logout:
```bash
termos logout
```

On first use of `termos run`, you will be prompted to enter your username and password. The authentication token will be stored for future use. Use `termos logout` to remove stored credentials.
```

## 5. Testing the Logout Functionality

To test the logout functionality:

1. Ensure you're logged in by running a task:
   ```
   termos run --task "Test task"
   ```

2. Now, run the logout command:
   ```
   termos logout
   ```

3. You should see a message confirming that you've been logged out.

4. Try running another task. You should be prompted to log in again.

## 6. Error Handling

Consider adding error handling to the logout function. For example:

```python
import os
from pathlib import Path

TOKEN_FILE = Path.home() / '.termos_token'

def logout():
    try:
        if TOKEN_FILE.exists():
            os.remove(TOKEN_FILE)
            print("Logged out successfully. Tokens removed.")
        else:
            print("No active session found.")
    except Exception as e:
        print(f"An error occurred during logout: {e}")
```

This will catch any unexpected errors that might occur during the logout process and inform the user.