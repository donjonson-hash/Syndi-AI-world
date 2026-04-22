"""
Quantum Circuit Visualization.
Requires qiskit (optional dependency).
"""
import io
import logging

logger = logging.getLogger(__name__)

try:
    from qiskit import QuantumCircuit
    from qiskit.visualization import circuit_drawer
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logger.info("qiskit not installed — quantum visuals disabled")


def plot_circuit() -> bytes:
    """Генерирует изображение квантовой схемы. Возвращает PNG bytes."""
    if not QISKIT_AVAILABLE:
        return b""  # пустой результат если qiskit не установлен

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    buf = io.BytesIO()
    circuit_drawer(qc, output="mpl").savefig(buf, format="png")
    buf.seek(0)
    return buf.getvalue()
