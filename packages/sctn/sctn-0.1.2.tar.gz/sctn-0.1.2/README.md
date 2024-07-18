![](res/logo.png)

--------------------------------------------------------------------------------

SCTN is a novel Spiking Neural Network (SNN) architecture designed to advance the field of neuromorphic computing. SCTN,
short for Spiking Continuous Time Neuron, leverages the dynamics of spiking neurons to process information in a manner
that closely mimics biological neural networks. This repository offers a comprehensive implementation of SCTN, providing
researchers and developers with tools to explore and utilize this cutting-edge SNN framework for various applications in
machine learning and artificial intelligence.

## Quickstart

```python
import numpy as np

from sctn.layers import SCTNLayer
from sctn.spiking_network import SpikingNetwork
from sctn.spiking_neuron import create_SCTN, BINARY

def new_neuron():
    neuron = create_SCTN()
    neuron.leakage_factor = 2
    neuron.leakage_period = 2
    neuron.log_out_spikes = True
    neuron.threshold_pulse = 50
    neuron.activation_function = BINARY
    neuron.log_membrane_potential = True
    # make different neurons using random weights
    neuron.synapses_weights = np.array(10 + (10 * np.random.random(1)))
    return neuron

network = SpikingNetwork()
network.add_layer(SCTNLayer([new_neuron() for i in range(5)]))
network.add_layer(SCTNLayer([new_neuron()]))

spikes_input = np.zeros(100)
spikes_input[np.random.choice(np.arange(len(spikes_input)), 45)] = 1
spikes_layer_1 = np.zeros((len(spikes_input), len(network.layers_neurons[0].neurons)))

for i, s in enumerate(spikes_input):
    # neuron may have several inputs from different source so the input should be wrapped in another array
    network.input(s)

fig, axs = plt.subplots(4, 1, figsize=(16, 9))

for i, neuron in enumerate(network.layers_neurons[0].neurons):
    spikes_layer_1[:, i] = neuron.out_spikes(is_timestamps=False, spikes_array_size=len(spikes_input))

output_neuron = network.neurons[-1]
membrane_potential = output_neuron.membrane_potential_graph()
spikes_output = output_neuron.out_spikes(is_timestamps=False, spikes_array_size=len(spikes_input))

axs[0].set_title('Input Spikes')
axs[0].stem(spikes_input)
axs[1].set_title('Layer 1 Spikes')
axs[1].set_ylabel('Layer 1 neurons')
axs[1].scatter(*np.where(spikes_layer_1 == 1))
axs[2].set_title('Membrane Potential')
axs[2].plot(membrane_potential)
axs[2].axhline(output_neuron.threshold_pulse, xmin=0, xmax=200, color='r')
axs[3].set_title('Output spikes')
axs[3].stem(spikes_output)
fig.tight_layout()
```

For further details and comprehensive explanations, please refer to the examples directory.
![](res/example_output.png)


## Installation

Run the following to install

```
pip install sctn
```