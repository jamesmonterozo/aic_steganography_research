# steg_message

## Table of contents
* [Motivation](#motivation)
* [Setup](#setup)
* [Test](#test)
* [Usage](#usage)
* [Note](#note)

## Motivation
The aim for this is to explore ways of hiding string messages inside of images and later decoding the message hidden in the string.

## Setup
Ensure that you have Python 3. Unstall the pillow library using `pip` and clone the repository locally:
```
pip install pillow
git clone https://github.com/jamesmonterozo/aic_steganography_research/
cd aic_steganography_research/steg_message
```

## Test
To ensure that the program works, conduct a test run of the decoding and encoding commands.

For encoding, run the following command and it should output a file named `hidden_arete.png` in the `out` folder.
```
python steg.py encode in/arete.jpg in/message.txt out/hidden_arete.png
```

For decoding, run the following command and it should output a file named `decoded_arete.txt` in the `out` folder.
```
python steg.py decode out/hidden_arete.png +754700668796 out/decoded_arete.txt
```

## Usage
### Encoding
Add the image file and the message text files in the `in` folder. The message text file should contain the cipher on the first line and the message in the succeeding lines like the example below:
```
+1234567890
Lorem Ipsum Dolor Est
Lorem Ipsum
...
```
The cipher should follow the format: `[+/-][number movement]`. Examples: +345, -2993821, +1, -201. Then, run the steg.py file with the following commandline arguments format:
```
python steg.py encode in/[image-filename] in/[message-filename] out/[output-filename]
```
The output image should appear in the `out` folder.

### Decoding
Add the image file to decode in the `in` folder. Then, run the steg.py file with the following commandline arguments format:
```
python steg.py decode in/[input-filename] [cipher] out/[output-filename]
```
The output text file with the decoded message should appear in the `out` folder and the commandline should also display the message.
