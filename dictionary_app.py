import sys  
import os  
import json  
import pandas as pd  
import requests  
import gradio as gr  

sys.path.append(os.path.join(os.path.realpath('.'), 'deps'))  

# Function to fetch the meaning of a word  
def fetch_meaning(word):  
    url = f"https://www.bing.com/dict/search?q={word}"  
    response = requests.get(url)  

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
    return meaning  

# Initialize the word list  
word_list = {}  

# Load previously saved data  
def load_previous_data(filename='dictionary.json'):  
    print('load_previous_data')  
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

# Query the meaning  
def query_meaning(word):  
    meaning = fetch_meaning(word)  
    if meaning:  
        word_list[word] = meaning  
        # Save the updated dictionary to a JSON file  
        with open("dictionary.json", "w", encoding='utf-8') as f:  
            json.dump(word_list, f, ensure_ascii=False, indent=4)  # Save the dictionary in JSON format  
        return get_dataframe()  
    else:  
        return f"Meaning not found for '{word}'."  

# Function to get the complete DataFrame  
def get_dataframe():  
    print(word_list)  
    df = pd.DataFrame(list(word_list.items()), columns=["Word", "Meaning"])  
    return df  # Return the complete DataFrame, including Word and Meaning columns  

load_previous_data()   

# Create Gradio interface  
with gr.Blocks() as interface:  
    word_input = gr.Textbox(label="Enter a word")  
    submit_button = gr.Button("Query")  
    refresh_checkbox = gr.Checkbox(label="Show All")  
    output_display = gr.HTML()  # Output box for displaying the DataFrame    

    def on_submit(word):  
        if word:  
            return query_meaning(word).to_html(escape=False, index=False)  # Return the complete DataFrame in HTML format  

    def on_refresh(should_refresh):  
        if should_refresh:  # If the checkbox is selected  
            load_previous_data()  # Reload the data  
            return get_dataframe().to_html(escape=False, index=False)  # Return the updated DataFrame in HTML format  
        return output_display.value  # If the checkbox is not selected, keep the current value   

    # Bind button events  
    submit_button.click(on_submit, inputs=word_input, outputs=output_display)  
    refresh_checkbox.change(on_refresh, inputs=refresh_checkbox, outputs=output_display)  

# Launch Gradio interface  
if __name__ == "__main__":  
    interface.launch()