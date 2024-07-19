
## SEEQC Client User Guide

The SEEQC Client is a library for interfacing with SEEQC's quantum devices via the cloud.
It allows access to an emulator as well.

### Prerequisite
SEEQC CLI requires an installation of Python>=3.8 along with Pip. We suggest installing SEEQC CLI into a new virtual environment.
Using SEEQC CLI will require a username and password which can be obtained by request.

### Installation
The library should be installed from PyPi using Pip as:
````
 pip install seeqc-client
 ````
This will install SEEQC CLI into your active Python environment along with its dependencies.


### Getting Started
Instantiate the client as:

````
from seeqc_client import Client
client = Client()
````

#### Password creation and resetting
If you have not yet created a password or need to reset an existing one, trigger a password reset email as:

```` 
client.auth.send_password_reset_email(<email>)
````

#### Initialisation
The client must then be initialised in order to authenticate with the server.
The basic initialisation is performed as

````
client.initialise()
````
This will prompt username and password entry and upon success provide the client with the credentials required to access our systems.
The client will require re-instantiation once per day.

#### Programmatic access
To facilitate programmatic access the client may be initialised with a path to a *refresh token* file that contains an authentication token linked to an account:
````
client.initialise(<token path>)
````
The token may be generated using the following call that will require manually inputting credentials and will produce a refresh token for this account stored in a file:
````
client.gen_token(<target token path>)
````


### Running the emulator

The emulator accepts input files using instructions as part of a restrictive subset of QASM v2 as described in the next section. The result is returned in the same function call that made the request as a dictionary containing informations about the measurement outcomes, the qasm file being run and the emulator version.

#### Target systems

Circuits must be run on a specific target system.
The list of available target systems can be accessed with
````
client.get_emulator_target_systems()
````

#### Coupling

CZ gates can only be performed between qubits with couplers between them. A coupling map can be retrieved for a given target system of form: [[0,2], [1,2]], which would correspond to coupling between the 2nd qubit with the 0th and 1st qubits.

The coupling for a given backend can be retrieved as:

```
coupling = client.get_emulator_coupling(<target_backend>)
```

#### Submitting emulator jobs

Mandatory inputs to the emulator run API call are the qasm file and the system to target, whereas the number of shots is optional (not exceeding 10,000).
The result format is a dictionary with 3 keys:
- `"measurement_outcomes"`
- `"emulator_version"`
- `"qasm"`


Noise can be scaled using the noise percentage parameter where 100 is the default amount of noise and 0 corresponds to no noise. This must be an integer between 0 and 100, and will scale the noise parameters correspondingly. 

The emulator contains a wrapper for the qiskit transpiler. If the parameter allow_transpilation is True then this will be run and will transpile to the native gate set for the selected backend. The user should review the qasm that is returned with the response to see what exactly was run.
Transpilation is disabled by default.

````
results = client.run_emulator('./my_experiment.qasm', num_shots=1000, target_system='red', allow_transpilation=False, noise_percentage=100)
````




### Running Experiments
Experiments can be created using QASM format files with a subset of QASM commands being accepted:
   - `qreg q[<num_qubits>]`
   - `rx(pi/2)`
   - `rx(-pi/2)`
   - `ry(pi/2)`
   - `ry(-pi/2)`
   - `rx(<angle>)` where `<angle>` is a floating point number
   - `ry(<angle>)` where `<angle>` is a floating point number
   - `cz q[<qubit_a>] q[<qubit_b>]`
   - `reset q[<qubit_a>]`
   - `measure q[<qubit_a>] -> c[<creg_idx>]`

Note that the 2-qubit gates must be used on pairs of qubits that have the correct type of couplers between them.


````
exp = client.create_experiment('./my_experiment.qasm')
````
This will create a new experiment object associated with this QASM file that can be submitted to be run as:
````
exp.run()
````
This sends the QASM instructions to our platform and returns an experiment id which can be used to recover experiments from another session.
The status of the experiment can be checked as:
````
exp.get_status()
````
The status will iterate through pending, running and complete. Once the status is set to complete it will automatically retrieve the experiment results, which can then be viewed as:
````
exp.show_results()
````
Results here correspond to the population distributions. To return the full quantum register as a numpy array instead use
````
exp.get_register()
````
### Retrieving Experiments
Metadata on previous experiments can be accessed as:
````
client.get_experiments(start_index, end_index)
````
If no indices are provided the last 10 experiments you ran will be returned.
From the list of experiments you can retrieve the experiment id which can be used to reload a previous experiment as:
````
exp = client.get_experiment(experiment_id)
````
checking the status as shown above will recover the associated data providing the experiment has completed.

### Plotting
To produce a histogram of results distributions:
````
exp.plot()
````
