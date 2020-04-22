Run the following commands at the UNIX terminal to setup Python3.6.7 
(if not already set up)
----------------------------------------------------------------

Step 1:
$ wget https://www.python.org/ftp/python/3.6.7/Python-3.6.7.tgz

Step 2:
$ tar xvzf Python-3.6.7.tgz

Step 3:
$ cd Python-3.6.7

Step 4:
$ ./configure --prefix=$HOME/.local

Step 5:
$ make

Step 6:
$ make install

Step 7:
$ cd $home
$ vi .bash_profile

Step 8:
With an editor, add the following lines, then save the file:

# Python 3 
export PATH="$HOME/.local/bin:$PATH"

Step 9:
$ source ~/.bash_profile
------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------
Run the following commands to run the program:
----------------------------------------------

Step 1) Run the following command to run the file

$ python3 -m pip install --upgrade pip
$ pip3 install numpy
$ pip3 install pandas
$ pip3 install nltk
$ pip3 install wordnet


Navigate to the directory where you have unizipped the files
$ cd HA3_jxv160930
$ python3 statistical_model.py /people/cs/s/sanda/cs6322/Cranfield/ /people/cs/s/sanda/cs6322/resourcesIR/stopwords /people/cs/s/sanda/cs6322/hw3.queries

  python3 <filename> <filepath to Cranfield documents folder> <filepath to stopwords file> <filepath to hw3.queries>

------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------
To view the Program description - 

$ cat program_description.txt