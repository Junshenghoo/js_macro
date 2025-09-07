import json

def convert_txt_to_json(txt_file, json_file):
    bitmap_data = []
    
    # Read the text file line by line
    with open(txt_file, "r") as f:
        for line in f:
            row = [int(char) for char in line.strip()]
            bitmap_data.append(row)
    
    # Wrap into dict
    data = {"bitmap_data": bitmap_data}
    
    # Dump JSON with compact row formatting
    with open(json_file, "w") as f:
        json.dump(data, f, separators=(",", ": "))
    
    print(f"Converted {txt_file} → {json_file}")

if __name__ == "__main__":
    convert_txt_to_json("test.txt", "display.json")