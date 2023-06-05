#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>

using namespace std;

string byteToBinary(string text) // turn ascii bytes into binary for internal representation
{
    string result = "";
    map<char, string> asciiBinaryMap{ { '0', "0000" }, { '1', "0001" },
                                      { '2', "0010" }, { '3', "0011" },
                                      { '4', "0100" }, { '5', "0101" },
                                      { '6', "0110" }, { '7', "0111" },
                                      { '8', "1000" }, { '9', "1001" },
                                      { 'A', "1010" }, { 'B', "1011" },
                                      { 'C', "1100" }, { 'D', "1101" },
                                      { 'E', "1110" }, { 'F', "1111" } };

    for (long long i=0; i<text.size(); i++)
    {
        result += asciiBinaryMap[text[i]];
    }
    
    return result;
}

void outputModified(string text, vector<int> endlines) // print the modified text and its binary
{
    int endlineIndex = 0; // where is the string ends to put an endline
    for (long long i=0; i<text.size(); i++)
    {
        cout << text[i];
        if (i == endlines[endlineIndex] - 1)
        {
            cout << '\n';
            endlineIndex++;
        }
    }

    string temp = "";
    endlineIndex = 0;
    cout << "binary form: ";
    for (long long i=0; i<text.size(); i++)
    {
        temp += text[i]; // transform each text into binary seperately
        if (i == endlines[endlineIndex] - 1)
        {
            cout << byteToBinary(temp);
            cout << '\n' << '\n';
            temp = "";
            endlineIndex++;
        }
    }
}

void modification(string& text, unsigned long long modificationPos, string address)
{
    stringstream ss;
    
    unsigned long long pos, startingAddress;
    string modificationResult;
    cout << "here's the original text: " << text << '\n';
    cout << "here's the address(hex): " << address << '\n';

    ss.clear();
    ss.str("");

    cout << "where to modify in text: " << text.substr(modificationPos * 2 + 1, 5) << '\n';
    ss << hex << text.substr(modificationPos * 2 + 1, 5); // *2 because two digits in text
                                                          // is one byte. +1 because the format
                                                          // 4 flag doesn't need modification
    ss >> pos;
    cout << "where to modify in text(dec): " << pos << '\n';

    ss.clear();
    ss.str("");

    ss << hex << address;
    ss >> startingAddress;
    cout << "starting address: " << startingAddress << '\n';
    pos += startingAddress; // add the pos with starting address

    ss.clear();
    ss.str("");
    ss << hex << pos;
    ss >> modificationResult; // turn the result back into string, for later replacement
    for (int j=0; j<modificationResult.size(); j++)
        modificationResult[j] = toupper(modificationResult[j]);
    cout << "result: " << modificationResult << '\n';
    for (int j=0; j<5; j++)
    {
        text[(modificationPos * 2 + 1) + j] = modificationResult[j];
    }
}

int main(int argc, char *argv[])
{
    stringstream ss;
    unsigned long long len;
    string str, startingAddress;
    string text = "";
    char startingAddressArr[20];
    ifstream file(argv[1]);
    vector<unsigned long long>textStartingAddress, modificationPos;
    vector<int>endlines;
    vector<string> texts;
    int endlinePlace, previousEndline = -1;
    
    sprintf(startingAddressArr,"%p", &text); // get starting address of the string that contains
                                             // the whole text section
    startingAddress = startingAddressArr; // convert the c type char array to string object
    int startingAddressLen = startingAddress.size();
    startingAddressLen -= 5; // to get the final five digits of the starting address to be added with 

    if (file)
    {
        while(getline(file, str))
        {
            ss.clear();
            ss.str("");

            if (str[0] == 'T') // text section of the program
            {
                ss << hex << str.substr(1, 6);
                ss >> len;
                textStartingAddress.push_back(len);
                
                ss.clear();
                ss.str("");

                text = str.substr(9);
                texts.push_back(text);

                ss << hex << str.substr(7, 2);
                ss >> endlinePlace;

                if (previousEndline == -1) // to get each texts' endline position
                    endlines.push_back(endlinePlace * 2);
                else
                    endlines.push_back(endlinePlace * 2 + endlines[previousEndline]);
                previousEndline++;
            }
            else if (str[0] == 'M') // modification section of the program
            {
                ss << hex << str.substr(1, 6);
                ss >> len;

                modificationPos.push_back(len); // this records where to be modified,
                                                // bytes on object program, so times two
                                                // to get the exact length of the string
                                                // add 1 because there's no external
                                                // reference in our project, so all 
                                                // length will be 05
            }
        }

        int index = -1; // getting the offset of each modification record based on the text string
                        // that needs to be modified
        for (unsigned int i=0; i<modificationPos.size(); i++)
        {
            for (unsigned int j=0; j<textStartingAddress.size(); j++)
            {
                index = -1;
                if (modificationPos[i] < textStartingAddress[j]) // find the text string that
                                                                 // modification belongs to
                {
                    if (j != 0)
                        index = j - 1;
                    else 
                        index = 0;
                    break;
                }                
            }
            if (index == -1)
                index = textStartingAddress.size()-1; // belongs to the last text string
            
            modificationPos[i] -= textStartingAddress[index];
            modification(texts[index], modificationPos[i], startingAddress.substr(startingAddressLen));
        }

        text = "";  // turn the modified text into a string for gdb representations
        for (int i=0; i<texts.size(); i++)
            text += texts[i]; 
        outputModified(text, endlines);
    }
    else
    {
        cout << "File " << argv[1] << " does not exists!\n";
    }

    file.close();
    return 0;
}
