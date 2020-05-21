## Algorithm tests

These tests do not need exareme+docker to run. They use an algorithm runner, 
written in python, which simulates the exareme environment. 

#### Run tests
First we need to install the project's requirements.
There are two options:
1. Make virtual environment with python2.7 and install 
    requirements listed in Exareme-Docker/src/mip-algorithms/tests/tests_requirements.txt.
2. Or install the same requirements globally.

To make a virtual environment do the following
- Go to repository root
    ```bash
    cd exareme
    ```
- Install virtualenv
    ```bash
    pip install virtualenv
    ```  
- Create virtualenv using python 2.7
    ```bash
    virtualenv -p $(which python2.7) venv
    ```
- Activate virtualenv
    ```bash
    source venv/bin/activate
    ```
- Install requirements
    ```bash
    pip install -r Exareme-Docker/src/mip-algorithms/tests/tests_requirements.txt
    ```
- Add environment variable for testing
    ```bash
    export ENVIRONMENT_TYPE=TEST
    ```

Now we are ready to run the tests
```bash
cd Exareme-Docker/src/mip-algorithms/tests/algorithm_tests/
python -B -m pytest
```

To exit virtualenv
```bash
deactivate
```