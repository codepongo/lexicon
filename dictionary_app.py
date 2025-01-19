import sys
import os
import json
import pandas as pd
import requests
import gradio as gr

server_port = 8001

password = 'passworD000' if 'PASSWORD' not in os.environ else os.environ['PASSWORD'] 


if len(sys.argv) > 1:
    try:
        server_port = int(sys.argv[1])
    except ValueError as e:
        pass

sys.path.append(os.path.join(os.path.realpath('.'), 'deps'))

# Function to fetch the meaning of a word
def fetch_meaning(word):
    session = requests.Session()
    initial_url = 'https://www.bing.com/dict'
    session.get(initial_url)
    url = f"https://www.bing.com/dict/search?q={word}"
    response = session.get(url)

    if response.status_code != 200:
       return None  # Return None if unable to fetch the meaning

    page_content = response.text
    start_tag = '<meta name="description" content="'
    end_tag = '" />'

    start_index = page_content.find(start_tag)
    if start_index == -1:
        return None

    start_index += len(start_tag)
    end_index = page_content.find(end_tag, start_index)

    if end_index == -1:
        return None

    meaning = page_content[start_index:end_index]
    meaning = meaning.replace(f'必应词典为您提供{word}的释义，', '')
    return meaning

# Initialize the word list
word_list = {}

# Load previously saved data
def load_previous_data(filename='dictionary.json'):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
           json.dump({}, f)  # Create an empty JSON object
    else:
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                if content:  # Only load if content is non-empty
                    word_list.update(json.loads(content))  # Safely load JSON
            except json.JSONDecodeError:
                print("Failed to decode JSON; starting with an empty dictionary.")
                word_list.clear()  # Clear the dictionary to ensure it's empty

# Save the word list to a JSON file
def save():
    # Save the updated dictionary to a JSON file
    with open("dictionary.json", "w", encoding='utf-8') as f:
        json.dump(word_list, f, ensure_ascii=False, indent=4)  # Save the dictionary in JSON format

# Query the meaning of a word
def query_meaning(word):
    meaning = fetch_meaning(word)
    if meaning:
        word_list[word] = meaning
        return meaning
    else:
        return f"Meaning not found for '{word}'."

# Get the complete DataFrame
def get_dataframe():
    df = pd.DataFrame(list(word_list.items()), columns=["Word", "Meaning"])
    return df  # Return the complete DataFrame, including Word and Meaning columns

load_previous_data()

# Create Gradio interface
with gr.Blocks(title='Recite', css="""
table {
    border-radius: 3px; /* Set border radius */
}
table th, table td {
    border: 1px solid #ddd; /* Set border style */
    padding: 8px; /* Set cell padding */
    text-align: left; /* Align text to the left */
}
table th {
    background-color: #f2f2f2; /* Header background color */
}
""") as demo:
    gr.HTML('''
    <link rel="icon" type="image/png" href="favicon.ico" />
    ''')
    word_input = gr.Textbox(label="Enter a word")
    word_output = gr.Textbox(show_label=False, interactive=False)
    query_button = gr.Button("Query")
    clear_button = gr.Button('Clear')
    save_button = gr.Button("Save")
    refresh_checkbox = gr.Checkbox(label="Show All", container=False)
    output_display = gr.HTML(padding=False)

    def on_save(word):
        save()

    def on_query(word):
        if word:
            return query_meaning(word)

    def on_clear(word):
        if word:
            del word_list[word]
            return True, "", "", get_dataframe().to_html(escape=False, index=False)  # Return the complete DataFrame in HTML format

    def on_refresh(should_refresh):
        if should_refresh:  # If the checkbox is selected
            load_previous_data()  # Reload the data
            return get_dataframe().to_html(escape=False, index=False)  # Return the updated DataFrame in HTML format
        return output_display.value  # If the checkbox is not selected, keep the current value

    # Bind button events
    query_button.click(on_query, inputs=word_input, outputs=word_output)
    save_button.click(on_save, inputs=word_input)
    clear_button.click(on_clear, inputs=word_input, outputs=(refresh_checkbox, word_input, word_output, output_display))
    refresh_checkbox.change(on_refresh, inputs=refresh_checkbox, outputs=output_display)

# Launch Gradio interface
if __name__ == "__main__":
    demo.launch(server_name = '0.0.0.0',
                server_port = server_port,
                auth = ('zuohaitao', password),
                favicon_path = 'favicon.ico'
                )
