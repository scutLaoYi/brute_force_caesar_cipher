echo "Test with key abcd"
python3 encode.py -in plain_text.txt -out encrypt_vigenere_abcd.txt -type 2 -key abcd
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_vigenere_abcd.txt -out test.out -type 2 -l 4 

echo "Test with key python"
python3 encode.py -in plain_text.txt -out encrypt_vigenere_python.txt -type 2 -key python
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_vigenere_python.txt -out test.out -type 2 -l 6 
