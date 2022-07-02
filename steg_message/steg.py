from PIL import Image
import numpy
import sys

# ===== ===== GENERAL HELPER METHODS ===== =====
def binary_to_ascii (binary):
    """
    Converts binary values to ascii values
    """
    if(type(binary) is list):
       return [int(x, 2) for x in binary]
    else:
        return int(binary, 2)

def ascii_to_binary(ascii):
    """
    Converts ascii values to binary values
    """
    if(type(ascii) is list):
       return [f'{x:08b}' for x in ascii]
    else:
        return f'{ascii:08b}'

def char_to_ascii(char):
    """
    Converts characters to ascii values
    """
    if(type(char) is list):
       return [ord(x) for x in char]
    else:
        return ord(char)

def ascii_to_char(ascii):
    """
    Converts ascii characters to characters
    """
    if(type(ascii) is list):
       return [chr(x) for x in ascii]
    else:
        return chr(ascii)

def load_image (path):
    """
    This opens the image and converts it such that the pixels
    are to be read as RGB values.
    """
    return Image.open(path)

# ===== ===== ENCODING METHODS ===== =====
def check_message_size (im, message, cipher):
    """
    This checks if the image can fit the message to be encoded.
    8-bits are required to encode one character, 
    so one character needs 8 R, G or B values to be encoded properly.

    Buffers at the start and end are also needed. Each consist of 8-bits.
    """
    area = im.size[0] * im.size[1]
    return area >= (len(message) + 8 * 2 + len(cipher) * 8)

def encrypt(message, cipher):
    """
    Encrypt Message into binary values
    """
    ascii_message = char_to_ascii(message) # Convert to ascii values
    
    # === GET INITIAL DIRECTION OF CIPHER ===
    forward = (cipher[0] == '+')
    cipher = [int(x) for x in cipher[1:]] # Convert remaining cipher to integers

    i = 0 # indexes the cipher
    for j in range(len(ascii_message)):
        # OBTAIN THE MOVEMENT AND DIRECTION OF MOVEMENT TO BE APPLIED
        movement = cipher[i]
        if not(forward):
            movement *= -1

        ascii_message[j] += movement # Moves the ascii

        # ENSURE THE ASCII VALUE IS WITHIN ASCII RANGE (0 - 127)
        if ascii_message[j] > 127:
            ascii_message[j] = ascii_message[j] - 128
        elif ascii_message[j] < 0:
            ascii_message[j] = 128 - abs(ascii_message[j])
        
        # PREPARE FOR THE NEXT ITTERATION
        if i == len(cipher) - 1:
            i = 0 # reset if we reach the end of the cipher
            forward = not(forward) # reverse direction
        else:
            i += 1 # go to next digit in cipher
    
    # === CONVERT ASCII VALUES TO BINARY FOR EMBEDDING INTO IMAGE ===
    return ascii_to_binary(ascii_message)

def save_image (im, binary, out_path):
    """
    Saves to image by obtaining a list of tuples.
    """
    # === OBTAIN THE PIXEL VALUES AS A LIST OF TUPLES ===
    pixels = list(im.getdata()) 
    
    i = 0
    x = 0
    for b in binary:
        # OBTAIN AND EDIT COLOR VALUE
        cur_value = list(ascii_to_binary(pixels[x][i])) # Obtain binary value of current color value as a list
        cur_value[-1] = b # Replace the Least bit
        cur_value = "".join(cur_value) # Convert list into string
        cur_value = binary_to_ascii(cur_value) # Convert string binary to ascii

        # RETURN EDITTED ASCII VALUE TO TUPLE AND PIXEL LIST
        temp = list(pixels[x]) # Get RGB Values
        temp[i] = cur_value # Edit color value accordingly
        pixels[x] = tuple(temp) # Edit pixel value to max RGB value

        # PREPARE FOR NEXT ITERATION
        if i < 2:
            i += 1 # Move to the next Color value
        else:
            i = 0 # Reset to first color value
            x += 1 # Go to next pixel
    
    # === SAVE EDITTED PIXEL VALUES INTO AN IMAGE ===
    im.putdata(pixels)
    im.save(out_path, mode="png")

def encode(in_path, out_path, message, cipher):
    """
    This encodes the message into the image file.
    """
    # === OPEN AND CHECK THE IMAGE FILE ===
    im = load_image(in_path)
    if not(check_message_size(im, message, cipher)):
        print("Error: image is not large enough")
        return None
    
    to_encode = encrypt(list(message), list(cipher)) # Encrypt message

    # === BUILD BINARY VALUES WITH DELIMITERS ===
    delimiter = ['11111111'] # Delimeter to signify start and end
    to_encode = delimiter + to_encode + delimiter

    # === ENCODE THE VALUES INTO THE IMAGE AND SAVE ===
    save_image(im, "".join(to_encode), out_path)

# ===== ===== DECODING METHODS ===== =====
def decrypt (binaries, delims, cipher):
    """
    This decrypts the binaries and returns the string message.
    """
    # === PROCESS THE CIPHER DIRECTION ===
    forward = (cipher[0] == "-") # Do the reverse direction
    cipher = [int(x) for x in cipher[1:]] # extract the rest of the cipher into integer values

    # === CONVERT THE BINARIES INTO TEXT ===
    i = 0
    message = ""    
    for binary in binaries[delims[0] + 1:delims[1]]:
        temp = binary_to_ascii(binary) # Convert Binary to ASCII values

        # PERFORM THE MOVEMENT TO OBTAIN ORIGINAL ASCII VALUES
        movement = cipher[i]
        if not(forward): movement *= -1
        temp = temp + movement

        # MAKE SURE ASCII VALUE IS WITHIN ASCII RANGE (0 - 127)  
        if temp > 127:
            temp = temp - 128
        elif temp < 0:
            temp = 128 - abs(temp)
        
        # CONVERT ASCII TO CHARACTER AND APPEND TO MESSAGE STRING
        temp = ascii_to_char(temp)        
        message += temp

        # PREPARE FOR NEXT ITERATION
        if i < len(cipher) - 1: 
            i += 1 # Loop through cipher
        else: 
            i = 0 # Reset cipher upon reaching the end
            forward = not(forward) # flip the direction
    
    # === RETURN THE MESSAGE ===
    return message

def decode(in_path, out_path, cipher):
    """
    This decodes the image file and outputs a text file containing the message.
    """

    # === LOADING IMAGE AND PIXEL VALUES ===
    im = load_image(in_path) # Load the image
    
    pixels = list(im.getdata()) # Get a list of tuples representing RGB values of the image
    pixels = [y for x in pixels for y in x] # Flattens the list such that all values are in one list with no nested tuples
    
    # === EXTRACTING BINARY VALUES FROM LEAST BITS === 
    binaries = []
    curBin = ""
    delims = []
    for i in range(len(pixels)):
        temp = pixels[i] # takes the color value
        
        curBin += ascii_to_binary(temp)[-1] # appends the least bit to the current 8-bit being constructed
        if len(curBin) == 8: # if we complete all 8 bits
            binaries.append(curBin) # add to the list
            if curBin == "11111111": # if we find a delimiter
                delims.append(len(binaries) - 1) # Add the location to the list
                if len(delims) == 2: break # end loop if the 2nd delimiter is found
            curBin = "" # reset the current bin
    
    # === PROCESS THE BINARIES EXTRACTED ===
    if len(delims) == 2: # If 2 delimeters were found
        message = decrypt(binaries, delims, cipher) # decrypt the binaries

        # Output the decoded message
        print("Decoded Message:\n" + message)
        with open(out_path, "w") as f:
            f.write(message)
    else:
        print("No Message Found") # No deilimiters were found

if __name__ == "__main__":
    """
    ==COMMANDLINE ARGUMENT SYSTEM==
    python steg.py encode [image-directory] [message-text-file] [output-directory] 
    python steg.py decode [input-directory] [cipher] [output-directory]

    For message text file, add cipher to first line and remaining lines will be the message.

    ==FORMAT OF CIPHER==
    [+/-][number movement]
    Ex: +345, -2993821, +1, -201
    
    ==CIPHER PROCESS==
    The cipher will go through each digit one by one and it'll move it forward(+) or backward(-)
    depending on the sign indicated. After all digits are exhausted, it will return to the
    first digit. Then, it will reverse the direction. It goes with the process until the 
    entire message is encrypted.

    Ex: Say we have a cipher of +345 and the ascii values {122, 100, 50, 60, 49, 20, 10, 20}
    this will be the transformation:
    {   
        122 + 3, 100 + 4, 50 + 5, 
        60 - 3, 49 - 4, 20 - 5, 
        10 + 3, 20 + 4
    }
    The end result is: {127, 104, 55, 57, 45, 15, 13, 24}

    === FOR TESTING ===
    Encode: python steg.py encode in/arete.jpg in/message.txt out/hidden_arete.png
    Decode: python steg.py decode out/hidden_arete.png +754700668796 out/decoded_arete.txt
    """
    try:
        operation = str(sys.argv[1]).upper()
        in_path = sys.argv[2]

        if operation == "ENCODE":
            message_path = sys.argv[3]
            try:
                out_path = sys.argv[4]
            except:
                out_path = "out.png" # Default output image file
            
            # Extracts the cipher from the first line
            # and the message from succeeding lines
            with open(message_path, 'r') as file:
                cipher = file.readline().rstrip()
                message = file.read()
            
            encode(in_path, out_path, message, cipher)
        elif operation == "DECODE":
            cipher = sys.argv[3]
            try:
                out_path = sys.argv[4]
            except:
                out_path = "decoded.txt" # Default output text file
            decode(in_path, out_path, cipher)
        else:
            raise IndexError # Raise an error if decode/encode isn't indicated
    except (IndexError):
        print("Follow the commandline format:")
        print("python steg.py encode [image-directory] [message-file] [output-directory]")
        print("python steg.py decode [input-directory] [cipher] [output-directory] ")





"""
def save_image(im, binary):
    
    Saves to image by editting through pixel access
    
    pixels = im.load()
    width, height = im.size
    
    i = 0
    x = 0
    y = 0
    for b in binary:
        cur_value = list(ascii_to_binary(pixels[x,y][i]))
        cur_value[-1] = b
        cur_value = "".join(cur_value)
        cur_value = binary_to_ascii(cur_value)
        temp = list(pixels[x,y])
        temp[i] = cur_value
        pixels[x,y] = tuple(temp)

        if i < 2:
            i += 1
        else:
            i = 0
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
    
    print(list(im.getdata())[:5])
    im.save("output.png")

"""