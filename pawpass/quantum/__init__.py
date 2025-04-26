"""
Azure Quantum integration module for PawPass
"""
from pawpass.quantum.quantum_service import (
    QuantumService,
    QuantumProvider
)

# Create a singleton instance of the quantum service
quantum_service = QuantumService()

# Export functions that use the singleton
def quantum_optimize(resource_type, constraints=None):
    """Optimize resource allocation using quantum algorithms"""
    return quantum_service.quantum_optimize(resource_type, constraints)

def quantum_encrypt(data, security_level="standard"):
    """Encrypt data using quantum-resistant methods"""
    return quantum_service.quantum_encrypt(data, security_level)

def quantum_simulate(simulation_type, **kwargs):
    """Simulate complex systems using quantum algorithms"""
    return quantum_service.quantum_simulate(simulation_type, **kwargs)

__all__ = [
    'QuantumService',
    'QuantumProvider',
    'quantum_service',
    'quantum_optimize',
    'quantum_encrypt',
    'quantum_simulate'
]