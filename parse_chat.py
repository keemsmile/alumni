from chat_parser import ChatParser
import sys

# Set console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Read chat file
try:
    with open('_chat.txt', 'r', encoding='utf-8') as f:
        chat_text = f.read()
except UnicodeDecodeError:
    # Try with a different encoding if UTF-8 fails
    with open('_chat.txt', 'r', encoding='latin1') as f:
        chat_text = f.read()

# Save first few lines to a file
with open('chat_preview.txt', 'w', encoding='utf-8') as f:
    f.write("\nFirst few lines of chat_text:\n")
    f.write("\n".join(chat_text.split('\n')[:5]))

# Parse
parser = ChatParser()
df = parser.parse_chat(chat_text)

# Save debug info to a file
with open('debug_info.txt', 'w', encoding='utf-8') as f:
    f.write("\nDataFrame Info:\n")
    f.write(f"Columns: {df.columns.tolist()}\n")
    f.write("\nFirst few rows:\n")
    f.write(df.head().to_string())
    f.write(f"\nShape: {df.shape}\n")

# Save results
df.to_csv('parsed_chat.csv', index=False, encoding='utf-8')

# Save statistics to a file
with open('user_statistics.txt', 'w', encoding='utf-8') as f:
    f.write("\nUser Statistics:\n")
    f.write(str(parser.get_user_statistics(df)))
