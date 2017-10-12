Nappy Units Tests directory
===========================

Need unit tests as follows:


1. Read tests for all FFIs

2. Read and write and diff tests for all FFIs

3. Write only tests for all FFIs

4. Convert NC to NA tests

5. Convert NA to NC tests

6. Write tests for CSV format

7. Convert NC to CSV format tests

8. Testing of individual utility modules

9. Error stack needed


Running tests
=============

nose is handy utility. It allows you to run:

$ nosetests __init__.py 

and it runs all tests that match "test_*.py"
