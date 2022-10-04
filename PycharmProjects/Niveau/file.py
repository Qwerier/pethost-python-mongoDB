
def count_words(filename):
    try:
        with open(filename) as file_object:
            contents = file_object.read()
    except FileNotFoundError:
        message = "Sorry, the file "+filename+" doesn't exist"
        print(message)
    else:
        words = contents.split()
        sum = 0
        for string in words:
            sum +=len(string)

        num_words = len(words)
        print("The file "+filename+" has about "+str(num_words)+" words and circa "\
        +str(sum)+" characters")

filename = "devangari.txt"
count_words(filename)

