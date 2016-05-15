echo "Test with offset 1"
python3 encode.py -in plain_text.txt -out encrypt_caesar_1.txt -type 1 -offset 1
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_caesar_1.txt -out test.out -type 1 

echo "Test with offset 2"
python3 encode.py -in plain_text.txt -out encrypt_caesar_2.txt -type 1 -offset 2
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_caesar_2.txt -out test.out -type 1 

echo "Test with offset 15"
python3 encode.py -in plain_text.txt -out encrypt_caesar_15.txt -type 1 -offset 15
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_caesar_15.txt -out test.out -type 1 

echo "Test with offset 25"
python3 encode.py -in plain_text.txt -out encrypt_caesar_25.txt -type 1 -offset 25
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_caesar_25.txt -out test.out -type 1 

echo "Test with offset 100"
python3 encode.py -in plain_text.txt -out encrypt_caesar_100.txt -type 1 -offset 100
python3 brute_force_crack.py -dic dictionary.txt -t 4 -in encrypt_caesar_100.txt -out test.out -type 1 
