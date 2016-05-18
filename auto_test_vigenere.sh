echo "Test with key abcd"
python3 encode.py -in plain_text.txt -out encrypt_vigenere_abcd.txt -type 2 -key abcd
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_vigenere_abcd.txt -out test.out -type 2  
sleep 3

echo "Test with key fuck"
python3 encode.py -in plain_text.txt -out encrypt_vigenere_fuck.txt -type 2 -key fuck
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_vigenere_fuck.txt -out test.out -type 2  
sleep 3

echo "Test with key alphabet"
python3 encode.py -in plain_text.txt -out encrypt_vigenere_alphabet.txt -type 2 -key alphabet
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_vigenere_alphabet.txt -out test.out -type 2  
sleep 3

echo "Test with key lovepython"
python3 encode.py -in plain_text.txt -out encrypt_vigenere_ilovepython.txt -type 2 -key lovepython
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_vigenere_ilovepython.txt -out test.out -type 2 
